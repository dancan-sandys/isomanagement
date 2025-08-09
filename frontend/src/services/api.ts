import axios, { AxiosResponse } from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
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

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(
            `${process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'}/auth/refresh`,
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
    const response: AxiosResponse = await api.post('/auth/refresh', { refresh_token: refreshToken });
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

  resetPassword: async (userId: number) => {
    const response: AxiosResponse = await api.post(`/users/${userId}/reset-password`);
    return response.data;
  },

  getDashboard: async () => {
    const response: AxiosResponse = await api.get('/users/dashboard');
    return response.data;
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

  getVersionHistory: async (documentId: number) => {
    const response: AxiosResponse = await api.get(`/documents/${documentId}/versions`);
    return response.data;
  },

  getSpecificVersion: async (documentId: number, versionId: number) => {
    const response: AxiosResponse = await api.get(`/documents/${documentId}/versions/${versionId}`);
    return response.data;
  },

  approveVersion: async (documentId: number, versionId: number, comments?: string) => {
    const formData = new FormData();
    if (comments) {
      formData.append('comments', comments);
    }
    
    const response: AxiosResponse = await api.post(
      `/documents/${documentId}/versions/${versionId}/approve`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
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
    return response.data;
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
    const response: AxiosResponse = await api.get('/documents/templates', { params });
    return response.data;
  },

  getDocumentTemplate: async (templateId: number) => {
    const response: AxiosResponse = await api.get(`/documents/templates/${templateId}`);
    return response.data;
  },

  createDocumentTemplate: async (templateData: any) => {
    const response: AxiosResponse = await api.post('/documents/templates', templateData);
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
    const response: AxiosResponse = await api.get('/dashboard');
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
};

// Notifications API
export const notificationAPI = {
  getNotifications: async (params?: { page?: number; size?: number; read?: boolean }) => {
    const response: AxiosResponse = await api.get('/notifications', { params });
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
    const response: AxiosResponse = await api.post(`/notifications/${notificationId}/read`);
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

  updateSetting: async (settingId: number, value: any) => {
    const response: AxiosResponse = await api.put(`/settings/${settingId}`, { value });
    return response.data;
  },

  createSetting: async (settingData: any) => {
    const response: AxiosResponse = await api.post('/settings', settingData);
    return response.data;
  },

  deleteSetting: async (settingId: number) => {
    const response: AxiosResponse = await api.delete(`/settings/${settingId}`);
    return response.data;
  },

  getSystemInfo: async () => {
    const response: AxiosResponse = await api.get('/settings/system-info');
    return response.data;
  },

  updateSystemSettings: async (settings: any) => {
    const response: AxiosResponse = await api.put('/settings/system', settings);
    return response.data;
  },

  getBackupStatus: async () => {
    const response: AxiosResponse = await api.get('/settings/backup-status');
    return response.data;
  },

  getUserPreferences: async () => {
    const response: AxiosResponse = await api.get('/settings/user-preferences');
    return response.data;
  },

  bulkUpdateSettings: async (settings: any[]) => {
    const response: AxiosResponse = await api.put('/settings/bulk-update', { settings });
    return response.data;
  },

  initializeSettings: async () => {
    const response: AxiosResponse = await api.post('/settings/initialize');
    return response.data;
  },

  resetSetting: async (settingKey: string) => {
    const response: AxiosResponse = await api.post(`/settings/${settingKey}/reset`);
    return response.data;
  },

  exportSettings: async () => {
    const response: AxiosResponse = await api.get('/settings/export');
    return response.data;
  },

  importSettings: async (settingsData: any) => {
    const response: AxiosResponse = await api.post('/settings/import', settingsData);
    return response.data;
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
    const response: AxiosResponse = await api.get('/suppliers/dashboard');
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

  getTraceabilityChain: async (batchId: number) => {
    const response: AxiosResponse = await api.get(`/traceability/batches/${batchId}/trace`);
    return response.data;
  },

  getDashboard: async () => {
    const response: AxiosResponse = await api.get('/traceability/dashboard');
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

export default api; 