# Requirements Mapping & Compliance Matrix

This document maps all official requirements from the Hackathon Master Build Prompt to their exact code implementations, models, API endpoints, and automated tests.

| Section | Requirement Description | Implementation Component | Verification / Test |
|---|---|---|---|
| **§2. Workflow 1-4** | Admin logs in, registers machines, uploads PDF manuals with revision | `apps/accounts/views.py`<br>`apps/machines/`<br>`apps/manuals/models.py` | `tests/test_rbac_permissions.py`<br>`tests/test_api_endpoints.py` |
| **§2. Workflow 5-7** | Extract text with PyMuPDF, preserve page numbers, index embeddings | `apps/document_processing/pdf_extractor.py`<br>`apps/document_processing/chunker.py`<br>`apps/document_processing/processor.py` | `tests/test_pdf_processing.py` |
| **§2. Workflow 8-11** | Engineer logs in, selects machine, asks question, machine-scoped retrieval | `apps/rag_engine/engine.py`<br>`integrations/vector_store/in_db_store.py` | `tests/test_retrieval_isolation.py` *(MANDATORY TEST 2)* |
| **§2. Workflow 12-14** | Grounded LLM answer, citation display (title, revision, page), open PDF | `apps/rag_engine/engine.py`<br>`templates/engineer_dashboard/index.html`<br>`apps/manuals/views.py:manual_view_pdf_view` | `tests/test_rag_pipeline.py` |
| **§2. Workflow 15-16** | Engineer saved history, Supervisor cross-engineer review of unanswered queries | `apps/question_history/models.py`<br>`apps/question_history/views.py`<br>`templates/supervisor_dashboard/index.html` | `tests/test_rbac_permissions.py`<br>`tests/test_rag_pipeline.py` |
| **§3. Tech Stack** | Django, DRF, PostgreSQL, PyMuPDF, Pytest, Bootstrap 5 | `config/settings/base.py`<br>`requirements.txt`<br>`templates/base.html` | All 16 automated tests pass with `pytest` |
| **§5. Config** | Centralized configuration for LLM, Embeddings, Vector Store, Chunking, Thresholds | `config/settings/base.py`<br>`.env.example`<br>`apps/dashboard/views.py:system_config_view` | `tests/test_rag_pipeline.py` |
| **§6. Machines** | Register, edit, delete with safeguards, model number, status | `apps/machines/models.py`<br>`apps/machines/views.py` | `tests/test_rbac_permissions.py`<br>`tests/test_api_endpoints.py` |
| **§7. Manuals** | Upload validation, PDF readability check, status lifecycle, retry | `apps/manuals/models.py`<br>`apps/manuals/validators.py`<br>`apps/manuals/views.py` | `tests/test_pdf_processing.py` |
| **§8. Extraction** | PyMuPDF extraction, 1-indexed page preservation, metadata retention | `apps/document_processing/pdf_extractor.py` | `tests/test_pdf_processing.py` |
| **§9. Chunking** | Configurable chunk size, overlap, page range preservation | `apps/document_processing/chunker.py` | `tests/test_pdf_processing.py` |
| **§10-11. RAG & Vector** | Pluggable embeddings, strict machine-filtered vector search | `integrations/embeddings/`<br>`integrations/vector_store/in_db_store.py` | `tests/test_retrieval_isolation.py` |
| **§12. Generation** | Anti-hallucination, citations, versioned system prompt | `apps/rag_engine/engine.py`<br>`apps/rag_engine/prompts/system_v1.txt` | `tests/test_rag_pipeline.py` |
| **§13. Insufficient** | Configurable threshold, explicit insufficient evidence response | `apps/rag_engine/engine.py` | `tests/test_rag_pipeline.py` |
| **§14. History** | Persist query, answer, citations, feedback rating | `apps/question_history/models.py`<br>`apps/question_history/views.py` | `tests/test_rag_pipeline.py` |
| **§15A. RBAC** | Django Groups (`Administrator`, `Engineer`, `Supervisor`), `setup_roles`, `create_demo_users` | `apps/accounts/permissions.py`<br>`apps/accounts/management/commands/setup_roles.py`<br>`create_demo_users.py` | `tests/test_rbac_permissions.py` *(MANDATORY TEST 1)* |
| **§15B. Audit Logs** | Immutable non-sensitive audit logging | `apps/audit_logs/models.py`<br>`apps/audit_logs/utils.py` | Verified in login, upload, ask events |
| **§17. Frontend** | Modern industrial SaaS layout, side-by-side evidence, role dashboards | `templates/base.html`<br>`templates/admin_dashboard/`<br>`templates/engineer_dashboard/`<br>`templates/supervisor_dashboard/` | Tested via browser & HTTP sessions |
