from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum

from app.models.user import UserStatus


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role_id: Optional[int] = None


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserSignup(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    employee_id: Optional[str] = Field(None, max_length=50)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    role_id: int = Field(..., description="ID of the role to assign")
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    employee_id: Optional[str] = Field(None, max_length=50)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role_id: Optional[int] = None
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    employee_id: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role_id: int # Changed from role: UserRole
    role_name: Optional[str] = None  # Include role name for frontend
    status: UserStatus
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None # Made optional
    updated_at: Optional[datetime] = None # Made optional

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int

    model_config = {"from_attributes": True}


class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)

    model_config = {"from_attributes": True}


class PasswordResetRequest(BaseModel):
    email: EmailStr

    model_config = {"from_attributes": True}


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

    model_config = {"from_attributes": True}


class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role_id: int
    role_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserSessionInfo(BaseModel):
    user_id: int
    username: str
    role_id: int
    is_active: bool
    session_id: str
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True} 