from rest_framework import serializers
from .models import QuestionHistory, AnswerFeedback

class AnswerFeedbackSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AnswerFeedback
        fields = ['id', 'question', 'user', 'username', 'rating', 'feedback_text', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class QuestionHistorySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    machine_name = serializers.CharField(source='machine.name', read_only=True)
    machine_model = serializers.CharField(source='machine.model_number', read_only=True)
    feedbacks = AnswerFeedbackSerializer(many=True, read_only=True)

    class Meta:
        model = QuestionHistory
        fields = [
            'id', 'user', 'username', 'machine', 'machine_name', 'machine_model',
            'question_text', 'answer_text', 'status', 'confidence_score',
            'retrieved_evidence', 'llm_provider', 'prompt_version',
            'feedbacks', 'created_at'
        ]
        read_only_fields = fields
