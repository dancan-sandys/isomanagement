import api from './api';
import { AxiosResponse } from 'axios';

export interface RiskListParams {
  page?: number;
  size?: number;
  search?: string;
  item_type?: 'risk' | 'opportunity';
  category?: string;
  classification?: 'food_safety' | 'business' | 'customer';
  status?: string;
  severity?: string;
  likelihood?: string;
  detectability?: 'easily_detectable' | 'moderately_detectable' | 'difficult' | 'very_difficult' | 'almost_undetectable';
  assigned_to?: number;
  date_from?: string;
  date_to?: string;
}

export const riskAPI = {
  list: async (params?: RiskListParams) => {
    const response: AxiosResponse = await api.get('/risk', { params });
    return response.data;
  },
  get: async (id: number) => {
    const response: AxiosResponse = await api.get(`/risk/${id}`);
    return response.data;
  },
  create: async (payload: any) => {
    const response: AxiosResponse = await api.post('/risk', payload);
    return response.data;
  },
  update: async (id: number, payload: any) => {
    const response: AxiosResponse = await api.put(`/risk/${id}`, payload);
    return response.data;
  },
  progress: async (id: number) => {
    const response: AxiosResponse = await api.get(`/risk/${id}/progress`);
    return response.data;
  },
  remove: async (id: number) => {
    const response: AxiosResponse = await api.delete(`/risk/${id}`);
    return response.data;
  },
  stats: async () => {
    const response: AxiosResponse = await api.get('/risk/stats/overview');
    return response.data;
  },
  addAction: async (id: number, payload: { title: string; description?: string; assigned_to?: number; due_date?: string }) => {
    const response: AxiosResponse = await api.post(`/risk/${id}/actions`, payload);
    return response.data;
  },
  listActions: async (id: number) => {
    const response: AxiosResponse = await api.get(`/risk/${id}/actions`);
    return response.data;
  },
  completeAction: async (actionId: number) => {
    const response: AxiosResponse = await api.post(`/risk/actions/${actionId}/complete`);
    return response.data;
  },
  updateAction: async (actionId: number, payload: any) => {
    const response: AxiosResponse = await api.put(`/risk/actions/${actionId}`, payload);
    return response.data;
  },
  deleteAction: async (actionId: number) => {
    const response: AxiosResponse = await api.delete(`/risk/actions/${actionId}`);
    return response.data;
  },
};

export default riskAPI;


