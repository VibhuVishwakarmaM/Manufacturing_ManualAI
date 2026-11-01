from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from rest_framework import status, views, permissions
from rest_framework.response import Response

from .permissions import (
    IsAdministrator,
    get_user_role,
    user_is_administrator,
    ALL_ROLES,
    ROLE_ADMIN,
    ROLE_ENGINEER,
    ROLE_SUPERVISOR
)
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserRoleUpdateSerializer,
    LoginSerializer
)
from apps.audit_logs.utils import log_audit_event

# -----------------------------------------------------------------------------
# WEB TEMPLATE VIEWS
# -----------------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form_data = request.POST
        username = form_data.get('username')
        password = form_data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                log_audit_event(
                    user=user,
                    action='USER_LOGIN',
                    resource_type='User',
                    resource_id=str(user.id),
                    metadata={'username': user.username},
                    request=request
                )
                messages.success(request, f"Welcome back, {user.username} ({get_user_role(user)})")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard:index')
            else:
                messages.error(request, "This account has been deactivated. Please contact an administrator.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        log_audit_event(
            user=request.user,
            action='USER_LOGOUT',
            resource_type='User',
            resource_id=str(request.user.id),
            metadata={'username': request.user.username},
            request=request
        )
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')

@login_required
def user_management_view(request):
    """Admin dashboard section for managing users and roles."""
    if not user_is_administrator(request.user):
        messages.error(request, "Access denied: Administrator privileges required.")
        return redirect('dashboard:index')

    users = User.objects.all().order_by('-date_joined')
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    admin_count = users.filter(groups__name=ROLE_ADMIN).count()
    engineer_count = users.filter(groups__name=ROLE_ENGINEER).count()
    supervisor_count = users.filter(groups__name=ROLE_SUPERVISOR).count()

    # Annotate role onto user objects for simple template display
    for u in users:
        u.current_role = get_user_role(u)

    context = {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'admin_count': admin_count,
        'engineer_count': engineer_count,
        'supervisor_count': supervisor_count,
        'all_roles': ALL_ROLES,
    }
    return render(request, 'accounts/user_management.html', context)

@login_required
@require_POST
def user_create_web_view(request):
    if not user_is_administrator(request.user):
        messages.error(request, "Access denied.")
        return redirect('dashboard:index')

    username = request.POST.get('username')
    email = request.POST.get('email', '')
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    password = request.POST.get('password')
    role = request.POST.get('role', ROLE_ENGINEER)

    if not username or not password:
        messages.error(request, "Username and password are required.")
        return redirect('accounts:user_management')

    if User.objects.filter(username=username).exists():
        messages.error(request, f"Username '{username}' already exists.")
        return redirect('accounts:user_management')

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    group, _ = Group.objects.get_or_create(name=role)
    user.groups.add(group)

    log_audit_event(
        user=request.user,
        action='CREATE_USER',
        resource_type='User',
        resource_id=str(user.id),
        metadata={'username': username, 'role': role},
        request=request
    )
    messages.success(request, f"User '{username}' created successfully with role '{role}'.")
    return redirect('accounts:user_management')

@login_required
@require_POST
def user_toggle_status_web_view(request, user_id):
    if not user_is_administrator(request.user):
        messages.error(request, "Access denied.")
        return redirect('dashboard:index')

    target_user = get_object_or_404(User, id=user_id)
    if target_user.id == request.user.id:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('accounts:user_management')

    target_user.is_active = not target_user.is_active
    target_user.save()

    status_str = "activated" if target_user.is_active else "deactivated"
    log_audit_event(
        user=request.user,
        action=f'USER_{status_str.upper()}',
        resource_type='User',
        resource_id=str(target_user.id),
        metadata={'username': target_user.username, 'is_active': target_user.is_active},
        request=request
    )
    messages.success(request, f"User '{target_user.username}' has been {status_str}.")
    return redirect('accounts:user_management')

@login_required
@require_POST
def user_change_role_web_view(request, user_id):
    if not user_is_administrator(request.user):
        messages.error(request, "Access denied.")
        return redirect('dashboard:index')

    target_user = get_object_or_404(User, id=user_id)
    new_role = request.POST.get('role')

    if new_role not in ALL_ROLES:
        messages.error(request, "Invalid role specified.")
        return redirect('accounts:user_management')

    # Remove existing role groups
    for r in ALL_ROLES:
        group_obj = Group.objects.filter(name=r).first()
        if group_obj:
            target_user.groups.remove(group_obj)

    new_group, _ = Group.objects.get_or_create(name=new_role)
    target_user.groups.add(new_group)

    log_audit_event(
        user=request.user,
        action='UPDATE_USER_ROLE',
        resource_type='User',
        resource_id=str(target_user.id),
        metadata={'username': target_user.username, 'new_role': new_role},
        request=request
    )
    messages.success(request, f"Updated role for '{target_user.username}' to '{new_role}'.")
    return redirect('accounts:user_management')


# -----------------------------------------------------------------------------
# REST API VIEWS
# -----------------------------------------------------------------------------

class LoginAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        log_audit_event(
            user=user,
            action='API_USER_LOGIN',
            resource_type='User',
            resource_id=str(user.id),
            metadata={'username': user.username},
            request=request
        )
        return Response({
            'message': 'Login successful.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class LogoutAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        log_audit_event(
            user=request.user,
            action='API_USER_LOGOUT',
            resource_type='User',
            resource_id=str(request.user.id),
            metadata={'username': request.user.username},
            request=request
        )
        logout(request)
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)

class CurrentUserAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

class UserListCreateAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdministrator]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_audit_event(
            user=request.user,
            action='API_CREATE_USER',
            resource_type='User',
            resource_id=str(user.id),
            metadata={'username': user.username, 'role': get_user_role(user)},
            request=request
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class UserRoleUpdateAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdministrator]

    def patch(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        serializer = UserRoleUpdateSerializer(target_user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_audit_event(
            user=request.user,
            action='API_UPDATE_USER_ROLE',
            resource_type='User',
            resource_id=str(target_user.id),
            metadata={'username': target_user.username, 'new_role': get_user_role(target_user)},
            request=request
        )
        return Response(UserSerializer(target_user).data)
