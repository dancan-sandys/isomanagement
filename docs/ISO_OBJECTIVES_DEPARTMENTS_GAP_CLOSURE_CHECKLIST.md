### ISO Objectives & Departments Gap Closure Checklist

Purpose: Complete every checkbox to achieve an ISO-aligned, efficient, auditable, and user-friendly Objectives & Departments module.
Scope: ISO Annex SL 6.2 (Objectives), with mappings to ISO 9001:2015 (6.2), ISO 14001:2015 (6.2), ISO/IEC 27001:2022 (6.2), ISO 22000:2018 (6.2, 9.3), and ISO 31000 for risk linkage.
Outcome: When all items are checked, gaps are closed and the system is audit-ready with great UX.

### References
- Annex SL / Harmonized Structure: Objectives planning and evaluation (clause 6.2)
- ISO 9001:2015 6.2 Quality objectives and planning to achieve them
- ISO 14001:2015 6.2 Environmental objectives and planning to achieve them
- ISO/IEC 27001:2022 6.2 Information security objectives and planning to achieve them
- ISO 22000:2018 6.2 Food safety objectives; 9.3 Management review
- ISO 31000:2018 Risk management principles and guidelines

### 1) Data model completeness (Objectives, Targets, Progress, Departments)
- [ ] Objective: owner_user_id (required), sponsor_user_id (optional) stored and indexed
- [ ] Objective: method_of_evaluation (enum/text) and acceptance_criteria (JSON/thresholds) present
- [ ] Objective: resource_plan (text/JSON), budget_estimate (number, currency) present
- [ ] Objective: communication_plan (text), review_frequency (enum), next_review_date present
- [ ] Objective: linked_risk_ids (array), linked_control_ids (e.g., CCP/OPRP), linked_document_ids present
- [ ] Objective: management_review_refs (array of MR session IDs) present
- [ ] Objective: status lifecycle supports planned/active/on_track/at_risk/off_track/closed
- [ ] Objective: version, superseded_by_id, change_reason present for versioning
- [ ] Objective: last_updated_by/at maintained via backend automatically
- [ ] Target: baseline_value, target_value, unit_of_measure validated and required appropriately
- [ ] Target: calculation_method (manual/aggregated/formula) present
- [ ] Target: upper_threshold and lower_threshold supported; rationale captured
- [ ] Progress: evidence_document_ids (array) supported; data_capture_method present
- [ ] Progress: qa_verified_by and qa_verified_at supported
- [ ] Department: manager_id present and enforced; parent_department_id supports hierarchy
- [ ] Department: raci JSON structure or equivalent governance metadata present

Acceptance: DB migrations created and applied; schema reflected in OpenAPI and type definitions; seed/update scripts backfilled without data loss.

### 2) API coverage and integrity
- [ ] Departments: full CRUD implemented (create, list, get, update, delete) with DB persistence
- [ ] Objectives: CRUD with ISO 6.2 mandatory fields validation server-side
- [ ] Objectives: assign/approve/close endpoints with workflow and RBAC enforced
- [ ] Objectives: link/unlink endpoints for risks, controls, documents, MR references
- [ ] Objectives: evaluate endpoint to record evaluation result and update status
- [ ] Progress: bulk create, list, evidence linking, and verification supported
- [ ] Targets: bulk create and list; validation of period/frequency alignment
- [ ] Dashboards: KPIs, trends, alerts compute from real data (no placeholders)
- [ ] Export: JSON/CSV/XLSX (and PDF if available) with signed URLs and filters
- [ ] Pagination, filtering (type, dept, hierarchy, status, color, dates) consistent across endpoints
- [ ] OpenAPI docs updated; frontend services aligned; error messages actionable

Acceptance: All endpoints have integration tests (200/4xx/403/404), and no placeholder returns remain.

### 3) Business rules, automation, and calculations
- [ ] Status automation: server computes on_track/at_risk/off_track using thresholds and trend slope
- [ ] Due/overdue automation based on target_date and review_frequency/next_review_date
- [ ] Risk-weighted priority index incorporates ISO 31000 likelihood × impact for sorting/highlighting
- [ ] Review scheduler generates tasks; notifications emitted for upcoming/overdue reviews
- [ ] Objective closure requires evaluation, evidence, and approval per RBAC
- [ ] Department rollup: child objectives cascade to parent metrics with defined aggregation logic

Acceptance: Unit tests cover boundary cases, hysteresis, and aggregation logic; dashboards reflect automated states.

### 4) Auditability and change control
- [ ] Immutable audit log of objective/target/progress changes with actor, timestamp, before/after diffs
- [ ] Progress corrections done via reversal entries with reason; originals preserved
- [ ] Read API supports time-travel or revision retrieval for audit
- [ ] Export includes change log where applicable; signatures/approvals tracked

Acceptance: Audit log entries verified in tests; retrieval endpoints produce complete trace for a sample objective.

### 5) RBAC and governance
- [ ] Roles mapped: System Administrator, QA Manager, QA Specialist, Production Manager, Department Manager, Viewer
- [ ] Permissions enforced server-side: create/update/approve/close/assign/evidence-verify per role
- [ ] Segregation of duties: owners cannot approve their own objectives by policy
- [ ] Department scoping: users limited to their departments unless elevated roles

Acceptance: Authorization tests pass for each protected action; least-privilege verified.

### 6) Risk and FSMS integration
- [ ] Link objectives to risks (ISO 31000) with live status and severity
- [ ] Link objectives to CCP/OPRP/PRP controls (ISO 22000) when relevant
- [ ] Risk-based dimension available in dashboards (filters, heatmap overlays)
- [ ] Management Review (9.3) outcomes can create/update objectives; MR references stored on objectives

Acceptance: Cross-module tests demonstrate links and consistent navigation; dashboards show risk overlays.

### 7) Evidence and document control
- [ ] Attach evidence documents to progress entries and evaluations
- [ ] Evidence references validated (existence, permissions); preview/download flows secure
- [ ] Data_source and auto_ingest_source_id support system/integration sources
- [ ] Evidence verification workflow (assign verifier, record verification)

Acceptance: Upload/associate/verify flows tested; evidence appears in exports and audits.

### 8) Frontend UX: creation and management
- [ ] Objective creation wizard enforces ISO 6.2 fields with inline validations and tooltips
- [ ] Guided steps: Context & Alignment → Targets & Thresholds → Plan & Resources → Risks/Controls → Review & Communication
- [ ] Hierarchical tree view with drag-and-drop and alignment indicators to policy and risks
- [ ] Objective detail tabs: Overview, Plan, Risks & Controls, Evidence, Progress, Evaluation, History, MR Links
- [ ] Progress entry form supports evidence attach and verification; input masks and date pickers use ISO format
- [ ] Inline status, thresholds, and due/overdue badges with accessible color contrast

Acceptance: UX review passes; accessibility checks (contrast, keyboard nav) pass; E2E flows green.

### 9) Frontend UX: dashboards and reporting
- [ ] Department scorecards (on-track/at-risk/off-track, completion rate, average attainment)
- [ ] Trend graphs with annotations/justifications; ability to add notes for anomalies
- [ ] Risk-weighted performance view and heatmap; department comparisons
- [ ] Export from UI with filters preserved and context headers
- [ ] Performance alerts panel with drill-down into underlying objectives

Acceptance: Dashboard data matches backend KPIs; interactions are performant and accessible.

### 10) Performance, resilience, and scalability
- [ ] API queries optimized with indexes; N+1 avoided; measured response times under agreed SLOs
- [ ] Batch endpoints for bulk progress/targets efficient and safe (validation, partial failure handling)
- [ ] Background jobs for review scheduling and notifications resilient with retries
- [ ] Caching/pagination implemented for heavy dashboards

Acceptance: Load test baseline documented; SLOs met in test environment.

### 11) Testing: unit, integration, E2E, and ISO conformance
- [ ] Unit tests cover calculations, status automation, permissions, and validators
- [ ] Integration tests cover full API flows including RBAC and error states
- [ ] E2E tests cover wizard, dashboards, evidence, and approvals
- [ ] ISO conformance tests verify 6.2 required data presence and review cadence enforcement

Acceptance: Test suite green in CI; coverage thresholds met; conformance suite passes.

### 12) Migrations and data backfill
- [ ] Migrations created for all new fields/tables/indexes with rollback scripts
- [ ] Backfill existing objectives with default owners, review frequencies, and status
- [ ] Idempotent seed updates (demo data) reflect new fields and flows

Acceptance: Migration run tested locally and in staging; data integrity verified.

### 13) Documentation, training, and clause mapping
- [ ] Update API and type docs; add field-level guidance aligned to ISO
- [ ] Create a clause-to-feature mapping matrix for audits
- [ ] Update Management Review docs to cover objective linkage and outcomes
- [ ] In-app help and tooltips cite relevant clauses (non-normative)

Acceptance: Docs published; internal training shared; auditors can navigate mapping quickly.

### 14) Telemetry, notifications, and observability
- [ ] Emit events for create/update/approve/close/review due/overdue
- [ ] Notification channels configured (email/in-app) with preferences by role
- [ ] Metrics for objective lifecycle times, review adherence, evidence verification SLAs
- [ ] Logs and traces instrumented for key flows

Acceptance: Dashboards visible to admins; alerts configured for misses or backlogs.

### 15) Rollout & governance
- [ ] Feature flags guard major UX changes; phased rollout plan defined
- [ ] Data privacy review performed; access to sensitive objectives scoped
- [ ] Post-rollout monitoring and feedback loop established

Acceptance: Rollout executed with no P1 issues; feedback captured and acted upon.

### Sign-off checklist
- [ ] Product/Process Owner sign-off
- [ ] QA/Compliance sign-off
- [ ] Security/Risk sign-off
- [ ] Department Managers sign-off
- [ ] Final management review acceptance recorded (ISO 22000 9.3)