#!/usr/bin/env python3
"""
Script to initialize default settings for the ISO 22000 FSMS system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.settings import ApplicationSetting, SettingCategory, SettingType
from app.schemas.settings import DEFAULT_SETTINGS

def initialize_default_settings():
    """Initialize default settings in the database"""
    
    db = SessionLocal()
    
    try:
        # Check if settings already exist
        existing_settings = db.query(ApplicationSetting).count()
        if existing_settings > 0:
            print(f"Found {existing_settings} existing settings. Skipping initialization.")
            return
        
        print("Initializing default settings...")
        
        # Create default settings
        for setting_data in DEFAULT_SETTINGS:
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
                default_value=setting_data.get("default_value", setting_data["value"]),
                group_name=setting_data.get("group_name"),
                created_by=1  # Admin user
            )
            
            db.add(setting)
            print(f"Created setting: {setting_data['display_name']} ({setting_data['key']})")
        
        db.commit()
        print(f"\nSuccessfully initialized {len(DEFAULT_SETTINGS)} default settings!")
        
        # Print summary by category
        print("\nSettings by Category:")
        print("=" * 50)
        categories = db.query(ApplicationSetting.category).distinct().all()
        for category in categories:
            count = db.query(ApplicationSetting).filter(ApplicationSetting.category == category[0]).count()
            print(f"{category[0].value}: {count} settings")
        
    except Exception as e:
        print(f"Error initializing settings: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing default settings for ISO 22000 FSMS...")
    initialize_default_settings()
    print("Done!") 