import uuid
import os
from django.db import models
from django.contrib.auth.models import User
from apps.machines.models import Machine

def manual_upload_path(instance, filename):
    """Generate isolated file storage path for equipment manual PDFs."""
    machine_id = str(instance.machine_id) if instance.machine_id else 'unassigned'
    return os.path.join('manuals', machine_id, filename)

class Manual(models.Model):
    STATUS_UPLOADED = 'UPLOADED'
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_INDEXED = 'INDEXED'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = (
        (STATUS_UPLOADED, 'Uploaded / Pending Extraction'),
        (STATUS_PROCESSING, 'Processing & Embedding'),
        (STATUS_INDEXED, 'Indexed & Searchable'),
        (STATUS_FAILED, 'Processing Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='manuals')
    title = models.CharField(max_length=255, help_text="e.g., VF-2SS Maintenance & Lubrication Manual")
    file = models.FileField(upload_to=manual_upload_path)
    original_filename = models.CharField(max_length=255)
    model_information = models.CharField(max_length=150, blank=True, default='', help_text="Equipment model version if specific")
    revision = models.CharField(max_length=50, default='Rev 1.0', help_text="e.g., Rev A, Rev 2.1, 2024-Q1")
    file_size = models.BigIntegerField(default=0, help_text="File size in bytes")
    page_count = models.IntegerField(default=0)
    chunk_count = models.IntegerField(default=0)
    processing_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_UPLOADED, db_index=True)
    error_message = models.TextField(blank=True, default='')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_manuals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Manual'
        verbose_name_plural = 'Manuals'

    def __str__(self):
        return f"{self.title} ({self.revision}) - [{self.machine.name}]"

    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)
