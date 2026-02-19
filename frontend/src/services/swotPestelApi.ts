/**
 * ISO-Compliant SWOT/PESTEL API Service
 * Connects frontend to backend ISO 9001:2015 compliant endpoints
 */

import axios, { AxiosResponse } from 'axios';
import {
  SWOTAnalysisCreate,
  SWOTAnalysisUpdate,
  SWOTAnalysisResponse,
  SWOTItemCreate,
  SWOTItemUpdate,
  SWOTItemResponse,
  PESTELAnalysisCreate,
  PESTELAnalysisUpdate,
  PESTELAnalysisResponse,
  PESTELItemCreate,
  PESTELItemUpdate,
  PESTELItemResponse,
  SWOTAnalytics,
  PESTELAnalytics,
  ISOComplianceMetrics,
  ISODashboardMetrics,
  StrategicContextAssessment,
  ISOReviewResult,
  RiskSummary,
  MonitoringDashboard,
  ManagementReviewInput,
  StrategicContext,
  ApiResponse,
  SWOTCategory,
  PESTELCategory
} from '../types/swotPestel';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const SWOT_PESTEL_BASE = `${API_BASE_URL}/swot-pestel`;

// Configure axios with auth token
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor
apiClient.interceptors.request.use((config) => {
  const authHeaders = getAuthHeaders();
  Object.assign(config.headers, authHeaders);
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export class SWOTPESTELApiService {
  
  // ============================
  // SWOT Analysis Management
  // ============================
  
  static async createSWOTAnalysis(data: SWOTAnalysisCreate): Promise<SWOTAnalysisResponse> {
    const response: AxiosResponse<SWOTAnalysisResponse> = await apiClient.post(
      `${SWOT_PESTEL_BASE}/swot-analyses/`,
      data
    );
    return response.data;
  }

  static async getSWOTAnalyses(
    skip: number = 0,
    limit: number = 100,
    is_active?: boolean,
    scope?: string
  ): Promise<SWOTAnalysisResponse[]> {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (is_active !== undefined) params.append('is_active', is_active.toString());
    if (scope) params.append('scope', scope);

    const response: AxiosResponse<SWOTAnalysisResponse[]> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/swot-analyses/?${params.toString()}`
    );
    return response.data;
  }

  static async getSWOTAnalysis(id: number): Promise<SWOTAnalysisResponse> {
    const response: AxiosResponse<SWOTAnalysisResponse> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/swot-analyses/${id}`
    );
    return response.data;
  }

  static async updateSWOTAnalysis(id: number, data: SWOTAnalysisUpdate): Promise<SWOTAnalysisResponse> {
    const response: AxiosResponse<SWOTAnalysisResponse> = await apiClient.put(
      `${SWOT_PESTEL_BASE}/swot-analyses/${id}`,
      data
    );
    return response.data;
  }

  static async deleteSWOTAnalysis(id: number): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.delete(
      `${SWOT_PESTEL_BASE}/swot-analyses/${id}`
    );
    return response.data;
  }

  // ============================
  // SWOT Items Management
  // ============================

  static async createSWOTItem(analysisId: number, data: SWOTItemCreate): Promise<SWOTItemResponse> {
    const response: AxiosResponse<SWOTItemResponse> = await apiClient.post(
      `${SWOT_PESTEL_BASE}/swot-analyses/${analysisId}/items/`,
      data
    );
    return response.data;
  }

  static async getSWOTItems(
    analysisId: number,
    category?: SWOTCategory
  ): Promise<SWOTItemResponse[]> {
    const params = category ? `?category=${category}` : '';
    const response: AxiosResponse<SWOTItemResponse[]> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/swot-analyses/${analysisId}/items/${params}`
    );
    return response.data;
  }

  static async updateSWOTItem(itemId: number, data: SWOTItemUpdate): Promise<SWOTItemResponse> {
    const response: AxiosResponse<SWOTItemResponse> = await apiClient.put(
      `${SWOT_PESTEL_BASE}/swot-items/${itemId}`,
      data
    );
    return response.data;
  }

  static async deleteSWOTItem(itemId: number): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.delete(
      `${SWOT_PESTEL_BASE}/swot-items/${itemId}`
    );
    return response.data;
  }

  // ============================
  // PESTEL Analysis Management
  // ============================

  static async createPESTELAnalysis(data: PESTELAnalysisCreate): Promise<PESTELAnalysisResponse> {
    const response: AxiosResponse<PESTELAnalysisResponse> = await apiClient.post(
      `${SWOT_PESTEL_BASE}/pestel-analyses/`,
      data
    );
    return response.data;
  }

  static async getPESTELAnalyses(
    skip: number = 0,
    limit: number = 100,
    is_active?: boolean,
    scope?: string
  ): Promise<PESTELAnalysisResponse[]> {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (is_active !== undefined) params.append('is_active', is_active.toString());
    if (scope) params.append('scope', scope);

    const response: AxiosResponse<PESTELAnalysisResponse[]> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/pestel-analyses/?${params.toString()}`
    );
    return response.data;
  }

  static async getPESTELAnalysis(id: number): Promise<PESTELAnalysisResponse> {
    const response: AxiosResponse<PESTELAnalysisResponse> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/pestel-analyses/${id}`
    );
    return response.data;
  }

  static async updatePESTELAnalysis(id: number, data: PESTELAnalysisUpdate): Promise<PESTELAnalysisResponse> {
    const response: AxiosResponse<PESTELAnalysisResponse> = await apiClient.put(
      `${SWOT_PESTEL_BASE}/pestel-analyses/${id}`,
      data
    );
    return response.data;
  }

  static async deletePESTELAnalysis(id: number): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.delete(
      `${SWOT_PESTEL_BASE}/pestel-analyses/${id}`
    );
    return response.data;
  }

  // ============================
  // PESTEL Items Management
  // ============================

  static async createPESTELItem(analysisId: number, data: PESTELItemCreate): Promise<PESTELItemResponse> {
    const response: AxiosResponse<PESTELItemResponse> = await apiClient.post(
      `${SWOT_PESTEL_BASE}/pestel-analyses/${analysisId}/items/`,
      data
    );
    return response.data;
  }

  static async getPESTELItems(
    analysisId: number,
    category?: PESTELCategory
  ): Promise<PESTELItemResponse[]> {
    const params = category ? `?category=${category}` : '';
    const response: AxiosResponse<PESTELItemResponse[]> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/pestel-analyses/${analysisId}/items/${params}`
    );
    return response.data;
  }

  static async updatePESTELItem(itemId: number, data: PESTELItemUpdate): Promise<PESTELItemResponse> {
    const response: AxiosResponse<PESTELItemResponse> = await apiClient.put(
      `${SWOT_PESTEL_BASE}/pestel-items/${itemId}`,
      data
    );
    return response.data;
  }

  static async deletePESTELItem(itemId: number): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.delete(
      `${SWOT_PESTEL_BASE}/pestel-items/${itemId}`
    );
    return response.data;
  }

  // ============================
  // Analytics and Reporting
  // ============================

  static async getSWOTAnalytics(): Promise<SWOTAnalytics> {
    const response: AxiosResponse<SWOTAnalytics> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/analytics/swot-summary`
    );
    return response.data;
  }

  static async getPESTELAnalytics(): Promise<PESTELAnalytics> {
    const response: AxiosResponse<PESTELAnalytics> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/analytics/pestel-summary`
    );
    return response.data;
  }

  // ============================
  // ISO Compliance Features
  // ============================

  static async getISOComplianceMetrics(): Promise<ISOComplianceMetrics> {
    const response: AxiosResponse<ISOComplianceMetrics> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/iso/compliance-metrics`
    );
    return response.data;
  }

  static async getISODashboardMetrics(): Promise<ISODashboardMetrics> {
    const response: AxiosResponse<ISODashboardMetrics> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/iso/dashboard-metrics`
    );
    return response.data;
  }

  static async getClause41Assessment(): Promise<StrategicContextAssessment> {
    const response: AxiosResponse<StrategicContextAssessment> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/iso/clause-4-1-assessment`
    );
    return response.data;
  }

  static async conductSWOTISOReview(analysisId: number): Promise<ISOReviewResult> {
    const response: AxiosResponse<ISOReviewResult> = await apiClient.post(
      `${SWOT_PESTEL_BASE}/swot-analyses/${analysisId}/iso-review`
    );
    return response.data;
  }

  static async conductPESTELISOReview(analysisId: number): Promise<ISOReviewResult> {
    const response: AxiosResponse<ISOReviewResult> = await apiClient.post(
      `${SWOT_PESTEL_BASE}/pestel-analyses/${analysisId}/iso-review`
    );
    return response.data;
  }

  // ============================
  // Risk Integration
  // ============================

  static async linkSWOTToRisk(analysisId: number, riskId: number): Promise<{ message: string; analysis_id: number; risk_assessment_id: number; linked_at: string }> {
    const response = await apiClient.post(
      `${SWOT_PESTEL_BASE}/swot-analyses/${analysisId}/link-risk/${riskId}`
    );
    return response.data;
  }

  static async linkPESTELToRisk(analysisId: number, riskId: number): Promise<{ message: string; analysis_id: number; risk_assessment_id: number; linked_at: string }> {
    const response = await apiClient.post(
      `${SWOT_PESTEL_BASE}/pestel-analyses/${analysisId}/link-risk/${riskId}`
    );
    return response.data;
  }

  static async getSWOTRiskFactors(analysisId: number): Promise<RiskSummary> {
    const response: AxiosResponse<RiskSummary> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/swot-analyses/${analysisId}/risk-factors`
    );
    return response.data;
  }

  static async getPESTELRiskFactors(analysisId: number): Promise<RiskSummary> {
    const response: AxiosResponse<RiskSummary> = await apiClient.get(
      `${SWOT_PESTEL_BASE}/pestel-analyses/${analysisId}/risk-factors`
    );
    return response.data;
  }

  // ============================
  // Strategic Planning Integration
  // ============================

  static async createStrategicContext(contextData: StrategicContext): Promise<{
    message: string;
    strategic_context: any;
    iso_compliance: {
      clause: string;
      status: string;
      assessment_date: string;
    };
  }> {
    const response = await apiClient.post(
      `${SWOT_PESTEL_BASE}/strategic-context`,
      contextData
    );
    return response.data;
  }

  static async assessStrategicContextCompleteness(): Promise<{
    assessment: any;
    recommendations: string[];
    iso_requirements: {
      clause: string;
      title: string;
      key_requirements: string[];
    };
  }> {
    const response = await apiClient.get(
      `${SWOT_PESTEL_BASE}/strategic-context/assessment`
    );
    return response.data;
  }

  static async generateManagementReviewInput(
    startDate?: string,
    endDate?: string
  ): Promise<{
    management_review_input: ManagementReviewInput;
    iso_reference: {
      clause: string;
      title: string;
      input_requirements: string[];
    };
  }> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await apiClient.get(
      `${SWOT_PESTEL_BASE}/management-review-input?${params.toString()}`
    );
    return response.data;
  }

  // ============================
  // Continuous Monitoring
  // ============================

  static async getContinuousMonitoringDashboard(): Promise<{
    monitoring_dashboard: MonitoringDashboard;
    action_items: (string | null)[];
    compliance_alerts: (string | null)[];
  }> {
    const response = await apiClient.get(
      `${SWOT_PESTEL_BASE}/continuous-monitoring/dashboard`
    );
    return response.data;
  }

  // ============================
  // Utility Methods
  // ============================

  static async refreshAllData(): Promise<{
    swot_analyses: SWOTAnalysisResponse[];
    pestel_analyses: PESTELAnalysisResponse[];
    swot_analytics: SWOTAnalytics;
    pestel_analytics: PESTELAnalytics;
    iso_metrics: ISOComplianceMetrics;
  }> {
    try {
      const [
        swot_analyses,
        pestel_analyses,
        swot_analytics,
        pestel_analytics,
        iso_metrics
      ] = await Promise.all([
        this.getSWOTAnalyses(),
        this.getPESTELAnalyses(),
        this.getSWOTAnalytics(),
        this.getPESTELAnalytics(),
        this.getISOComplianceMetrics()
      ]);

      return {
        swot_analyses,
        pestel_analyses,
        swot_analytics,
        pestel_analytics,
        iso_metrics
      };
    } catch (error) {
      console.error('Error refreshing all data:', error);
      throw error;
    }
  }

  // ============================
  // Error Handling Utilities
  // ============================

  static handleApiError(error: any): string {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  }

  static isAuthError(error: any): boolean {
    return error.response?.status === 401 || error.response?.status === 403;
  }

  static isValidationError(error: any): boolean {
    return error.response?.status === 422 || error.response?.status === 400;
  }
}

export default SWOTPESTELApiService;