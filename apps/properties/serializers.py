from rest_framework import serializers
from .models import Property, Review
from apps.messaging.serializers import UserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    user = UserSerializer(read_only=True)
    reviewer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'property', 'user', 'guest_name', 'guest_email',
            'rating', 'comment', 'is_approved', 'is_anonymous',
            'reviewer_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_reviewer_name(self, obj):
        """Get reviewer name (user or guest name)"""
        if obj.user:
            return obj.user.get_full_name()
        return obj.guest_name or 'Anonymous'
    
    def validate(self, data):
        """Validate that either user or guest info is provided"""
        if not data.get('user') and not data.get('guest_name'):
            raise serializers.ValidationError(
                "Either user must be authenticated or guest_name must be provided."
            )
        return data


class PropertySerializer(serializers.ModelSerializer):
    """Serializer for Property model"""
    host = UserSerializer(read_only=True)
    host_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    display_price = serializers.ReadOnlyField()
    
    # Backward compatibility
    price = serializers.DecimalField(source='price_per_night', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'host', 'host_id', 'title', 'description', 'property_type',
            'price_per_night', 'price', 'location', 'address', 'city', 'country',
            'latitude', 'longitude', 'bedrooms', 'bathrooms', 'beds', 'max_guests',
            'square_feet', 'wifi', 'kitchen', 'parking', 'pool', 'air_conditioning',
            'heating', 'tv', 'washer', 'dryer', 'image', 'image_url', 'is_active',
            'is_featured', 'reviews', 'average_rating', 'review_count',
            'display_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'average_rating', 'review_count']
    
    def create(self, validated_data):
        """Create property with host from request"""
        host_id = validated_data.pop('host_id', None)
        if host_id:
            from apps.messaging.models import User
            try:
                validated_data['host'] = User.objects.get(user_id=host_id)
            except User.DoesNotExist:
                pass
        
        # If no host_id but user is authenticated, use request user
        if not validated_data.get('host') and self.context.get('request'):
            user = self.context['request'].user
            if user.is_authenticated:
                validated_data['host'] = user
        
        return super().create(validated_data)


class PropertyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for property listings"""
    host_name = serializers.SerializerMethodField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    display_price = serializers.ReadOnlyField()
    price = serializers.DecimalField(source='price_per_night', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'property_type', 'price_per_night', 'price',
            'location', 'city', 'country', 'bedrooms', 'bathrooms', 'beds', 'max_guests',
            'wifi', 'kitchen', 'parking', 'pool', 'image_url', 'is_featured',
            'host_name', 'average_rating', 'review_count', 'display_price', 'created_at'
        ]
    
    def get_host_name(self, obj):
        """Get host name"""
        if obj.host:
            return obj.host.get_full_name()
        return 'Host'
