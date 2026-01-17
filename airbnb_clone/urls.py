"""
URL configuration for airbnb_clone project.

Unified URL routing for all integrated ALX services.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.views.generic import TemplateView
from apps.messaging.auth_views import register_user, get_current_user, CustomTokenObtainPairView

# Swagger/OpenAPI Schema View
schema_view = get_schema_view(
    openapi.Info(
        title="Airbnb Clone API",
        default_version='v1',
        description="""
        Unified API for Airbnb Clone Project integrating all ALX backend services:
        - Security: IP Tracking & Security System
        - Properties: Property Listings with Caching
        - CRM: GraphQL Customer Relationship Management
        - Travel: Travel Listings & Bookings
        - Messaging: User Communication System
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@airbnbclone.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Swagger/OpenAPI Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Custom authentication (with user data)
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('api/auth/register/', register_user, name='auth_register'),
    path('api/auth/me/', get_current_user, name='auth_me'),
    
    # Security App (IP Tracking)
    path('api/security/', include('apps.security.urls', namespace='security')),
    
    # Properties App (Caching)
    path('api/properties/', include('apps.properties.urls', namespace='properties')),
    path('properties/', include('apps.properties.urls', namespace='properties-frontend')),
    
    # CRM App (GraphQL)
    path('api/crm/', include('apps.crm.urls', namespace='crm')),
    path('graphql/', include('apps.crm.urls', namespace='graphql')),  # Alternative GraphQL endpoint
    
    # Travel App (Listings & Bookings)
    path('api/travel/', include('apps.travel.urls_api')),
    path('travel/', include('apps.travel.urls')),
    
    # Messaging App (User Communication)
    path('api/messaging/', include('apps.messaging.urls_api')),
    path('messaging/', include('apps.messaging.urls')),
    
    # Frontend Pages
    path('', TemplateView.as_view(template_name='index.html'), name='frontend-home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('signup/', TemplateView.as_view(template_name='signup.html'), name='signup'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
