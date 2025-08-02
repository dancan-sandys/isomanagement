from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.settings import SettingCategory, SettingType


class SettingBase(BaseModel):
    key: str
    value: str
    setting_type: SettingType
    category: SettingCategory
    display_name: str
    description: Optional[str] = None
    is_editable: bool = True
    is_required: bool = False
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None
    group_name: Optional[str] = None


class SettingCreate(SettingBase):
    pass


class SettingUpdate(BaseModel):
    value: str
    updated_by: int


class SettingResponse(SettingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    updated_by: Optional[int]

    class Config:
        from_attributes = True


class UserPreferenceBase(BaseModel):
    key: str
    value: str
    setting_type: SettingType = SettingType.STRING


class UserPreferenceCreate(UserPreferenceBase):
    user_id: int


class UserPreferenceUpdate(BaseModel):
    value: str


class UserPreferenceResponse(UserPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SettingsByCategory(BaseModel):
    category: SettingCategory
    settings: List[SettingResponse]


class SettingsResponse(BaseModel):
    categories: List[SettingsByCategory]
    total_settings: int


class BulkSettingsUpdate(BaseModel):
    settings: List[Dict[str, str]]  # List of {key: value} pairs


class SettingValidationError(BaseModel):
    key: str
    error: str


class SettingsValidationResponse(BaseModel):
    valid: bool
    errors: List[SettingValidationError] = []


# Validation functions
def validate_setting_value(value: str, setting_type: SettingType, validation_rules: Optional[Dict] = None) -> bool:
    """Validate setting value based on type and rules"""
    try:
        if setting_type == SettingType.INTEGER:
            int_value = int(value)
            if validation_rules:
                min_val = validation_rules.get('min')
                max_val = validation_rules.get('max')
                if min_val is not None and int_value < min_val:
                    return False
                if max_val is not None and int_value > max_val:
                    return False
        elif setting_type == SettingType.BOOLEAN:
            if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                return False
        elif setting_type == SettingType.EMAIL:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                return False
        elif setting_type == SettingType.URL:
            import re
            url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
            if not re.match(url_pattern, value):
                return False
        elif setting_type == SettingType.JSON:
            import json
            json.loads(value)
        
        return True
    except (ValueError, json.JSONDecodeError):
        return False


# Default settings configuration
DEFAULT_SETTINGS = [
    # General Settings
    {
        "key": "company_name",
        "value": "Dairy Processing Plant",
        "setting_type": SettingType.STRING,
        "category": SettingCategory.GENERAL,
        "display_name": "Company Name",
        "description": "Name of the dairy processing facility",
        "is_required": True,
        "group_name": "Company Information"
    },
    {
        "key": "facility_address",
        "value": "123 Dairy Street, Milk City, MC 12345",
        "setting_type": SettingType.STRING,
        "category": SettingCategory.GENERAL,
        "display_name": "Facility Address",
        "description": "Physical address of the processing facility",
        "group_name": "Company Information"
    },
    {
        "key": "contact_email",
        "value": "info@dairy.com",
        "setting_type": SettingType.EMAIL,
        "category": SettingCategory.GENERAL,
        "display_name": "Contact Email",
        "description": "Primary contact email for the facility",
        "group_name": "Company Information"
    },
    {
        "key": "contact_phone",
        "value": "+1-555-123-4567",
        "setting_type": SettingType.STRING,
        "category": SettingCategory.GENERAL,
        "display_name": "Contact Phone",
        "description": "Primary contact phone number",
        "group_name": "Company Information"
    },
    {
        "key": "timezone",
        "value": "UTC-5",
        "setting_type": SettingType.STRING,
        "category": SettingCategory.GENERAL,
        "display_name": "Timezone",
        "description": "Default timezone for the facility",
        "group_name": "System Configuration"
    },
    {
        "key": "date_format",
        "value": "MM/DD/YYYY",
        "setting_type": SettingType.STRING,
        "category": SettingCategory.GENERAL,
        "display_name": "Date Format",
        "description": "Default date format for the application",
        "group_name": "System Configuration"
    },
    
    # Notifications
    {
        "key": "email_notifications_enabled",
        "value": "true",
        "setting_type": SettingType.BOOLEAN,
        "category": SettingCategory.NOTIFICATIONS,
        "display_name": "Enable Email Notifications",
        "description": "Send email notifications for important events",
        "group_name": "Email Settings"
    },
    {
        "key": "notification_email",
        "value": "qa@dairy.com",
        "setting_type": SettingType.EMAIL,
        "category": SettingCategory.NOTIFICATIONS,
        "display_name": "Notification Email",
        "description": "Email address for system notifications",
        "group_name": "Email Settings"
    },
    {
        "key": "ccp_alert_threshold",
        "value": "5",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.NOTIFICATIONS,
        "display_name": "CCP Alert Threshold (minutes)",
        "description": "Minutes before CCP monitoring is due to send alert",
        "validation_rules": {"min": 1, "max": 60},
        "group_name": "Alert Settings"
    },
    {
        "key": "prp_reminder_days",
        "value": "1",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.NOTIFICATIONS,
        "display_name": "PRP Reminder Days",
        "description": "Days before PRP tasks are due to send reminder",
        "validation_rules": {"min": 0, "max": 7},
        "group_name": "Alert Settings"
    },
    
    # Security
    {
        "key": "password_min_length",
        "value": "8",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.SECURITY,
        "display_name": "Minimum Password Length",
        "description": "Minimum required password length",
        "validation_rules": {"min": 6, "max": 20},
        "group_name": "Password Policy"
    },
    {
        "key": "password_expiry_days",
        "value": "90",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.SECURITY,
        "display_name": "Password Expiry (days)",
        "description": "Number of days before password expires",
        "validation_rules": {"min": 30, "max": 365},
        "group_name": "Password Policy"
    },
    {
        "key": "session_timeout_minutes",
        "value": "30",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.SECURITY,
        "display_name": "Session Timeout (minutes)",
        "description": "Minutes of inactivity before session expires",
        "validation_rules": {"min": 5, "max": 480},
        "group_name": "Session Settings"
    },
    {
        "key": "failed_login_attempts",
        "value": "5",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.SECURITY,
        "display_name": "Failed Login Attempts",
        "description": "Number of failed attempts before account lockout",
        "validation_rules": {"min": 3, "max": 10},
        "group_name": "Account Security"
    },
    
    # HACCP Settings
    {
        "key": "haccp_team_leader",
        "value": "qa_manager",
        "setting_type": SettingType.STRING,
        "category": SettingCategory.HACCP,
        "display_name": "HACCP Team Leader",
        "description": "Username of the HACCP team leader",
        "group_name": "Team Configuration"
    },
    {
        "key": "ccp_monitoring_frequency",
        "value": "continuous",
        "setting_type": SettingType.STRING,
        "category": SettingCategory.HACCP,
        "display_name": "Default CCP Monitoring Frequency",
        "description": "Default frequency for CCP monitoring",
        "group_name": "Monitoring Settings"
    },
    {
        "key": "hazard_assessment_matrix",
        "value": "3x3",
        "setting_type": SettingType.STRING,
        "category": SettingCategory.HACCP,
        "display_name": "Hazard Assessment Matrix",
        "description": "Matrix size for hazard assessment (3x3, 5x5)",
        "group_name": "Assessment Settings"
    },
    
    # PRP Settings
    {
        "key": "prp_auto_escalation",
        "value": "true",
        "setting_type": SettingType.BOOLEAN,
        "category": SettingCategory.PRP,
        "display_name": "Auto-escalate Missed PRPs",
        "description": "Automatically escalate missed PRP tasks",
        "group_name": "Workflow Settings"
    },
    {
        "key": "prp_escalation_hours",
        "value": "24",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.PRP,
        "display_name": "PRP Escalation Delay (hours)",
        "description": "Hours after due date before escalation",
        "validation_rules": {"min": 1, "max": 168},
        "group_name": "Workflow Settings"
    },
    
    # Supplier Settings
    {
        "key": "supplier_evaluation_frequency",
        "value": "12",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.SUPPLIERS,
        "display_name": "Supplier Evaluation Frequency (months)",
        "description": "Months between supplier evaluations",
        "validation_rules": {"min": 1, "max": 24},
        "group_name": "Evaluation Settings"
    },
    {
        "key": "certificate_expiry_alert_days",
        "value": "30",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.SUPPLIERS,
        "display_name": "Certificate Expiry Alert (days)",
        "description": "Days before certificate expiry to send alert",
        "validation_rules": {"min": 7, "max": 90},
        "group_name": "Alert Settings"
    },
    
    # Traceability Settings
    {
        "key": "batch_retention_period",
        "value": "730",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.TRACEABILITY,
        "display_name": "Batch Record Retention (days)",
        "description": "Days to retain batch records",
        "validation_rules": {"min": 365, "max": 2555},
        "group_name": "Record Retention"
    },
    {
        "key": "auto_generate_barcodes",
        "value": "true",
        "setting_type": SettingType.BOOLEAN,
        "category": SettingCategory.TRACEABILITY,
        "display_name": "Auto-generate Barcodes",
        "description": "Automatically generate barcodes for new batches",
        "group_name": "Barcode Settings"
    },
    
    # Audit Settings
    {
        "key": "internal_audit_frequency",
        "value": "6",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.AUDIT,
        "display_name": "Internal Audit Frequency (months)",
        "description": "Months between internal audits",
        "validation_rules": {"min": 1, "max": 12},
        "group_name": "Audit Schedule"
    },
    {
        "key": "audit_report_template",
        "value": "standard",
        "setting_type": SettingType.STRING,
        "category": SettingCategory.AUDIT,
        "display_name": "Audit Report Template",
        "description": "Default template for audit reports",
        "group_name": "Report Settings"
    },
    
    # Training Settings
    {
        "key": "training_expiry_alert_days",
        "value": "30",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.TRAINING,
        "display_name": "Training Expiry Alert (days)",
        "description": "Days before training expiry to send alert",
        "validation_rules": {"min": 7, "max": 90},
        "group_name": "Alert Settings"
    },
    {
        "key": "competency_assessment_frequency",
        "value": "12",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.TRAINING,
        "display_name": "Competency Assessment Frequency (months)",
        "description": "Months between competency assessments",
        "validation_rules": {"min": 3, "max": 24},
        "group_name": "Assessment Settings"
    },
    
    # Reporting Settings
    {
        "key": "default_report_format",
        "value": "PDF",
        "setting_type": SettingType.STRING,
        "category": SettingCategory.REPORTING,
        "display_name": "Default Report Format",
        "description": "Default format for generated reports",
        "group_name": "Report Settings"
    },
    {
        "key": "auto_generate_reports",
        "value": "false",
        "setting_type": SettingType.BOOLEAN,
        "category": SettingCategory.REPORTING,
        "display_name": "Auto-generate Reports",
        "description": "Automatically generate scheduled reports",
        "group_name": "Report Settings"
    },
    {
        "key": "report_retention_days",
        "value": "2555",
        "setting_type": SettingType.INTEGER,
        "category": SettingCategory.REPORTING,
        "display_name": "Report Retention (days)",
        "description": "Days to retain generated reports",
        "validation_rules": {"min": 365, "max": 3650},
        "group_name": "Report Settings"
    },
    
    # Integration Settings
    {
        "key": "erp_integration_enabled",
        "value": "false",
        "setting_type": SettingType.BOOLEAN,
        "category": SettingCategory.INTEGRATION,
        "display_name": "Enable ERP Integration",
        "description": "Enable integration with ERP system",
        "group_name": "System Integration"
    },
    {
        "key": "erp_api_url",
        "value": "",
        "setting_type": SettingType.URL,
        "category": SettingCategory.INTEGRATION,
        "display_name": "ERP API URL",
        "description": "URL for ERP system API",
        "group_name": "System Integration"
    },
    {
        "key": "lims_integration_enabled",
        "value": "false",
        "setting_type": SettingType.BOOLEAN,
        "category": SettingCategory.INTEGRATION,
        "display_name": "Enable LIMS Integration",
        "description": "Enable integration with LIMS system",
        "group_name": "System Integration"
    }
] 