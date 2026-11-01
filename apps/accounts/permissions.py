from rest_framework import permissions

ROLE_ADMIN = 'Administrator'
ROLE_ENGINEER = 'Engineer'
ROLE_SUPERVISOR = 'Supervisor'
ALL_ROLES = [ROLE_ADMIN, ROLE_ENGINEER, ROLE_SUPERVISOR]

def get_user_role(user):
    """Return primary role string for a given user."""
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser or user.groups.filter(name=ROLE_ADMIN).exists():
        return ROLE_ADMIN
    if user.groups.filter(name=ROLE_SUPERVISOR).exists():
        return ROLE_SUPERVISOR
    if user.groups.filter(name=ROLE_ENGINEER).exists():
        return ROLE_ENGINEER
    return None

def user_is_administrator(user):
    if not user or not user.is_authenticated or not user.is_active:
        return False
    return user.is_superuser or user.groups.filter(name=ROLE_ADMIN).exists()

def user_is_engineer(user):
    if not user or not user.is_authenticated or not user.is_active:
        return False
    return user.groups.filter(name=ROLE_ENGINEER).exists() or user.is_superuser

def user_is_supervisor(user):
    if not user or not user.is_authenticated or not user.is_active:
        return False
    return user.groups.filter(name=ROLE_SUPERVISOR).exists() or user.is_superuser

class IsAdministrator(permissions.BasePermission):
    """Allows access only to users in Administrator group or superusers."""
    def has_permission(self, request, view):
        return bool(request.user and user_is_administrator(request.user))

class IsEngineer(permissions.BasePermission):
    """Allows access to users in Engineer group."""
    def has_permission(self, request, view):
        return bool(request.user and (user_is_engineer(request.user) or user_is_administrator(request.user)))

class IsSupervisor(permissions.BasePermission):
    """Allows access to users in Supervisor group or Administrator."""
    def has_permission(self, request, view):
        return bool(request.user and (user_is_supervisor(request.user) or user_is_administrator(request.user)))

class IsAdminOrSupervisor(permissions.BasePermission):
    """Allows access to Administrator or Supervisor."""
    def has_permission(self, request, view):
        return bool(request.user and (user_is_administrator(request.user) or user_is_supervisor(request.user)))
