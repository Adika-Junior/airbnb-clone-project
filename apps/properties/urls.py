from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'properties'

# REST API Router
router = DefaultRouter()
router.register(r'properties', views.PropertyViewSet, basename='property')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # REST API endpoints (via router)
    path('api/', include(router.urls)),
    
    # Direct API endpoints
    path('api/list/', views.property_list_api, name='property_list_api'),
    path('api/<int:pk>/', views.property_detail_api, name='property_detail_api'),
    path('api/<int:pk>/reviews/', views.property_reviews_api, name='property_reviews_api'),
    path('api/<int:pk>/add-review/', views.add_review_api, name='add_review_api'),
    path('api/create/', views.create_property_api, name='create_property_api'),
    path('metrics/', views.property_metrics, name='property_metrics'),
    
    # HTML endpoints
    path('', views.property_list_html, name='property_list_html'),
    path('add/', views.property_create_html, name='property_create_html'),
    path('<int:pk>/', views.property_detail_html, name='property_detail_html'),
]
