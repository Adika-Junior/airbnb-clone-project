"""
Serializers for IP Tracking API endpoints.
"""
from rest_framework import serializers
from .models import RequestLog, BlockedIP, SuspiciousIP


class RequestLogSerializer(serializers.ModelSerializer):
    """Serializer for RequestLog model."""
    
    class Meta:
        model = RequestLog
        fields = ['id', 'ip_address', 'timestamp', 'path', 'method', 'country', 'city', 'user']
        read_only_fields = ['id', 'timestamp']


class BlockedIPSerializer(serializers.ModelSerializer):
    """Serializer for BlockedIP model."""
    
    class Meta:
        model = BlockedIP
        fields = ['id', 'ip_address', 'reason', 'created_at', 'created_by']
        read_only_fields = ['id', 'created_at']


class SuspiciousIPSerializer(serializers.ModelSerializer):
    """Serializer for SuspiciousIP model."""
    
    class Meta:
        model = SuspiciousIP
        fields = ['id', 'ip_address', 'reason', 'flagged_at', 'last_seen', 'request_count']
        read_only_fields = ['id', 'flagged_at', 'last_seen']
