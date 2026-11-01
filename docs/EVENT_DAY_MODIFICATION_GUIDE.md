# Event-Day Rapid Modification & Onboarding Guide

## 1. Overview
On hackathon day, the organizers will release the official problem input pack containing:
1. Specific machine names and model numbers.
2. 3 official equipment manual PDFs.
3. Specific revision numbers and technical specifications.
4. Designated LLM / Embedding credentials or local endpoints.

This guide provides the exact steps, files to edit, and commands to run to adapt the application in **under 5 minutes** without rewriting code.

---

## 2. Step-by-Step Adaptation Runbook

### Step 1: Switch AI / LLM Provider & Credentials
Open `.env` in the project root:

#### Scenario A: Using OpenAI (e.g. GPT-4o-mini & text-embedding-3-small)
```ini
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-proj-YOUR-ORGANIZER-OPENAI-KEY
LLM_API_BASE_URL=https://api.openai.com/v1

EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=sk-proj-YOUR-ORGANIZER-OPENAI-KEY
EMBEDDING_DIMENSION=1536

SIMILARITY_THRESHOLD=0.65
```

#### Scenario B: Using Local Ollama (e.g. Llama-3 & Local Embeddings)
```ini
LLM_PROVIDER=ollama
LLM_MODEL=llama3
LLM_API_BASE_URL=http://localhost:11434

EMBEDDING_PROVIDER=local
SIMILARITY_THRESHOLD=0.35
```

#### Scenario C: Using Anthropic Claude 3.5 Sonnet
```ini
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_API_KEY=sk-ant-YOUR-KEY
```

---

### Step 2: Register the Actual Machines
You can register machines directly in the **Administrator Web Interface** or via Django management command.

#### Option A: Via Web UI
1. Log in at `http://localhost:8000/accounts/login/` with username `admin` / password `AdminPass123!`.
2. Navigate to **Machines** (`/machines/`) -> Click **Register New Machine**.
3. Input the organizer's exact Machine Name, Model Number, and Manufacturer.
4. Repeat for all 3 machines.

#### Option B: Via Python Shell
```bash
python manage.py shell -c "from apps.machines.models import Machine; Machine.objects.create(name='Actual Machine A', model_number='M-100');"
```

---

### Step 3: Ingest the Official PDF Manuals
1. In the Admin Portal, click **Upload Manual PDF** (`/manuals/upload/`).
2. Select the target machine from the dropdown.
3. Enter the official **Manual Title** and **Revision** (e.g. `Rev 2.4`).
4. Select the organizer's PDF file and click **Upload and Index Manual**.
5. The pipeline automatically:
   - Validates PDF structure with PyMuPDF.
   - Extracts page-by-page text preserving 1-indexed page boundaries.
   - Chunks the text with page metadata.
   - Generates embeddings with the newly configured model.
   - Indexes chunks strictly into the machine's vector partition.

---

### Step 4: Adjust Chunking Settings & Retrieval Thresholds
If the organizer's manuals contain very dense technical tables or long procedures, adjust `.env`:
```ini
# Increase chunk size if paragraphs are long
CHUNK_SIZE=700
CHUNK_OVERLAP=150

# Adjust Top-K returned evidence passages
TOP_K=5

# Evidence confidence threshold
SIMILARITY_THRESHOLD=0.65
```
After changing chunking or embedding models, re-index existing documents:
- Click the **Reprocess Document** button in the Web UI (`/manuals/`), OR
- Run:
  ```bash
  python manage.py shell -c "from apps.manuals.models import Manual; from apps.document_processing.processor import process_manual; [process_manual(m.id, force_reprocess=True) for m in Manual.objects.all()];"
  ```

---

### Step 5: Update Prompt Template (If Requested by Judges)
Prompts are versioned in `apps/rag_engine/prompts/`:
- Edit `apps/rag_engine/prompts/system_v1.txt` or create `system_v2.txt`.
- Set `RAG_PROMPT_VERSION=v2` in `.env`.
- No server restart required!

---

### Step 6: Verify and Run Automated Tests
Execute the test suite to ensure RBAC and machine isolation remain 100% intact:
```bash
pytest -v
```
All 16 tests must report green.
