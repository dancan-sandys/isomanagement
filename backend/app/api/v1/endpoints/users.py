from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.security import get_current_active_user, require_permission, get_password_hash, validate_password_policy, get_current_user
from app.models.user import User, UserStatus
from app.models.rbac import Role
from app.schemas.auth import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.schemas.common import ResponseModel, PaginationParams, PaginatedResponse
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("/dashboard", response_model=ResponseModel)
async def get_users_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user management dashboard data
    """
    try:
        # Get total users count
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        inactive_users = db.query(User).filter(User.is_active == False).count()
        pending_approval = db.query(User).filter(User.status == UserStatus.PENDING_APPROVAL).count()

        # Users by role
        users_by_role = {}
        roles = db.query(Role).all()
        for role in roles:
            count = db.query(User).filter(User.role_id == role.id).count()
            if count > 0:
                users_by_role[role.name] = count

        # Users by department
        users_by_department = {}
        try:
            # Use department_name field instead of department relationship
            departments = db.query(User.department_name).distinct().filter(User.department_name != None).all()
            for dept in departments:
                if dept[0]:
                    count = db.query(User).filter(User.department_name == dept[0]).count()
                    users_by_department[dept[0]] = count
        except Exception as dept_error:
            print(f"Error getting users by department: {dept_error}")
            users_by_department = {}

        # Recent logins (today)
        recent_logins = 0
        try:
            from datetime import datetime
            today = datetime.now().date()
            recent_logins = db.query(User).filter(User.last_login >= today).count()
        except Exception as login_error:
            print(f"Error getting recent logins: {login_error}")

        # Placeholder training metrics
        training_overdue = 3
        competencies_expiring = 5

        dashboard_data = {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "pending_approval": pending_approval,
            "users_by_role": users_by_role,
            "users_by_department": users_by_department,
            "recent_logins": recent_logins,
            "training_overdue": training_overdue,
            "competencies_expiring": competencies_expiring,
        }

        return ResponseModel(success=True, message="Dashboard data retrieved successfully", data=dashboard_data)
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve dashboard data: {str(e)}")


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def get_users(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, description="Search by username, email, or full name"),
    role_id: Optional[int] = Query(None, description="Filter by role ID"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    department: Optional[str] = Query(None, description="Filter by department name (legacy)"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of users with optional filtering
    """
    query = db.query(User)
    
    # Apply search filter
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Apply role filter
    if role_id:
        query = query.filter(User.role_id == role_id)
    
    # Apply status filter
    if status:
        query = query.filter(User.status == status)
    
    # Apply department filters
    if department_id:
        query = query.filter(User.department_id == department_id)
    elif department:
        query = query.filter(User.department_name == department)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.size
    users = query.offset(offset).limit(pagination.size).all()
    
    # Calculate pagination info
    pages = (total + pagination.size - 1) // pagination.size
    has_next = pagination.page < pages
    has_prev = pagination.page > 1
    
    # Convert users to UserResponse objects
    user_responses = []
    for user in users:
        # Get role name
        role = db.query(Role).filter(Role.id == user.role_id).first()
        role_name = role.name if role else None
        
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
        user_responses.append(user_response)
    
    return PaginatedResponse(
        items=user_responses,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_permission("users:read")),
    db: Session = Depends(get_db)
):
    """
    Get user by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Build response explicitly to ensure department_name is returned
    role = db.query(Role).filter(Role.id == user.role_id).first()
    role_name = role.name if role else None
    return UserResponse(
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


@router.post("/", response_model=ResponseModel[UserResponse])
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_permission("users:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new user
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
    
    # Verify role exists
    role = db.query(Role).filter(Role.id == user_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role ID"
        )
    
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
        employee_id=user_data.employee_id,
        created_by=current_user.id
    )
    # If department_id provided, set FK and sync name if resolvable
    if getattr(user_data, 'department_id', None):
        try:
            from app.models.departments import Department as DepartmentModel
            dep = db.query(DepartmentModel).filter(DepartmentModel.id == user_data.department_id).first()
            if dep:
                db_user.department_id = dep.id
                db_user.department_name = dep.name
        except Exception:
            pass
    
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
        # Log error but don't fail the user creation
        print(f"Failed to send welcome email: {str(e)}")
    
    # Get role name for response
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
    
    return ResponseModel(
        success=True,
        message="User created successfully",
        data=user_response
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_permission("users:write")),
    db: Session = Depends(get_db)
):
    """
    Update user information
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields if provided
    update_data = user_data.dict(exclude_unset=True)
    # Map legacy 'department' to canonical 'department_name'
    if "department" in update_data:
        user.department_name = update_data.pop("department")
    # If department_id provided, set FK and sync name
    if "department_id" in update_data and update_data["department_id"] is not None:
        try:
            from app.models.departments import Department as DepartmentModel
            dep = db.query(DepartmentModel).filter(DepartmentModel.id == update_data["department_id"]).first()
            if dep:
                user.department_id = dep.id
                user.department_name = dep.name
        except Exception:
            pass
        update_data.pop("department_id", None)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_by = current_user.id
    db.commit()
    db.refresh(user)
    
    # Build response explicitly to ensure department_name is returned
    role = db.query(Role).filter(Role.id == user.role_id).first()
    role_name = role.name if role else None
    return UserResponse(
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


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("users:delete")),
    db: Session = Depends(get_db)
):
    """
    Delete user (soft delete by setting is_active to False)
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete
    user.is_active = False
    user.updated_by = current_user.id
    db.commit()
    
    return ResponseModel(
        success=True,
        message="User deleted successfully"
    )


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(require_permission("users:write")),
    db: Session = Depends(get_db)
):
    """
    Activate a user account
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    user.status = UserStatus.ACTIVE
    user.updated_by = current_user.id
    db.commit()
    
    return ResponseModel(
        success=True,
        message="User activated successfully"
    )


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_permission("users:write")),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user account
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    user.updated_by = current_user.id
    db.commit()
    
    return ResponseModel(
        success=True,
        message="User deactivated successfully"
    )


@router.post("/{user_id}/reset-password", response_model=ResponseModel)
async def admin_reset_password(
    user_id: int,
    payload: dict,
    current_user: User = Depends(require_permission("users:write")),
    db: Session = Depends(get_db)
):
    """Reset a user's password (admin only)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot reset your own password via admin endpoint")

    new_password = payload.get("new_password")
    if not new_password or not validate_password_policy(new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="new_password does not meet security requirements")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.hashed_password = get_password_hash(new_password)
    user.updated_by = current_user.id
    db.commit()

    return ResponseModel(success=True, message="Password reset successfully")

 