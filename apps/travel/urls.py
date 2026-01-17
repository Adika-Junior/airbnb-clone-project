"""
Frontend HTML URLs for Travel app - used via /travel/
"""
from django.urls import path
from .views import listing_list_html, booking_list_html

app_name = 'travel-frontend'

urlpatterns = [
    path('listings/', listing_list_html, name='listing_list_html'),
    path('bookings/', booking_list_html, name='booking_list_html'),
]
