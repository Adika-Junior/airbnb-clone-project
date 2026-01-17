"""
IP Tracking Models

This module contains models for logging IP addresses, blocking IPs,
and tracking suspicious IPs.
"""
from django.db import models
from django.conf import settings


class RequestLog(models.Model):
    """
    Model to log IP addresses, timestamps, and request paths.
    Extended with geolocation data (country, city) in Task 2.
    """
    ip_address = models.GenericIPAddressField(help_text="Client IP address")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    path = models.CharField(max_length=500, help_text="Request path")
    method = models.CharField(max_length=10, default='GET', help_text="HTTP method")
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Country from geolocation"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="City from geolocation"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Authenticated user if available"
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['path']),
        ]
        verbose_name = 'Request Log'
        verbose_name_plural = 'Request Logs'

    def __str__(self):
        return f"{self.ip_address} - {self.path} - {self.timestamp}"


class BlockedIP(models.Model):
    """
    Model to store blocked IP addresses.
    Used in Task 1 for IP blacklisting.
    """
    ip_address = models.GenericIPAddressField(
        unique=True,
        help_text="IP address to block"
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Reason for blocking"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the IP was blocked"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who blocked this IP"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blocked IP'
        verbose_name_plural = 'Blocked IPs'

    def __str__(self):
        return f"{self.ip_address} (blocked: {self.created_at})"


class SuspiciousIP(models.Model):
    """
    Model to track suspicious IP addresses detected by anomaly detection.
    Used in Task 4.
    """
    ip_address = models.GenericIPAddressField(
        unique=True,
        help_text="Suspicious IP address"
    )
    reason = models.TextField(help_text="Reason for flagging as suspicious")
    flagged_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the IP was flagged"
    )
    last_seen = models.DateTimeField(
        auto_now=True,
        help_text="Last time this IP was seen"
    )
    request_count = models.IntegerField(
        default=0,
        help_text="Number of requests in the detection window"
    )

    class Meta:
        ordering = ['-flagged_at']
        indexes = [
            models.Index(fields=['flagged_at']),
        ]
        verbose_name = 'Suspicious IP'
        verbose_name_plural = 'Suspicious IPs'

    def __str__(self):
        return f"{self.ip_address} - {self.reason[:50]}"
