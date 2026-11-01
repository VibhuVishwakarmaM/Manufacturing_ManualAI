# Troubleshooting & Operational FAQ

## 1. Common Issues and Resolutions

### Issue: "psycopg2: connection to server at 'localhost' (127.0.0.1), port 5432 failed"
- **Cause**: PostgreSQL server is not installed or not currently running on host.
- **Resolution**:
  - The project is configured with `USE_SQLITE_FALLBACK=True` in `.env`.
  - When PostgreSQL is unreachable, the system automatically falls back to SQLite so local development and testing never stall.
  - To connect to a live PostgreSQL server, start your Postgres service (`net start postgresql` or Docker) and configure `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` in `.env`.

### Issue: "Upload fails: Invalid or corrupted PDF"
- **Cause**: The uploaded file has zero bytes, an invalid header, or is not a readable PDF.
- **Resolution**: PyMuPDF tests PDF structure upon upload. Verify that the file can be opened locally in a PDF viewer.

### Issue: "Insufficient information returned on supported questions"
- **Cause**: `SIMILARITY_THRESHOLD` is set too high for the active embedding model.
- **Resolution**:
  - For `MockEmbeddingProvider`, set `SIMILARITY_THRESHOLD=0.35` in `.env`.
  - For `OpenAIEmbeddingProvider` (`text-embedding-3-small`), set `SIMILARITY_THRESHOLD=0.65`.

### Issue: "Port 8000 already in use"
- **Resolution**:
  Run server on another port:
  ```bash
  python manage.py runserver 127.0.0.1:8080
  ```

### Issue: "Tests fail with fixture AttributeError in pytest"
- **Resolution**:
  Use `pytest<9.0.0` (specifically pytest 8.3 or 8.4):
  ```bash
  pip install "pytest<9.0.0"
  ```
