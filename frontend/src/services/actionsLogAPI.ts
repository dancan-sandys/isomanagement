import api from './api';
import { AxiosResponse } from 'axios';
import {
  ActionLog,
  ActionLogCreate,
  ActionLogUpdate,
  ActionsAnalytics,
  ActionsDashboard,
  ActionLogFilters,
  ApiResponse
} from '../types/actionsLog';

// Remove empty strings, null, and undefined from params
const cleanParams = (obj?: Record<string, any>) => {
  if (!obj) return undefined;
  const out: Record<string, any> = {};
  Object.entries(obj).forEach(([k, v]) => {
    if (v === undefined || v === null) return;
    if (typeof v === 'string' && v.trim() === '') return;
    if (Array.isArray(v) && v.length === 0) return;
    out[k] = v;
  });
  return out;
};

export const actionsLogAPI = {
  // Action Management
  getActions: async (params?: ActionLogFilters) => {
    const response: AxiosResponse = await api.get('/actions-log/actions', { 
      params: cleanParams(params) 
    });
    return response.data as ActionLog[];
  },

  getAction: async (actionId: number) => {
    const response: AxiosResponse = await api.get(`/actions-log/actions/${actionId}`);
    return response.data as ActionLog;
  },

  createAction: async (actionData: ActionLogCreate) => {
    const response: AxiosResponse = await api.post('/actions-log/actions', actionData);
    return response.data as ActionLog;
  },

  updateAction: async (actionId: number, actionData: ActionLogUpdate) => {
    const response: AxiosResponse = await api.put(`/actions-log/actions/${actionId}`, actionData);
    return response.data as ActionLog;
  },

  deleteAction: async (actionId: number) => {
    const response: AxiosResponse = await api.delete(`/actions-log/actions/${actionId}`);
    return response.data;
  },

  // Analytics and Dashboard
  getAnalytics: async () => {
    const response: AxiosResponse = await api.get('/actions-log/analytics');
    return response.data as ActionsAnalytics;
  },

  getDashboard: async () => {
    const response: AxiosResponse = await api.get('/actions-log/dashboard');
    return response.data as ActionsDashboard;
  },

  // Specialized endpoints
  getCriticalActions: async () => {
    const response: AxiosResponse = await api.get('/actions-log/critical');
    return response.data as ActionLog[];
  },

  getRecentActions: async (limit: number = 10) => {
    const response: AxiosResponse = await api.get('/actions-log/recent', {
      params: { limit }
    });
    return response.data as ActionLog[];
  },

  getOverdueActions: async () => {
    const response: AxiosResponse = await api.get('/actions-log/overdue');
    return response.data as ActionLog[];
  },

  // Progress tracking
  getActionProgress: async (actionId: number) => {
    const response: AxiosResponse = await api.get(`/actions-log/actions/${actionId}/progress`);
    return response.data;
  },

  addProgressUpdate: async (actionId: number, progressData: any) => {
    const response: AxiosResponse = await api.post(`/actions-log/actions/${actionId}/progress`, progressData);
    return response.data;
  },

  // Management Review Integration
  getActionsBySource: async (source: string, sourceId?: number) => {
    const response: AxiosResponse = await api.get(`/actions-log/by-source/${source}`, {
      params: sourceId ? { source_id: sourceId } : {}
    });
    return response.data as ActionLog[];
  },

  getManagementReviewActions: async (reviewId: number) => {
    const response: AxiosResponse = await api.get(`/actions-log/management-review/${reviewId}`);
    return response.data as ActionLog[];
  }
};

export default actionsLogAPI;