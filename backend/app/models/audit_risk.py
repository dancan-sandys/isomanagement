from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum,
    DateTime,
    ForeignKey,
    Boolean,
    Float,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AuditRiskAssessmentType(str, enum.Enum):
    AUDIT = "audit"
    FINDING = "finding"
    PROGRAM = "program"


class AuditRiskReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_ACTION = "needs_action"


class AuditRiskReviewType(str, enum.Enum):
    PERIODIC = "periodic"
    INCIDENT = "incident"
    CHANGE = "change"
    MANAGEMENT = "management"


class AuditRiskReviewOutcome(str, enum.Enum):
    ACCEPTABLE = "acceptable"
    UNACCEPTABLE = "unacceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"


class AuditRiskMonitoringType(str, enum.Enum):
    ROUTINE = "routine"
    PERIODIC = "periodic"
    INCIDENT = "incident"


class AuditRiskMonitoringResult(str, enum.Enum):
    ACCEPTABLE = "acceptable"
    UNACCEPTABLE = "unacceptable"
    MARGINAL = "marginal"


class AuditRiskIntegrationType(str, enum.Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    RELATED = "related"


class AuditElementType(str, enum.Enum):
    AUDIT = "audit"
    FINDING = "finding"
    PROGRAM = "program"


class AuditRiskAssessment(Base):
    __tablename__ = "audit_risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)
    audit_finding_id = Column(Integer, ForeignKey("audit_findings.id"), nullable=True)
    assessment_type = Column(Enum(AuditRiskAssessmentType), nullable=False)
    assessment_method = Column(String(100), nullable=False)
    assessment_date = Column(DateTime(timezone=True), nullable=False)
    assessor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_date = Column(DateTime(timezone=True), nullable=True)
    review_status = Column(Enum(AuditRiskReviewStatus), default=AuditRiskReviewStatus.PENDING)
    
    # Risk assessment details
    initial_risk_score = Column(Integer, nullable=False)
    initial_risk_level = Column(String(50), nullable=False)
    control_effectiveness = Column(Integer, nullable=True)  # 1-5 scale
    residual_risk_score = Column(Integer, nullable=True)
    residual_risk_level = Column(String(50), nullable=True)
    risk_acceptable = Column(Boolean, nullable=True)
    risk_justification = Column(Text, nullable=True)
    
    # Control measures
    control_measures = Column(Text, nullable=True)
    control_verification = Column(Text, nullable=True)
    control_monitoring = Column(Text, nullable=True)
    
    # Treatment and monitoring
    treatment_plan = Column(Text, nullable=True)
    monitoring_frequency = Column(String(100), nullable=True)
    review_frequency = Column(String(100), nullable=True)
    next_monitoring_date = Column(DateTime(timezone=True), nullable=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    audit = relationship("Audit", foreign_keys=[audit_id])
    audit_finding = relationship("AuditFinding", foreign_keys=[audit_finding_id])
    assessor = relationship("User", foreign_keys=[assessor_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    monitoring_records = relationship("AuditRiskMonitoring", back_populates="assessment", cascade="all, delete-orphan")
    reviews = relationship("AuditRiskReview", back_populates="assessment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AuditRiskAssessment(id={self.id}, type='{self.assessment_type}', date='{self.assessment_date}')>"


class AuditRiskIntegration(Base):
    __tablename__ = "audit_risk_integration"

    id = Column(Integer, primary_key=True, index=True)
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    audit_element_type = Column(Enum(AuditElementType), nullable=False)
    audit_element_id = Column(Integer, nullable=False)
    integration_type = Column(Enum(AuditRiskIntegrationType), nullable=False)
    integration_strength = Column(Integer, nullable=True)  # 1-5 scale
    impact_description = Column(Text, nullable=False)
    compliance_impact = Column(Text, nullable=True)
    operational_impact = Column(Text, nullable=True)
    quality_impact = Column(Text, nullable=True)
    integration_date = Column(DateTime(timezone=True), server_default=func.now())
    integrated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_required = Column(Boolean, default=True)
    review_frequency = Column(String(100), nullable=True)
    last_review_date = Column(DateTime(timezone=True), nullable=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    risk_register_item = relationship("RiskRegisterItem", foreign_keys=[risk_register_item_id])
    integrated_by_user = relationship("User", foreign_keys=[integrated_by])
    
    def __repr__(self):
        return f"<AuditRiskIntegration(id={self.id}, element_type='{self.audit_element_type}', element_id={self.audit_element_id})>"


class AuditRiskMonitoring(Base):
    __tablename__ = "audit_risk_monitoring"

    id = Column(Integer, primary_key=True, index=True)
    audit_risk_assessment_id = Column(Integer, ForeignKey("audit_risk_assessments.id"), nullable=False)
    monitoring_date = Column(DateTime(timezone=True), nullable=False)
    monitor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    monitoring_type = Column(Enum(AuditRiskMonitoringType), nullable=False)
    monitoring_method = Column(String(100), nullable=False)
    monitoring_result = Column(Enum(AuditRiskMonitoringResult), nullable=False)
    risk_score_observed = Column(Integer, nullable=True)
    risk_level_observed = Column(String(50), nullable=True)
    control_effectiveness_observed = Column(Integer, nullable=True)
    deviations_found = Column(Boolean, default=False)
    deviation_description = Column(Text, nullable=True)
    corrective_actions_required = Column(Boolean, default=False)
    corrective_actions = Column(Text, nullable=True)
    preventive_actions = Column(Text, nullable=True)
    next_monitoring_date = Column(DateTime(timezone=True), nullable=True)
    comments = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assessment = relationship("AuditRiskAssessment", back_populates="monitoring_records")
    monitor = relationship("User", foreign_keys=[monitor_id])
    
    def __repr__(self):
        return f"<AuditRiskMonitoring(id={self.id}, assessment_id={self.audit_risk_assessment_id}, date='{self.monitoring_date}')>"


class AuditRiskReview(Base):
    __tablename__ = "audit_risk_reviews"

    id = Column(Integer, primary_key=True, index=True)
    audit_risk_assessment_id = Column(Integer, ForeignKey("audit_risk_assessments.id"), nullable=False)
    review_date = Column(DateTime(timezone=True), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_type = Column(Enum(AuditRiskReviewType), nullable=False)
    review_status = Column(Enum(AuditRiskReviewStatus), nullable=False)
    review_outcome = Column(Enum(AuditRiskReviewOutcome), nullable=True)
    risk_score_reviewed = Column(Integer, nullable=True)
    risk_level_reviewed = Column(String(50), nullable=True)
    control_effectiveness_reviewed = Column(Integer, nullable=True)
    changes_identified = Column(Boolean, default=False)
    changes_description = Column(Text, nullable=True)
    actions_required = Column(Boolean, default=False)
    actions_description = Column(Text, nullable=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    review_comments = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assessment = relationship("AuditRiskAssessment", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    
    def __repr__(self):
        return f"<AuditRiskReview(id={self.id}, assessment_id={self.audit_risk_assessment_id}, type='{self.review_type}')>"


class PRPAuditIntegration(Base):
    __tablename__ = "prp_audit_integration"

    id = Column(Integer, primary_key=True, index=True)
    prp_program_id = Column(Integer, ForeignKey("prp_programs.id"), nullable=False)
    audit_finding_id = Column(Integer, ForeignKey("audit_findings.id"), nullable=False)
    integration_type = Column(Enum(AuditRiskIntegrationType), nullable=False)
    integration_strength = Column(Integer, nullable=True)  # 1-5 scale
    impact_description = Column(Text, nullable=False)
    prp_impact = Column(Text, nullable=True)
    audit_impact = Column(Text, nullable=True)
    compliance_impact = Column(Text, nullable=True)
    integration_date = Column(DateTime(timezone=True), server_default=func.now())
    integrated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_required = Column(Boolean, default=True)
    review_frequency = Column(String(100), nullable=True)
    last_review_date = Column(DateTime(timezone=True), nullable=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    prp_program = relationship("PRPProgram", foreign_keys=[prp_program_id])
    audit_finding = relationship("AuditFinding", foreign_keys=[audit_finding_id])
    integrated_by_user = relationship("User", foreign_keys=[integrated_by])
    
    def __repr__(self):
        return f"<PRPAuditIntegration(id={self.id}, prp_id={self.prp_program_id}, finding_id={self.audit_finding_id})>"
