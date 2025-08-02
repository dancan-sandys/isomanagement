import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

console.log('API Base URL:', API_BASE_URL);

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
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

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Try to refresh token
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          
          // Retry the original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// API response types
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    // Use URLSearchParams for proper form encoding
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    try {
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response.data;
    } catch (error: any) {
      console.error('Login API Error:', error);
      console.error('Error response:', error.response);
      
      if (error.response?.status === 401) {
        throw new Error('Invalid username or password');
      } else if (error.response?.status === 423) {
        throw new Error('Account is locked. Please contact administrator.');
      } else if (error.response?.status === 400) {
        throw new Error('Inactive user account');
      } else if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
        throw new Error('Cannot connect to server. Please check if the backend is running.');
      } else {
        throw new Error(error.response?.data?.detail || 'Login failed. Please try again.');
      }
    }
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },

  refresh: async (refreshToken: string) => {
    const response = await api.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  me: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Users API
export const usersAPI = {
  getUsers: async (params?: {
    page?: number;
    size?: number;
    search?: string;
    role?: string;
  }) => {
    const response = await api.get('/users/', { params });
    return response.data;
  },

  getUser: async (id: number) => {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },

  createUser: async (userData: any) => {
    const response = await api.post('/users/', userData);
    return response.data;
  },

  updateUser: async (id: number, userData: any) => {
    const response = await api.put(`/users/${id}`, userData);
    return response.data;
  },

  deleteUser: async (id: number) => {
    const response = await api.delete(`/users/${id}`);
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
  }) => {
    const response = await api.get('/documents/', { params });
    return response.data;
  },

  getDocument: async (id: number) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },

  createDocument: async (formData: FormData) => {
    const response = await api.post('/documents/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  updateDocument: async (id: number, formData: FormData) => {
    const response = await api.put(`/documents/${id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  deleteDocument: async (id: number) => {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  },

  downloadDocument: async (id: number) => {
    const response = await api.get(`/documents/${id}/download`, {
      responseType: 'blob',
    });
    return response;
  },

  uploadFile: async (id: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/documents/${id}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// HACCP API
export const haccpAPI = {
  getProducts: async (params?: {
    page?: number;
    size?: number;
    search?: string;
  }) => {
    const response = await api.get('/haccp/products/', { params });
    return response.data;
  },

  getProduct: async (id: number) => {
    const response = await api.get(`/haccp/products/${id}`);
    return response.data;
  },

  createProduct: async (productData: any) => {
    const response = await api.post('/haccp/products', productData);
    return response.data;
  },

  createProcessFlow: async (productId: number, flowData: any) => {
    const response = await api.post(`/haccp/products/${productId}/process-flows`, flowData);
    return response.data;
  },

  createHazard: async (productId: number, hazardData: any) => {
    const response = await api.post(`/haccp/products/${productId}/hazards`, hazardData);
    return response.data;
  },

  createCCP: async (productId: number, ccpData: any) => {
    const response = await api.post(`/haccp/products/${productId}/ccps`, ccpData);
    return response.data;
  },

  createMonitoringLog: async (ccpId: number, logData: any) => {
    const response = await api.post(`/haccp/ccps/${ccpId}/monitoring-logs`, logData);
    return response.data;
  },

  getMonitoringLogs: async (ccpId: number) => {
    const response = await api.get(`/haccp/ccps/${ccpId}/monitoring-logs`);
    return response.data;
  },

  createVerificationLog: async (ccpId: number, logData: any) => {
    const response = await api.post(`/haccp/ccps/${ccpId}/verification-logs`, logData);
    return response.data;
  },

  getDashboard: async () => {
    const response = await api.get('/haccp/dashboard');
    return response.data;
  },
};

// PRP API
export const prpAPI = {
  getPrograms: async (params?: {
    page?: number;
    size?: number;
    category?: string;
    status?: string;
    search?: string;
  }) => {
    const response = await api.get('/prp/programs/', { params });
    return response.data;
  },

  createProgram: async (programData: any) => {
    const response = await api.post('/prp/programs', programData);
    return response.data;
  },

  getChecklists: async (programId: number, params?: {
    page?: number;
    size?: number;
    status?: string;
  }) => {
    const response = await api.get(`/prp/programs/${programId}/checklists`, { params });
    return response.data;
  },

  createChecklist: async (programId: number, checklistData: any) => {
    const response = await api.post(`/prp/programs/${programId}/checklists`, checklistData);
    return response.data;
  },

  getDashboard: async () => {
    const response = await api.get('/prp/dashboard');
    return response.data;
  },
};

// Supplier API
export const supplierAPI = {
  getSuppliers: async (params?: {
    page?: number;
    size?: number;
    category?: string;
    status?: string;
    search?: string;
  }) => {
    const response = await api.get('/suppliers/suppliers/', { params });
    return response.data;
  },

  createSupplier: async (supplierData: any) => {
    const response = await api.post('/suppliers/suppliers', supplierData);
    return response.data;
  },

  getSupplier: async (id: number) => {
    const response = await api.get(`/suppliers/suppliers/${id}`);
    return response.data;
  },

  getMaterials: async (supplierId: number, params?: {
    page?: number;
    size?: number;
  }) => {
    const response = await api.get(`/suppliers/suppliers/${supplierId}/materials`, { params });
    return response.data;
  },

  createMaterial: async (supplierId: number, materialData: any) => {
    const response = await api.post(`/suppliers/suppliers/${supplierId}/materials`, materialData);
    return response.data;
  },

  getEvaluations: async (supplierId: number, params?: {
    page?: number;
    size?: number;
  }) => {
    const response = await api.get(`/suppliers/suppliers/${supplierId}/evaluations`, { params });
    return response.data;
  },

  createEvaluation: async (supplierId: number, evaluationData: any) => {
    const response = await api.post(`/suppliers/suppliers/${supplierId}/evaluations`, evaluationData);
    return response.data;
  },

  getDashboard: async () => {
    const response = await api.get('/suppliers/suppliers/dashboard');
    return response.data;
  },
};



// Dashboard API
export const dashboardAPI = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },

  getRecentActivity: async () => {
    const response = await api.get('/dashboard/recent-activity');
    return response.data;
  },

  getComplianceMetrics: async () => {
    const response = await api.get('/dashboard/compliance-metrics');
    return response.data;
  },

  getSystemStatus: async () => {
    const response = await api.get('/dashboard/system-status');
    return response.data;
  },
};

// Traceability API
export const traceabilityAPI = {
  // Batch Management
  getBatches: async (params?: {
    skip?: number;
    limit?: number;
    batch_type?: string;
    status?: string;
    product_name?: string;
    search?: string;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.batch_type) queryParams.append('batch_type', params.batch_type);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.product_name) queryParams.append('product_name', params.product_name);
    if (params?.search) queryParams.append('search', params.search);
    
    const response = await api.get(`/traceability/batches?${queryParams}`);
    return response.data;
  },

  createBatch: async (batchData: any) => {
    const response = await api.post('/traceability/batches', batchData);
    return response.data;
  },

  getBatch: async (batchId: number) => {
    const response = await api.get(`/traceability/batches/${batchId}`);
    return response.data;
  },

  // Traceability Links
  createTraceabilityLink: async (batchId: number, linkData: any) => {
    const response = await api.post(`/traceability/batches/${batchId}/links`, linkData);
    return response.data;
  },

  // Recall Management
  getRecalls: async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    recall_type?: string;
    search?: string;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);
    if (params?.recall_type) queryParams.append('recall_type', params.recall_type);
    if (params?.search) queryParams.append('search', params.search);
    
    const response = await api.get(`/traceability/recalls?${queryParams}`);
    return response.data;
  },

  createRecall: async (recallData: any) => {
    const response = await api.post('/traceability/recalls', recallData);
    return response.data;
  },

  getRecall: async (recallId: number) => {
    const response = await api.get(`/traceability/recalls/${recallId}`);
    return response.data;
  },

  updateRecallStatus: async (recallId: number, statusData: any) => {
    const response = await api.put(`/traceability/recalls/${recallId}/status`, statusData);
    return response.data;
  },

  // Traceability Reports
  createTraceabilityReport: async (traceData: any) => {
    const response = await api.post('/traceability/trace', traceData);
    return response.data;
  },

  getTraceabilityReports: async (params?: {
    skip?: number;
    limit?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    
    const response = await api.get(`/traceability/trace/reports?${queryParams}`);
    return response.data;
  },

  // Dashboard
  getDashboard: async () => {
    const response = await api.get('/traceability/dashboard');
    return response.data;
  },
};

export default api; 