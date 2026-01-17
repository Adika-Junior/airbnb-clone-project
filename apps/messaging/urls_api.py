"""
API URLs for Messaging app - used via /api/messaging/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet
from .auth_views import register_user, get_current_user

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

app_name = 'messaging-api'

urlpatterns = [
    # Authentication endpoints
    path('register/', register_user, name='register'),
    path('me/', get_current_user, name='current_user'),
    
    # Router provides API endpoints
    path('', include(router.urls)),
]
