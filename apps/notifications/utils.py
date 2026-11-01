import logging
from django.contrib.auth.models import User
from .models import Notification
from apps.accounts.permissions import ROLE_ADMIN

logger = logging.getLogger(__name__)

def notify_user(user, title, message, level='info'):
    try:
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            level=level
        )
    except Exception as e:
        logger.warning(f"Failed to create notification: {e}")
        return None

def notify_admins(title, message, level='info'):
    try:
        # Also create a broadcast notification with user=None
        Notification.objects.create(
            user=None,
            title=title,
            message=message,
            level=level
        )
        # And for specific admin users
        for admin_user in User.objects.filter(groups__name=ROLE_ADMIN):
            Notification.objects.create(
                user=admin_user,
                title=title,
                message=message,
                level=level
            )
    except Exception as e:
        logger.warning(f"Failed to notify admins: {e}")
