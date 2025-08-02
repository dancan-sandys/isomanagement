from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.core.security import get_current_active_user, require_permission
from app.models.user import User
from app.models.settings import ApplicationSetting, UserPreference, SettingCategory, SettingType
from app.schemas.settings import (
    SettingCreate, SettingUpdate, SettingResponse, SettingsResponse, SettingsByCategory,
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse,
    BulkSettingsUpdate, SettingsValidationResponse, SettingValidationError,
    validate_setting_value, DEFAULT_SETTINGS
)
from app.schemas.common import ResponseModel

router = APIRouter()


@router.get("/", response_model=SettingsResponse)
async def get_settings(
    category: Optional[SettingCategory] = Query(None, description="Filter by category"),
    current_user: User = Depends(require_permission("settings:read")),
    db: Session = Depends(get_db)
):
    """
    Get all application settings, optionally filtered by category
    """
    query = db.query(ApplicationSetting)
    
    if category:
        query = query.filter(ApplicationSetting.category == category)
    
    settings = query.order_by(ApplicationSetting.category, ApplicationSetting.group_name, ApplicationSetting.display_name).all()
    
    # Group settings by category
    categories_dict = {}
    for setting in settings:
        if setting.category not in categories_dict:
            categories_dict[setting.category] = []
        categories_dict[setting.category].append(SettingResponse.from_orm(setting))
    
    # Convert to list format
    categories = [
        SettingsByCategory(category=cat, settings=settings_list)
        for cat, settings_list in categories_dict.items()
    ]
    
    return SettingsResponse(
        categories=categories,
        total_settings=len(settings)
    )


@router.get("/categories", response_model=List[str])
async def get_setting_categories(
    current_user: User = Depends(require_permission("settings:read")),
    db: Session = Depends(get_db)
):
    """
    Get all available setting categories
    """
    categories = db.query(ApplicationSetting.category).distinct().all()
    return [cat[0].value for cat in categories]


@router.get("/{setting_key}", response_model=SettingResponse)
async def get_setting(
    setting_key: str,
    current_user: User = Depends(require_permission("settings:read")),
    db: Session = Depends(get_db)
):
    """
    Get a specific setting by key
    """
    setting = db.query(ApplicationSetting).filter(ApplicationSetting.key == setting_key).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    return SettingResponse.from_orm(setting)


@router.put("/{setting_key}", response_model=SettingResponse)
async def update_setting(
    setting_key: str,
    setting_update: SettingUpdate,
    current_user: User = Depends(require_permission("settings:write")),
    db: Session = Depends(get_db)
):
    """
    Update a specific setting
    """
    setting = db.query(ApplicationSetting).filter(ApplicationSetting.key == setting_key).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    if not setting.is_editable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This setting is not editable"
        )
    
    # Validate the new value
    if not validate_setting_value(setting_update.value, setting.setting_type, setting.validation_rules):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid value for setting type {setting.setting_type.value}"
        )
    
    setting.value = setting_update.value
    setting.updated_by = current_user.id
    
    db.commit()
    db.refresh(setting)
    
    return SettingResponse.from_orm(setting)


@router.post("/bulk-update", response_model=SettingsValidationResponse)
async def bulk_update_settings(
    bulk_update: BulkSettingsUpdate,
    current_user: User = Depends(require_permission("settings:write")),
    db: Session = Depends(get_db)
):
    """
    Update multiple settings at once
    """
    errors = []
    updated_settings = []
    
    for setting_data in bulk_update.settings:
        if len(setting_data) != 1:  # Should have exactly one key-value pair
            errors.append(SettingValidationError(
                key="unknown",
                error="Invalid setting format"
            ))
            continue
        
        key, value = list(setting_data.items())[0]
        setting = db.query(ApplicationSetting).filter(ApplicationSetting.key == key).first()
        
        if not setting:
            errors.append(SettingValidationError(
                key=key,
                error="Setting not found"
            ))
            continue
        
        if not setting.is_editable:
            errors.append(SettingValidationError(
                key=key,
                error="Setting is not editable"
            ))
            continue
        
        if not validate_setting_value(value, setting.setting_type, setting.validation_rules):
            errors.append(SettingValidationError(
                key=key,
                error=f"Invalid value for setting type {setting.setting_type.value}"
            ))
            continue
        
        setting.value = value
        setting.updated_by = current_user.id
        updated_settings.append(setting)
    
    if not errors:
        db.commit()
        return SettingsValidationResponse(valid=True)
    else:
        return SettingsValidationResponse(valid=False, errors=errors)


@router.post("/initialize", response_model=ResponseModel)
async def initialize_default_settings(
    current_user: User = Depends(require_permission("settings:write")),
    db: Session = Depends(get_db)
):
    """
    Initialize default settings if they don't exist
    """
    try:
        existing_keys = {s.key for s in db.query(ApplicationSetting.key).all()}
        created_count = 0
        
        for setting_data in DEFAULT_SETTINGS:
            if setting_data["key"] not in existing_keys:
                setting = ApplicationSetting(
                    key=setting_data["key"],
                    value=setting_data["value"],
                    setting_type=setting_data["setting_type"],
                    category=setting_data["category"],
                    display_name=setting_data["display_name"],
                    description=setting_data.get("description"),
                    is_editable=setting_data.get("is_editable", True),
                    is_required=setting_data.get("is_required", False),
                    validation_rules=setting_data.get("validation_rules"),
                    default_value=setting_data.get("default_value"),
                    group_name=setting_data.get("group_name"),
                    created_by=current_user.id
                )
                db.add(setting)
                created_count += 1
        
        db.commit()
        
        return ResponseModel(
            success=True,
            message=f"Initialized {created_count} default settings"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize settings: {str(e)}"
        )


@router.post("/reset/{setting_key}", response_model=SettingResponse)
async def reset_setting_to_default(
    setting_key: str,
    current_user: User = Depends(require_permission("settings:write")),
    db: Session = Depends(get_db)
):
    """
    Reset a setting to its default value
    """
    setting = db.query(ApplicationSetting).filter(ApplicationSetting.key == setting_key).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    if not setting.default_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No default value available for this setting"
        )
    
    setting.value = setting.default_value
    setting.updated_by = current_user.id
    
    db.commit()
    db.refresh(setting)
    
    return SettingResponse.from_orm(setting)


# User Preferences endpoints
@router.get("/preferences/me", response_model=List[UserPreferenceResponse])
async def get_user_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's preferences
    """
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id
    ).all()
    
    return [UserPreferenceResponse.from_orm(pref) for pref in preferences]


@router.post("/preferences", response_model=UserPreferenceResponse)
async def create_user_preference(
    preference: UserPreferenceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a user preference
    """
    # Users can only create preferences for themselves
    if preference.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create preferences for other users"
        )
    
    # Check if preference already exists
    existing = db.query(UserPreference).filter(
        and_(
            UserPreference.user_id == preference.user_id,
            UserPreference.key == preference.key
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preference already exists"
        )
    
    db_preference = UserPreference(
        user_id=preference.user_id,
        key=preference.key,
        value=preference.value,
        setting_type=preference.setting_type
    )
    
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    
    return UserPreferenceResponse.from_orm(db_preference)


@router.put("/preferences/{preference_key}", response_model=UserPreferenceResponse)
async def update_user_preference(
    preference_key: str,
    preference_update: UserPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a user preference
    """
    preference = db.query(UserPreference).filter(
        and_(
            UserPreference.user_id == current_user.id,
            UserPreference.key == preference_key
        )
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
    
    preference.value = preference_update.value
    
    db.commit()
    db.refresh(preference)
    
    return UserPreferenceResponse.from_orm(preference)


@router.delete("/preferences/{preference_key}")
async def delete_user_preference(
    preference_key: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user preference
    """
    preference = db.query(UserPreference).filter(
        and_(
            UserPreference.user_id == current_user.id,
            UserPreference.key == preference_key
        )
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


# Utility endpoints
@router.get("/export/json", response_model=Dict[str, Any])
async def export_settings_json(
    current_user: User = Depends(require_permission("settings:read")),
    db: Session = Depends(get_db)
):
    """
    Export all settings as JSON
    """
    settings = db.query(ApplicationSetting).all()
    
    export_data = {
        "exported_at": "2024-01-15T10:00:00Z",
        "exported_by": current_user.username,
        "settings": {}
    }
    
    for setting in settings:
        export_data["settings"][setting.key] = {
            "value": setting.value,
            "category": setting.category.value,
            "setting_type": setting.setting_type.value,
            "display_name": setting.display_name,
            "description": setting.description,
            "group_name": setting.group_name
        }
    
    return export_data


@router.post("/import/json", response_model=ResponseModel)
async def import_settings_json(
    settings_data: Dict[str, Any],
    current_user: User = Depends(require_permission("settings:write")),
    db: Session = Depends(get_db)
):
    """
    Import settings from JSON
    """
    try:
        imported_count = 0
        errors = []
        
        for key, data in settings_data.get("settings", {}).items():
            setting = db.query(ApplicationSetting).filter(ApplicationSetting.key == key).first()
            
            if not setting:
                errors.append(f"Setting '{key}' not found")
                continue
            
            if not setting.is_editable:
                errors.append(f"Setting '{key}' is not editable")
                continue
            
            # Validate the value
            if not validate_setting_value(data["value"], setting.setting_type, setting.validation_rules):
                errors.append(f"Invalid value for setting '{key}'")
                continue
            
            setting.value = data["value"]
            setting.updated_by = current_user.id
            imported_count += 1
        
        if errors:
            return ResponseModel(
                success=False,
                message=f"Import completed with {len(errors)} errors",
                data={"errors": errors, "imported_count": imported_count}
            )
        
        db.commit()
        
        return ResponseModel(
            success=True,
            message=f"Successfully imported {imported_count} settings"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import settings: {str(e)}"
        ) 