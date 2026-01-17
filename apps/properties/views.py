from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from .models import Property, Review
from .serializers import PropertySerializer, PropertyListSerializer, ReviewSerializer
from .utils import get_all_properties, get_redis_cache_metrics


class PropertyViewSet(ModelViewSet):
    """ViewSet for Property model"""
    queryset = Property.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        return PropertySerializer
    
    def get_queryset(self):
        queryset = Property.objects.filter(is_active=True)
        
        # Filter by host if provided
        host_id = self.request.query_params.get('host', None)
        if host_id:
            queryset = queryset.filter(host__user_id=host_id)
        
        # Filter by location
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(
                Q(location__icontains=location) |
                Q(city__icontains=location) |
                Q(country__icontains=location)
            )
        
        # Filter by property type
        property_type = self.request.query_params.get('type', None)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        # Filter featured
        featured = self.request.query_params.get('featured', None)
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.order_by('-is_featured', '-created_at')
    
    def perform_create(self, serializer):
        """Set host to current user if authenticated"""
        if self.request.user.is_authenticated:
            serializer.save(host=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get reviews for a property"""
        property = self.get_object()
        reviews = property.reviews.filter(is_approved=True)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def add_review(self, request, pk=None):
        """Add a review to a property (allows anonymous)"""
        property = self.get_object()
        data = request.data.copy()
        data['property'] = property.id
        
        # If user is authenticated, use user; otherwise use guest info
        if request.user.is_authenticated:
            data['user'] = request.user.user_id
            data['is_anonymous'] = False
        else:
            data['is_anonymous'] = True
            if not data.get('guest_name') or not data.get('guest_email'):
                return Response(
                    {'error': 'guest_name and guest_email are required for anonymous reviews'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(ModelViewSet):
    """ViewSet for Review model"""
    queryset = Review.objects.filter(is_approved=True)
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Review.objects.filter(is_approved=True)
        property_id = self.request.query_params.get('property', None)
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set user if authenticated"""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, is_anonymous=False)
        else:
            serializer.save(is_anonymous=True)


# API Views
@api_view(['GET'])
@permission_classes([AllowAny])
def property_list_api(request):
    """API endpoint to list all properties (public)"""
    properties = Property.objects.filter(is_active=True).order_by('-is_featured', '-created_at')
    serializer = PropertyListSerializer(properties, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def property_detail_api(request, pk):
    """API endpoint to get property details"""
    property = get_object_or_404(Property, pk=pk, is_active=True)
    serializer = PropertySerializer(property)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_property_api(request):
    """API endpoint to create a property (requires authentication)"""
    serializer = PropertySerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(host=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def property_reviews_api(request, pk):
    """API endpoint to get reviews for a property"""
    property = get_object_or_404(Property, pk=pk, is_active=True)
    reviews = property.reviews.filter(is_approved=True).order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_review_api(request, pk):
    """API endpoint to add a review (allows anonymous)"""
    property = get_object_or_404(Property, pk=pk, is_active=True)
    data = request.data.copy()
    data['property'] = property.id
    
    if request.user.is_authenticated:
        data['user'] = request.user.user_id
        data['is_anonymous'] = False
    else:
        data['is_anonymous'] = True
        if not data.get('guest_name') or not data.get('guest_email'):
            return Response(
                {'error': 'guest_name and guest_email are required for anonymous reviews'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    serializer = ReviewSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def property_metrics(request):
    """API endpoint to get cache metrics"""
    metrics = get_redis_cache_metrics()
    return Response(metrics)


# HTML Views
def property_list_html(request):
    """HTML view for property list"""
    properties = Property.objects.filter(is_active=True).order_by('-is_featured', '-created_at')
    return render(request, 'property_list.html', {'properties': properties})


def property_detail_html(request, pk):
    """HTML view for property detail"""
    property = get_object_or_404(Property, pk=pk, is_active=True)
    reviews = property.reviews.filter(is_approved=True).order_by('-created_at')[:10]
    return render(request, 'property_detail.html', {
        'property': property,
        'reviews': reviews
    })


@csrf_exempt
def property_create_html(request):
    """HTML view for property creation"""
    if not request.user.is_authenticated:
        return redirect('/login/?next=/properties/add/')
    
    if request.method == 'POST':
        # Handle property creation
        from .serializers import PropertySerializer
        serializer = PropertySerializer(data=request.POST, context={'request': request})
        if serializer.is_valid():
            serializer.save(host=request.user)
            return redirect(f'/properties/{serializer.data["id"]}/')
        # If validation fails, render form with errors
        return render(request, 'property_form.html', {'errors': serializer.errors})
    
    return render(request, 'property_form.html')
