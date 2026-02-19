from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import SessionLocal
from app.models.audit_mgmt import Audit, AuditStatus, AuditFinding, FindingStatus


def backfill() -> None:
	"""Backfill Audit.actual_end_at and AuditFinding.closed_at for existing rows.
	- actual_end_at: set to updated_at if status in (completed, closed) and actual_end_at is null
	- closed_at: set to target_completion_date if status in (verified, closed) and closed_at is null
	This is heuristic; real values should be set by workflow going forward.
	"""
	db: Session = SessionLocal()
	updated_audits = 0
	updated_findings = 0
	try:
		# Backfill audits.actual_end_at
		q_a = db.query(Audit).filter(
			and_(Audit.status.in_([AuditStatus.COMPLETED, AuditStatus.CLOSED]), Audit.actual_end_at.is_(None))
		)
		for a in q_a.all():
			candidate = a.updated_at or a.end_date or a.start_date
			if candidate:
				a.actual_end_at = candidate
				updated_audits += 1

		# Backfill findings.closed_at
		q_f = db.query(AuditFinding).filter(
			and_(AuditFinding.status.in_([FindingStatus.VERIFIED, FindingStatus.CLOSED]), AuditFinding.closed_at.is_(None))
		)
		for f in q_f.all():
			candidate = f.target_completion_date or f.created_at
			if candidate:
				f.closed_at = candidate
				updated_findings += 1

		db.commit()
	finally:
		db.close()
	print({
		"updated_audits": updated_audits,
		"updated_findings": updated_findings,
	})


if __name__ == "__main__":
	backfill()
