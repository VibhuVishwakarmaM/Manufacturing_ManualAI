from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics, permissions
from .models import AuditLog
from .serializers import AuditLogSerializer
from apps.accounts.permissions import IsAdministrator, IsAdminOrSupervisor, user_is_administrator, user_is_supervisor

@login_required
def audit_log_list_web_view(request):
    if not (user_is_administrator(request.user) or user_is_supervisor(request.user)):
        messages.error(request, "Access denied: Audit log access requires Administrator or Supervisor privileges.")
        return redirect('dashboard:index')

    logs = AuditLog.objects.select_related('user').all()[:100]
    return render(request, 'audit_logs/audit_list.html', {'logs': logs})

class AuditLogListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.select_related('user').all()
    filterset_fields = ['action', 'resource_type']
