"""
Custom permission classes for the messaging app.
"""
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Conversation, Message


class IsParticipantOfConversation(BasePermission):
    """Custom permission to check if user is a participant in a conversation."""
    
    def has_permission(self, request, view):
        """Require authentication."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is participant."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        if isinstance(obj, Message):
            conversation = obj.conversation
            return conversation.participants.filter(user_id=request.user.user_id).exists()
        
        return False
