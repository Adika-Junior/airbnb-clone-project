"""
URL configuration for IP Tracking app.
"""
from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('sensitive/', views.sensitive_view, name='sensitive'),
    path('logs/', views.api_request_logs, name='api_logs'),
    path('suspicious/', views.api_suspicious_ips, name='api_suspicious'),
    path('blocked/', views.api_blocked_ips, name='api_blocked'),
]
