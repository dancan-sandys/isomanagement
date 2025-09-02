import { AxiosResponse } from 'axios';
import { api } from './api';

export interface DepartmentPayload {
  department_code: string;
  name: string;
  description?: string;
  parent_department_id?: number;
  manager_id?: number;
  status?: string;
  color_code?: string;
  raci_json?: Record<string, any>;
  governance_notes?: string;
  created_by?: number;
}

export const departmentsAPI = {
  list: async (params?: { page?: number; size?: number; search?: string; status_filter?: string }) => {
    const filteredParams: any = {};
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') filteredParams[k] = v;
      });
    }
    const response: AxiosResponse = await api.get('/departments/', { params: filteredParams });
    return response.data;
  },
  get: async (departmentId: number) => {
    const response: AxiosResponse = await api.get(`/departments/${departmentId}`);
    return response.data;
  },
  create: async (payload: DepartmentPayload) => {
    const response: AxiosResponse = await api.post('/departments/', payload);
    return response.data;
  },
  update: async (departmentId: number, payload: Partial<DepartmentPayload>) => {
    const response: AxiosResponse = await api.put(`/departments/${departmentId}`, payload);
    return response.data;
  },
  remove: async (departmentId: number) => {
    const response: AxiosResponse = await api.delete(`/departments/${departmentId}`);
    return response.data;
  },
  listUsers: async (departmentId: number) => {
    const response: AxiosResponse = await api.get(`/departments/${departmentId}/users`);
    return response.data;
  },
  assignUser: async (departmentId: number, payload: { user_id: number; role?: string; assigned_from?: string; assigned_until?: string; is_active?: boolean }) => {
    const response: AxiosResponse = await api.post(`/departments/${departmentId}/users`, payload);
    return response.data;
  },
  unassignUser: async (departmentId: number, userId: number) => {
    const response: AxiosResponse = await api.delete(`/departments/${departmentId}/users/${userId}`);
    return response.data;
  },
};