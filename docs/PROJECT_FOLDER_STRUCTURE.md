# Complete Project Folder Structure

```text
e:/Manufacturing_ManualAI/
│
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                   # Central settings, AI config, DB fallback
│   │   ├── development.py            # Local development settings
│   │   └── production.py             # Strict production settings
│   ├── urls.py                       # Root URL routing table
│   ├── wsgi.py                       # WSGI entrypoint
│   └── asgi.py                       # ASGI entrypoint
│
├── apps/
│   ├── accounts/                     # Authentication, RBAC, Users & Roles
│   │   ├── management/commands/
│   │   │   ├── setup_roles.py        # Automated Django Groups configuration
│   │   │   └── create_demo_users.py  # Demo accounts initializer
│   │   ├── permissions.py            # IsAdministrator, IsEngineer, IsSupervisor
│   │   ├── serializers.py            # DRF serializers
│   │   ├── views.py                  # Web & API controllers
│   │   └── urls.py
│   │
│   ├── machines/                     # Equipment Machine Registry
│   │   ├── management/commands/
│   │   │   └── seed_demo_data.py     # Demo equipment & synthetic PDF generator
│   │   ├── models.py                 # Machine model
│   │   ├── serializers.py
│   │   ├── views.py                  # Machine CRUD & safeguard checks
│   │   └── urls.py
│   │
│   ├── manuals/                      # PDF Manual Ingestion & Lifecycle
│   │   ├── models.py                 # Manual model & status choices
│   │   ├── validators.py             # PyMuPDF integrity & size validation
│   │   ├── serializers.py
│   │   ├── views.py                  # Upload, authorized view, download, reprocess
│   │   └── urls.py
│   │
│   ├── document_processing/          # PyMuPDF Extraction & Chunking Engine
│   │   ├── models.py                 # DocumentChunk with page boundaries & embeddings
│   │   ├── pdf_extractor.py          # PyMuPDF page-by-page text extractor
│   │   ├── chunker.py                # Page-attributed sliding window chunker
│   │   └── processor.py              # Ingestion orchestrator
│   │
│   ├── rag_engine/                   # Retrieval-Augmented Generation Subsystem
│   │   ├── prompts/
│   │   │   └── system_v1.txt         # Versioned industrial system prompt
│   │   └── engine.py                 # RAGEngine with strict machine isolation
│   │
│   ├── question_history/             # Persistent History & Feedback
│   │   ├── models.py                 # QuestionHistory & AnswerFeedback
│   │   ├── serializers.py
│   │   ├── views.py                  # Q&A API, personal & supervisor history
│   │   └── urls.py
│   │
│   ├── dashboard/                    # Role-Specific Dashboards
│   │   ├── context_processors.py     # Global role & AI metadata
│   │   ├── views.py                  # Admin, Engineer, Supervisor views
│   │   └── urls.py
│   │
│   ├── audit_logs/                   # Non-Sensitive Operational Audit Trail
│   │   ├── models.py                 # AuditLog model
│   │   ├── utils.py                  # sanitize_metadata, log_audit_event
│   │   ├── views.py
│   │   └── urls.py
│   │
│   └── notifications/                # In-App Notifications
│       ├── models.py
│       └── utils.py
│
├── integrations/
│   ├── llm/                          # Pluggable LLM Drivers
│   │   ├── base.py                   # BaseLLMProvider interface
│   │   ├── mock_provider.py          # Deterministic mock provider
│   │   ├── openai_provider.py        # OpenAI GPT driver
│   │   ├── anthropic_provider.py     # Anthropic Claude driver
│   │   ├── ollama_provider.py        # Local Ollama driver
│   │   └── factory.py                # LLM factory
│   │
│   ├── embeddings/                   # Pluggable Embedding Drivers
│   │   ├── base.py                   # BaseEmbeddingProvider interface
│   │   ├── mock_provider.py          # TF / Hash unit-length vectorizer
│   │   ├── openai_provider.py        # OpenAI text-embedding driver
│   │   ├── local_provider.py         # Local offline vectorizer
│   │   └── factory.py                # Embedding factory
│   │
│   └── vector_store/                 # Vector Store Abstraction
│       ├── base.py                   # BaseVectorStore interface
│       ├── in_db_store.py            # Machine-isolated ORM & NumPy vector store
│       └── factory.py                # Vector store factory
│
├── templates/                        # Bootstrap 5 Modern Industrial SaaS UI
│   ├── base.html                     # Main shell layout with role indicator
│   ├── accounts/
│   │   ├── login.html                # Login with role quick-fill buttons
│   │   └── user_management.html      # Admin operator & RBAC management
│   ├── admin_dashboard/
│   │   ├── index.html                # Admin operations hub
│   │   └── system_config.html        # Active runtime configuration
│   ├── engineer_dashboard/
│   │   └── index.html                # Machine selector, Q&A, and citation viewer
│   ├── supervisor_dashboard/
│   │   └── index.html                # Cross-engineer audit & gap analytics
│   ├── machines/
│   │   ├── machine_list.html
│   │   └── machine_form.html
│   ├── manuals/
│   │   ├── manual_list.html
│   │   └── manual_upload.html
│   └── audit_logs/
│       └── audit_list.html
│
├── static/
│   ├── css/industrial_saas.css       # Industrial design system
│   └── js/app.js                     # Real-time Q&A client controller
│
├── media/                            # Uploaded & generated equipment manuals
├── tests/                            # Automated Pytest Suite
│   ├── test_rbac_permissions.py      # Mandatory Test 1: RBAC enforcement
│   ├── test_retrieval_isolation.py   # Mandatory Test 2: Machine isolation
│   ├── test_pdf_processing.py        # PyMuPDF page preservation
│   ├── test_rag_pipeline.py          # Grounded answers & insufficient info
│   └── test_api_endpoints.py         # REST API test suite
│
├── docs/                             # Complete Documentation (21 Guides)
├── manage.py
├── requirements.txt
├── pytest.ini
├── .env.example
├── .env
└── README.md
```
