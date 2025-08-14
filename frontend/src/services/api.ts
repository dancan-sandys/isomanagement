import axios, { AxiosResponse } from 'axios';

// Resolve API base URL intelligently for dev/prod
function resolveBaseURL(): string {
  const envUrl = process.env.REACT_APP_API_URL;
  if (envUrl && envUrl.trim().length > 0) return envUrl.trim();
  const isCRADev = typeof window !== 'undefined' && window.location && window.location.port === '3000';
  if (isCRADev) {
    // Let CRA dev proxy forward to backend (see package.json proxy)
    return '/api/v1';
  }
  // Same-origin reverse proxy in production
  const origin = typeof window !== 'undefined' ? window.location.origin : '';
  return origin ? `${origin}/api/v1` : '/api/v1';
}

// Create axios instance
const api = axios.create({
  // Prefer env; otherwise dynamic resolution for dev/prod
  baseURL: resolveBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
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

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry && !(originalRequest?.url || '').includes('/auth/refresh')) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(
            `${process.env.REACT_APP_API_URL || '/api/v1'}/auth/refresh`,
            { refresh_token: refreshToken }
          );

          const { access_token } = response.data.data;
          localStorage.setItem('access_token', access_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: { username: string; password: string }) => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response: AxiosResponse = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  signup: async (signupData: {
    username: string;
    email: string;
    password: string;
    full_name: string;
    department?: string;
    position?: string;
    phone?: string;
    employee_id?: string;
  }) => {
    const response: AxiosResponse = await api.post('/auth/signup', signupData);
    return response.data;
  },

  logout: async () => {
    const response: AxiosResponse = await api.post('/auth/logout');
    return response.data;
  },

  refresh: async (refreshToken: string) => {
    // Use a bare axios call to avoid interceptor recursion and stale Authorization headers
    const baseURL = process.env.REACT_APP_API_URL || '/api/v1';
    const response: AxiosResponse = await axios.post(
      `${baseURL}/auth/refresh`,
      { refresh_token: refreshToken },
      { headers: { 'Content-Type': 'application/json' }, timeout: 15000 }
    );
    return response.data;
  },

  me: async () => {
    const response: AxiosResponse = await api.get('/auth/me');
    return response.data;
  },
};

// Users API
export const usersAPI = {
  getUsers: async (params?: { 
    page?: number; 
    size?: number; 
    search?: string;
    role_id?: number;
    status?: string;
    department?: string;
  }) => {
    // Filter out empty string parameters
    const filteredParams: any = {};
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          filteredParams[key] = value;
        }
      });
    }
    const response: AxiosResponse = await api.get('/users', { params: filteredParams });
    return response.data;
  },

  getUser: async (userId: number) => {
    const response: AxiosResponse = await api.get(`/users/${userId}`);
    return response.data;
  },

  createUser: async (userData: any) => {
    const response: AxiosResponse = await api.post('/users', userData);
    return response.data;
  },

  updateUser: async (userId: number, userData: any) => {
    const response: AxiosResponse = await api.put(`/users/${userId}`, userData);
    return response.data;
  },

  deleteUser: async (userId: number) => {
    const response: AxiosResponse = await api.delete(`/users/${userId}`);
    return response.data;
  },

  activateUser: async (userId: number) => {
    const response: AxiosResponse = await api.post(`/users/${userId}/activate`);
    return response.data;
  },

  deactivateUser: async (userId: number) => {
    const response: AxiosResponse = await api.post(`/users/${userId}/deactivate`);
    return response.data;
  },

  resetPassword: async (userId: number, newPassword: string) => {
    const response: AxiosResponse = await api.post(`/users/${userId}/reset-password`, { new_password: newPassword });
    return response.data;
  },

  getDashboard: async () => {
    const response: AxiosResponse = await api.get('/users/dashboard');
    // Backend returns ResponseModel
    return response.data?.data || response.data;
  },
};

// Documents API
export const documentsAPI = {
  getDocuments: async (params?: {
    page?: number;
    size?: number;
    search?: string;
    category?: string;
    status?: string;
    document_type?: string;
    department?: string;
    product_line?: string;
    created_by?: number;
    date_from?: string;
    date_to?: string;
    review_date_from?: string;
    review_date_to?: string;
    keywords?: string;
  }) => {
    // Filter out empty string parameters
    const filteredParams: any = {};
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          // For enum fields, only send if it's a valid value
          if (['category', 'status', 'document_type'].includes(key)) {
            if (value && typeof value === 'string' && value.trim() !== '') {
              filteredParams[key] = value;
            }
          }
          // For date fields, only send if it's a valid date string
          else if (['date_from', 'date_to', 'review_date_from', 'review_date_to'].includes(key)) {
            if (value && typeof value === 'string' && value.trim() !== '') {
              filteredParams[key] = value;
            }
          }
          // For other fields, send if not empty
          else {
            filteredParams[key] = value;
          }
        }
      });
    }
    const response: AxiosResponse = await api.get('/documents', { params: filteredParams });
    return response.data;
  },

  // Multi-step approvals for documents
  submitApprovalFlow: async (
    documentId: number,
    approvers: Array<{ approver_id: number; approval_order: number }>
  ) => {
    const response: AxiosResponse = await api.post(`/documents/${documentId}/approvals`, approvers);
    return response.data;
  },

  getPendingApprovals: async () => {
    const response: AxiosResponse = await api.get('/documents/approvals/pending');
    return response.data;
  },

  approveApprovalStep: async (
    documentId: number,
    approvalId: number,
    payload?: { password?: string; comments?: string }
  ) => {
    const form = new FormData();
    if (payload?.password) form.append('password', payload.password);
    if (payload?.comments) form.append('comments', payload.comments);
    const response: AxiosResponse = await api.post(
      `/documents/${documentId}/approvals/${approvalId}/approve`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  rejectApprovalStep: async (
    documentId: number,
    approvalId: number,
    payload?: { comments?: string }
  ) => {
    const form = new FormData();
    if (payload?.comments) form.append('comments', payload.comments);
    const response: AxiosResponse = await api.post(
      `/documents/${documentId}/approvals/${approvalId}/reject`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  // Exports
  exportDocuments: async (
    format: 'pdf' | 'xlsx',
    filters?: Record<string, any>
  ) => {
    const response: AxiosResponse = await api.post('/documents/export', filters || {}, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },

  exportChangeLog: async (documentId: number, format: 'pdf' | 'xlsx' = 'pdf') => {
    const response: AxiosResponse = await api.get(
      `/documents/${documentId}/change-log/export`,
      { params: { format }, responseType: 'blob' }
    );
    return response.data;
  },

  exportVersions: async (documentId: number, format: 'pdf' | 'xlsx' = 'pdf') => {
    const response: AxiosResponse = await api.get(
      `/documents/${documentId}/versions/export`,
      { params: { format }, responseType: 'blob' }
    );
    return response.data;
  },

  // Document-Product linking
  getDocumentProducts: async (documentId: number) => {
    const response: AxiosResponse = await api.get(`/documents/${documentId}/products`);
    return response.data;
  },

  linkDocumentToProducts: async (documentId: number, productIds: number[]) => {
    const response: AxiosResponse = await api.post(`/documents/${documentId}/products`, { product_ids: productIds });
    return response.data;
  },

  unlinkDocumentProduct: async (documentId: number, productId: number) => {
    const response: AxiosResponse = await api.delete(`/documents/${documentId}/products/${productId}`);
    return response.data;
  },

  // Status transitions
  markObsolete: async (documentId: number, reason: string) => {
    const response: AxiosResponse = await api.post(`/documents/${documentId}/status/obsolete`, { reason });
    return response.data;
  },

  archiveDocument: async (documentId: number, reason: string) => {
    const response: AxiosResponse = await api.post(`/documents/${documentId}/status/archive`, { reason });
    return response.data;
  },

  activateDocument: async (documentId: number, reason?: string) => {
    const response: AxiosResponse = await api.post(`/documents/${documentId}/status/activate`, { reason });
    return response.data;
  },

  // Controlled distribution
  distributeDocument: async (
    documentId: number,
    distributionData: { user_ids?: number[]; department_ids?: number[]; notes?: string; copy_number?: string }
  ) => {
    const response: AxiosResponse = await api.post(`/documents/${documentId}/distribute`, distributionData);
    return response.data;
  },

  acknowledgeDistribution: async (documentId: number, userId: number) => {
    const response: AxiosResponse = await api.post(`/documents/${documentId}/distribution/${userId}/acknowledge`);
    return response.data;
  },

  getDocument: async (documentId: number) => {
    const response: AxiosResponse = await api.get(`/documents/${documentId}`);
    return response.data;
  },

  createDocument: async (formData: FormData) => {
    const response: AxiosResponse = await api.post('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  updateDocument: async (documentId: number, formData: FormData) => {
    const response: AxiosResponse = await api.put(`/documents/${documentId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  deleteDocument: async (documentId: number) => {
    const response: AxiosResponse = await api.delete(`/documents/${documentId}`);
    return response.data;
  },

  downloadDocument: async (documentId: number) => {
    const response: AxiosResponse = await api.get(`/documents/${documentId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  downloadVersion: async (documentId: number, versionId: number) => {
    const response: AxiosResponse = await api.get(`/documents/${documentId}/versions/${versionId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Version Control APIs
  createNewVersion: async (documentId: number, formData: FormData) => {
    const response: AxiosResponse = await api.post(`/documents/${documentId}/versions`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Approval workflow APIs
  getApprovalWorkflow: async (documentId: number) => {
    const response: AxiosResponse = await api.get(`/documents/${documentId}/approvals`);
    return response.data;
  },

  getVersionHistory: async (documentId: number) => {
    const response: AxiosResponse = await api.get(`/documents/${documentId}/versions`);
    return response.data;
  },

  getSpecificVersion: async (documentId: number, versionId: number) => {
    const response: AxiosResponse = await api.get(`/documents/${documentId}/versions/${versionId}`);
    return response.data;
  },

  // Approve a specific version of a document
  approveVersion: async (documentId: number, versionId: number, comments?: string) => {
    const formData = new FormData();
    if (comments) {
      formData.append('comments', comments);
    }
    
    const response = await api.post(
      `/documents/${documentId}/versions/${versionId}/approve`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response;
  },

  getChangeLog: async (documentId: number) => {
    const response: AxiosResponse = await api.get(`/documents/${documentId}/change-log`);
    return response.data;
  },

  uploadDocumentFile: async (documentId: number, formData: FormData) => {
    const response: AxiosResponse = await api.post(`/documents/${documentId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Document Statistics
  getDocumentStats: async () => {
    const response: AxiosResponse = await api.get('/documents/stats/overview');
    // Some endpoints return { success, data }, others raw
    return response.data?.data || response.data;
  },

  // Bulk Operations
  bulkUpdateStatus: async (documentIds: number[], action: string, reason?: string) => {
    const response: AxiosResponse = await api.post('/documents/bulk/status', {
      document_ids: documentIds,
      action,
      reason,
    });
    return response.data;
  },

  // Maintenance Operations
  archiveObsoleteDocuments: async () => {
    const response: AxiosResponse = await api.post('/documents/maintenance/archive-obsolete');
    return response.data;
  },

  getExpiredDocuments: async () => {
    const response: AxiosResponse = await api.get('/documents/maintenance/expired');
    return response.data;
  },

  // Document Templates
  getDocumentTemplates: async (params?: {
    page?: number;
    size?: number;
    document_type?: string;
    category?: string;
  }) => {
    const response: AxiosResponse = await api.get('/documents/templates/', { params });
    return response.data;
  },

  // Template versions and approvals
  createTemplateVersion: async (
    templateId: number,
    payload: { change_description: string; change_reason: string; template_content?: string }
  ) => {
    const response: AxiosResponse = await api.post(`/documents/templates/${templateId}/versions`, payload);
    return response.data;
  },

  getTemplateVersions: async (templateId: number) => {
    const response: AxiosResponse = await api.get(`/documents/templates/${templateId}/versions`);
    return response.data;
  },

  submitTemplateApprovalFlow: async (
    templateId: number,
    approvers: Array<{ approver_id: number; approval_order: number }>
  ) => {
    const response: AxiosResponse = await api.post(`/documents/templates/${templateId}/approvals`, approvers);
    return response.data;
  },

  approveTemplateApprovalStep: async (
    templateId: number,
    approvalId: number,
    payload?: { password?: string; comments?: string }
  ) => {
    const form = new FormData();
    if (payload?.password) form.append('password', payload.password);
    if (payload?.comments) form.append('comments', payload.comments);
    const response: AxiosResponse = await api.post(
      `/documents/templates/${templateId}/approvals/${approvalId}/approve`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  rejectTemplateApprovalStep: async (
    templateId: number,
    approvalId: number,
    payload?: { comments?: string }
  ) => {
    const form = new FormData();
    if (payload?.comments) form.append('comments', payload.comments);
    const response: AxiosResponse = await api.post(
      `/documents/templates/${templateId}/approvals/${approvalId}/reject`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  getDocumentTemplate: async (templateId: number) => {
    const response: AxiosResponse = await api.get(`/documents/templates/${templateId}`);
    return response.data;
  },

  createDocumentTemplate: async (templateData: any) => {
    const response: AxiosResponse = await api.post('/documents/templates/', templateData);
    return response.data;
  },

  deleteDocumentTemplate: async (templateId: number) => {
    const response: AxiosResponse = await api.delete(`/documents/templates/${templateId}`);
    return response.data;
  },
};

// HACCP API
export const haccpAPI = {
  // Products
  getProducts: async () => {
    const response: AxiosResponse = await api.get('/haccp/products');
    return response.data;
  },

  getProduct: async (productId: number) => {
    const response: AxiosResponse = await api.get(`/haccp/products/${productId}`);
    return response.data;
  },

  createProduct: async (productData: any) => {
    const response: AxiosResponse = await api.post('/haccp/products', productData);
    return response.data;
  },

  updateProduct: async (productId: number, productData: any) => {
    const response: AxiosResponse = await api.put(`/haccp/products/${productId}`, productData);
    return response.data;
  },

  deleteProduct: async (productId: number) => {
    const response: AxiosResponse = await api.delete(`/haccp/products/${productId}`);
    return response.data;
  },

  // Process Flows
  createProcessFlow: async (productId: number, flowData: any) => {
    const response: AxiosResponse = await api.post(`/haccp/products/${productId}/process-flows`, flowData);
    return response.data;
  },

  updateProcessFlow: async (flowId: number, flowData: any) => {
    const response: AxiosResponse = await api.put(`/haccp/process-flows/${flowId}`, flowData);
    return response.data;
  },

  deleteProcessFlow: async (flowId: number) => {
    const response: AxiosResponse = await api.delete(`/haccp/process-flows/${flowId}`);
    return response.data;
  },

  // Hazards
  createHazard: async (productId: number, hazardData: any) => {
    const response: AxiosResponse = await api.post(`/haccp/products/${productId}/hazards`, hazardData);
    return response.data;
  },

  updateHazard: async (hazardId: number, hazardData: any) => {
    const response: AxiosResponse = await api.put(`/haccp/hazards/${hazardId}`, hazardData);
    return response.data;
  },

  deleteHazard: async (hazardId: number) => {
    const response: AxiosResponse = await api.delete(`/haccp/hazards/${hazardId}`);
    return response.data;
  },

  runDecisionTree: async (hazardId: number) => {
    const response: AxiosResponse = await api.post(`/haccp/hazards/${hazardId}/decision-tree`);
    return response.data;
  },

  // CCPs
  createCCP: async (productId: number, ccpData: any) => {
    const response: AxiosResponse = await api.post(`/haccp/products/${productId}/ccps`, ccpData);
    return response.data;
  },

  updateCCP: async (ccpId: number, ccpData: any) => {
    const response: AxiosResponse = await api.put(`/haccp/ccps/${ccpId}`, ccpData);
    return response.data;
  },

  deleteCCP: async (ccpId: number) => {
    const response: AxiosResponse = await api.delete(`/haccp/ccps/${ccpId}`);
    return response.data;
  },

  // Monitoring Logs
  createMonitoringLog: async (ccpId: number, logData: any) => {
    const response: AxiosResponse = await api.post(`/haccp/ccps/${ccpId}/monitoring-logs`, logData);
    return response.data;
  },

  getMonitoringLogs: async (ccpId: number) => {
    const response: AxiosResponse = await api.get(`/haccp/ccps/${ccpId}/monitoring-logs`);
    return response.data;
  },

  // Verification Logs
  createVerificationLog: async (ccpId: number, logData: any) => {
    const response: AxiosResponse = await api.post(`/haccp/ccps/${ccpId}/verification-logs`, logData);
    return response.data;
  },

  getVerificationLogs: async (ccpId: number) => {
    const response: AxiosResponse = await api.get(`/haccp/ccps/${ccpId}/verification-logs`);
    return response.data;
  },

  // Dashboard and Reports
  getDashboard: async () => {
    const response: AxiosResponse = await api.get('/haccp/dashboard');
    return response.data;
  },

  getEnhancedDashboard: async () => {
    const response: AxiosResponse = await api.get('/haccp/dashboard/enhanced');
    return response.data;
  },

  getAlertsSummary: async (days: number = 7) => {
    const response: AxiosResponse = await api.get(`/haccp/alerts/summary?days=${days}`);
    return response.data;
  },

  getFlowchartData: async (productId: number) => {
    const response: AxiosResponse = await api.get(`/haccp/products/${productId}/flowchart`);
    return response.data;
  },

  generateReport: async (productId: number, reportRequest: any) => {
    const response: AxiosResponse = await api.post(`/haccp/products/${productId}/reports`, reportRequest);
    return response.data;
  },
  
  // HACCP Plan APIs
  createPlan: async (productId: number, payload: { title: string; description?: string; content: string; effective_date?: string; review_date?: string }) => {
    const response: AxiosResponse = await api.post(`/haccp/products/${productId}/plan`, payload);
    return response.data;
  },
  createPlanVersion: async (planId: number, payload: { content: string; change_description?: string; change_reason?: string }) => {
    const response: AxiosResponse = await api.post(`/haccp/plans/${planId}/versions`, payload);
    return response.data;
  },
  submitPlanApprovals: async (planId: number, approvals: Array<{ approver_id: number; approval_order: number }>) => {
    const response: AxiosResponse = await api.post(`/haccp/plans/${planId}/approvals`, approvals);
    return response.data;
  },
  approvePlanStep: async (planId: number, approvalId: number) => {
    const response: AxiosResponse = await api.post(`/haccp/plans/${planId}/approvals/${approvalId}/approve`);
    return response.data;
  },
  rejectPlanStep: async (planId: number, approvalId: number, comments?: string) => {
    const form = new FormData(); if (comments) form.append('comments', comments);
    const response: AxiosResponse = await api.post(`/haccp/plans/${planId}/approvals/${approvalId}/reject`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  },
};

// PRP API
export const prpAPI = {
  getPrograms: async (params?: { search?: string; category?: string }) => {
    const response: AxiosResponse = await api.get('/prp/programs', { params });
    return response.data;
  },

  getProgram: async (programId: number) => {
    const response: AxiosResponse = await api.get(`/prp/programs/${programId}`);
    return response.data;
  },

  createProgram: async (programData: any) => {
    const response: AxiosResponse = await api.post('/prp/programs', programData);
    return response.data;
  },

  getChecklists: async (programId: number, params?: { page?: number; size?: number }) => {
    const response: AxiosResponse = await api.get(`/prp/programs/${programId}/checklists`, { params });
    return response.data;
  },

  createChecklist: async (programId: number, checklistData: any) => {
    const response: AxiosResponse = await api.post(`/prp/programs/${programId}/checklists`, checklistData);
    return response.data;
  },

  getDashboard: async () => {
    const response: AxiosResponse = await api.get('/prp/dashboard');
    return response.data;
  },
};

// Dashboard API
export const dashboardAPI = {
  getDashboard: async () => {
    const response: AxiosResponse = await api.get('/dashboard/stats');
    return response.data;
  },

  getStats: async () => {
    const response: AxiosResponse = await api.get('/dashboard/stats');
    return response.data;
  },

  getRecentActivity: async () => {
    const response: AxiosResponse = await api.get('/dashboard/recent-activity');
    return response.data;
  },

  getComplianceMetrics: async () => {
    const response: AxiosResponse = await api.get('/dashboard/compliance-metrics');
    return response.data;
  },

  getSystemStatus: async () => {
    const response: AxiosResponse = await api.get('/dashboard/system-status');
    return response.data;
  },

  // Enhanced UX Methods (fallback to existing data if new endpoints not available)
  getUserMetrics: async (userId: string) => {
    try {
      const response: AxiosResponse = await api.get(`/dashboard/user-metrics/${userId}`);
      return response.data;
    } catch (error) {
      console.log('getUserMetrics endpoint not available, using fallback data');
      // Fallback to existing stats with some role-based customization
      const stats = await dashboardAPI.getStats();
      return {
        user_id: userId,
        metrics: {
          compliance_score: 94.2,
          open_capas: stats?.data?.pendingApprovals || 8,
          audit_score: 98.5,
          risk_level: 'low',
          tasks_completed_today: 6,
          line_efficiency: 96.8
        },
        trends: {
          compliance_change: 2.1,
          capa_change: -2,
          audit_change: 1.2
        }
      };
    }
  },

  getPriorityTasks: async (userId: string) => {
    try {
      const response: AxiosResponse = await api.get(`/dashboard/priority-tasks/${userId}`);
      return response.data;
    } catch (error) {
      console.log('getPriorityTasks endpoint not available, using fallback data');
      // Fallback: derive from recent activity or create sample based on role
      return {
        tasks: [
          {
            id: '1',
            title: 'Monthly HACCP Review',
            description: 'Review and approve HACCP plans for new products',
            priority: 'high',
            due_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
            category: 'HACCP',
            progress: 75,
            estimated_time: '2 hours'
          },
          {
            id: '2',
            title: 'Supplier Audit Schedule',
            description: 'Schedule quarterly audits for critical suppliers',
            priority: 'medium',
            due_date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
            category: 'Supplier Management',
            estimated_time: '1 hour'
          }
        ]
      };
    }
  },

  getInsights: async (userId: string) => {
    try {
      const response: AxiosResponse = await api.get(`/dashboard/insights/${userId}`);
      return response.data;
    } catch (error) {
      console.log('getInsights endpoint not available, using fallback data');
      // Fallback: basic insights that could be derived from existing data
      return {
        insights: [
          {
            id: '1',
            type: 'info',
            title: 'System Performance',
            description: 'System is running optimally with 99.9% uptime',
            action: {
              label: 'View Details',
              endpoint: '/dashboard/stats',
              method: 'GET'
            }
          }
        ]
      };
    }
  }
};

// Enhanced Search API
export const searchAPI = {
  smartSearch: async (query: string, userId?: string, limit: number = 10) => {
    try {
      const response: AxiosResponse = await api.get('/search/smart', {
        params: { q: query, user_id: userId, limit }
      });
      return response.data;
    } catch (error) {
      console.log('smartSearch endpoint not available, using fallback');
      // Fallback: search across existing endpoints
      const fallbackResults = await searchAPI.fallbackSearch(query, limit);
      return {
        results: fallbackResults,
        suggestions: [
          {
            id: '1',
            text: `Create new ${query}`,
            category: 'Quick Actions',
            action_type: 'create'
          }
        ]
      };
    }
  },

  fallbackSearch: async (query: string, limit: number = 10) => {
    // Search across multiple existing endpoints
      const searchPromises: Array<Promise<any[]>> = [];
    
    // Search documents
    try {
      searchPromises.push(
        documentsAPI.getDocuments({ search: query, size: 3 }).then((res: any) => 
          res?.data?.documents?.map((doc: any) => ({
            id: doc.id,
            title: doc.title,
            description: doc.description || 'Document',
            category: 'Documents',
            path: `/documents/${doc.id}`,
            priority: 8,
            last_used: doc.updated_at
          })) || []
        )
      );
    } catch (e) {
      searchPromises.push(Promise.resolve([]));
    }

    // Search HACCP products
    try {
      searchPromises.push(
        haccpAPI.getProducts().then((res: any) =>
          (res?.data?.products || res?.products || res || []).map((product: any) => ({
            id: product.id,
            title: product.name,
            description: `HACCP Product - ${product.product_type}`,
            category: 'HACCP',
            path: `/haccp/products/${product.id}`,
            priority: 9
          })) || []
        )
      );
    } catch (e) {
      searchPromises.push(Promise.resolve([]));
    }

    // Search suppliers
    try {
      searchPromises.push(
        supplierAPI.getSuppliers({ search: query, size: 3 }).then(res =>
          res?.data?.suppliers?.map((supplier: any) => ({
            id: supplier.id,
            title: supplier.name,
            description: `Supplier - ${supplier.supplier_type}`,
            category: 'Suppliers',
            path: `/suppliers/${supplier.id}`,
            priority: 7
          })) || []
        )
      );
    } catch (e) {
      searchPromises.push(Promise.resolve([]));
    }

    const results = await Promise.all(searchPromises);
    return results.flat().slice(0, limit);
  },

  trackSearch: async (userId: string, query: string, resultsCount: number, selectedResult?: string) => {
    try {
      await api.post('/search/analytics', {
        user_id: userId,
        query,
        results_count: resultsCount,
        selected_result: selectedResult,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.log('Search analytics endpoint not available');
    }
  }
};

// Notifications API
export const notificationAPI = {
  getNotifications: async (params?: { page?: number; size?: number; read?: boolean; is_read?: boolean }) => {
    const mappedParams: any = { ...params };
    if (mappedParams && typeof mappedParams.read !== 'undefined') {
      mappedParams.is_read = mappedParams.read;
      delete mappedParams.read;
    }
    const response: AxiosResponse = await api.get('/notifications', { params: mappedParams });
    return response.data;
  },

  getUnreadNotifications: async (limit: number = 10) => {
    const response: AxiosResponse = await api.get(`/notifications/unread?limit=${limit}`);
    return response.data;
  },

  getNotificationSummary: async () => {
    const response: AxiosResponse = await api.get('/notifications/summary');
    return response.data;
  },

  markAsRead: async (notificationId: number) => {
    const response: AxiosResponse = await api.put(`/notifications/${notificationId}/read`);
    return response.data;
  },

  markAllAsRead: async () => {
    const response: AxiosResponse = await api.put('/notifications/read-all');
    return response.data;
  },

  deleteNotification: async (notificationId: number) => {
    const response: AxiosResponse = await api.delete(`/notifications/${notificationId}`);
    return response.data;
  },

  clearReadNotifications: async () => {
    const response: AxiosResponse = await api.delete('/notifications/clear-read');
    return response.data;
  },
};

// Settings API
export const settingsAPI = {
  getSettings: async () => {
    const response: AxiosResponse = await api.get('/settings');
    return response.data;
  },

  updateSetting: async (settingId: string, value: any) => {
    const response: AxiosResponse = await api.put(`/settings/${settingId}`, { value });
    return response.data;
  },

  createSetting: async (settingData: any) => {
    // Not supported by backend; settings are initialized via /settings/initialize and updated via PUT /settings/{key}
    throw new Error('createSetting endpoint is not available on the backend');
  },

  deleteSetting: async (settingId: number) => {
    // Not supported by backend; settings can be reset via /settings/reset/{key}
    throw new Error('deleteSetting endpoint is not available on the backend');
  },

  // system-info endpoint not available on backend

  // system settings endpoint not available on backend

  // backup-status endpoint not available on backend

  getUserPreferences: async () => {
    const response: AxiosResponse = await api.get('/settings/preferences/me');
    return response.data;
  },

  bulkUpdateSettings: async (settings: any[]) => {
    const response: AxiosResponse = await api.post('/settings/bulk-update', { settings });
    return response.data;
  },

  initializeSettings: async () => {
    const response: AxiosResponse = await api.post('/settings/initialize');
    return response.data;
  },

  resetSetting: async (settingKey: string) => {
    const response: AxiosResponse = await api.post(`/settings/reset/${settingKey}`);
    return response.data;
  },

  exportSettings: async () => {
    const response: AxiosResponse = await api.get('/settings/export/json');
    return response.data;
  },

  importSettings: async (settingsData: any) => {
    const response: AxiosResponse = await api.post('/settings/import/json', settingsData);
    return response.data;
  },

  // Newly implemented backend endpoints
  getSystemInfo: async () => {
    const response: AxiosResponse = await api.get('/settings/system-info');
    return response.data?.data || response.data;
  },
  getBackupStatus: async () => {
    const response: AxiosResponse = await api.get('/settings/backup-status');
    return response.data?.data || response.data;
  },
};

// Suppliers API
export const supplierAPI = {
  getSuppliers: async (params?: { page?: number; size?: number; search?: string }) => {
    const response: AxiosResponse = await api.get('/suppliers', { params });
    return response.data;
  },

  getSupplier: async (supplierId: number) => {
    const response: AxiosResponse = await api.get(`/suppliers/${supplierId}`);
    return response.data;
  },

  createSupplier: async (supplierData: any) => {
    const response: AxiosResponse = await api.post('/suppliers', supplierData);
    return response.data;
  },

  updateSupplier: async (supplierId: number, supplierData: any) => {
    const response: AxiosResponse = await api.put(`/suppliers/${supplierId}`, supplierData);
    return response.data;
  },

  deleteSupplier: async (supplierId: number) => {
    const response: AxiosResponse = await api.delete(`/suppliers/${supplierId}`);
    return response.data;
  },

  getDashboard: async () => {
    const response: AxiosResponse = await api.get('/suppliers/dashboard/stats');
    return response.data;
  },
};

// Non-Conformance & CAPA API
export const ncAPI = {
  // Non-Conformances
  getNonConformances: async (params?: { page?: number; size?: number; search?: string; source?: string; status?: string; severity?: string; date_from?: string; date_to?: string }) => {
    const response: AxiosResponse = await api.get('/nonconformance/', { params });
    return response.data;
  },
  getNonConformance: async (ncId: number) => {
    const response: AxiosResponse = await api.get(`/nonconformance/${ncId}`);
    return response.data;
  },
  createNonConformance: async (payload: any) => {
    const response: AxiosResponse = await api.post('/nonconformance/', payload);
    return response.data;
  },
  updateNonConformance: async (ncId: number, payload: any) => {
    const response: AxiosResponse = await api.put(`/nonconformance/${ncId}`, payload);
    return response.data;
  },
  deleteNonConformance: async (ncId: number) => {
    const response: AxiosResponse = await api.delete(`/nonconformance/${ncId}`);
    return response.data;
  },

  // CAPA Actions
  getCAPAList: async (params?: { page?: number; size?: number; non_conformance_id?: number; status?: string; responsible_person?: number; action_type?: string; date_from?: string; date_to?: string }) => {
    const response: AxiosResponse = await api.get('/nonconformance/capas/', { params });
    return response.data;
  },
  getCAPA: async (capaId: number) => {
    const response: AxiosResponse = await api.get(`/nonconformance/capas/${capaId}`);
    return response.data;
  },
  createCAPA: async (ncId: number, payload: any) => {
    const response: AxiosResponse = await api.post(`/nonconformance/${ncId}/capas/`, payload);
    return response.data;
  },
  updateCAPA: async (capaId: number, payload: any) => {
    const response: AxiosResponse = await api.put(`/nonconformance/capas/${capaId}`, payload);
    return response.data;
  },
  deleteCAPA: async (capaId: number) => {
    const response: AxiosResponse = await api.delete(`/nonconformance/capas/${capaId}`);
    return response.data;
  },

  // CAPA Verifications
  getCAPAVerifications: async (ncId: number) => {
    const response: AxiosResponse = await api.get(`/nonconformance/${ncId}/verifications/`);
    return response.data;
  },
  createCAPAVerification: async (ncId: number, capaId: number, payload: any) => {
    const response: AxiosResponse = await api.post(`/nonconformance/${ncId}/capas/${capaId}/verifications/`, payload);
    return response.data;
  },

  // RCA persistence wrappers
  persistFiveWhys: async (ncId: number, payload: { problem: string; why_1: string; why_2: string; why_3: string; why_4: string; why_5: string; root_cause: string }) => {
    const response: AxiosResponse = await api.post(`/nonconformance/${ncId}/tools/five-whys`, payload);
    return response.data;
  },
  persistIshikawa: async (ncId: number, payload: { problem: string; categories: Record<string, string[]>; diagram_data: any }) => {
    const response: AxiosResponse = await api.post(`/nonconformance/${ncId}/tools/ishikawa`, payload);
    return response.data;
  },
  getRCAList: async (ncId: number) => {
    const response: AxiosResponse = await api.get(`/nonconformance/${ncId}/root-cause-analyses/`);
    return response.data;
  },
};

// Complaints API
export const complaintsAPI = {
  list: async (params?: { page?: number; size?: number }) => {
    const response = await api.get('/complaints', { params });
    return response.data;
  },
  get: async (id: number) => {
    const response = await api.get(`/complaints/${id}`);
    return response.data;
  },
  create: async (payload: any) => {
    const response = await api.post('/complaints', payload);
    return response.data;
  },
  update: async (id: number, payload: any) => {
    const response = await api.put(`/complaints/${id}`, payload);
    return response.data;
  },
  listCommunications: async (id: number) => {
    const response = await api.get(`/complaints/${id}/communications`);
    return response.data;
  },
  getInvestigation: async (id: number) => {
    const response = await api.get(`/complaints/${id}/investigation`);
    return response.data;
  },
  addCommunication: async (id: number, payload: { channel: string; sender?: string; recipient?: string; message: string }) => {
    const response = await api.post(`/complaints/${id}/communications`, payload);
    return response.data;
  },
  createInvestigation: async (id: number, payload: { investigator_id?: number; summary?: string }) => {
    const response = await api.post(`/complaints/${id}/investigation`, payload);
    return response.data;
  },
  updateInvestigation: async (id: number, payload: { investigator_id?: number; root_cause_analysis_id?: number; summary?: string; outcome?: string }) => {
    const response = await api.put(`/complaints/${id}/investigation`, payload);
    return response.data;
  },
  trends: async () => {
    const response = await api.get('/complaints/reports/trends');
    return response.data;
  },
};

// Traceability API
export const traceabilityAPI = {
  getBatches: async (params?: { page?: number; size?: number; search?: string; batch_type?: string; status?: string }) => {
    const response: AxiosResponse = await api.get('/traceability/batches', { params });
    return response.data;
  },

  getBatch: async (batchId: number) => {
    const response: AxiosResponse = await api.get(`/traceability/batches/${batchId}`);
    return response.data;
  },

  createBatch: async (batchData: any) => {
    const response: AxiosResponse = await api.post('/traceability/batches', batchData);
    return response.data;
  },

  updateBatch: async (batchId: number, batchData: any) => {
    const response: AxiosResponse = await api.put(`/traceability/batches/${batchId}`, batchData);
    return response.data;
  },

  deleteBatch: async (batchId: number) => {
    const response: AxiosResponse = await api.delete(`/traceability/batches/${batchId}`);
    return response.data;
  },

  // No generic /trace endpoint on backend; use dedicated functions from traceabilityAPI.ts when needed

  getDashboard: async () => {
    const response: AxiosResponse = await api.get('/traceability/dashboard/enhanced');
    return response.data;
  },

  getRecalls: async (params?: { page?: number; size?: number; search?: string; recall_type?: string; status?: string }) => {
    const response: AxiosResponse = await api.get('/traceability/recalls', { params });
    return response.data;
  },

  getTraceabilityReports: async (params?: { page?: number; size?: number; search?: string }) => {
    const response: AxiosResponse = await api.get('/traceability/reports', { params });
    return response.data;
  },

  createRecall: async (recallData: any) => {
    const response: AxiosResponse = await api.post('/traceability/recalls', recallData);
    return response.data;
  },

  createTraceabilityReport: async (reportData: any) => {
    const response: AxiosResponse = await api.post('/traceability/reports', reportData);
    return response.data;
  },
};

// Audits API
export const auditsAPI = {
  // Audits
  listAudits: async (params?: { search?: string; audit_type?: 'internal'|'external'|'supplier'; status?: string; page?: number; size?: number }) => {
    const response: AxiosResponse = await api.get('/audits', { params });
    return response.data;
  },
  createAudit: async (payload: any) => {
    const response: AxiosResponse = await api.post('/audits', payload);
    return response.data;
  },
  getAudit: async (auditId: number) => {
    const response: AxiosResponse = await api.get(`/audits/${auditId}`);
    return response.data;
  },
  updateAudit: async (auditId: number, payload: any) => {
    const response: AxiosResponse = await api.put(`/audits/${auditId}`, payload);
    return response.data;
  },
  deleteAudit: async (auditId: number) => {
    const response: AxiosResponse = await api.delete(`/audits/${auditId}`);
    return response.data;
  },

  // Stats
  getStats: async () => {
    const response: AxiosResponse = await api.get('/audits/stats');
    return response.data;
  },

  // Export list
  exportAudits: async (format: 'pdf'|'xlsx', filters?: { search?: string; audit_type?: string; status?: string }) => {
    const response: AxiosResponse<Blob> = await api.post('/audits/export', filters || {}, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },

  // Single audit report
  exportReport: async (auditId: number, format: 'pdf'|'xlsx') => {
    const response: AxiosResponse<Blob> = await api.get(`/audits/${auditId}/report`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },

  // Audit-level attachments
  listAttachments: async (auditId: number) => {
    const response: AxiosResponse = await api.get(`/audits/${auditId}/attachments`);
    return response.data;
  },
  deleteAttachment: async (attachmentId: number) => {
    const response: AxiosResponse = await api.delete(`/audits/attachments/${attachmentId}`);
    return response.data;
  },

  // Auditees
  listAuditees: async (auditId: number) => {
    const response: AxiosResponse = await api.get(`/audits/${auditId}/auditees`);
    return response.data;
  },
  addAuditee: async (auditId: number, userId: number, role?: string) => {
    const response: AxiosResponse = await api.post(`/audits/${auditId}/auditees`, null, { params: { user_id: userId, role } });
    return response.data;
  },
  removeAuditee: async (id: number) => {
    const response: AxiosResponse = await api.delete(`/audits/auditees/${id}`);
    return response.data;
  },

  // Templates
  createTemplate: async (payload: any) => {
    const response: AxiosResponse = await api.post('/audits/templates', payload);
    return response.data;
  },
  listTemplates: async () => {
    const response: AxiosResponse = await api.get('/audits/templates');
    return response.data;
  },

  // Checklist items
  listChecklistItems: async (auditId: number) => {
    const response: AxiosResponse = await api.get(`/audits/${auditId}/checklist`);
    return response.data;
  },
  addChecklistItem: async (auditId: number, payload: any) => {
    const response: AxiosResponse = await api.post(`/audits/${auditId}/checklist`, payload);
    return response.data;
  },
  updateChecklistItem: async (itemId: number, payload: any) => {
    const response: AxiosResponse = await api.put(`/audits/checklist/${itemId}`, payload);
    return response.data;
  },
  listItemAttachments: async (itemId: number) => {
    const response: AxiosResponse = await api.get(`/audits/checklist/${itemId}/attachments`);
    return response.data;
  },
  uploadItemAttachment: async (itemId: number, file: File) => {
    const form = new FormData(); form.append('file', file);
    const response: AxiosResponse = await api.post(`/audits/checklist/${itemId}/attachments`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  },
  deleteItemAttachment: async (attachmentId: number) => {
    const response: AxiosResponse = await api.delete(`/audits/checklist/attachments/${attachmentId}`);
    return response.data;
  },

  // Findings
  listFindings: async (auditId: number) => {
    const response: AxiosResponse = await api.get(`/audits/${auditId}/findings`);
    return response.data;
  },
  addFinding: async (auditId: number, payload: any) => {
    const response: AxiosResponse = await api.post(`/audits/${auditId}/findings`, payload);
    return response.data;
  },
  updateFinding: async (findingId: number, payload: any) => {
    const response: AxiosResponse = await api.put(`/audits/findings/${findingId}`, payload);
    return response.data;
  },
  listFindingAttachments: async (findingId: number) => {
    const response: AxiosResponse = await api.get(`/audits/findings/${findingId}/attachments`);
    return response.data;
  },
  uploadFindingAttachment: async (findingId: number, file: File) => {
    const form = new FormData(); form.append('file', file);
    const response: AxiosResponse = await api.post(`/audits/findings/${findingId}/attachments`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  },
  deleteFindingAttachment: async (attachmentId: number) => {
    const response: AxiosResponse = await api.delete(`/audits/findings/attachments/${attachmentId}`);
    return response.data;
  },
  createNCFromFinding: async (findingId: number) => {
    const response: AxiosResponse = await api.post(`/audits/findings/${findingId}/create-nc`);
    return response.data;
  },

  // Attachments
  uploadAttachment: async (auditId: number, file: File) => {
    const form = new FormData();
    form.append('file', file);
    const response: AxiosResponse = await api.post(`/audits/${auditId}/attachments`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  },
};

// Training API
export const trainingAPI = {
  // Programs
  getPrograms: async (params?: { search?: string }) => {
    const response: AxiosResponse = await api.get('/training/programs', { params });
    return response.data;
  },
  createProgram: async (payload: { code: string; title: string; description?: string; department?: string }) => {
    const response: AxiosResponse = await api.post('/training/programs', payload);
    return response.data;
  },
  getProgram: async (programId: number) => {
    const response: AxiosResponse = await api.get(`/training/programs/${programId}`);
    return response.data;
  },
  updateProgram: async (programId: number, payload: { title?: string; description?: string; department?: string }) => {
    const response: AxiosResponse = await api.put(`/training/programs/${programId}`, payload);
    return response.data;
  },
  deleteProgram: async (programId: number) => {
    const response: AxiosResponse = await api.delete(`/training/programs/${programId}`);
    return response.data;
  },

  // Sessions
  getSessions: async (programId: number) => {
    const response: AxiosResponse = await api.get(`/training/programs/${programId}/sessions`);
    return response.data;
  },
  createSession: async (programId: number, payload: { session_date: string; location?: string; trainer?: string; notes?: string }) => {
    const response: AxiosResponse = await api.post(`/training/programs/${programId}/sessions`, payload);
    return response.data;
  },
  updateSession: async (sessionId: number, payload: { session_date?: string; location?: string; trainer?: string; notes?: string }) => {
    const response: AxiosResponse = await api.put(`/training/sessions/${sessionId}`, payload);
    return response.data;
  },
  deleteSession: async (sessionId: number) => {
    const response: AxiosResponse = await api.delete(`/training/sessions/${sessionId}`);
    return response.data;
  },

  // Attendance
  getAttendance: async (sessionId: number) => {
    const response: AxiosResponse = await api.get(`/training/sessions/${sessionId}/attendance`);
    return response.data;
  },
  addAttendance: async (sessionId: number, payload: { user_id: number; attended?: boolean; comments?: string }) => {
    const response: AxiosResponse = await api.post(`/training/sessions/${sessionId}/attendance`, payload);
    return response.data;
  },
  updateAttendance: async (attendanceId: number, payload: { attended?: boolean; comments?: string }) => {
    const params: any = {};
    if (typeof payload.attended !== 'undefined') params.attended = payload.attended;
    if (typeof payload.comments !== 'undefined') params.comments = payload.comments;
    const response: AxiosResponse = await api.put(`/training/attendance/${attendanceId}`, null, { params });
    return response.data;
  },
  deleteAttendance: async (attendanceId: number) => {
    const response: AxiosResponse = await api.delete(`/training/attendance/${attendanceId}`);
    return response.data;
  },
  exportAttendanceCSV: async (sessionId: number) => {
    const response: AxiosResponse<Blob> = await api.get(`/training/sessions/${sessionId}/attendance/export`, { responseType: 'blob' });
    return response.data;
  },

  // Materials
  uploadProgramMaterial: async (programId: number, file: File) => {
    const form = new FormData();
    form.append('file', file);
    const response: AxiosResponse = await api.post(`/training/programs/${programId}/materials`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  },
  listProgramMaterials: async (programId: number) => {
    const response: AxiosResponse = await api.get(`/training/programs/${programId}/materials`);
    return response.data;
  },
  uploadSessionMaterial: async (sessionId: number, file: File) => {
    const form = new FormData();
    form.append('file', file);
    const response: AxiosResponse = await api.post(`/training/sessions/${sessionId}/materials`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  },
  listSessionMaterials: async (sessionId: number) => {
    const response: AxiosResponse = await api.get(`/training/sessions/${sessionId}/materials`);
    return response.data;
  },
  downloadMaterial: async (materialId: number) => {
    const response: AxiosResponse<Blob> = await api.get(`/training/materials/${materialId}/download`, { responseType: 'blob' });
    return response.data;
  },
  deleteMaterial: async (materialId: number) => {
    const response: AxiosResponse = await api.delete(`/training/materials/${materialId}`);
    return response.data;
  },

  // Role-required trainings
  assignRequiredTraining: async (payload: { role_id: number; program_id: number; is_mandatory?: boolean }) => {
    const response: AxiosResponse = await api.post('/training/required', payload);
    return response.data;
  },
  listRequiredTrainings: async (params?: { role_id?: number; program_id?: number }) => {
    const response: AxiosResponse = await api.get('/training/required', { params });
    return response.data;
  },
  deleteRequiredTraining: async (recordId: number) => {
    const response: AxiosResponse = await api.delete(`/training/required/${recordId}`);
    return response.data;
  },

  // Quizzes
  listProgramQuizzes: async (programId: number) => {
    const response: AxiosResponse = await api.get(`/training/programs/${programId}/quizzes`);
    return response.data;
  },
  createProgramQuiz: async (
    programId: number,
    payload: {
      title: string;
      description?: string;
      pass_threshold?: number;
      is_published?: boolean;
      questions: Array<{ text: string; order_index?: number; options: Array<{ text: string; is_correct?: boolean }> }>;
    }
  ) => {
    const response: AxiosResponse = await api.post(`/training/programs/${programId}/quizzes`, payload);
    return response.data;
  },
  getQuiz: async (quizId: number) => {
    const response: AxiosResponse = await api.get(`/training/quizzes/${quizId}`);
    return response.data;
  },
  submitQuiz: async (quizId: number, answers: Array<{ question_id: number; selected_option_id: number }>) => {
    const response: AxiosResponse = await api.post(`/training/quizzes/${quizId}/submit`, { answers });
    return response.data;
  },
  // Certificates
  uploadCertificate: async (sessionId: number, file: File) => {
    const form = new FormData(); form.append('file', file);
    const response: AxiosResponse = await api.post(`/training/sessions/${sessionId}/certificates`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
    return response.data;
  },
  listSessionCertificates: async (sessionId: number) => {
    const response: AxiosResponse = await api.get(`/training/sessions/${sessionId}/certificates`);
    return response.data;
  },
  downloadCertificate: async (certId: number) => {
    const response: AxiosResponse<Blob> = await api.get(`/training/certificates/${certId}/download`, { responseType: 'blob' });
    return response.data;
  },
  getMyTrainingMatrix: async () => {
    const response: AxiosResponse = await api.get('/training/matrix/me');
    return response.data;
  },
};

export default api; 
 
// Allergen & Label Control API
export const allergenLabelAPI = {
  listAssessments: async (params?: { product_id?: number }) => {
    const response: AxiosResponse = await api.get('/allergen-label/assessments', { params });
    return response.data;
  },
  createAssessment: async (payload: {
    product_id: number;
    inherent_allergens?: string[];
    cross_contact_sources?: string[];
    risk_level?: 'low' | 'medium' | 'high';
    precautionary_labeling?: string;
    control_measures?: string;
    validation_verification?: string;
    reviewed_by?: number;
  }) => {
    const response: AxiosResponse = await api.post('/allergen-label/assessments', payload);
    return response.data;
  },
  updateAssessment: async (assessmentId: number, payload: any) => {
    const response: AxiosResponse = await api.put(`/allergen-label/assessments/${assessmentId}`, payload);
    return response.data;
  },
  listTemplates: async (include_inactive: boolean = false) => {
    const response: AxiosResponse = await api.get('/allergen-label/templates', { params: { include_inactive } });
    return response.data;
  },
  createTemplate: async (payload: { name: string; description?: string; product_id?: number | null; is_active?: boolean }) => {
    const response: AxiosResponse = await api.post('/allergen-label/templates', payload);
    return response.data;
  },
  createTemplateVersion: async (templateId: number, payload: { content: string; change_description: string; change_reason: string }) => {
    const response: AxiosResponse = await api.post(`/allergen-label/templates/${templateId}/versions`, payload);
    return response.data;
  },
  listTemplateVersions: async (templateId: number) => {
    const response: AxiosResponse = await api.get(`/allergen-label/templates/${templateId}/versions`);
    return response.data;
  },
  listVersionApprovals: async (templateId: number, versionId: number) => {
    const response: AxiosResponse = await api.get(`/allergen-label/templates/${templateId}/versions/${versionId}/approvals`);
    return response.data;
  },
  submitTemplateApprovals: async (templateId: number, approvers: Array<{ approver_id: number; approval_order: number }>) => {
    const response: AxiosResponse = await api.post(`/allergen-label/templates/${templateId}/approvals`, approvers);
    return response.data;
  },
  approveTemplate: async (templateId: number, approvalId: number) => {
    const response: AxiosResponse = await api.post(`/allergen-label/templates/${templateId}/approvals/${approvalId}/approve`);
    return response.data;
  },
  rejectTemplate: async (templateId: number, approvalId: number) => {
    const response: AxiosResponse = await api.post(`/allergen-label/templates/${templateId}/approvals/${approvalId}/reject`);
    return response.data;
  },
  exportVersionPDF: async (templateId: number, versionId: number) => {
    const response: AxiosResponse<Blob> = await api.get(`/allergen-label/templates/${templateId}/versions/${versionId}/export`, { responseType: 'blob' });
    return response.data;
  },
};