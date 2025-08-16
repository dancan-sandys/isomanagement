from typing import List, Optional, Union
from functools import wraps
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.rbac import Module, PermissionType
from app.services.rbac_service import RBACService


def require_permission(permission_string: str):
    """
    Decorator to require specific permission
    Format: "module:action" (e.g., "documents:create", "users:read")
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract module and action from permission string
            try:
                module_str, action_str = permission_string.split(":")
                module = Module(module_str)
                action = PermissionType(action_str)
            except (ValueError, KeyError):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Invalid permission format: {permission_string}"
                )
            
            # Get current user and check permission
            request = kwargs.get('request') or args[0] if args else None
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )
            
            db = next(get_db())
            current_user = get_current_user(request, db)
            
            rbac_service = RBACService(db)
            if not rbac_service.has_permission(current_user.id, module, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission_string}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permissions: List[str]):
    """
    Decorator to require any of the specified permissions
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or args[0] if args else None
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )
            
            db = next(get_db())
            current_user = get_current_user(request, db)
            rbac_service = RBACService(db)
            
            has_any = False
            for permission_string in permissions:
                try:
                    module_str, action_str = permission_string.split(":")
                    module = Module(module_str)
                    action = PermissionType(action_str)
                    
                    if rbac_service.has_permission(current_user.id, module, action):
                        has_any = True
                        break
                except (ValueError, KeyError):
                    continue
            
            if not has_any:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required one of: {', '.join(permissions)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_module_access(module: Module):
    """
    Decorator to require access to a specific module
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or args[0] if args else None
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )
            
            db = next(get_db())
            current_user = get_current_user(request, db)
            rbac_service = RBACService(db)
            
            user_modules = rbac_service.get_user_modules(current_user.id)
            if module not in user_modules:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to module: {module.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# FastAPI dependency functions
def require_permission_dependency(permission_string: str):
    """
    FastAPI dependency to require specific permission
    """
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        try:
            module_str, action_str = permission_string.split(":")
            module = Module(module_str)
            action = PermissionType(action_str)
        except (ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid permission format: {permission_string}. Expected format: 'module:action'"
            )
        
        rbac_service = RBACService(db)
        if not rbac_service.has_permission(current_user.id, module, action):
            # Get user's current permissions for better error message
            user_permissions = rbac_service.get_user_permissions(current_user.id)
            user_modules = rbac_service.get_user_modules(current_user.id)
            
            error_detail = {
                "error": "Insufficient permissions",
                "required_permission": permission_string,
                "required_module": module.value,
                "required_action": action.value,
                "user_id": current_user.id,
                "user_username": current_user.username,
                "user_has_module_access": module in user_modules,
                "user_permissions_count": len(user_permissions),
                "available_modules": [m.value for m in user_modules],
                "available_permissions": [f"{p.module.value}:{p.action.value}" for p in user_permissions[:10]]  # Limit to first 10
            }
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_detail
            )
        
        return current_user
    
    return dependency


def require_any_permission_dependency(permissions: List[str]):
    """
    FastAPI dependency to require any of the specified permissions
    """
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        rbac_service = RBACService(db)
        
        has_any = False
        checked_permissions = []
        for permission_string in permissions:
            try:
                module_str, action_str = permission_string.split(":")
                module = Module(module_str)
                action = PermissionType(action_str)
                checked_permissions.append(f"{module.value}:{action.value}")
                
                if rbac_service.has_permission(current_user.id, module, action):
                    has_any = True
                    break
            except (ValueError, KeyError):
                checked_permissions.append(f"INVALID: {permission_string}")
                continue
        
        if not has_any:
            # Get user's current permissions for better error message
            user_permissions = rbac_service.get_user_permissions(current_user.id)
            user_modules = rbac_service.get_user_modules(current_user.id)
            
            error_detail = {
                "error": "Insufficient permissions",
                "required_permissions": permissions,
                "checked_permissions": checked_permissions,
                "user_id": current_user.id,
                "user_username": current_user.username,
                "user_permissions_count": len(user_permissions),
                "available_modules": [m.value for m in user_modules],
                "available_permissions": [f"{p.module.value}:{p.action.value}" for p in user_permissions[:10]]  # Limit to first 10
            }
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_detail
            )
        
        return current_user
    
    return dependency


def require_module_access_dependency(module: Module):
    """
    FastAPI dependency to require access to a specific module
    """
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        rbac_service = RBACService(db)
        
        user_modules = rbac_service.get_user_modules(current_user.id)
        if module not in user_modules:
            # Get user's current permissions for better error message
            user_permissions = rbac_service.get_user_permissions(current_user.id)
            
            error_detail = {
                "error": "Module access denied",
                "required_module": module.value,
                "user_id": current_user.id,
                "user_username": current_user.username,
                "user_permissions_count": len(user_permissions),
                "available_modules": [m.value for m in user_modules],
                "available_permissions": [f"{p.module.value}:{p.action.value}" for p in user_permissions[:10]]  # Limit to first 10
            }
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_detail
            )
        
        return current_user
    
    return dependency


# Permission checking utility functions
def check_permission(user_id: int, module: Module, action: PermissionType, db: Session) -> bool:
    """Check if user has specific permission"""
    rbac_service = RBACService(db)
    return rbac_service.has_permission(user_id, module, action)


def check_any_permission(user_id: int, module: Module, actions: List[PermissionType], db: Session) -> bool:
    """Check if user has any of the specified permissions for a module"""
    rbac_service = RBACService(db)
    return rbac_service.has_any_permission(user_id, module, actions)


def get_user_modules(user_id: int, db: Session) -> List[Module]:
    """Get all modules user has access to"""
    rbac_service = RBACService(db)
    return rbac_service.get_user_modules(user_id)


def get_user_permissions(user_id: int, db: Session) -> List:
    """Get all permissions for a user"""
    rbac_service = RBACService(db)
    return rbac_service.get_user_permissions(user_id) 