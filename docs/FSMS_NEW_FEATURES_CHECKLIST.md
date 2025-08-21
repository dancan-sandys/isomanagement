# FSMS New Features Implementation Checklist

## Overview
This checklist tracks the implementation of three major additions: Objectives, Production Sheet, and Unified Actions Log. Work proceeds in phases. Items will be checked off as they are completed.

## Phase 1 — Objectives: targets, progress tracking, and dashboard graphs

- [ ] Define backend models for objectives targets and progress
  - [ ] `ObjectiveTarget` with department/period/target/thresholds/weight
  - [ ] `ObjectiveProgress` with period/actual/evidence/attainment/status
  - [ ] Indexes on `(objective_id, period_start)` and `(department_id, period_start)`
- [x] Implemented models and indexes (ObjectiveTarget, ObjectiveProgress)
- [x] Create Pydantic schemas for objectives, targets, progress, KPIs
- [x] Implement service layer for objectives calculations and roll-ups
- [x] Implement API endpoints
  - [ ] CRUD for objectives
  - [ ] CRUD for targets and progress entries
  - [ ] KPIs and trends: attainment, projections, on-track/at-risk
- [x] Integrate objectives with dashboard endpoints (`/dashboard/stats` objectivesKPI)
- [ ] RBAC: permissions for manage/view objectives (corp/department scope)
- [x] Seed sample objectives, targets, and progress for demo (see `backend/seed_objectives_demo.py`)
- [ ] Backend tests: models, services, endpoints, calculations
- [ ] Frontend minimal UI
  - [ ] Objectives list/detail
  - [ ] Progress entry form
  - [ ] KPI cards and basic charts

## Phase 2 — Production Sheet (Fresh milk, Mala/Yoghurt, Cheese)

- [ ] Define production process models: `ProductionProcess`, `ProcessStep`, `ProcessLog`, `YieldRecord`, `ColdRoomTransfer`, `AgingRecord`
- [ ] Create process templates for Fresh milk HTST, Yoghurt/Mala, Cheese
- [ ] Implement validation rules (time–temperature, diversion, yields)
- [ ] API endpoints for process creation, logging, yield, transfers, analytics
- [ ] Dashboard integration for production KPIs and trends
- [ ] Frontend production wizards with live compliance indicators
- [ ] Permissions and verification workflow (Operator/QC/Supervisor)
- [ ] Tests: validation scenarios, diversion logic, analytics

## Phase 3 — Unified Actions Log from 4 sources

- [ ] Define `ActionLogEntry` with `source` enum and linking to source entities
- [ ] Implement Interested Parties analysis with actions to address needs
- [ ] Implement SWOT and PESTEL issue capture with required actions
- [ ] Auto-ingest actions from Risk & Opportunity assessments
- [ ] Optional: ingest Management Review outputs and CAPA linkage
- [ ] API: list/filter/update actions; de-duplication/merge logic
- [ ] Dashboard: open/overdue actions by source, effectiveness trends
- [ ] Frontend: Kanban/list, inline create from analyses, bulk updates
- [ ] Tests: ingestion, status sync, dashboards

## Cross-cutting

- [ ] Background roll-ups and schedules for projections and reminders
- [ ] WebSocket notifications for live updates
- [ ] Exports (CSV/Excel) using existing export framework
- [ ] Documentation and user guides per feature

