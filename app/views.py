from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.db.models import F


class campingdata(APIView):
    # Handles GET, POST, PUT, DELETE operations for Campaigns
    def get(self, request):
        # Fetch and return all campaign records
        campaign = Campaign.objects.all()
        serializer = CampaignSerializer(campaign, many=True)
        return Response(serializer.data)
    def post(self, request):
        # Create a new campaign with the provided data
        serializer = CampaignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        # Update an existing campaign (partial update supported)
        if not pk:
            return Response({"error": "Campaign ID is required for update."}, status=status.HTTP_400_BAD_REQUEST)
        
        campaign = get_object_or_404(Campaign, pk=pk)
        serializer = CampaignSerializer(campaign, data=request.data, partial=True)  # Use `partial=True` to allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        # Delete a campaign by its ID
        if not pk:
            return Response({"error": "Campaign ID is required for deletion."}, status=status.HTTP_400_BAD_REQUEST)

        campaign = get_object_or_404(Campaign, pk=pk)
        campaign.delete()
        return Response({"message": "Campaign deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    
    

class AvailableCampaignsView(APIView):
    # Returns campaigns available to a specific user today, based on targeting and usage limits
    def get(self, request):
        # Step 1: Identify the user
        user_id = request.GET.get('user')
        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = request.user  # Requires authentication

        today = timezone.now().date()

        # Step 2: Fetch campaigns active today
        campaigns = Campaign.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        )

        # Step 3: Filter campaigns that either target the user or are for all users
        campaigns = campaigns.filter(
            Q(target_customers=user) | Q(target_customers__isnull=True)
        ).distinct()

        # Step 4: Get campaign usage counts for this user today
        usage_counts = CampaignUsage.objects.filter(
            user=user,
            campaign__in=campaigns,
            used_at__date=today
        ).values('campaign').annotate(count=Count('id'))
        
        # Create a mapping of campaign_id -> usage count
        usage_map = {item['campaign']: item['count'] for item in usage_counts}

        # Step 5: Filter campaigns the user hasn't exceeded the usage limit for
        eligible_campaigns = []
        for campaign in campaigns:
            usage = usage_map.get(campaign.id, 0)
            if usage < campaign.max_usage_per_day:
                eligible_campaigns.append(campaign)

        # Step 6: Serialize and return the eligible campaigns
        serializer = CampaignSerializer(eligible_campaigns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)