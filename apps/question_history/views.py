from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import views, generics, permissions, status
from rest_framework.response import Response

from .models import QuestionHistory, AnswerFeedback
from .serializers import QuestionHistorySerializer, AnswerFeedbackSerializer
from apps.accounts.permissions import (
    IsEngineer,
    IsSupervisor,
    IsAdminOrSupervisor,
    user_is_supervisor,
    user_is_administrator
)
from apps.rag_engine.engine import RAGEngine
from apps.audit_logs.utils import log_audit_event

# -----------------------------------------------------------------------------
# REST API VIEWS
# -----------------------------------------------------------------------------

class AskQuestionAPIView(views.APIView):
    """
    Core RAG Question Answering Endpoint.
    Accepts: { machine_id: UUID, question: str }
    Executes machine-isolated vector search, evidence validation, and generation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        machine_id = request.data.get('machine_id')
        question_text = request.data.get('question')

        if not machine_id:
            return Response({'error': 'machine_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not question_text or not question_text.strip():
            return Response({'error': 'question text cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

        rag = RAGEngine()
        try:
            result = rag.answer_question(
                user=request.user,
                machine_id=str(machine_id),
                question_text=question_text
            )

            log_audit_event(
                user=request.user,
                action='ASK_QUESTION',
                resource_type='Machine',
                resource_id=str(machine_id),
                metadata={'question': question_text[:80], 'status': result['status']},
                request=request
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuestionHistoryListAPIView(generics.ListAPIView):
    """
    Lists question history.
    Engineers see only their own queries; Supervisors/Admins can see all queries.
    """
    serializer_class = QuestionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = QuestionHistory.objects.select_related('machine', 'user').prefetch_related('feedbacks')
        
        machine_id = self.request.query_params.get('machine')
        if machine_id:
            qs = qs.filter(machine_id=machine_id)

        # Non-supervisors and non-admins only see personal history
        if not (user_is_administrator(user) or user_is_supervisor(user)):
            qs = qs.filter(user=user)

        return qs.order_by('-created_at')

class QuestionDetailAPIView(generics.RetrieveAPIView):
    serializer_class = QuestionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = QuestionHistory.objects.select_related('machine', 'user').prefetch_related('feedbacks')
        if not (user_is_administrator(user) or user_is_supervisor(user)):
            qs = qs.filter(user=user)
        return qs

class SubmitAnswerFeedbackAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        question = get_object_or_404(QuestionHistory, pk=pk)
        rating = request.data.get('rating')
        comment = request.data.get('feedback_text', '')

        if rating not in [AnswerFeedback.RATING_HELPFUL, AnswerFeedback.RATING_UNHELPFUL]:
            return Response({'error': 'Invalid rating choice.'}, status=status.HTTP_400_BAD_REQUEST)

        feedback, _ = AnswerFeedback.objects.update_or_create(
            question=question,
            user=request.user,
            defaults={'rating': rating, 'feedback_text': comment}
        )

        return Response(AnswerFeedbackSerializer(feedback).data, status=status.HTTP_200_OK)

class SupervisorQuestionHistoryAPIView(generics.ListAPIView):
    """Supervisor endpoint to review all questions with filtering."""
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]
    serializer_class = QuestionHistorySerializer

    def get_queryset(self):
        qs = QuestionHistory.objects.select_related('machine', 'user').prefetch_related('feedbacks').all()

        machine_id = self.request.query_params.get('machine')
        user_id = self.request.query_params.get('user')
        q_status = self.request.query_params.get('status')

        if machine_id:
            qs = qs.filter(machine_id=machine_id)
        if user_id:
            qs = qs.filter(user_id=user_id)
        if q_status:
            qs = qs.filter(status=q_status)

        return qs.order_by('-created_at')

class SupervisorUnansweredQueriesAPIView(generics.ListAPIView):
    """Supervisor endpoint to identify unanswered or insufficient evidence questions."""
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]
    serializer_class = QuestionHistorySerializer

    def get_queryset(self):
        return QuestionHistory.objects.select_related('machine', 'user').filter(
            status__in=[QuestionHistory.STATUS_INSUFFICIENT, QuestionHistory.STATUS_FAILED]
        ).order_by('-created_at')
