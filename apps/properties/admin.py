from django.contrib import admin
from .models import Property, Review


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'property_type', 'price_per_night', 'location', 'is_active', 'is_featured', 'created_at')
    list_filter = ('property_type', 'is_active', 'is_featured', 'location', 'created_at')
    search_fields = ('title', 'description', 'location', 'city', 'country', 'host__email', 'host__first_name', 'host__last_name')
    readonly_fields = ('created_at', 'updated_at', 'average_rating', 'review_count')
    fieldsets = (
        ('Basic Information', {
            'fields': ('host', 'title', 'description', 'property_type')
        }),
        ('Location', {
            'fields': ('location', 'address', 'city', 'country', 'latitude', 'longitude')
        }),
        ('Pricing', {
            'fields': ('price_per_night',)
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'beds', 'max_guests', 'square_feet')
        }),
        ('Amenities', {
            'fields': ('wifi', 'kitchen', 'parking', 'pool', 'air_conditioning', 'heating', 'tv', 'washer', 'dryer'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('image', 'image_url')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'review_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'reviewer_display', 'rating', 'is_approved', 'is_anonymous', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_anonymous', 'created_at')
    search_fields = ('property__title', 'comment', 'guest_name', 'guest_email', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    def reviewer_display(self, obj):
        if obj.user:
            return f"{obj.user.get_full_name()} ({obj.user.email})"
        return f"{obj.guest_name} ({obj.guest_email})" if obj.guest_name else "Anonymous"
    reviewer_display.short_description = 'Reviewer'
