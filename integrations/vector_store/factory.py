from django.conf import settings
from .base import BaseVectorStore
from .in_db_store import InDatabaseVectorStore

def get_vector_store(name: str = None) -> BaseVectorStore:
    """Factory to retrieve vector store instance."""
    ai_cfg = getattr(settings, 'AI_SETTINGS', {})
    provider_name = (name or ai_cfg.get('VECTOR_STORE_PROVIDER', 'in_db')).lower()

    if provider_name in ['in_db', 'postgres', 'sqlite']:
        return InDatabaseVectorStore()
    else:
        # Default fallback
        return InDatabaseVectorStore()
