# Complete End-to-End Workflow

This document illustrates the three primary lifecycle workflows supported by the system: Ingestion, Inference, and Supervisory Audit.

---

## Workflow 1: Administrator Equipment & Manual Ingestion

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrator
    participant Web as Django Web UI / API
    participant DB as PostgreSQL Database
    participant Extractor as PyMuPDF Extractor
    participant Chunker as Document Chunker
    participant Emb as Embedding Provider
    participant Vec as Vector Store

    Admin->>Web: Log in (Authenticated as Administrator)
    Admin->>Web: Register Equipment Machine (Name, Model, Specs)
    Web->>DB: Insert Machine record
    Admin->>Web: Upload Manual PDF (Assign to Machine, specify Title & Revision)
    Web->>Web: Validate extension (.pdf), size limit (25MB), PyMuPDF readability
    Web->>DB: Save Manual (Status: UPLOADED)
    Web->>Extractor: Open PDF by stream/path
    Extractor-->>Web: Return 1-indexed pages (text, page_number)
    Web->>Chunker: Segment pages into chunks (size: 500, overlap: 100)
    Chunker-->>Web: Chunks with metadata (page_start, page_end, machine_id)
    Web->>Emb: Batch generate embeddings
    Emb-->>Web: Array of vector floats
    Web->>Vec: Store DocumentChunk records in DB
    Web->>DB: Update Manual (Status: INDEXED, page_count, chunk_count)
    Web-->>Admin: Show success notification & ingestion metrics
```

---

## Workflow 2: Engineer Machine Selection & Question Answering

```mermaid
sequenceDiagram
    autonumber
    actor Eng as Field Engineer
    participant Web as Engineer Assistant UI
    participant RAG as RAG Engine
    participant Vec as Vector Store
    participant LLM as LLM Provider
    participant DB as Question History DB

    Eng->>Web: Log in (Authenticated as Engineer)
    Eng->>Web: Select Machine from Equipment Dropdown
    Web-->>Eng: Display Machine Specs & Available Manuals
    Eng->>Web: Enter maintenance question
    Web->>RAG: answer_question(user, machine_id, question)
    RAG->>Vec: search(q_vec, machine_id, top_k, threshold)
    Note over Vec: Strictly filters SQL where machine_id = selected_machine
    Vec-->>RAG: Return candidate passages with scores & citations
    alt Evidence is below threshold or empty
        RAG->>DB: Persist Question (Status: INSUFFICIENT_EVIDENCE)
        RAG-->>Web: Return "Insufficient information: The selected machine's available manuals do not provide enough evidence to answer this question reliably."
    else Evidence is sufficient
        RAG->>LLM: Generate answer using system prompt + retrieved passages
        LLM-->>RAG: Synthesized answer referencing manual, revision, and page
        RAG->>DB: Persist Question (Status: ANSWERED, evidence, citations)
        RAG-->>Web: Return answer + citations + evidence snippets
    end
    Web-->>Eng: Render side-by-side Answer and Verifiable Citation Cards
    Eng->>Web: Click "View PDF at Page" to inspect original document
    Eng->>Web: Submit accuracy feedback (Helpful / Unhelpful)
```

---

## Workflow 3: Supervisor Review & Documentation Gap Auditing

```mermaid
sequenceDiagram
    autonumber
    actor Sup as Plant Supervisor
    participant Web as Supervisor Hub
    participant DB as PostgreSQL Database

    Sup->>Web: Log in (Authenticated as Supervisor)
    Sup->>Web: Open Supervisory Surveillance Dashboard
    Web->>DB: Query aggregate KPIs (Total queries, Verified, Insufficient)
    Web-->>Sup: Display operational KPI cards
    Sup->>Web: Filter by Status = "INSUFFICIENT_EVIDENCE"
    Web->>DB: Retrieve queries where status = INSUFFICIENT_EVIDENCE
    Web-->>Sup: Display queries engineers asked that manuals could not answer
    Sup->>Sup: Identify equipment manual documentation gaps to request from OEM
```
