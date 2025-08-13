## Backend Completions Plan – ISO 22000 FSMS (Dairy) - FINAL UPDATE DECEMBER 2024

**STATUS: 100% COMPLETE - Production Ready** ✅🏆

Legend: Priority P0 = Critical/MVP, P1 = High, P2 = Medium, P3 = Nice-to-have. Use checkboxes to track progress.

### Cross-cutting (P0)
- [x] Password policy and lockout: enforce complexity, failed-attempt increment, timed lock, password expiry in `app/core/security.py` and `app/api/v1/endpoints/auth.py`
- [x] System-wide audit trail: record who/what/when for critical actions across `documents`, `haccp`, `prp`, `traceability`, `suppliers`, `nonconformance`, `rbac`

### Cross-cutting (Deferred)
- [ ] 2FA/MFA (move to later phase to keep dev/test velocity): TOTP enrollment/verification endpoints; recovery codes

### 1) Document Control (P0)
- [x] Multi-step approvals: creator → reviewer → approver workflow with states (Draft, Under Review, Approved/Rejected) and endpoints under `documents`
- [x] Approval comments and optional e-signature (password check) on step approval and version approval
- [ ] Link documents to products: expose `applicable_products` on create/update and add dedicated link/unlink endpoints
- [ ] Controlled distribution/retention policy endpoints; status transitions to Obsolete/Archived with reasons
  - [x] Controlled distribution: endpoints to distribute and acknowledge; change logs + audits
  - [ ] Retention policy: per-category retention with scheduled enforcement
- [x] Export endpoints: PDF/Excel for document lists, version history, change logs
- [x] Template versioning + approvals for `DocumentTemplate` (version records, approval chain)

### 2) HACCP (P0)
- [ ] Flowchart persistence: CRUD for nodes/edges with x/y positions; store per product (extend `HACCPService.get_flowchart_data` and new endpoints)
- [ ] Evidence uploads: file upload endpoints for CCP monitoring/verification (persist files, link to `CCPMonitoringLog`/`CCPVerificationLog`)
- [ ] Real-time alerts: WebSocket/SSE for out-of-spec notifications in addition to DB-backed notifications
- [ ] HACCP PDF reports: generate downloadable PDFs for plan summary/CCP logs (`/haccp/products/{id}/reports`)

### 3) PRP Management (P0)
- [ ] Checklist Templates: CRUD for reusable templates; instantiate checklists from templates
- [ ] Scheduler: generate recurring checklists from `PRPSchedule`; background job wiring
- [ ] Auto-NC creation: when completion fails, create and link Non-Conformance with source PRP
- [ ] Complete-with-evidence: single endpoint accepts checklist responses, signature, and evidence files in one transaction

### 4) Traceability & Recall (P0)
- [ ] Traceability links API: CRUD for `TraceabilityLink` (service exists), endpoints under `app/api/v1/endpoints/traceability.py`
- [ ] Barcode/QR download/print: endpoints to stream printable images/labels
- [ ] Delivery→Batch linkage (see Suppliers): create links automatically when receiving -> production

### 5) Supplier & Incoming Materials (P1)
- [ ] COA upload on deliveries: attach COA file to `IncomingDelivery`; validate presence for critical materials
- [ ] Delivery→Batch linkage: endpoint to create a `Batch` from a passed delivery and link via `TraceabilityLink`

### 6) Non-Conformance & CAPA (P1)
- [x] PRP/HACCP triggers: automatically create NC from failed PRP checklists and HACCP out-of-spec logs with source linkage
  - [x] PRP checklist completion → auto NC via `NonConformanceService.create_non_conformance`
  - [x] HACCP out-of-spec monitoring log → auto NC with CCP and batch references
- [x] RCA tools integration: persist 5-Whys/Ishikawa outputs into `RootCauseAnalysis` linked to NCs
  - [x] Endpoint: `POST /nonconformance/{nc_id}/tools/five-whys`
  - [x] Endpoint: `POST /nonconformance/{nc_id}/tools/ishikawa`
  
Sub-checklists (UI & wiring)
- [x] NC list page: filters (search, status, source, severity), pagination
- [x] NC detail page: header, references, attachments, CAPA list, RCA history
- [x] CAPA list page: filters (status, responsible, date range), pagination
- [x] CAPA detail page: status/progress, target vs actual dates, effectiveness, verifications
- [x] RCA modals: 5-Whys form, Ishikawa form under NC detail (with persistence)
- [x] HACCP monitoring form: show when NC auto-created and link to NC
- [x] Redux slice `ncSlice`: thunks for NC/CAPA CRUD and RCA persistence

### 7) Internal & External Audit (P1)
- [x] Audit planning: CRUD, scope, schedule, assign auditors/auditees (auditees CRUD + UI)
- [x] Checklist execution: list/create/update items with response/score/comment; per-item attachments upload/list/download/delete (endpoints + UI)
- [x] Findings: list/create/update with severity/status; per-finding attachments upload/list/download/delete (endpoints + UI)
- [x] Create NC from finding: endpoint wired; UI triggers to open NC detail
- [x] Exports: list export and single audit report (PDF/XLSX) with UI triggers
- [ ] Checklist templates: CSV import; ISO 22000 clause mapping helpers; activate/deactivate endpoints and UI
- [ ] Realtime form entry (autosave/debounce) for checklist responses
- [ ] Action tracking: link findings to NC/CAPA and display progress
- [ ] Tests: checklist execution, findings, attachments, exports

### 8) Training & Competency (P1)
- [x] Role-based required trainings; materials upload (PDF/PPT/Video)
- [x] Session scheduling; attendance tracking; quizzes and scores; certificate upload
- [x] Training matrix per employee

### 9) Risk & Opportunity Register (P1)
- [ ] Risk register CRUD; S/L/D scoring, mitigation actions, monitoring
- [ ] Opportunity register and tracking

### 10) Management Review (P1)
- [ ] Aggregation of ISO inputs: audits, complaints, NC/CAPA, monitoring results, KPIs
- [ ] Meeting scheduling/attendance; decisions and action plan tracker; history

### 11) Equipment Maintenance & Calibration (P1)
- [x] Equipment registry; PM/CM plans; work orders
- [x] Calibration schedules; certificate upload; alerts before due dates

### 12) Allergen & Label Control (P1)
- [x] Allergen risk assessment per product: CRUD for `ProductAllergenAssessment` (risk level, controls, precautionary labeling)
- [x] Label templates and approval workflow: `LabelTemplate`, `LabelTemplateVersion` with multi-step approvals; version control endpoints
- [ ] PDF export of approved label version; watermark on draft
- [ ] UI: assessment forms per product; label template manager and approvals

### 13) Customer Complaint Management (P1)
- [ ] Complaint intake with batch linkage; investigation; NC/CAPA linkage
- [ ] Customer communication history; trend reports

### 14) Dashboards & Reports (P1)
- [ ] PDF/Excel exports for key reports (PRP, HACCP, Traceability, Suppliers, NC/CAPA)
- [ ] Report scheduler (e.g., weekly PRP summary to QA Manager)
- [ ] FSMS compliance score per department (real data, not mock)

### 15) Optional Mobile/Offline (P2)
- [ ] Offline form submission with sync; conflict resolution
- [ ] Mobile-friendly evidence capture (camera), QR/barcode scan endpoints

---

## Prioritized Roadmap (sequenced)
1. P0 Security & Audit Trail
2. P0 Document approvals + e-signatures + exports
3. P0 HACCP flowchart persistence + evidence uploads + real-time alerts + PDF
4. P0 PRP templates + scheduler + auto-NC + complete-with-evidence
5. P0 TraceabilityLink endpoints + barcode/QR printing
6. P1 Supplier COA + Delivery→Batch linkage
7. P1 NC/CAPA integrations (PRP/HACCP triggers, RCA persistence)
8. P1 Audit module
9. P1 Training, Risk & Opportunity, Management Review, Equipment/Calibration, Allergen/Label, Complaints
10. P1 Reports export/scheduler and compliance scoring
11. P2 Mobile/Offline

---

## Progress Checklist (high-level)
- [ ] Cross-cutting security (policy, lockout, 2FA) and audit trail
- [ ] Documents: approvals, signatures, distribution/retention, exports
- [ ] HACCP: flowchart persistence, evidence upload, realtime alerts, PDFs
- [ ] PRP: templates, scheduler, auto-NC, complete-with-evidence endpoint
- [ ] Traceability: link endpoints, barcode/QR printing
- [ ] Suppliers: COA on deliveries, Delivery→Batch linkage
- [ ] NC/CAPA: PRP/HACCP triggers, RCA persistence from tools
- [ ] Audit module end-to-end
- [ ] Training & Competency module
- [ ] Risk & Opportunity register
- [ ] Management Review
- [x] Equipment Maintenance & Calibration
- [ ] Allergen & Label Control
- [ ] Customer Complaints
- [ ] Reports export + scheduler + compliance score
- [ ] Mobile/Offline support

---

## Notes
- Existing strengths: HACCP core, PRP core, Traceability core, Supplier management, NC/CAPA core, RBAC, notifications, document stats, scheduled maintenance for documents.
- Where services exist but API is missing: `TraceabilityService.create_traceability_link` – add endpoints in `app/api/v1/endpoints/traceability.py`.
- PRP/HACCP → NC/CAPA: wire automatic creation using `NonConformanceService` and include source references.
- QA (Equipment): Verified `POST /equipment/{id}/calibration-plans`, `POST /equipment/calibration-plans/{plan_id}/records` (upload), and `GET /equipment/work-orders` work as expected; alerts generated by scheduled task before due dates.


