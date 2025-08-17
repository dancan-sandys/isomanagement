# Import all models for Alembic to detect them
from .rbac import Role, Permission, UserPermission
from .user import User, UserSession, PasswordReset
from .document import Document, DocumentVersion, DocumentApproval, DocumentChangeLog, DocumentTemplate
from .haccp import Product, ProcessFlow, Hazard, HazardReview, CCP, CCPMonitoringLog, CCPVerificationLog, ProductRiskConfig, DecisionTree, CCPMonitoringSchedule, CCPVerificationProgram, CCPValidation, RiskLevel
from .prp import (
    PRPProgram, PRPChecklist, PRPChecklistItem, PRPTemplate, PRPSchedule,
    RiskMatrix, RiskAssessment, RiskControl, CorrectiveAction, PreventiveAction,
    PRPCategory, PRPFrequency, PRPStatus, ChecklistStatus, CorrectiveActionStatus
)
from .supplier import Supplier, Material, SupplierEvaluation, IncomingDelivery, SupplierDocument
from .traceability import Batch, TraceabilityLink, Recall, RecallEntry, RecallAction, TraceabilityReport
from .training import TrainingProgram, TrainingSession, TrainingAttendance, RoleRequiredTraining, TrainingCertificate, HACCPRequiredTraining
from .equipment import Equipment, MaintenancePlan, MaintenanceWorkOrder, CalibrationPlan, CalibrationRecord
from .settings import ApplicationSetting, UserPreference
from .risk import (
    RiskRegisterItem, RiskAction, RiskManagementFramework, RiskContext,
    FSMSRiskIntegration, RiskCorrelation, RiskResourceAllocation,
    RiskCommunication, RiskKPI
)
from .haccp_risk import (
    HACCPRiskAssessment, HACCPRiskIntegration, HACCPRiskMonitoring, HACCPRiskReview,
    HACCPRiskAssessmentType, HACCPRiskReviewStatus, HACCPRiskReviewType,
    HACCPRiskMonitoringType, HACCPRiskMonitoringResult, HACCPRiskIntegrationType,
    HACCPElementType, HACCPRiskReviewOutcome
)
from .notification import Notification, NotificationType, NotificationCategory, NotificationPriority
from .management_review import ManagementReview, ReviewAgendaItem, ReviewAction, ManagementReviewStatus
from .audit_mgmt import (
    Audit, AuditType, AuditStatus,
    AuditChecklistTemplate, AuditChecklistItem, ChecklistResponse,
    AuditFinding, FindingSeverity, FindingStatus,
    AuditAttachment, AuditItemAttachment, AuditFindingAttachment, AuditAuditee,
)

__all__ = [
    # User models
    "Role", "Permission", "UserPermission", "User", "UserSession", "PasswordReset",
    
    # Document models
    "Document", "DocumentVersion", "DocumentApproval", "DocumentChangeLog", "DocumentTemplate",
    
    # HACCP models
    "Product", "ProcessFlow", "Hazard", "HazardReview", "CCP", "CCPMonitoringLog", "CCPVerificationLog", "ProductRiskConfig", "DecisionTree", "CCPMonitoringSchedule", "CCPVerificationProgram", "CCPValidation",
    
    # PRP models
    "PRPProgram", "PRPChecklist", "PRPChecklistItem", "PRPTemplate", "PRPSchedule",
    "RiskMatrix", "RiskAssessment", "RiskControl", "CorrectiveAction", "PreventiveAction",
    "PRPCategory", "PRPFrequency", "PRPStatus", "ChecklistStatus", "RiskLevel", "CorrectiveActionStatus",
    
    # Supplier models
    "Supplier", "Material", "SupplierEvaluation", "IncomingDelivery", "SupplierDocument",
    
    # Traceability models
    "Batch", "TraceabilityLink", "Recall", "RecallEntry", "RecallAction", "TraceabilityReport",
    # Training models
    "TrainingProgram", "TrainingSession", "TrainingAttendance", "RoleRequiredTraining", "TrainingCertificate", "HACCPRequiredTraining",
    # Equipment models
    "Equipment", "MaintenancePlan", "MaintenanceWorkOrder", "CalibrationPlan", "CalibrationRecord",
    
    # Settings models
    "ApplicationSetting", "UserPreference",
    # Risk & Opportunity register
    "RiskRegisterItem", "RiskAction", "RiskManagementFramework", "RiskContext",
    "FSMSRiskIntegration", "RiskCorrelation", "RiskResourceAllocation",
    "RiskCommunication", "RiskKPI",
    "HACCPRiskAssessment", "HACCPRiskIntegration", "HACCPRiskMonitoring", "HACCPRiskReview",
    "HACCPRiskAssessmentType", "HACCPRiskReviewStatus", "HACCPRiskReviewType",
    "HACCPRiskMonitoringType", "HACCPRiskMonitoringResult", "HACCPRiskIntegrationType",
    "HACCPElementType", "HACCPRiskReviewOutcome",
    # Notification models
    "Notification", "NotificationType", "NotificationCategory", "NotificationPriority",
    # Management Reviews
    "ManagementReview", "ReviewAgendaItem", "ReviewAction", "ManagementReviewStatus",
    # Audit management
    "Audit", "AuditType", "AuditStatus",
    "AuditChecklistTemplate", "AuditChecklistItem", "ChecklistResponse",
    "AuditFinding", "FindingSeverity", "FindingStatus",
    "AuditAttachment",
] 