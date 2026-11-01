from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Web views
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_management_view, name='user_management'),
    path('users/create/', views.user_create_web_view, name='user_create'),
    path('users/<int:user_id>/toggle-status/', views.user_toggle_status_web_view, name='user_toggle_status'),
    path('users/<int:user_id>/change-role/', views.user_change_role_web_view, name='user_change_role'),

    # REST API endpoints
    path('api/auth/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/auth/logout/', views.LogoutAPIView.as_view(), name='api_logout'),
    path('api/auth/me/', views.CurrentUserAPIView.as_view(), name='api_me'),
    path('api/auth/users/', views.UserListCreateAPIView.as_view(), name='api_users'),
    path('api/auth/users/<int:pk>/role/', views.UserRoleUpdateAPIView.as_view(), name='api_user_role'),
]
