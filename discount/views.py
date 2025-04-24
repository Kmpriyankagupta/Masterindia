from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import F, Q

from .models import Campaign,DiscountUsage
from .serializers import CampaignSerializer

class CampaignListCreateView(APIView):
    """
    API View for listing all campaigns and creating new ones.

    GET:
        - Returns a list of all existing campaigns.
    POST:
        - Creates a new Campaign based on the provided data.
    """
    def get(self, request):
        # Fetch all campaigns from the database
        campaigns = Campaign.objects.all()
        # Serialize the queryset into JSON format
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Deserialize incoming JSON data to a CampaignSerializer
        serializer = CampaignSerializer(data=request.data)
        # Validate the data against the Campaign model
        if serializer.is_valid():
            campaign = serializer.save()  # Save valid data, creating a Campaign
            # Return the created campaign with HTTP 201 status
            return Response(CampaignSerializer(campaign).data, status=status.HTTP_201_CREATED)
        # Return validation errors with HTTP 400 status
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CampaignDetailView(APIView):
    """
    API View for retrieving, updating, or deleting a specific campaign.

    GET:
        - Retrieve details of a campaign by its primary key (pk).
    PUT:
        - Update an existing campaign with new data.
    DELETE:
        - Delete the specified campaign.
    """
    def get_object(self, pk):
        # Helper method to fetch a campaign or return 404 if not found
        return get_object_or_404(Campaign, pk=pk)
    
    def get(self, request, pk):
        campaign = self.get_object(pk)
        serializer = CampaignSerializer(campaign)
        return Response(serializer.data)
    
    def put(self, request, pk):
        campaign = self.get_object(pk)
        serializer = CampaignSerializer(campaign, data=request.data)
        if serializer.is_valid():
            campaign = serializer.save()  # Save updates to the campaign
            return Response(CampaignSerializer(campaign).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        campaign = self.get_object(pk)
        campaign.delete()  # Remove the campaign from the database
        return Response(status=status.HTTP_204_NO_CONTENT)


class AvailableCampaignsView(APIView):
    """
    API View to fetch campaigns available for a customer based on:
      1. Active date range
      2. Remaining budget
      3. Discount type filter
      4. Customer targeting (global or specific)
    """
    def get(self, request):
        # Extract optional query parameters
        customer_id = request.query_params.get('customer_id')
        discount_type = request.query_params.get('discount_type')
        now = timezone.now()

        # 1. Filter by active date range and remaining budget
        campaigns = Campaign.objects.filter(
            start_date__lte=now,
            end_date__gte=now,
            used_budget__lt=F('total_budget')
        )
        print(f"[Date & Budget] {campaigns.count()} campaigns match")

        # 2. If a discount_type is provided, filter by it
        if discount_type:
            campaigns = campaigns.filter(discount_type=discount_type)
            print(f"[Type={discount_type}] {campaigns.count()} campaigns match")

        # 3. If a customer_id is provided, filter by allowed customers
        if customer_id:
            try:
                customer = User.objects.get(pk=customer_id)
            except User.DoesNotExist:
                # Invalid customer ID passed
                print(f"Invalid customer_id={customer_id}")
                return Response({"error": "Invalid customer ID"}, status=status.HTTP_400_BAD_REQUEST)

            # Include campaigns that are either global (no restrictions)
            # or explicitly include this customer
            campaigns = campaigns.filter(
                Q(allowed_customers__isnull=True) |
                Q(allowed_customers=customer)
            ).distinct()
            print(f"[Customer ID={customer_id}] {campaigns.count()} campaigns match")

        # Serialize and return the final queryset
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)

from decimal import Decimal
from rest_framework.exceptions import ValidationError
def apply_campaign_discount(order, campaign, customer):
    today = timezone.now().date()

    # 1. Get or create today's usage record for the customer
    usage, created = DiscountUsage.objects.get_or_create(
        campaign=campaign,
        customer=customer,
        used_on=today
    )

    # 2. Enforce daily usage limit
    if usage.transaction_count >= campaign.daily_usage_limit:
        raise ValidationError("You’ve reached your daily discount limit.")

    # 3. Convert float subtotal/delivery_fee to Decimal
    subtotal = Decimal(str(order['subtotal']))
    delivery_fee = Decimal(str(order['delivery_fee']))
    discount_value = campaign.discount_value

    # 4. Calculate discount
    if campaign.discount_type == 'cart':
        discount_amount = subtotal * (discount_value / Decimal('100'))
    else:
        discount_amount = delivery_fee * (discount_value / Decimal('100'))

    # 5. Apply discount
    order['discount_applied'] = round(discount_amount, 2)
    order['total'] = float(subtotal + delivery_fee - discount_amount)

    # 6. Update usage and campaign budget
    usage.transaction_count += 1
    usage.save()

    campaign.used_budget += discount_amount
    campaign.save()

    return order
class ApplyDiscountView(APIView):
    """
    API to apply a discount without saving an order.
    Accepts subtotal, delivery_fee, and campaign_id.
    Returns calculated discount and final total.
    """
    def post(self, request):
        subtotal = float(request.data.get('subtotal', 0))
        delivery_fee = float(request.data.get('delivery_fee', 0))
        campaign_id = request.data.get('campaign_id')
        customer = request.data.get('customer')
        customer=User.objects.get(id=customer)
        if campaign_id is None:
            return Response({"error": "Campaign ID is required."}, status=400)

        # Ensure campaign exists
        campaign = get_object_or_404(Campaign, pk=campaign_id)

        # ✅ Create mock order dictionary
        temp_order = {
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'total': subtotal + delivery_fee,  # Initial total before discount
            'discount_applied': 0
        }

        # ✅ Call the discount logic
        result = apply_campaign_discount(temp_order, campaign, customer)
        return Response(result, status=200)
