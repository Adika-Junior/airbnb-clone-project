"""
Frontend HTML URLs for Messaging app - used via /messaging/
"""
from django.urls import path
from .views import conversation_list_html, conversation_detail_html

app_name = 'messaging-frontend'

urlpatterns = [
    path('conversations/', conversation_list_html, name='conversation_list_html'),
    path('conversations/<uuid:pk>/', conversation_detail_html, name='conversation_detail_html'),
]
