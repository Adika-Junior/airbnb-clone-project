"""
Filter classes for the messaging app.
"""
import django_filters
from django_filters import rest_framework as filters
from .models import Message, Conversation
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageFilter(filters.FilterSet):
    """Filter class for messages."""
    conversation = filters.UUIDFilter(field_name='conversation__conversation_id')
    sender = filters.UUIDFilter(field_name='sender__user_id')
    sender_email = filters.CharFilter(field_name='sender__email', lookup_expr='iexact')
    sent_at_after = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_at_before = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    
    class Meta:
        model = Message
        fields = ['conversation', 'sender', 'sent_at']


class ConversationFilter(filters.FilterSet):
    """Filter class for conversations."""
    participant = filters.UUIDFilter(
        field_name='participants__user_id',
        distinct=True
    )
    participant_email = filters.CharFilter(
        field_name='participants__email',
        lookup_expr='iexact',
        distinct=True
    )
    
    class Meta:
        model = Conversation
        fields = ['participant', 'participant_email']
