from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class NonConformanceSource(str, enum.Enum):
    PRP = "prp"
    AUDIT = "audit"
    COMPLAINT = "complaint"
    PRODUCTION_DEVIATION = "production_deviation"
    SUPPLIER = "supplier"
    HACCP = "haccp"
    DOCUMENT = "document"
    OTHER = "other"


class NonConformanceStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    ROOT_CAUSE_IDENTIFIED = "root_cause_identified"
    CAPA_ASSIGNED = "capa_assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CLOSED = "closed"


class CAPAStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CLOSED = "closed"
    OVERDUE = "overdue"


class RootCauseMethod(str, enum.Enum):
    FIVE_WHYS = "five_whys"
    ISHIKAWA = "ishikawa"
    FISHBONE = "fishbone"
    FAULT_TREE = "fault_tree"
    OTHER = "other"


class NonConformance(Base):
    __tablename__ = "non_conformances"

    id = Column(Integer, primary_key=True, index=True)
    nc_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(Enum(NonConformanceSource), nullable=False)
    
    # Reference information
    batch_reference = Column(String(100))
    product_reference = Column(String(100))
    process_reference = Column(String(100))
    location = Column(String(200))
    
    # Classification
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    impact_area = Column(String(100))  # food safety, quality, regulatory, customer
    category = Column(String(100))
    
    # Status and dates
    status = Column(Enum(NonConformanceStatus), nullable=False, default=NonConformanceStatus.OPEN)
    reported_date = Column(DateTime(timezone=True), nullable=False)
    target_resolution_date = Column(DateTime(timezone=True))
    actual_resolution_date = Column(DateTime(timezone=True))
    
    # Assignment
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    assigned_date = Column(DateTime(timezone=True))
    
    # Evidence and attachments
    evidence_files = Column(JSON)  # JSON array of file paths
    attachments = Column(JSON)  # JSON array of attachment information
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # New NC/CAPA fields
    requires_immediate_action = Column(Boolean, default=False)
    risk_level = Column(String(20))  # low, medium, high, critical
    escalation_status = Column(String(20))  # none, pending, escalated, resolved
    
    # Relationships
    capa_actions = relationship("CAPAAction", back_populates="non_conformance")
    root_cause_analyses = relationship("RootCauseAnalysis", back_populates="non_conformance")
    verifications = relationship("CAPAVerification", back_populates="non_conformance")
    
    # New NC/CAPA relationships
    immediate_actions = relationship("ImmediateAction", back_populates="non_conformance")
    risk_assessments = relationship("NonConformanceRiskAssessment", back_populates="non_conformance")
    preventive_actions = relationship("PreventiveAction", back_populates="non_conformance")
    effectiveness_monitoring = relationship("EffectivenessMonitoring", back_populates="non_conformance")
    
    def __repr__(self):
        return f"<NonConformance(id={self.id}, nc_number='{self.nc_number}', title='{self.title}')>"


class RootCauseAnalysis(Base):
    __tablename__ = "root_cause_analyses"

    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    
    # Analysis details
    method = Column(Enum(RootCauseMethod), nullable=False)
    analysis_date = Column(DateTime(timezone=True), nullable=False)
    conducted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Analysis results
    immediate_cause = Column(Text)
    underlying_cause = Column(Text)
    root_cause = Column(Text)
    
    # 5 Whys analysis
    why_1 = Column(Text)
    why_2 = Column(Text)
    why_3 = Column(Text)
    why_4 = Column(Text)
    why_5 = Column(Text)
    
    # Ishikawa/Fishbone analysis
    fishbone_categories = Column(JSON)  # JSON object with categories and factors
    fishbone_diagram_data = Column(JSON)  # JSON object with diagram structure
    
    # Contributing factors
    contributing_factors = Column(Text)  # JSON array of contributing factors
    system_failures = Column(Text)  # JSON array of system failures
    
    # Recommendations
    recommendations = Column(Text)  # JSON array of recommendations
    preventive_measures = Column(Text)  # JSON array of preventive measures
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    non_conformance = relationship("NonConformance", back_populates="root_cause_analyses")
    
    def __repr__(self):
        # Avoid accessing potentially expired attributes (detached instances)
        try:
            rid = object.__getattribute__(self, 'id')
        except Exception:
            rid = None
        return f"<RootCauseAnalysis(id={rid})>"


class CAPAAction(Base):
    __tablename__ = "capa_actions"

    id = Column(Integer, primary_key=True, index=True)
    capa_number = Column(String(50), unique=True, index=True, nullable=False)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    
    # CAPA details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    action_type = Column(String(50))  # corrective, preventive, both
    
    # Assignment
    responsible_person = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_date = Column(DateTime(timezone=True), nullable=False)
    target_completion_date = Column(DateTime(timezone=True), nullable=False)
    actual_completion_date = Column(DateTime(timezone=True))
    
    # Status and progress
    status = Column(Enum(CAPAStatus), nullable=False, default=CAPAStatus.PENDING)
    progress_percentage = Column(Float, default=0.0)
    
    # Resources and budget
    required_resources = Column(Text)  # JSON array of resources
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    
    # Implementation details
    implementation_plan = Column(Text)
    milestones = Column(JSON)  # JSON array of milestones
    deliverables = Column(Text)  # JSON array of deliverables
    
    # Effectiveness
    effectiveness_criteria = Column(Text)  # JSON array of effectiveness criteria
    effectiveness_measured = Column(Boolean, default=False)
    effectiveness_score = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    non_conformance = relationship("NonConformance", back_populates="capa_actions")
    verifications = relationship("CAPAVerification", back_populates="capa_action")
    
    def __repr__(self):
        return f"<CAPAAction(id={self.id}, capa_number='{self.capa_number}', title='{self.title}')>"


class CAPAVerification(Base):
    __tablename__ = "capa_verifications"

    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    capa_action_id = Column(Integer, ForeignKey("capa_actions.id"), nullable=False)
    
    # Verification details
    verification_date = Column(DateTime(timezone=True), nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Verification criteria
    verification_criteria = Column(Text)  # JSON array of verification criteria
    verification_method = Column(String(100))
    verification_evidence = Column(Text)  # JSON array of evidence
    
    # Results
    verification_result = Column(String(20))  # passed, failed, conditional
    effectiveness_score = Column(Float)
    comments = Column(Text)
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_actions = Column(Text)  # JSON array of follow-up actions
    next_verification_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    non_conformance = relationship("NonConformance", back_populates="verifications")
    capa_action = relationship("CAPAAction", back_populates="verifications")
    
    def __repr__(self):
        return f"<CAPAVerification(id={self.id}, non_conformance_id={self.non_conformance_id}, capa_action_id={self.capa_action_id})>"


class NonConformanceAttachment(Base):
    __tablename__ = "non_conformance_attachments"

    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    
    # File information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(100))
    original_filename = Column(String(255))
    
    # Attachment details
    attachment_type = Column(String(50))  # evidence, document, photo, video, etc.
    description = Column(Text)
    
    # Upload information
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    non_conformance = relationship("NonConformance")
    
    def __repr__(self):
        return f"<NonConformanceAttachment(id={self.id}, non_conformance_id={self.non_conformance_id}, file_name='{self.file_name}')>"


# New NC/CAPA Models

class ImmediateAction(Base):
    __tablename__ = "immediate_actions"

    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    
    # Action details
    action_type = Column(String(50), nullable=False)  # containment, isolation, emergency_response, notification
    description = Column(Text, nullable=False)
    
    # Implementation
    implemented_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    implemented_at = Column(DateTime(timezone=True), nullable=False)
    
    # Verification
    effectiveness_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    verification_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    non_conformance = relationship("NonConformance", back_populates="immediate_actions")
    
    def __repr__(self):
        return f"<ImmediateAction(id={self.id}, action_type='{self.action_type}', non_conformance_id={self.non_conformance_id})>"
    
    def verify_effectiveness(self, verified_by: int, verification_date: DateTime = None):
        """Verify the effectiveness of the immediate action."""
        self.effectiveness_verified = True
        self.verification_by = verified_by
        self.verification_date = verification_date or func.now()
    
    def is_verified(self) -> bool:
        """Check if the immediate action has been verified."""
        return self.effectiveness_verified


class NonConformanceRiskAssessment(Base):
    __tablename__ = "nonconformance_risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    
    # Risk impact assessments
    food_safety_impact = Column(String(20), nullable=False)  # low, medium, high, critical
    regulatory_impact = Column(String(20), nullable=False)  # low, medium, high, critical
    customer_impact = Column(String(20), nullable=False)  # low, medium, high, critical
    business_impact = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # Risk scoring
    overall_risk_score = Column(Float, nullable=False)
    risk_matrix_position = Column(String(10), nullable=False)  # e.g., "A1", "B2", "C3"
    requires_escalation = Column(Boolean, default=False)
    escalation_level = Column(String(20))  # supervisor, manager, director, executive
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    non_conformance = relationship("NonConformance", back_populates="risk_assessments")
    
    def __repr__(self):
        return f"<NonConformanceRiskAssessment(id={self.id}, overall_risk_score={self.overall_risk_score}, requires_escalation={self.requires_escalation})>"
    
    def calculate_risk_score(self) -> float:
        """Calculate the overall risk score based on impact assessments."""
        impact_scores = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        food_safety = impact_scores.get(self.food_safety_impact.lower(), 1)
        regulatory = impact_scores.get(self.regulatory_impact.lower(), 1)
        customer = impact_scores.get(self.customer_impact.lower(), 1)
        business = impact_scores.get(self.business_impact.lower(), 1)
        
        # Weighted average (food safety and regulatory have higher weights)
        self.overall_risk_score = (food_safety * 0.4 + regulatory * 0.3 + customer * 0.2 + business * 0.1)
        return self.overall_risk_score
    
    def determine_escalation_need(self) -> bool:
        """Determine if escalation is required based on risk score."""
        self.requires_escalation = self.overall_risk_score >= 3.0
        return self.requires_escalation
    
    def get_risk_level(self) -> str:
        """Get the risk level based on the overall risk score."""
        if self.overall_risk_score >= 3.5:
            return "critical"
        elif self.overall_risk_score >= 2.5:
            return "high"
        elif self.overall_risk_score >= 1.5:
            return "medium"
        else:
            return "low"


class EscalationRule(Base):
    __tablename__ = "escalation_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Rule configuration
    rule_name = Column(String(100), nullable=False)
    rule_description = Column(Text)
    trigger_condition = Column(String(50), nullable=False)  # risk_score, time_delay, severity_level
    trigger_value = Column(Float, nullable=False)
    escalation_level = Column(String(20), nullable=False)  # supervisor, manager, director, executive
    notification_recipients = Column(Text)  # JSON array of user IDs or email addresses
    escalation_timeframe = Column(Integer)  # hours
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    def __repr__(self):
        return f"<EscalationRule(id={self.id}, rule_name='{self.rule_name}', trigger_condition='{self.trigger_condition}')>"
    
    def should_trigger(self, value: float) -> bool:
        """Check if the rule should trigger based on the given value."""
        if not self.is_active:
            return False
        
        if self.trigger_condition == "risk_score":
            return value >= self.trigger_value
        elif self.trigger_condition == "time_delay":
            return value >= self.trigger_value
        elif self.trigger_condition == "severity_level":
            severity_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            return severity_scores.get(str(value).lower(), 0) >= self.trigger_value
        
        return False
    
    def get_notification_recipients(self) -> list:
        """Get the list of notification recipients."""
        import json
        try:
            return json.loads(self.notification_recipients) if self.notification_recipients else []
        except (json.JSONDecodeError, TypeError):
            return []


class PreventiveAction(Base):
    __tablename__ = "preventive_actions"

    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    
    # Action details
    action_title = Column(String(200), nullable=False)
    action_description = Column(Text, nullable=False)
    action_type = Column(String(50), nullable=False)  # process_improvement, training, equipment_upgrade, procedure_update
    priority = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False)  # planned, in_progress, completed, cancelled
    completion_date = Column(DateTime(timezone=True))
    
    # Effectiveness
    effectiveness_target = Column(Float)  # percentage target for effectiveness
    effectiveness_measured = Column(Float)  # actual effectiveness percentage
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    non_conformance = relationship("NonConformance", back_populates="preventive_actions")
    
    def __repr__(self):
        return f"<PreventiveAction(id={self.id}, action_title='{self.action_title}', status='{self.status}')>"
    
    def is_overdue(self) -> bool:
        """Check if the preventive action is overdue."""
        from datetime import datetime
        return self.status not in ['completed', 'cancelled'] and self.due_date < datetime.now()
    
    def calculate_effectiveness(self) -> float:
        """Calculate the effectiveness percentage."""
        if self.effectiveness_target and self.effectiveness_measured:
            return (self.effectiveness_measured / self.effectiveness_target) * 100
        return 0.0
    
    def is_effective(self) -> bool:
        """Check if the preventive action is effective (meets target)."""
        return self.calculate_effectiveness() >= 100.0


class EffectivenessMonitoring(Base):
    __tablename__ = "effectiveness_monitoring"

    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    
    # Monitoring period
    monitoring_period_start = Column(DateTime(timezone=True), nullable=False)
    monitoring_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Metric details
    metric_name = Column(String(100), nullable=False)
    metric_description = Column(Text)
    target_value = Column(Float, nullable=False)
    actual_value = Column(Float)
    measurement_unit = Column(String(20))  # percentage, count, days, etc.
    measurement_frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly
    measurement_method = Column(Text)  # how the measurement is taken
    
    # Status and results
    status = Column(String(20), nullable=False)  # active, completed, suspended
    achievement_percentage = Column(Float)  # calculated field
    trend_analysis = Column(Text)  # JSON data for trend analysis
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    non_conformance = relationship("NonConformance", back_populates="effectiveness_monitoring")
    
    def __repr__(self):
        return f"<EffectivenessMonitoring(id={self.id}, metric_name='{self.metric_name}', status='{self.status}')>"
    
    def calculate_achievement_percentage(self) -> float:
        """Calculate the achievement percentage."""
        if self.target_value and self.actual_value is not None:
            self.achievement_percentage = (self.actual_value / self.target_value) * 100
            return self.achievement_percentage
        return 0.0
    
    def is_on_target(self) -> bool:
        """Check if the monitoring is on target."""
        return self.achievement_percentage >= 100.0 if self.achievement_percentage else False
    
    def is_active_monitoring(self) -> bool:
        """Check if the monitoring is currently active."""
        from datetime import datetime
        now = datetime.now()
        return (self.status == "active" and 
                self.monitoring_period_start <= now <= self.monitoring_period_end) 

# Backwards-compatibility aliases used by tests and existing code
# Some tests expect a generic name 'RiskAssessment' under nonconformance module
RiskAssessment = NonConformanceRiskAssessment