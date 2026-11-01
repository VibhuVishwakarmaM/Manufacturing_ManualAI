from django.urls import path
from . import views

app_name = 'audit_logs'

urlpatterns = [
    path('logs/', views.audit_log_list_web_view, name='log_list'),
    path('api/audit/logs/', views.AuditLogListAPIView.as_view(), name='api_log_list'),
]
