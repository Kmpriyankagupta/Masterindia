from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Campaign(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('cart', 'Overall Cart'),
        ('delivery', 'Delivery Charges'),
    )
    
    name = models.CharField(max_length=255)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Discount value (e.g. percentage or fixed amount)")
    start_date = models.DateTimeField(help_text="Campaign start date and time")
    end_date = models.DateTimeField(help_text="Campaign end date and time")
    total_budget = models.DecimalField(max_digits=10, decimal_places=2, help_text="Max total discount budget available for this campaign")
    daily_usage_limit = models.IntegerField(default=1, help_text="Max transactions per customer per day")
    allowed_customers = models.ManyToManyField(
        User,
        blank=True,
        help_text="If empty, campaign is available for all customers"
    )
    used_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Budget used so far")

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.used_budget < self.total_budget

    def __str__(self):
        return self.name

class DiscountUsage(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='usages')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discount_usages')
    used_on = models.DateField(auto_now_add=True)  # date when the discount was used
    transaction_count = models.IntegerField(default=0)  # how many times user used the discount on that day

    def __str__(self):
        return f"{self.customer.username} used {self.campaign.name} on {self.used_on} ({self.transaction_count}x)"