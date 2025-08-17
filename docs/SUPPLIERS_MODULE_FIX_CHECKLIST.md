# Suppliers Module Fix Checklist

This checklist tracks the end-to-end fixes to stabilize and align the Suppliers module (backend + frontend) with consistent contracts, robust validation, and ISO-aligned behavior.

## 1) Routing and Response Consistency
- [x] Remove duplicate route definitions in `app/api/v1/endpoints/suppliers.py` to avoid collisions
  - [x] Remove second duplicate block of materials endpoints (`/materials`, `/materials/{id}`, bulk)
  - [x] Remove duplicate analytics endpoints (`/analytics/performance`, `/analytics/risk-assessment`)
  - [x] Remove duplicate alerts endpoint (`/alerts`)
  - [x] Remove duplicate supplier stats endpoint (`/stats`)
  - [x] Remove duplicate material stats endpoint (`/materials/stats`)
- [ ] Standardize all endpoints to return `ResponseModel<T>` envelopes
  - [x] Wrap alerts/analytics/stats in `ResponseModel`
  - [x] Wrap document endpoints and add pagination envelope
  - [ ] Wrap remaining delivery endpoints and COA upload

## 2) Materials Approvals and Bulk Actions
- [x] Implement service methods in `SupplierService`
  - [x] `approve_material(material_id, user_id) -> Material`
  - [x] `reject_material(material_id, reason, user_id) -> Material`
  - [x] `bulk_approve_materials(material_ids, user_id) -> int`
  - [x] `bulk_reject_materials(material_ids, reason, user_id) -> int`
- [x] Fix endpoint payload shapes to accept JSON bodies (matching FE)
  - [ ] `POST /suppliers/materials/{id}/approve` -> JSON body optional comments (currently accepted but ignored)
  - [x] `POST /suppliers/materials/{id}/reject` -> JSON body `{ reason }`, return updated `Material`
  - [x] `POST /suppliers/materials/bulk/approve` -> JSON `{ material_ids, comments? }`
  - [x] `POST /suppliers/materials/bulk/reject` -> JSON `{ material_ids, rejection_reason }`

## 3) Documents (Upload, List, Download, Verify)
- [x] Fix upload to accept metadata via `Form(...)` and compute file size reliably
  - [x] Use `os.path.getsize(file_path)` after save
  - [x] Wrap response in `ResponseModel`
- [x] Wrap `GET /suppliers/{supplier_id}/documents` in `ResponseModel<Paginated>` and support pagination params
- [x] Implement missing endpoints to match FE
  - [x] `GET /suppliers/documents/{document_id}/download`
  - [x] `POST /suppliers/documents/{document_id}/verify` (set `is_verified`, `verified_by`, `verified_at`)

## 4) Deliveries
- [x] Accept FE payloads and normalize values without 422s
  - [x] Accept `status: 'under_review'` and normalize to `pending` on inspection
  - [x] Support `quantity` alias for `quantity_received` in schemas (validation + serialization alias)
- [ ] Ensure delivery endpoints return `ResponseModel<T>` consistently

## 5) Materials Serialization (Schema/Model Mismatch)
- [ ] Normalize `Material` JSON/text fields to prevent 422/500
  - [ ] On create/update: serialize lists (`allergens`, `quality_parameters`) to JSON strings for DB Text columns
  - [x] On read: parse JSON strings back to arrays for responses
  - [ ] (Optional) Migrate DB columns to JSON to eliminate conversions

## 6) Supplier Listings and Metrics
- [ ] Compute `materials_count` per supplier via aggregate instead of hardcoded 0
- [ ] Ensure dashboard stats match FE expectations and remain wrapped in `ResponseModel`

## 7) Alerts and Analytics
- [x] Ensure `/suppliers/alerts` returns consistent paginated shape in `ResponseModel`
- [x] Keep analytics endpoints returning envelopes matching FE typings

## 8) Search Endpoint (Optional or Adjust FE)
- [ ] Provide `/suppliers/search` (name/code/contact) OR align FE to use global `/search`

## 9) ISO Alignment Touchpoints (user-friendly, PRP/Traceability integration)
- [x] COA enforcement for critical categories (raw milk, additives, cultures) is in place — extend/parametrize as needed
- [x] Document verification status aligned to expiry and verification metadata
- [ ] Add concise validation messages to support audit/readiness (ISO 22000 context)

## 10) Regression and Tests
- [ ] Run backend tests and smoke endpoint testers after changes
- [ ] Verify FE flows: Suppliers list, Materials CRUD, Evaluations, Deliveries, Documents, Alerts, Analytics

---

### Change Log (to update as we progress)
- [x] Service: implemented material approvals and bulk endpoints
- [x] Endpoints: approvals payload shape fixed, responses normalized
- [x] Documents: upload fixed, download/verify added, list wrapped
- [x] Deliveries: inspection normalization, quantity alias support
- [x] Duplicates: routes deduplicated (materials, analytics, alerts, stats)
- [x] Materials serialization normalization (read path)
- [ ] Supplier metrics improved (materials_count)