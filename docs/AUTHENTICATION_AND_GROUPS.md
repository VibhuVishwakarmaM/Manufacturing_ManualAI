# Authentication, Django Groups & User Management

## 1. Django Built-in Authentication
In strict compliance with requirements, the application relies on Django's battle-tested authentication subsystem:
- Secure PBKDF2 password hashing with SHA256.
- Password complexity validation via Django auth validators.
- Session-based authentication for interactive web views.
- Session and Basic authentication for DRF REST API endpoints.

---

## 2. Django Groups & Role Initialization
Three primary Django Groups represent the application roles:
1. `Administrator`
2. `Engineer`
3. `Supervisor`

### Management Command: `python manage.py setup_roles`
This command idempotently configures the three groups and assigns granular Django permissions across all application models:
- **`Administrator`**: Receives all model permissions (`add`, `change`, `delete`, `view`) across `machines`, `manuals`, `document_processing`, `question_history`, and `audit_logs`.
- **`Engineer`**: Receives `view_machine`, `view_manual`, `add_questionhistory`, `view_questionhistory`, `add_answerfeedback`.
- **`Supervisor`**: Receives `view_machine`, `view_manual`, `view_questionhistory`, `view_answerfeedback`, and `view_auditlog`.

This command can be safely re-run at any time.

---

## 3. Demonstration Accounts Command: `python manage.py create_demo_users`
Creates or updates the three standard demonstration accounts:

| Username | Password | Assigned Role / Group | Staff Status |
|---|---|---|---|
| `admin` | `AdminPass123!` | Administrator | Staff / Superuser |
| `engineer` | `EngineerPass123!` | Engineer | Standard User |
| `supervisor` | `SupervisorPass123!` | Supervisor | Standard User |

Credentials can be overridden via environment variables:
- `DEMO_ADMIN_PASSWORD`
- `DEMO_ENGINEER_PASSWORD`
- `DEMO_SUPERVISOR_PASSWORD`
