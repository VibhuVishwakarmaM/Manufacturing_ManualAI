from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', default='System', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'username', 'action', 'resource_type', 'resource_id', 'metadata', 'ip_address', 'timestamp']
        read_only_fields = fields
