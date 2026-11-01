from django.apps import AppConfig

class DocumentProcessingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.document_processing'
    verbose_name = 'PDF Processing & Chunking'
