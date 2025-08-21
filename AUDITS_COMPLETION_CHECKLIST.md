## Audits Module Completion Checklist (ISO-aligned)

Scope: Ensure the following four submenus are implemented to meet ISO 19011 and ISO 22000 requirements.

### 1) Audits (Register)
- Backend/API
  - [ ] GET /api/v1/audits supports filters: search, audit_type, status, department, auditor_id, page, size
  - [ ] POST /api/v1/audits creates audits with validation
  - [ ] PUT /api/v1/audits/{id} updates audits with ownership checks
  - [ ] DELETE /api/v1/audits/{id} enforces RBAC and ownership
  - [ ] GET /api/v1/audits/stats returns counts by status/type and recent
  - [ ] GET /api/v1/audits/kpis/overview returns KPIs (lead_time_days_avg, on_time_audit_rate, finding_closure_days_avg, totals)
  - [ ] POST /api/v1/audits/export returns PDF/XLSX with applied filters
  - [ ] RBAC: audits:view/create/update/delete/approve/export enforced
  - [ ] Ownership: lead auditor or program manager for destructive actions
- Database
  - [ ] Indexes: title, status, audit_type, department, auditor_id/lead_auditor_id, created_at
  - [ ] Optional: actual_start_at, actual_end_at (for KPI accuracy)
- Frontend
  - [ ] Page `frontend/src/pages/Audits.tsx` shows register with filters, pagination, sorting
  - [ ] Create/Edit dialog includes title, type, status, dates, scope, objectives, criteria, department, lead/team auditors
  - [ ] KPI snapshot chips
  - [ ] Export list (PDF/XLSX) honoring filters
  - [ ] Attachments dialog
- Validation/Rules
  - [ ] Start_date <= end_date; status transitions validated
  - [ ] Impartiality warning when auditor department matches auditee
- Testing
  - [ ] Unit and API tests for filters, pagination, KPI math, permissions
  - [ ] E2E CRUD + export + attachment flows
- ISO Coverage
  - [ ] ISO 19011 5.4; 6.3–6.6; ISO 22000 9.2

### 2) Audit Schedule
- Backend/API
  - [ ] Use GET /api/v1/audits for dates and PUT /api/v1/audits/{id} to update
  - [ ] GET /api/v1/audits/programs/{id}/schedule for program timeline
  - [x] NEW GET /api/v1/audits/schedule/conflicts (start, end, auditor_id, department)
  - [x] NEW POST /api/v1/audits/schedule/bulk-update (id, start_date, end_date[])
  - [ ] RBAC: view vs update (MANAGE_PROGRAM for cross-team)
- Database
  - [ ] Indexes: (start_date, end_date), (auditor_id, start_date), (lead_auditor_id, start_date)
  - [ ] Fields: schedule_lock, lock_reason, reschedule_count, last_rescheduled_at
- Frontend
  - [ ] New page `frontend/src/pages/AuditSchedule.tsx` with calendar/Gantt
  - [ ] Filters: program, department, auditor, status; overdue badges
  - [ ] Drag-drop rescheduling with optimistic UI and rollback
  - [ ] Conflict detection banner and approval flow
- Validation/Rules
  - [ ] Prevent invalid date ranges; program year bounds respected
  - [ ] Conflict policy: warn or block based on role
- Testing
  - [ ] API conflict cases; bulk update atomicity; role checks
  - [ ] E2E drag-drop and conflict prompts
- ISO Coverage
  - [ ] ISO 19011 5.5

### 3) Findings & NCs
- Backend/API
  - [ ] Per-audit endpoints present (list/add/update, attachments, create-nc)
  - [x] NEW GET /api/v1/audits/findings (cross-audit) with filters: audit_id, program_id, severity, status, date range, responsible_person_id, department, has_nc, overdue
  - [x] NEW POST /api/v1/audits/findings/bulk-update-status
  - [x] NEW POST /api/v1/audits/findings/bulk-assign
  - [x] NEW GET /api/v1/audits/findings/analytics (severity/status distributions, closure time stats, dept heatmap)
  - [ ] RBAC: view/update; delete restricted to lead auditor or program manager; create NC requires NC permission
- Database
  - [ ] Indexes: audit_id, severity, status, created_at, responsible_person_id, target_completion_date, related_nc_id
  - [ ] Ensure closed_at set on close; overdue derived
- Frontend
  - [ ] New page `frontend/src/pages/AuditFindings.tsx` with advanced filters and saved views
  - [ ] Bulk select: assign and status updates
  - [ ] Create NC from finding; open NC detail
  - [ ] Analytics: severity heatmap, KPIs (open/overdue/critical/avg closure days)
- Validation/Rules
  - [ ] Status transitions; prevent duplicate NC linkage
- Testing
  - [ ] API filter correctness; bulk ops authorization
  - [ ] E2E triage → assign → create NC → verify link
- ISO Coverage
  - [ ] ISO 19011 6.4.10, 6.6; ISO 22000 10

### 4) Audit Reports
- Backend/API
  - [ ] GET /api/v1/audits/{id}/report (pdf|xlsx); POST /api/v1/audits/export
  - [ ] NEW POST /api/v1/audits/{id}/report/approve with report_approved_by/at, notes
  - [ ] NEW GET /api/v1/audits/{id}/report/history (versions, approvers, timestamps)
  - [ ] NEW POST /api/v1/audits/reports/consolidated (filters; pdf|xlsx)
  - [ ] RBAC: audits:export, audits:approve
- Database
  - [ ] Audit report_* fields and `AuditReportHistory` table with index (audit_id, version desc)
- Frontend
  - [ ] New page `frontend/src/pages/AuditReports.tsx` list with filters and per-audit export
  - [ ] Approve report and view approval trail
  - [ ] Consolidated export wizard
- Validation/Rules
  - [ ] Approval only when mandatory sections complete; versioned immutable history
- Testing
  - [ ] Unit: approval, history, consolidated export
  - [ ] E2E: generate → approve → verify history; consolidated export
- ISO Coverage
  - [ ] ISO 19011 6.6

### Cross-cutting
- Navigation & Routing
  - [x] Add routes: /audits/schedule, /audits/findings, /audits/reports
  - [ ] Update `frontend/src/theme/navigationConfig.ts` if needed
- Performance & Security
  - [ ] Pagination and server-side filters everywhere; add missing DB indexes
  - [ ] Validate inputs; file size/type constraints; audit events logged
- Documentation
  - [ ] Update README/user guides with ISO clause mapping
  - [ ] OpenAPI updated with new endpoints
- Sign-off
  - [ ] Role matrix validated (QA Manager, Auditor, Auditee, Program Manager)
  - [ ] All tests green; manual export verification

