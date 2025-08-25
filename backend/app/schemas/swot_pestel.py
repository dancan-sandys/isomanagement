from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SWOTCategory(str, Enum):
    STRENGTHS = "strengths"
    WEAKNESSES = "weaknesses"
    OPPORTUNITIES = "opportunities"
    THREATS = "threats"

class PESTELCategory(str, Enum):
    POLITICAL = "political"
    ECONOMIC = "economic"
    SOCIAL = "social"
    TECHNOLOGICAL = "technological"
    ENVIRONMENTAL = "environmental"
    LEGAL = "legal"

class ImpactLevel(str, Enum):
    """ISO-compliant impact assessment levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class PriorityLevel(str, Enum):
    """ISO-compliant priority levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AnalysisScope(str, Enum):
    """ISO organizational context scope"""
    ORGANIZATION_WIDE = "organization_wide"
    DEPARTMENT = "department"
    PROCESS = "process"
    PROJECT = "project"
    PRODUCT_SERVICE = "product_service"

class ReviewFrequency(str, Enum):
    """ISO-compliant review frequencies"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    AS_NEEDED = "as_needed"

# ISO-Compliant Strategic Context Schema
class StrategicContext(BaseModel):
    """ISO 9001:2015 Clause 4.1 - Understanding the organization and its context"""
    organizational_purpose: str = Field(..., description="Organization's purpose and strategic direction")
    interested_parties: List[str] = Field(default=[], description="Relevant interested parties")
    external_issues: List[str] = Field(default=[], description="External issues affecting the organization")
    internal_issues: List[str] = Field(default=[], description="Internal issues affecting the organization")
    qms_scope: Optional[str] = Field(None, description="Scope of the quality management system")

# SWOT Analysis Schemas
class SWOTAnalysisBase(BaseModel):
    title: str = Field(..., description="Title of the SWOT analysis")
    description: Optional[str] = Field(None, description="Description of the analysis")
    analysis_date: datetime = Field(default_factory=datetime.now, description="Date of analysis")
    is_active: bool = Field(True, description="Whether the analysis is active")
    
    # ISO Compliance Fields
    scope: AnalysisScope = Field(AnalysisScope.ORGANIZATION_WIDE, description="Analysis scope per ISO requirements")
    strategic_context: Optional[StrategicContext] = Field(None, description="Strategic context per ISO 9001:2015 Clause 4.1")
    review_frequency: ReviewFrequency = Field(ReviewFrequency.ANNUALLY, description="Review frequency for continuous monitoring")
    next_review_date: Optional[datetime] = Field(None, description="Next scheduled review date")
    iso_clause_reference: List[str] = Field(default=["4.1"], description="Relevant ISO clause references")
    compliance_notes: Optional[str] = Field(None, description="ISO compliance notes and observations")
    
    # Risk Integration
    risk_assessment_id: Optional[int] = Field(None, description="Associated risk assessment ID")
    risk_factors_identified: int = Field(0, description="Number of risk factors identified")
    
    # Strategic Alignment
    strategic_objectives_alignment: Optional[Dict[str, Any]] = Field(None, description="Alignment with strategic objectives")
    kpi_impact_assessment: Optional[Dict[str, Any]] = Field(None, description="Impact on key performance indicators")

class SWOTAnalysisCreate(SWOTAnalysisBase):
    pass

class SWOTAnalysisUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    analysis_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class SWOTAnalysisResponse(SWOTAnalysisBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    strengths_count: int = 0
    weaknesses_count: int = 0
    opportunities_count: int = 0
    threats_count: int = 0
    actions_generated: int = 0
    completed_actions: int = 0

    class Config:
        from_attributes = True

# SWOT Item Schemas
class SWOTItemBase(BaseModel):
    category: SWOTCategory = Field(..., description="SWOT category")
    title: str = Field(..., description="Title of the SWOT item")
    description: str = Field(..., description="Description of the item")
    impact_level: ImpactLevel = Field(..., description="Impact level assessment")
    priority: PriorityLevel = Field(..., description="Priority level for action")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    # ISO Compliance Enhancement
    probability_score: Optional[int] = Field(None, ge=1, le=10, description="Probability score (1-10) for opportunities/threats")
    urgency_score: Optional[int] = Field(None, ge=1, le=10, description="Urgency score (1-10)")
    strategic_relevance: Optional[str] = Field(None, description="Strategic relevance to organizational objectives")
    iso_context_factor: Optional[str] = Field(None, description="Internal/external context factor per ISO 4.1")
    
    # Risk Integration
    associated_risks: List[str] = Field(default=[], description="Associated risks identified")
    mitigation_strategies: List[str] = Field(default=[], description="Mitigation strategies")
    
    # Action Tracking
    action_required: bool = Field(False, description="Whether action is required")
    target_completion_date: Optional[datetime] = Field(None, description="Target completion date for actions")
    responsible_party: Optional[str] = Field(None, description="Responsible party for actions")
    
    # Evidence and Documentation
    evidence_sources: List[str] = Field(default=[], description="Sources of evidence supporting this item")
    documentation_references: List[str] = Field(default=[], description="Related documentation references")

class SWOTItemCreate(SWOTItemBase):
    pass

class SWOTItemUpdate(BaseModel):
    category: Optional[SWOTCategory] = None
    description: Optional[str] = None
    impact_level: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None

class SWOTItemResponse(SWOTItemBase):
    id: int
    analysis_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

# PESTEL Analysis Schemas
class PESTELAnalysisBase(BaseModel):
    title: str = Field(..., description="Title of the PESTEL analysis")
    description: Optional[str] = Field(None, description="Description of the analysis")
    analysis_date: datetime = Field(default_factory=datetime.now, description="Date of analysis")
    is_active: bool = Field(True, description="Whether the analysis is active")
    
    # ISO Compliance Fields
    scope: AnalysisScope = Field(AnalysisScope.ORGANIZATION_WIDE, description="Analysis scope per ISO requirements")
    strategic_context: Optional[StrategicContext] = Field(None, description="Strategic context per ISO 9001:2015 Clause 4.1")
    review_frequency: ReviewFrequency = Field(ReviewFrequency.ANNUALLY, description="Review frequency for continuous monitoring")
    next_review_date: Optional[datetime] = Field(None, description="Next scheduled review date")
    iso_clause_reference: List[str] = Field(default=["4.1"], description="Relevant ISO clause references")
    compliance_notes: Optional[str] = Field(None, description="ISO compliance notes and observations")
    
    # External Environment Focus
    market_analysis: Optional[Dict[str, Any]] = Field(None, description="Market environment analysis")
    regulatory_landscape: Optional[Dict[str, Any]] = Field(None, description="Regulatory environment assessment")
    stakeholder_impact: Optional[Dict[str, Any]] = Field(None, description="Impact on stakeholders")
    
    # Risk Integration
    risk_assessment_id: Optional[int] = Field(None, description="Associated risk assessment ID")
    external_risk_factors: int = Field(0, description="Number of external risk factors identified")
    
    # Strategic Alignment
    strategic_objectives_alignment: Optional[Dict[str, Any]] = Field(None, description="Alignment with strategic objectives")
    competitive_advantage_analysis: Optional[Dict[str, Any]] = Field(None, description="Competitive advantage analysis")

class PESTELAnalysisCreate(PESTELAnalysisBase):
    pass

class PESTELAnalysisUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    analysis_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class PESTELAnalysisResponse(PESTELAnalysisBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    political_count: int = 0
    economic_count: int = 0
    social_count: int = 0
    technological_count: int = 0
    environmental_count: int = 0
    legal_count: int = 0
    actions_generated: int = 0
    completed_actions: int = 0

    class Config:
        from_attributes = True

# PESTEL Item Schemas
class PESTELItemBase(BaseModel):
    category: PESTELCategory = Field(..., description="PESTEL category")
    title: str = Field(..., description="Title of the PESTEL item")
    description: str = Field(..., description="Description of the item")
    impact_level: ImpactLevel = Field(..., description="Impact level assessment")
    priority: PriorityLevel = Field(..., description="Priority level for action")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    # ISO Compliance Enhancement
    probability_score: Optional[int] = Field(None, ge=1, le=10, description="Probability score (1-10)")
    timeframe: Optional[str] = Field(None, description="Timeframe for impact (short/medium/long term)")
    external_factor_type: Optional[str] = Field(None, description="Type of external factor per ISO 4.1")
    stakeholder_impact: Optional[str] = Field(None, description="Impact on interested parties")
    
    # Regulatory Compliance
    regulatory_requirements: List[str] = Field(default=[], description="Related regulatory requirements")
    compliance_implications: Optional[str] = Field(None, description="Compliance implications")
    
    # Risk Integration
    associated_risks: List[str] = Field(default=[], description="Associated external risks")
    monitoring_indicators: List[str] = Field(default=[], description="Key indicators to monitor")
    
    # Action Planning
    action_required: bool = Field(False, description="Whether action is required")
    adaptation_strategies: List[str] = Field(default=[], description="Strategies to adapt to this factor")
    contingency_plans: List[str] = Field(default=[], description="Contingency plans")
    
    # Evidence and Documentation
    data_sources: List[str] = Field(default=[], description="Data sources for this analysis")
    expert_opinions: List[str] = Field(default=[], description="Expert opinions consulted")
    last_updated: Optional[datetime] = Field(None, description="Last update date for this factor")

class PESTELItemCreate(PESTELItemBase):
    pass

class PESTELItemUpdate(BaseModel):
    category: Optional[PESTELCategory] = None
    description: Optional[str] = None
    impact_level: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None

class PESTELItemResponse(PESTELItemBase):
    id: int
    analysis_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

# Analytics Schemas
class SWOTAnalytics(BaseModel):
    total_analyses: int
    active_analyses: int
    total_items: int
    strengths_count: int
    weaknesses_count: int
    opportunities_count: int
    threats_count: int
    actions_generated: int
    completed_actions: int
    completion_rate: float

class PESTELAnalytics(BaseModel):
    total_analyses: int
    active_analyses: int
    total_items: int
    political_count: int
    economic_count: int
    social_count: int
    technological_count: int
    environmental_count: int
    legal_count: int
    actions_generated: int
    completed_actions: int
    completion_rate: float

# ISO-Specific Analytics Schemas
class ISOComplianceMetrics(BaseModel):
    """ISO compliance metrics for SWOT/PESTEL analyses"""
    total_analyses_with_context: int = Field(0, description="Analyses with strategic context defined")
    clause_4_1_compliance_rate: float = Field(0.0, description="Compliance rate with ISO 9001:2015 Clause 4.1")
    overdue_reviews: int = Field(0, description="Number of overdue reviews")
    risk_integration_rate: float = Field(0.0, description="Rate of analyses integrated with risk management")
    strategic_alignment_rate: float = Field(0.0, description="Rate of analyses aligned with strategic objectives")
    documented_evidence_rate: float = Field(0.0, description="Rate of analyses with proper documentation")

class StrategicInsights(BaseModel):
    """Strategic insights from SWOT/PESTEL analyses"""
    critical_strengths: List[str] = Field(default=[], description="Critical organizational strengths")
    major_weaknesses: List[str] = Field(default=[], description="Major organizational weaknesses")
    high_impact_opportunities: List[str] = Field(default=[], description="High-impact opportunities")
    significant_threats: List[str] = Field(default=[], description="Significant external threats")
    key_external_factors: List[str] = Field(default=[], description="Key external environmental factors")
    regulatory_compliance_gaps: List[str] = Field(default=[], description="Identified compliance gaps")
    
class ContinuousImprovementMetrics(BaseModel):
    """Continuous improvement metrics per ISO requirements"""
    actions_from_analyses: int = Field(0, description="Total actions generated from analyses")
    completed_improvement_actions: int = Field(0, description="Completed improvement actions")
    pending_critical_actions: int = Field(0, description="Pending critical actions")
    average_action_completion_time: float = Field(0.0, description="Average action completion time in days")
    stakeholder_satisfaction_improvement: float = Field(0.0, description="Stakeholder satisfaction improvement rate")

class ISODashboardMetrics(BaseModel):
    """Comprehensive ISO dashboard metrics"""
    compliance_metrics: ISOComplianceMetrics
    strategic_insights: StrategicInsights
    improvement_metrics: ContinuousImprovementMetrics
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
# ISO Audit and Review Schemas
class ISOAuditFinding(BaseModel):
    """ISO audit findings related to SWOT/PESTEL analyses"""
    finding_id: str = Field(..., description="Unique finding identifier")
    audit_date: datetime = Field(..., description="Date of audit")
    finding_type: str = Field(..., description="Type of finding (observation, minor, major)")
    iso_clause: str = Field(..., description="Related ISO clause")
    description: str = Field(..., description="Finding description")
    corrective_action_required: bool = Field(False, description="Whether corrective action is required")
    responsible_party: str = Field(..., description="Responsible party for resolution")
    target_completion_date: Optional[datetime] = Field(None, description="Target completion date")
    status: str = Field("open", description="Finding status")

class ManagementReviewInput(BaseModel):
    """Management review input from SWOT/PESTEL analyses"""
    review_period_start: datetime = Field(..., description="Review period start date")
    review_period_end: datetime = Field(..., description="Review period end date")
    swot_summary: SWOTAnalytics
    pestel_summary: PESTELAnalytics
    iso_compliance: ISOComplianceMetrics
    strategic_insights: StrategicInsights
    improvement_opportunities: List[str] = Field(default=[], description="Identified improvement opportunities")
    resource_requirements: List[str] = Field(default=[], description="Resource requirements for improvements")
    management_recommendations: List[str] = Field(default=[], description="Recommendations for management")
