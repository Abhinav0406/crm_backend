from rest_framework import serializers
from .models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def to_internal_value(self, data):
        """Convert string numbers to integers for numeric fields."""
        if 'max_users' in data and isinstance(data['max_users'], str):
            data = data.copy()
            data['max_users'] = int(data['max_users'])
        if 'max_storage_gb' in data and isinstance(data['max_storage_gb'], str):
            data = data.copy()
            data['max_storage_gb'] = int(data['max_storage_gb'])
        return super().to_internal_value(data)
    
    def validate_slug(self, value):
        """Validate that the slug is unique."""
        # Get the current instance if this is an update
        instance = getattr(self, 'instance', None)
        
        # Check if slug exists for other tenants
        queryset = Tenant.objects.filter(slug=value)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
            
        if queryset.exists():
            raise serializers.ValidationError("A tenant with this slug already exists.")
        return value
    
    def create(self, validated_data):
        """Create a new tenant with default values."""
        # Set default values if not provided
        if 'subscription_status' not in validated_data:
            validated_data['subscription_status'] = 'active'
        if 'is_active' not in validated_data:
            validated_data['is_active'] = True
        if 'max_users' not in validated_data:
            validated_data['max_users'] = 5
        if 'max_storage_gb' not in validated_data:
            validated_data['max_storage_gb'] = 10
            
        return super().create(validated_data) 