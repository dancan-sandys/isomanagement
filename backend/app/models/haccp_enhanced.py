"""
Enhanced HACCP Data Models with Performance Optimizations and Validation
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, 
    Index, CheckConstraint, UniqueConstraint, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime, timedelta
import json
import logging

from app.core.database import Base
from app.models.enums import HazardType, RiskLevel, CCPStatus

logger = logging.getLogger(__name__)

# Use JSONB for PostgreSQL, JSON for SQLite
JSON_TYPE = JSONB if hasattr(Base.metadata.bind, 'dialect') and Base.metadata.bind.dialect.name == 'postgresql' else JSON


class EnhancedProduct(Base):
    """
    Enhanced Product model with performance optimizations and validation
    """
    __tablename__ = "enhanced_products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100), nullable=False, index=True)
    haccp_plan_approved = Column(Boolean, default=False, index=True)
    haccp_plan_version = Column(String(20))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Enhanced fields for performance
    hazard_count = Column(Integer, default=0, index=True)
    ccp_count = Column(Integer, default=0, index=True)
    last_monitoring_date = Column(DateTime(timezone=True), index=True)
    last_verification_date = Column(DateTime(timezone=True), index=True)
    risk_score_summary = Column(JSON_TYPE)  # Cached risk calculations
    
    # Relationships
    process_flows = relationship("EnhancedProcessFlow", back_populates="product", cascade="all, delete-orphan")
    hazards = relationship("EnhancedHazard", back_populates="product", cascade="all, delete-orphan")
    ccps = relationship("EnhancedCCP", back_populates="product", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_product_category_approved', 'category', 'haccp_plan_approved'),
        Index('idx_product_created_at', 'created_at'),
        Index('idx_product_risk_summary', 'risk_score_summary'),
        CheckConstraint('length(product_code) >= 3', name='product_code_min_length'),
        CheckConstraint('length(name) >= 2', name='product_name_min_length'),
    )
    
    @validates('product_code')
    def validate_product_code(self, key, value):
        if not value or len(value.strip()) < 3:
            raise ValueError("Product code must be at least 3 characters long")
        return value.strip().upper()
    
    @validates('name')
    def validate_name(self, key, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("Product name must be at least 2 characters long")
        return value.strip()
    
    @validates('category')
    def validate_category(self, key, value):
        valid_categories = ['Dairy', 'Meat', 'Poultry', 'Seafood', 'Produce', 'Grains', 'Beverages', 'Snacks', 'Other']
        if value not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        return value
    
    def update_risk_summary(self):
        """Update cached risk score summary"""
        try:
            total_risk = sum(h.risk_score or 0 for h in self.hazards)
            avg_risk = total_risk / len(self.hazards) if self.hazards else 0
            high_risk_count = sum(1 for h in self.hazards if h.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL])
            
            self.risk_score_summary = {
                'total_risk': total_risk,
                'average_risk': round(avg_risk, 2),
                'high_risk_count': high_risk_count,
                'total_hazards': len(self.hazards),
                'updated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating risk summary for product {self.id}: {e}")


class EnhancedProcessFlow(Base):
    """
    Enhanced Process Flow model with validation and performance optimizations
    """
    __tablename__ = "enhanced_process_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("enhanced_products.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(200), nullable=False)
    step_description = Column(Text)
    control_measures = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Enhanced fields
    has_hazards = Column(Boolean, default=False, index=True)
    has_ccps = Column(Boolean, default=False, index=True)
    risk_level = Column(SQLEnum(RiskLevel), index=True)
    
    # Relationships
    product = relationship("EnhancedProduct", back_populates="process_flows")
    hazards = relationship("EnhancedHazard", back_populates="process_flow")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_process_flow_product_step', 'product_id', 'step_number'),
        Index('idx_process_flow_risk', 'risk_level'),
        UniqueConstraint('product_id', 'step_number', name='unique_product_step'),
        CheckConstraint('step_number > 0', name='positive_step_number'),
    )
    
    @validates('step_number')
    def validate_step_number(self, key, value):
        if value <= 0:
            raise ValueError("Step number must be positive")
        return value
    
    @validates('step_name')
    def validate_step_name(self, key, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("Step name must be at least 2 characters long")
        return value.strip()


class EnhancedHazard(Base):
    """
    Enhanced Hazard model with comprehensive validation and performance features
    """
    __tablename__ = "enhanced_hazards"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("enhanced_products.id"), nullable=False, index=True)
    process_flow_id = Column(Integer, ForeignKey("enhanced_process_flows.id"), nullable=False, index=True)
    hazard_type = Column(SQLEnum(HazardType), nullable=False, index=True)
    hazard_name = Column(String(200), nullable=False)
    description = Column(Text)
    likelihood = Column(Integer, nullable=False)
    severity = Column(Integer, nullable=False)
    risk_score = Column(Integer, nullable=False, index=True)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False, index=True)
    control_measures = Column(Text)
    is_ccp = Column(Boolean, default=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Enhanced fields for decision tree and validation
    rationale = Column(Text)
    prp_reference_ids = Column(JSON_TYPE)  # Array of PRP program IDs
    references = Column(JSON_TYPE)  # Array of reference documents
    last_assessment_date = Column(DateTime(timezone=True), index=True)
    next_assessment_date = Column(DateTime(timezone=True), index=True)
    assessment_frequency_days = Column(Integer, default=365)
    
    # Relationships
    product = relationship("EnhancedProduct", back_populates="hazards")
    process_flow = relationship("EnhancedProcessFlow", back_populates="hazards")
    ccps = relationship("EnhancedCCP", back_populates="hazard")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_hazard_product_type', 'product_id', 'hazard_type'),
        Index('idx_hazard_risk_level', 'risk_level'),
        Index('idx_hazard_is_ccp', 'is_ccp'),
        Index('idx_hazard_assessment_dates', 'last_assessment_date', 'next_assessment_date'),
        CheckConstraint('likelihood >= 1 AND likelihood <= 5', name='valid_likelihood'),
        CheckConstraint('severity >= 1 AND severity <= 5', name='valid_severity'),
        CheckConstraint('risk_score >= 1 AND risk_score <= 25', name='valid_risk_score'),
        CheckConstraint('assessment_frequency_days >= 30', name='min_assessment_frequency'),
    )
    
    @validates('likelihood')
    def validate_likelihood(self, key, value):
        if not (1 <= value <= 5):
            raise ValueError("Likelihood must be between 1 and 5")
        return value
    
    @validates('severity')
    def validate_severity(self, key, value):
        if not (1 <= value <= 5):
            raise ValueError("Severity must be between 1 and 5")
        return value
    
    @validates('risk_score')
    def validate_risk_score(self, key, value):
        if not (1 <= value <= 25):
            raise ValueError("Risk score must be between 1 and 25")
        return value
    
    def calculate_risk_score(self):
        """Calculate risk score based on likelihood and severity"""
        return self.likelihood * self.severity
    
    def determine_risk_level(self):
        """Determine risk level based on score"""
        if self.risk_score <= 4:
            return RiskLevel.LOW
        elif self.risk_score <= 8:
            return RiskLevel.MEDIUM
        elif self.risk_score <= 15:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def update_assessment_dates(self):
        """Update assessment dates based on frequency"""
        self.last_assessment_date = datetime.utcnow()
        self.next_assessment_date = self.last_assessment_date + timedelta(days=self.assessment_frequency_days)


class EnhancedCCP(Base):
    """
    Enhanced CCP model with comprehensive monitoring and validation features
    """
    __tablename__ = "enhanced_ccps"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("enhanced_products.id"), nullable=False, index=True)
    hazard_id = Column(Integer, ForeignKey("enhanced_hazards.id"), nullable=False, index=True)
    ccp_number = Column(String(20), nullable=False)
    ccp_name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(CCPStatus), default=CCPStatus.ACTIVE, index=True)
    
    # Critical limits with enhanced validation
    critical_limit_min = Column(Float)
    critical_limit_max = Column(Float)
    critical_limit_unit = Column(String(50))
    critical_limit_description = Column(Text)
    critical_limits = Column(JSON_TYPE)  # Multiple critical limits
    
    # Monitoring configuration
    monitoring_frequency = Column(String(50), nullable=False)
    monitoring_method = Column(Text, nullable=False)
    monitoring_responsible = Column(String(200))
    monitoring_equipment = Column(String(200))
    
    # Corrective actions
    corrective_actions = Column(Text, nullable=False)
    
    # Verification configuration
    verification_frequency = Column(String(50))
    verification_method = Column(Text)
    verification_responsible = Column(String(200))
    
    # Record keeping
    monitoring_records = Column(Text)
    verification_records = Column(Text)
    
    # Enhanced fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Performance tracking
    last_monitoring_date = Column(DateTime(timezone=True), index=True)
    next_monitoring_date = Column(DateTime(timezone=True), index=True)
    last_verification_date = Column(DateTime(timezone=True), index=True)
    next_verification_date = Column(DateTime(timezone=True), index=True)
    deviation_count = Column(Integer, default=0, index=True)
    compliance_rate = Column(Float, default=100.0, index=True)
    
    # Relationships
    product = relationship("EnhancedProduct", back_populates="ccps")
    hazard = relationship("EnhancedHazard", back_populates="ccps")
    monitoring_logs = relationship("EnhancedCCPMonitoringLog", back_populates="ccp", cascade="all, delete-orphan")
    verification_logs = relationship("EnhancedCCPVerificationLog", back_populates="ccp", cascade="all, delete-orphan")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_ccp_product_hazard', 'product_id', 'hazard_id'),
        Index('idx_ccp_status', 'status'),
        Index('idx_ccp_monitoring_dates', 'last_monitoring_date', 'next_monitoring_date'),
        Index('idx_ccp_verification_dates', 'last_verification_date', 'next_verification_date'),
        Index('idx_ccp_compliance', 'compliance_rate'),
        UniqueConstraint('product_id', 'ccp_number', name='unique_product_ccp_number'),
        CheckConstraint('critical_limit_min IS NULL OR critical_limit_max IS NULL OR critical_limit_min <= critical_limit_max', 
                       name='valid_critical_limits'),
        CheckConstraint('compliance_rate >= 0 AND compliance_rate <= 100', name='valid_compliance_rate'),
    )
    
    @validates('ccp_number')
    def validate_ccp_number(self, key, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("CCP number must be at least 2 characters long")
        return value.strip().upper()
    
    @validates('ccp_name')
    def validate_ccp_name(self, key, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("CCP name must be at least 2 characters long")
        return value.strip()
    
    @validates('monitoring_frequency')
    def validate_monitoring_frequency(self, key, value):
        valid_frequencies = ['hourly', 'daily', 'weekly', 'monthly', 'quarterly', 'annually']
        if value not in valid_frequencies:
            raise ValueError(f"Monitoring frequency must be one of: {valid_frequencies}")
        return value
    
    def update_compliance_rate(self):
        """Update compliance rate based on monitoring logs"""
        try:
            total_logs = len(self.monitoring_logs)
            if total_logs == 0:
                self.compliance_rate = 100.0
                return
            
            compliant_logs = sum(1 for log in self.monitoring_logs if log.is_within_limits)
            self.compliance_rate = (compliant_logs / total_logs) * 100
        except Exception as e:
            logger.error(f"Error updating compliance rate for CCP {self.id}: {e}")


class EnhancedCCPMonitoringLog(Base):
    """
    Enhanced CCP Monitoring Log with comprehensive validation and performance features
    """
    __tablename__ = "enhanced_ccp_monitoring_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ccp_id = Column(Integer, ForeignKey("enhanced_ccps.id"), nullable=False, index=True)
    monitoring_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    monitored_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), index=True)
    
    # Monitoring values
    parameter_name = Column(String(100), nullable=False)
    measured_value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    is_within_limits = Column(Boolean, nullable=False, index=True)
    
    # Enhanced fields
    batch_number = Column(String(100), index=True)
    lot_number = Column(String(100), index=True)
    shift = Column(String(50))
    notes = Column(Text)
    attachments = Column(JSON_TYPE)  # Array of document IDs
    
    # Performance tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    ccp = relationship("EnhancedCCP", back_populates="monitoring_logs")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_monitoring_ccp_timestamp', 'ccp_id', 'monitoring_timestamp'),
        Index('idx_monitoring_within_limits', 'is_within_limits'),
        Index('idx_monitoring_batch_lot', 'batch_number', 'lot_number'),
        CheckConstraint('measured_value >= 0', name='positive_measured_value'),
    )
    
    @validates('measured_value')
    def validate_measured_value(self, key, value):
        if value < 0:
            raise ValueError("Measured value cannot be negative")
        return value
    
    @validates('parameter_name')
    def validate_parameter_name(self, key, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("Parameter name must be at least 2 characters long")
        return value.strip()


class EnhancedCCPVerificationLog(Base):
    """
    Enhanced CCP Verification Log with comprehensive validation
    """
    __tablename__ = "enhanced_ccp_verification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ccp_id = Column(Integer, ForeignKey("enhanced_ccps.id"), nullable=False, index=True)
    verification_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Verification details
    verification_type = Column(String(100), nullable=False)
    verification_method = Column(Text, nullable=False)
    verification_result = Column(String(50), nullable=False, index=True)
    findings = Column(Text)
    recommendations = Column(Text)
    
    # Enhanced fields
    attachments = Column(JSON_TYPE)  # Array of document IDs
    next_verification_date = Column(DateTime(timezone=True), index=True)
    
    # Performance tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    ccp = relationship("EnhancedCCP", back_populates="verification_logs")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_verification_ccp_timestamp', 'ccp_id', 'verification_timestamp'),
        Index('idx_verification_result', 'verification_result'),
        Index('idx_verification_type', 'verification_type'),
    )
    
    @validates('verification_result')
    def validate_verification_result(self, key, value):
        valid_results = ['pass', 'fail', 'conditional_pass', 'requires_action']
        if value not in valid_results:
            raise ValueError(f"Verification result must be one of: {valid_results}")
        return value
