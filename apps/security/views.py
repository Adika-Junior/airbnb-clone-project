"""
Views for IP Tracking application.

Task 3: Implement rate limiting on sensitive views.
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import RequestLog, BlockedIP, SuspiciousIP


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@csrf_exempt
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Example sensitive view with rate limiting.
    Task 3: Rate limit - 5 requests/minute for anonymous users.
    """
    if request.method == 'POST':
        # Simulate login logic
        return JsonResponse({
            'message': 'Login endpoint (rate limited: 5 requests/minute for anonymous)',
            'status': 'success'
        })
    return JsonResponse({
        'message': 'Login page',
        'rate_limit': '5 requests/minute for anonymous users'
    })


@ratelimit(key='user_or_ip', rate='10/m', block=True)
@login_required
def sensitive_view(request):
    """
    Example sensitive view for authenticated users.
    Task 3: Rate limit - 10 requests/minute for authenticated users.
    """
    return JsonResponse({
        'message': 'Sensitive data endpoint',
        'rate_limit': '10 requests/minute for authenticated users',
        'user': request.user.username
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='10/m', block=True)
def api_request_logs(request):
    """
    API endpoint to retrieve request logs.
    Rate limited: 10 requests/minute for authenticated users.
    """
    from .serializers import RequestLogSerializer
    from rest_framework.pagination import PageNumberPagination

    logs = RequestLog.objects.all().order_by('-timestamp')
    
    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 50
    page = paginator.paginate_queryset(logs, request)
    
    if page is not None:
        serializer = RequestLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = RequestLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='10/m', block=True)
def api_suspicious_ips(request):
    """
    API endpoint to retrieve suspicious IPs.
    Rate limited: 10 requests/minute for authenticated users.
    """
    from .serializers import SuspiciousIPSerializer
    
    suspicious = SuspiciousIP.objects.all().order_by('-flagged_at')
    serializer = SuspiciousIPSerializer(suspicious, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='10/m', block=True)
def api_blocked_ips(request):
    """
    API endpoint to retrieve blocked IPs.
    Rate limited: 10 requests/minute for authenticated users.
    """
    from .serializers import BlockedIPSerializer
    
    blocked = BlockedIP.objects.all().order_by('-created_at')
    serializer = BlockedIPSerializer(blocked, many=True)
    return Response(serializer.data)


def home_view(request):
    """Home page view."""
    return JsonResponse({
        'message': 'IP Tracking System',
        'status': 'active',
        'endpoints': {
            'login': '/api/security/login/',
            'sensitive': '/api/security/sensitive/ (requires authentication)',
            'api_logs': '/api/security/logs/ (requires authentication)',
            'api_suspicious': '/api/security/suspicious/ (requires authentication)',
            'api_blocked': '/api/security/blocked/ (requires authentication)',
        },
        'note': 'This request has been logged. Check admin panel to see your IP address.'
    })
