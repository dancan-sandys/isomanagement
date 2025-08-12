from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class AuditBase(BaseModel):
  title: str
  audit_type: str = Field(pattern="^(internal|external|supplier)$")
  scope: Optional[str] = None
  objectives: Optional[str] = None
  criteria: Optional[str] = None
  start_date: Optional[datetime] = None
  end_date: Optional[datetime] = None
  status: Optional[str] = Field(default="planned", pattern="^(planned|in_progress|completed|closed)$")
  auditor_id: Optional[int] = None
  lead_auditor_id: Optional[int] = None
  auditee_department: Optional[str] = None


class AuditCreate(AuditBase):
  pass


class AuditUpdate(AuditBase):
  pass


class AuditResponse(AuditBase):
  id: int
  created_by: int
  created_at: datetime
  updated_at: datetime

  class Config:
    from_attributes = True


class ChecklistTemplateBase(BaseModel):
  name: str
  clause_ref: Optional[str] = None
  question: str
  requirement: Optional[str] = None
  category: Optional[str] = None
  is_active: Optional[bool] = True


class ChecklistTemplateCreate(ChecklistTemplateBase):
  pass


class ChecklistTemplateResponse(ChecklistTemplateBase):
  id: int
  created_by: int
  created_at: datetime

  class Config:
    from_attributes = True


class ChecklistItemBase(BaseModel):
  audit_id: int
  template_id: Optional[int] = None
  clause_ref: Optional[str] = None
  question: Optional[str] = None
  response: Optional[str] = Field(default=None, pattern="^(conforming|nonconforming|not_applicable)$")
  evidence_text: Optional[str] = None
  score: Optional[float] = None
  comment: Optional[str] = None
  responsible_person_id: Optional[int] = None
  due_date: Optional[datetime] = None


class ChecklistItemCreate(ChecklistItemBase):
  pass


class ChecklistItemUpdate(ChecklistItemBase):
  pass


class ChecklistItemResponse(ChecklistItemBase):
  id: int
  evidence_file_path: Optional[str] = None
  created_at: datetime

  class Config:
    from_attributes = True


class AuditItemAttachmentResponse(BaseModel):
  id: int
  item_id: int
  file_path: str
  filename: str
  uploaded_by: int
  uploaded_at: datetime

  class Config:
    from_attributes = True


class AuditFindingAttachmentResponse(BaseModel):
  id: int
  finding_id: int
  file_path: str
  filename: str
  uploaded_by: int
  uploaded_at: datetime

  class Config:
    from_attributes = True


class AuditAttachmentResponse(BaseModel):
  id: int
  audit_id: int
  file_path: str
  filename: str
  uploaded_by: int
  uploaded_at: datetime

  class Config:
    from_attributes = True


class FindingBase(BaseModel):
  audit_id: int
  clause_ref: Optional[str] = None
  description: str
  severity: str = Field(pattern="^(minor|major|critical)$")
  corrective_action: Optional[str] = None
  responsible_person_id: Optional[int] = None
  target_completion_date: Optional[datetime] = None
  status: Optional[str] = Field(default="open", pattern="^(open|in_progress|verified|closed)$")
  related_nc_id: Optional[int] = None


class FindingCreate(FindingBase):
  pass


class FindingUpdate(FindingBase):
  pass


class FindingResponse(FindingBase):
  id: int
  created_at: datetime

  class Config:
    from_attributes = True


class AuditListResponse(BaseModel):
  items: List[AuditResponse]
  total: int
  page: int
  size: int
  pages: int


class AuditStatsResponse(BaseModel):
  total: int
  by_status: Dict[str, int]
  by_type: Dict[str, int]
  recent_created: List[Dict[str, str]]


class AuditeeResponse(BaseModel):
  id: int
  audit_id: int
  user_id: int
  role: Optional[str] = None
  added_at: datetime

  class Config:
    from_attributes = True


