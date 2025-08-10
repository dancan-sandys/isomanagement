## Frontend ⇄ Backend API Gap Analysis

Last updated: 2025-08-10

Scope: Compare frontend service calls in `frontend/src/services/**` against backend routes mounted under `/api/v1` to identify mismatches and missing pieces. Includes a phased plan to close gaps.

### Legend
- FE: Frontend request (method + path)
- BE: Backend route (method + path)
- Action: Proposed fix (Frontend change, Backend change, or Remove/Defer)

---

### A) Frontend calls with no matching backend route or mismatched method/path/params

1) Dashboard
- FE: GET `/dashboard`, GET `/dashboard/stats`, GET `/dashboard/recent-activity`
- BE: routes exist in `backend/app/api/v1/endpoints/dashboard.py` but the router is NOT mounted in `api.py`
- Action: Backend change — include `dashboard.router` in `backend/app/api/v1/api.py`

2) Settings
- FE: GET `/settings` (OK)
- FE: PUT `/settings/{settingId}` with `{ value }`
  - BE: PUT `/settings/{setting_key}` expects key (string) and `SettingUpdate` body
  - Action: Frontend change — use string key; update typing and callers
- FE: POST `/settings` (create)
  - BE: No create endpoint
  - Action: Remove/Defer or add BE create if required
- FE: DELETE `/settings/{settingId}`
  - BE: No delete endpoint
  - Action: Remove/Defer or add BE delete if required
- FE: GET `/settings/system-info`
  - BE: No such route
  - Action: Remove/Defer or add BE route
- FE: PUT `/settings/system`
  - BE: No such route
  - Action: Remove/Defer or add BE route
- FE: GET `/settings/backup-status`
  - BE: No such route
  - Action: Remove/Defer or add BE route
- FE: GET `/settings/user-preferences`
  - BE: GET `/settings/preferences/me`
  - Action: Frontend change — call `/settings/preferences/me`
- FE: PUT `/settings/bulk-update`
  - BE: POST `/settings/bulk-update`
  - Action: Frontend change — switch to POST
- FE: POST `/settings/initialize` (OK)
- FE: POST `/settings/{settingKey}/reset`
  - BE: POST `/settings/reset/{setting_key}`
  - Action: Frontend change — adjust path to `/settings/reset/{key}`
- FE: GET `/settings/export`
  - BE: GET `/settings/export/json`
  - Action: Frontend change — call `/settings/export/json`
- FE: POST `/settings/import`
  - BE: POST `/settings/import/json`
  - Action: Frontend change — call `/settings/import/json`

3) Users
- FE: POST `/users/{id}/reset-password`
  - BE: No admin reset endpoint; only `/auth/change-password` and `/profile/me/change-password`
  - Action: Remove/Defer or add BE admin reset endpoint

4) Documents
- FE: Templates uses `/documents/templates` (no trailing slash)
  - BE: `/documents/templates/` and `/documents/templates/{id}` (trailing slash)
  - Action: Frontend change — prefer exact BE paths (or verify redirect behavior)

5) Notifications
- FE: GET `/notifications` with `read` param
  - BE: `is_read` param
  - Action: Frontend change — rename param to `is_read`
- FE: POST `/notifications/{id}/read`
  - BE: PUT `/notifications/{id}/read`
  - Action: Frontend change — use PUT
- FE: POST `/notifications/read-all`
  - BE: PUT `/notifications/read-all`
  - Action: Frontend change — use PUT

6) HACCP
- FE: PUT `/haccp/products/{id}`, DELETE `/haccp/products/{id}`
  - BE: Missing
  - Action: Remove/Defer or add BE update/delete for Product
- FE: PUT `/haccp/process-flows/{flowId}`, DELETE `/haccp/process-flows/{flowId}`
  - BE: Missing
  - Action: Remove/Defer or add BE update/delete for ProcessFlow
- FE: PUT `/haccp/hazards/{hazardId}`, DELETE `/haccp/hazards/{hazardId}`
  - BE: Missing
  - Action: Remove/Defer or add BE update/delete for Hazard
- FE: PUT `/haccp/ccps/{ccpId}`, DELETE `/haccp/ccps/{ccpId}`
  - BE: Missing
  - Action: Remove/Defer or add BE update/delete for CCP

7) Suppliers
- FE: POST `/suppliers/bulk/status`
  - BE: POST `/suppliers/bulk/action`
  - Action: Frontend change — use `/suppliers/bulk/action`
- FE: POST `/suppliers/bulk/evaluation-schedule`
  - BE: Missing
  - Action: Remove/Defer or add BE endpoint
- FE: Material approvals
  - POST `/suppliers/materials/{id}/approve`, POST `/suppliers/materials/{id}/reject`
  - BE: Missing; only `/suppliers/materials/bulk/action`
  - Action: Remove/Defer or add BE endpoints
- FE: POST `/suppliers/materials/bulk/approve`, `/suppliers/materials/bulk/reject`
  - BE: `/suppliers/materials/bulk/action`
  - Action: Frontend change — consolidate to `/materials/bulk/action`
- FE: GET `/suppliers/{supplierId}/evaluations`
  - BE: No such route; use GET `/suppliers/evaluations` with `supplier_id`
  - Action: Frontend change — switch to filtered list
- FE: POST `/suppliers/deliveries/{id}/inspect`
  - BE: Missing; inspection is modeled via checklists endpoints
  - Action: Remove/Defer or add BE endpoint mapping to checklist workflow
- FE: Quality Alerts
  - GET `/suppliers/alerts` (filtered), POST `/suppliers/alerts/{id}/resolve`
  - BE: Only specific alert lists exist: `/alerts/expired-certificates`, `/alerts/overdue-evaluations`, `/alerts/noncompliant-deliveries`, `/alerts/delivery-summary`
  - Action: Remove/Defer or add BE generic alerts API
- FE: COA
  - POST `/suppliers/deliveries/{id}/coa`, GET `/suppliers/deliveries/{id}/coa/download`
  - BE: Missing
  - Action: Remove/Defer or add BE endpoints
- FE: Supplier Documents download/verify
  - GET `/suppliers/documents/{id}/download`, POST `/suppliers/documents/{id}/verify`
  - BE: Missing
  - Action: Remove/Defer or add BE endpoints
- FE: Analytics/Reports/Exports/Search/Stats
  - `/suppliers/analytics/*`, `/suppliers/reports/generate`, `/suppliers/*/export`, `/suppliers/*/search`, `/suppliers/*/stats`
  - BE: Missing
  - Action: Remove/Defer or add BE endpoints
- FE: GET `/suppliers/dashboard`
  - BE: GET `/suppliers/dashboard/stats`
  - Action: Frontend change — call `/dashboard/stats`

8) Traceability
- FE: GET `/traceability/batches/{id}`
  - BE: Missing (no GET by id)
  - Action: Remove/Defer or add BE GET by id
- FE: Barcode/QR
  - POST `/batches/{id}/barcode`, POST `/batches/{id}/qrcode`, POST `/batches/{id}/print`
  - BE: GET `/batches/{id}/barcode/print` only
  - Action: Frontend change — use GET print endpoint; remove barcode/qrcode posts unless added in BE
- FE: Trace chain
  - GET `/batches/{id}/trace`, `/backward-trace`, `/forward-trace`, `/full-trace`
  - BE: GET `/batches/{id}/trace/backward`, `/batches/{id}/trace/forward`; no `full-trace`
  - Action: Frontend change — use available endpoints; remove `full-trace`
- FE: Links
  - POST `/links`, DELETE `/links/{id}`
  - BE: Missing
  - Action: Remove/Defer or add BE endpoints
- FE: Recalls list/detail/delete
  - GET `/recalls` (list), GET `/recalls/{id}`, DELETE `/recalls/{id}`
  - BE: Create/Update only (POST `/recalls`, PUT `/recalls/{id}`)
  - Action: Remove/Defer or add BE list/detail/delete
- FE: Search
  - POST `/search/batches` and `/search/recalls`
  - BE: POST `/batches/search/enhanced` only; no `/search/recalls`
  - Action: Frontend change — call `/batches/search/enhanced`; remove recalls search unless added
- FE: Reports
  - GET `/reports`, GET `/reports/{id}`, PUT `/reports/{id}`, DELETE `/reports/{id}`, POST `/reports/{id}/export`
  - BE: POST `/reports` only
  - Action: Remove/Defer or add BE routes
- FE: GET `/traceability/dashboard`
  - BE: GET `/traceability/dashboard/enhanced`
  - Action: Frontend change — call `/dashboard/enhanced`
- FE: Bulk
  - PUT `/batches/bulk`, DELETE `/batches/bulk`
  - BE: Missing
  - Action: Remove/Defer or add BE bulk routes

9) RBAC
- Current FE RBAC calls match BE routes (OK)

---

### B) Backend routes not currently used by frontend

Auth
- POST `/auth/register`
- POST `/auth/change-password`

Profile
- GET `/profile/me`, PUT `/profile/me`
- POST `/profile/me/change-password`
- POST `/profile/me/upload-avatar`, DELETE `/profile/me/avatar`
- GET `/profile/me/preferences`, POST `/profile/me/preferences`, DELETE `/profile/me/preferences/{key}`
- GET `/profile/me/activity`, GET `/profile/me/security`

Dashboard (router not mounted)
- GET `/dashboard/stats`, `/dashboard/recent-activity`, `/dashboard/compliance-metrics`, `/dashboard/system-status`

PRP
- POST `/prp/checklists/{checklist_id}/complete`
- POST `/prp/checklists/{checklist_id}/upload-evidence`
- GET `/prp/checklists/overdue`
- GET `/prp/dashboard/enhanced`
- POST `/prp/reports`
- GET `/prp/non-conformances`
- GET `/prp/checklists/{checklist_id}/items`

Suppliers — Inspection Checklists and Alerts
- GET `/suppliers/deliveries/{delivery_id}/checklists/`
- GET `/suppliers/checklists/{checklist_id}`
- POST `/suppliers/deliveries/{delivery_id}/checklists/`
- PUT `/suppliers/checklists/{checklist_id}`
- DELETE `/suppliers/checklists/{checklist_id}`
- GET `/suppliers/checklists/{checklist_id}/items/`
- POST `/suppliers/checklists/{checklist_id}/items/`
- PUT `/suppliers/checklist-items/{item_id}`
- POST `/suppliers/checklists/{checklist_id}/complete`
- GET `/suppliers/alerts/expired-certificates`
- GET `/suppliers/alerts/overdue-evaluations`
- GET `/suppliers/alerts/noncompliant-deliveries`
- GET `/suppliers/alerts/delivery-summary`
- GET `/suppliers/dashboard/stats`

Traceability
- GET `/traceability/batches/{batch_id}/barcode/print`
- GET `/traceability/batches/{batch_id}/trace/backward`
- GET `/traceability/batches/{batch_id}/trace/forward`
- POST `/traceability/recalls/{recall_id}/report/with-corrective-action`
- POST `/traceability/recalls/{recall_id}/entries`
- POST `/traceability/recalls/{recall_id}/actions`
- PUT `/traceability/batches/{batch_id}/status`
- POST `/traceability/batches/search/enhanced`

Settings
- GET `/settings/categories`
- GET `/settings/{setting_key}`
- PUT `/settings/{setting_key}`
- POST `/settings/reset/{setting_key}`
- GET `/settings/preferences/me`
- POST `/settings/preferences`
- PUT `/settings/preferences/{preference_key}`
- DELETE `/settings/preferences/{preference_key}`
- GET `/settings/export/json`
- POST `/settings/import/json`

Notifications
- GET `/notifications/{notification_id}`
- PUT `/notifications/{notification_id}/read`
- PUT `/notifications/read-all`

Non-conformance
- All routes under `/nonconformance` (not currently used by FE)

---

### Phased plan to close gaps

Phase 1 — Quick alignment (low-risk FE changes)
- Mount `dashboard` router in BE `api.py`
- Adjust FE methods/paths/params to match BE:
  - Notifications: use `is_read`, PUT for read/read-all
  - Settings: POST `/bulk-update`, `/reset/{key}`, `/export/json`, `/import/json`, `/preferences/me`
  - Suppliers: use `/dashboard/stats`, `/bulk/action`, `/materials/bulk/action`, use filtered `/suppliers/evaluations`
  - Traceability: use `/dashboard/enhanced`, `/batches/{id}/trace/backward|forward`, `/batches/search/enhanced`, `/batches/{id}/barcode/print`
  - Documents: confirm templates path trailing slash
  - Users: remove FE `reset-password` call

Phase 2 — FE removals or BE adds (decide scope)
- Settings: decide on create/delete/system-info/system/backup-status; either remove from FE or add BE
- Suppliers: decide on COA, generic alerts, inspections shortcut, approvals flows, analytics/reports/exports/search/stats; remove or add BE
- Traceability: decide on links, recalls list/detail/delete, reports CRUD/export, batches GET by id, bulk ops; remove or add BE
- HACCP: decide on update/delete for products/flows/hazards/ccps; remove or add BE

Phase 3 — Implement selected BE endpoints
- Add the prioritized missing BE endpoints from Phase 2 (with schemas, permissions)
- Extend tests and update OpenAPI

Phase 4 — FE integration and UI updates
- Wire FE to new endpoints, adjust types, toasts, error handling
- Update any pages/components relying on removed endpoints

Phase 5 — Validation and cleanup
- E2E smoke across Documents, Suppliers, HACCP, PRP, Traceability, Settings
- Remove dead code and feature flags for deferred endpoints

---

### Concrete task list (initial)

- [ ] Backend: include `dashboard.router` in `backend/app/api/v1/api.py`
- [ ] FE: Notifications API — `is_read` param, PUT methods for read/read-all
- [ ] FE: Settings API — switch to BE-supported endpoints and paths
- [ ] FE: Suppliers API — swap to `/dashboard/stats`, `/bulk/action`, `/materials/bulk/action`, remove vendor-only endpoints (or ticket BE)
- [ ] FE: Traceability API — align to `/dashboard/enhanced`, trace paths, search path, barcode print
- [ ] FE: Users API — drop `reset-password` call
- [ ] FE: Documents templates route — verify/align trailing slash

Follow-ups (require product decision before implementing)
- [ ] Decide on implementing vs dropping: Settings create/delete/system/system-info/backup-status
- [ ] Suppliers: COA, generic alerts, approval endpoints, analytics/reports/search/export/stats
- [ ] Traceability: links, recalls list/detail/delete, reports CRUD/export, batch GET by id, bulk ops
- [ ] HACCP: update/delete endpoints for product/flow/hazard/ccp


