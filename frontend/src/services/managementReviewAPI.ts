import api from './api';
import { AxiosResponse } from 'axios';

export interface MRPayload {
  title: string;
  review_date?: string;
  attendees?: string;
  inputs?: string;
  status?: 'planned' | 'in_progress' | 'completed';
  next_review_date?: string;
  agenda?: Array<{ topic: string; discussion?: string; decision?: string; order_index?: number }>;
}

const managementReviewAPI = {
  list: async (params?: { page?: number; size?: number }) => {
    const resp: AxiosResponse = await api.get('/management-reviews', { params });
    return resp.data;
  },
  get: async (id: number) => {
    const resp: AxiosResponse = await api.get(`/management-reviews/${id}`);
    return resp.data;
  },
  create: async (payload: MRPayload) => {
    const resp: AxiosResponse = await api.post('/management-reviews', payload);
    return resp.data;
  },
  update: async (id: number, payload: Partial<MRPayload>) => {
    const resp: AxiosResponse = await api.put(`/management-reviews/${id}`, payload);
    return resp.data;
  },
  addAction: async (id: number, payload: { title: string; description?: string; assigned_to?: number; due_date?: string }) => {
    const resp: AxiosResponse = await api.post(`/management-reviews/${id}/actions`, payload);
    return resp.data;
  },
  listActions: async (id: number) => {
    const resp: AxiosResponse = await api.get(`/management-reviews/${id}/actions`);
    return resp.data;
  },
  completeAction: async (actionId: number) => {
    const resp: AxiosResponse = await api.post(`/management-reviews/actions/${actionId}/complete`);
    return resp.data;
  },
};

export default managementReviewAPI;


