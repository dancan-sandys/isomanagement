from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ChangeRequestCreate(BaseModel):
	title: str
	reason: str
	process_id: Optional[int] = None
	document_id: Optional[int] = None
	impact_areas: Optional[Dict[str, Any]] = None
	risk_rating: Optional[str] = None
	validation_plan: Optional[str] = None
	training_plan: Optional[str] = None
	effective_date: Optional[datetime] = None


class ChangeApprovalStep(BaseModel):
	approver_id: int
	sequence: int


class ChangeRequestResponse(BaseModel):
	id: int
	title: str
	reason: str
	status: str
	initiator_id: int
	process_id: Optional[int]
	document_id: Optional[int]
	impact_areas: Optional[Dict[str, Any]]
	risk_rating: Optional[str]
	validation_plan: Optional[str]
	training_plan: Optional[str]
	effective_date: Optional[datetime]
	created_at: datetime
	updated_at: Optional[datetime]
	approvals: List[Dict[str, Any]] = []
	events: Optional[List[Dict[str, Any]]] = None

	class Config:
		from_attributes = True


class ChangeAssessUpdate(BaseModel):
	impact_areas: Optional[Dict[str, Any]] = None
	risk_rating: Optional[str] = None
	validation_plan: Optional[str] = None
	training_plan: Optional[str] = None
	effective_date: Optional[datetime] = None


class ChangeDecisionRequest(BaseModel):
	decision: str
	comments: Optional[str] = None