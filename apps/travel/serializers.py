from rest_framework import serializers
from .models import Listing, Booking
from apps.messaging.serializers import UserSerializer
from apps.properties.serializers import PropertyListSerializer


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model"""
    host = UserSerializer(read_only=True)
    host_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Listing
        fields = [
            'id', 'host', 'host_id', 'title', 'description', 'price_per_night',
            'location', 'image_url', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create listing with host from request"""
        host_id = validated_data.pop('host_id', None)
        if host_id:
            from apps.messaging.models import User
            try:
                validated_data['host'] = User.objects.get(user_id=host_id)
            except User.DoesNotExist:
                pass
        
        if not validated_data.get('host') and self.context.get('request'):
            user = self.context['request'].user
            if user.is_authenticated:
                validated_data['host'] = user
        
        return super().create(validated_data)


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model (allows anonymous)"""
    user = UserSerializer(read_only=True)
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'property', 'property_id', 'listing', 'listing_id',
            'user', 'guest_name', 'guest_email', 'guest_phone',
            'check_in', 'check_out', 'guests', 'total_price',
            'status', 'special_requests', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
    
    def validate(self, data):
        """Validate booking data"""
        property_id = data.get('property_id')
        listing_id = data.get('listing_id')
        
        if not property_id and not listing_id:
            raise serializers.ValidationError(
                "Either property_id or listing_id must be provided."
            )
        
        if property_id and listing_id:
            raise serializers.ValidationError(
                "Cannot book both property and listing. Choose one."
            )
        
        # Validate dates
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date."
                )
        
        # Validate guest info for anonymous bookings
        if not self.context.get('request').user.is_authenticated:
            if not data.get('guest_name') or not data.get('guest_email'):
                raise serializers.ValidationError(
                    "guest_name and guest_email are required for anonymous bookings."
                )
        
        return data
    
    def create(self, validated_data):
        """Create booking"""
        request = self.context.get('request')
        
        # Set user if authenticated
        if request.user.is_authenticated:
            validated_data['user'] = request.user
            # Use user's name and email if not provided
            if not validated_data.get('guest_name'):
                validated_data['guest_name'] = request.user.get_full_name()
            if not validated_data.get('guest_email'):
                validated_data['guest_email'] = request.user.email
        
        # Set property or listing
        property_id = validated_data.pop('property_id', None)
        listing_id = validated_data.pop('listing_id', None)
        
        if property_id:
            from apps.properties.models import Property
            validated_data['property'] = Property.objects.get(id=property_id)
        elif listing_id:
            validated_data['listing'] = Listing.objects.get(id=listing_id)
        
        # Calculate total price if not provided
        if not validated_data.get('total_price'):
            from datetime import timedelta
            check_in = validated_data['check_in']
            check_out = validated_data['check_out']
            nights = (check_out - check_in).days
            
            if property_id:
                property = validated_data['property']
                validated_data['total_price'] = property.price_per_night * nights
            elif listing_id:
                listing = validated_data['listing']
                validated_data['total_price'] = listing.price_per_night * nights
        
        return super().create(validated_data)
