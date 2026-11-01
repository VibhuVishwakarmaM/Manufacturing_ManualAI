from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return redirect('accounts:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect, name='root'),

    # Application URLs
    path('accounts/', include('apps.accounts.urls')),
    path('machines/', include('apps.machines.urls')),
    path('manuals/', include('apps.manuals.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('audit/', include('apps.audit_logs.urls')),
    path('questions/', include('apps.question_history.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
