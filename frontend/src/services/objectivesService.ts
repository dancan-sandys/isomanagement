import axios from 'axios';
import {
  Objective,
  CreateObjective,
  UpdateObjective,
  ProgressEntry,
  CreateProgress,
  Department,
  DashboardKPI,
  PerformanceMetrics,
  TrendAnalysis,
  ObjectiveAlert,
  ObjectiveFilters,
  PaginationParams,
  ObjectivesResponse,
  ObjectiveResponse,
  ProgressResponse,
  DashboardResponse,
  ObjectiveEvidence
} from '../types/objectives';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Objectives Management API
export const objectivesService = {
  // Get all objectives with optional filtering and pagination
  getObjectives: async (
    filters?: ObjectiveFilters,
    pagination?: PaginationParams
  ): Promise<ObjectivesResponse> => {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.search) params.append('search', filters.search);
      if (filters.objective_type && filters.objective_type !== 'all') {
        params.append('objective_type', filters.objective_type);
      }
      if (filters.hierarchy_level && filters.hierarchy_level !== 'all') {
        params.append('hierarchy_level', filters.hierarchy_level);
      }
      if (filters.department_id && filters.department_id !== 'all') {
        params.append('department_id', filters.department_id.toString());
      }
      if (filters.performance_color && filters.performance_color !== 'all') {
        params.append('performance_color', filters.performance_color);
      }
      if (filters.date_range) {
        params.append('start_date', filters.date_range.start_date);
        params.append('end_date', filters.date_range.end_date);
      }
    }
    
    if (pagination) {
      params.append('page', pagination.page.toString());
      params.append('size', pagination.size.toString());
      if (pagination.sort_by) params.append('sort_by', pagination.sort_by);
      if (pagination.sort_order) params.append('sort_order', pagination.sort_order);
    }
    
            const response = await apiClient.get(`/objectives-v2/objectives?${params.toString()}`);
    return response.data;
  },

  // Get a specific objective by ID
  getObjective: async (id: number): Promise<ObjectiveResponse> => {
              const response = await apiClient.get(`/objectives-v2/objectives/${id}`);
    return response.data;
  },

  // Create a new objective
  createObjective: async (objective: CreateObjective): Promise<ObjectiveResponse> => {
              const response = await apiClient.post('/objectives-v2/objectives/', objective);
    return response.data;
  },

  // Update an existing objective
  updateObjective: async (id: number, objective: UpdateObjective): Promise<ObjectiveResponse> => {
              const response = await apiClient.put(`/objectives-v2/objectives/${id}`, objective);
    return response.data;
  },

  // Delete an objective
  deleteObjective: async (id: number): Promise<void> => {
              await apiClient.delete(`/objectives-v2/objectives/${id}`);
  },

  // Get corporate objectives
  getCorporateObjectives: async (): Promise<ObjectivesResponse> => {
              const response = await apiClient.get('/objectives-v2/objectives/corporate');
    return response.data;
  },

  // Get departmental objectives
  getDepartmentalObjectives: async (departmentId: number): Promise<ObjectivesResponse> => {
              const response = await apiClient.get(`/objectives-v2/objectives/departmental/${departmentId}`);
    return response.data;
  },

  // Get hierarchical objectives view
  getHierarchicalObjectives: async (): Promise<ObjectivesResponse> => {
              const response = await apiClient.get('/objectives-v2/objectives/hierarchy');
    return response.data;
  },

  // Progress Management API
  // Get progress history for an objective
  getObjectiveProgress: async (objectiveId: number): Promise<ProgressResponse> => {
              const response = await apiClient.get(`/objectives-v2/objectives/${objectiveId}/progress`);
    return response.data;
  },

  // Record progress for an objective
  createProgress: async (objectiveId: number, progress: CreateProgress): Promise<ProgressResponse> => {
              const response = await apiClient.post(`/objectives-v2/objectives/${objectiveId}/progress`, progress);
    return response.data;
  },

  // Get trend analysis for an objective
  getObjectiveTrend: async (objectiveId: number): Promise<TrendAnalysis> => {
              const response = await apiClient.get(`/objectives-v2/objectives/${objectiveId}/progress/trend`);
    return response.data;
  },

  // Bulk progress update
  bulkProgressUpdate: async (updates: CreateProgress[]): Promise<ProgressResponse> => {
              const response = await apiClient.post('/objectives-v2/objectives/progress/bulk', { updates });
    return response.data;
  },

  // Objective Linkages API
  getObjectiveLinks: async (objectiveId: number): Promise<{ linked_risk_ids: number[]; linked_control_ids: number[]; linked_document_ids: number[]; management_review_refs: number[] }> => {
              const response = await apiClient.get(`/objectives-v2/objectives/${objectiveId}/links`);
    return response.data;
  },
  updateObjectiveLinks: async (objectiveId: number, payload: Partial<{ linked_risk_ids: number[]; linked_control_ids: number[]; linked_document_ids: number[]; management_review_refs: number[] }>): Promise<ObjectiveResponse> => {
              const response = await apiClient.put(`/objectives-v2/objectives/${objectiveId}/links`, payload);
    return response.data;
  },

  // Dashboard API
  // Get dashboard KPIs
  getDashboardKPIs: async (): Promise<DashboardKPI> => {
              const response = await apiClient.get('/objectives-v2/objectives/dashboard/kpis');
    return response.data;
  },

  // Get performance metrics
  getPerformanceMetrics: async (): Promise<PerformanceMetrics[]> => {
              const response = await apiClient.get('/objectives-v2/objectives/dashboard/performance');
    return response.data;
  },

  // Get trend data
  getTrendData: async (): Promise<TrendAnalysis[]> => {
              const response = await apiClient.get('/objectives-v2/objectives/dashboard/trends');
    return response.data;
  },

  // Get performance alerts
  getPerformanceAlerts: async (): Promise<ObjectiveAlert[]> => {
              const response = await apiClient.get('/objectives-v2/objectives/dashboard/alerts');
    return response.data;
  },

  // Get period comparisons
  getPeriodComparisons: async (period1: string, period2: string): Promise<any> => {
              const response = await apiClient.get(`/objectives-v2/objectives/dashboard/comparison?period1=${period1}&period2=${period2}`);
    return response.data;
  },

  // Get complete dashboard data
  getDashboardData: async (): Promise<DashboardResponse> => {
              const response = await apiClient.get('/objectives-v2/objectives/dashboard/summary');
    return response.data;
  },

  // Department Management API
  // Get all departments
  getDepartments: async (): Promise<{ data: Department[] }> => {
              const response = await apiClient.get('/objectives-v2/departments');
    return response.data;
  },

  // Get a specific department
  getDepartment: async (id: number): Promise<{ data: Department }> => {
              const response = await apiClient.get(`/objectives-v2/departments/${id}`);
    return response.data;
  },

  // Create a new department
  createDepartment: async (department: Partial<Department>): Promise<{ data: Department }> => {
              const response = await apiClient.post('/objectives-v2/departments/', department);
    return response.data;
  },

  // Update a department
  updateDepartment: async (id: number, department: Partial<Department>): Promise<{ data: Department }> => {
              const response = await apiClient.put(`/objectives-v2/departments/${id}`, department);
    return response.data;
  },

  // Delete a department
  deleteDepartment: async (id: number): Promise<void> => {
              await apiClient.delete(`/objectives-v2/departments/${id}`);
  },

  // Evidence API
  listEvidence: async (objectiveId: number): Promise<{ data: ObjectiveEvidence[] }> => {
              const response = await apiClient.get(`/objectives-v2/objectives/${objectiveId}/evidence`);
    return response.data;
  },
  uploadEvidence: async (objectiveId: number, payload: { file: File; notes?: string; progress_id?: number }): Promise<ObjectiveEvidence> => {
    const formData = new FormData();
    formData.append('file', payload.file);
    if (payload.notes) formData.append('notes', payload.notes);
    if (payload.progress_id) formData.append('progress_id', String(payload.progress_id));
              const response = await apiClient.post(`/objectives-v2/objectives/${objectiveId}/evidence`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  },
  verifyEvidence: async (objectiveId: number, evidenceId: number): Promise<ObjectiveEvidence> => {
              const response = await apiClient.post(`/objectives-v2/objectives/${objectiveId}/evidence/${evidenceId}/verify`);
    return response.data;
  },
  deleteEvidence: async (objectiveId: number, evidenceId: number): Promise<void> => {
              await apiClient.delete(`/objectives-v2/objectives/${objectiveId}/evidence/${evidenceId}`);
  },

  // Utility functions
  // Export objectives data
  exportObjectives: async (format: 'csv' | 'excel' = 'csv'): Promise<Blob> => {
              const response = await apiClient.get(`/objectives-v2/objectives/export?format=${format}`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Import objectives data
  importObjectives: async (file: File): Promise<{ success: boolean; message: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    
              const response = await apiClient.post('/objectives-v2/objectives/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get objectives statistics
  getObjectivesStats: async (): Promise<{
    total: number;
    by_type: Record<string, number>;
    by_level: Record<string, number>;
    by_status: Record<string, number>;
  }> => {
              const response = await apiClient.get('/objectives-v2/objectives/stats');
    return response.data;
  },

  // Search objectives
  searchObjectives: async (query: string): Promise<Objective[]> => {
              const response = await apiClient.get(`/objectives-v2/objectives/search?q=${encodeURIComponent(query)}`);
    return response.data;
  },
};

// Export the service
export default objectivesService;
