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
- [x] Calibration plan cadence
  - [x] Add `CalibrationPlan.frequency_days: int` (nullable=False, with sensible default)
  - [ ] Backfill existing rows (set from business default, e.g., 365)
  - [ ] Index `CalibrationPlan.next_due_at`
- [x] Maintenance plan scheduling
  - [x] Ensure `MaintenancePlan.next_due_at` is set at creation: now + `frequency_days` (or `start_date` if added)
  - [ ] Add optional `start_date` (nullable) if needed for predictable scheduling
- [x] Work order richness
  - [x] Add `status` Enum('PENDING','COMPLETED') with default 'PENDING'
  - [x] Add `priority` Enum('LOW','MEDIUM','HIGH') (optional, default 'MEDIUM')
  - [x] Add `assigned_to` (FK users.id, nullable)
  - [x] Add `due_date` (nullable, indexed)
  - [x] Add `created_by` (FK users.id)
- [x] Equipment completeness (ISO/PRP)
  - [x] Add `is_active` (bool, default True)
  - [x] Add `critical_to_food_safety` (bool, default False)
  - [ ] Add optional metadata: `asset_tag`, `manufacturer`, `model`, `commissioned_at`, `decommissioned_at`, `owner_department`, `warranty_expiry`
- [x] Calibration record auditability
  - [x] Keep join via plan_id; do not duplicate equipment_id
  - [x] Add optional metadata: `certificate_number`, `calibrated_by` (text/vendor), `result` (pass/fail/text), `comments`
- [ ] Create Alembic migration(s) for all above
  - [ ] Include safe defaults and data backfills
  - [ ] Add indexes (`next_due_at`, `due_date`, `status`)

## Phase 2 — Schemas (Pydantic)
- [x] Equipment
  - [x] Extend `EquipmentCreate`/`EquipmentResponse` with `is_active`, `critical_to_food_safety`
- [x] Maintenance Plan
  - [x] `MaintenancePlanCreate`: allow lowercase `maintenance_type`; optionally `start_date` — accepting lowercase via service normalization
  - [x] `MaintenancePlanResponse`: include `equipment_name`, `last_maintenance_date`, `next_due_date`, computed `status`
- [x] Work Orders
  - [x] `MaintenanceWorkOrderCreate/Response`: include `status`, `priority`, `assigned_to`, `due_date`, `created_by`, and `equipment_name`
- [x] Calibration
  - [x] `CalibrationPlanCreate/Response`: include `frequency_days`, `equipment_name`, `last_calibration_date` (alias), computed `status`
  - [x] `CalibrationRecordResponse`: add certificate metadata fields
- [x] Input normalization helpers (case-insensitive enum handling)

## Phase 3 — Services
- [x] `EquipmentService`
  - [x] Normalize `maintenance_type` input (case-insensitive)
  - [x] `create_maintenance_plan`: set `next_due_at` on creation
  - [x] `list_maintenance_plans`: support `equipment_id` filter
  - [x] `create_work_order`: set `status='PENDING'`, capture `created_by`, optional `assigned_to`, `due_date`, `priority`
  - [x] `list_work_orders`: filter by `equipment_id`, `plan_id`, `status`; include `equipment_name` via endpoint
  - [x] `complete_work_order`: set `status='COMPLETED'`; update plan `last_performed_at` and `next_due_at`
  - [x] `create_calibration_plan`: require `frequency_days`; set `next_due_at = schedule_date`
  - [x] `record_calibration`: use `performed_at` as calibration date; set plan `last_calibrated_at` and `next_due_at = performed_at + frequency_days`
  - [ ] `get_equipment_stats/_get_maintenance_status`: update metrics to use `is_active`
  - [x] `get_upcoming_maintenance/get_overdue_calibrations`: rely on `next_due_at`
- [ ] `EquipmentCalibrationService`
  - [ ] Fix queries: join `CalibrationRecord -> CalibrationPlan` and use `CalibrationRecord.performed_at`
  - [ ] Use `CalibrationPlan.frequency_days` for next calibration computations
  - [ ] Import and use `Role` correctly: `User.role.has(Role.name.in_([...]))`
  - [ ] Return robust statuses: VALID, EXPIRING_SOON (<=30 days), EXPIRED/OVERDUE, NOT_CALIBRATED

## Phase 4 — Endpoints (FastAPI)
- [x] Equipment CRUD
- [x] Maintenance Plans (param/list, update, delete)
- [x] Work Orders (filters, CRUD)
- [x] Calibration Plans & Records (param/list, update, delete, download)
- [x] History endpoints
- [x] Response DTO enrichment (names, status, aliased dates)

## Phase 5 — Frontend alignment
- [x] `src/services/equipmentAPI.ts` verified
- [x] `src/pages/Equipment.tsx` loads plans/calibrations

## Phase 6 — Tests & QA
- [ ] Backend API tests
- [ ] Frontend e2e smoke
- [ ] Performance & indexes

## Phase 7 — ISO/PRP alignment
- [ ] Confirm calibration traceability fields
- [ ] Maintenance PRP linkage (SOP/PRP id, verification)
- [ ] Risk flag (`critical_to_food_safety`) usage in UI/KPIs
- [ ] Auditability: created_by/updated_by, verification user
- [ ] Update docs

## Phase 8 — Deployment & Data
- [ ] Generate and apply Alembic migrations
- [ ] Backfill `next_due_at` for existing plans
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