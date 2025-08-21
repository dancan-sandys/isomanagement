import { api } from './api';

export type ActionStatus = 'open' | 'in_progress' | 'completed' | 'verified' | 'cancelled';
export type ActionSource = 'interested_party' | 'swot' | 'pestel' | 'risk_opportunity' | 'management_review' | 'capa';
export type ActionPriority = 'low' | 'medium' | 'high' | 'critical';

const actionsAPI = {
  list: async (params?: { source?: ActionSource; status?: ActionStatus; priority?: ActionPriority }) => {
    const res = await api.get('/actions/actions-log', { params });
    return res.data;
  },
  update: async (id: number, payload: Partial<{ status: ActionStatus; priority: ActionPriority; owner_id: number; due_date: string }>) => {
    const res = await api.put(`/actions/actions-log/${id}`, payload);
    return res.data;
  },
};

export default actionsAPI;

