from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """ViewSet for Listing model"""
    queryset = Listing.objects.filter(is_active=True)
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Listing.objects.filter(is_active=True)
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set host to current user if authenticated"""
        if self.request.user.is_authenticated:
            serializer.save(host=self.request.user)
        else:
            serializer.save()


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for Booking model (allows anonymous)"""
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]  # Allow anonymous bookings
    
    def get_queryset(self):
        """Filter bookings based on user role"""
        queryset = Booking.objects.all()
        
        # If user is authenticated, show their bookings
        if self.request.user.is_authenticated:
            user = self.request.user
            if user.role == 'admin':
                # Admin can see all bookings
                pass
            elif user.role == 'host':
                # Host sees bookings for their properties/listings
                queryset = queryset.filter(
                    Q(property__host=user) | Q(listing__host=user)
                )
            else:
                # Guest sees only their own bookings
                queryset = queryset.filter(user=user)
        else:
            # Anonymous users can't see bookings (would need email/name filter)
            queryset = Booking.objects.none()
        
        # Filter by property or listing if provided
        property_id = self.request.query_params.get('property', None)
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        
        listing_id = self.request.query_params.get('listing', None)
        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create booking (allows anonymous)"""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        
        # Check permissions
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to cancel booking'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user = request.user
        can_cancel = (
            user.role == 'admin' or
            booking.user == user or
            (booking.property and booking.property.host == user) or
            (booking.listing and booking.listing.host == user)
        )
        
        if not can_cancel:
            return Response(
                {'error': 'You do not have permission to cancel this booking'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)


# Direct API endpoints for easier access
@api_view(['GET'])
@permission_classes([AllowAny])
def listing_list_api(request):
    """API endpoint to list all listings (public)"""
    listings = Listing.objects.filter(is_active=True).order_by('-created_at')
    serializer = ListingSerializer(listings, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking_api(request):
    """API endpoint to create a booking (allows anonymous)"""
    serializer = BookingSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookings_api(request):
    """API endpoint to get current user's bookings"""
    user = request.user
    bookings = Booking.objects.filter(user=user).order_by('-created_at')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


# HTML Views for frontend
def listing_list_html(request):
    """HTML view for travel listings"""
    listings = Listing.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'travel_listings.html', {'listings': listings})


def booking_list_html(request):
    """HTML view for user bookings"""
    if not request.user.is_authenticated:
        return redirect('/login/?next=/travel/bookings/')
    
    user = request.user
    if user.role == 'admin':
        bookings = Booking.objects.all().order_by('-created_at')
    elif user.role == 'host':
        bookings = Booking.objects.filter(
            Q(property__host=user) | Q(listing__host=user)
        ).order_by('-created_at')
    else:
        bookings = Booking.objects.filter(user=user).order_by('-created_at')
    
    return render(request, 'bookings.html', {'bookings': bookings})
