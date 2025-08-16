### Audits KPIs and Timeline (ISO 19011 aligned)

This document defines success metrics for the Audits module. Each KPI includes a definition, exact formula, data source, target, owner, and review cadence.

References:
- ISO 19011:2018 Guidelines for auditing management systems: https://www.iso.org/obp/ui/#iso:std:iso:19011:ed-3:v1:en
- ASQ ISO 19011 overview: https://asq.org/quality-resources/iso-19011?srsltid=AfmBOoocPokHUdEopakbz0QO_DcY-XxBShmy4EllwE4TpmiFnP0SxiTl

---

### KPI 1: Lead time to plan an audit
- **Definition**: Days from audit creation to plan approval. If plan approval not implemented yet, use audit creation → audit start.
- **Formula**: `lead_time_days = date(plan_approved_at) - date(audit_created_at)` (fallback: `date(start_date) - date(created_at)`).
- **Data source**:
  - `audits.created_at`
  - `audit_plans.approved_at` (to be added), fallback `audits.start_date`
- **Target**: ≤ 10 calendar days (initial), stretch ≤ 7 days.
- **Owner**: Audit Program Manager.
- **Review cadence**: Weekly (ops), Monthly (management review).

### KPI 2: On-time audit rate
- **Definition**: Percentage of completed audits finished on or before planned end date.
- **Formula**: `on_time_rate = (# audits with actual_end <= planned_end) / (total completed audits)`.
- **Data source**:
  - `audits.end_date` (planned)
  - `audits.actual_end_at` (to be added)
- **Target**: ≥ 90% (initial), stretch ≥ 95%.
- **Owner**: Audit Program Manager.
- **Review cadence**: Monthly.

### KPI 3: Finding closure days
- **Definition**: Days from finding creation to verified/closed status, tracked by severity and finding_type.
- **Formula**: `closure_days = date(finding_closed_at) - date(finding_created_at)`.
- **Data source**:
  - `audit_findings.created_at`
  - `audit_findings.closed_at` (to be added) and `status in {verified, closed}`
  - `finding_type` (to be added) and `severity`
- **Target**: Median ≤ 30 days for major/critical; ≤ 20 days for minor and OFIs.
- **Owner**: Process Owners; oversight by QA Manager.
- **Review cadence**: Weekly.

### KPI 4 (optional): Overdue actions rate
- **Definition**: Share of open findings past their target completion date.
- **Formula**: `overdue_rate = (# open findings with now() > target_completion_date) / (# open findings)`.
- **Data source**: `audit_findings.target_completion_date`, `audit_findings.status`.
- **Target**: ≤ 10%.
- **Owner**: QA Manager.
- **Review cadence**: Weekly.

### KPI 5 (optional): Audit coverage of high-risk areas
- **Definition**: Portion of high‑risk areas audited within required cycle.
- **Formula**: `coverage = (# high-risk areas audited within cycle) / (total high-risk areas)`.
- **Data source**: `audit_risks` (to be added), audit-to-area mapping, last_audit_date.
- **Target**: ≥ 95% per cycle.
- **Owner**: Audit Program Manager.
- **Review cadence**: Quarterly.

---

### Timeline and Review Plan
- Week 1:
  - Baseline KPI 1–3 from current data (using fallbacks where needed).
  - Add fields needed for exact formulas: `audit_plans.approved_at`, `audits.actual_end_at`, `audit_findings.closed_at`, `audit_findings.finding_type`.
- Week 2:
  - Implement dashboard widgets and API endpoints for KPIs; add filters by period/department.
  - Set alerts for KPI thresholds (e.g., overdue actions > 10%).
- Ongoing:
  - Weekly ops: review KPI 1 and 3; Monthly: KPI 2; Quarterly: KPI 5.

---

### Query Sketches (for backend implementation)
- Lead time (fallback):
  - `SELECT AVG(DATE(start_date) - DATE(created_at)) FROM audits WHERE start_date IS NOT NULL;`
- On-time rate:
  - `SELECT SUM(CASE WHEN actual_end_at <= end_date THEN 1 ELSE 0 END)::float / COUNT(*) FROM audits WHERE status IN ('completed','closed');`
- Finding closure days:
  - `SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY (closed_at - created_at)) FROM audit_findings WHERE status IN ('verified','closed');`
- Overdue actions rate:
  - `SELECT SUM(CASE WHEN NOW() > target_completion_date THEN 1 ELSE 0 END)::float / NULLIF(SUM(CASE WHEN status IN ('open','in_progress') THEN 1 ELSE 0 END),0) FROM audit_findings;`


