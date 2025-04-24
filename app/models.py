from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone

# This model defines a marketing or promotional campaign
class Campaign(models.Model):
    # Two types of discounts - either on cart total or delivery charges
    DISCOUNT_TYPE = (
        ('cart', 'Cart'),
        ('delivery', 'Delivery'),
    )
    # Name of the campaign
    name = models.CharField(max_length=100)
    # Type of discount: 'cart' or 'delivery'
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE)
    #  Discount percentage offered (e.g., 10%)
    discount_percent = models.FloatField()
    # Start date of the campaign
    start_date = models.DateField()
    # End date of the campaign
    end_date = models.DateField()
    # Maximum total budget allowed for the campaign
    max_budget = models.DecimalField(max_digits=10, decimal_places=2)
    # Users targeted by this campaign (can be empty = all users)
    target_customers = models.ManyToManyField(User, blank=True)
    # Max number of times a single user can use this campaign per day
    max_usage_per_day = models.PositiveIntegerField()
    
    # Checks if the campaign is active based on date and remaining budget
    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.max_usage_per_day < self.max_budget
    
 # Tracks each time a user uses a campaign (for limiting usage)   
class CampaignUsage(models.Model):
    # Reference to the campaign used
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    # Reference to the user who used the campaign
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Timestamp when the campaign was used
    used_at = models.DateTimeField(auto_now_add=True)