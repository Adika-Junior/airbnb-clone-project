from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'password', 'phone_number', 'role', 'created_at']
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        """Check if email already exists."""
        if self.instance is None:  # Only check on creation
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',
        write_only=True,
        required=False
    )
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all())
    message_body = serializers.CharField(required=True, allow_blank=False, max_length=5000)
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'sender_id', 'conversation', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']
    
    def validate_message_body(self, value):
        """Validate message body is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value.strip()
    
    def create(self, validated_data):
        """Create a new message."""
        return Message.objects.create(**validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested messages."""
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'participant_ids', 'messages', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']
    
    def validate_participant_ids(self, value):
        """Validate participant IDs."""
        if value and len(value) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants.")
        if value:
            existing_ids = set(User.objects.filter(user_id__in=value).values_list('user_id', flat=True))
            provided_ids = set(value)
            missing_ids = provided_ids - existing_ids
            if missing_ids:
                raise serializers.ValidationError(f"Invalid participant IDs: {list(missing_ids)}")
        return value
    
    def create(self, validated_data):
        """Create a new conversation with participants."""
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)
        return conversation


class ConversationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing conversations."""
    participants = UserSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'message_count', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_message_count(self, obj):
        """Get the count of messages in the conversation."""
        return obj.messages.count()
