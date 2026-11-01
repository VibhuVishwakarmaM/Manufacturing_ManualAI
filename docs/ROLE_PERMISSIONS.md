# Role-Based Access Control & Permissions

The application implements strict, backend-enforced RBAC through Django's built-in Authentication and Permissions framework. Frontend button visibility is treated solely as a UI convenience, not a security boundary.

---

## 1. Role Capabilities Matrix

| Feature / Resource | Administrator | Field Engineer | Plant Supervisor | Anonymous |
|---|:---:|:---:|:---:|:---:|
| **Sign In / Sign Out** | YES | YES | YES | Sign In Only |
| **View Equipment Machines** | YES | YES | YES | NO (401/302) |
| **Register / Edit / Delete Machines** | YES | NO (403) | NO (403) | NO (401) |
| **View Manuals Catalog** | YES | YES | YES | NO (401) |
| **Upload Manual PDF** | YES | NO (403) | NO (403) | NO (401) |
| **Reprocess / Re-index Manual** | YES | NO (403) | NO (403) | NO (401) |
| **View / Download PDF Document** | YES | YES | YES | NO (401/302) |
| **Ask RAG Maintenance Questions** | YES | YES | YES | NO (401) |
| **View Personal Query History** | YES | YES | YES | NO (401) |
| **View Cross-Engineer Query History** | YES | NO (Filtered) | YES | NO (401) |
| **Submit Question Feedback** | YES | YES | YES | NO (401) |
| **Manage Users & Assign Roles** | YES | NO (403) | NO (403) | NO (401) |
| **Inspect System Audit Logs** | YES | NO (403) | YES (Read-Only) | NO (401) |
| **View System Pipeline Config** | YES | NO (403) | NO (403) | NO (401) |

---

## 2. DRF Permission Classes
Located in `apps/accounts/permissions.py`:
- `IsAdministrator`: Verifies `user.is_superuser` or membership in group `Administrator`.
- `IsEngineer`: Verifies membership in group `Engineer` or `Administrator`.
- `IsSupervisor`: Verifies membership in group `Supervisor` or `Administrator`.
- `IsAdminOrSupervisor`: Verifies membership in either `Administrator` or `Supervisor`.
