from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Audit Program Schemas
class AuditProgramBase(BaseModel):
    name: str
    description: Optional[str] = None
    objectives: str
    scope: str
    year: int = Field(..., ge=2020, le=2030)
    period: Optional[str] = Field(None, pattern="^(Q1|Q2|Q3|Q4|Annual|H1|H2)$")
    manager_id: int
    risk_method: str = Field(default="qualitative", pattern="^(qualitative|quantitative|hybrid)$")
    resources: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    kpis: Optional[Dict[str, Any]] = None
    status: str = Field(default="draft", pattern="^(draft|active|completed|archived)$")


class AuditProgramCreate(AuditProgramBase):
    pass


class AuditProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    objectives: Optional[str] = None
    scope: Optional[str] = None
    year: Optional[int] = Field(None, ge=2020, le=2030)
    period: Optional[str] = Field(None, pattern="^(Q1|Q2|Q3|Q4|Annual|H1|H2)$")
    manager_id: Optional[int] = None
    risk_method: Optional[str] = Field(None, pattern="^(qualitative|quantitative|hybrid)$")
    resources: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    kpis: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(draft|active|completed|archived)$")


class AuditProgramResponse(AuditProgramBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditProgramListResponse(BaseModel):
    items: List[AuditProgramResponse]
    total: int
    page: int
    size: int
    pages: int


class AuditProgramKpisResponse(BaseModel):
    program_id: int
    program_name: str
    total_audits: int = 0
    completed_audits: int = 0
    overdue_audits: int = 0
    on_time_rate: Optional[float] = None
    total_findings: int = 0
    open_findings: int = 0
    critical_findings: int = 0
    average_closure_days: Optional[float] = None
    risk_coverage_percentage: Optional[float] = None
    resource_utilization: Optional[float] = None


# Audit Schemas
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
  program_id: Optional[int] = None


class AuditCreate(AuditBase):
  pass


class AuditUpdate(AuditBase):
  pass


class AuditResponse(AuditBase):
  id: int
  created_by: int
  created_at: datetime
  updated_at: datetime
  actual_end_at: datetime | None = None

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
  audit_id: int
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
  clause_ref: Optional[str] = None
  description: str
  severity: str = Field(pattern="^(minor|major|critical)$")
  corrective_action: Optional[str] = None
  responsible_person_id: Optional[int] = None
  target_completion_date: Optional[datetime] = None
  status: Optional[str] = Field(default="open", pattern="^(open|in_progress|verified|closed)$")
  related_nc_id: Optional[int] = None
  finding_type: Optional[str] = Field(default="nonconformity", pattern="^(nonconformity|observation|ofi)$")
  closed_at: Optional[datetime] = None


class FindingCreate(FindingBase):
  pass


class FindingUpdate(FindingBase):
  pass


class FindingResponse(FindingBase):
  audit_id: int
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


class AuditKpisResponse(BaseModel):
  lead_time_days_avg: Optional[float] = None
  on_time_audit_rate: Optional[float] = None
  finding_closure_days_avg: Optional[float] = None
  total_audits: int = 0
  completed_audits: int = 0
  overdue_audits: int = 0
  total_findings: int = 0
  open_findings: int = 0
  overdue_findings: int = 0
  critical_findings: int = 0
  period: str = "month"
  department: Optional[str] = None
  auditor_id: Optional[int] = None


class AuditPlanBase(BaseModel):
  agenda: Optional[str] = None
  criteria_refs: Optional[str] = None
  sampling_plan: Optional[str] = None
  documents_to_review: Optional[str] = None
  logistics: Optional[str] = None


class AuditPlanCreate(AuditPlanBase):
  pass


class AuditPlanResponse(AuditPlanBase):
  id: int
  audit_id: int
  approved_by: Optional[int] = None
  approved_at: Optional[datetime] = None
  created_at: datetime

  class Config:
    from_attributes = True


class AuditeeResponse(BaseModel):
  id: int
  audit_id: int
  user_id: int
  role: Optional[str] = None
  added_at: datetime

  class Config:
    from_attributes = True


