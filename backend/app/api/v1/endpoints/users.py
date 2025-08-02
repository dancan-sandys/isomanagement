from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.security import get_current_active_user, require_permission, get_password_hash
from app.models.user import User, UserRole, UserStatus
from app.schemas.auth import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.schemas.common import ResponseModel, PaginationParams, PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[UserListResponse])
async def get_users(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, description="Search by username, email, or full name"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    department: Optional[str] = Query(None, description="Filter by department"),
    current_user: User = Depends(require_permission("users:read")),
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
    if role:
        query = query.filter(User.role == role)
    
    # Apply status filter
    if status:
        query = query.filter(User.status == status)
    
    # Apply department filter
    if department:
        query = query.filter(User.department == department)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.size
    users = query.offset(offset).limit(pagination.size).all()
    
    # Calculate pagination info
    pages = (total + pagination.size - 1) // pagination.size
    has_next = pagination.page < pages
    has_prev = pagination.page > 1
    
    return PaginatedResponse(
        items=[UserListResponse.from_orm(user) for user in users],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
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
    
    return UserResponse.from_orm(user)


@router.post("/", response_model=UserResponse)
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
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role or UserRole.VIEWER,
        department=user_data.department,
        position=user_data.position,
        phone=user_data.phone,
        employee_id=user_data.employee_id,
        created_by=current_user.id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.from_orm(db_user)


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
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_by = current_user.id
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)


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


@router.get("/dashboard", response_model=ResponseModel)
async def get_users_dashboard(
    current_user: User = Depends(require_permission("users:read")),
    db: Session = Depends(get_db)
):
    """
    Get user management dashboard data
    """
    try:
        # Get total users count
        total_users = db.query(User).count()
        
        # Get active users count
        active_users = db.query(User).filter(User.is_active == True).count()
        
        # Get inactive users count
        inactive_users = db.query(User).filter(User.is_active == False).count()
        
        # Get pending approval count
        pending_approval = db.query(User).filter(User.status == UserStatus.PENDING_APPROVAL).count()
        
        # Get users by role
        users_by_role = {}
        for role in UserRole:
            count = db.query(User).filter(User.role == role).count()
            if count > 0:
                users_by_role[role.value] = count
        
        # Get users by department
        users_by_department = {}
        departments = db.query(User.department).distinct().filter(User.department.isnot(None)).all()
        for dept in departments:
            if dept[0]:
                count = db.query(User).filter(User.department == dept[0]).count()
                users_by_department[dept[0]] = count
        
        # Get recent logins (users who logged in today)
        from datetime import datetime, timedelta
        today = datetime.now().date()
        recent_logins = db.query(User).filter(
            User.last_login >= today
        ).count()
        
        # Mock data for training and competency (these would come from separate tables)
        training_overdue = 3  # Mock value
        competencies_expiring = 5  # Mock value
        
        dashboard_data = {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "pending_approval": pending_approval,
            "users_by_role": users_by_role,
            "users_by_department": users_by_department,
            "recent_logins": recent_logins,
            "training_overdue": training_overdue,
            "competencies_expiring": competencies_expiring
        }
        
        return ResponseModel(
            success=True,
            message="Dashboard data retrieved successfully",
            data=dashboard_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard data: {str(e)}"
        ) 