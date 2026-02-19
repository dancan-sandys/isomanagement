from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class DepartmentBase(BaseModel):
    department_code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    parent_department_id: Optional[int] = Field(None, description="Parent department ID for hierarchy")
    manager_id: Optional[int] = Field(None, description="User ID of the department manager")
    status: Optional[str] = Field("active", description="active, inactive, archived")
    color_code: Optional[str] = Field(None, description="Hex color for UI display, e.g., #1E88E5")
    raci_json: Optional[dict] = Field(None, description="RACI governance metadata")
    governance_notes: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    created_by: int


class DepartmentUpdate(BaseModel):
    department_code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    parent_department_id: Optional[int] = None
    manager_id: Optional[int] = None
    status: Optional[str] = None
    color_code: Optional[str] = None
    raci_json: Optional[dict] = None
    governance_notes: Optional[str] = None


class Department(DepartmentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    model_config = {"from_attributes": True}


class DepartmentTreeNode(Department):
    children: List['DepartmentTreeNode'] = []


class DepartmentListResponse(BaseModel):
    items: List[Department]
    total: int
    page: int
    size: int
    pages: int


class DepartmentUserAssignment(BaseModel):
    user_id: int
    role: Optional[str] = Field(None, description="member, supervisor, manager, etc.")
    assigned_from: Optional[datetime] = None
    assigned_until: Optional[datetime] = None
    is_active: Optional[bool] = True


class DepartmentUsersResponse(BaseModel):
    department_id: int
    users: List[dict]

