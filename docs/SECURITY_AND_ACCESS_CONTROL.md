# Security and Access Control

## 1. Threat Model & Mitigations

### 1. Cross-Machine Information Leakage (Critical)
- **Risk**: An engineer asking about Machine A receives confidential, incompatible, or hazardous torque/pressure instructions from Machine B.
- **Mitigation**: The retrieval layer partitions queries at the SQL layer with `WHERE machine_id = :id`. Passages from outside the selected machine cannot be evaluated by the similarity engine or passed to the LLM.

### 2. Unauthorized Document Access
- **Risk**: An unauthenticated user downloads proprietary equipment PDFs directly.
- **Mitigation**: File downloads and views are routed through Django controller views (`manual_view_pdf_view` and `manual_download_pdf_view`) protected by `@login_required` and object existence validation. Direct media directory browsing is disabled.

### 3. Privilege Escalation
- **Risk**: An engineer attempts to upload a PDF or grant themselves Administrator rights via API.
- **Mitigation**: All modification endpoints are protected with DRF permission classes (`IsAdministrator`). Unit tests explicitly verify that unauthorized API calls return `403 Forbidden`.

### 4. Injection and Malicious PDF Uploads
- **Risk**: An attacker uploads a shell script or corrupted binary disguised as a PDF.
- **Mitigation**: The upload validator (`validate_pdf_file`) checks file extension, enforces max file size (25MB), and verifies that PyMuPDF can parse the PDF structure without errors before saving to disk.

### 5. Secrets Management
- **Risk**: API keys or database passwords committed to version control.
- **Mitigation**: All secrets are loaded from `.env` via `python-dotenv`. `.env.example` provides sanitized defaults with mock providers. The System Config admin page redacts sensitive keys.
