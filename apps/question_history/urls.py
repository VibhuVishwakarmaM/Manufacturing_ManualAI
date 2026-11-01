from django.urls import path
from . import views

app_name = 'question_history'

urlpatterns = [
    # REST API endpoints for Questions and History
    path('api/questions/ask/', views.AskQuestionAPIView.as_view(), name='api_ask_question'),
    path('api/questions/history/', views.QuestionHistoryListAPIView.as_view(), name='api_question_history'),
    path('api/questions/<uuid:pk>/', views.QuestionDetailAPIView.as_view(), name='api_question_detail'),
    path('api/questions/<uuid:pk>/feedback/', views.SubmitAnswerFeedbackAPIView.as_view(), name='api_question_feedback'),

    # Supervisor-specific endpoints
    path('api/supervisor/history/', views.SupervisorQuestionHistoryAPIView.as_view(), name='api_supervisor_history'),
    path('api/supervisor/unanswered/', views.SupervisorUnansweredQueriesAPIView.as_view(), name='api_supervisor_unanswered'),
]
