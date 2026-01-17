from django.contrib import admin
from .models import Listing, Booking


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'host', 'price_per_night', 'location', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'location', 'host__email', 'host__first_name', 'host__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_display', 'guest_display', 'check_in', 'check_out', 'guests', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'check_in', 'check_out', 'created_at']
    search_fields = ['property__title', 'listing__title', 'guest_name', 'guest_email', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def booking_display(self, obj):
        if obj.property:
            return f"Property: {obj.property.title}"
        elif obj.listing:
            return f"Listing: {obj.listing.title}"
        return "Unknown"
    booking_display.short_description = 'Item'
    
    def guest_display(self, obj):
        if obj.user:
            return f"{obj.user.get_full_name()} ({obj.user.email})"
        return f"{obj.guest_name} ({obj.guest_email})"
    guest_display.short_description = 'Guest'
