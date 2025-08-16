### Audits Plan Checklist (ISO 19011 aligned)

This step-by-step checklist drives closing identified gaps in the Audits module and ensuring a high‑efficiency end-to-end process across backend and frontend. Use it as a working plan; check items as completed. Where files are mentioned, they refer to paths in this repository.

References:
- ISO 19011:2018 Guidelines for auditing management systems: https://www.iso.org/obp/ui/#iso:std:iso:19011:ed-3:v1:en
- ASQ ISO 19011 overview: https://asq.org/quality-resources/iso-19011?srsltid=AfmBOoocPokHUdEopakbz0QO_DcY-XxBShmy4EllwE4TpmiFnP0SxiTl

---

### 0) Planning and Governance
- [x] Define success metrics and timeline (lead time, on-time audit rate, closure days). Document in `docs/AUDITS_KPIS.md`.
- [ ] Add KPI-supporting fields via migrations and schemas:
  - [x] `audits.actual_end_at`
  - [x] `audit_plans.approved_at`
  - [x] `audit_findings.closed_at`
  - [x] `audit_findings.finding_type` (nc | observation | ofi)
  - Update `backend/app/schemas/audit.py` and OpenAPI accordingly.
- [x] Confirm RBAC model coverage for audits (permissions, roles, modules) with stakeholders.
- [x] Align notification channels (email/in-app) and scheduler cadence.
  - Implemented audit reminders in `ScheduledTasksService` (plan reminders, findings due, overdue escalations)
  - Created `EmailService` for priority notifications with SMTP configuration
  - Added CLI script `run_scheduled_tasks.py` for cron/systemd integration
  - Created `SCHEDULER_SETUP.md` with setup instructions and cron examples

Acceptance:
- [ ] KPIs defined and signed off.
- [ ] Program backlog prioritized and scheduled across sprints.

---

### 1) RBAC and Security Hardening
- [x] Define `Module.AUDITS` permission set in RBAC (read, create, update, delete, manage_program, export, approve, acknowledge).
- [x] Enforce permission dependencies on all audit routes in `backend/app/api/v1/endpoints/audits.py` using `require_permission_dependency(...)` from `backend/app/core/permissions.py`.
- [ ] Restrict delete/update to owners or roles (lead auditor/program manager) where applicable. (SKIPPED - not crucial)
- [x] Centralize file handling via `backend/app/services/storage_service.py` (sanitize filename, content-type/size validations, checksum; optional AV scan if available). Replace direct `open(...)` usage in audits endpoints.
  - Enhanced StorageService with security features (filename sanitization, content-type validation, file size limits, checksum calculation)
  - Updated all audit file upload/download/delete endpoints to use StorageService
  - Removed direct file operations (open, shutil.copyfileobj) from audit endpoints
- [ ] Return 403 for unauthorized users; add comprehensive error messages.

Acceptance:
- [ ] API tests cover 401/403 for each route per role.
- [ ] File upload attempts with disallowed types/sizes are blocked and logged.

---

### 2) Audit Program (ISO 19011 clause 6)
- [ ] Add `AuditProgram` model: objectives, scope, year/period, manager_id, risk_method, resources, schedule, KPIs, status.
- [ ] CRUD endpoints: `/audits/programs` (`GET/POST/PUT/DELETE`), `/audits/programs/{id}/schedule`.
- [ ] Dashboard endpoints for program KPIs (on-time audits, overdue actions, risk coverage, NC rates).
- [ ] Frontend: Program list/detail pages, schedule/calendar view (risk-prioritized backlog).

Acceptance:
- [ ] Create/update program, view KPIs and schedule calendar end-to-end in UI.

---

### 3) Risk-Based Planning (ISO 19011 6.3/6.4)
- [ ] Add `AuditRisk` model linking areas/processes/suppliers with risk rating, rationale, last audit date.
- [ ] Use risk + elapsed time to suggest/schedule audits; expose endpoint `/audits/programs/{id}/risk-plan`.
- [ ] Frontend: risk matrix widget; filter/sort audits by risk.

Acceptance:
- [ ] Risk input changes update scheduling suggestions; visible in UI.

---

### 4) Audit Planning and Team Competence/Impartiality (ISO 19011 clause 7)
- [ ] Add `AuditTeamMember` (audit_id, user_id, role: lead/auditor/observer, competence_tags, independence_confirmed, signed_at).
- [ ] Integrate with Training module to validate competence (required trainings complete) before assignment.
- [x] Add `AuditPlan` (agenda, processes to audit, criteria refs, sampling plan, documents to review, logistics, communications). Endpoints: create/update/approve.
- [ ] Impartiality check: block assignment where auditee department = auditor’s department unless explicitly approved.
- [x] Frontend wizard to build/approve plan; send notifications to auditees for acknowledgement.

Acceptance:
- [ ] Cannot assign unqualified auditors; impartiality conflicts flagged and blocked (or require approval).
- [ ] Plan is created, approved, and auditees acknowledge in UI.

---

### 5) Conducting Audit: Checklist, Evidence, Activity Log
- [ ] Extend `AuditChecklistItem` to include sampling details (population, sample size, method) and evidence structure.
- [ ] Add `AuditEvidence` (who, when, source, description, files) linked to item/finding.
- [ ] Add `AuditActivityLog` (interviews, walkthroughs, observations) with timestamp and participants.
- [ ] Frontend: improved checklist UX (inline responses, scoring, evidence capture, attachments per item).

Acceptance:
- [ ] Auditors can capture objective evidence with traceability and attachments per item/finding.

---

### 6) Findings, Observations, OFIs, and Follow-up (ISO 19011 7.5/7.6)
- [ ] Extend `AuditFinding` with `finding_type` (nonconformity, observation, ofi) and fields for auditee response, containment, correction, root cause, corrective action, verification.
- [ ] Add reminders/escalations for overdue actions; integrate with existing NC/CAPA for major/critical NCs.
- [ ] Frontend: follow-up board (by due date/status); link to NC/CAPA and verify closure.

Acceptance:
- [ ] Findings lifecycle from creation → auditee response → actions → verification → closure is fully supported and tracked.

---

### 7) Audit Report and Approvals (ISO 19011 7.5)
- [ ] Add `AuditReport` model (content sections: scope, team, plan summary, criteria coverage, evidence summary, findings, conclusions, recommendations; distribution list).
- [ ] Signature workflow: lead auditor sign-off, auditee acknowledgement, optional management approval; record signed_at/by.
- [ ] Enhance exports: PDF/XLSX with standardized sections, headers/footers, page numbers, watermark for draft.
- [ ] Frontend: report assembly preview and signature collection UI.

Acceptance:
- [ ] Signed report generated and downloadable; signatures/acknowledgements stored and auditable.

---

### 8) Attachments and Storage
- [ ] Migrate audits attachments to `storage_service` with UUID paths, metadata (size, checksum, content_type, uploader_id), and access checks.
- [ ] Add download authorization (only team/program roles or auditees).
- [ ] Optional: AV scanning hook; quarantine on fail.
- [ ] Use signed URLs or short‑lived tokens for downloads; avoid exposing raw paths.
- [ ] Enforce encryption at rest (storage backend) and TLS in transit; document configuration.
- [ ] Sanitize `Content-Disposition` filenames; prevent path traversal and content sniffing.

Acceptance:
- [ ] Uploads with invalid mime/size are rejected; downloads respect RBAC and are logged.

---

### 9) Dashboards and KPIs
- [x] Implement program/audit KPIs endpoints (on-time audits, NCs by severity, average closure days, risk coverage, auditor utilization).
- [ ] Wire basic KPI endpoints for initial rollout:
  - [x] `GET /audits/kpis/overview` (lead time, on-time rate, closure days)
  - [x] Add filters: period (`week|month|quarter|year`), department, auditor
  - Enhanced KPI endpoint with period-based date filtering (week/month/quarter/year)
  - Added comprehensive KPI metrics (total audits, completed, overdue, findings counts)
  - Improved filtering by department and auditor_id
  - Enhanced response model with additional metrics and filter context
  - [x] Ensure queries use new fields `actual_end_at`, `approved_at`, `closed_at`, and `finding_type`.
- [x] Frontend cards in dashboard and audits pages; filters by period and department.
  - Enhanced Audits page with comprehensive KPI display (core metrics + counts)
  - Added period filter dropdown (week/month/quarter/year)
  - Added department filter with search functionality
  - Added Apply Filters and Clear Filters buttons
  - Color-coded chips for different metric types (primary, info, success, warning, error)
  - Responsive design with proper spacing and layout

Acceptance:
- [ ] KPI values match database queries; visualizations render and filter correctly.
- [ ] New fields exist in DB and are populated for new records; backfill strategy documented for existing records.

---

### 10) API and Schema Quality
- [ ] Replace regex string enums in `backend/app/schemas/audit.py` with Pydantic `Literal`/Enum synchronized to models to prevent drift.
- [ ] Add pagination and sorting consistently.
- [ ] Add OpenAPI descriptions for new endpoints; ensure schema examples exist.
- [ ] Add change history/audit trail for critical entities (findings, plans, reports) via history tables or versioning.
- [ ] Prefer soft-delete where regulatory retention applies; include `deleted_at` and actor fields.
- [ ] Add DB indexes for common filters (status, audit_type, dates, responsible_person_id).
- [ ] Normalize evidence model and remove duplication (e.g., converge on `AuditEvidence`; deprecate `evidence_file_path`).

Acceptance:
- [ ] OpenAPI docs clear; generated clients (if any) build successfully.

---

### 11) Notifications and Scheduler
- [ ] Scheduled jobs for: plan approval reminders, audit start reminders, action due reminders, escalation alerts.
- [ ] In-app notifications + optional email integration using existing notifications service.

Acceptance:
- [ ] Jobs run on schedule; sample notifications received for key events.

---

### 12) Data Logging and Retention
- [ ] Ensure `app/utils/audit.py` writes to `AuditLog` reliably; log failures to server logs (without blocking business flow).
- [ ] Add retention policies and an archival/export endpoint for audit logs.

Acceptance:
- [ ] Audit events visible for key actions; retention/archival controls documented and tested.

---

### 13) Migrations and Backfill
- [ ] Alembic migrations for all new models/fields in `backend/alembic/versions/`.
- [ ] Backfill scripts to map old data to new structures (evidence, finding types, reports).

Acceptance:
- [ ] Migrations apply cleanly on staging and restore from backup validated.

---

### 14) Frontend UX and Performance
- [ ] Add audits calendar, planning wizard, report signature screens.
- [ ] Optimize lists (virtualized tables where needed), loading states, and error handling.
- [ ] File uploads use progress bars and size/type validations client-side too.

Acceptance:
- [ ] Lighthouse/React profiler shows acceptable performance; no major UI blocking.

---

### 15) Testing and QA
- [ ] Unit tests for models/schemas (enums, validations, transitions).
- [ ] API tests for RBAC, planning, findings lifecycle, report signatures, exports, attachments security.
- [ ] E2E tests (Cypress/Playwright):
  - [ ] Create program → plan → assign team (competence validated) → auditee acknowledgement.
  - [ ] Conduct audit → checklist responses → evidence uploads.
  - [ ] Create findings (OFI/NC) → link to NC/CAPA → reminders → verification → closure.
  - [ ] Generate and sign report → download PDF.
- [ ] Performance tests for large attachment handling and list views.

Acceptance:
- [ ] CI green; coverage threshold met; critical paths verified end-to-end.

---

### 16) Deployment and Rollout
- [ ] Feature flag new workflows if needed; progressive rollout plan.
- [ ] Update `README.md` and user docs with new flows.
- [ ] Train users (brief release notes; link to doc pages).

Acceptance:
- [ ] Production rollout completed with monitoring; no high severity issues.

---

### 17) ISO 19011 Principles Embedment
- [ ] Document and embed audit principles (integrity, fair presentation, due professional care, confidentiality, independence/impartiality, evidence‑based, risk‑based approach) into SOP and UI prompts.
- [ ] Add auditor code of conduct acknowledgement for each audit (checkbox + timestamp).
- [ ] Enforce impartiality checks programmatically; require override approval if conflict exists.

Acceptance:
- [ ] Principles visible in auditor workflow; acknowledgements stored per audit.

---

### 18) Data Model Integrity & History
- [ ] Add `created_by`, `updated_by` to audits, plans, findings, reports where missing.
- [ ] Implement entity history/versioning for Findings and Report (who changed what, when, old→new values).
- [ ] Ensure timezone‑aware timestamps consistently (UTC in DB; convert in UI).

Acceptance:
- [ ] History records present for updates; timestamps uniform and correct across API/UI.

---

### 19) Security & Privacy Enhancements
- [ ] Apply rate limiting to sensitive endpoints (attachments download, exports).
- [ ] Review and minimize PII in findings/evidence; redact in exports/notifications where not needed.
- [ ] CORS, CSRF (if applicable), and robust input validation across endpoints.

Acceptance:
- [ ] Security checks pass; pen test findings (if any) addressed.

---

### 20) Monitoring & Observability
- [ ] Add structured logging, request IDs, and correlation for audit flows.
- [ ] Expose metrics (e.g., audit creation rate, on‑time rate, average closure days) via monitoring adapter.
- [ ] Alerts for scheduler failures and KPI threshold breaches.

Acceptance:
- [ ] Dashboards and alerts configured; incident playbook documented.

---

### 21) Accessibility & Internationalization
- [ ] Ensure WCAG 2.1 AA for audit pages: keyboard nav, ARIA, color contrast.
- [ ] Externalize text strings to enable i18n; allow localized report headers/footers.

Acceptance:
- [ ] Accessibility audit passes; optional locale switch demonstrates translation handling.

---

### 22) Integrations & Interop
- [ ] Calendar (iCal) export/invite for audit schedule; email templates for plan/reports.
- [ ] SSO/e-sign integration options for report signatures (if available in environment).

Acceptance:
- [ ] iCal file valid; email templates rendered; signature integration validated or stubbed with config flag.

---

### 23) Documentation & SOPs
- [ ] Author `docs/AUDITS_SOP.md` covering program setup, planning, conduct, reporting, and follow‑up.
- [ ] Add role‑specific quick guides for Auditors and Auditees; link from UI help.

Acceptance:
- [ ] SOP approved; help links accessible in UI.

---

### 24) Data Protection, Backup & DR
- [ ] Verify backups include audit evidence and logs; test restore procedure.
- [ ] Define retention periods for evidence, reports, logs; configure lifecycle policies.

Acceptance:
- [ ] Successful restore test; retention policies applied.

---

### 25) Seeding & Demo Data
- [ ] Update demo/seed scripts to populate programs, plans, audits, findings (OFIs/observations), and evidence for realistic demos.

Acceptance:
- [ ] Demo environment showcases full workflow end‑to‑end with realistic content.

---

### 26) Edge Cases & QA Scenarios
- [ ] Timezones and DST changes; leap day handling.
- [ ] Large files and slow uploads (progress, retry); filename collisions; virus scan failures.
- [ ] Concurrency: multiple auditors editing checklists/findings; optimistic locking or last‑write wins policy.

Acceptance:
- [ ] Identified edge cases have tests and verified behaviors.

### Definition of Done (Module Level)
- [ ] All security and RBAC checks enforced for audit routes and file access.
- [ ] Audit Program, Planning, Conduct, Reporting, and Follow-up fully supported and aligned with ISO 19011.
- [ ] Risk-based scheduling and KPI dashboards operational.
- [ ] Evidence and logs meet auditability requirements; exports are complete and professional.
- [ ] Frontend UX supports the full lifecycle efficiently with strong performance.


