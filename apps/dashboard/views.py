from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import views, permissions, status
from rest_framework.response import Response

from apps.accounts.permissions import (
    get_user_role,
    user_is_administrator,
    user_is_supervisor,
    user_is_engineer,
    ROLE_ADMIN,
    ROLE_SUPERVISOR,
    ROLE_ENGINEER,
    IsAdministrator
)
from apps.machines.models import Machine
from apps.manuals.models import Manual
from apps.question_history.models import QuestionHistory
from apps.audit_logs.models import AuditLog

@login_required
def dashboard_index_view(request):
    """Main routing view based on user role."""
    role = get_user_role(request.user)

    if role == ROLE_ADMIN or request.user.is_superuser:
        return redirect('dashboard:admin')
    elif role == ROLE_SUPERVISOR:
        return redirect('dashboard:supervisor')
    else:
        return redirect('dashboard:engineer')

@login_required
def admin_dashboard_view(request):
    if not user_is_administrator(request.user):
        return redirect('dashboard:index')

    machines = Machine.objects.all().prefetch_related('manuals')
    manuals = Manual.objects.select_related('machine', 'uploaded_by').all()
    recent_uploads = manuals.order_by('-created_at')[:5]
    failed_manuals = manuals.filter(processing_status=Manual.STATUS_FAILED)

    total_machines = machines.count()
    total_manuals = manuals.count()
    indexed_manuals = manuals.filter(processing_status=Manual.STATUS_INDEXED).count()
    failed_count = failed_manuals.count()

    total_users = User.objects.count()
    total_questions = QuestionHistory.objects.count()
    recent_audits = AuditLog.objects.select_related('user').all()[:8]

    context = {
        'total_machines': total_machines,
        'total_manuals': total_manuals,
        'indexed_manuals': indexed_manuals,
        'failed_count': failed_count,
        'total_users': total_users,
        'total_questions': total_questions,
        'recent_uploads': recent_uploads,
        'failed_manuals': failed_manuals,
        'recent_audits': recent_audits,
        'machines': machines,
    }
    return render(request, 'admin_dashboard/index.html', context)

@login_required
def engineer_dashboard_view(request):
    """Engineer Q&A and verification workspace."""
    machines = Machine.objects.filter(status='ACTIVE')
    selected_machine_id = request.GET.get('machine_id')

    selected_machine = None
    manuals_for_machine = []
    if selected_machine_id:
        selected_machine = machines.filter(id=selected_machine_id).first()
        if selected_machine:
            manuals_for_machine = selected_machine.manuals.filter(processing_status=Manual.STATUS_INDEXED)

    # Personal recent questions
    user_questions = QuestionHistory.objects.filter(user=request.user).select_related('machine')[:10]

    context = {
        'machines': machines,
        'selected_machine': selected_machine,
        'manuals_for_machine': manuals_for_machine,
        'user_questions': user_questions,
    }
    return render(request, 'engineer_dashboard/index.html', context)

@login_required
def supervisor_dashboard_view(request):
    """Supervisor audit, analytics, and unanswered queries review workspace."""
    if not (user_is_supervisor(request.user) or user_is_administrator(request.user)):
        return redirect('dashboard:index')

    machines = Machine.objects.all()
    engineers = User.objects.filter(groups__name=ROLE_ENGINEER)

    # Filters
    selected_machine = request.GET.get('machine')
    selected_user = request.GET.get('engineer')
    selected_status = request.GET.get('status')

    questions_qs = QuestionHistory.objects.select_related('machine', 'user').prefetch_related('feedbacks').all()

    if selected_machine:
        questions_qs = questions_qs.filter(machine_id=selected_machine)
    if selected_user:
        questions_qs = questions_qs.filter(user_id=selected_user)
    if selected_status:
        questions_qs = questions_qs.filter(status=selected_status)

    total_queries = QuestionHistory.objects.count()
    answered_queries = QuestionHistory.objects.filter(status=QuestionHistory.STATUS_ANSWERED).count()
    insufficient_queries = QuestionHistory.objects.filter(status=QuestionHistory.STATUS_INSUFFICIENT).count()
    failed_queries = QuestionHistory.objects.filter(status=QuestionHistory.STATUS_FAILED).count()

    context = {
        'questions': questions_qs[:50],
        'machines': machines,
        'engineers': engineers,
        'selected_machine': selected_machine,
        'selected_user': selected_user,
        'selected_status': selected_status,
        'total_queries': total_queries,
        'answered_queries': answered_queries,
        'insufficient_queries': insufficient_queries,
        'failed_queries': failed_queries,
    }
    return render(request, 'supervisor_dashboard/index.html', context)

@login_required
def system_config_view(request):
    """Admin-only view of active system configuration without exposing secrets."""
    if not user_is_administrator(request.user):
        return redirect('dashboard:index')

    ai_cfg = getattr(settings, 'AI_SETTINGS', {})
    safe_config = {
        'LLM_PROVIDER': ai_cfg.get('LLM_PROVIDER'),
        'LLM_MODEL': ai_cfg.get('LLM_MODEL'),
        'LLM_API_BASE_URL': ai_cfg.get('LLM_API_BASE_URL'),
        'EMBEDDING_PROVIDER': ai_cfg.get('EMBEDDING_PROVIDER'),
        'EMBEDDING_MODEL': ai_cfg.get('EMBEDDING_MODEL'),
        'EMBEDDING_DIMENSION': ai_cfg.get('EMBEDDING_DIMENSION'),
        'VECTOR_STORE_PROVIDER': ai_cfg.get('VECTOR_STORE_PROVIDER'),
        'VECTOR_COLLECTION': ai_cfg.get('VECTOR_COLLECTION'),
        'CHUNK_SIZE': ai_cfg.get('CHUNK_SIZE'),
        'CHUNK_OVERLAP': ai_cfg.get('CHUNK_OVERLAP'),
        'TOP_K': ai_cfg.get('TOP_K'),
        'SIMILARITY_THRESHOLD': ai_cfg.get('SIMILARITY_THRESHOLD'),
        'MAX_UPLOAD_SIZE_MB': ai_cfg.get('MAX_UPLOAD_SIZE_MB'),
        'RAG_PROMPT_VERSION': ai_cfg.get('RAG_PROMPT_VERSION'),
        'DATABASE_ENGINE': settings.DATABASES['default']['ENGINE'],
        'DATABASE_NAME': settings.DATABASES['default']['NAME'],
    }
    return render(request, 'admin_dashboard/system_config.html', {'config': safe_config})


# -----------------------------------------------------------------------------
# REST API VIEWS
# -----------------------------------------------------------------------------

class DashboardSummaryAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_machines = Machine.objects.count()
        total_manuals = Manual.objects.count()
        indexed_manuals = Manual.objects.filter(processing_status=Manual.STATUS_INDEXED).count()
        failed_manuals = Manual.objects.filter(processing_status=Manual.STATUS_FAILED).count()
        total_questions = QuestionHistory.objects.count()
        insufficient_questions = QuestionHistory.objects.filter(status=QuestionHistory.STATUS_INSUFFICIENT).count()

        ai_cfg = getattr(settings, 'AI_SETTINGS', {})

        return Response({
            'total_machines': total_machines,
            'total_manuals': total_manuals,
            'indexed_manuals': indexed_manuals,
            'failed_manuals': failed_manuals,
            'total_questions': total_questions,
            'insufficient_evidence_questions': insufficient_questions,
            'user_role': get_user_role(request.user),
            'ai_provider': ai_cfg.get('LLM_PROVIDER'),
            'embedding_provider': ai_cfg.get('EMBEDDING_PROVIDER'),
            'vector_store_provider': ai_cfg.get('VECTOR_STORE_PROVIDER'),
        }, status=status.HTTP_200_OK)
