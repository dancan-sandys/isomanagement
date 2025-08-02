from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class SettingCategory(str, enum.Enum):
    GENERAL = "GENERAL"
    NOTIFICATIONS = "NOTIFICATIONS"
    SECURITY = "SECURITY"
    HACCP = "HACCP"
    PRP = "PRP"
    SUPPLIERS = "SUPPLIERS"
    TRACEABILITY = "TRACEABILITY"
    AUDIT = "AUDIT"
    TRAINING = "TRAINING"
    REPORTING = "REPORTING"
    INTEGRATION = "INTEGRATION"


class SettingType(str, enum.Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"
    EMAIL = "EMAIL"
    URL = "URL"
    FILE_PATH = "FILE_PATH"


class ApplicationSetting(Base):
    __tablename__ = "application_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    setting_type = Column(Enum(SettingType), nullable=False, default=SettingType.STRING)
    category = Column(Enum(SettingCategory), nullable=False, default=SettingCategory.GENERAL)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    is_editable = Column(Boolean, default=True)
    is_required = Column(Boolean, default=False)
    validation_rules = Column(JSON)  # Store validation rules as JSON
    default_value = Column(Text)
    group_name = Column(String(100))  # For grouping related settings
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)
    
    def __repr__(self):
        return f"<ApplicationSetting(key='{self.key}', category='{self.category}')>"


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    setting_type = Column(Enum(SettingType), nullable=False, default=SettingType.STRING)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, key='{self.key}')>" 