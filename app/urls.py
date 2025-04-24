from django.contrib import admin
from django.urls import path
from .views import *

# Define URL patterns for the campaign-related API endpoints
urlpatterns = [
    # Endpoint to handle CRUD operations for Campaigns (GET, POST, PUT, DELETE)
    path('campingdata/', campingdata.as_view()),
    # Endpoint to fetch currently active and eligible campaigns for a user
    path('available-campaigns/', AvailableCampaignsView.as_view(), name='available-campaigns'),
]
