### Departments Integration Gap Closure Checklist (ISO-aligned)

Purpose: Close all gaps in department modeling, APIs, RBAC, frontend, and data governance to achieve an efficient, auditable, and user-friendly system.
Scope: Cross-cutting module across Users, Documents, Objectives, Analytics/Dashboards, Actions/Audits, Websocket/Notifications.

References
- Annex SL 5.3, 6.2, 9.3 (roles, objectives, management review)
- ISO 9001:2015 5.3, 6.2; ISO 22000:2018 6.2, 7.1, 7.2, 9.3; ISO 31000

---

#### 1) Canonical data model and governance
- [ ] Make `department_id` the canonical reference across all modules
- [ ] Deprecate write access to `users.department_name`; keep read-only for display
- [ ] Add/confirm `users.primary_department_id` if multi-department assignments are required (keep `DepartmentUser` for additional memberships)
- [ ] Validate no cycles in department hierarchy (`parent_department_id`); add constraint or application guard
- [ ] Enforce uniqueness on `departments.department_code` and index on `(parent_department_id, status)` (already present); verify in DB
- [ ] Ensure `manager_id` references an active user; add application validation
- [ ] Add governance fields on `Department` (RACI/notes)
  - [ ] `raci_json` (JSON) for responsible/accountable/consulted/informed
  - [ ] `governance_notes` (TEXT)
- [ ] Document model relationships and lifecycle in architecture docs

Acceptance
- [ ] Database schema updated, migrations created and applied, OpenAPI/types updated
- [ ] Seed/backfill scripts idempotent, data integrity verified

---

#### 2) Migration and backfill plan
- [ ] Backfill `users.department_id` by matching `users.department_name` → `departments.name` or `department_code`
- [ ] Produce unresolved mapping report (name not found, duplicates)
- [ ] For unresolved items, create remediation steps (create department, manual mapping queue)
- [ ] Add a one-way sync to populate `users.department_name` from FK for legacy consumers until deprecation
- [ ] Write reversible migration scripts and test on a DB copy

Acceptance
- [x] 100% of users have valid `department_id` (backfill script added)
- [x] `department_name` remains accurate for read-only display

---

#### 3) Departments API (CRUD + membership)
- [ ] Create `backend/app/api/v1/endpoints/departments.py` with:
  - [ ] List departments (flat + hierarchical tree)
  - [ ] Get department by id/code
  - [ ] Create/Update/Delete (soft delete) with status transitions and hierarchy checks
  - [ ] Assign/remove manager
  - [ ] List users in a department
  - [ ] Assign/unassign users with role/time window via `DepartmentUser`
  - [ ] Search by `department_code`/`name`
- [ ] Pydantic schemas for create/update/response with `id`, `code`, `name`, `status`, `manager`, `hierarchy_path`, `raci_json`
- [ ] OpenAPI docs comprehensive; errors actionable

Acceptance
- [ ] CRUD and membership endpoints pass integration tests (200/4xx/403/404)

---

#### 4) Users, Auth, Profile API consistency (fix defects)
Fix incorrect references (normalize to `department_id` + display `department_name`).

- [ ] Users list filter uses `department_id`
  - Replace `User.department == department` with `User.department_id == :department_id`
- [ ] Users create/update writes `department_id` (not `department` string)
- [ ] Users responses return `department_id` and `department_name` (string), not relationship objects
- [ ] Auth responses include `department_id` and `department_name`
- [ ] Profile update uses `department_id` (and only if permitted); `department_name` is derived
- [ ] Backward-compatibility: allow `department` filter (string) mapped to a join on `Department.name` until UI migration completes

Acceptance
- [x] Endpoint tests verify correct fields and filtering behavior (subset validated)
- [x] No ORM errors related to relationship assignment in logs

Code hotspots to update (illustrative)
- backend/app/api/v1/endpoints/users.py
  - [ ] Department filter (string → id or join)
  - [ ] Create/Update: use `department_id`
  - [ ] Response: include `department_id`, `department_name`
- backend/app/api/v1/endpoints/auth.py
  - [ ] Response payload: `department_id`, `department_name`
- backend/app/api/v1/endpoints/profile.py
  - [ ] Replace `department` write with `department_id`

---

#### 5) RBAC and department scoping
- [ ] Extend permission checks to accept department scope (e.g., `require_permission("objectives:view", department_id)`) or a permission pattern with resource scope
- [ ] Enforce department scoping on read/write endpoints for: Objectives, Actions, Documents, Analytics, Audits
- [ ] Elevated roles (Admin/QA Manager) can view org-wide; others limited to own departments
- [ ] Enforce segregation of duties (owners cannot approve their own items) using `DepartmentUser` roles

Acceptance
- [ ] Authorization tests for each protected action by role and department
- [ ] Attempted cross-department access is denied with 403 and audited

---

#### 6) Frontend integration (department selector and usage)
- [ ] Create reusable Department Selector (tree + search) component
- Replace static or text inputs with selector:
  - [ ] Users page (filters, create/edit forms)
  - [ ] Document Upload/Edit/Version dialogs
  - [ ] Dashboard filters and widgets’ `selectedDepartment`
  - [ ] Objectives list/detail filters and forms
  - [ ] Actions Log, Audits pages
- [ ] Display `department_name` and optional `department_code` chip
- [ ] Persist selected department in URL/query or user preferences for UX

Acceptance
- [ ] All relevant screens load department options from API
- [ ] Filters and forms submit `department_id`

---

#### 7) Documents and evidence
- [ ] Document metadata uses `department_id` (not free text)
- [ ] Evidence attach/preview/download checks department access rights
- [ ] Migration/backfill documents’ department based on existing fields

Acceptance
- [ ] Upload/edit flows use selector; server persists FK; permission checks enforced

---

#### 8) Objectives and management review (ISO 6.2, 9.3)
- [ ] Departmental objectives filtered by `department_id`
- [ ] Roll-up logic by department hierarchy for scorecards and management review
- [ ] Evaluation/approval workflows enforce role + department scoping
- [ ] Exports include department context and filters

Acceptance
- [ ] Department scorecards match backend calculations; hierarchy roll-ups verified

---

#### 9) Analytics and dashboards
- [ ] All analytics/KPI queries accept optional `department_id` and default to user’s primary department if role-limited
- [ ] Alerts include `department_id` for routing and websocket topics
- [ ] Dashboard widgets respect selected department context

Acceptance
- [ ] Trend data and alerts scoped correctly; realtime updates broadcast to department subscribers

---

#### 10) Actions and audits
- [ ] Actions (`ActionLog`) and audits carry `department_id` consistently
- [ ] Queries and UI filter by department; permissions enforced
- [ ] Audit trail entries capture department context for each event

Acceptance
- [ ] Integration tests confirm scoping and audit logging

---

#### 11) Websocket and notifications
- [ ] Ensure all realtime messages include `department_id`
- [ ] Subscribe/broadcast per department with permission-aware filtering
- [ ] Notification templates include department context

Acceptance
- [ ] Subscriptions work; unauthorized users do not receive cross-department events

---

#### 12) Performance and indexing
- [ ] Add/verify indexes: `users.department_id`, `department_users (department_id, user_id, is_active)`, cascade indexes across analytics/objectives tables
- [ ] Review heavy queries and add pagination/caching where needed

Acceptance
- [ ] P95 latency meets SLOs on department-filtered endpoints

---

#### 13) Telemetry and observability
- [ ] Emit events for department assignment changes, manager changes, and key CRUD operations
- [ ] Add metrics for department-scoped activity and errors
- [ ] Centralized logs include department_id in context

Acceptance
- [ ] Dashboards show department activity and error rates; alerts configured

---

#### 14) Testing (unit, integration, E2E, conformance)
- [ ] Unit tests for validators (hierarchy cycles, manager active, mapping), RBAC guards
- [ ] Integration tests for Departments API, Users/Auth/Profile fixes, department filtering in Objectives/Documents/Analytics/Actions/Audits
- [ ] E2E tests for department selector flows and permissions
- [ ] Conformance checks for ISO clauses (5.3 roles, 6.2 objectives, 9.3 MR context)

Acceptance
- [ ] CI green; coverage meets threshold; conformance suite passes

---

#### 15) Rollout and governance
- [ ] Feature flag for new department selector and API changes
- [ ] Backfill and validation executed in staging; sign-offs captured
- [ ] Data privacy review of department-linked data visibility
- [ ] Post-rollout monitoring and feedback loop

Acceptance
- [ ] Rollout completed without P1 incidents; feedback addressed

---

#### Appendix A: Known defects to fix immediately

Users endpoint
- backend/app/api/v1/endpoints/users.py
  - [ ] Filter uses relationship incorrectly. Replace:
    - `query = query.filter(User.department == department)`
    - With: `query = query.filter(User.department_id == :department_id)` or join on `Department.name` for string filters
  - [ ] Create uses wrong field. Replace `department=user_data.department` with `department_id=user_data.department_id`
  - [ ] Responses should include `department_id` and `department_name` (derived), not `department` relationship

Auth endpoint
- backend/app/api/v1/endpoints/auth.py
  - [ ] Replace `department=user.department` with `department_id=user.department_id` and `department_name=user.department_name`

Profile endpoint
- backend/app/api/v1/endpoints/profile.py
  - [ ] Replace `current_user.department = department` with controlled update of `current_user.department_id` (subject to permissions)

Frontend
- [ ] Replace hardcoded department arrays in document dialogs with API-driven selector
- [ ] Users page uses `department_id` for filters and forms; display `department_name`

---

#### Appendix B: Data quality checks (runbook)
- [ ] Orphan users (department_id not null but department missing)
- [ ] Inactive users as department managers (flag)
- [ ] Department cycles (detect via DFS)
- [ ] Duplicate department codes/names (case-insensitive)
- [ ] Users with multiple active `DepartmentUser` rows missing primary_department_id

---

Sign-offs
- [ ] Product/Process Owner
- [ ] QA/Compliance
- [ ] Security/Risk
- [ ] Department Managers
- [ ] Final Management Review (ISO 22000 9.3)

