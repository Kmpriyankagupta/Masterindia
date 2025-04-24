from rest_framework import serializers
from .models import *

# This serializer automatically converts the Campaign model to and from JSON.
class CampaignSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Campaign    # Link the serializer to the Campaign model
        fields = '__all__' # Include all model fields in the API (you can also list specific fields instead)