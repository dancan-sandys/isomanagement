from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_permission
from app.models.user import User
from app.models.rbac import Module, PermissionType, Role, Permission, UserPermission
from app.schemas.rbac import (
    RoleCreate, RoleUpdate, RoleClone, Role as RoleResponse,
    RoleListResponse, RoleDetailResponse, PermissionListResponse,
    RoleSummaryResponse, PermissionMatrixResponse, UserPermissionCreate, PermissionCreate
)
from app.schemas.common import ResponseModel, PaginatedResponse
from app.services.rbac_service import RBACService
from app.models.audit import AuditLog
from sqlalchemy import and_, desc
from app.core.security import require_permission

router = APIRouter()
# Audit Logs Admin Endpoints
@router.get("/audits", response_model=ResponseModel)
async def get_audit_logs(
    page: int = 1,
    size: int = 20,
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("audits:read")),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    total = query.count()
    logs = query.order_by(desc(AuditLog.created_at)).offset((page - 1) * size).limit(size).all()
    items = [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "created_at": log.created_at,
        }
        for log in logs
    ]
    return ResponseModel(success=True, message="Audit logs retrieved", data={"items": items, "total": total, "page": page, "size": size})



# Permission endpoints
@router.get("/permissions", response_model=PermissionListResponse)
async def get_permissions(
    module: Optional[Module] = Query(None, description="Filter by module"),
    action: Optional[PermissionType] = Query(None, description="Filter by action"),
    current_user: User = Depends(require_permission("roles:read")),
    db: Session = Depends(get_db)
):
    """Get all permissions with optional filtering"""
    rbac_service = RBACService(db)
    
    query = db.query(Permission)
    if module:
        query = query.filter(Permission.module == module)
    if action:
        query = query.filter(Permission.action == action)
    
    permissions = query.all()
    
    # Convert to Pydantic models manually
    from app.schemas.rbac import Permission as PermissionResponse
    permission_responses = []
    for perm in permissions:
        permission_responses.append(PermissionResponse(
            id=perm.id,
            module=perm.module.value,  # Convert enum to string
            action=perm.action.value,  # Convert enum to string
            description=perm.description,
            created_at=perm.created_at
        ))
    
    return PermissionListResponse(
        success=True,
        data=permission_responses,
        total=len(permission_responses)
    )


@router.post("/permissions", response_model=ResponseModel)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(require_permission("roles:write")),
    db: Session = Depends(get_db)
):
    """Create a new permission"""
    rbac_service = RBACService(db)
    
    # Check if permission already exists
    existing = db.query(Permission).filter(
        Permission.module == permission_data.module,
        Permission.action == permission_data.action
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already exists"
        )
    
    permission = Permission(
        module=permission_data.module,
        action=permission_data.action,
        description=permission_data.description
    )
    
    db.add(permission)
    db.commit()
    db.refresh(permission)
    
    return ResponseModel(
        success=True,
        message="Permission created successfully",
        data=permission
    )


# Role endpoints
@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    current_user: User = Depends(require_permission("roles:read")),
    db: Session = Depends(get_db)
):
    """
    Get all roles
    """
    roles = db.query(Role).filter(Role.is_active == True).all()
    return [RoleResponse.from_orm(role) for role in roles]


@router.get("/roles/summary", response_model=RoleSummaryResponse)
async def get_role_summary(
    current_user: User = Depends(require_permission("roles:read")),
    db: Session = Depends(get_db)
):
    """Get role summary with user counts"""
    rbac_service = RBACService(db)
    
    summary_data = rbac_service.get_role_summary()
    
    # Convert to proper RoleSummary objects
    from app.schemas.rbac import RoleSummary, PermissionSummary
    summary = []
    for item in summary_data:
        # Convert permission dictionaries to PermissionSummary models
        permission_responses = []
        for perm_data in item["permissions"]:
            permission_responses.append(PermissionSummary(
                id=perm_data["id"],  # Access dictionary key, not attribute
                module=perm_data["module"],  # Already a string from the service
                action=perm_data["action"],  # Already a string from the service
                description=perm_data["description"],
                created_at=perm_data["created_at"]
            ))
        summary.append(RoleSummary(
            role_id=item["role_id"],
            role_name=item["role_name"],
            user_count=item["user_count"],
            permissions=permission_responses
        ))
    
    return RoleSummaryResponse(
        success=True,
        data=summary
    )


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(require_permission("roles:read")),
    db: Session = Depends(get_db)
):
    """
    Get role by ID
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return RoleResponse.from_orm(role)


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_permission("roles:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new role
    """
    # Check if role name already exists
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists"
        )
    
    # Create role
    role = Role(
        name=role_data.name,
        description=role_data.description,
        is_default=role_data.is_default,
        is_editable=role_data.is_editable,
        is_active=role_data.is_active
    )
    
    # Add permissions
    if role_data.permissions:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_data.permissions)
        ).all()
        role.permissions = permissions
    
    db.add(role)
    db.commit()
    db.refresh(role)
    
    return RoleResponse.from_orm(role)


@router.put("/roles/{role_id}", response_model=RoleDetailResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(require_permission("roles:write")),
    db: Session = Depends(get_db)
):
    """Update an existing role"""
    rbac_service = RBACService(db)
    
    role = rbac_service.update_role(role_id, role_data, current_user.id)
    role.user_count = db.query(User).filter(User.role_id == role.id).count()
    
    return RoleDetailResponse(
        success=True,
        data=RoleResponse.from_orm(role)
    )


@router.post("/roles/{role_id}/clone", response_model=RoleDetailResponse)
async def clone_role(
    role_id: int,
    clone_data: RoleClone,
    current_user: User = Depends(require_permission("roles:write")),
    db: Session = Depends(get_db)
):
    """Clone an existing role"""
    rbac_service = RBACService(db)
    
    role = rbac_service.clone_role(role_id, clone_data, current_user.id)
    role.user_count = 0
    
    return RoleDetailResponse(
        success=True,
        data=RoleResponse.from_orm(role)
    )


@router.delete("/roles/{role_id}", response_model=ResponseModel)
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_permission("roles:write")),
    db: Session = Depends(get_db)
):
    """Delete a role"""
    rbac_service = RBACService(db)
    
    rbac_service.delete_role(role_id, current_user.id)
    
    return ResponseModel(
        success=True,
        message="Role deleted successfully"
    )


@router.get("/permissions/matrix", response_model=PermissionMatrixResponse)
async def get_permission_matrix(
    current_user: User = Depends(require_permission("roles:read")),
    db: Session = Depends(get_db)
):
    """Get permission matrix for all roles"""
    rbac_service = RBACService(db)
    
    matrix_data = rbac_service.get_permission_matrix()
    
    # Convert to proper PermissionMatrix object
    from app.schemas.rbac import PermissionMatrix
    matrix = PermissionMatrix(
        modules=[module.value for module in matrix_data["modules"]],
        permissions=[perm.value for perm in matrix_data["permissions"]],
        role_permissions=matrix_data["role_permissions"]
    )
    
    return PermissionMatrixResponse(
        success=True,
        data=matrix
    )


# User permission endpoints
@router.get("/users/{user_id}/permissions", response_model=ResponseModel)
async def get_user_permissions(
    user_id: int,
    current_user: User = Depends(require_permission("users:read")),
    db: Session = Depends(get_db)
):
    """Get all permissions for a specific user"""
    rbac_service = RBACService(db)
    
    permissions = rbac_service.get_user_permissions(user_id)
    # Convert SQLAlchemy Permission models to Pydantic responses to avoid serialization errors
    from app.schemas.rbac import Permission as PermissionResponse
    permission_responses = []
    for perm in permissions:
        permission_responses.append(PermissionResponse(
            id=perm.id,
            module=perm.module,
            action=perm.action,
            description=perm.description,
            created_at=perm.created_at,
        ))
    
    return ResponseModel(
        success=True,
        data=permission_responses
    )


@router.post("/users/{user_id}/permissions", response_model=ResponseModel)
async def assign_user_permission(
    user_id: int,
    permission_data: UserPermissionCreate,
    current_user: User = Depends(require_permission("users:write")),
    db: Session = Depends(get_db)
):
    """Assign custom permission to user"""
    rbac_service = RBACService(db)
    
    user_perm = rbac_service.assign_user_permission(
        user_id, 
        permission_data.permission_id, 
        permission_data.granted, 
        current_user.id
    )
    
    return ResponseModel(
        success=True,
        message="Permission assigned successfully",
        data=user_perm
    )


@router.delete("/users/{user_id}/permissions/{permission_id}", response_model=ResponseModel)
async def remove_user_permission(
    user_id: int,
    permission_id: int,
    current_user: User = Depends(require_permission("users:write")),
    db: Session = Depends(get_db)
):
    """Remove custom permission from user"""
    rbac_service = RBACService(db)
    
    success = rbac_service.remove_user_permission(user_id, permission_id)
    
    if success:
        return ResponseModel(
            success=True,
            message="Permission removed successfully"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User permission not found"
        )


# Permission check endpoint
@router.post("/check-permission", response_model=ResponseModel)
async def check_permission(
    module: Module,
    action: PermissionType,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if current user has specific permission"""
    rbac_service = RBACService(db)
    
    has_perm = rbac_service.has_permission(current_user.id, module, action)
    
    return ResponseModel(
        success=True,
        data={"has_permission": has_perm}
    ) 