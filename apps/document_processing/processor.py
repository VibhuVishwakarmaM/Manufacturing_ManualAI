import logging
import traceback
from django.db import transaction
from apps.manuals.models import Manual
from .models import DocumentChunk
from .pdf_extractor import PyMuPDFExtractor
from .chunker import DocumentChunker
from integrations.embeddings import get_embedding_provider
from apps.audit_logs.utils import log_audit_event
from apps.notifications.utils import notify_user, notify_admins

logger = logging.getLogger(__name__)

def process_manual(manual_id: str, force_reprocess: bool = False):
    """
    Complete PDF extraction, chunking, embedding generation, and indexing pipeline.
    Preserves exact 1-indexed page references and binds chunks strictly to machine_id.
    """
    manual = Manual.objects.select_related('machine', 'uploaded_by').get(id=manual_id)

    # Prevent accidental duplicate processing unless forced
    if manual.processing_status == Manual.STATUS_PROCESSING and not force_reprocess:
        logger.warning(f"Manual {manual_id} is already being processed.")
        return {'status': 'ALREADY_PROCESSING', 'manual_id': str(manual.id)}

    manual.processing_status = Manual.STATUS_PROCESSING
    manual.error_message = ''
    manual.save(update_fields=['processing_status', 'error_message'])

    try:
        # Step 1: Open PDF and extract pages via PyMuPDF
        pdf_path = manual.file.path
        with PyMuPDFExtractor(pdf_path) as extractor:
            page_count = extractor.get_page_count()
            if page_count < 1:
                raise ValueError("PDF has 0 pages or no readable contents.")
            pages_data = extractor.extract_pages()

        manual.page_count = page_count

        # Step 2: Chunk text while preserving page attribution
        chunker = DocumentChunker()
        chunk_dicts = chunker.chunk_pages(
            pages_data=pages_data,
            manual_id=manual.id,
            machine_id=manual.machine_id,
            manual_title=manual.title,
            revision=manual.revision
        )

        if not chunk_dicts:
            raise ValueError("No extractable text chunks could be produced from this document.")

        # Step 3: Generate embeddings
        embedding_provider = get_embedding_provider()
        chunk_texts = [c['content'] for c in chunk_dicts]
        embeddings = embedding_provider.embed_batch(chunk_texts)

        # Step 4: Atomic DB indexing
        with transaction.atomic():
            # Clear previous chunks if reprocessing
            DocumentChunk.objects.filter(manual=manual).delete()

            chunk_instances = []
            for i, c_data in enumerate(chunk_dicts):
                emb = embeddings[i] if i < len(embeddings) else []
                chunk_instances.append(
                    DocumentChunk(
                        manual=manual,
                        machine=manual.machine,
                        chunk_index=c_data['chunk_index'],
                        page_start=c_data['page_start'],
                        page_end=c_data['page_end'],
                        content=c_data['content'],
                        metadata=c_data['metadata'],
                        embedding=emb
                    )
                )
            DocumentChunk.objects.bulk_create(chunk_instances)

        # Step 5: Mark manual as INDEXED
        manual.chunk_count = len(chunk_instances)
        manual.processing_status = Manual.STATUS_INDEXED
        manual.error_message = ''
        manual.save()

        # Step 6: Audit log and notifications
        log_audit_event(
            user=manual.uploaded_by,
            action='MANUAL_INDEXED',
            resource_type='Manual',
            resource_id=str(manual.id),
            metadata={
                'title': manual.title,
                'machine': manual.machine.name,
                'pages': manual.page_count,
                'chunks': manual.chunk_count
            }
        )

        notify_admins(
            title="Manual Successfully Indexed",
            message=f"Manual '{manual.title}' for machine '{manual.machine.name}' indexed ({manual.page_count} pages, {manual.chunk_count} chunks).",
            level='success'
        )

        return {
            'status': 'SUCCESS',
            'manual_id': str(manual.id),
            'page_count': manual.page_count,
            'chunk_count': manual.chunk_count
        }

    except Exception as e:
        err_msg = str(e)
        logger.error(f"Processing failed for manual {manual_id}: {err_msg}\n{traceback.format_exc()}")
        manual.processing_status = Manual.STATUS_FAILED
        manual.error_message = err_msg
        manual.save(update_fields=['processing_status', 'error_message'])

        log_audit_event(
            user=manual.uploaded_by,
            action='MANUAL_PROCESSING_FAILED',
            resource_type='Manual',
            resource_id=str(manual.id),
            metadata={'title': manual.title, 'error': err_msg}
        )

        notify_admins(
            title="Manual Processing Failed",
            message=f"Failed to process manual '{manual.title}': {err_msg}",
            level='error'
        )

        return {
            'status': 'FAILED',
            'manual_id': str(manual.id),
            'error': err_msg
        }
