### HACCP roles and responsibilities (mapped to RBAC)

This document defines standard HACCP roles, their responsibilities, and the required permissions mapped to the existing RBAC `Module` and `PermissionType` enums. Use this as the authoritative reference for seeding roles and enforcing permissions in endpoints.

#### Notes
- Module names reference `app.models.rbac.Module`. Actions reference `app.models.rbac.PermissionType`.
- Where finer-grained control is needed (e.g., monitoring vs plan edits), we map to the closest existing actions and constrain usage in the service/endpoints.
- Separation of duties is enforced by assigning different roles to monitoring vs verification/approval.

### Core roles

#### 1) HACCP Team Leader (or HACCP Coordinator)
- Responsibilities:
  - Lead hazard analysis workshops and maintain the HACCP plan
  - Define and update CCPs, critical limits, monitoring procedures
  - Coordinate validation and revalidation activities
  - Prepare plan for approval workflow
- Required permissions (minimum):
  - HACCP: view, create, update, export
  - Documents: view, export (reference SOPs/evidence)
  - PRP: view (reference PRPs used as controls)
  - Traceability: view (for batch context)
  - NC/CAPA: view (link corrective actions)

#### 2) QA Verifier
- Responsibilities:
  - Conduct verification activities: record review, direct observation, sampling/testing
  - Confirm adherence to monitoring procedures and acceptance criteria
  - Ensure equipment used is calibrated/within period prior to accepting records
- Required permissions (minimum):
  - HACCP: view, update (create verification logs)
  - Documents: view, export
  - Maintenance: view (calibration records)

#### 3) QA Approver (QA Manager)
- Responsibilities:
  - Approve HACCP plans and changes
  - Approve batch disposition following out-of-spec events
  - Oversee validation evidence and revalidation triggers
- Required permissions (minimum):
  - HACCP: view, approve, export, update
  - Documents: view, approve, export
  - NC/CAPA: view, approve
  - Traceability: view (for batch hold/disposition)

#### 4) Production Manager
- Responsibilities:
  - Oversee execution of monitoring by operators
  - Initiate corrective actions, open NCs when necessary
  - Review operational trends (non-approving role)
- Required permissions (minimum):
  - HACCP: view, update (may log monitoring if needed), export
  - NC/CAPA: view, create, update
  - Traceability: view, create, update

#### 5) Line Operator (Monitor)
- Responsibilities:
  - Perform CCP monitoring at defined frequency
  - Record measurements and attach evidence
  - Initiate immediate corrective actions as per SOP (non-approving role)
- Required permissions (minimum):
  - HACCP: view, create (create monitoring logs only), update (edit own logs in session if permitted)
  - Traceability: view, create (batch selection/creation if permitted)

#### 6) Auditor
- Responsibilities:
  - Review HACCP plan conformance and records
  - Raise NCs on gaps; no operational edits
- Required permissions (minimum):
  - HACCP: view, export
  - Audits: view, create, update, export
  - NC/CAPA: view, create, update, export
  - Documents: view

#### 7) Compliance Officer (Read-only)
- Responsibilities:
  - Organization-wide read access for compliance oversight
- Required permissions (minimum):
  - HACCP: view, export
  - Documents/PRP/Traceability/NC-CAPA: view, export

### Permission matrix (by module → actions)

Use the following as a guide when seeding/assigning permissions:

- HACCP
  - Line Operator: view, create (monitoring logs), update (own logs), export
  - Production Manager: view, update, export
  - HACCP Team Leader: view, create, update, export
  - QA Verifier: view, update (create verification logs), export
  - QA Approver: view, update, approve, export
  - Auditor/Compliance: view, export

- NC/CAPA
  - Line Operator: create (when out-of-spec), view
  - Production Manager: view, create, update
  - QA Approver: view, approve
  - Auditor: view, create, update, export
  - Compliance: view, export

- Documents
  - HACCP Team Leader: view, export
  - QA Approver: view, approve, export
  - Auditor/Compliance: view, export

- Traceability
  - Line Operator: view, create (batch selection/creation if allowed)
  - Production Manager: view, create, update
  - QA Approver/Compliance/Auditor: view (export for reporting)

- Maintenance (Calibration)
  - QA Verifier: view
  - Maintenance Engineer: view, create, update, delete, assign, export

### Separation of duties rules

- Operators who create monitoring logs cannot verify or approve those same records.
- QA Verifiers cannot approve plans they verified alone; QA Manager approves final plans.
- Plan approval is blocked unless validation evidence is present and hazard analysis sign-offs are complete.

### Competency and training requirements

- Monitoring and verification actions require assigned training/competency for the specific CCP and equipment.
- The system shall validate competency at action time; otherwise reject with 403.

### Endpoint enforcement guidelines

- Monitoring logs: require HACCP:view + HACCP:create (and competency); enforce equipment calibration.
- Verification logs: require HACCP:view + HACCP:update and role = QA Verifier (or QA Manager), and role segregation from monitor.
- Plan approval: require HACCP:approve (QA Manager) and preconditions: validation present, sign-offs complete.
- Hazard/CCP edits: require HACCP:update (HACCP Team Leader or QA Manager).

### Mapping to existing seeded roles

- QA Manager → QA Approver responsibilities (plus plan editing if desired)
- Production Manager → Production Manager responsibilities
- Line Operator → Line Operator responsibilities
- Auditor → Auditor responsibilities
- Compliance Officer → Compliance responsibilities
- Additions recommended to seed:
  - "HACCP Team Leader" (new)
  - "QA Verifier" (new)

These new roles should be added to `backend/create_rbac_seed_data.py` with the permissions described above.


