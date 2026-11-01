# Audit Logging Subsystem

## 1. Principles & Safeguards
The audit logging subsystem (`apps/audit_logs`) records security-critical actions and operational lifecycle events.

Key design principles:
1. **Separation of Concerns**: Audit logs are maintained in an independent model (`AuditLog`) completely separated from `QuestionHistory`.
2. **Strict Non-Sensitive Metadata**: Passwords, authorization tokens, session keys, and API credentials are automatically stripped or redacted before persistence via `sanitize_metadata()`.
3. **Resilience**: The `log_audit_event()` helper handles exceptions gracefully so an audit failure never crashes a primary user transaction.

---

## 2. Tracked Event Actions
- `USER_LOGIN` / `USER_LOGOUT` / `API_USER_LOGIN`
- `CREATE_USER` / `UPDATE_USER_ROLE` / `USER_DEACTIVATED` / `USER_ACTIVATED`
- `CREATE_MACHINE` / `UPDATE_MACHINE` / `DELETE_MACHINE`
- `UPLOAD_MANUAL` / `MANUAL_INDEXED` / `MANUAL_PROCESSING_FAILED` / `DELETE_MANUAL`
- `ASK_QUESTION`

---

## 3. Data Model Schema
- `id`: UUID.
- `user`: ForeignKey to `User` (SET_NULL on user deletion).
- `action`: String (e.g. `UPLOAD_MANUAL`).
- `resource_type`: String (e.g. `Manual`, `Machine`, `User`).
- `resource_id`: String identifier of target resource.
- `metadata`: JSONField containing scrubbed non-sensitive context (e.g. title, machine name, page count).
- `ip_address`: GenericIPAddressField extracted from `X-Forwarded-For` or `REMOTE_ADDR`.
- `timestamp`: DateTimeField with auto_now_add.
