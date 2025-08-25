from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.change import ChangeRequest, ChangeApproval, ChangeStatus, ApprovalDecision


class ChangeService:
	def __init__(self, db: Session):
		self.db = db

	def create_change(self, initiator_id: int, data: Dict[str, Any], approvals: Optional[List[Dict[str, int]]] = None) -> ChangeRequest:
		cr = ChangeRequest(
			title=data["title"],
			reason=data["reason"],
			initiator_id=initiator_id,
			process_id=data.get("process_id"),
			document_id=data.get("document_id"),
			impact_areas=data.get("impact_areas"),
			risk_rating=data.get("risk_rating"),
			validation_plan=data.get("validation_plan"),
			training_plan=data.get("training_plan"),
			effective_date=data.get("effective_date"),
			status=ChangeStatus.ASSESSING,
		)
		self.db.add(cr)
		self.db.flush()
		# Insert approval steps
		for ap in sorted(approvals or [], key=lambda a: a.get("sequence", 0)):
			row = ChangeApproval(
				change_request_id=cr.id,
				approver_id=ap["approver_id"],
				sequence=ap["sequence"],
				decision=ApprovalDecision.PENDING,
			)
			self.db.add(row)
		self.db.commit(); self.db.refresh(cr)
		return cr

	def update_assessment(self, change_id: int, data: Dict[str, Any]) -> ChangeRequest:
		cr = self.db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
		if not cr:
			raise ValueError("Change request not found")
		cr.impact_areas = data.get("impact_areas", cr.impact_areas)
		cr.risk_rating = data.get("risk_rating", cr.risk_rating)
		cr.validation_plan = data.get("validation_plan", cr.validation_plan)
		cr.training_plan = data.get("training_plan", cr.training_plan)
		cr.effective_date = data.get("effective_date", cr.effective_date)
		self.db.commit(); self.db.refresh(cr)
		return cr

	def approve_step(self, change_id: int, approver_id: int, sequence: Optional[int], decision: ApprovalDecision, comments: Optional[str]) -> ChangeRequest:
		q = self.db.query(ChangeApproval).filter(ChangeApproval.change_request_id == change_id, ChangeApproval.decision == ApprovalDecision.PENDING)
		if sequence is not None:
			q = q.filter(ChangeApproval.sequence == sequence)
		step = q.order_by(ChangeApproval.sequence.asc()).first()
		if not step:
			raise ValueError("No pending approval step found")
		if step.approver_id != approver_id:
			raise PermissionError("Not assigned approver for this step")
		step.decision = decision
		step.comments = comments
		step.decided_at = datetime.utcnow()
		self.db.commit()
		# If all steps approved -> mark CR approved
		pending = self.db.query(ChangeApproval).filter(ChangeApproval.change_request_id == change_id, ChangeApproval.decision == ApprovalDecision.PENDING).count()
		cr = self.db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
		if decision == ApprovalDecision.REJECTED:
			cr.status = ChangeStatus.REJECTED
		elif pending == 0:
			cr.status = ChangeStatus.APPROVED
		self.db.commit(); self.db.refresh(cr)
		return cr

	def implement(self, change_id: int) -> ChangeRequest:
		cr = self.db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
		if not cr:
			raise ValueError("Change request not found")
		if cr.status != ChangeStatus.APPROVED:
			raise ValueError("Change must be approved before implementation")
		cr.status = ChangeStatus.IMPLEMENTED
		self.db.commit(); self.db.refresh(cr)
		return cr

	def verify_and_close(self, change_id: int) -> ChangeRequest:
		cr = self.db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
		if not cr:
			raise ValueError("Change request not found")
		if cr.status != ChangeStatus.IMPLEMENTED:
			raise ValueError("Change must be implemented before verification")
		cr.status = ChangeStatus.CLOSED
		self.db.commit(); self.db.refresh(cr)
		return cr