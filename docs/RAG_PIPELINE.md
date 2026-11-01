# RAG Retrieval-Augmented Generation Pipeline

## 1. Pipeline Overview
The RAG pipeline is designed to eliminate hallucination in manufacturing equipment operations. It enforces an evidence-grounded paradigm: **No evidence, no answer.**

```text
Engineer Question
       |
       v
1. Selected Machine Validation
   (Ensures machine exists and is in ACTIVE status)
       |
       v
2. Question Embedding Generation
   (Vector computed via configured Embedding Provider)
       |
       v
3. Machine-Scoped Vector Retrieval
   (Strict WHERE machine_id = selected_machine partition)
       |
       v
4. Evidence Relevance Validation
   (Filter by SIMILARITY_THRESHOLD; check top_score >= threshold)
       |
       v
   +---[ Score < Threshold OR Empty Chunks ]---> Return "Insufficient information: The selected
   |                                             machine's available manuals do not provide enough
   v                                             evidence to answer this question reliably."
5. Context Construction
   (Format structured evidence with manual title, revision, page)
       |
       v
6. LLM Generation
   (Prompt: system_v1.txt with anti-hallucination guardrails)
       |
       v
7. Citation Extraction & Validation
   (Verify citations match retrieved chunks; prevent phantom citations)
       |
       v
8. Response & Persistence
   (Return answer + citations + evidence; persist to QuestionHistory)
```

---

## 2. Anti-Hallucination Guardrails
1. **Machine-Level Scope Enforcement**: A database index constraint ensures retrieval queries only search `DocumentChunk` records matching `machine_id`. Even if another machine's manual has an exact keyword match, it is barred from SQL retrieval.
2. **Deterministic Fallback**: If retrieved passages fail the cosine similarity threshold, the pipeline short-circuits without calling the LLM, immediately returning the standard insufficient evidence statement.
3. **Structured System Prompting**: System prompt strictly forbids guessing numerical tolerances, pressures, or torque values.
4. **Citation Verification**: Every citation returned to the engineer maps to a valid `manual_id` and 1-indexed `page_number` in storage.
