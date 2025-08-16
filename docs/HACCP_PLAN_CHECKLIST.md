### HACCP implementation hardening checklist (FDA/FSIS/ISO 22000 aligned)

This checklist closes the identified gaps in the current HACCP module and ensures an efficient, compliant end-to-end process across backend and frontend. Complete each section in order. Track status with the checkboxes.

#### Legend
- [ ] = To do, [x] = Done
- Artifacts: files, endpoints, UI views to be created/updated
- Acceptance: concrete acceptance criteria

### 1) Governance, roles, and access control
- [x] Define HACCP roles and responsibilities (Operators, QA Verifier, QA Manager, Approver) and map to `rbac` roles.
  - Artifacts: `backend/app/core/permissions.py`, role seeds, documentation
  - Acceptance: Only permitted roles can create hazards/CCPs, log monitoring, verify, and approve plans.
- [x] Enforce permissions in HACCP endpoints (create/update/delete, approve/verify).
  - Artifacts: `backend/app/api/v1/endpoints/haccp.py`
  - Acceptance: All sensitive endpoints validate role; unauthorized calls return 403.
- [x] Integrate training/competency checks for monitoring and verification.
  - Artifacts: `backend/app/models/training.py`, usage in endpoints/services
  - Acceptance: Users without required competency cannot log monitoring or verification.
- [x] Action-specific competency policy (monitor vs verify) and optional CCP/equipment-specific requirements.
  - Artifacts: DB migration to extend `role_required_trainings` with `action` (enum: monitor|verify) or new table `haccp_required_trainings(role_id, action, ccp_id|equipment_id, program_id)`; service updates.
  - Acceptance: Policy can target action and optionally CCP/equipment; enforcement prefers specific policy over role-wide; unit tests cover cases.
- [x] Admin eligibility endpoints for visibility and audits.
  - Artifacts: `GET /training/matrix/{user_id}` (admin view of any user); `GET /training/eligibility?user_id=&action=&ccp_id=&equipment_id=` returning `{ eligible, missing_program_ids }`.
  - Acceptance: Admin can query any user’s eligibility and see missing trainings; responses are fast and paginated where needed.
- [x] User Management UI: Training & Competency management.
  - Artifacts: Update `frontend/src/pages/Users.tsx` with a dialog/tab to view a selected user’s training matrix, eligibility badges for monitor/verify, and list missing trainings; actions to assign required trainings.
  - Acceptance: Admin can view eligibility at a glance and assign requirements without leaving the page; changes reflect immediately.
- [x] Add role-required training assignment in dialog and a simple admin view for role requirements.
  - Artifacts: In `Users.tsx` competency dialog: list role-required trainings for the user’s role, add/select program, delete entries; Admin tab to list and manage role-required records.
  - Acceptance: Admin can add/remove role-required training quickly; list refreshes without page reload.
- [x] Enrich role-required list to show program code/title instead of IDs.
  - Artifacts: Join against program list in `Users.tsx` and render `code — title`.
  - Acceptance: UI shows human-readable program names in the role-required table.
- [x] Scoped requirement assignment controls (monitor/verify + optional CCP/equipment) in Users dialog.
  - Artifacts: Add action selector and optional CCP/equipment pickers; call `/training/required/haccp` endpoints.
  - Acceptance: Admin can assign/remove scoped requirements from within the dialog; selections persist.
- [x] Role-required training configuration UI (with action and optional CCP/equipment scoping).
  - Artifacts: Admin view under Training to add/list/remove required trainings (uses `/training/required` and new action/scoping fields).
  - Acceptance: Policies are persisted and visible; duplicates prevented; audit logs captured.

### 2) Product, process flow, and batch integration
- [x] Ensure `ProcessFlow` fully represents actual flow; require at least one step.
  - Acceptance: Cannot approve HACCP plan if no flow exists.
- [x] Link monitoring logs to `Traceability.Batch` via `batch_id` (not free-text only).
  - Artifacts: DB migration, model field addition; keep `batch_number` for legacy display.
  - Acceptance: Monitoring logs must reference a valid batch; UI allows selecting a batch.

### 3) Hazard analysis (Principle 1)
- [x] Standardize hazard analysis data capture (rationale, PRP reliance, references).
  - Artifacts: Extend `Hazard` model/schema with `rationale`, `prp_reference_ids`, `references`.
  - Acceptance: Hazard record stores reasoning and links to PRPs/SOPs.
- [x] Configurable risk model (matrix thresholds/scales per site/product).
  - Artifacts: `RiskThreshold` model, API endpoints, frontend management UI, service integration.
  - Acceptance: Risk levels computed per configured thresholds; supports site-wide, product-specific, and category-specific configurations; different calculation methods (multiplication, addition, matrix).
- [x] Team review sign-off for hazard analysis.
  - Artifacts: `HazardReview` model, API endpoints, review criteria tracking.
  - Acceptance: Hazard reviews track identification, risk assessment, control measures, and CCP determination; product-level review status endpoint available.
- [x] **CRITICAL: Restructure risk assessment to be ISO 22000/HACCP compliant (product-specific, not global).**
  - **Issue:** Current global risk thresholds violate ISO 22000 principles. Risk assessment must be product-specific and integrated with hazard analysis.
  - **Artifacts:** ✅ Added `ProductRiskConfig` model; ✅ Updated HACCP service to use product-specific risk calculation; ✅ Created database migration; ✅ Updated models imports.
  - **Acceptance:** Each product has its own risk configuration; risk calculation happens during hazard creation/editing; no global risk thresholds; fully compliant with ISO 22000 Clause 8.5.2-8.5.4.

### 4) CCP determination (Principle 2)
- [x] Replace heuristic decision tree with explicit Codex branching (Q1–Q4), persist answers.
  - Artifacts: ✅ Added `DecisionTree` model; ✅ Created Pydantic schemas; ✅ Updated HACCP service with decision tree methods; ✅ Created database migration.
  - Acceptance: Given a defined answer path, the system produces the Codex-consistent CCP decision with full step audit.
- [x] Frontend interactive decision tree UI linked to hazards.
  - Artifacts: ✅ Created `DecisionTreeDialog` component; ✅ Added API endpoints for decision tree operations; ✅ Integrated decision tree button into hazard cards; ✅ Added decision tree API client methods.
  - Acceptance: Users can click the decision tree button on any hazard to run the Codex Alimentarius decision tree with interactive Q&A flow.
  - Artifacts: React component(s) under `frontend/src/components/HACCP/DecisionTree/`.
  - Acceptance: Users can answer Q1–Q4 with explanations; result displays CCP decision and persists.

### 5) Critical limits (Principle 3)
- [x] Support numeric and qualitative limits; allow multi-parameter constraints (e.g., time-temperature pairs).
  - Artifacts: ✅ Enhanced CCP model with `critical_limits` JSON field; ✅ Added `CriticalLimitParameter` and `ValidationEvidence` schemas; ✅ Implemented `validate_limits()` and `get_limits_summary()` methods; ✅ Created database migration.
  - Acceptance: CCPs can now define multiple parameters with numeric/qualitative limits and validation evidence.
- [x] Standardize units (UCUM) and validate.
  - Artifacts: ✅ UCUM units library with validation; ✅ Unit conversion utilities; ✅ Enhanced schema validation for parameter-specific units; ✅ Comprehensive unit type mapping.
  - Acceptance: Only allowed UCUM units can be saved; unit conversions handled consistently; parameter-specific unit validation enforced.
- [x] Reference validation evidence (SOPs, studies).
  - Artifacts: ✅ `ValidationEvidence` schema with multiple evidence types; ✅ Service methods for adding/removing evidence; ✅ API endpoints for evidence management; ✅ Evidence summary and validation completeness tracking.
  - Acceptance: Each critical limit can have multiple reference documents; evidence is tracked and validated prior to plan approval.

### 6) Monitoring (Principle 4)
- [ ] **FIXED: Monitoring log creation endpoint (POST /ccps/{id}/monitoring-logs/enhanced) returning 500 error.**
  - **Issue:** Endpoint fails with 500 Internal Server Error despite debug logging showing data is received correctly.
  - **Status:** Debugged extensively - server running with Python 3.x, data validation improved, but still failing.
  - **Next Steps:** Investigate in Section 4 or later when focusing on monitoring improvements.
  - **Acceptance:** Monitoring logs can be created successfully without errors.
- [ ] Structured monitoring schedule (interval/cron + tolerance window) instead of free-text.
  - Artifacts: `CCPMonitoringSchedule` model; UI scheduler control.
  - Acceptance: Backend can compute due/overdue states; UI shows next due and overdue badges.
- [ ] Missed monitoring detection job with alerts.
  - Artifacts: Background task in `services/scheduled_tasks.py`.
  - Acceptance: When a due window is missed, notification is sent and appears on dashboard.
- [ ] Enforce competent user logging; capture device/equipment used.
  - Artifacts: Endpoint validation + `equipment_id` on logs.
  - Acceptance: Attempt to log without competency or with out-of-calibration equipment is rejected.

### 7) Corrective actions and product hold (Principle 5)
- [ ] Mandatory NC/CAPA creation on out-of-spec monitoring (all routes).
  - Artifacts: Route consolidation to service; enforce in `create_monitoring_log`.
  - Acceptance: Every out-of-spec log automatically creates an NC with severity heuristic and links to batch.
- [ ] Automatic product hold/quarantine on affected batch; disposition workflow.
  - Artifacts: `Batch.status` updates and release approval; UI to manage hold/release.
  - Acceptance: Batch remains on hold until QA disposition is recorded with e-signature.

### 8) Verification (Principle 6)
- [ ] Define and schedule verification activities (record review, direct observation, sampling/testing, calibration checks).
  - Artifacts: `CCPVerificationProgram`, scheduled tasks, UI dashboard.
  - Acceptance: Verification tasks appear on a calendar/queue and require role-based completion.
- [ ] Role segregation enforcement (operator vs verifier).
  - Acceptance: The same user cannot verify their own monitoring logs.
- [ ] Add missing GET endpoint for verification logs and pagination.
  - Artifacts: `GET /haccp/ccps/{ccp_id}/verification-logs` with paging; update `frontend/src/services/haccpAPI.ts`.
  - Acceptance: Frontend call returns paged logs without 404.

### 9) Validation and revalidation
- [ ] Add `CCPValidation` artifacts linking to process authority letters/tests.
  - Acceptance: Plan cannot reach approval without validation entries.
- [ ] Revalidation scheduling and triggers (formula changes, equipment changes, trend shifts).
  - Acceptance: Revalidation tasks are generated when configured triggers occur.

### 10) Recordkeeping and evidence (Principle 7)
- [ ] Replace free-text `evidence_files` with first-class attachments linked to `Document` storage.
  - Acceptance: Evidence is uploaded/stored with metadata and versioning.
- [ ] Immutable monitoring/verification logs with e-signatures; full audit trail.
  - Artifacts: Append-only or WORM-like constraints; audit log entries.
  - Acceptance: Updates preserve history; signatures captured on critical events.

### 11) Service-layer consolidation and endpoint cleanup
- [ ] Deduplicate routes in `haccp.py`; keep single definitions.
  - Acceptance: No duplicate blocks; API surface documented and tested.
- [ ] Route all write paths through `HACCPService` to centralize risk calc, NC, notifications, validation.
  - Acceptance: Direct DB writes removed from endpoints; unit tests cover service logic.
- [ ] Switch endpoints from `dict` payloads to Pydantic schemas (`backend/app/schemas/haccp.py`).
  - Acceptance: Strict validation, consistent error responses.

### 12) Data model hardening
- [ ] Add FK `batch_id` to monitoring logs; maintain `batch_number` for display.
- [ ] Unique constraint on `(product_id, ccp_number)`.
- [ ] JSON columns for complex `limits` and `test_results` instead of `Text` JSON strings where applicable.
- [ ] Indexes for monitoring/verification logs on `ccp_id`, `monitoring_time`.
  - Acceptance: DB migration applies cleanly; backfills consistent.

### 13) Equipment calibration enforcement
- [ ] Equipment entity linkage for CCPs and logs; calibration status check at log time.
  - Acceptance: Out-of-calibration equipment blocks logging or flags NC.

### 14) Notifications and dashboards
- [ ] Alerts on out-of-spec, missed monitoring, verification overdue.
  - Acceptance: Alerts appear in notification center and enhanced dashboard.
- [ ] HACCP dashboard shows KPIs: active CCPs, due/overdue monitoring, out-of-spec trends, verification status.
  - Artifacts: Extend `/haccp/dashboard/enhanced`.

### 15) Frontend UX flows
- [ ] HACCP workspace overview (products, plan status, alerts).
- [ ] Flowchart builder integrated with process steps and hazards overlay.
- [ ] Hazard analysis table with filters, risk calc, sign-offs.
- [ ] Decision tree UI for each hazard, with stored step answers and justification.
- [ ] CCP editor with complex limit builder (numeric, qualitative, multi-parameter), SOP links, unit selection.
- [ ] Monitoring console: list of due CCP checks, quick entry, equipment selector, batch picker, evidence upload.
- [ ] Verification console: scheduled tasks, sampling plans, role-restricted actions.
- [ ] NC/CAPA linking from monitoring entries; batch hold/release view.
  - Acceptance: UX supports end-to-end workflow with minimal clicks and clear statuses.

### 16) Reporting and exports
- [ ] HACCP plan report (hazard analysis table, CCP summaries) matching FSIS guidebook structure.
- [ ] Monitoring trend charts; export to PDF/Excel.
- [ ] Audit-ready evidence export with filters/date ranges.
  - Acceptance: Reports render and download; totals match database queries.

### 17) Testing and quality gates
- [ ] Unit tests for service logic (risk, decision tree, alerts, NC creation).
- [ ] API tests for endpoints (auth, RBAC, payload validation, pagination).
- [ ] E2E tests for core UX flows (Cypress/Playwright).
- [ ] Performance regression tests on monitoring log ingestion and dashboard queries.
  - Acceptance: CI green; coverage thresholds met; performance within targets.

### 18) Data migration and backfill
- [ ] Migration scripts to add new fields and backfill from legacy Text JSON where needed.
- [ ] Backfill `batch_id` where possible using `batch_number` mapping.
  - Acceptance: Zero data loss; post-migration integrity checks pass.

### 19) Documentation and training
- [ ] Update API docs and architectural diagrams.
- [ ] SOPs for monitoring, verification, corrective actions, and plan approval embedded as documents.
- [ ] Internal training materials and role guides.
  - Acceptance: Users can perform duties with new system; feedback addressed.

### 20) Definition of Done (overall)
- [ ] All checklist items completed or risk-accepted with documented rationale.
- [ ] FDA/FSIS 7 principles traceability matrix completed.
- [ ] ISO 22000 clauses mapped to system features with evidence links.
- [ ] Internal audit walkthrough completed; findings closed.

### Compliance traceability matrices

#### FDA/FSIS HACCP principles mapping (excerpt)
- **Principle 1**: Hazard analysis — Sections 3, 2; evidence: Hazard table, sign-offs.
- **Principle 2**: CCPs — Section 4; evidence: Decision tree records per hazard.
- **Principle 3**: Critical limits — Section 5; evidence: Limit definitions with references.
- **Principle 4**: Monitoring — Section 6; evidence: Schedules, due/overdue, logs.
- **Principle 5**: Corrective actions — Section 7; evidence: NCs, batch hold/disposition.
- **Principle 6**: Verification — Section 8; evidence: program tasks, records, role separation.
- **Principle 7**: Recordkeeping — Section 10; evidence: immutable logs, e-signatures, document links.

#### ISO 22000 alignment (excerpt)
- Context/Leadership/Planning/Support — PRPs, roles, training, communication.
- Operation — Hazard control plan (this module) integrated with PRPs and traceability.
- Performance evaluation — Monitoring, verification KPIs and management review.
- Improvement — NC/CAPA integration and trend analysis.

### References
- FDA HACCP Principles and Application Guidelines
- FSIS Guidebook for the Preparation of HACCP Plans
- ISO 22000 Food safety management systems


