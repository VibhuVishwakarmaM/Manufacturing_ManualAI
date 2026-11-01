# System Architecture

## 1. High-Level Architecture Diagram

```mermaid
graph TD
    Client[Web Browser / REST Client] --> WebLayer[Django Web & REST API Layer]
    
    subgraph Security_and_Auth [Security & Access Control]
        WebLayer --> Auth[Django Authentication]
        Auth --> RBAC[Role-Based Groups: Admin, Engineer, Supervisor]
        WebLayer --> Audit[Audit Logging Subsystem]
    end

    subgraph App_Modules [Core Application Modules]
        WebLayer --> MachApp[apps.machines]
        WebLayer --> ManApp[apps.manuals]
        WebLayer --> DashApp[apps.dashboard]
        WebLayer --> HistApp[apps.question_history]
    end

    subgraph Ingestion_Pipeline [Document Ingestion & Indexing]
        ManApp --> Extractor[apps.document_processing: PyMuPDF Extractor]
        Extractor --> Chunker[apps.document_processing: Document Chunker]
        Chunker --> EmbDriver[integrations.embeddings: BaseEmbeddingProvider]
        EmbDriver --> VecStore[integrations.vector_store: InDatabaseVectorStore]
    end

    subgraph RAG_Engine [Inference & Evidence Grounding]
        HistApp --> RAGOrchestrator[apps.rag_engine: RAGEngine]
        RAGOrchestrator -->|Strict Machine Filter| VecStore
        RAGOrchestrator --> PromptTemplate[apps.rag_engine.prompts: System Prompt]
        RAGOrchestrator --> LLMDriver[integrations.llm: BaseLLMProvider]
        LLMDriver --> ResponseValidator[Citation & Sufficiency Validator]
        ResponseValidator --> HistApp
    end

    subgraph Persistence_Layer [Database Storage]
        MachApp --> DB[(PostgreSQL / SQLite)]
        ManApp --> DB
        VecStore --> DB
        HistApp --> DB
        Audit --> DB
    end
```

---

## 2. Component Decoupling & Interfaces

### 1. Ingestion Decoupling
The PDF extraction service (`PyMuPDFExtractor`) only interacts with binary PDF data and produces structured page dictionaries (`page_number`, `text`, `char_count`). It has no knowledge of database models or embedding services. The `DocumentChunker` processes arbitrary page text arrays and applies overlap while retaining page bounds.

### 2. Embedding Driver Decoupling
All embedding operations adhere to `BaseEmbeddingProvider` (`embed_text`, `embed_batch`, `dimension`). Switching from local/mock embeddings to OpenAI or a self-hosted Sentence Transformer requires updating `EMBEDDING_PROVIDER` in `.env` without touching document extraction or the vector store.

### 3. Vector Retrieval & Machine Isolation
The vector store (`BaseVectorStore`) enforces `machine_id` partitioning. Queries filter by `machine_id` at the database index layer before computing vector similarity. This guarantees that Machine A never evaluates passages from Machine B.

### 4. LLM Provider Decoupling
The generation layer adheres to `BaseLLMProvider` (`generate_answer`). Whether running `mock`, `openai` (GPT-4o), `anthropic` (Claude 3.5 Sonnet), or `ollama` (Llama 3), the input/output schema remains identical.
