from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.rbac import Role, Permission, UserPermission, Module, PermissionType
from app.models.user import User
from app.schemas.rbac import RoleCreate, RoleUpdate, RoleClone
from fastapi import HTTPException, status


def check_user_permission(db: Session, user_id: int, module: str, action: str) -> bool:
    """Standalone function to check if user has specific permission"""
    try:
        # Convert string to enum (use lowercase to match enum values)
        module_enum = Module(module.lower())
        action_enum = PermissionType(action.lower())
    except ValueError:
        return False
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return False
    
    # Check role permissions
    if user.role:
        for permission in user.role.permissions:
            if permission.module == module_enum and permission.action == action_enum:
                return True
    
    # Check custom permissions
    for user_perm in user.custom_permissions:
        if (user_perm.permission.module == module_enum and 
            user_perm.permission.action == action_enum and 
            user_perm.granted):
            return True
    
    return False


class RBACService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_permissions(self, user_id: int) -> List[Permission]:
        """Get all permissions for a user (role + custom permissions)"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # Get role permissions
        role_permissions = user.role.permissions if user.role else []
        
        # Get custom permissions
        custom_permissions = []
        for user_perm in user.custom_permissions:
            if user_perm.granted:
                custom_permissions.append(user_perm.permission)
        
        # Combine and deduplicate
        all_permissions = role_permissions + custom_permissions
        unique_permissions = {p.id: p for p in all_permissions}.values()
        
        return list(unique_permissions)

    def has_permission(self, user_id: int, module: Module, action: PermissionType) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_user_permissions(user_id)
        
        for permission in permissions:
            if permission.module == module and permission.action == action:
                return True
        
        return False

    def has_any_permission(self, user_id: int, module: Module, actions: List[PermissionType]) -> bool:
        """Check if user has any of the specified permissions for a module"""
        permissions = self.get_user_permissions(user_id)
        
        for permission in permissions:
            if permission.module == module and permission.action in actions:
                return True
        
        return False

    def get_user_modules(self, user_id: int) -> List[Module]:
        """Get all modules user has access to"""
        permissions = self.get_user_permissions(user_id)
        modules = set()
        
        for permission in permissions:
            modules.add(permission.module)
        
        return list(modules)

    def create_role(self, role_data: RoleCreate, created_by: int) -> Role:
        """Create a new role"""
        # Check if role name already exists
        existing_role = self.db.query(Role).filter(Role.name == role_data.name).first()
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
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(role_data.permissions)
            ).all()
            role.permissions = permissions
        
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        
        return role

    def update_role(self, role_id: int, role_data: RoleUpdate, updated_by: int) -> Role:
        """Update an existing role"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        if not role.is_editable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This role cannot be edited"
            )
        
        # Check if name is being changed and if it already exists
        if role_data.name and role_data.name != role.name:
            existing_role = self.db.query(Role).filter(
                and_(Role.name == role_data.name, Role.id != role_id)
            ).first()
            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role with this name already exists"
                )
        
        # Update fields
        if role_data.name is not None:
            role.name = role_data.name
        if role_data.description is not None:
            role.description = role_data.description
        if role_data.is_active is not None:
            role.is_active = role_data.is_active
        
        # Update permissions
        if role_data.permissions is not None:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(role_data.permissions)
            ).all()
            role.permissions = permissions
        
        self.db.commit()
        self.db.refresh(role)
        
        return role

    def clone_role(self, role_id: int, clone_data: RoleClone, created_by: int) -> Role:
        """Clone an existing role"""
        original_role = self.db.query(Role).filter(Role.id == role_id).first()
        if not original_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Original role not found"
            )
        
        # Check if new name already exists
        existing_role = self.db.query(Role).filter(Role.name == clone_data.name).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists"
            )
        
        # Create new role
        new_role = Role(
            name=clone_data.name,
            description=clone_data.description or f"Cloned from {original_role.name}",
            is_default=False,
            is_editable=True,
            is_active=True
        )
        
        # Copy permissions
        if clone_data.permissions:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(clone_data.permissions)
            ).all()
            new_role.permissions = permissions
        else:
            new_role.permissions = original_role.permissions.copy()
        
        self.db.add(new_role)
        self.db.commit()
        self.db.refresh(new_role)
        
        return new_role

    def delete_role(self, role_id: int, deleted_by: int) -> bool:
        """Delete a role (only if no users are assigned)"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        if not role.is_editable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This role cannot be deleted"
            )
        
        # Check if any users are assigned to this role
        user_count = self.db.query(User).filter(User.role_id == role_id).count()
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role. {user_count} user(s) are assigned to this role."
            )
        
        self.db.delete(role)
        self.db.commit()
        
        return True

    def get_role_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all roles with user counts"""
        roles = self.db.query(Role).filter(Role.is_active == True).all()
        summary = []
        
        for role in roles:
            user_count = self.db.query(User).filter(User.role_id == role.id).count()
            summary.append({
                "role_id": role.id,
                "role_name": role.name,
                "user_count": user_count,
                "permissions": role.permissions
            })
        
        return summary

    def get_permission_matrix(self) -> Dict[str, Any]:
        """Get permission matrix for all roles"""
        roles = self.db.query(Role).filter(Role.is_active == True).all()
        modules = list(Module)
        permissions = list(PermissionType)
        
        matrix = {
            "modules": modules,
            "permissions": permissions,
            "role_permissions": {}
        }
        
        for role in roles:
            role_perms = {}
            for module in modules:
                module_perms = []
                for permission in role.permissions:
                    if permission.module == module:
                        module_perms.append(permission.action.value)
                role_perms[module.value] = module_perms
            matrix["role_permissions"][role.name] = role_perms
        
        return matrix

    def assign_user_permission(self, user_id: int, permission_id: int, granted: bool, assigned_by: int) -> UserPermission:
        """Assign custom permission to user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        # Check if permission already exists
        existing_perm = self.db.query(UserPermission).filter(
            and_(UserPermission.user_id == user_id, UserPermission.permission_id == permission_id)
        ).first()
        
        if existing_perm:
            existing_perm.granted = granted
            existing_perm.granted_by = assigned_by
            self.db.commit()
            self.db.refresh(existing_perm)
            return existing_perm
        else:
            user_perm = UserPermission(
                user_id=user_id,
                permission_id=permission_id,
                granted=granted,
                granted_by=assigned_by
            )
            self.db.add(user_perm)
            self.db.commit()
            self.db.refresh(user_perm)
            return user_perm

    def remove_user_permission(self, user_id: int, permission_id: int) -> bool:
        """Remove custom permission from user"""
        user_perm = self.db.query(UserPermission).filter(
            and_(UserPermission.user_id == user_id, UserPermission.permission_id == permission_id)
        ).first()
        
        if user_perm:
            self.db.delete(user_perm)
            self.db.commit()
            return True
        
        return False 