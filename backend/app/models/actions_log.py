# -*- coding: utf-8 -*-
"""
Actions Log System Models
Phase 3: Comprehensive action tracking from various sources
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum


class ActionStatus(str, Enum):
    """Action status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    OVERDUE = "overdue"


class ActionPriority(str, Enum):
    """Action priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class ActionSource(str, Enum):
    """Sources of actions"""
    INTERESTED_PARTY = "interested_party"
    SWOT_ANALYSIS = "swot_analysis"
    PESTEL_ANALYSIS = "pestel_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    AUDIT_FINDING = "audit_finding"
    NON_CONFORMANCE = "non_conformance"
    MANAGEMENT_REVIEW = "management_review"
    COMPLAINT = "complaint"
    REGULATORY = "regulatory"
    STRATEGIC_PLANNING = "strategic_planning"
    CONTINUOUS_IMPROVEMENT = "continuous_improvement"


class PartyCategory(str, Enum):
    """Interested party categories"""
    CUSTOMERS = "customers"
    SUPPLIERS = "suppliers"
    EMPLOYEES = "employees"
    REGULATORS = "regulators"
    SHAREHOLDERS = "shareholders"
    COMMUNITY = "community"
    COMPETITORS = "competitors"
    PARTNERS = "partners"
    MEDIA = "media"
    FINANCIAL_INSTITUTIONS = "financial_institutions"


class SWOTCategory(str, Enum):
    """SWOT analysis categories"""
    STRENGTHS = "strengths"
    WEAKNESSES = "weaknesses"
    OPPORTUNITIES = "opportunities"
    THREATS = "threats"


class PESTELCategory(str, Enum):
    """PESTEL analysis categories"""
    POLITICAL = "political"
    ECONOMIC = "economic"
    SOCIAL = "social"
    TECHNOLOGICAL = "technological"
    ENVIRONMENTAL = "environmental"
    LEGAL = "legal"


class ActionLog(Base):
    """Main actions log table"""
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    action_source = Column(String(50), nullable=False, index=True)
    source_id = Column(Integer, nullable=True, index=True)  # ID of the source record
    # Direct linkage to a Risk item so risk module can natively use actions log
    risk_id = Column(Integer, nullable=True, index=True)  # Temporarily removed FK constraint until risk_register table exists
    status = Column(String(20), default=ActionStatus.PENDING, index=True)
    priority = Column(String(20), default=ActionPriority.MEDIUM, index=True)
    
    # Assignment and responsibility
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    
    # Timeline
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    progress_percent = Column(Float, default=0.0)
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    
    # Additional metadata
    tags = Column(Text, nullable=True)  # For flexible tagging (stored as JSON string)
    attachments = Column(Text, nullable=True)  # File attachments (stored as JSON string)
    notes = Column(Text, nullable=True)
    
    # Relationships
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_actions")
    created_by_user = relationship("User", foreign_keys=[assigned_by], back_populates="created_actions")
    department = relationship("Department", back_populates="actions")
    progress_updates = relationship("ActionProgress", back_populates="action", cascade="all, delete-orphan")
    related_actions = relationship("ActionRelationship", foreign_keys="ActionRelationship.action_id", back_populates="action")


class ActionProgress(Base):
    """Action progress tracking"""
    __tablename__ = "action_progress"

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("action_logs.id"), nullable=False, index=True)
    update_type = Column(String(50), nullable=False)  # status_change, progress_update, note, etc.
    description = Column(Text, nullable=False)
    progress_percent = Column(Float, nullable=True)
    hours_spent = Column(Float, nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    action = relationship("ActionLog", back_populates="progress_updates")
    user = relationship("User", back_populates="action_progress_updates")


class ActionRelationship(Base):
    """Relationships between actions"""
    __tablename__ = "action_relationships"

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("action_logs.id"), nullable=False, index=True)
    related_action_id = Column(Integer, ForeignKey("action_logs.id"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False)  # blocks, depends_on, related_to, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    action = relationship("ActionLog", foreign_keys=[action_id], back_populates="related_actions")
    related_action = relationship("ActionLog", foreign_keys=[related_action_id])


class InterestedParty(Base):
    """Interested parties table"""
    __tablename__ = "interested_parties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    contact_person = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    
    # Assessment
    satisfaction_level = Column(Integer, nullable=True)  # 1-10 scale
    last_assessment_date = Column(DateTime(timezone=True), nullable=True)
    next_assessment_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    expectations = relationship("PartyExpectation", back_populates="party", cascade="all, delete-orphan")
    actions = relationship("PartyAction", back_populates="party", cascade="all, delete-orphan")


class PartyExpectation(Base):
    """Needs and expectations of interested parties"""
    __tablename__ = "party_expectations"

    id = Column(Integer, primary_key=True, index=True)
    party_id = Column(Integer, ForeignKey("interested_parties.id"), nullable=False, index=True)
    expectation_type = Column(String(100), nullable=False)  # quality, delivery, communication, etc.
    description = Column(Text, nullable=False)
    importance_level = Column(Integer, nullable=False)  # 1-10 scale
    current_satisfaction = Column(Integer, nullable=True)  # 1-10 scale
    target_satisfaction = Column(Integer, nullable=False)  # 1-10 scale
    
    # Assessment
    assessment_date = Column(DateTime(timezone=True), nullable=True)
    assessment_notes = Column(Text, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    party = relationship("InterestedParty", back_populates="expectations")
    actions = relationship("PartyAction", back_populates="expectation", cascade="all, delete-orphan")


class PartyAction(Base):
    """Actions to address party expectations"""
    __tablename__ = "party_actions"

    id = Column(Integer, primary_key=True, index=True)
    party_id = Column(Integer, ForeignKey("interested_parties.id"), nullable=False, index=True)
    expectation_id = Column(Integer, ForeignKey("party_expectations.id"), nullable=True, index=True)
    action_log_id = Column(Integer, ForeignKey("action_logs.id"), nullable=False, index=True)
    
    # Action details
    action_type = Column(String(100), nullable=False)  # improve, maintain, address_concern, etc.
    description = Column(Text, nullable=False)
    expected_impact = Column(Text, nullable=True)
    success_metrics = Column(Text, nullable=True)
    
    # Assessment
    impact_assessment = Column(Text, nullable=True)
    satisfaction_improvement = Column(Integer, nullable=True)  # Improvement in satisfaction score
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    party = relationship("InterestedParty", back_populates="actions")
    expectation = relationship("PartyExpectation", back_populates="actions")
    action_log = relationship("ActionLog")


class SWOTAnalysis(Base):
    """SWOT analysis table"""
    __tablename__ = "swot_analyses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    analysis_date = Column(DateTime(timezone=True), nullable=False, index=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Analysis scope
    scope = Column(String(255), nullable=True)  # department, process, organization, etc.
    context = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default="active", index=True)  # active, archived, draft
    is_current = Column(Boolean, default=False, index=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("SWOTItem", back_populates="analysis", cascade="all, delete-orphan")
    actions = relationship("SWOTAction", back_populates="analysis", cascade="all, delete-orphan")


class SWOTItem(Base):
    """Individual SWOT items"""
    __tablename__ = "swot_items"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("swot_analyses.id"), nullable=False, index=True)
    category = Column(String(20), nullable=False, index=True)  # strengths, weaknesses, opportunities, threats
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Impact assessment
    impact_level = Column(Integer, nullable=False)  # 1-10 scale
    probability = Column(Integer, nullable=True)  # 1-10 scale (for opportunities/threats)
    urgency = Column(Integer, nullable=True)  # 1-10 scale
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_addressed = Column(Boolean, default=False, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analysis = relationship("SWOTAnalysis", back_populates="items")
    actions = relationship("SWOTAction", back_populates="item", cascade="all, delete-orphan")


class SWOTAction(Base):
    """Actions from SWOT analysis"""
    __tablename__ = "swot_actions"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("swot_analyses.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("swot_items.id"), nullable=True, index=True)
    action_log_id = Column(Integer, ForeignKey("action_logs.id"), nullable=False, index=True)
    
    # Action details
    action_type = Column(String(100), nullable=False)  # leverage, mitigate, exploit, avoid, etc.
    description = Column(Text, nullable=False)
    expected_outcome = Column(Text, nullable=True)
    success_criteria = Column(Text, nullable=True)
    
    # Assessment
    effectiveness = Column(Integer, nullable=True)  # 1-10 scale
    assessment_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analysis = relationship("SWOTAnalysis", back_populates="actions")
    item = relationship("SWOTItem", back_populates="actions")
    action_log = relationship("ActionLog")


class PESTELAnalysis(Base):
    """PESTEL analysis table"""
    __tablename__ = "pestel_analyses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    analysis_date = Column(DateTime(timezone=True), nullable=False, index=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Analysis scope
    scope = Column(String(255), nullable=True)  # market, industry, organization, etc.
    context = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default="active", index=True)  # active, archived, draft
    is_current = Column(Boolean, default=False, index=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("PESTELItem", back_populates="analysis", cascade="all, delete-orphan")
    actions = relationship("PESTELAction", back_populates="analysis", cascade="all, delete-orphan")


class PESTELItem(Base):
    """Individual PESTEL items"""
    __tablename__ = "pestel_items"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("pestel_analyses.id"), nullable=False, index=True)
    category = Column(String(20), nullable=False, index=True)  # political, economic, social, technological, environmental, legal
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Impact assessment
    impact_level = Column(Integer, nullable=False)  # 1-10 scale
    probability = Column(Integer, nullable=True)  # 1-10 scale
    timeframe = Column(String(50), nullable=True)  # short_term, medium_term, long_term
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_addressed = Column(Boolean, default=False, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analysis = relationship("PESTELAnalysis", back_populates="items")
    actions = relationship("PESTELAction", back_populates="item", cascade="all, delete-orphan")


class PESTELAction(Base):
    """Actions from PESTEL analysis"""
    __tablename__ = "pestel_actions"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("pestel_analyses.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("pestel_items.id"), nullable=True, index=True)
    action_log_id = Column(Integer, ForeignKey("action_logs.id"), nullable=False, index=True)
    
    # Action details
    action_type = Column(String(100), nullable=False)  # monitor, adapt, influence, prepare, etc.
    description = Column(Text, nullable=False)
    expected_outcome = Column(Text, nullable=True)
    success_criteria = Column(Text, nullable=True)
    
    # Assessment
    effectiveness = Column(Integer, nullable=True)  # 1-10 scale
    assessment_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analysis = relationship("PESTELAnalysis", back_populates="actions")
    item = relationship("PESTELItem", back_populates="actions")
    action_log = relationship("ActionLog")
