from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Campaign

class UserSerializer(serializers.ModelSerializer):
    """
    Serializes basic User info to show in Campaign responses.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Only expose these fields

class CampaignSerializer(serializers.ModelSerializer):
    """
    Handles serialization and deserialization of Campaign instances.
    
    - `allowed_customers` (read-only): Nested list of User objects for display.
    - `allowed_customers_ids` (write-only): List of user PKs to assign on create/update.
    """
    # When returning data: show full user objects
    allowed_customers = UserSerializer(many=True, read_only=True)
    
    # When writing data: accept a list of user IDs
    allowed_customers_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        source='allowed_customers'  # maps to the model’s ManyToMany field
    )
    
    class Meta:
        model = Campaign
        # Include all relevant campaign fields, both read and write
        fields = [
            'id',
            'name',
            'discount_type',
            'discount_value',
            'start_date',
            'end_date',
            'total_budget',
            'used_budget',
            'daily_usage_limit',
            'allowed_customers',      # nested users for read
            'allowed_customers_ids',  # IDs for write
        ]

    def create(self, validated_data):
        """
        Override create to pop out allowed_customers list,
        create the campaign, then set the many-to-many relation.
        """
        allowed_customers = validated_data.pop('allowed_customers', [])
        campaign = Campaign.objects.create(**validated_data)
        if allowed_customers:
            # Assign the users to the campaign
            campaign.allowed_customers.set(allowed_customers)
        return campaign

    def update(self, instance, validated_data):
        """
        Override update to handle allowed_customers separately,
        updating the model fields first, then resetting the M2M field.
        """
        allowed_customers = validated_data.pop('allowed_customers', None)
        
        # Update all other simple fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If the caller explicitly provided allowed_customers_ids,
        # reset the many-to-many relationship
        if allowed_customers is not None:
            instance.allowed_customers.set(allowed_customers)
        return instance

