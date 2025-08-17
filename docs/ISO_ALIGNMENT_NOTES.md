### ISO Alignment Summary: Equipment, Maintenance, and Calibration

This document summarizes how the implementation supports ISO 22000 PRPs and calibration traceability best practices (aligned with ISO 10012 principles).

- Equipment master data
  - Fields: `is_active`, `critical_to_food_safety` for risk-based prioritization and accurate population of active equipment in analytics.

- Maintenance programs (PRPs)
  - `MaintenancePlan` includes `frequency_days`, `maintenance_type` (preventive/corrective), `next_due_at`, `last_performed_at`.
  - PRP/SOP linkage via `prp_document_id` to associate plans with documented procedures.
  - `MaintenanceWorkOrder` captures lifecycle and accountability:
    - `status`, `priority`, `assigned_to`, `due_date`, `created_by`, `completed_by`, timestamps.
    - Verification fields: `verified_by`, `verified_at` to confirm proper execution per PRP.

- Calibration management (traceability)
  - `CalibrationPlan` includes `frequency_days`, `schedule_date`, `last_calibrated_at`, `next_due_at`.
  - `CalibrationRecord` includes certificate attachment metadata and traceability:
    - `certificate_number`, `calibrated_by`, `result`, `comments`, plus file metadata.
  - Enforcement service validates calibration status for equipment used in CCP monitoring, with robust status classification: valid, expiring_soon (≤30 days), overdue (≤30 days past due), expired (>30 days past due).

- Notifications and governance
  - Alerts for upcoming maintenance and overdue calibrations.
  - Role-based notification routing to HACCP/maintenance roles.

- Auditability
  - Timestamps and user fields (`created_by`, `completed_by`, `verified_by`) enable audit trails.
  - History endpoints expose maintenance and calibration history for reviews.

- UI support
  - Equipment page shows PRP linked docs for maintenance plans.
  - Work orders display verification status when present.
  - Calibration plans display status and allow certificate upload/download.

- Data and performance considerations
  - Indexes on `maintenance_work_orders(due_date, status)` and `calibration_plans(next_due_at)` to support dashboards and alerts.

Open items
- Extend analytics to use `is_active` for equipment counts and compliance KPIs.
- Add UI affordances to verify work orders and attach PRP references during plan creation.
- Expand automated tests to cover PRP document link and verification flows.