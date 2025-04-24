import logging
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from .models import Campaign

# Configure basic logging to stdout for debugging test flow
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CampaignAPITest(TestCase):
    """
    Test suite for Discount Campaign API endpoints.
    Includes tests for creating campaigns and fetching available campaigns with customer targeting.
    """
    def setUp(self):
        """
        Common setup for all tests:
        - Initialize API client
        - Create two test users
        - Create a default "Cart Discount" campaign available to all users
        """
        self.client = APIClient()
        # Create two sample users
        self.user1 = User.objects.create(username='user1', email='user1@example.com')
        self.user2 = User.objects.create(username='user2', email='user2@example.com')
        logger.debug("Created test users: %s and %s", self.user1, self.user2)

        # Create a default campaign that applies to all customers
        self.campaign = Campaign.objects.create(
            name="Cart Discount",
            discount_type="cart",
            discount_value=10,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=5),
            total_budget=100,
            daily_usage_limit=3
        )
        logger.debug("Created default campaign: %s", self.campaign)

    def test_create_campaign(self):
        """
        Test the creation of a new campaign via the POST endpoint.
        Verifies:
        - HTTP 201 status returned
        - Response contains the correct campaign name
        """
        logger.debug("Starting test_create_campaign")

        # Build the URL for create-list endpoint
        url = reverse('campaign-list-create')

        # Payload for creating a "Delivery Discount" campaign targeting user1
        data = {
            "name": "Delivery Discount",
            "discount_type": "delivery",
            "discount_value": "5.00",
            "start_date": timezone.now().isoformat(),
            "end_date": (timezone.now() + timezone.timedelta(days=3)).isoformat(),
            "total_budget": "50.00",
            "daily_usage_limit": 2,
            "allowed_customers_ids": [self.user1.id]
        }
        logger.debug("POST payload: %s", data)

        # Send POST request
        response = self.client.post(url, data, format='json')
        logger.debug("Response status: %s, body: %s", response.status_code, response.data)

        # Assert correct status and content
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Delivery Discount")
        logger.debug("Finished test_create_campaign")

    def test_targeted_campaign_only_for_specific_user(self):
        """
        Test that a campaign targeted at a specific user is returned only for that user.
        Steps:
        1. Create a "Targeted Discount" campaign allowing only user1.
        2. Confirm user1 sees the campaign in available list.
        3. Confirm user2 does NOT see the campaign.
        """
        logger.debug("Starting test_targeted_campaign_only_for_specific_user")

        # Create a new campaign that is valid now and only for user1
        campaign = Campaign.objects.create(
            name="Targeted Discount",
            discount_type="cart",
            discount_value=20,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(days=1),
            total_budget=100,
            daily_usage_limit=1
        )
        # Link user1 to this campaign
        campaign.allowed_customers.add(self.user1)
        logger.debug("Created targeted campaign: %s", campaign)

        # Endpoint to fetch available campaigns
        url = reverse('available-campaigns')

        # 1️⃣ Test for user1 (should see the campaign)
        logger.debug("Testing availability for user1 (should see it)")
        response1 = self.client.get(url, {'customer_id': self.user1.id, 'discount_type': 'cart'})
        logger.debug("user1 response: %s", response1.data)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        # Check that the targeted campaign appears in the response
        self.assertTrue(any(c['name'] == "Targeted Discount" for c in response1.data))

        # 2️⃣ Test for user2 (should NOT see the campaign)
        logger.debug("Testing availability for user2 (should NOT see it)")
        response2 = self.client.get(url, {'customer_id': self.user2.id, 'discount_type': 'cart'})
        logger.debug("user2 response: %s", response2.data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        # Ensure no entry for the targeted campaign
        self.assertFalse(any(c['name'] == "Targeted Discount" for c in response2.data))

        logger.debug("Finished test_targeted_campaign_only_for_specific_user")
