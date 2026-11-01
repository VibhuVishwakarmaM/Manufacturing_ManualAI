import uuid
from django.db import models

class Machine(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active / Operational'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('DECOMMISSIONED', 'Decommissioned'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Machine name (e.g., CNC Milling Unit Alpha)")
    model_number = models.CharField(max_length=100, db_index=True, help_text="Equipment model number (e.g., VF-2SS-2024)")
    manufacturer = models.CharField(max_length=150, blank=True, default='', help_text="Manufacturer name")
    description = models.TextField(blank=True, default='', help_text="Equipment specs, line location, and operational notes")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Machine'
        verbose_name_plural = 'Machines'

    def __str__(self):
        return f"{self.name} [{self.model_number}]"

    @property
    def manual_count(self):
        return self.manuals.count()

    @property
    def active_manuals(self):
        return self.manuals.filter(processing_status='INDEXED')
