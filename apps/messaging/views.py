from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import render, redirect, get_object_or_404
from .models import Conversation, Message, User
from .serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    MessageSerializer
)
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination, ConversationPagination
from .filters import MessageFilter, ConversationFilter


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversations."""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = ConversationPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['participants__email', 'participants__first_name', 'participants__last_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views."""
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        """Filter conversations to only show those where the user is a participant."""
        queryset = Conversation.objects.all()
        if self.request.user and self.request.user.is_authenticated:
            queryset = queryset.filter(participants__user_id=self.request.user.user_id).distinct()
        return queryset.prefetch_related('participants', 'messages__sender')
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to a conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body', 'sender__email']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        """Filter messages by conversation if provided."""
        queryset = Message.objects.filter(
            conversation__participants__user_id=self.request.user.user_id
        ).select_related('sender', 'conversation').distinct()
        
        conversation_id = self.request.query_params.get('conversation', None)
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create a new message in a conversation."""
        data = request.data.copy()
        
        if request.user and request.user.is_authenticated:
            data['sender_id'] = request.user.user_id
        else:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# HTML Views for frontend
def conversation_list_html(request):
    """HTML view for conversations list"""
    if not request.user.is_authenticated:
        return redirect('/login/?next=/messaging/conversations/')
    
    conversations = Conversation.objects.filter(
        participants__user_id=request.user.user_id
    ).distinct().prefetch_related('participants', 'messages__sender').order_by('-created_at')
    
    return render(request, 'conversations.html', {'conversations': conversations})


def conversation_detail_html(request, pk):
    """HTML view for conversation detail with messages"""
    if not request.user.is_authenticated:
        return redirect(f'/login/?next=/messaging/conversations/{pk}/')
    
    conversation = get_object_or_404(
        Conversation.objects.filter(participants__user_id=request.user.user_id),
        pk=pk
    )
    messages = conversation.messages.select_related('sender').order_by('sent_at')
    
    return render(request, 'conversation_detail.html', {
        'conversation': conversation,
        'messages': messages
    })
