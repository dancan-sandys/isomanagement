import { api } from './api';

export interface ProcessCreatePayload {
  batch_id: number;
  process_type: 'fresh_milk' | 'yoghurt' | 'mala' | 'cheese';
  operator_id?: number;
  spec: any;
}

const productionAPI = {
  createProcess: async (payload: ProcessCreatePayload) => {
    const res = await api.post('/production/process', payload);
    return res.data;
  },
  addLog: async (processId: number, payload: any) => {
    const res = await api.post(`/production/${processId}/log`, payload);
    return res.data;
  },
  recordYield: async (processId: number, payload: { output_qty: number; expected_qty?: number; unit: string }) => {
    const res = await api.post(`/production/${processId}/yield`, payload);
    return res.data;
  },
  transfer: async (processId: number, payload: { quantity: number; unit: string; location?: string; lot_number?: string; verified_by?: number }) => {
    const res = await api.post(`/production/${processId}/transfer`, payload);
    return res.data;
  },
  aging: async (processId: number, payload: any) => {
    const res = await api.post(`/production/${processId}/aging`, payload);
    return res.data;
  },
  getProcess: async (processId: number) => {
    const res = await api.get(`/production/${processId}`);
    return res.data;
  },
  analytics: async (process_type?: string) => {
    const res = await api.get('/production/analytics', { params: { process_type } });
    return res.data;
  },
};

export default productionAPI;

