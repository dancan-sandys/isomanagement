import api from './api';
import { AxiosResponse } from 'axios';

export interface RiskListParams {
  page?: number;
  size?: number;
  search?: string;
  item_type?: 'risk' | 'opportunity';
  category?: string;
  classification?: 'food_safety' | 'business' | 'customer';
  status?: string;
  severity?: string;
  likelihood?: string;
  detectability?: 'easily_detectable' | 'moderately_detectable' | 'difficult' | 'very_difficult' | 'almost_undetectable';
  assigned_to?: number;
  date_from?: string;
  date_to?: string;
}

// ISO 31000:2018 Risk Management Framework Interface
export interface RiskFramework {
  id?: number;
  policy_statement: string;
  risk_appetite_statement: string;
  risk_tolerance_levels: Record<string, any>;
  risk_criteria: Record<string, any>;
  risk_assessment_methodology: string;
  risk_treatment_strategies: Record<string, any>;
  monitoring_review_frequency: string;
  communication_plan: string;
  review_cycle: string;
  next_review_date?: string;
  approved_by?: number;
  approved_at?: string;
}

// ISO 31000:2018 Risk Context Interface
export interface RiskContext {
  id?: number;
  organizational_context: string;
  external_context: string;
  internal_context: string;
  risk_management_context: string;
  stakeholder_analysis: Record<string, any>;
  risk_criteria: Record<string, any>;
  review_frequency: string;
  last_review_date?: string;
  next_review_date?: string;
}

// Risk Assessment Data Interface
export interface RiskAssessmentData {
  risk_assessment_method: string;
  severity?: string;
  likelihood?: string;
  detectability?: string;
  impact_score?: number;
  risk_treatment_strategy?: string;
  risk_treatment_plan?: string;
  monitoring_frequency?: string;
  review_frequency?: string;
}

// Risk Treatment Data Interface
export interface RiskTreatmentData {
  risk_treatment_strategy: 'avoid' | 'transfer' | 'mitigate' | 'accept';
  risk_treatment_plan: string;
  risk_treatment_cost?: number;
  risk_treatment_benefit?: number;
  risk_treatment_timeline?: string;
}

export const riskAPI = {
  // ============================================================================
  // EXISTING BASIC RISK OPERATIONS
  // ============================================================================
  list: async (params?: RiskListParams) => {
    const response: AxiosResponse = await api.get('/risk', { params });
    return response.data;
  },
  get: async (id: number) => {
    const response: AxiosResponse = await api.get(`/risk/${id}`);
    return response.data;
  },
  create: async (payload: any) => {
    const response: AxiosResponse = await api.post('/risk', payload);
    return response.data;
  },
  update: async (id: number, payload: any) => {
    const response: AxiosResponse = await api.put(`/risk/${id}`, payload);
    return response.data;
  },
  progress: async (id: number) => {
    const response: AxiosResponse = await api.get(`/risk/${id}/progress`);
    return response.data;
  },
  remove: async (id: number) => {
    const response: AxiosResponse = await api.delete(`/risk/${id}`);
    return response.data;
  },
  stats: async () => {
    const response: AxiosResponse = await api.get('/risk/stats/overview');
    return response.data;
  },

  // ============================================================================
  // ISO 31000:2018 RISK FRAMEWORK OPERATIONS
  // ============================================================================
  
  // Risk Management Framework
  getFramework: async () => {
    const response: AxiosResponse = await api.get('/risk-framework/framework');
    return response.data;
  },
  createFramework: async (frameworkData: Partial<RiskFramework>) => {
    const response: AxiosResponse = await api.post('/risk-framework/framework', frameworkData);
    return response.data;
  },
  getRiskAppetite: async () => {
    const response: AxiosResponse = await api.get('/risk-framework/framework/appetite');
    return response.data;
  },
  getRiskMatrix: async () => {
    const response: AxiosResponse = await api.get('/risk-framework/framework/matrix');
    return response.data;
  },

  // Risk Context Management
  getContext: async () => {
    const response: AxiosResponse = await api.get('/risk-framework/context');
    return response.data;
  },
  createContext: async (contextData: Partial<RiskContext>) => {
    const response: AxiosResponse = await api.post('/risk-framework/context', contextData);
    return response.data;
  },

  // ============================================================================
  // ISO 31000:2018 RISK ASSESSMENT & TREATMENT
  // ============================================================================
  
  // Risk Assessment
  assessRisk: async (riskId: number, assessmentData: RiskAssessmentData) => {
    const response: AxiosResponse = await api.post(`/risk-framework/${riskId}/assess`, assessmentData);
    return response.data;
  },
  
  // Risk Treatment (by id)
  planTreatmentById: async (riskId: number, treatmentData: RiskTreatmentData) => {
    const response: AxiosResponse = await api.post(`/risk-framework/${riskId}/treat`, treatmentData);
    return response.data;
  },
  approveTreatment: async (riskId: number, approvalNotes?: string) => {
    const response: AxiosResponse = await api.post(`/risk-framework/${riskId}/treat/approve`, {
      approval_notes: approvalNotes
    });
    return response.data;
  },
  
  // Monitoring & Review
  scheduleMonitoring: async (riskId: number, monitoringData: any) => {
    const response: AxiosResponse = await api.post(`/risk-framework/${riskId}/monitor`, monitoringData);
    return response.data;
  },
  scheduleReview: async (riskId: number, reviewData: any) => {
    const response: AxiosResponse = await api.post(`/risk-framework/${riskId}/review`, reviewData);
    return response.data;
  },
  conductReview: async (riskId: number, reviewData: any) => {
    const response: AxiosResponse = await api.post(`/risk-framework/${riskId}/review/conduct`, reviewData);
    return response.data;
  },

  // ============================================================================
  // ISO 22000:2018 FSMS INTEGRATION
  // ============================================================================
  
  // FSMS Integration
  integrateWithFSMS: async (riskId: number, fsmsData: any) => {
    const response: AxiosResponse = await api.post(`/risk-framework/${riskId}/fsms/integrate`, fsmsData);
    return response.data;
  },
  getFSMSIntegrations: async (riskId: number) => {
    const response: AxiosResponse = await api.get(`/risk-framework/${riskId}/fsms/integrations`);
    return response.data;
  },

  // ============================================================================
  // ADVANCED RISK MANAGEMENT FEATURES
  // ============================================================================
  
  // Risk Correlations
  correlateRisks: async (riskId: number, correlationData: any) => {
    const response: AxiosResponse = await api.post(`/risk-framework/${riskId}/correlate`, correlationData);
    return response.data;
  },
  getCorrelations: async (riskId: number) => {
    const response: AxiosResponse = await api.get(`/risk-framework/${riskId}/correlations`);
    return response.data;
  },
  
  // Resource Allocation
  allocateResources: async (riskId: number, allocationData: any) => {
    const response: AxiosResponse = await api.post(`/risk-framework/${riskId}/resources/allocate`, allocationData);
    return response.data;
  },
  approveResourceAllocation: async (allocationId: number) => {
    const response: AxiosResponse = await api.post(`/risk-framework/resources/${allocationId}/approve`);
    return response.data;
  },
  
  // Risk Communication
  createCommunication: async (riskId: number, communicationData: any) => {
    const response: AxiosResponse = await api.post(`/risk-framework/${riskId}/communicate`, communicationData);
    return response.data;
  },
  sendCommunication: async (communicationId: number) => {
    const response: AxiosResponse = await api.post(`/risk-framework/communications/${communicationId}/send`);
    return response.data;
  },
  
  // KPI Management
  createKPI: async (kpiData: any) => {
    const response: AxiosResponse = await api.post('/risk-framework/kpis', kpiData);
    return response.data;
  },
  updateKPIValue: async (kpiId: number, value: number) => {
    const response: AxiosResponse = await api.put(`/risk-framework/kpis/${kpiId}/value`, { value });
    return response.data;
  },
  getKPIs: async (category?: string) => {
    const response: AxiosResponse = await api.get('/risk-framework/kpis', { 
      params: category ? { category } : {} 
    });
    return response.data;
  },
  
  // Dashboard & Analytics
  getDashboard: async () => {
    const response: AxiosResponse = await api.get('/risk-framework/dashboard');
    return response.data;
  },

  // ============================================================================
  // ENHANCED ANALYTICS & COMPLIANCE ENDPOINTS
  // ============================================================================
  
  // Comprehensive Analytics
  getAnalytics: async (filters?: {
    date_from?: string;
    date_to?: string;
    category?: string;
    severity?: string;
    status?: string;
    include_opportunities?: boolean;
  }) => {
    const response: AxiosResponse = await api.get('/risk-framework/analytics', { params: filters });
    return response.data;
  },
  
  // Risk Trends
  getTrends: async (period: string = 'monthly', periods_back: number = 12) => {
    const response: AxiosResponse = await api.get('/risk-framework/trends', { 
      params: { period, periods_back } 
    });
    return response.data;
  },
  
  // Performance Metrics
  getPerformance: async () => {
    const response: AxiosResponse = await api.get('/risk-framework/performance');
    return response.data;
  },
  
  // ISO Compliance Status
  getComplianceStatus: async () => {
    const response: AxiosResponse = await api.get('/risk-framework/compliance-status');
    return response.data;
  },

  // ============================================================================
  // FSMS INTEGRATION ENDPOINTS
  // ============================================================================
  
  // Create FSMS Integration
  createFSMSIntegration: async (integrationData: {
    risk_register_item_id: number;
    fsms_element: string;
    fsms_element_id?: number;
    impact_on_fsms: string;
    food_safety_objective_id?: number;
    interested_party_impact?: Record<string, any>;
    compliance_requirement?: string;
  }) => {
    const response: AxiosResponse = await api.post('/risk-framework/fsms-integration', integrationData);
    return response.data;
  },
  
  // Get FSMS Integration (alternate path)
  getFSMSIntegration: async (riskId: number) => {
    const response: AxiosResponse = await api.get(`/risk-framework/fsms-integration/${riskId}`);
    return response.data;
  },
  
  // Create Risk from HACCP Hazard
  createRiskFromHazard: async (hazardId: number) => {
    const response: AxiosResponse = await api.post(`/risk-framework/integrate/haccp-hazard/${hazardId}`);
    return response.data;
  },
  
  // Create Risk from PRP Non-conformance
  createRiskFromPRP: async (prpId: number, description: string) => {
    const response: AxiosResponse = await api.post(`/risk-framework/integrate/prp-nonconformance/${prpId}`, {
      description
    });
    return response.data;
  },
  
  // Create Risk from Supplier Evaluation
  createRiskFromSupplier: async (supplierId: number, findings: string) => {
    const response: AxiosResponse = await api.post(`/risk-framework/integrate/supplier-evaluation/${supplierId}`, {
      findings
    });
    return response.data;
  },
  
  // Create Risk from Audit Finding
  createRiskFromAudit: async (findingId: number) => {
    const response: AxiosResponse = await api.post(`/risk-framework/integrate/audit-finding/${findingId}`);
    return response.data;
  },
  
  // Create Opportunity from Audit Finding
  createOpportunityFromAudit: async (findingId: number) => {
    const response: AxiosResponse = await api.post(`/risk-framework/integrate/audit-opportunity/${findingId}`);
    return response.data;
  },

  // ============================================================================
  // ENHANCED RISK ASSESSMENT & TREATMENT
  // ============================================================================
  
  // Conduct Risk Assessment (ISO 31000:2018 compliant)
  conductAssessment: async (assessmentData: {
    risk_id: number;
    risk_context_id?: number;
    assessment_method: string;
    assessor_id: number;
    assessment_data: Record<string, any>;
  }) => {
    const response: AxiosResponse = await api.post('/risk-framework/assess', assessmentData);
    return response.data;
  },
  
  // Plan Risk Treatment (ISO 31000:2018 compliant)
  planTreatment: async (treatmentData: {
    risk_id: number;
    treatment_strategy: 'avoid' | 'transfer' | 'mitigate' | 'accept';
    treatment_plan: string;
    treatment_cost?: number;
    treatment_benefit?: number;
    treatment_timeline?: string;
  }) => {
    const response: AxiosResponse = await api.post('/risk-framework/treat', treatmentData);
    return response.data;
  },

  // ============================================================================
  // RISK CONTEXT & FRAMEWORK MANAGEMENT
  // ============================================================================
  
  // Risk Context Management
  getRiskContext: async () => {
    const response: AxiosResponse = await api.get('/risk-framework/context');
    return response.data;
  },
  
  createRiskContext: async (contextData: RiskContext) => {
    const response: AxiosResponse = await api.post('/risk-framework/context', contextData);
    return response.data;
  },
  
  // Enhanced KPI Management
  createKPIEnhanced: async (kpiData: {
    kpi_name: string;
    kpi_description?: string;
    kpi_category: string;
    kpi_formula?: string;
    kpi_target?: number;
    kpi_unit?: string;
    kpi_frequency: string;
    kpi_owner: number;
  }) => {
    const response: AxiosResponse = await api.post('/risk-framework/kpis', kpiData);
    return response.data;
  },
  
  getKPIsEnhanced: async (category?: string) => {
    const response: AxiosResponse = await api.get('/risk-framework/kpis', { 
      params: category ? { category } : {} 
    });
    return response.data;
  },

  // ============================================================================
  // EXISTING ACTION OPERATIONS (Enhanced)
  // ============================================================================
  addAction: async (id: number, payload: { title: string; description?: string; assigned_to?: number; due_date?: string }) => {
    const response: AxiosResponse = await api.post(`/risk/${id}/actions`, payload);
    return response.data;
  },
  listActions: async (id: number) => {
    const response: AxiosResponse = await api.get(`/risk/${id}/actions`);
    return response.data;
  },
  completeAction: async (actionId: number) => {
    const response: AxiosResponse = await api.post(`/risk/actions/${actionId}/complete`);
    return response.data;
  },
  updateAction: async (actionId: number, payload: any) => {
    const response: AxiosResponse = await api.put(`/risk/actions/${actionId}`, payload);
    return response.data;
  },
  deleteAction: async (actionId: number) => {
    const response: AxiosResponse = await api.delete(`/risk/actions/${actionId}`);
    return response.data;
  },
};

export default riskAPI;


