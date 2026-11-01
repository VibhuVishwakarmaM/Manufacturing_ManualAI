import uuid
from django.db import models
from apps.machines.models import Machine
from apps.manuals.models import Manual

class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manual = models.ForeignKey(Manual, on_delete=models.CASCADE, related_name='chunks')
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='chunks', db_index=True)
    chunk_index = models.IntegerField(db_index=True)
    page_start = models.IntegerField(help_text="1-indexed starting PDF page number")
    page_end = models.IntegerField(help_text="1-indexed ending PDF page number")
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    embedding = models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['chunk_index']
        indexes = [
            models.Index(fields=['machine', 'manual']),
            models.Index(fields=['machine', 'page_start']),
        ]
        verbose_name = 'Document Chunk'
        verbose_name_plural = 'Document Chunks'

    def __str__(self):
        return f"[{self.manual.title}] Chunk #{self.chunk_index} (pp. {self.page_start}-{self.page_end})"

    @property
    def page_number(self):
        """Single page number or range for citation display."""
        if self.page_start == self.page_end:
            return self.page_start
        return f"{self.page_start}-{self.page_end}"
