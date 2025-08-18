import axios from 'axios';
import {
  DashboardStats,
  KPIDefinition,
  KPIValue,
  DashboardAlert,
  ComplianceScoreBreakdown,
  KPITrendPoint,
  KPICardData,
  ChartData,
  ExportRequest,
  ExportResponse
} from '../types/dashboard';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class DashboardService {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_BASE_URL}/api/dashboard`;
  }

  // Format KPI values with proper units and decimal places
  formatKPIValue(value: number, unit?: string): string {
    if (value === null || value === undefined) {
      return 'N/A';
    }

    // Format based on unit type
    if (unit) {
      switch (unit.toLowerCase()) {
        case 'percentage':
        case '%':
          return `${value.toFixed(1)}%`;
        case 'currency':
        case '$':
          return `$${value.toFixed(2)}`;
        case 'count':
        case 'number':
          return value.toLocaleString();
        case 'decimal':
          return value.toFixed(2);
        default:
          return `${value.toFixed(2)} ${unit}`;
      }
    }

    // Default formatting
    return value.toFixed(2);
  }

  // Get dashboard statistics
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      const response = await axios.get(`${this.baseURL}/stats`);
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  }

  // Get KPI definitions
  async getKPIDefinitions(category?: string): Promise<KPIDefinition[]> {
    try {
      const params = category ? { category } : {};
      const response = await axios.get(`${this.baseURL}/kpi-definitions`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching KPI definitions:', error);
      throw error;
    }
  }

  // Get KPI values
  async getKPIValues(
    kpiDefinitionId: number,
    periodStart?: string,
    periodEnd?: string,
    departmentId?: number
  ): Promise<KPIValue[]> {
    try {
      const params: any = { kpi_definition_id: kpiDefinitionId };
      if (periodStart) params.period_start = periodStart;
      if (periodEnd) params.period_end = periodEnd;
      if (departmentId) params.department_id = departmentId;

      const response = await axios.get(`${this.baseURL}/kpi-values`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching KPI values:', error);
      throw error;
    }
  }

  // Get KPI trend data
  async getKPITrend(
    kpiDefinitionId: number,
    periodStart: string,
    periodEnd: string,
    departmentId?: number
  ): Promise<KPITrendPoint[]> {
    try {
      const params: any = {
        kpi_definition_id: kpiDefinitionId,
        period_start: periodStart,
        period_end: periodEnd
      };
      if (departmentId) params.department_id = departmentId;

      const response = await axios.get(`${this.baseURL}/kpi-trend`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching KPI trend:', error);
      throw error;
    }
  }

  // Get KPI trend data (alias for compatibility)
  async getKPITrendData(
    kpiDefinitionId: number,
    periods: number,
    departmentId?: number
  ): Promise<KPITrendPoint[]> {
    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - periods * 30); // Approximate months

      const params: any = {
        kpi_definition_id: kpiDefinitionId,
        period_start: startDate.toISOString(),
        period_end: endDate.toISOString()
      };
      if (departmentId) params.department_id = departmentId;

      const response = await axios.get(`${this.baseURL}/kpi-trend`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching KPI trend data:', error);
      throw error;
    }
  }

  // Determine KPI status based on current value, target value, and operator
  determineKPIStatus(currentValue: number, targetValue: number, operator: string): string {
    if (targetValue === null || targetValue === undefined) {
      return 'no_target';
    }

    switch (operator.toLowerCase()) {
      case 'greater_than':
      case '>':
        return currentValue > targetValue ? 'good' : 'critical';
      case 'greater_than_or_equal':
      case '>=':
        return currentValue >= targetValue ? 'good' : 'critical';
      case 'less_than':
      case '<':
        return currentValue < targetValue ? 'good' : 'critical';
      case 'less_than_or_equal':
      case '<=':
        return currentValue <= targetValue ? 'good' : 'critical';
      case 'equals':
      case '=':
        return currentValue === targetValue ? 'good' : 'critical';
      case 'not_equals':
      case '!=':
        return currentValue !== targetValue ? 'good' : 'critical';
      case 'between':
        // For between, we assume targetValue is the lower bound
        // This is a simplified implementation
        return currentValue >= targetValue ? 'good' : 'critical';
      default:
        return 'unknown';
    }
  }

  // Get dashboard alerts
  async getDashboardAlerts(maxItems?: number, level?: string): Promise<DashboardAlert[]> {
    try {
      const params = level ? { level } : {};
      const response = await axios.get(`${this.baseURL}/alerts`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard alerts:', error);
      throw error;
    }
  }

  // Get compliance score breakdown
  async getComplianceScoreBreakdown(departmentId?: number): Promise<ComplianceScoreBreakdown> {
    try {
      const params = departmentId ? { department_id: departmentId } : {};
      const response = await axios.get(`${this.baseURL}/compliance-score`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching compliance score:', error);
      throw error;
    }
  }

  // Get KPI card data
  async getKPICardData(kpiIds: number[], departmentId?: number): Promise<KPICardData[]> {
    try {
      const params: any = { kpi_ids: kpiIds.join(',') };
      if (departmentId) params.department_id = departmentId;

      const response = await axios.get(`${this.baseURL}/kpi-cards`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching KPI card data:', error);
      throw error;
    }
  }

  // Export dashboard data
  async exportDashboardData(exportRequest: ExportRequest): Promise<ExportResponse> {
    try {
      const response = await axios.post(`${this.baseURL}/export`, exportRequest);
      return response.data;
    } catch (error) {
      console.error('Error exporting dashboard data:', error);
      throw error;
    }
  }

  // Get chart data for specific KPI
  async getChartData(
    kpiDefinitionId: number,
    chartType: string,
    periodStart: string,
    periodEnd: string,
    departmentId?: number
  ): Promise<ChartData> {
    try {
      const params: any = {
        kpi_definition_id: kpiDefinitionId,
        chart_type: chartType,
        period_start: periodStart,
        period_end: periodEnd
      };
      if (departmentId) params.department_id = departmentId;

      const response = await axios.get(`${this.baseURL}/chart-data`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching chart data:', error);
      throw error;
    }
  }

  // Get real-time updates via WebSocket (placeholder for future implementation)
  subscribeToUpdates(callback: (data: any) => void): () => void {
    // This would be implemented with WebSocket connection
    // For now, return a no-op unsubscribe function
    return () => {};
  }
}

// Export singleton instance
export const dashboardService = new DashboardService();
