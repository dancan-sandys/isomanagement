# Equipment & Maintenance Model/API Fix Checklist

This checklist guides fixing functional gaps across models, schemas, services, endpoints, and UI for the equipment, maintenance, and calibration domains. It aligns with ISO 22000 PRP expectations and calibration traceability best practices.

## Scope overview
- Backend: `app/models/equipment.py`, `app/schemas/equipment.py`, `app/services/equipment_service.py`, `app/services/equipment_calibration_service.py`, `app/api/v1/endpoints/equipment.py`
- Frontend: `src/services/equipmentAPI.ts`, `src/pages/Equipment.tsx`
- Migrations: `backend/alembic/versions`
- Tests: `backend/test_equipment_endpoints.py`

---

## Phase 1 — Database and Models
- [ ] MaintenanceType casing normalization
  - [ ] Decide on canonical values (recommend lowercase 'preventive'/'corrective')
  - [ ] If changing enum values, add an Alembic migration to alter Enum values safely; otherwise, normalize input in service layer
- [ ] Calibration plan cadence
  - [ ] Add `CalibrationPlan.frequency_days: int` (nullable=False, with sensible default)
  - [ ] Backfill existing rows (set from business default, e.g., 365)
  - [ ] Index `CalibrationPlan.next_due_at`
- [ ] Maintenance plan scheduling
  - [ ] Ensure `MaintenancePlan.next_due_at` is set at creation: now + `frequency_days` (or `start_date` if added)
  - [ ] Add optional `start_date` (nullable) if needed for predictable scheduling
- [ ] Work order richness
  - [ ] Add `status` Enum('PENDING','COMPLETED') with default 'PENDING'
  - [ ] Add `priority` Enum('LOW','MEDIUM','HIGH') (optional, default 'MEDIUM')
  - [ ] Add `assigned_to` (FK users.id, nullable)
  - [ ] Add `due_date` (nullable, indexed)
  - [ ] Add `created_by` (FK users.id)
- [ ] Equipment completeness (ISO/PRP)
  - [ ] Add `is_active` (bool, default True)
  - [ ] Add `critical_to_food_safety` (bool, default False)
  - [ ] Add optional metadata: `asset_tag`, `manufacturer`, `model`, `commissioned_at`, `decommissioned_at`, `owner_department`, `warranty_expiry`
- [ ] Calibration record auditability
  - [ ] Keep join via plan_id; do not duplicate equipment_id
  - [ ] Add optional metadata: `certificate_number`, `calibrated_by` (text/vendor), `result` (pass/fail/text), `comments`
- [ ] Create Alembic migration(s) for all above
  - [ ] Include safe defaults and data backfills
  - [ ] Add indexes (`next_due_at`, `due_date`, `status`)

## Phase 2 — Schemas (Pydantic)
- [ ] Equipment
  - [ ] Extend `EquipmentCreate`/`EquipmentResponse` with new optional fields (`is_active`, criticality, asset metadata)
- [ ] Maintenance Plan
  - [ ] `MaintenancePlanCreate`: allow lowercase `maintenance_type`; optionally `start_date`
  - [ ] `MaintenancePlanResponse`: include `equipment_name`, `last_maintenance_date` (alias of `last_performed_at`), `next_due_date` (alias of `next_due_at`), and computed `status`
- [ ] Work Orders
  - [ ] `MaintenanceWorkOrderCreate/Response`: include `status`, `priority`, `assigned_to`, `due_date`, `created_by`, and `equipment_name`
- [ ] Calibration
  - [ ] `CalibrationPlanCreate/Response`: include `frequency_days`, `equipment_name`, `last_calibration_date` (alias of `last_calibrated_at`), computed `status`
  - [ ] `CalibrationRecordResponse`: add certificate metadata fields and `download_url` when applicable
- [ ] Input normalization helpers (case-insensitive enum handling)

## Phase 3 — Services
- [ ] `EquipmentService`
  - [ ] Normalize `maintenance_type` input (case-insensitive)
  - [ ] `create_maintenance_plan`: set `next_due_at` on creation; accept optional `start_date`
  - [ ] `list_maintenance_plans`: support `equipment_id` filter; enrich response with `equipment_name`, `status`, and aliased dates
  - [ ] `create_work_order`: set `status='PENDING'`, capture `created_by`, optional `assigned_to`, `due_date`, `priority`
  - [ ] `list_work_orders`: filter by `equipment_id`, `plan_id`, `status`; include `equipment_name`
  - [ ] `complete_work_order`: set `status='COMPLETED'`; update plan `last_performed_at` and `next_due_at`
  - [ ] `create_calibration_plan`: require/accept `frequency_days`; set `next_due_at = schedule_date` or `performed_at + frequency_days` after first record
  - [ ] `record_calibration`: use `performed_at` as calibration date; set plan `last_calibrated_at` and `next_due_at = performed_at + frequency_days`
  - [ ] `get_equipment_stats/_get_maintenance_status`: update metrics to use `is_active` and improved status buckets
  - [ ] `get_upcoming_maintenance/get_overdue_calibrations`: rely on `next_due_at` and frequency; include `equipment_name`
- [ ] `EquipmentCalibrationService`
  - [ ] Fix queries: join `CalibrationRecord -> CalibrationPlan` and use `CalibrationRecord.performed_at`
  - [ ] Use `CalibrationPlan.frequency_days` for next calibration computations
  - [ ] Import and use `Role` correctly: `User.role.has(Role.name.in_([...]))`
  - [ ] Return robust statuses: VALID, EXPIRING_SOON (<=30 days), EXPIRED/OVERDUE, NOT_CALIBRATED

## Phase 4 — Endpoints (FastAPI)
- [ ] Equipment CRUD
  - [ ] GET `/equipment/{id}`
  - [ ] PUT `/equipment/{id}`
  - [ ] DELETE `/equipment/{id}`
- [ ] Maintenance Plans
  - [ ] GET `/equipment/maintenance-plans?equipment_id=` (param variant), keep existing path-based
  - [ ] PUT `/equipment/maintenance-plans/{plan_id}`
  - [ ] DELETE `/equipment/maintenance-plans/{plan_id}`
- [ ] Work Orders
  - [ ] GET `/equipment/work-orders/{id}`
  - [ ] PUT `/equipment/work-orders/{id}`
  - [ ] DELETE `/equipment/work-orders/{id}`
  - [ ] Enhance GET `/equipment/work-orders` to accept `status` and other filters
- [ ] Calibration Plans & Records
  - [ ] GET `/equipment/calibration-plans?equipment_id=` (param variant), keep existing path-based
  - [ ] PUT `/equipment/calibration-plans/{plan_id}`
  - [ ] DELETE `/equipment/calibration-plans/{plan_id}`
  - [ ] GET `/equipment/calibration-records/{record_id}/download` (stream file)
- [ ] History & Analytics
  - [ ] GET `/equipment/maintenance-history` (supports `equipment_id`, `start_date`, `end_date`)
  - [ ] GET `/equipment/calibration-history` (supports `equipment_id`, `start_date`, `end_date`)
  - [ ] Ensure analytics endpoints return shapes used by UI
- [ ] Response DTOs
  - [ ] Ensure enriched DTOs include `equipment_name`, aliased date fields, and computed `status`

## Phase 5 — Frontend alignment
- [ ] `src/services/equipmentAPI.ts`
  - [ ] Verify all methods match backend routes and payloads
  - [ ] Ensure `list*` methods support `equipment_id` param variants
  - [ ] Implement `downloadCalibrationCertificate(recordId)` against new download endpoint
- [ ] `src/pages/Equipment.tsx`
  - [ ] Load and display maintenance plans (`equipmentAPI.listMaintenancePlans`)
  - [ ] Load and display calibration plans (`equipmentAPI.listCalibrationPlans`)
  - [ ] Expect enriched fields (`equipment_name`, `status`, aliased dates)

## Phase 6 — Tests & QA
- [ ] Backend API tests
  - [ ] Update `backend/test_equipment_endpoints.py` to exercise new endpoints and payloads
  - [ ] Add tests for upload + download calibration certificate
  - [ ] Add service-layer tests for scheduling logic (maintenance/calibration next due)
- [ ] Frontend e2e smoke (existing scripts)
  - [ ] Run `frontend_functionality_test.py` and ensure Equipment flows pass
- [ ] Performance & indexes
  - [ ] Verify list endpoints with filters perform adequately; add indexes if needed

## Phase 7 — ISO/PRP alignment
- [ ] Confirm required calibration traceability fields (certificate number, provider, date, next due, status)
- [ ] Confirm maintenance PRP linkage (SOP/PRP document id, verification on completion)
- [ ] Add `critical_to_food_safety` to support risk-based prioritization
- [ ] Ensure auditability: timestamps, `created_by/updated_by`, user actions on completion/verification
- [ ] Update docs to reflect compliance alignment

## Phase 8 — Deployment & Data
- [ ] Generate and apply Alembic migrations
- [ ] Backfill `next_due_at` for maintenance plans and calibration plans
- [ ] Seed demo data for new fields (optional)

---

## Acceptance criteria
- [ ] All endpoints called by `src/services/equipmentAPI.ts` exist and return expected shapes
- [ ] `backend/test_equipment_endpoints.py` passes with ≥95% success and no missing endpoints
- [ ] Frontend Equipment page lists equipment, maintenance plans, work orders, and calibration plans with names/statuses populated
- [ ] Upload and download of calibration certificates works end-to-end
- [ ] Overdue/upcoming analytics reflect correct counts based on `next_due_at`
- [ ] Calibration enforcement service returns correct status and sends notifications to appropriate roles
- [ ] ISO alignment: calibration traceability and maintenance PRP verifiable in data and responses

## Operational notes
- Apply non-interactive migrations and run tests after each phase.
- Prefer enriching response DTOs over pushing UI joins.
- Normalize external inputs (enum strings, dates) defensively.