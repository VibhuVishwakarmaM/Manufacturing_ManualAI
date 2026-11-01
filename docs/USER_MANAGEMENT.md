# User Management Dashboard & Administration

## 1. Overview
The User Management interface is restricted exclusively to Administrators (`/accounts/users/`). It empowers the plant lead to provision operators, manage access status, and reassign roles dynamically.

---

## 2. Interface Features

### 1. Operator Telemetry Tiles
Displays real-time user counts:
- Total Users Registered
- Active Accounts
- Administrator Count
- Field Engineer Count
- Plant Supervisor Count

### 2. User Directory Table
Lists all users with:
- Username & full name
- Color-coded Role Badge (`badge-role-admin`, `badge-role-engineer`, `badge-role-supervisor`)
- Account status pill (`Active` / `Inactive`)
- Registration timestamp

### 3. Account Actions
- **Register New Operator Modal**: Form validating username, email, full name, password (minimum 6 characters), and initial Django Group assignment.
- **Role Reassignment Modal**: Changes user group membership immediately; removes user from previous role groups and enrolls them in the newly chosen group.
- **Account Deactivation / Activation**: One-click toggle. Deactivated users are blocked from logging in or making API requests. Self-deactivation is protected to prevent administrative lockout.

---

## 3. Extensibility: Adding a New Role
To introduce a new role (e.g. `QualityAuditor`):
1. Add the role name to `ALL_ROLES` in `apps/accounts/permissions.py`.
2. Define a permission class (e.g. `IsQualityAuditor`) and helper method.
3. Add group creation and permissions assignment to `apps/accounts/management/commands/setup_roles.py`.
4. Re-run `python manage.py setup_roles`.
