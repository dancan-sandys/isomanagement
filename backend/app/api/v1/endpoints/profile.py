from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import os
import shutil

from app.core.database import get_db
from app.core.security import get_current_active_user, get_password_hash, verify_password
from app.models.user import User
from app.models.settings import UserPreference, SettingType
from app.schemas.auth import UserProfile, PasswordChange
from app.schemas.common import ResponseModel

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile information
    """
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role_id=current_user.role_id,
        role_name=None,
        department=current_user.department_name,
        position=current_user.position,
        phone=current_user.phone,
        employee_id=current_user.employee_id,
        profile_picture=current_user.profile_picture,
        bio=current_user.bio,
        last_login=current_user.last_login
    )


@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    full_name: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information
    """
    # Update fields if provided
    if full_name is not None:
        current_user.full_name = full_name
    if department is not None:
        current_user.department_name = department
    if position is not None:
        current_user.position = position
    if phone is not None:
        current_user.phone = phone
    if bio is not None:
        current_user.bio = bio
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role_id=current_user.role_id,
        role_name=None,
        department=current_user.department_name,
        position=current_user.position,
        phone=current_user.phone,
        employee_id=current_user.employee_id,
        profile_picture=current_user.profile_picture,
        bio=current_user.bio,
        last_login=current_user.last_login
    )


@router.post("/me/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password
    """
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    hashed_password = get_password_hash(password_change.new_password)
    current_user.hashed_password = hashed_password
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return ResponseModel(
        success=True,
        message="Password changed successfully"
    )


@router.post("/me/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload profile picture
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Validate file size (max 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"avatar_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update user profile
    current_user.profile_picture = file_path
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return ResponseModel(
        success=True,
        message="Avatar uploaded successfully",
        data={"avatar_url": file_path}
    )


@router.delete("/me/avatar")
async def delete_avatar(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete profile picture
    """
    if current_user.profile_picture:
        # Delete file if it exists
        if os.path.exists(current_user.profile_picture):
            os.remove(current_user.profile_picture)
        
        # Update user profile
        current_user.profile_picture = None
        current_user.updated_at = datetime.utcnow()
        db.commit()
    
    return ResponseModel(
        success=True,
        message="Avatar deleted successfully"
    )


@router.get("/me/preferences")
async def get_my_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's preferences
    """
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id
    ).all()
    
    return ResponseModel(
        success=True,
        message="Preferences retrieved successfully",
        data=preferences
    )


@router.post("/me/preferences")
async def create_preference(
    key: str = Form(...),
    value: str = Form(...),
    setting_type: SettingType = Form(SettingType.STRING),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create or update user preference
    """
    # Check if preference already exists
    existing_pref = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id,
        UserPreference.key == key
    ).first()
    
    if existing_pref:
        # Update existing preference
        existing_pref.value = value
        existing_pref.setting_type = setting_type
        existing_pref.updated_at = datetime.utcnow()
    else:
        # Create new preference
        preference = UserPreference(
            user_id=current_user.id,
            key=key,
            value=value,
            setting_type=setting_type
        )
        db.add(preference)
    
    db.commit()
    
    return ResponseModel(
        success=True,
        message="Preference saved successfully"
    )


@router.delete("/me/preferences/{key}")
async def delete_preference(
    key: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete user preference
    """
    preference = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id,
        UserPreference.key == key
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
    
    db.delete(preference)
    db.commit()
    
    return ResponseModel(
        success=True,
        message="Preference deleted successfully"
    )


@router.get("/me/activity")
async def get_my_activity(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's activity summary
    """
    # Get user sessions
    sessions = db.query(User).filter(
        User.id == current_user.id
    ).first()
    
    activity_data = {
        "last_login": current_user.last_login,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "failed_login_attempts": current_user.failed_login_attempts,
        "is_locked": current_user.locked_until and current_user.locked_until > datetime.utcnow(),
        "locked_until": current_user.locked_until
    }
    
    return ResponseModel(
        success=True,
        message="Activity data retrieved successfully",
        data=activity_data
    )


@router.get("/me/security")
async def get_security_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's security information
    """
    security_data = {
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "failed_login_attempts": current_user.failed_login_attempts,
        "locked_until": current_user.locked_until,
        "last_login": current_user.last_login,
        "account_created": current_user.created_at,
        "last_updated": current_user.updated_at
    }
    
    return ResponseModel(
        success=True,
        message="Security information retrieved successfully",
        data=security_data
    ) 