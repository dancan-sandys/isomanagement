### ISO 22000 Production Workflow Implementation Checklist (Stateful FSM + Audit)

- [x] Define data model mappings to existing SQLAlchemy models
  - **Batch**: map to `app.models.traceability.Batch` (ensure status transitions are audited)
  - **Process/Stage**: use `ProductionProcess` and `ProcessStage` as FSM instances
  - **Measurements**: use `StageMonitoringRequirement` + `StageMonitoringLog` and `ProcessParameter`
  - **Audit**: leverage `log_audit_event` and `StageTransition`

- [x] Seed versioned workflow JSONs
  - **fresh_milk_workflow.json**: HTST 72C x 15s with auto-divert
  - **yoghurt_mala_workflow.json**: fermentation params per variant
  - **cheese_workflow.json**: coagulation and ageing controls

- [x] Implement workflow engine
  - Load JSON by `product_type`
  - Instantiate `ProcessStage` rows in sequence
  - Derive `StageMonitoringRequirement` from conditions
  - Bind workflow version to `ProductionProcess.spec`

- [x] Expose APIs
  - GET `/api/v1/workflows/{product_type}`
  - POST `/api/v1/workflows/instantiate/{product_type}` {batch_id, operator_id, fields}
  - POST `/api/v1/workflows/validate` {process_id}
  - Reuse progression endpoints in `batch_progression`

- [ ] Operator UX (future)
  - Stage panel with live PASS/FAIL badges
  - Gate signing with e-sign and re-auth
  - Pass/Fail/Rework/Divert actions
  - Timeline + audit viewer

- [x] Yield calculation
  - Formula: ((total_yield_kg - start_qty_kg)/start_qty_kg)*100
  - Store context for losses

- [ ] Compliance controls
  - Auto-divert sets HOLD and alerts QA
  - Append-only audit events, include WHO/WHEN/WHAT/WHY
  - Sampling policy enforcement (ONLINE or 30-min)
  - Workflow version pinned per process

- [ ] Bold Challenge demo (Fresh Milk)
  1. Create batch (start 1000 kg)
  2. Instantiate `fresh_milk` workflow
  3. Start process
  4. Ingest 10-min stream: include a 10s dip to 70C
  5. Verify auto-divert event exists and stage transitions reflect HOLD/DIVERT
  6. Rework to pasteurization and continue
  7. Record yield 950 kg → expect -5.0% underrun
  8. Generate PDF batch record (future) and verify 5W1H

- [ ] Test scenarios
  - HTST pass
  - HTST auto-divert on dip
  - Yield underrun computation

- [ ] Security & roles
  - Only QA releases HOLD
  - E-sign requires re-auth; signature hashing stored
  - Clock skew and tamper-evident audit

