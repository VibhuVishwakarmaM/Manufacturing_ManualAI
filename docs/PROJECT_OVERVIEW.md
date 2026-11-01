# Project Overview: Manufacturing Manual AI Assistant

## 1. Executive Summary
The **Manufacturing Manual AI Assistant** is a specialized, production-minded industrial SaaS application developed for a Python Full Stack & AI Hackathon. 

In industrial production lines, equipment downtime costs thousands of dollars per minute. Maintenance engineers must troubleshoot complex machinery quickly by consulting lengthy technical equipment manuals. Traditional keyword search often fails to capture operational nuances, while generic AI chatbots suffer from hallucinations and lack verifiable citations.

This application provides:
- **Equipment-Scoped Knowledge Retrieval**: RAG retrieval bounded strictly to the selected equipment machine, preventing cross-machine information leakage.
- **Verifiable Evidence Grounding**: Answers cite the exact manual title, revision, and 1-indexed PDF page number, allowing engineers to verify procedures instantly.
- **Direct PDF Traceability**: Operators can open the original PDF at the cited page directly from the user interface.
- **Strict Anti-Hallucination & Insufficient-Evidence Guardrails**: If an equipment manual lacks sufficient evidence for a question, the assistant explicitly states the lack of documentation rather than fabricating answers.
- **Role-Based Access Control (RBAC)**: Backend-enforced permissions for Administrators, Field Engineers, and Plant Supervisors.
- **Operational Auditing**: Non-sensitive logging of all queries, ingestion tasks, and administrative updates.

---

## 2. Target Users & Personas

### Administrator (Plant Engineering Lead)
- **Goals**: Register equipment machines, upload manufacturer PDF manuals, manage OCR/text extraction and vector indexing lifecycles, configure AI providers and retrieval thresholds, assign operator roles.
- **Access**: Full read/write access to machinery, manuals, user accounts, and system configuration.

### Field Engineer (Maintenance Technician)
- **Goals**: Select active line equipment, ask technical troubleshooting and maintenance procedure questions, inspect supporting evidence passages, open source PDF pages, revisit query history, and submit accuracy feedback.
- **Access**: Read-only access to equipment and manuals; write access to queries and feedback; strictly barred from administrative actions.

### Plant Supervisor (Operations Manager)
- **Goals**: Monitor maintenance inquiries across all field engineers, identify documentation gaps (queries marked `INSUFFICIENT_EVIDENCE`), filter historical queries by machine and status, review operator feedback.
- **Access**: Read-only access across all equipment, manuals, audit logs, and cross-engineer question history.

---

## 3. Technology Stack Summary
- **Backend**: Python 3.10+, Django 5.x, Django REST Framework.
- **Database**: PostgreSQL (with psycopg2 adapter and SQLite development fallback).
- **PDF Extraction**: PyMuPDF (`fitz`) with 1-indexed page preservation.
- **AI / RAG**: Pluggable provider architecture supporting OpenAI, Anthropic, Ollama, and deterministic Mock providers.
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Bootstrap 5 (Modern Industrial SaaS aesthetic).
- **Testing**: Pytest, pytest-django.
