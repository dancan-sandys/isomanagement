/**
 * ISO-Compliant SWOT/PESTEL Analysis Types
 * Based on ISO 9001:2015 requirements for organizational context understanding
 */

// Core Enumerations
export enum SWOTCategory {
  STRENGTHS = "strengths",
  WEAKNESSES = "weaknesses", 
  OPPORTUNITIES = "opportunities",
  THREATS = "threats"
}

export enum PESTELCategory {
  POLITICAL = "political",
  ECONOMIC = "economic", 
  SOCIAL = "social",
  TECHNOLOGICAL = "technological",
  ENVIRONMENTAL = "environmental",
  LEGAL = "legal"
}

export enum ImpactLevel {
  VERY_LOW = "very_low",
  LOW = "low",
  MEDIUM = "medium", 
  HIGH = "high",
  VERY_HIGH = "very_high"
}

export enum PriorityLevel {
  VERY_LOW = "very_low",
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high", 
  CRITICAL = "critical"
}

export enum AnalysisScope {
  ORGANIZATION_WIDE = "organization_wide",
  DEPARTMENT = "department",
  PROCESS = "process",
  PROJECT = "project",
  PRODUCT_SERVICE = "product_service"
}

export enum ReviewFrequency {
  MONTHLY = "monthly",
  QUARTERLY = "quarterly",
  SEMI_ANNUALLY = "semi_annually", 
  ANNUALLY = "annually",
  AS_NEEDED = "as_needed"
}

// Strategic Context Interface (ISO 9001:2015 Clause 4.1)
export interface StrategicContext {
  organizational_purpose: string;
  interested_parties: string[];
  external_issues: string[];
  internal_issues: string[];
  qms_scope?: string;
}

// SWOT Analysis Interfaces
export interface SWOTAnalysisBase {
  title: string;
  description?: string;
  analysis_date: string;
  is_active: boolean;
  
  // ISO Compliance Fields
  scope: AnalysisScope;
  strategic_context?: StrategicContext;
  review_frequency: ReviewFrequency;
  next_review_date?: string;
  iso_clause_reference: string[];
  compliance_notes?: string;
  
  // Risk Integration
  risk_assessment_id?: number;
  risk_factors_identified: number;
  
  // Strategic Alignment
  strategic_objectives_alignment?: Record<string, any>;
  kpi_impact_assessment?: Record<string, any>;
}

export interface SWOTAnalysisCreate extends SWOTAnalysisBase {}

export interface SWOTAnalysisUpdate {
  title?: string;
  description?: string;
  analysis_date?: string;
  is_active?: boolean;
  scope?: AnalysisScope;
  strategic_context?: StrategicContext;
  review_frequency?: ReviewFrequency;
  next_review_date?: string;
  iso_clause_reference?: string[];
  compliance_notes?: string;
  risk_assessment_id?: number;
  risk_factors_identified?: number;
  strategic_objectives_alignment?: Record<string, any>;
  kpi_impact_assessment?: Record<string, any>;
}

export interface SWOTAnalysisResponse extends SWOTAnalysisBase {
  id: number;
  created_at: string;
  updated_at?: string;
  created_by?: number;
  strengths_count: number;
  weaknesses_count: number;
  opportunities_count: number;
  threats_count: number;
  actions_generated: number;
  completed_actions: number;
}

// SWOT Item Interfaces
export interface SWOTItemBase {
  category: SWOTCategory;
  title: string;
  description: string;
  impact_level: ImpactLevel;
  priority: PriorityLevel;
  notes?: string;
  
  // ISO Compliance Enhancement
  probability_score?: number; // 1-10 scale
  urgency_score?: number; // 1-10 scale
  strategic_relevance?: string;
  iso_context_factor?: string;
  
  // Risk Integration
  associated_risks: string[];
  mitigation_strategies: string[];
  
  // Action Tracking
  action_required: boolean;
  target_completion_date?: string;
  responsible_party?: string;
  
  // Evidence and Documentation
  evidence_sources: string[];
  documentation_references: string[];
}

export interface SWOTItemCreate extends SWOTItemBase {}

export interface SWOTItemUpdate {
  category?: SWOTCategory;
  title?: string;
  description?: string;
  impact_level?: ImpactLevel;
  priority?: PriorityLevel;
  notes?: string;
  probability_score?: number;
  urgency_score?: number;
  strategic_relevance?: string;
  iso_context_factor?: string;
  associated_risks?: string[];
  mitigation_strategies?: string[];
  action_required?: boolean;
  target_completion_date?: string;
  responsible_party?: string;
  evidence_sources?: string[];
  documentation_references?: string[];
}

export interface SWOTItemResponse extends SWOTItemBase {
  id: number;
  analysis_id: number;
  created_at: string;
  updated_at?: string;
  created_by?: number;
}

// PESTEL Analysis Interfaces
export interface PESTELAnalysisBase {
  title: string;
  description?: string;
  analysis_date: string;
  is_active: boolean;
  
  // ISO Compliance Fields
  scope: AnalysisScope;
  strategic_context?: StrategicContext;
  review_frequency: ReviewFrequency;
  next_review_date?: string;
  iso_clause_reference: string[];
  compliance_notes?: string;
  
  // External Environment Focus
  market_analysis?: Record<string, any>;
  regulatory_landscape?: Record<string, any>;
  stakeholder_impact?: Record<string, any>;
  
  // Risk Integration
  risk_assessment_id?: number;
  external_risk_factors: number;
  
  // Strategic Alignment
  strategic_objectives_alignment?: Record<string, any>;
  competitive_advantage_analysis?: Record<string, any>;
}

export interface PESTELAnalysisCreate extends PESTELAnalysisBase {}

export interface PESTELAnalysisUpdate {
  title?: string;
  description?: string;
  analysis_date?: string;
  is_active?: boolean;
  scope?: AnalysisScope;
  strategic_context?: StrategicContext;
  review_frequency?: ReviewFrequency;
  next_review_date?: string;
  iso_clause_reference?: string[];
  compliance_notes?: string;
  market_analysis?: Record<string, any>;
  regulatory_landscape?: Record<string, any>;
  stakeholder_impact?: Record<string, any>;
  risk_assessment_id?: number;
  external_risk_factors?: number;
  strategic_objectives_alignment?: Record<string, any>;
  competitive_advantage_analysis?: Record<string, any>;
}

export interface PESTELAnalysisResponse extends PESTELAnalysisBase {
  id: number;
  created_at: string;
  updated_at?: string;
  created_by?: number;
  political_count: number;
  economic_count: number;
  social_count: number;
  technological_count: number;
  environmental_count: number;
  legal_count: number;
  actions_generated: number;
  completed_actions: number;
}

// PESTEL Item Interfaces
export interface PESTELItemBase {
  category: PESTELCategory;
  title: string;
  description: string;
  impact_level: ImpactLevel;
  priority: PriorityLevel;
  notes?: string;
  
  // ISO Compliance Enhancement
  probability_score?: number; // 1-10 scale
  timeframe?: string; // short/medium/long term
  external_factor_type?: string;
  stakeholder_impact?: string;
  
  // Regulatory Compliance
  regulatory_requirements: string[];
  compliance_implications?: string;
  
  // Risk Integration
  associated_risks: string[];
  monitoring_indicators: string[];
  
  // Action Planning
  action_required: boolean;
  adaptation_strategies: string[];
  contingency_plans: string[];
  
  // Evidence and Documentation
  data_sources: string[];
  expert_opinions: string[];
  last_updated?: string;
}

export interface PESTELItemCreate extends PESTELItemBase {}

export interface PESTELItemUpdate {
  category?: PESTELCategory;
  title?: string;
  description?: string;
  impact_level?: ImpactLevel;
  priority?: PriorityLevel;
  notes?: string;
  probability_score?: number;
  timeframe?: string;
  external_factor_type?: string;
  stakeholder_impact?: string;
  regulatory_requirements?: string[];
  compliance_implications?: string;
  associated_risks?: string[];
  monitoring_indicators?: string[];
  action_required?: boolean;
  adaptation_strategies?: string[];
  contingency_plans?: string[];
  data_sources?: string[];
  expert_opinions?: string[];
  last_updated?: string;
}

export interface PESTELItemResponse extends PESTELItemBase {
  id: number;
  analysis_id: number;
  created_at: string;
  updated_at?: string;
  created_by?: number;
}

// Analytics Interfaces
export interface SWOTAnalytics {
  total_analyses: number;
  active_analyses: number;
  total_items: number;
  strengths_count: number;
  weaknesses_count: number;
  opportunities_count: number;
  threats_count: number;
  actions_generated: number;
  completed_actions: number;
  completion_rate: number;
}

export interface PESTELAnalytics {
  total_analyses: number;
  active_analyses: number;
  total_items: number;
  political_count: number;
  economic_count: number;
  social_count: number;
  technological_count: number;
  environmental_count: number;
  legal_count: number;
  actions_generated: number;
  completed_actions: number;
  completion_rate: number;
}

// ISO-Specific Analytics
export interface ISOComplianceMetrics {
  total_analyses_with_context: number;
  clause_4_1_compliance_rate: number;
  overdue_reviews: number;
  risk_integration_rate: number;
  strategic_alignment_rate: number;
  documented_evidence_rate: number;
}

export interface StrategicInsights {
  critical_strengths: string[];
  major_weaknesses: string[];
  high_impact_opportunities: string[];
  significant_threats: string[];
  key_external_factors: string[];
  regulatory_compliance_gaps: string[];
}

export interface ContinuousImprovementMetrics {
  actions_from_analyses: number;
  completed_improvement_actions: number;
  pending_critical_actions: number;
  average_action_completion_time: number;
  stakeholder_satisfaction_improvement: number;
}

export interface ISODashboardMetrics {
  compliance_metrics: ISOComplianceMetrics;
  strategic_insights: StrategicInsights;
  improvement_metrics: ContinuousImprovementMetrics;
  last_updated: string;
}

// ISO Audit and Review Interfaces
export interface ISOAuditFinding {
  finding_id: string;
  audit_date: string;
  finding_type: string; // observation, minor, major
  iso_clause: string;
  description: string;
  corrective_action_required: boolean;
  responsible_party: string;
  target_completion_date?: string;
  status: string;
}

export interface ManagementReviewInput {
  review_period_start: string;
  review_period_end: string;
  swot_summary: SWOTAnalytics;
  pestel_summary: PESTELAnalytics;
  iso_compliance: ISOComplianceMetrics;
  strategic_insights: StrategicInsights;
  improvement_opportunities: string[];
  resource_requirements: string[];
  management_recommendations: string[];
}

// Risk Integration Interfaces
export interface RiskFactor {
  item_id: number;
  category: string;
  description: string;
  impact_level: ImpactLevel;
  associated_risks: string[];
  mitigation_strategies?: string[];
  adaptation_strategies?: string[];
  monitoring_indicators?: string[];
}

export interface RiskSummary {
  total_risk_factors?: number;
  total_external_risks?: number;
  risk_factors?: RiskFactor[];
  external_risk_factors?: RiskFactor[];
  risk_summary: Record<string, number>;
}

// ISO Review Results
export interface ISOReviewResult {
  analysis_id: number;
  review_date: string;
  compliance_score: number;
  compliance_level: string; // "Fully Compliant" | "Mostly Compliant" | "Partially Compliant" | "Non-Compliant"
  findings: string[];
  recommendations: string[];
}

// Strategic Context Assessment
export interface StrategicContextAssessment {
  total_analyses: number;
  analyses_with_context: number;
  analyses_with_scope_defined: number;
  analyses_with_review_schedule: number;
  swot_analyses: {
    total: number;
    with_strategic_context: number;
    with_iso_references: number;
    organization_wide_scope: number;
  };
  pestel_analyses: {
    total: number;
    with_strategic_context: number;
    with_iso_references: number;
    organization_wide_scope: number;
  };
  compliance_recommendations: string[];
}

// Continuous Monitoring Dashboard
export interface MonitoringDashboard {
  last_updated: string;
  swot_status: SWOTAnalytics;
  pestel_status: PESTELAnalytics;
  iso_compliance: ISOComplianceMetrics;
  clause_4_1_assessment: any; // Would be more specific based on actual API response
  review_status: {
    overdue_reviews: number;
    upcoming_reviews: number;
    overdue_swot: number;
    overdue_pestel: number;
    upcoming_swot: number;
    upcoming_pestel: number;
  };
}

// API Response Wrappers
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  success: boolean;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}