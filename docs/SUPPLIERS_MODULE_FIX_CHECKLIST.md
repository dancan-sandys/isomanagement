# Suppliers Module Fix Checklist

This checklist tracks the end-to-end fixes to stabilize and align the Suppliers module (backend + frontend) with consistent contracts, robust validation, and ISO-aligned behavior.

## 1) Routing and Response Consistency
- [ ] Remove duplicate route definitions in `app/api/v1/endpoints/suppliers.py` to avoid collisions
  - [ ] Remove second duplicate block of materials endpoints (`/materials`, `/materials/{id}`, bulk)
  - [ ] Remove duplicate analytics endpoints (`/analytics/performance`, `/analytics/risk-assessment`)
  - [ ] Remove duplicate alerts endpoint (`/alerts`)
  - [ ] Remove duplicate supplier stats endpoint (`/stats`)
  - [ ] Remove duplicate material stats endpoint (`/materials/stats`)
- [ ] Standardize all endpoints to return `ResponseModel<T>` envelopes
  - [ ] Wrap raw dict/Pydantic responses in `ResponseModel`
  - [ ] Ensure consistent success/message/data payloads

## 2) Materials Approvals and Bulk Actions
- [ ] Implement service methods in `SupplierService`
  - [ ] `approve_material(material_id, user_id) -> Material`
  - [ ] `reject_material(material_id, reason, user_id) -> Material`
  - [ ] `bulk_approve_materials(material_ids, user_id) -> int`
  - [ ] `bulk_reject_materials(material_ids, reason, user_id) -> int`
- [ ] Fix endpoint payload shapes to accept JSON bodies (matching FE)
  - [ ] `POST /suppliers/materials/{id}/approve` -> JSON body optional comments, return updated `Material`
  - [ ] `POST /suppliers/materials/{id}/reject` -> JSON body `{ reason }`, return updated `Material`
  - [ ] `POST /suppliers/materials/bulk/approve` -> JSON `{ material_ids, comments? }`
  - [ ] `POST /suppliers/materials/bulk/reject` -> JSON `{ material_ids, rejection_reason }`

## 3) Documents (Upload, List, Download, Verify)
- [ ] Fix upload to accept metadata via `Form(...)` and compute file size reliably
  - [ ] Use `os.path.getsize(file_path)` after save
  - [ ] Wrap response in `ResponseModel`
- [ ] Wrap `GET /suppliers/{supplier_id}/documents` in `ResponseModel<Paginated>` and support pagination params
- [ ] Implement missing endpoints to match FE
  - [ ] `GET /suppliers/documents/{document_id}/download`
  - [ ] `POST /suppliers/documents/{document_id}/verify` (set `is_verified`, `verified_by`, `verified_at`)

## 4) Deliveries
- [ ] Accept FE payloads and normalize values without 422s
  - [ ] Accept `status: 'under_review'` and normalize to `pending` on inspection
  - [ ] Support `quantity` alias for `quantity_received` in schemas (validation + serialization alias)
- [ ] Ensure delivery endpoints return `ResponseModel<T>` consistently

## 5) Materials Serialization (Schema/Model Mismatch)
- [ ] Normalize `Material` JSON/text fields to prevent 422/500
  - [ ] On create/update: serialize lists (`allergens`, `quality_parameters`) to JSON strings for DB Text columns
  - [ ] On read: parse JSON strings back to arrays for responses
  - [ ] (Optional) Migrate DB columns to JSON to eliminate conversions

## 6) Supplier Listings and Metrics
- [ ] Compute `materials_count` per supplier via aggregate instead of hardcoded 0
- [ ] Ensure dashboard stats match FE expectations and remain wrapped in `ResponseModel`

## 7) Alerts and Analytics
- [ ] Ensure `/suppliers/alerts` returns consistent paginated shape in `ResponseModel`
- [ ] Keep analytics endpoints returning envelopes matching FE typings

## 8) Search Endpoint (Optional or Adjust FE)
- [ ] Provide `/suppliers/search` (name/code/contact) OR align FE to use global `/search`

## 9) ISO Alignment Touchpoints (user-friendly, PRP/Traceability integration)
- [ ] COA enforcement for critical categories (raw milk, additives, cultures) is in place — extend/parametrize as needed
- [ ] Document verification status aligned to expiry and verification metadata
- [ ] Add concise validation messages to support audit/readiness (ISO 22000 context)

## 10) Regression and Tests
- [ ] Run backend tests and smoke endpoint testers after changes
- [ ] Verify FE flows: Suppliers list, Materials CRUD, Evaluations, Deliveries, Documents, Alerts, Analytics

---

### Change Log (to update as we progress)
- [ ] Service: implemented material approvals and bulk endpoints
- [ ] Endpoints: approvals payload shape fixed, responses normalized
- [ ] Documents: upload fixed, download/verify added, list wrapped
- [ ] Deliveries: inspection normalization, quantity alias support
- [ ] Duplicates: routes deduplicated (materials, analytics, alerts, stats)
- [ ] Materials serialization normalization
- [ ] Supplier metrics improved