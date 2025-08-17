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


class CorrelationType(str, enum.Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    CASCADING = "cascading"
    AMPLIFYING = "amplifying"


class CorrelationDirection(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    BIDIRECTIONAL = "bidirectional"


class ResourceType(str, enum.Enum):
    PERSONNEL = "personnel"
    FINANCIAL = "financial"
    EQUIPMENT = "equipment"
    TIME = "time"


class AggregationType(str, enum.Enum):
    CATEGORY = "category"
    PROCESS = "process"
    DEPARTMENT = "department"
    PROJECT = "project"


class AnalysisType(str, enum.Enum):
    SCENARIO = "scenario"
    SENSITIVITY = "sensitivity"
    STRESS_TEST = "stress_test"
    WHAT_IF = "what_if"


class PortfolioType(str, enum.Enum):
    BUSINESS_UNIT = "business_unit"
    PROJECT = "project"
    PRODUCT = "product"
    SERVICE = "service"


class RiskCorrelation(Base):
    __tablename__ = "risk_correlations"

    id = Column(Integer, primary_key=True, index=True)
    primary_risk_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    correlated_risk_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    correlation_type = Column(Enum(CorrelationType), nullable=False)
    correlation_strength = Column(Integer, nullable=False)  # 1-5 scale
    correlation_direction = Column(Enum(CorrelationDirection), nullable=False)
    correlation_description = Column(Text, nullable=False)
    impact_analysis = Column(Text, nullable=True)
    mitigation_strategy = Column(Text, nullable=True)
    monitoring_required = Column(Boolean, default=True)
    review_frequency = Column(String(100), nullable=True)
    last_review_date = Column(DateTime(timezone=True), nullable=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    identified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    identified_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    primary_risk = relationship("RiskRegisterItem", foreign_keys=[primary_risk_id])
    correlated_risk = relationship("RiskRegisterItem", foreign_keys=[correlated_risk_id])
    identified_by_user = relationship("User", foreign_keys=[identified_by])
    
    def __repr__(self):
        return f"<RiskCorrelation(id={self.id}, primary_risk={self.primary_risk_id}, correlated_risk={self.correlated_risk_id})>"


class RiskResourceAllocation(Base):
    __tablename__ = "risk_resource_allocation"

    id = Column(Integer, primary_key=True, index=True)
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    resource_type = Column(Enum(ResourceType), nullable=False)
    resource_name = Column(String(200), nullable=False)
    resource_description = Column(Text, nullable=True)
    allocation_amount = Column(Float, nullable=False)
    allocation_unit = Column(String(50), nullable=True)  # hours, dollars, percentage, etc.
    allocation_priority = Column(Integer, nullable=False)  # 1-5 scale
    allocation_justification = Column(Text, nullable=False)
    allocation_start_date = Column(DateTime(timezone=True), nullable=True)
    allocation_end_date = Column(DateTime(timezone=True), nullable=True)
    allocation_status = Column(String(20), nullable=False, default='planned')  # planned, active, completed, cancelled
    actual_usage = Column(Float, nullable=True)
    effectiveness_rating = Column(Integer, nullable=True)  # 1-5 scale
    cost_benefit_analysis = Column(Text, nullable=True)
    allocated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    allocation_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    risk_register_item = relationship("RiskRegisterItem", foreign_keys=[risk_register_item_id])
    allocated_by_user = relationship("User", foreign_keys=[allocated_by])
    
    def __repr__(self):
        return f"<RiskResourceAllocation(id={self.id}, risk_id={self.risk_register_item_id}, resource='{self.resource_name}')>"


class RiskAggregation(Base):
    __tablename__ = "risk_aggregations"

    id = Column(Integer, primary_key=True, index=True)
    aggregation_name = Column(String(200), nullable=False)
    aggregation_description = Column(Text, nullable=True)
    aggregation_type = Column(Enum(AggregationType), nullable=False)
    aggregation_criteria = Column(JSON, nullable=True)  # JSON criteria for aggregation
    aggregated_risk_score = Column(Integer, nullable=True)
    aggregated_risk_level = Column(String(50), nullable=True)
    aggregation_frequency = Column(String(100), nullable=True)
    last_aggregation_date = Column(DateTime(timezone=True), nullable=True)
    next_aggregation_date = Column(DateTime(timezone=True), nullable=True)
    aggregation_status = Column(String(20), nullable=False, default='active')  # active, inactive, archived
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    aggregation_items = relationship("RiskAggregationItem", back_populates="aggregation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RiskAggregation(id={self.id}, name='{self.aggregation_name}', type='{self.aggregation_type}')>"


class RiskAggregationItem(Base):
    __tablename__ = "risk_aggregation_items"

    id = Column(Integer, primary_key=True, index=True)
    aggregation_id = Column(Integer, ForeignKey("risk_aggregations.id"), nullable=False)
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    weight_factor = Column(Float, nullable=True, default=1.0)  # Weight in aggregation calculation
    inclusion_reason = Column(Text, nullable=True)
    added_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    aggregation = relationship("RiskAggregation", back_populates="aggregation_items")
    risk_register_item = relationship("RiskRegisterItem", foreign_keys=[risk_register_item_id])
    
    def __repr__(self):
        return f"<RiskAggregationItem(id={self.id}, aggregation_id={self.aggregation_id}, risk_id={self.risk_register_item_id})>"


class RiskStrategicAnalysis(Base):
    __tablename__ = "risk_strategic_analysis"

    id = Column(Integer, primary_key=True, index=True)
    analysis_name = Column(String(200), nullable=False)
    analysis_description = Column(Text, nullable=True)
    analysis_type = Column(Enum(AnalysisType), nullable=False)
    analysis_scope = Column(JSON, nullable=True)  # JSON scope definition
    analysis_parameters = Column(JSON, nullable=True)  # JSON parameters for analysis
    analysis_results = Column(JSON, nullable=True)  # JSON results
    key_findings = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    analysis_date = Column(DateTime(timezone=True), nullable=False)
    next_analysis_date = Column(DateTime(timezone=True), nullable=True)
    analysis_status = Column(String(20), nullable=False, default='completed')  # planned, in_progress, completed, reviewed
    conducted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conducted_by_user = relationship("User", foreign_keys=[conducted_by])
    reviewed_by_user = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<RiskStrategicAnalysis(id={self.id}, name='{self.analysis_name}', type='{self.analysis_type}')>"


class RiskPortfolio(Base):
    __tablename__ = "risk_portfolios"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_name = Column(String(200), nullable=False)
    portfolio_description = Column(Text, nullable=True)
    portfolio_type = Column(Enum(PortfolioType), nullable=False)
    portfolio_owner = Column(Integer, ForeignKey("users.id"), nullable=True)
    portfolio_risk_appetite = Column(JSON, nullable=True)  # JSON risk appetite definition
    portfolio_risk_tolerance = Column(JSON, nullable=True)  # JSON risk tolerance levels
    portfolio_risk_capacity = Column(JSON, nullable=True)  # JSON risk capacity limits
    portfolio_risk_score = Column(Integer, nullable=True)
    portfolio_risk_level = Column(String(50), nullable=True)
    portfolio_status = Column(String(20), nullable=False, default='active')  # active, inactive, archived
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    portfolio_owner_user = relationship("User", foreign_keys=[portfolio_owner])
    created_by_user = relationship("User", foreign_keys=[created_by])
    portfolio_items = relationship("RiskPortfolioItem", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RiskPortfolio(id={self.id}, name='{self.portfolio_name}', type='{self.portfolio_type}')>"


class RiskPortfolioItem(Base):
    __tablename__ = "risk_portfolio_items"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("risk_portfolios.id"), nullable=False)
    risk_register_item_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    allocation_percentage = Column(Float, nullable=True)  # Percentage allocation in portfolio
    contribution_to_portfolio_risk = Column(Float, nullable=True)  # Risk contribution factor
    diversification_benefit = Column(Float, nullable=True)  # Diversification benefit factor
    added_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    portfolio = relationship("RiskPortfolio", back_populates="portfolio_items")
    risk_register_item = relationship("RiskRegisterItem", foreign_keys=[risk_register_item_id])
    
    def __repr__(self):
        return f"<RiskPortfolioItem(id={self.id}, portfolio_id={self.portfolio_id}, risk_id={self.risk_register_item_id})>"

