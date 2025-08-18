from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.rbac import Module, PermissionType


# Permission types and modules are now imported from models


# Permission schemas
class PermissionBase(BaseModel):
    module: Module
    action: PermissionType
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class Permission(PermissionBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# Role schemas
class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_default: bool = False
    is_editable: bool = True
    is_active: bool = True

    model_config = {"from_attributes": True}


class RoleCreate(RoleBase):
    permissions: List[int] = []  # List of permission IDs

    model_config = {"from_attributes": True}


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permissions: Optional[List[int]] = None

    model_config = {"from_attributes": True}


class Role(RoleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    permissions: List[Permission] = []
    user_count: Optional[int] = 0

    model_config = {"from_attributes": True}


# User Permission schemas
class UserPermissionBase(BaseModel):
    permission_id: int
    granted: bool = True


class UserPermissionCreate(UserPermissionBase):
    pass


class UserPermission(UserPermissionBase):
    id: int
    user_id: int
    granted_by: Optional[int] = None
    granted_at: datetime
    permission: Permission

    model_config = {
        "from_attributes": True
    }


# Role Management schemas
class RoleClone(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    permissions: List[int] = []


class RoleSummary(BaseModel):
    role_id: int
    role_name: str
    user_count: int
    permissions: List[Permission]


class PermissionMatrix(BaseModel):
    modules: List[Module]
    permissions: List[PermissionType]
    role_permissions: Dict[str, Dict[str, List[str]]]  # role_name -> module -> actions


# Response schemas
class RoleListResponse(BaseModel):
    success: bool
    data: List[Role]
    total: int
    page: int
    size: int


class RoleDetailResponse(BaseModel):
    success: bool
    data: Role


class PermissionListResponse(BaseModel):
    success: bool
    data: List[Permission]
    total: int


class RoleSummaryResponse(BaseModel):
    success: bool
    data: List[RoleSummary]


class PermissionMatrixResponse(BaseModel):
    success: bool
    data: PermissionMatrix 