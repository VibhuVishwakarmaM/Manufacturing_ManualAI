import uuid
from django.db import models
from django.contrib.auth.models import User
from apps.machines.models import Machine

class QuestionHistory(models.Model):
    STATUS_ANSWERED = 'ANSWERED'
    STATUS_INSUFFICIENT = 'INSUFFICIENT_EVIDENCE'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = (
        (STATUS_ANSWERED, 'Answered with Supporting Evidence'),
        (STATUS_INSUFFICIENT, 'Insufficient Information in Manuals'),
        (STATUS_FAILED, 'Query Processing Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='questions', db_index=True)
    question_text = models.TextField()
    answer_text = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_ANSWERED, db_index=True)
    confidence_score = models.FloatField(default=0.0, help_text="Top evidence retrieval similarity score (0.0 to 1.0)")
    retrieved_evidence = models.JSONField(
        default=list,
        help_text="Retrieved passages with manual title, revision, page number, and content snippet"
    )
    llm_provider = models.CharField(max_length=50, blank=True, default='')
    prompt_version = models.CharField(max_length=20, default='v1')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Question History'
        verbose_name_plural = 'Question Histories'

    def __str__(self):
        return f"[{self.user.username}] {self.machine.name}: {self.question_text[:50]}"

    @property
    def is_insufficient_evidence(self):
        return self.status == self.STATUS_INSUFFICIENT

    @property
    def evidence_count(self):
        return len(self.retrieved_evidence) if isinstance(self.retrieved_evidence, list) else 0

class AnswerFeedback(models.Model):
    RATING_HELPFUL = 'HELPFUL'
    RATING_UNHELPFUL = 'UNHELPFUL'
    RATING_CHOICES = (
        (RATING_HELPFUL, 'Helpful / Accurate'),
        (RATING_UNHELPFUL, 'Unhelpful / Inaccurate'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(QuestionHistory, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    feedback_text = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('question', 'user')

    def __str__(self):
        return f"{self.rating} by {self.user.username} on question {self.question_id}"
