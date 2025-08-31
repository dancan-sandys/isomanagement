import { api } from './api';

export interface ProcessCreatePayload {
  batch_id: number;
  process_type: 'fresh_milk' | 'yoghurt' | 'mala' | 'cheese' | 'pasteurized_milk' | 'fermented_products';
  operator_id?: number;
  spec?: any;
  notes?: string;
}

export interface ProcessParameterPayload {
  step_id?: number;
  parameter_name: string;
  parameter_value: number;
  unit: string;
  target_value?: number;
  tolerance_min?: number;
  tolerance_max?: number;
  notes?: string;
}

export interface ProcessDeviationPayload {
  step_id?: number;
  parameter_id?: number;
  deviation_type: string;
  expected_value: number;
  actual_value: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  impact_assessment?: string;
  corrective_action?: string;
}

export interface ProcessAlertPayload {
  alert_type: string;
  alert_level: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  parameter_value?: number;
  threshold_value?: number;
}

export interface ProcessTemplatePayload {
  template_name: string;
  product_type: 'fresh_milk' | 'yoghurt' | 'mala' | 'cheese' | 'pasteurized_milk' | 'fermented_products';
  description?: string;
  steps: any[];
  parameters?: any;
}

export interface ProcessStepSpec {
  step_type: string;
  sequence: number;
  target_temp_c?: number;
  target_time_seconds?: number;
  tolerance_c?: number;
  required: boolean;
  step_metadata?: any;
}

export interface ProcessLogPayload {
  step_id?: number;
  timestamp?: string;
  event: 'start' | 'reading' | 'complete' | 'divert';
  measured_temp_c?: number;
  note?: string;
  auto_flag?: boolean;
  source?: string;
}

export interface YieldPayload {
  output_qty: number;
  expected_qty?: number;
  unit: string;
}

export interface TransferPayload {
  quantity: number;
  unit: string;
  location?: string;
  lot_number?: string;
  verified_by?: number;
}

export interface AgingPayload {
  start_time?: string;
  end_time?: string;
  room_temperature_c?: number;
  target_temp_min_c?: number;
  target_temp_max_c?: number;
  target_days?: number;
  room_location?: string;
  notes?: string;
}

export interface MaterialConsumptionPayload {
  material_id: number;
  quantity: number;
  unit: string;
  supplier_id?: number;
  delivery_id?: number;
  lot_number?: string;
  notes?: string;
}

const productionAPI = {
  createProcess: async (payload: ProcessCreatePayload) => {
    const res = await api.post('/production/process', payload);
    return res.data;
  },
  addLog: async (processId: number, payload: ProcessLogPayload) => {
    const res = await api.post(`/production/${processId}/log`, payload);
    return res.data;
  },
  recordYield: async (processId: number, payload: YieldPayload) => {
    const res = await api.post(`/production/${processId}/yield`, payload);
    return res.data;
  },
  transfer: async (processId: number, payload: TransferPayload) => {
    const res = await api.post(`/production/${processId}/transfer`, payload);
    return res.data;
  },
  aging: async (processId: number, payload: AgingPayload) => {
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

  // Enhanced Production API Methods
  createProcessEnhanced: async (payload: ProcessCreatePayload) => {
    const res = await api.post('/production/processes', payload);
    return res.data;
  },

  listProcesses: async (params?: { process_type?: string; status?: string; limit?: number; offset?: number }) => {
    const res = await api.get('/production/processes', { params });
    return res.data;
  },

  updateProcess: async (processId: number, payload: any) => {
    const res = await api.put(`/production/processes/${processId}`, payload);
    return res.data;
  },

  recordParameter: async (processId: number, payload: ProcessParameterPayload) => {
    const res = await api.post(`/production/processes/${processId}/parameters`, payload);
    return res.data;
  },

  getProcessParameters: async (processId: number) => {
    const res = await api.get(`/production/processes/${processId}/parameters`);
    return res.data;
  },

  createDeviation: async (processId: number, payload: ProcessDeviationPayload) => {
    const res = await api.post(`/production/processes/${processId}/deviations`, payload);
    return res.data;
  },

  resolveDeviation: async (deviationId: number, correctiveAction: string) => {
    const res = await api.put(`/production/deviations/${deviationId}/resolve`, { corrective_action: correctiveAction });
    return res.data;
  },

  createAlert: async (processId: number, payload: ProcessAlertPayload) => {
    const res = await api.post(`/production/processes/${processId}/alerts`, payload);
    return res.data;
  },

  acknowledgeAlert: async (alertId: number) => {
    const res = await api.put(`/production/alerts/${alertId}/acknowledge`);
    return res.data;
  },

  createTemplate: async (payload: ProcessTemplatePayload) => {
    const res = await api.post('/production/templates', payload);
    return res.data;
  },

  getTemplates: async (productType?: string) => {
    const res = await api.get('/production/templates', { params: { product_type: productType } });
    return res.data;
  },

  getEnhancedAnalytics: async (processType?: string) => {
    const res = await api.get('/production/analytics/enhanced', { params: { process_type: processType } });
    return res.data;
  },
  exportAnalyticsCSV: async (processType?: string) => {
    const res = await api.get('/production/analytics/export/csv', { params: { process_type: processType }, responseType: 'blob' });
    return res.data as Blob;
  },
  exportAnalyticsPDF: async (processType?: string) => {
    const res = await api.get('/production/analytics/export/pdf', { params: { process_type: processType }, responseType: 'blob' });
    return res.data as Blob;
  },

  getProcessDetails: async (processId: number) => {
    const res = await api.get(`/production/processes/${processId}/details`);
    return res.data;
  },

  getProcessAudit: async (processId: number, params?: { limit?: number; offset?: number }) => {
    const res = await api.get(`/production/processes/${processId}/audit`, { params });
    return res.data as Array<{ id: number; user_id?: number; action: string; details?: any; created_at: string; ip_address?: string; user_agent?: string }>;
  },

  // Spec binding and release
  bindSpec: async (processId: number, payload: { document_id: number; document_version: string; locked_parameters?: any }) => {
    const res = await api.post(`/production/processes/${processId}/spec/bind`, payload);
    return res.data;
  },

  checkRelease: async (processId: number) => {
    const res = await api.get(`/production/processes/${processId}/release/check`);
    return res.data;
  },

  releaseProcess: async (processId: number, payload: { released_qty?: number; unit?: string; signature_hash: string }) => {
    const res = await api.post(`/production/processes/${processId}/release`, payload);
    return res.data;
  },

  exportProductionSheetPDF: async (processId: number) => {
    const res = await api.get(`/production/processes/${processId}/export/pdf`, { responseType: 'blob' });
    return res.data as Blob;
  },

  recordMaterialConsumption: async (processId: number, payload: MaterialConsumptionPayload) => {
    const res = await api.post(`/production/processes/${processId}/materials`, payload);
    return res.data;
  },

  // MOC helpers (via change-requests endpoints)
  listChangeRequests: async (params?: { process_id?: number; status?: string }) => {
    const res = await api.get('/change-requests/', { params });
    return res.data;
  },
  getChangeRequest: async (id: number) => {
    const res = await api.get(`/change-requests/${id}`);
    return res.data;
  },
  approveChangeRequest: async (id: number, payload: { decision: 'approved'|'rejected'; comments?: string; sequence?: number }) => {
    const res = await api.post(`/change-requests/${id}/approve`, { decision: payload.decision, comments: payload.comments }, { params: { sequence: payload.sequence } });
    return res.data;
  },

  getTransitions: async (processId: number) => {
    const res = await api.get(`/production/processes/${processId}/transitions`);
    return res.data as Array<{ id: number; from_stage_id?: number; to_stage_id?: number; transition_type: string; auto_transition?: boolean; reason?: string; initiated_by: number; timestamp: string; requires_approval?: boolean; approved_by?: number|null }>;
  },

  getAuditSimple: async (processId: number) => {
    const res = await api.get(`/production/processes/${processId}/audit-simple`);
    return res.data as { process_id: number; transitions: any[]; diverts: any[] };
  },

  // Batch progression (FSM) endpoints
  evaluateStage: async (processId: number, stageId: number) => {
    const res = await api.get(`/batch-progression/processes/${processId}/stages/${stageId}/evaluate`);
    return res.data as { can_progress: boolean; requires_approval: boolean; available_actions: string[]; next_stage?: any };
  },
  transitionStage: async (processId: number, stageId: number, payload: { transition_type: 'normal'|'rollback'|'skip'|'emergency'|'rework'; reason?: string; notes?: string; deviations_recorded?: string; corrective_actions?: string; prerequisites_met?: boolean }) => {
    const res = await api.post(`/batch-progression/processes/${processId}/stages/${stageId}/transition`, payload);
    return res.data;
  },
  getActiveStage: async (processId: number) => {
    const res = await api.get(`/production/processes/${processId}/active-stage`);
    return res.data as { active_stage: { id: number; name: string; sequence: number; status: string } | null };
  },
};

export const suppliersAPI = {
  searchMaterials: async (q: string, limit: number = 10) => {
    const res = await api.get('/suppliers/materials/search', { params: { q, limit } });
    return res.data?.data?.results || [];
  },
};

export default productionAPI;

