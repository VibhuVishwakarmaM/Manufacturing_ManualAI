# Configuration Guide

The application is completely configurable via `.env` without modifying Python code.

---

## 1. Environment Variable Reference

### Core Django
| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(django secret)* | Django crypto secret key |
| `DEBUG` | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated list of permitted host headers |

### Database (PostgreSQL)
| Variable | Default | Description |
|---|---|---|
| `DB_ENGINE` | `django.db.backends.postgresql` | Database engine adapter |
| `DB_NAME` | `manufacturing_manuals` | PostgreSQL database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | `postgres` | Database password |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |
| `USE_SQLITE_FALLBACK` | `True` | Fall back to SQLite if Postgres unreachable |

### AI LLM Provider
| Variable | Options | Default | Description |
|---|---|---|---|
| `LLM_PROVIDER` | `mock`, `openai`, `anthropic`, `ollama` | `mock` | Active generation provider |
| `LLM_MODEL` | *(provider model string)* | `gpt-4o-mini` | Model identifier |
| `LLM_API_KEY` | *(api key string)* | `""` | Provider authentication key |
| `LLM_API_BASE_URL` | `http://localhost:11434` / `...` | `https://api.openai.com/v1` | Custom endpoint URL |

### Embeddings & Vector Store
| Variable | Options | Default | Description |
|---|---|---|---|
| `EMBEDDING_PROVIDER` | `mock`, `openai`, `local` | `mock` | Embedding engine |
| `EMBEDDING_MODEL` | *(model string)* | `text-embedding-3-small` | Model name |
| `EMBEDDING_API_KEY` | *(api key string)* | `""` | Embedding provider API key |
| `EMBEDDING_DIMENSION` | `128`, `1536`, `256` | `128` (or 1536 for OpenAI) | Dimensionality of vectors |
| `VECTOR_STORE_PROVIDER` | `in_db`, `postgres`, `sqlite` | `in_db` | Storage and retrieval driver |

### Chunking & Retrieval Parameters
| Variable | Default | Description |
|---|---|---|
| `CHUNK_SIZE` | `500` | Target character size per text chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between adjacent chunks |
| `TOP_K` | `4` | Max passages passed to context |
| `SIMILARITY_THRESHOLD` | `0.35` (mock) / `0.65` (dense) | Minimum cosine similarity to consider evidence |
| `RAG_PROMPT_VERSION` | `v1` | System prompt version located in `apps/rag_engine/prompts/` |
| `MAX_UPLOAD_SIZE_MB` | `25` | Maximum PDF file upload size limit |
