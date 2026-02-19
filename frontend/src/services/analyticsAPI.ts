// Analytics API Service
// Phase 5: Frontend service for analytics and reporting

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api/v1';

// Types
export interface AnalyticsReport {
  id: number;
  title: string;
  description?: string;
  report_type: 'kpi_dashboard' | 'compliance_report' | 'performance_report' | 'trend_analysis' | 'audit_report' | 'risk_report' | 'action_report';
  status: 'draft' | 'published' | 'archived' | 'scheduled';
  report_config: any;
  chart_configs?: any;
  export_formats?: string[];
  is_public: boolean;
  department_id?: number;
  created_by: number;
  created_at: string;
  updated_at?: string;
  published_at?: string;
  creator_name?: string;
  department_name?: string;
}

export interface KPI {
  id: number;
  name: string;
  display_name: string;
  description?: string;
  category: string;
  module: string;
  calculation_method: string;
  calculation_query?: string;
  data_sources?: any;
  aggregation_type?: string;
  unit?: string;
  decimal_places: number;
  target_value?: number;
  min_value?: number;
  max_value?: number;
  warning_threshold?: number;
  critical_threshold?: number;
  alert_enabled: boolean;
  is_active: boolean;
  refresh_interval: number;
  last_calculation_at?: string;
  created_at: string;
  updated_at?: string;
  created_by: number;
  creator_name?: string;
  current_value?: number;
  trend?: string;
}

export interface KPIValue {
  id: number;
  kpi_id: number;
  value: number;
  department_id?: number;
  period_start?: string;
  period_end?: string;
  context_data?: any;
  calculated_at: string;
  department_name?: string;
}

export interface AnalyticsDashboard {
  id: number;
  name: string;
  description?: string;
  layout_config: any;
  theme: string;
  refresh_interval: number;
  is_public: boolean;
  department_id?: number;
  is_active: boolean;
  is_default: boolean;
  created_by: number;
  created_at: string;
  updated_at?: string;
  creator_name?: string;
  department_name?: string;
  widgets_count?: number;
}

export interface DashboardWidget {
  id: number;
  dashboard_id: number;
  widget_type: string;
  title: string;
  description?: string;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  data_source?: string;
  data_config?: any;
  chart_config?: any;
  refresh_interval?: number;
  is_visible: boolean;
  created_at: string;
  updated_at?: string;
}

export interface TrendAnalysis {
  id: number;
  name: string;
  description?: string;
  analysis_type: string;
  data_source: string;
  time_period: string;
  start_date: string;
  end_date: string;
  confidence_level: number;
  trend_direction?: string;
  trend_strength?: number;
  forecast_values?: any;
  confidence_intervals?: any;
  is_active: boolean;
  last_updated_at: string;
  created_by: number;
  created_at: string;
  creator_name?: string;
}

export interface AnalyticsSummary {
  total_reports: number;
  total_kpis: number;
  total_dashboards: number;
  active_trend_analyses: number;
  recent_reports: AnalyticsReport[];
  top_kpis: KPI[];
  system_health: any;
}

export interface KPIAnalytics {
  kpi_id: number;
  kpi_name: string;
  current_value: number;
  target_value?: number;
  trend: string;
  trend_percentage: number;
  historical_values: KPIValue[];
  performance_status: string;
  alerts_count: number;
}

export interface ReportAnalytics {
  report_id: number;
  report_title: string;
  report_type: string;
  execution_count: number;
  last_execution?: string;
  average_execution_time?: number;
  success_rate: number;
  user_engagement: any;
}

export interface DashboardAnalytics {
  dashboard_id: number;
  dashboard_name: string;
  view_count: number;
  last_viewed?: string;
  average_session_duration?: number;
  popular_widgets: any[];
  user_feedback: any;
}

// API Service
class AnalyticsAPI {
  private baseURL = `${API_BASE_URL}/analytics`;

  // Analytics Summary
  async getAnalyticsSummary(): Promise<AnalyticsSummary> {
    const response = await axios.get(`${this.baseURL}/summary`);
    return response.data;
  }

  async getSystemHealth(): Promise<any> {
    const response = await axios.get(`${this.baseURL}/health`);
    return response.data;
  }

  // Analytics Reports
  async createReport(reportData: Partial<AnalyticsReport>): Promise<AnalyticsReport> {
    const response = await axios.post(`${this.baseURL}/reports`, reportData);
    return response.data;
  }

  async getReports(params?: {
    report_type?: string;
    status?: string;
    is_public?: boolean;
    department_id?: number;
    limit?: number;
    offset?: number;
  }): Promise<AnalyticsReport[]> {
    const response = await axios.get(`${this.baseURL}/reports`, { params });
    return response.data;
  }

  async getReport(reportId: number): Promise<AnalyticsReport> {
    const response = await axios.get(`${this.baseURL}/reports/${reportId}`);
    return response.data;
  }

  async updateReport(reportId: number, updateData: Partial<AnalyticsReport>): Promise<AnalyticsReport> {
    const response = await axios.put(`${this.baseURL}/reports/${reportId}`, updateData);
    return response.data;
  }

  async getReportAnalytics(reportId: number): Promise<ReportAnalytics> {
    const response = await axios.get(`${this.baseURL}/reports/${reportId}/analytics`);
    return response.data;
  }

  // KPIs
  async createKPI(kpiData: Partial<KPI>): Promise<KPI> {
    const response = await axios.post(`${this.baseURL}/kpis`, kpiData);
    return response.data;
  }

  async getKPIs(params?: {
    category?: string;
    module?: string;
    is_active?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<KPI[]> {
    const response = await axios.get(`${this.baseURL}/kpis`, { params });
    return response.data;
  }

  async getKPI(kpiId: number): Promise<KPI> {
    const response = await axios.get(`${this.baseURL}/kpis/${kpiId}`);
    return response.data;
  }

  async updateKPI(kpiId: number, updateData: Partial<KPI>): Promise<KPI> {
    const response = await axios.put(`${this.baseURL}/kpis/${kpiId}`, updateData);
    return response.data;
  }

  async calculateKPI(kpiId: number, departmentId?: number): Promise<any> {
    const response = await axios.post(`${this.baseURL}/kpis/${kpiId}/calculate`, null, {
      params: { department_id: departmentId }
    });
    return response.data;
  }

  async getKPITrend(kpiId: number, days: number = 30): Promise<any> {
    const response = await axios.get(`${this.baseURL}/kpis/${kpiId}/trend`, {
      params: { days }
    });
    return response.data;
  }

  async getKPIAnalytics(kpiId: number): Promise<KPIAnalytics> {
    const response = await axios.get(`${this.baseURL}/kpis/${kpiId}/analytics`);
    return response.data;
  }

  // KPI Values
  async createKPIValue(valueData: Partial<KPIValue>): Promise<KPIValue> {
    const response = await axios.post(`${this.baseURL}/kpi-values`, valueData);
    return response.data;
  }

  async getKPIValues(kpiId: number, params?: {
    limit?: number;
    offset?: number;
  }): Promise<KPIValue[]> {
    const response = await axios.get(`${this.baseURL}/kpi-values/${kpiId}`, { params });
    return response.data;
  }

  // Dashboards
  async createDashboard(dashboardData: Partial<AnalyticsDashboard>): Promise<AnalyticsDashboard> {
    const response = await axios.post(`${this.baseURL}/dashboards`, dashboardData);
    return response.data;
  }

  async getDashboards(params?: {
    is_public?: boolean;
    is_active?: boolean;
    department_id?: number;
    limit?: number;
    offset?: number;
  }): Promise<AnalyticsDashboard[]> {
    const response = await axios.get(`${this.baseURL}/dashboards`, { params });
    return response.data;
  }

  async getDashboard(dashboardId: number): Promise<AnalyticsDashboard> {
    const response = await axios.get(`${this.baseURL}/dashboards/${dashboardId}`);
    return response.data;
  }

  async updateDashboard(dashboardId: number, updateData: Partial<AnalyticsDashboard>): Promise<AnalyticsDashboard> {
    const response = await axios.put(`${this.baseURL}/dashboards/${dashboardId}`, updateData);
    return response.data;
  }

  async getDashboardAnalytics(dashboardId: number): Promise<DashboardAnalytics> {
    const response = await axios.get(`${this.baseURL}/dashboards/${dashboardId}/analytics`);
    return response.data;
  }

  // Widgets
  async createWidget(widgetData: Partial<DashboardWidget>): Promise<DashboardWidget> {
    const response = await axios.post(`${this.baseURL}/widgets`, widgetData);
    return response.data;
  }

  async getDashboardWidgets(dashboardId: number): Promise<DashboardWidget[]> {
    const response = await axios.get(`${this.baseURL}/dashboards/${dashboardId}/widgets`);
    return response.data;
  }

  async getWidget(widgetId: number): Promise<DashboardWidget> {
    const response = await axios.get(`${this.baseURL}/widgets/${widgetId}`);
    return response.data;
  }

  async updateWidget(widgetId: number, updateData: Partial<DashboardWidget>): Promise<DashboardWidget> {
    const response = await axios.put(`${this.baseURL}/widgets/${widgetId}`, updateData);
    return response.data;
  }

  // Trend Analysis
  async createTrendAnalysis(analysisData: Partial<TrendAnalysis>): Promise<TrendAnalysis> {
    const response = await axios.post(`${this.baseURL}/trend-analysis`, analysisData);
    return response.data;
  }

  async getTrendAnalyses(params?: {
    is_active?: boolean;
    analysis_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<TrendAnalysis[]> {
    const response = await axios.get(`${this.baseURL}/trend-analysis`, { params });
    return response.data;
  }

  async getTrendAnalysis(analysisId: number): Promise<TrendAnalysis> {
    const response = await axios.get(`${this.baseURL}/trend-analysis/${analysisId}`);
    return response.data;
  }

  async calculateTrendAnalysis(analysisId: number): Promise<any> {
    const response = await axios.post(`${this.baseURL}/trend-analysis/${analysisId}/calculate`);
    return response.data;
  }
}

export const analyticsAPI = new AnalyticsAPI();
export default analyticsAPI;
