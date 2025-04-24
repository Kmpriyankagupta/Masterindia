from django.contrib import admin
from .models import Campaign

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'discount_type', 
        'discount_value', 
        'start_date', 
        'end_date', 
        'total_budget', 
        'used_budget', 
        'daily_usage_limit',
        'is_active',  # Display the active status of the campaign
    )
    list_filter = ('discount_type', 'start_date', 'end_date')
    search_fields = ('name',)
    filter_horizontal = ('allowed_customers',)  # Better UI for many-to-many field
