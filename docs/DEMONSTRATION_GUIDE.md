# Hackathon Demonstration Guide

Follow this 5-minute script to demonstrate the application to judges.

---

## 1. Setup & Demo Initialization (30 Seconds)
1. Start the server:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```
2. Open browser at `http://127.0.0.1:8000/`.
3. Highlight the **Demo Role Quick-Fill** buttons on the login screen (`Admin`, `Engineer`, `Supervisor`).

---

## 2. Act I: Administrator Operations & Manual Ingestion (1.5 Minutes)
1. Click **Admin Quick-Fill** -> Click **Authenticate & Enter System**.
2. **Show Admin Operations Hub**:
   - Total Registered Machines (2 seeded machines).
   - Ingestion status table showing `INDEXED` status, page counts, and chunk counts.
3. **Demonstrate Upload Safeguards & PyMuPDF**:
   - Go to **Manuals** -> Show the ingested `VF-2SS Maintenance & Lubrication Manual` and `HP-500 Hydraulic Manual`.
   - Click **View PDF** to demonstrate that original PDFs are accessible to authorized users directly in the browser.
4. **Show RBAC User Management**:
   - Go to **Users & Roles** (`/accounts/users/`).
   - Demonstrate the three Django Groups (`Administrator`, `Engineer`, `Supervisor`).
   - Show how administrators can deactivate an operator or reassign groups dynamically.

---

## 3. Act II: Field Engineer Evidence-Grounded AI Assistance (2 Minutes)
1. Sign out and click **Engineer Quick-Fill** -> Sign in as `engineer`.
2. Notice the role badge switches to cyan **ENGINEER** and navigation adapts to technical maintenance workflows.
3. **Machine Selection & Scope Isolation**:
   - Select `CNC Vertical Machining Center VF-2SS`.
   - Point out the active scope badge: **"Scope: CNC Vertical Machining Center VF-2SS ONLY"**.
4. **Scenario A: Answering Supported Maintenance Question**:
   - Click the preset: *"What is the recommended spindle lubrication procedure and interval?"*
   - Click **Query AI Manual Assistant**.
   - **Showcase the Side-by-Side Interface**:
     - Left: Direct answer quoting Mobil SHC 625 synthetic oil, weekly reservoir check, and 2,000-hour replacement.
     - Right: Verifiable Source Reference Card citing `VF-2SS Maintenance & Lubrication Manual (2024.1), Page 2`.
     - Click the link icon on the citation card to jump directly to page 2 of the PDF!
     - Click the **Helpful** feedback button to persist operator verification.
5. **Scenario B: Testing Machine Isolation & Insufficient Evidence**:
   - With `VF-2SS CNC` still selected, ask about a hydraulic press topic:
     *"What is the hydraulic system cracking pressure and primary relief valve setting?"*
   - Click **Query AI Manual Assistant**.
   - Point out that even though Machine B has this exact information, Machine A strictly returns:
     > **"Insufficient information: The selected machine's available manuals do not provide enough evidence to answer this question reliably."**
   - This proves **zero cross-machine leakage** and **zero hallucination**!

---

## 4. Act III: Plant Supervisor Surveillance & Gap Analysis (1 Minute)
1. Sign out and click **Supervisor Quick-Fill** -> Sign in as `supervisor`.
2. Notice the role badge switches to amber **SUPERVISOR**.
3. **Showcase Query Analytics & Gap Auditing**:
   - Show aggregate KPIs: Total Queries, Verified Answers, Insufficient Manual Evidence queries.
   - Filter by Status: **Insufficient Evidence**.
   - Explain to judges: *"Supervisors use this view to identify gaps in OEM manuals where technicians are asking questions that manufacturer documentation does not answer."*
   - Click **View** on any query to inspect the full audit trail.
