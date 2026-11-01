from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Web views
    path('', views.dashboard_index_view, name='index'),
    path('admin/', views.admin_dashboard_view, name='admin'),
    path('engineer/', views.engineer_dashboard_view, name='engineer'),
    path('supervisor/', views.supervisor_dashboard_view, name='supervisor'),
    path('system-config/', views.system_config_view, name='system_config'),

    # REST API endpoints
    path('api/dashboard/summary/', views.DashboardSummaryAPIView.as_view(), name='api_summary'),
]
