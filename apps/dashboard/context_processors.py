from django.conf import settings
from apps.accounts.permissions import get_user_role
from apps.notifications.models import Notification

def app_settings_context(request):
    """Context processor providing role and general application metadata."""
    ai_cfg = getattr(settings, 'AI_SETTINGS', {})
    user = request.user
    role = get_user_role(user) if user.is_authenticated else None

    unread_notifications_count = 0
    if user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False).count()

    return {
        'APP_TITLE': 'Manufacturing Manual AI Assistant',
        'CURRENT_USER_ROLE': role,
        'AI_PROVIDER': ai_cfg.get('LLM_PROVIDER', 'mock'),
        'AI_MODEL': ai_cfg.get('LLM_MODEL', 'gpt-4o-mini'),
        'EMBEDDING_PROVIDER': ai_cfg.get('EMBEDDING_PROVIDER', 'mock'),
        'SIMILARITY_THRESHOLD': ai_cfg.get('SIMILARITY_THRESHOLD', 0.65),
    }
