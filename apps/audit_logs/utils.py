import logging
from .models import AuditLog

logger = logging.getLogger(__name__)

SENSITIVE_KEYS = {'password', 'token', 'secret', 'api_key', 'authorization', 'key'}

def sanitize_metadata(meta):
    """Recursively scrub sensitive keys from metadata dictionary."""
    if not isinstance(meta, dict):
        return meta
    cleaned = {}
    for k, v in meta.items():
        if any(s in k.lower() for s in SENSITIVE_KEYS):
            cleaned[k] = '[REDACTED]'
        elif isinstance(v, dict):
            cleaned[k] = sanitize_metadata(v)
        else:
            cleaned[k] = v
    return cleaned

def get_client_ip(request):
    """Retrieve client IP address from standard headers."""
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_audit_event(user, action, resource_type, resource_id="", metadata=None, request=None):
    """Safely log an operational audit event."""
    try:
        ip_addr = get_client_ip(request)
        clean_meta = sanitize_metadata(metadata or {})
        AuditLog.objects.create(
            user=user if (user and user.is_authenticated) else None,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            metadata=clean_meta,
            ip_address=ip_addr
        )
    except Exception as e:
        logger.warning(f"Failed to record audit event: {e}")
