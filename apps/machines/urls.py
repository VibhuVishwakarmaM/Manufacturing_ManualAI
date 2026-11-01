from django.urls import path
from . import views

app_name = 'machines'

urlpatterns = [
    # Web views
    path('', views.machine_list_view, name='list'),
    path('create/', views.machine_create_view, name='create'),
    path('<uuid:pk>/edit/', views.machine_edit_view, name='edit'),
    path('<uuid:pk>/delete/', views.machine_delete_view, name='delete'),

    # REST API endpoints
    path('api/machines/', views.MachineListCreateAPIView.as_view(), name='api_machine_list'),
    path('api/machines/<uuid:pk>/', views.MachineDetailAPIView.as_view(), name='api_machine_detail'),
]
