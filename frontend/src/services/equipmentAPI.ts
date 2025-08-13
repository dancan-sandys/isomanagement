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
  get: async (id: number) => {
    const res = await api.get(`/equipment/${id}`);
    return res.data;
  },
  update: async (id: number, payload: { name?: string; equipment_type?: string; serial_number?: string; location?: string; notes?: string }) => {
    const res = await api.put(`/equipment/${id}`, payload);
    return res.data;
  },
  delete: async (id: number) => {
    const res = await api.delete(`/equipment/${id}`);
    return res.data;
  },

  // Maintenance Plans
  listMaintenancePlans: async (equipmentId?: number) => {
    const params = equipmentId ? { equipment_id: equipmentId } : {};
    const res = await api.get('/equipment/maintenance-plans', { params });
    return res.data;
  },
  createMaintenancePlan: async (equipmentId: number, payload: { frequency_days: number; maintenance_type: 'preventive'|'corrective'; notes?: string }) => {
    const res = await api.post(`/equipment/${equipmentId}/maintenance-plans`, payload);
    return res.data;
  },
  updateMaintenancePlan: async (planId: number, payload: { frequency_days?: number; maintenance_type?: 'preventive'|'corrective'; notes?: string }) => {
    const res = await api.put(`/equipment/maintenance-plans/${planId}`, payload);
    return res.data;
  },
  deleteMaintenancePlan: async (planId: number) => {
    const res = await api.delete(`/equipment/maintenance-plans/${planId}`);
    return res.data;
  },

  // Work Orders
  createWorkOrder: async (payload: { equipment_id: number; plan_id?: number; title: string; description?: string }) => {
    const res = await api.post('/equipment/work-orders', payload);
    return res.data;
  },
  listWorkOrders: async (params?: { equipment_id?: number; plan_id?: number; status?: 'pending' | 'completed' }) => {
    const res = await api.get('/equipment/work-orders', { params });
    return res.data;
  },
  getWorkOrder: async (id: number) => {
    const res = await api.get(`/equipment/work-orders/${id}`);
    return res.data;
  },
  updateWorkOrder: async (id: number, payload: { title?: string; description?: string; status?: 'pending' | 'completed' }) => {
    const res = await api.put(`/equipment/work-orders/${id}`, payload);
    return res.data;
  },
  completeWorkOrder: async (workOrderId: number) => {
    const res = await api.post(`/equipment/work-orders/${workOrderId}/complete`);
    return res.data;
  },
  deleteWorkOrder: async (id: number) => {
    const res = await api.delete(`/equipment/work-orders/${id}`);
    return res.data;
  },

  // Calibration Plans
  listCalibrationPlans: async (equipmentId?: number) => {
    const params = equipmentId ? { equipment_id: equipmentId } : {};
    const res = await api.get('/equipment/calibration-plans', { params });
    return res.data;
  },
  createCalibrationPlan: async (equipmentId: number, payload: { schedule_date: string; notes?: string }) => {
    const res = await api.post(`/equipment/${equipmentId}/calibration-plans`, payload);
    return res.data;
  },
  updateCalibrationPlan: async (planId: number, payload: { schedule_date?: string; notes?: string }) => {
    const res = await api.put(`/equipment/calibration-plans/${planId}`, payload);
    return res.data;
  },
  deleteCalibrationPlan: async (planId: number) => {
    const res = await api.delete(`/equipment/calibration-plans/${planId}`);
    return res.data;
  },
  uploadCalibrationCertificate: async (planId: number, file: File) => {
    const form = new FormData(); 
    form.append('file', file);
    const res = await api.post(`/equipment/calibration-plans/${planId}/records`, form, { 
      headers: { 'Content-Type': 'multipart/form-data' } 
    });
    return res.data;
  },
  downloadCalibrationCertificate: async (recordId: number) => {
    const res = await api.get(`/equipment/calibration-records/${recordId}/download`, {
      responseType: 'blob'
    });
    return res.data;
  },

  // Analytics and Reports
  getEquipmentStats: async () => {
    const res = await api.get('/equipment/stats');
    return res.data;
  },
  getMaintenanceHistory: async (equipmentId?: number, params?: { start_date?: string; end_date?: string }) => {
    const queryParams: any = { ...(params || {}) };
    if (equipmentId) (queryParams as any).equipment_id = equipmentId;
    const res = await api.get('/equipment/maintenance-history', { params: queryParams });
    return res.data;
  },
  getCalibrationHistory: async (equipmentId?: number, params?: { start_date?: string; end_date?: string }) => {
    const queryParams: any = { ...(params || {}) };
    if (equipmentId) (queryParams as any).equipment_id = equipmentId;
    const res = await api.get('/equipment/calibration-history', { params: queryParams });
    return res.data;
  },

  // Notifications and Alerts
  getUpcomingMaintenance: async () => {
    const res = await api.get('/equipment/upcoming-maintenance');
    return res.data;
  },
  getOverdueCalibrations: async () => {
    const res = await api.get('/equipment/overdue-calibrations');
    return res.data;
  },
  getEquipmentAlerts: async () => {
    const res = await api.get('/equipment/alerts');
    return res.data;
  },
};


