"""
Django Admin configuration for IP Tracking models.
"""
from django.contrib import admin
from .models import RequestLog, BlockedIP, SuspiciousIP


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    """Admin interface for RequestLog model."""
    list_display = ['ip_address', 'path', 'method', 'country', 'city', 'timestamp', 'user']
    list_filter = ['method', 'country', 'timestamp', 'path']
    search_fields = ['ip_address', 'path', 'country', 'city']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 50


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    """Admin interface for BlockedIP model."""
    list_display = ['ip_address', 'reason', 'created_at', 'created_by']
    list_filter = ['created_at']
    search_fields = ['ip_address', 'reason']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(SuspiciousIP)
class SuspiciousIPAdmin(admin.ModelAdmin):
    """Admin interface for SuspiciousIP model."""
    list_display = ['ip_address', 'reason', 'request_count', 'flagged_at', 'last_seen']
    list_filter = ['flagged_at']
    search_fields = ['ip_address', 'reason']
    readonly_fields = ['flagged_at', 'last_seen']
    date_hierarchy = 'flagged_at'
    actions = ['block_selected_ips']

    def block_selected_ips(self, request, queryset):
        """Action to block selected suspicious IPs."""
        from .models import BlockedIP
        count = 0
        for suspicious_ip in queryset:
            BlockedIP.objects.get_or_create(
                ip_address=suspicious_ip.ip_address,
                defaults={'reason': f'Auto-blocked: {suspicious_ip.reason}'}
            )
            count += 1
        self.message_user(request, f'{count} IP(s) blocked successfully.')
    block_selected_ips.short_description = "Block selected IPs"
