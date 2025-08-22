# ISO 9001 Production Module Improvement Checklist

Purpose: When all items are checked, the production module will be ISO 9001 compliant (with focus on clauses 7.5, 7.2, 7.1.5, 8.4, 8.5, 8.5.6, 8.6, 8.7), efficient, and deliver an excellent user experience.

## 1) Governance, Data Model, and Auditability
- [ ] Add `ChangeRequest` entity (id, title, reason, linked process/spec/template/doc refs, impact areas, risk rating, validation plan, training plan, effective date, status, created_by, approvals[], closure_review, created_at/updated_at)
- [ ] Add `ChangeApproval` entity (change_request_id, approver_id, role, sequence, decision, comments, signed_at, e_signature_id)
- [ ] Add `ReleaseRecord` entity (process_id/batch_id, verifier_id, approver_id, checklist_results JSON, released_qty/unit, attachments, signed_at, e_signature_id)
- [ ] Add `NonconformingOutput` entity (context refs: process_id/parameter_id/deviation_id, description, containment, disposition, concession/waiver if any, approvals, closed_by, closed_at)
- [ ] Add `MaterialConsumption` entity (process_id, material_id, material_name, supplier_id, lot_number, qty, unit, CoA refs, accepted_by, accepted_at)
- [ ] Add `EquipmentUse` entity (process_id, equipment_id, equipment_name, calibration_due_date, pre_use_check_result, operator_id, used_at)
- [ ] Add `ElectronicSignature` entity (user_id, purpose, payload_hash, signed_at, auth_method, metadata)
- [ ] Add `SpecVersionLink` (process_id, document_id, document_version, locked_parameters)
- [ ] Extend `ProductionProcess` (sop_document_id, sop_document_version, change_request_id, release_status, created_by, updated_by, closed_by, closed_at)
- [ ] Add created_by/updated_by timestamps to: ProcessLog, ProcessParameter, ProcessDeviation, ProcessAlert, YieldRecord
- [ ] Add DB indexes: (process_type, status, created_at), (batch_id), (operator_id), (created_at) for deviations/alerts
- [ ] Implement immutable audit trail events for workflow actions (MOC, release, NC)

## 2) Security, RBAC, Identity, and E‑signatures
- [ ] Enforce authentication across production endpoints; remove placeholder user_id usage
- [ ] Define roles/permissions: Operator, QA Verifier, QA Approver, Production Supervisor, Document Control, Admin
- [ ] Gate approvals/release endpoints by role (only QA Approver can release)
- [ ] Implement electronic signature capture API and hash binding to records (ChangeApproval, ReleaseRecord)
- [ ] Log IP/device/time for signature; verify multi‑factor or re‑auth on sign

## 3) Production Core APIs (Complete and Harden)
- [ ] Implement GET `/production/processes` with filters (type, status, date range, operator, batch) + pagination
- [ ] Implement GET `/production/processes/{id}/details` returning process, steps, logs, parameters, deviations, alerts
- [ ] Implement GET `/production/processes/{id}/parameters` to return parameter list ordered by recorded_at
- [ ] Implement PUT `/production/processes/{id}` for updating non‑critical metadata with audit log
- [ ] Implement POST `/production/processes/{id}/complete` to finalize a process after validations
- [ ] Ensure `record_parameter` validates against locked tolerances from `SpecVersionLink`
- [ ] Ensure auto‑deviation creation on out‑of‑tolerance with severity calculation
- [ ] Ensure `add_log` validates and auto‑diverts when critical criteria unmet (retain current HTST logic) with configurable rules

## 4) Change Control (ISO 9001: 8.5.6)
- [ ] POST `/change-requests` to create change request with reason and impacts
- [ ] PUT `/change-requests/{id}/assess` to attach risk rating, impact areas, validation plan, training plan
- [ ] Workflow: configure approval steps (sequence, required roles)
- [ ] PUT `/change-requests/{id}/approve` (with e‑signature); check role and sequence
- [ ] PUT `/change-requests/{id}/reject` with comments
- [ ] PUT `/change-requests/{id}/implement` to apply changes (bind new doc/spec versions)
- [ ] PUT `/change-requests/{id}/verify-effectiveness` with results evidence
- [ ] PUT `/change-requests/{id}/close` once verified and training complete
- [ ] Enforce that production templates/specs update only via approved, effective change requests

## 5) Release of Product (ISO 9001: 8.6)
- [ ] POST `/production/processes/{id}/release/checklist` to evaluate release criteria and return pass/fail details
- [ ] POST `/production/processes/{id}/release` to record `ReleaseRecord` with e‑signature
- [ ] Enforce release gating: all critical parameters recorded and within tolerance or NC disposition approved; inspections passed; documents current; equipment calibration valid; materials accepted; labels/traceability in place
- [ ] Block shipment/closure API calls unless released

## 6) Control of Nonconforming Outputs (ISO 9001: 8.7)
- [ ] POST `/nonconformance` from deviation/parameter context; pre‑filled data
- [ ] Fields: description, scope, containment action, disposition (rework, scrap, hold, concession), authority approval, verification of effectiveness
- [ ] Link NC to CAPA system; require disposition closed before release (unless concession documented)
- [ ] Reports: NC by severity, process, product; time to closure

## 7) Documented Information (ISO 9001: 7.5)
- [ ] Bind processes to SOP/work instruction document number and version (`SpecVersionLink`)
- [ ] Prevent use of obsolete documents: check current version at point of use
- [ ] Generate PDF/A production sheet: includes doc number/revision, process data, parameters, deviations/NC, release signatures, QR link to record
- [ ] Maintain change log for specs/templates tied to MOC

## 8) Competence and Training (ISO 9001: 7.2)
- [ ] At parameter entry/logging, validate operator competence for the process type
- [ ] Block/flag entries by unqualified operators; require supervisor override with reason
- [ ] Record training completion linked to change effective dates; ensure trained_before_effective

## 9) Monitoring and Measuring Resources (ISO 9001: 7.1.5)
- [ ] Capture `EquipmentUse` at start of process/step with calibration validity check
- [ ] Block critical step execution if calibration is overdue; allow controlled override with NC
- [ ] Link measurement devices to records for traceability

## 10) Externally Provided Processes and Materials (ISO 9001: 8.4)
- [ ] Implement `MaterialConsumption` recording (lot, qty, supplier, CoA)
- [ ] Validate supplier approval status and lot acceptance before consumption
- [ ] Traceability report: process → materials → suppliers → CoAs

## 11) Frontend UX: Production Workspace
- [ ] Add Production Detail page with tabs: Overview, Steps, Parameters, Deviations/NC, Materials, Equipment, Release
- [ ] Step timeline with targets vs. actual charts; highlight out‑of‑tolerance points
- [ ] Guided parameter entry from locked spec (units, tolerances auto‑filled)
- [ ] Quick actions: “Raise Deviation”, “Create NC”, “Acknowledge Alert”
- [ ] Version badge for SOP/work instruction; warning on obsolete version use
- [ ] One‑click PDF production sheet export

## 12) Frontend UX: Change Control (MOC)
- [ ] Change Request form per template: reason, impacted processes/docs, risk assessment, validation plan, training plan, effective date
- [ ] Approval workflow UI: step sequence, role badges, e‑signature dialog, audit trail timeline
- [ ] Implementation and effectiveness review screens with evidence uploads

## 13) Frontend UX: Release Checklist
- [ ] Dynamic checklist displaying pass/fail items with links to failing evidence
- [ ] E‑signature modal for final release with re‑authentication
- [ ] Success page with release certificate number and export options

## 14) Notifications and Real‑time
- [ ] WebSocket notifications for critical deviations, pending approvals, release readiness
- [ ] Escalation rules for unacknowledged critical alerts (time‑based)

## 15) Offline/Mobile and Accessibility
- [ ] Offline queue for parameter/log entries with conflict resolution
- [ ] Mobile‑optimized forms with large touch targets and barcode/QR scanning (batch, lot, equipment)
- [ ] WCAG‑compliant color contrast and focus states in critical workflows

## 16) Testing and Validation
- [ ] Unit tests: services for change control, release gating, competence/equipment guards, parameter validation
- [ ] Integration tests: end‑to‑end MOC and release flow with failure paths
- [ ] E2E tests: template selection → logging → deviation/NC → release → PDF export
- [ ] Contract tests for PDF fields and signatures (hash, signer identity, timestamps)
- [ ] Performance tests: lists pagination under 1s @ 10k records; analytics aggregation jobs

## 17) Performance, Observability, and Operations
- [ ] Add DB indexes and query plans; verify via EXPLAIN on heavy queries
- [ ] Background jobs for analytics KPIs (deviation rate, MOC cycle time, release lead time)
- [ ] Structured audit logs with correlation IDs; dashboard panels for key KPIs
- [ ] Backup/restore plan includes all new entities and files (PDFs, evidence)

## 18) Documentation and Training
- [ ] Update user guides for production, MOC, and release workflows
- [ ] Administrator guide: configuring approval sequences/roles, templates, and tolerances
- [ ] ISO mapping document showing clause → feature evidence

## 19) Acceptance Criteria (Definition of Done)
- [ ] All APIs implemented and passing unit/integration tests
- [ ] Release gate enforces all criteria; unauthorized release attempts blocked and logged
- [ ] MOC process required for any spec/template change; no direct edits possible
- [ ] NC/CAPA integration blocks release until disposition closed or concession documented
- [ ] Production sheet PDF/A includes all required data and signatures; metadata validated
- [ ] UI flows tested on desktop and mobile; offline queue verified
- [ ] KPIs visible on dashboards; audit logs complete and immutable
- [ ] Internal audit sim confirms compliance to 7.5, 7.2, 7.1.5, 8.4, 8.5, 8.5.6, 8.6, 8.7