# Developer Setup Guide

## 1. Prerequisites
- Python 3.10+ installed
- PostgreSQL 14+ (optional for production; SQLite automatic fallback supported for rapid local testing)
- Git

---

## 2. Installation Steps

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone <repo-url> manufacturing_manual_ai
cd manufacturing_manual_ai
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure `USE_SQLITE_FALLBACK=True` if you do not have an active local PostgreSQL daemon running.

### Step 4: Apply Database Migrations
```bash
python manage.py makemigrations accounts machines manuals document_processing question_history audit_logs notifications
python manage.py migrate
```

### Step 5: Initialize Django Groups & Demo Accounts
```bash
# 1. Setup Administrator, Engineer, and Supervisor Groups and assign model permissions
python manage.py setup_roles

# 2. Seed standard demonstration accounts
python manage.py create_demo_users
```

### Step 6: Seed Demo Machinery & Verifiable Technical Manuals
```bash
python manage.py seed_demo_data
```
This generates synthetic PDF equipment manuals for:
- `CNC Vertical Machining Center VF-2SS` (Spindle lubrication specs)
- `Heavy Hydraulic Stamping Press HP-500` (Hydraulic circuit specs)

### Step 7: Run Automated Tests
```bash
pytest -v
```
All 16 tests should pass.

### Step 8: Start the Local Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open `http://127.0.0.1:8000/` in your browser.
