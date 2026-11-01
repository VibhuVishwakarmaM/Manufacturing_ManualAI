# Manufacturing Manual AI Assistant

An enterprise, evidence-grounded maintenance intelligence platform built with **Django, Django REST Framework, PostgreSQL, PyMuPDF, and AI/RAG**.

Designed specifically for manufacturing plants to allow field engineers to query equipment manuals and receive accurate, grounded answers supported by verifiable, 1-indexed PDF page citations.

---

## Key Highlights

- **Machine-Specific Retrieval Isolation (Mandatory Organizer Test 2 Passed)**: Strict SQL-level partitioning guarantees that queries for Machine A never retrieve or leak confidential manuals from Machine B.
- **Verifiable PDF Source References**: Answers cite the exact Equipment Manual Title, Revision, and 1-Indexed PDF Page Number.
- **Direct PDF Traceability**: Authorized engineers can open the original PDF document at the cited page directly in the browser.
- **Strict Anti-Hallucination & Insufficient Evidence Handling**: When an equipment manual lacks sufficient evidence, the system reports:
  > *"Insufficient information: The selected machine's available manuals do not provide enough evidence to answer this question reliably."*
- **Backend-Enforced Role-Based Access Control (Mandatory Organizer Test 1 Passed)**:
  - **Administrator**: Machinery registration, PDF manual upload and reprocessing, operator user & group management, system audit surveillance.
  - **Field Engineer**: Machine selection, evidence-grounded AI inquiries, PDF inspection, query history, and answer feedback.
  - **Plant Supervisor**: Cross-engineer query history review, documentation gap analysis (unanswered / insufficient-evidence queries).
- **Comprehensive Test Suite**: 16 automated tests covering RBAC permissions, retrieval isolation, PDF page preservation, RAG logic, and API endpoints.

---

## Technology Stack

- **Backend**: Python 3.10+, Django 5.x, Django REST Framework
- **Database**: PostgreSQL (with psycopg2-binary adapter and automatic development fallback to SQLite)
- **PDF Extraction**: PyMuPDF (`fitz`) for fast, layout-preserving 1-indexed page extraction
- **AI & Numerical**: NumPy (cosine similarity), Requests (LLM/Embedding HTTP drivers)
- **Frontend**: HTML5, CSS3 (Modern Industrial SaaS design system), JavaScript, Bootstrap 5
- **Testing**: Pytest 8.x, pytest-django

---

## Architecture Overview

```text
manufacturing_manual_ai/
│
├── config/                  # Django project configuration & environment settings
├── apps/
│   ├── accounts/            # Authentication, Django Groups (Admin, Engineer, Supervisor)
│   ├── machines/            # Equipment registry & safeguard controls
│   ├── manuals/             # PDF ingestion, validation, and storage
│   ├── document_processing/ # PyMuPDF page-by-page extractor & chunker
│   ├── rag_engine/          # Machine-isolated RAG orchestrator & system prompts
│   ├── question_history/    # Query history persistence, citations & feedback
│   ├── dashboard/           # Admin, Engineer, and Supervisor role portals
│   ├── audit_logs/          # Operational audit trail
│   └── notifications/       # System and processing alerts
│
├── integrations/
│   ├── llm/                 # BaseLLMProvider (Mock, OpenAI, Anthropic, Ollama)
│   ├── embeddings/          # BaseEmbeddingProvider (Mock, OpenAI, Local)
│   └── vector_store/        # InDatabaseVectorStore (Machine-partitioned ORM/NumPy)
│
├── templates/               # Responsive Bootstrap 5 Industrial SaaS templates
├── static/                  # Custom CSS & JavaScript controllers
├── tests/                   # 16 automated pytest unit & integration tests
├── docs/                    # 21 comprehensive reference and modification guides
└── manage.py
```

---

## Quick Start (Installation & Execution)

### 1. Clone & Set Up Environment
```bash
git clone <repository_url> manufacturing_manual_ai
cd manufacturing_manual_ai

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux / macOS

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy the example environment file:
```bash
cp .env.example .env
```
Defaults use the deterministic `mock` provider and enable SQLite fallback if a local PostgreSQL daemon is not running.

### 3. Apply Migrations & Set Up Roles
```bash
# 1. Apply database migrations
python manage.py makemigrations accounts machines manuals document_processing question_history audit_logs notifications
python manage.py migrate

# 2. Setup Administrator, Engineer, and Supervisor Groups & permissions
python manage.py setup_roles

# 3. Create demonstration accounts
python manage.py create_demo_users

# 4. Seed demo machines and verifiable synthetic PDF manuals
python manage.py seed_demo_data
```

### 4. Run Automated Tests
```bash
pytest -v
```
All 16 tests pass without requiring external API keys.

### 5. Launch the Application
```bash
python manage.py runserver 127.0.0.1:8000
```
Open your browser at **`http://127.0.0.1:8000/`**.

---

## Demonstration Credentials

The login page features **1-Click Quick-Fill buttons** for rapid testing during evaluations:

| Role | Username | Password | Access Capabilities |
|---|---|---|---|
| **Administrator** | `admin` | `AdminPass123!` | Equipment registration, manual PDF upload, reprocessing, user & role management, audit trail |
| **Field Engineer** | `engineer` | `EngineerPass123!` | Active machine selection, AI maintenance questions, verifiable citations, open PDF, personal history |
| **Plant Supervisor** | `supervisor` | `SupervisorPass123!` | Cross-engineer query history review, filter by machine, identify unanswered/insufficient evidence queries |

---

## API Overview

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/accounts/api/auth/login/` | Operator session login | Public |
| `GET` | `/accounts/api/auth/me/` | Current user profile & role | Authenticated |
| `GET` | `/machines/api/machines/` | List equipment machines | Authenticated |
| `POST` | `/machines/api/machines/` | Register new machine | Administrator |
| `GET` | `/manuals/api/manuals/` | List manuals (filterable by machine) | Authenticated |
| `POST` | `/manuals/api/manuals/` | Upload and process manual PDF | Administrator |
| `GET` | `/manuals/api/manuals/{id}/status/` | Ingestion & indexing status | Authenticated |
| `POST` | `/questions/api/questions/ask/` | Ask machine-isolated RAG question | Authenticated |
| `GET` | `/questions/api/questions/history/` | Personal question history | Authenticated |
| `POST` | `/questions/api/questions/{id}/feedback/` | Submit helpful/unhelpful rating | Authenticated |
| `GET` | `/questions/api/supervisor/history/` | Cross-engineer query history | Supervisor / Admin |
| `GET` | `/questions/api/supervisor/unanswered/` | Insufficient evidence queries | Supervisor / Admin |
| `GET` | `/dashboard/api/dashboard/summary/` | Operational KPI metrics | Authenticated |

---

## Hackathon-Day Rapid Configuration

The application is built for instant event-day adaptation:
1. **Switch LLM / Embeddings**: Update `LLM_PROVIDER` and `EMBEDDING_PROVIDER` in `.env` (options: `openai`, `anthropic`, `ollama`, `mock`).
2. **Upload Actual Manuals**: Log in as `admin`, register the 3 machines, and upload the organizer's PDFs via the web interface.
3. **Inspect Page References**: Click the cited PDF icon to view the source PDF at the exact page.
4. Detailed step-by-step instructions: see [`docs/EVENT_DAY_MODIFICATION_GUIDE.md`](docs/EVENT_DAY_MODIFICATION_GUIDE.md).

---

## Documentation Index

The `docs/` folder contains 21 comprehensive architectural and procedural guides:
- [Project Overview](docs/PROJECT_OVERVIEW.md)
- [Requirements Compliance Matrix](docs/REQUIREMENTS_MAPPING.md)
- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Complete End-to-End Workflow](docs/COMPLETE_WORKFLOW.md)
- [Database Schema Specification](docs/DATABASE_DESIGN.md)
- [REST API Documentation](docs/API_DOCUMENTATION.md)
- [RAG Retrieval Pipeline](docs/RAG_PIPELINE.md)
- [PDF Extraction with PyMuPDF](docs/PDF_PROCESSING.md)
- [Vector Retrieval & Isolation](docs/VECTOR_RETRIEVAL.md)
- [Role-Based Access Control](docs/ROLE_PERMISSIONS.md)
- [Authentication & Django Groups](docs/AUTHENTICATION_AND_GROUPS.md)
- [User Management Administration](docs/USER_MANAGEMENT.md)
- [Audit Logging Subsystem](docs/AUDIT_LOGGING.md)
- [Security & Access Control](docs/SECURITY_AND_ACCESS_CONTROL.md)
- [System Configuration Guide](docs/CONFIGURATION_GUIDE.md)
- [Testing & Validation Guide](docs/TESTING_GUIDE.md)
- [5-Minute Demonstration Guide](docs/DEMONSTRATION_GUIDE.md)
- [Event-Day Rapid Modification Guide](docs/EVENT_DAY_MODIFICATION_GUIDE.md)
- [Troubleshooting & FAQ](docs/TROUBLESHOOTING.md)
- [Project Directory Structure](docs/PROJECT_FOLDER_STRUCTURE.md)
- [Developer Setup Guide](docs/DEVELOPER_SETUP_GUIDE.md)
