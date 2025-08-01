import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

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
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
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
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
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

  createDocument: async (documentData: any) => {
    const response = await api.post('/documents/', documentData);
    return response.data;
  },

  updateDocument: async (id: number, documentData: any) => {
    const response = await api.put(`/documents/${id}`, documentData);
    return response.data;
  },

  deleteDocument: async (id: number) => {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  },

  uploadFile: async (file: File, documentId: number) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/documents/${documentId}/upload`, formData, {
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

  getProcessFlows: async (productId: number) => {
    const response = await api.get(`/haccp/products/${productId}/process-flows`);
    return response.data;
  },

  getHazards: async (processFlowId: number) => {
    const response = await api.get(`/haccp/process-flows/${processFlowId}/hazards`);
    return response.data;
  },

  getCCPs: async (processFlowId: number) => {
    const response = await api.get(`/haccp/process-flows/${processFlowId}/ccps`);
    return response.data;
  },
};

// PRP API
export const prpAPI = {
  getPrograms: async (params?: {
    page?: number;
    size?: number;
    category?: string;
  }) => {
    const response = await api.get('/prp/programs/', { params });
    return response.data;
  },

  getChecklists: async (programId: number) => {
    const response = await api.get(`/prp/programs/${programId}/checklists`);
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
};

export default api; 