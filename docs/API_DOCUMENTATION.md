# REST API Documentation

All API endpoints require authentication via Session or Basic Auth unless explicitly marked Public.

---

## 1. Authentication Endpoints

### `POST /accounts/api/auth/login/`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "username": "engineer",
    "password": "EngineerPass123!"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "message": "Login successful.",
    "user": {
      "id": 2,
      "username": "engineer",
      "email": "engineer@manufacturing-ai.internal",
      "role": "Engineer"
    }
  }
  ```

### `POST /accounts/api/auth/logout/`
- **Access**: Authenticated
- **Response (200 OK)**: `{"message": "Logged out successfully."}`

### `GET /accounts/api/auth/me/`
- **Access**: Authenticated
- **Response (200 OK)**: Returns currently logged-in user profile with assigned role.

---

## 2. Equipment Machines Endpoints

### `GET /machines/api/machines/`
- **Access**: Authenticated (All Roles)
- **Response (200 OK)**: List of machines with status and manual counts.

### `POST /machines/api/machines/`
- **Access**: `Administrator` Only
- **Request Body**:
  ```json
  {
    "name": "Haas VF-2SS CNC",
    "model_number": "VF2SS-2024",
    "manufacturer": "Haas Automation",
    "description": "5-axis mill",
    "status": "ACTIVE"
  }
  ```
- **Response (201 Created)**: Machine record.

### `DELETE /machines/api/machines/{id}/?force=true`
- **Access**: `Administrator` Only
- **Response (204 No Content)**: Machine deleted. If manuals exist and `?force=true` is not passed, returns `400 Bad Request`.

---

## 3. Manuals Endpoints

### `GET /manuals/api/manuals/?machine={machine_id}`
- **Access**: Authenticated (All Roles)
- **Response (200 OK)**: List of manuals, filterable by machine.

### `POST /manuals/api/manuals/`
- **Access**: `Administrator` Only (Multipart Form Data)
- **Fields**: `machine` (UUID), `title` (str), `revision` (str), `file` (PDF file).
- **Response (201 Created)**: Manual record with ingestion initiated.

### `POST /manuals/api/manuals/{id}/process/`
- **Access**: `Administrator` Only
- **Response (200 OK)**: `{"status": "SUCCESS", "page_count": 12, "chunk_count": 28}`

### `GET /manuals/api/manuals/{id}/status/`
- **Access**: Authenticated
- **Response (200 OK)**:
  ```json
  {
    "manual_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "title": "VF-2SS Maintenance Manual",
    "processing_status": "INDEXED",
    "page_count": 2,
    "chunk_count": 3
  }
  ```

---

## 4. Question & RAG Endpoints

### `POST /questions/api/questions/ask/`
- **Access**: Authenticated (`Engineer`, `Administrator`, `Supervisor`)
- **Request Body**:
  ```json
  {
    "machine_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "question": "What is the recommended spindle bearing lubrication procedure?"
  }
  ```
- **Response (200 OK - Answered)**:
  ```json
  {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "machine_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "machine_name": "CNC Vertical Machining Center VF-2SS",
    "question": "What is the recommended spindle bearing lubrication procedure?",
    "answer": "**Direct Answer:** Based on VF-2SS Maintenance & Lubrication Manual (2024.1), page 2: Use Mobil SHC 625 synthetic oil...",
    "status": "ANSWERED",
    "confidence_score": 0.82,
    "citations": [
      {
        "manual_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "manual_title": "VF-2SS Maintenance & Lubrication Manual",
        "revision": "2024.1",
        "page_number": 2,
        "similarity_score": 0.82,
        "snippet": "SPINDLE BEARING LUBRICATION PROCEDURE: 1. The high-speed spindle bearings require Mobil SHC 625..."
      }
    ]
  }
  ```
- **Response (200 OK - Insufficient Evidence)**:
  ```json
  {
    "id": "...",
    "status": "INSUFFICIENT_EVIDENCE",
    "answer": "Insufficient information: The selected machine's available manuals do not provide enough evidence to answer this question reliably.",
    "citations": [],
    "evidence": []
  }
  ```

### `POST /questions/api/questions/{id}/feedback/`
- **Access**: Authenticated
- **Request Body**: `{"rating": "HELPFUL", "feedback_text": "Verified with manual page 2."}`

---

## 5. Supervisor Analytics Endpoints

### `GET /questions/api/supervisor/history/?machine={id}&status={status}`
- **Access**: `Supervisor` or `Administrator`
- **Response (200 OK)**: Cross-engineer question log.

### `GET /questions/api/supervisor/unanswered/`
- **Access**: `Supervisor` or `Administrator`
- **Response (200 OK)**: Filtered list of queries marked `INSUFFICIENT_EVIDENCE` or `FAILED`.
