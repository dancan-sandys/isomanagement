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


class HACCPRiskAssessmentType(str, enum.Enum):
    HAZARD = "hazard"
    CCP = "ccp"
    PRP = "prp"


class HACCPRiskReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_ACTION = "needs_action"


class HACCPRiskReviewType(str, enum.Enum):
    PERIODIC = "periodic"
    INCIDENT = "incident"
    CHANGE = "change"
    MANAGEMENT = "management"


class HACCPRiskReviewOutcome(str, enum.Enum):
    ACCEPTABLE = "acceptable"
    UNACCEPTABLE = "unacceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"


class HACCPRiskMonitoringType(str, enum.Enum):
    ROUTINE = "routine"
    PERIODIC = "periodic"
    INCIDENT = "incident"


class HACCPRiskMonitoringResult(str, enum.Enum):
    ACCEPTABLE = "acceptable"
    UNACCEPTABLE = "unacceptable"
    MARGINAL = "marginal"


class HACCPRiskIntegrationType(str, enum.Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    RELATED = "related"


class HACCPElementType(str, enum.Enum):
    HAZARD = "hazard"
    CCP = "ccp"
    PRP = "prp"
    PROCESS = "process"
    PRODUCT = "product"


class HACCPRiskAssessment(Base):
    __tablename__ = "haccp_risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    hazard_id = Column(Integer, ForeignKey("hazards.id"), nullable=False)
    ccp_id = Column(Integer, ForeignKey("ccps.id"), nullable=True)
    prp_program_id = Column(Integer, ForeignKey("prp_programs.id"), nullable=True)
    assessment_type = Column(Enum(HACCPRiskAssessmentType), nullable=False)
    assessment_method = Column(String(100), nullable=False)
    assessment_date = Column(DateTime(timezone=True), nullable=False)
    assessor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_date = Column(DateTime(timezone=True), nullable=True)
    review_status = Column(Enum(HACCPRiskReviewStatus), default=HACCPRiskReviewStatus.PENDING)
    
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
    hazard = relationship("Hazard", foreign_keys=[hazard_id])
    ccp = relationship("CCP", foreign_keys=[ccp_id])
    prp_program = relationship("PRPProgram", foreign_keys=[prp_program_id])
    assessor = relationship("User", foreign_keys=[assessor_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    monitoring_records = relationship("HACCPRiskMonitoring", back_populates="assessment", cascade="all, delete-orphan")
    reviews = relationship("HACCPRiskReview", back_populates="assessment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<HACCPRiskAssessment(id={self.id}, type='{self.assessment_type}', date='{self.assessment_date}')>"


class HACCPRiskIntegration(Base):
    __tablename__ = "haccp_risk_integration"

    id = Column(Integer, primary_key=True, index=True)
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    haccp_element_type = Column(Enum(HACCPElementType), nullable=False)
    haccp_element_id = Column(Integer, nullable=False)
    integration_type = Column(Enum(HACCPRiskIntegrationType), nullable=False)
    integration_strength = Column(Integer, nullable=True)  # 1-5 scale
    impact_description = Column(Text, nullable=False)
    food_safety_impact = Column(Text, nullable=True)
    compliance_impact = Column(Text, nullable=True)
    operational_impact = Column(Text, nullable=True)
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
        return f"<HACCPRiskIntegration(id={self.id}, element_type='{self.haccp_element_type}', element_id={self.haccp_element_id})>"


class HACCPRiskMonitoring(Base):
    __tablename__ = "haccp_risk_monitoring"

    id = Column(Integer, primary_key=True, index=True)
    haccp_risk_assessment_id = Column(Integer, ForeignKey("haccp_risk_assessments.id"), nullable=False)
    monitoring_date = Column(DateTime(timezone=True), nullable=False)
    monitor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    monitoring_type = Column(Enum(HACCPRiskMonitoringType), nullable=False)
    monitoring_method = Column(String(100), nullable=False)
    monitoring_result = Column(Enum(HACCPRiskMonitoringResult), nullable=False)
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
    assessment = relationship("HACCPRiskAssessment", back_populates="monitoring_records")
    monitor = relationship("User", foreign_keys=[monitor_id])
    
    def __repr__(self):
        return f"<HACCPRiskMonitoring(id={self.id}, assessment_id={self.haccp_risk_assessment_id}, date='{self.monitoring_date}')>"


class HACCPRiskReview(Base):
    __tablename__ = "haccp_risk_reviews"

    id = Column(Integer, primary_key=True, index=True)
    haccp_risk_assessment_id = Column(Integer, ForeignKey("haccp_risk_assessments.id"), nullable=False)
    review_date = Column(DateTime(timezone=True), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_type = Column(Enum(HACCPRiskReviewType), nullable=False)
    review_status = Column(Enum(HACCPRiskReviewStatus), nullable=False)
    review_outcome = Column(Enum(HACCPRiskReviewOutcome), nullable=True)
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
    assessment = relationship("HACCPRiskAssessment", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    
    def __repr__(self):
        return f"<HACCPRiskReview(id={self.id}, assessment_id={self.haccp_risk_assessment_id}, type='{self.review_type}')>"
