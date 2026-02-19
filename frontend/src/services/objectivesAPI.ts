import { api } from './api';

export interface ObjectiveCreatePayload {
  objective_code: string;
  title: string;
  description?: string;
  category?: string;
  measurement_unit?: string;
  frequency?: string;
  responsible_person_id?: number;
  review_frequency?: string;
  created_by: number;
}

export interface ObjectiveUpdatePayload {
  title?: string;
  description?: string;
  category?: string;
  measurement_unit?: string;
  frequency?: string;
  responsible_person_id?: number;
  review_frequency?: string;
  status?: 'active' | 'inactive' | 'archived';
}

export interface ObjectiveTargetPayload {
  objective_id: number;
  department_id?: number;
  period_start: string;
  period_end: string;
  target_value: number;
  lower_threshold?: number;
  upper_threshold?: number;
  weight?: number;
  is_lower_better?: boolean;
  created_by: number;
}

export interface ObjectiveProgressPayload {
  objective_id: number;
  department_id?: number;
  period_start: string;
  period_end: string;
  actual_value: number;
  evidence?: string;
  created_by: number;
}

const objectivesAPI = {
  // Basic Objectives Endpoints
  listObjectives: async () => {
    const res = await api.get('/objectives/');
    return res.data;
  },

  createObjective: async (payload: ObjectiveCreatePayload) => {
    const res = await api.post('/objectives/', payload);
    return res.data;
  },

  getObjective: async (objectiveId: number) => {
    const res = await api.get(`/objectives/${objectiveId}`);
    return res.data;
  },

  updateObjective: async (objectiveId: number, payload: ObjectiveUpdatePayload) => {
    const res = await api.put(`/objectives/${objectiveId}`, payload);
    return res.data;
  },

  // Targets
  createTarget: async (objectiveId: number, payload: ObjectiveTargetPayload) => {
    const res = await api.post(`/objectives/${objectiveId}/targets`, payload);
    return res.data;
  },

  getTargets: async (objectiveId: number) => {
    const res = await api.get(`/objectives/${objectiveId}/targets`);
    return res.data;
  },

  // Progress
  createProgress: async (objectiveId: number, payload: ObjectiveProgressPayload) => {
    const res = await api.post(`/objectives/${objectiveId}/progress`, payload);
    return res.data;
  },

  getProgress: async (objectiveId: number) => {
    const res = await api.get(`/objectives/${objectiveId}/progress`);
    return res.data;
  },

  // KPIs
  getKPIs: async (params?: { objective_id?: number; department_id?: number; period_start?: string; period_end?: string }) => {
    const res = await api.get('/objectives/kpis', { params });
    return res.data;
  },

  // Enhanced Objectives Endpoints
  listEnhancedObjectives: async (params?: { 
    objective_type?: string; 
    department_id?: number; 
    hierarchy_level?: string; 
    status?: string; 
    performance_color?: string; 
    trend_direction?: string; 
    page?: number; 
    size?: number 
  }) => {
    const res = await api.get('/objectives-v2/', { params });
    return res.data;
  },

  createEnhancedObjective: async (payload: any) => {
    const res = await api.post('/objectives-v2/', payload);
    return res.data;
  },

  getEnhancedObjective: async (objectiveId: number) => {
    const res = await api.get(`/objectives-v2/${objectiveId}`);
    return res.data;
  },

  updateEnhancedObjective: async (objectiveId: number, payload: any) => {
    const res = await api.put(`/objectives-v2/${objectiveId}`, payload);
    return res.data;
  },

  deleteEnhancedObjective: async (objectiveId: number) => {
    const res = await api.delete(`/objectives-v2/${objectiveId}`);
    return res.data;
  },

  // Corporate and Departmental
  getCorporateObjectives: async () => {
    const res = await api.get('/objectives-v2/corporate');
    return res.data;
  },

  getDepartmentalObjectives: async (departmentId: number) => {
    const res = await api.get(`/objectives-v2/departmental/${departmentId}`);
    return res.data;
  },

  getHierarchicalObjectives: async () => {
    const res = await api.get('/objectives-v2/hierarchy');
    return res.data;
  },

  // Enhanced Progress
  createEnhancedProgress: async (objectiveId: number, payload: any) => {
    const res = await api.post(`/objectives-v2/${objectiveId}/progress`, payload);
    return res.data;
  },

  getEnhancedProgress: async (objectiveId: number, limit?: number) => {
    const res = await api.get(`/objectives-v2/${objectiveId}/progress`, { params: { limit } });
    return res.data;
  },

  getTrendAnalysis: async (objectiveId: number, periods?: number) => {
    const res = await api.get(`/objectives-v2/${objectiveId}/progress/trend`, { params: { periods } });
    return res.data;
  },

  createBulkProgress: async (objectiveId: number, payload: any) => {
    const res = await api.post(`/objectives-v2/${objectiveId}/progress/bulk`, payload);
    return res.data;
  },

  // Enhanced Targets
  createEnhancedTarget: async (objectiveId: number, payload: any) => {
    const res = await api.post(`/objectives-v2/${objectiveId}/targets`, payload);
    return res.data;
  },

  getEnhancedTargets: async (objectiveId: number) => {
    const res = await api.get(`/objectives-v2/${objectiveId}/targets`);
    return res.data;
  },

  createBulkTargets: async (objectiveId: number, payload: any) => {
    const res = await api.post(`/objectives-v2/${objectiveId}/targets/bulk`, payload);
    return res.data;
  },

  // Dashboard
  getDashboardKPIs: async () => {
    const res = await api.get('/objectives-v2/dashboard/kpis');
    return res.data;
  },

  getPerformanceMetrics: async (departmentId?: number) => {
    const res = await api.get('/objectives-v2/dashboard/performance', { params: { department_id: departmentId } });
    return res.data;
  },

  getDashboardTrends: async (objectiveIds: number[], periods?: number) => {
    const res = await api.get('/objectives-v2/dashboard/trends', { 
      params: { 
        objective_ids: objectiveIds.join(','), 
        periods 
      } 
    });
    return res.data;
  },

  getDashboardAlerts: async () => {
    const res = await api.get('/objectives-v2/dashboard/alerts');
    return res.data;
  },

  getDashboardSummary: async () => {
    const res = await api.get('/objectives-v2/dashboard/summary');
    return res.data;
  },

  getPerformanceComparison: async (period1: string, period2: string) => {
    const res = await api.get('/objectives-v2/dashboard/comparison', { params: { period1, period2 } });
    return res.data;
  },

  // Departments
  createDepartment: async (payload: any) => {
    const res = await api.post('/objectives-v2/departments', payload);
    return res.data;
  },

  getDepartments: async () => {
    const res = await api.get('/objectives-v2/departments');
    return res.data;
  },

  getDepartment: async (departmentId: number) => {
    const res = await api.get(`/objectives-v2/departments/${departmentId}`);
    return res.data;
  },

  updateDepartment: async (departmentId: number, payload: any) => {
    const res = await api.put(`/objectives-v2/departments/${departmentId}`, payload);
    return res.data;
  },

  deleteDepartment: async (departmentId: number) => {
    const res = await api.delete(`/objectives-v2/departments/${departmentId}`);
    return res.data;
  },

  // Progress Summary
  getProgressSummary: async () => {
    const res = await api.get('/objectives-v2/progress/summary');
    return res.data;
  },

  // Export
  exportObjectives: async (format?: string, objectiveType?: string, departmentId?: number) => {
    const res = await api.get('/objectives-v2/export', { 
      params: { format, objective_type: objectiveType, department_id: departmentId },
      responseType: 'blob'
    });
    return res.data;
  },

  // Links
  getObjectiveLinks: async (objectiveId: number) => {
    const res = await api.get(`/objectives-v2/${objectiveId}/links`);
    return res.data;
  },

  updateObjectiveLinks: async (objectiveId: number, payload: any) => {
    const res = await api.put(`/objectives-v2/${objectiveId}/links`, payload);
    return res.data;
  },

  // Evidence
  uploadEvidence: async (objectiveId: number, payload: { file: File; notes?: string; progress_id?: number }) => {
    const formData = new FormData();
    formData.append('file', payload.file);
    if (payload.notes) formData.append('notes', payload.notes);
    if (payload.progress_id) formData.append('progress_id', String(payload.progress_id));
    
    const res = await api.post(`/objectives-v2/${objectiveId}/evidence`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  getEvidence: async (objectiveId: number) => {
    const res = await api.get(`/objectives-v2/${objectiveId}/evidence`);
    return res.data;
  },

  deleteEvidence: async (objectiveId: number, evidenceId: number) => {
    const res = await api.delete(`/objectives-v2/${objectiveId}/evidence/${evidenceId}`);
    return res.data;
  },

  verifyEvidence: async (objectiveId: number, evidenceId: number) => {
    const res = await api.post(`/objectives-v2/${objectiveId}/evidence/${evidenceId}/verify`);
    return res.data;
  },

  // Assignment and Approval
  assignOwner: async (objectiveId: number, payload: { owner_user_id: number }) => {
    const res = await api.post(`/objectives-v2/${objectiveId}/assign`, payload);
    return res.data;
  },

  submitForApproval: async (objectiveId: number, payload?: any) => {
    const res = await api.post(`/objectives-v2/${objectiveId}/submit`, payload);
    return res.data;
  },

  approveObjective: async (objectiveId: number, payload?: any) => {
    const res = await api.post(`/objectives-v2/${objectiveId}/approve`, payload);
    return res.data;
  },

  rejectObjective: async (objectiveId: number, payload?: any) => {
    const res = await api.post(`/objectives-v2/${objectiveId}/reject`, payload);
    return res.data;
  },

  closeObjective: async (objectiveId: number, payload?: any) => {
    const res = await api.post(`/objectives-v2/${objectiveId}/close`, payload);
    return res.data;
  },
};

export default objectivesAPI;

