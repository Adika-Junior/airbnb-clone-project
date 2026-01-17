"""
API URLs for Travel app - used via /api/travel/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ListingViewSet, BookingViewSet, listing_list_api, create_booking_api, 
    user_bookings_api
)

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')

app_name = 'travel-api'

urlpatterns = [
    # Router provides API endpoints
    path('', include(router.urls)),
    
    # Direct API endpoints
    path('listings/', listing_list_api, name='listing_list_api'),
    path('bookings/create/', create_booking_api, name='create_booking_api'),
    path('bookings/my/', user_bookings_api, name='user_bookings_api'),
]
