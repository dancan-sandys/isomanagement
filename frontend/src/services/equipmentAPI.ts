import api from './api';

export const equipmentAPI = {
  // Equipment
  list: async () => {
    const res = await api.get('/equipment');
    return res.data;
  },
  create: async (payload: { name: string; equipment_type: string; serial_number?: string; location?: string; notes?: string }) => {
    const res = await api.post('/equipment', payload);
    return res.data;
  },

  // Maintenance
  listMaintenancePlans: async (equipmentId: number) => {
    const res = await api.get(`/equipment/${equipmentId}/maintenance-plans`);
    return res.data;
  },
  createMaintenancePlan: async (equipmentId: number, payload: { frequency_days: number; maintenance_type: 'preventive'|'corrective'; notes?: string }) => {
    const res = await api.post(`/equipment/${equipmentId}/maintenance-plans`, payload);
    return res.data;
  },
  createWorkOrder: async (payload: { equipment_id: number; plan_id?: number; title: string; description?: string }) => {
    const res = await api.post('/equipment/work-orders', payload);
    return res.data;
  },
  listWorkOrders: async (params?: { equipment_id?: number; plan_id?: number }) => {
    const res = await api.get('/equipment/work-orders', { params });
    return res.data;
  },
  completeWorkOrder: async (workOrderId: number) => {
    const res = await api.post(`/equipment/work-orders/${workOrderId}/complete`);
    return res.data;
  },

  // Calibration
  listCalibrationPlans: async (equipmentId: number) => {
    const res = await api.get(`/equipment/${equipmentId}/calibration-plans`);
    return res.data;
  },
  createCalibrationPlan: async (equipmentId: number, payload: { schedule_date: string; notes?: string }) => {
    const res = await api.post(`/equipment/${equipmentId}/calibration-plans`, payload);
    return res.data;
  },
  uploadCalibrationCertificate: async (planId: number, file: File) => {
    const form = new FormData(); form.append('file', file);
    const res = await api.post(`/equipment/calibration-plans/${planId}/records`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
    return res.data;
  },
};


