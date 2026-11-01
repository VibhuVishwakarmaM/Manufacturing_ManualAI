from django.urls import path
from . import views

app_name = 'manuals'

urlpatterns = [
    # Web views
    path('', views.manual_list_view, name='list'),
    path('upload/', views.manual_upload_view, name='upload'),
    path('<uuid:pk>/reprocess/', views.manual_reprocess_view, name='reprocess'),
    path('<uuid:pk>/delete/', views.manual_delete_view, name='delete'),
    path('<uuid:pk>/view/', views.manual_view_pdf_view, name='view_pdf'),
    path('<uuid:pk>/download/', views.manual_download_pdf_view, name='download_pdf'),

    # REST API endpoints
    path('api/manuals/', views.ManualListCreateAPIView.as_view(), name='api_manual_list'),
    path('api/manuals/<uuid:pk>/', views.ManualDetailAPIView.as_view(), name='api_manual_detail'),
    path('api/manuals/<uuid:pk>/process/', views.ManualProcessAPIView.as_view(), name='api_manual_process'),
    path('api/manuals/<uuid:pk>/status/', views.ManualStatusAPIView.as_view(), name='api_manual_status'),
]
