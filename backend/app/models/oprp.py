"""
OPRP (Operational Prerequisites) Model for HACCP System
Based on ISO 22000:2018 requirements for operational prerequisite programs
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, 
    Index, CheckConstraint, UniqueConstraint, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import json
import logging

from app.core.database import Base

logger = logging.getLogger(__name__)


class OPRPStatus:
    """OPRP Status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_REVIEW = "under_review"
    SUSPENDED = "suspended"


class OPRP(Base):
    """
    Operational Prerequisites (OPRP) Model
    OPRPs are operational prerequisite programs that control significant food safety hazards
    but are not critical control points (CCPs)
    """
    __tablename__ = "oprps"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    hazard_id = Column(Integer, ForeignKey("hazards.id"), nullable=False, index=True)
    oprp_number = Column(String(20), nullable=False)
    oprp_name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default=OPRPStatus.ACTIVE, index=True)
    
    # Operational limits - similar to CCP but for operational control
    operational_limits = Column(JSON)  # JSON array of limit objects
    # Example structure:
    # [
    #   {
    #     "parameter": "temperature",
    #     "min_value": 2.0,
    #     "max_value": 8.0,
    #     "unit": "Cel",
    #     "condition": "during_storage",
    #     "limit_type": "numeric"
    #   },
    #   {
    #     "parameter": "visual_inspection",
    #     "value": "no_visible_contamination",
    #     "unit": null,
    #     "condition": "before_processing",
    #     "limit_type": "qualitative"
    #   }
    # ]
    
    # Legacy fields for backward compatibility
    operational_limit_min = Column(Float)
    operational_limit_max = Column(Float)
    operational_limit_unit = Column(String(50))
    operational_limit_description = Column(Text)
    
    # Monitoring configuration
    monitoring_frequency = Column(String(100))  # e.g., "Every 4 hours"
    monitoring_method = Column(Text)
    monitoring_responsible = Column(Integer, ForeignKey("users.id"))
    monitoring_equipment = Column(String(100))
    
    # Corrective actions
    corrective_actions = Column(Text)
    
    # Verification
    verification_frequency = Column(String(100))
    verification_method = Column(Text)
    verification_responsible = Column(Integer, ForeignKey("users.id"))
    
    # Documentation
    monitoring_records = Column(Text)  # JSON array of record types
    verification_records = Column(Text)  # JSON array of record types
    
    # OPRP-specific fields
    justification = Column(Text)  # Why this is an OPRP and not a CCP
    objective = Column(Text)  # Objective of the OPRP
    sop_reference = Column(Text)  # Reference to Standard Operating Procedure document
    effectiveness_validation = Column(Text)  # Evidence of effectiveness
    validation_evidence = Column(JSON)  # JSON array of evidence references
    
    # Risk integration fields
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=True)
    risk_assessment_method = Column(String(100), nullable=True)
    risk_assessment_date = Column(DateTime(timezone=True), nullable=True)
    risk_assessor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    risk_treatment_plan = Column(Text, nullable=True)
    risk_monitoring_frequency = Column(String(100), nullable=True)
    risk_review_frequency = Column(String(100), nullable=True)
    risk_control_effectiveness = Column(Integer, nullable=True)
    risk_residual_score = Column(Integer, nullable=True)
    risk_residual_level = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="oprps")
    hazard = relationship("Hazard", back_populates="oprps")
    monitoring_logs = relationship("OPRPMonitoringLog", back_populates="oprp")
    verification_logs = relationship("OPRPVerificationLog", back_populates="oprp")
    monitoring_schedule = relationship("OPRPMonitoringSchedule", back_populates="oprp", uselist=False, cascade="all, delete-orphan")
    verification_programs = relationship("OPRPVerificationProgram", back_populates="oprp", cascade="all, delete-orphan")
    validations = relationship("OPRPValidation", back_populates="oprp", cascade="all, delete-orphan")
    risk_register_item = relationship("RiskRegisterItem", foreign_keys=[risk_register_item_id])
    risk_assessor = relationship("User", foreign_keys=[risk_assessor_id])
    
    # Indexes and constraints
    __table_args__ = (
        Index('ix_oprps_product_hazard', 'product_id', 'hazard_id'),
        Index('ix_oprps_status_created', 'status', 'created_at'),
        UniqueConstraint('product_id', 'oprp_number', name='uq_oprp_product_number'),
        CheckConstraint("status IN ('active', 'inactive', 'under_review', 'suspended')", name='ck_oprp_status'),
    )
    
    def validate_limits(self, measured_values: dict) -> dict:
        """
        Validate measured values against operational limits
        Returns: dict with validation results for each parameter
        """
        if not self.operational_limits:
            return {"error": "No operational limits defined"}
        
        results = {}
        for limit in self.operational_limits:
            parameter = limit.get("parameter")
            limit_type = limit.get("limit_type", "numeric")
            
            if parameter not in measured_values:
                results[parameter] = {"valid": False, "error": "Parameter not measured"}
                continue
            
            measured_value = measured_values[parameter]
            
            if limit_type == "numeric":
                min_val = limit.get("min_value")
                max_val = limit.get("max_value")
                
                if min_val is not None and measured_value < min_val:
                    results[parameter] = {"valid": False, "error": f"Below minimum ({min_val})"}
                elif max_val is not None and measured_value > max_val:
                    results[parameter] = {"valid": False, "error": f"Above maximum ({max_val})"}
                else:
                    results[parameter] = {"valid": True}
                    
            elif limit_type == "qualitative":
                expected_value = limit.get("value")
                if measured_value != expected_value:
                    results[parameter] = {"valid": False, "error": f"Expected {expected_value}, got {measured_value}"}
                else:
                    results[parameter] = {"valid": True}
        
        return results
    
    def __repr__(self):
        return f"<OPRP(id={self.id}, product_id={self.product_id}, oprp_number='{self.oprp_number}', name='{self.oprp_name}')>"


class OPRPMonitoringLog(Base):
    """
    OPRP Monitoring Log - Records of operational limit monitoring
    """
    __tablename__ = "oprp_monitoring_logs"

    id = Column(Integer, primary_key=True, index=True)
    oprp_id = Column(Integer, ForeignKey("oprps.id", ondelete="CASCADE"), nullable=False)
    batch_number = Column(String(50), nullable=True)
    measured_values = Column(JSON)  # JSON object with parameter: value pairs
    measured_at = Column(DateTime(timezone=True), nullable=False)
    measured_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    equipment_used = Column(String(100), nullable=True)
    comments = Column(Text)
    
    # Validation results
    validation_results = Column(JSON)  # Results from validate_limits()
    is_within_limits = Column(Boolean, nullable=False)
    corrective_actions_taken = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    oprp = relationship("OPRP", back_populates="monitoring_logs")
    measured_by_user = relationship("User", foreign_keys=[measured_by])
    
    # Indexes
    __table_args__ = (
        Index('ix_oprp_monitoring_logs_oprp_measured', 'oprp_id', 'measured_at'),
        Index('ix_oprp_monitoring_logs_batch', 'batch_number'),
    )


class OPRPVerificationLog(Base):
    """
    OPRP Verification Log - Records of OPRP verification activities
    """
    __tablename__ = "oprp_verification_logs"

    id = Column(Integer, primary_key=True, index=True)
    oprp_id = Column(Integer, ForeignKey("oprps.id", ondelete="CASCADE"), nullable=False)
    verification_type = Column(String(50), nullable=False)  # calibration, review, audit, etc.
    verification_date = Column(DateTime(timezone=True), nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    findings = Column(Text)
    corrective_actions = Column(Text)
    next_verification_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    oprp = relationship("OPRP", back_populates="verification_logs")
    verified_by_user = relationship("User", foreign_keys=[verified_by])
    
    # Indexes
    __table_args__ = (
        Index('ix_oprp_verification_logs_oprp_date', 'oprp_id', 'verification_date'),
    )


class OPRPMonitoringSchedule(Base):
    """
    OPRP Monitoring Schedule - Defines when and how OPRP monitoring should occur
    """
    __tablename__ = "oprp_monitoring_schedules"

    id = Column(Integer, primary_key=True, index=True)
    oprp_id = Column(Integer, ForeignKey("oprps.id", ondelete="CASCADE"), nullable=False, unique=True)
    frequency_type = Column(String(20), nullable=False)  # hourly, daily, weekly, monthly, etc.
    frequency_value = Column(Integer, nullable=False)  # e.g., 4 for "every 4 hours"
    start_time = Column(String(10), nullable=True)  # e.g., "08:00" for 8 AM start
    end_time = Column(String(10), nullable=True)  # e.g., "17:00" for 5 PM end
    days_of_week = Column(String(20), nullable=True)  # e.g., "1,2,3,4,5" for Mon-Fri
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    oprp = relationship("OPRP", back_populates="monitoring_schedule")


class OPRPVerificationProgram(Base):
    """
    OPRP Verification Program - Defines verification activities for OPRPs
    """
    __tablename__ = "oprp_verification_programs"

    id = Column(Integer, primary_key=True, index=True)
    oprp_id = Column(Integer, ForeignKey("oprps.id", ondelete="CASCADE"), nullable=False)
    program_name = Column(String(100), nullable=False)
    program_type = Column(String(50), nullable=False)  # calibration, review, audit, testing, etc.
    frequency_type = Column(String(20), nullable=False)
    frequency_value = Column(Integer, nullable=False)
    responsible_person = Column(Integer, ForeignKey("users.id"), nullable=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    oprp = relationship("OPRP", back_populates="verification_programs")
    responsible_user = relationship("User", foreign_keys=[responsible_person])


class OPRPValidation(Base):
    """
    OPRP Validation - Records of OPRP validation activities
    """
    __tablename__ = "oprp_validations"

    id = Column(Integer, primary_key=True, index=True)
    oprp_id = Column(Integer, ForeignKey("oprps.id", ondelete="CASCADE"), nullable=False)
    validation_type = Column(String(50), nullable=False)  # initial, periodic, after_change
    validation_date = Column(DateTime(timezone=True), nullable=False)
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    validation_method = Column(Text)
    validation_results = Column(Text)
    effectiveness_confirmed = Column(Boolean, nullable=False)
    next_validation_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    oprp = relationship("OPRP", back_populates="validations")
    validated_by_user = relationship("User", foreign_keys=[validated_by])
    
    # Indexes
    __table_args__ = (
        Index('ix_oprp_validations_oprp_date', 'oprp_id', 'validation_date'),
    )
