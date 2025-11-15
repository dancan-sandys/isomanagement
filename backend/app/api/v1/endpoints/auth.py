from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    authenticate_user, create_access_token, create_refresh_token,
    create_user_session, invalidate_user_session, get_current_user,
    get_password_hash, verify_token, verify_password, validate_password_policy
)
from app.models.user import User, UserSession, UserStatus
from app.models.rbac import Role
from app.schemas.auth import Token, TokenData, UserLogin, UserCreate, UserResponse, UserSignup
from app.schemas.common import ResponseModel
from app.services import log_audit_event
from app.services.notification_service import NotificationService
from app.core.config import settings
from datetime import timedelta as _timedelta
from app.services.haccp_access import get_user_haccp_assignments

router = APIRouter()


@router.post("/login", response_model=ResponseModel[dict])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Authenticate user and return access token
    """
    # Authenticate user (with lockout tracking)
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Increment failed attempts and lock if threshold exceeded
        if user:
            now = datetime.utcnow()
            # If already locked, return locked immediately
            if user.locked_until and user.locked_until > now:
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="User account is locked"
                )
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= settings.ACCOUNT_LOCKOUT_THRESHOLD:
                user.locked_until = now + _timedelta(minutes=settings.ACCOUNT_LOCKOUT_DURATION_MINUTES)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Check if user is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="User account is locked"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Create user session
    ip_address = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    create_user_session(db, user.id, access_token, refresh_token, ip_address, user_agent)
    # Audit: successful login
    try:
        log_audit_event(db, user.id, action="login_success", resource_type="auth", details={"username": user.username}, ip_address=ip_address, user_agent=user_agent)
    except Exception:
        pass
    
    # Update last login & reset failure window
    user.last_login = datetime.utcnow()
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    
    # Get role name for response
    role = db.query(Role).filter(Role.id == user.role_id).first()
    role_name = role.name if role else None
    
    assignments = get_user_haccp_assignments(db, user.id)
    assignment_roles = []
    if assignments["monitoring_ccp_ids"]:
        assignment_roles.append("monitoring")
    if assignments["verification_ccp_ids"]:
        assignment_roles.append("verification")

    # Create user response with role name
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role_id=user.role_id,
        role_name=role_name,
        status=user.status,
        department=user.department_name,
        position=user.position,
        phone=user.phone,
        employee_id=user.employee_id,
        is_active=user.is_active,
        is_verified=user.is_verified,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
        has_haccp_assignment=bool(assignments["product_ids"]),
        haccp_assigned_product_ids=list(assignments["product_ids"]) if assignments["product_ids"] else None,
        haccp_assignment_roles=assignment_roles or None,
    )
    
    response = ResponseModel(
        success=True,
        message="Login successful",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,  # 30 minutes
            "user": user_response
        }
    )
    return response


@router.post("/signup", response_model=ResponseModel[UserResponse])
async def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    """
    Sign up a new user (defaults to default role)
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if employee_id already exists (if provided)
    if user_data.employee_id:
        existing_employee = db.query(User).filter(User.employee_id == user_data.employee_id).first()
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already registered"
            )
    
    # Get default role (System Administrator or first available role)
    default_role = db.query(Role).filter(Role.is_default == True).first()
    if not default_role:
        # Fallback to first available role
        default_role = db.query(Role).first()
        if not default_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No roles found in the system"
            )
    
    # Enforce password policy
    if not validate_password_policy(user_data.password):
        raise HTTPException(status_code=400, detail="Password does not meet security requirements")
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role_id=default_role.id,  # Assign default role
        status=UserStatus.ACTIVE,  # Use enum instead of string
        department_name=user_data.department,  # Use department_name instead of department
        position=user_data.position,
        phone=user_data.phone,
        employee_id=user_data.employee_id,
        is_active=True,
        is_verified=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send welcome email notification
    try:
        notification_service = NotificationService(db)
        notification_service.send_welcome_notification(
            user_id=db_user.id,
            username=db_user.username,
            role_name=default_role.name,
            department=db_user.department_name or "Not specified",
            login_url="/login"
        )
    except Exception as e:
        # Log error but don't fail the registration
        print(f"Failed to send welcome email: {str(e)}")
    
    # Create user response with role name
    user_response = UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        role_id=db_user.role_id,
        role_name=default_role.name,
        status=db_user.status,
        department=db_user.department_name,  # Use department_name instead of department
        position=db_user.position,
        phone=db_user.phone,
        employee_id=db_user.employee_id,
        is_active=db_user.is_active,
        is_verified=db_user.is_verified,
        last_login=db_user.last_login,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )
    
    return ResponseModel(
        success=True,
        message="User registered successfully",
        data=user_response
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Logout user and invalidate session
    """
    # Get authorization header
    auth_header = request.headers.get("Authorization") if request else None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        invalidate_user_session(db, token)
    
    # Audit logout
    try:
        ip_address = request.client.host if request and request.client else None
        user_agent = request.headers.get("user-agent") if request else None
        log_audit_event(db, current_user.id, action="logout", resource_type="auth", details=None, ip_address=ip_address, user_agent=user_agent)
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Successfully logged out"
    )


from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=ResponseModel[Token])
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    refresh_token = request.refresh_token
    """
    Refresh access token using refresh token
    """
    # Verify refresh token
    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )
    
    # Check if session exists and is active
    session = db.query(UserSession).filter(
        UserSession.refresh_token == refresh_token,
        UserSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update session
    session.session_token = access_token
    session.refresh_token = new_refresh_token
    session.expires_at = datetime.utcnow() + access_token_expires
    db.commit()
    
    # Get role name for response
    role = db.query(Role).filter(Role.id == user.role_id).first()
    role_name = role.name if role else None
    
    # Create user response with role name
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role_id=user.role_id,
        role_name=role_name,
        status=user.status,
        department=user.department_name,
        position=user.position,
        phone=user.phone,
        employee_id=user.employee_id,
        is_active=user.is_active,
        is_verified=user.is_verified,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    # Audit token refresh
    try:
        log_audit_event(db, user.id, action="token_refresh", resource_type="auth", details=None)
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Token refreshed successfully",
        data={
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "user": user_response
        }
    )


@router.post("/register", response_model=ResponseModel[UserResponse])
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user with specific role
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verify role exists
    role = db.query(Role).filter(Role.id == user_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role ID"
        )
    
    # Enforce password policy
    if not validate_password_policy(user_data.password):
        raise HTTPException(status_code=400, detail="Password does not meet security requirements")
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role_id=user_data.role_id,
        department_name=user_data.department,
        position=user_data.position,
        phone=user_data.phone,
        employee_id=user_data.employee_id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send welcome email notification
    try:
        notification_service = NotificationService(db)
        notification_service.send_welcome_notification(
            user_id=db_user.id,
            username=db_user.username,
            role_name=role.name,
            department=db_user.department_name or "Not specified",
            login_url="/login"
        )
    except Exception as e:
        # Log error but don't fail the registration
        print(f"Failed to send welcome email: {str(e)}")
    
    # Create user response with role name
    user_response = UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        role_id=db_user.role_id,
        role_name=role.name,
        status=db_user.status,
        department=db_user.department_name,
        position=db_user.position,
        phone=db_user.phone,
        employee_id=db_user.employee_id,
        is_active=db_user.is_active,
        is_verified=db_user.is_verified,
        last_login=db_user.last_login,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )
    
    # Audit user registration
    try:
        log_audit_event(db, db_user.id, action="user_registered", resource_type="user", resource_id=str(db_user.id), details={"username": db_user.username})
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="User registered successfully",
        data=user_response
    )


@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user information
    """
    # Get role name
    role = db.query(Role).filter(Role.id == current_user.role_id).first()
    role_name = role.name if role else None
    
    assignments = get_user_haccp_assignments(db, current_user.id)
    assignment_roles = []
    if assignments["monitoring_ccp_ids"]:
        assignment_roles.append("monitoring")
    if assignments["verification_ccp_ids"]:
        assignment_roles.append("verification")

    # Create user response with role name
    user_response = UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role_id=current_user.role_id,
        role_name=role_name,
        status=current_user.status,
        department=current_user.department_name,
        position=current_user.position,
        phone=current_user.phone,
        employee_id=current_user.employee_id,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        has_haccp_assignment=bool(assignments["product_ids"]),
        haccp_assigned_product_ids=list(assignments["product_ids"]) if assignments["product_ids"] else None,
        haccp_assignment_roles=assignment_roles or None,
    )
    
    return ResponseModel(
        success=True,
        message="User information retrieved successfully",
        data=user_response
    )


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Enforce password policy
    if not validate_password_policy(new_password):
        raise HTTPException(status_code=400, detail="Password does not meet security requirements")
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    # Audit password change
    try:
        log_audit_event(db, current_user.id, action="password_changed", resource_type="user", resource_id=str(current_user.id))
    except Exception:
        pass
    return ResponseModel(
        success=True,
        message="Password changed successfully"
    ) 