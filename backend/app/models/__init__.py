# Import all models for Alembic to detect them
from .rbac import Role, Permission, UserPermission
from .user import User, UserSession, PasswordReset
from .document import Document, DocumentVersion, DocumentApproval, DocumentChangeLog, DocumentTemplate
from .haccp import Product, ProcessFlow, Hazard, HazardReview, CCP, CCPMonitoringLog, CCPVerificationLog, ProductRiskConfig, DecisionTree, CCPMonitoringSchedule, CCPVerificationProgram, CCPValidation, HACCPEvidenceAttachment, HACCPAuditLog, RiskLevel
from .prp import (
    PRPProgram, PRPChecklist, PRPChecklistItem, PRPTemplate, PRPSchedule,
    RiskMatrix, RiskAssessment, RiskControl, CorrectiveAction, PRPPreventiveAction,
    PRPCategory, PRPFrequency, PRPStatus, ChecklistStatus, CorrectiveActionStatus
)
from .supplier import Supplier, Material, SupplierEvaluation, IncomingDelivery, SupplierDocument
from .traceability import Batch, TraceabilityLink, Recall, RecallEntry, RecallAction, TraceabilityReport
from .training import TrainingProgram, TrainingSession, TrainingAttendance, RoleRequiredTraining, TrainingCertificate, HACCPRequiredTraining
from .equipment import Equipment, MaintenancePlan, MaintenanceWorkOrder, CalibrationPlan, CalibrationRecord
from .settings import ApplicationSetting, UserPreference
from .food_safety_objectives import FoodSafetyObjective, ObjectiveTarget, ObjectiveProgress
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
from .audit_risk import (
    AuditRiskAssessment, AuditRiskIntegration, AuditRiskMonitoring, AuditRiskReview,
    AuditRiskAssessmentType, AuditRiskReviewStatus, AuditRiskReviewType,
    AuditRiskMonitoringType, AuditRiskMonitoringResult, AuditRiskIntegrationType,
    AuditElementType, AuditRiskReviewOutcome, PRPAuditIntegration
)
from .notification import Notification, NotificationType, NotificationCategory, NotificationPriority
from .management_review import (
    ManagementReview, ReviewAgendaItem, ReviewAction, ManagementReviewStatus,
    ManagementReviewType, ReviewInputType, ReviewOutputType, ActionPriority, ActionStatus,
    ManagementReviewInput, ManagementReviewOutput, ManagementReviewTemplate, ManagementReviewKPI
)
from .audit_mgmt import (
    Audit, AuditType, AuditStatus,
    AuditChecklistTemplate, AuditChecklistItem, ChecklistResponse,
    AuditFinding, FindingSeverity, FindingStatus,
    AuditAttachment, AuditItemAttachment, AuditFindingAttachment, AuditAuditee,
)
from .dashboard import Department

__all__ = [
    # User models
    "Role", "Permission", "UserPermission", "User", "UserSession", "PasswordReset",
    
    # Document models
    "Document", "DocumentVersion", "DocumentApproval", "DocumentChangeLog", "DocumentTemplate",
    
    # HACCP models
    "Product", "ProcessFlow", "Hazard", "HazardReview", "CCP", "CCPMonitoringLog", "CCPVerificationLog", "ProductRiskConfig", "DecisionTree", "CCPMonitoringSchedule", "CCPVerificationProgram", "CCPValidation", "HACCPEvidenceAttachment", "HACCPAuditLog", "HACCPEvidenceAttachment", "HACCPAuditLog",
    
    # PRP models
    "PRPProgram", "PRPChecklist", "PRPChecklistItem", "PRPTemplate", "PRPSchedule",
    "RiskMatrix", "RiskAssessment", "RiskControl", "CorrectiveAction", "PRPPreventiveAction",
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
    # Food safety objectives
    "FoodSafetyObjective", "ObjectiveTarget", "ObjectiveProgress",
    # Risk & Opportunity register
    "RiskRegisterItem", "RiskAction", "RiskManagementFramework", "RiskContext",
    "FSMSRiskIntegration", "RiskCorrelation", "RiskResourceAllocation",
    "RiskCommunication", "RiskKPI",
    "HACCPRiskAssessment", "HACCPRiskIntegration", "HACCPRiskMonitoring", "HACCPRiskReview",
    "HACCPRiskAssessmentType", "HACCPRiskReviewStatus", "HACCPRiskReviewType",
    "HACCPRiskMonitoringType", "HACCPRiskMonitoringResult", "HACCPRiskIntegrationType",
    "HACCPElementType", "HACCPRiskReviewOutcome",
    "AuditRiskAssessment", "AuditRiskIntegration", "AuditRiskMonitoring", "AuditRiskReview",
    "AuditRiskAssessmentType", "AuditRiskReviewStatus", "AuditRiskReviewType",
    "AuditRiskMonitoringType", "AuditRiskMonitoringResult", "AuditRiskIntegrationType",
    "AuditElementType", "AuditRiskReviewOutcome", "PRPAuditIntegration",
    # Notification models
    "Notification", "NotificationType", "NotificationCategory", "NotificationPriority",
    # Management Reviews
    "ManagementReview", "ReviewAgendaItem", "ReviewAction", "ManagementReviewStatus",
    "ManagementReviewType", "ReviewInputType", "ReviewOutputType", "ActionPriority", "ActionStatus",
    "ManagementReviewInput", "ManagementReviewOutput", "ManagementReviewTemplate", "ManagementReviewKPI",
    # Audit management
    "Audit", "AuditType", "AuditStatus",
    "AuditChecklistTemplate", "AuditChecklistItem", "ChecklistResponse",
    "AuditFinding", "FindingSeverity", "FindingStatus",
    "AuditAttachment",
    # Dashboard/Department
    "Department",
] 