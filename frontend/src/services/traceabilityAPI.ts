import api from './api';

// Enhanced Traceability API with all required endpoints
export const traceabilityAPI = {
  // Batch Management
  getBatches: async (params?: {
    page?: number;
    size?: number;
    search?: string;
    batch_type?: string;
    status?: string;
    quality_status?: string;
    date_from?: string;
    date_to?: string;
    product_name?: string;
  }) => {
    const response = await api.get('/traceability/batches', { params });
    return response.data;
  },

  getBatch: async (batchId: number) => {
    const response = await api.get(`/traceability/batches/${batchId}`);
    return response.data;
  },

  createBatch: async (batchData: any) => {
    const response = await api.post('/traceability/batches', batchData);
    return response.data;
  },

  updateBatch: async (batchId: number, batchData: any) => {
    const response = await api.put(`/traceability/batches/${batchId}`, batchData);
    return response.data;
  },

  deleteBatch: async (batchId: number) => {
    const response = await api.delete(`/traceability/batches/${batchId}`);
    return response.data;
  },

  // Barcode and QR Code System
  // Generate barcode and QR code data
  generateBarcode: async (batchId: number) => {
    const response = await api.get(`/traceability/batches/${batchId}/barcode`);
    return response.data;
  },
  generateQRCode: async (batchId: number) => {
    const response = await api.get(`/traceability/batches/${batchId}/qrcode`);
    return response.data;
  },
  // Print label (server returns printable content or URL)
  printBarcode: async (batchId: number) => {
    const response = await api.get(`/traceability/batches/${batchId}/barcode/print`);
    return response.data;
  },

  // Traceability Chain
  // No generic /trace endpoint on backend; prefer backward/forward

  createTraceabilityLink: async (linkData: {
    source_batch_id: number;
    target_batch_id: number;
    link_type: string;
    quantity_used: number;
    process_step: string;
  }) => {
    const response = await api.post('/traceability/links', linkData);
    return response.data;
  },

  deleteTraceabilityLink: async (linkId: number) => {
    const response = await api.delete(`/traceability/links/${linkId}`);
    return response.data;
  },

  // Traceability Chain & Enhanced Trace Analysis
  getTraceabilityChain: async (batchId: number) => {
    const response = await api.get(`/traceability/batches/${batchId}/traceability-chain`);
    return response.data;
  },
  
  // Enhanced Trace Analysis
  getBackwardTrace: async (batchId: number, depth: number = 5) => {
    const response = await api.get(`/traceability/batches/${batchId}/trace/backward`, {
      params: { depth }
    });
    return response.data;
  },

  getForwardTrace: async (batchId: number, depth: number = 5) => {
    const response = await api.get(`/traceability/batches/${batchId}/trace/forward`, {
      params: { depth }
    });
    return response.data;
  },

  getFullTrace: async (batchId: number, depth: number = 5) => {
    const response = await api.get(`/traceability/batches/${batchId}/full-trace`, {
      params: { depth }
    });
    return response.data;
  },

  // Recall Management
  getRecalls: async (params?: {
    page?: number;
    size?: number;
    search?: string;
    recall_type?: string;
    status?: string;
    date_from?: string;
    date_to?: string;
  }) => {
    const response = await api.get('/traceability/recalls', { params });
    return response.data;
  },

  getRecall: async (recallId: number) => {
    const response = await api.get(`/traceability/recalls/${recallId}`);
    return response.data;
  },

  createRecall: async (recallData: any) => {
    const response = await api.post('/traceability/recalls', recallData);
    return response.data;
  },

  updateRecall: async (recallId: number, recallData: any) => {
    const response = await api.put(`/traceability/recalls/${recallId}`, recallData);
    return response.data;
  },

  deleteRecall: async (recallId: number) => {
    const response = await api.delete(`/traceability/recalls/${recallId}`);
    return response.data;
  },

  // Recall Simulation
  simulateRecall: async (simulationData: {
    batch_id: number;
    recall_type: string;
    reason: string;
    risk_level: string;
  }) => {
    const response = await api.post('/traceability/recalls/simulate', simulationData);
    return response.data;
  },

  getRecallSimulation: async (simulationId: number) => {
    const response = await api.get(`/traceability/recalls/simulations/${simulationId}`);
    return response.data;
  },

  // Enhanced Search
  searchBatches: async (searchParams: {
    query: string;
    batch_type?: string;
    status?: string;
    quality_status?: string;
    date_from?: string;
    date_to?: string;
    product_name?: string;
    page?: number;
    size?: number;
  }) => {
    const response = await api.post('/traceability/batches/search/enhanced', searchParams);
    return response.data;
  },

  searchRecalls: async (searchParams: {
    query: string;
    recall_type?: string;
    status?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    size?: number;
  }) => {
    const response = await api.post('/traceability/search/recalls', searchParams);
    return response.data;
  },

  // Traceability Reports
  getTraceabilityReports: async (params?: {
    page?: number;
    size?: number;
    search?: string;
    report_type?: string;
    date_from?: string;
    date_to?: string;
  }) => {
    const response = await api.get('/traceability/reports', { params });
    return response.data;
  },

  getTraceabilityReport: async (reportId: number) => {
    const response = await api.get(`/traceability/reports/${reportId}`);
    return response.data;
  },

  createTraceabilityReport: async (reportData: any) => {
    const response = await api.post('/traceability/reports', reportData);
    return response.data;
  },

  updateTraceabilityReport: async (reportId: number, reportData: any) => {
    const response = await api.put(`/traceability/reports/${reportId}`, reportData);
    return response.data;
  },

  deleteTraceabilityReport: async (reportId: number) => {
    const response = await api.delete(`/traceability/reports/${reportId}`);
    return response.data;
  },

  // Corrective Actions
  getCorrectiveActions: async (recallId: number) => {
    const response = await api.get(`/traceability/recalls/${recallId}/corrective-actions`);
    return response.data;
  },

  createCorrectiveAction: async (recallId: number, actionData: any) => {
    const response = await api.post(`/traceability/recalls/${recallId}/corrective-actions`, actionData);
    return response.data;
  },

  updateCorrectiveAction: async (recallId: number, actionId: number, actionData: any) => {
    const response = await api.put(`/traceability/recalls/${recallId}/corrective-actions/${actionId}`, actionData);
    return response.data;
  },

  // Root Cause Analysis
  getRootCauseAnalysis: async (recallId: number) => {
    const response = await api.get(`/traceability/recalls/${recallId}/root-cause-analysis`);
    return response.data;
  },

  createRootCauseAnalysis: async (recallId: number, analysisData: any) => {
    const response = await api.post(`/traceability/recalls/${recallId}/root-cause-analysis`, analysisData);
    return response.data;
  },

  // Preventive Measures
  getPreventiveMeasures: async (recallId: number) => {
    const response = await api.get(`/traceability/recalls/${recallId}/preventive-measures`);
    return response.data;
  },

  createPreventiveMeasure: async (recallId: number, measureData: any) => {
    const response = await api.post(`/traceability/recalls/${recallId}/preventive-measures`, measureData);
    return response.data;
  },

  // Verification Plans
  getVerificationPlans: async (recallId: number) => {
    const response = await api.get(`/traceability/recalls/${recallId}/verification-plans`);
    return response.data;
  },

  createVerificationPlan: async (recallId: number, planData: any) => {
    const response = await api.post(`/traceability/recalls/${recallId}/verification-plans`, planData);
    return response.data;
  },

  // Effectiveness Reviews
  getEffectivenessReviews: async (recallId: number) => {
    const response = await api.get(`/traceability/recalls/${recallId}/effectiveness-reviews`);
    return response.data;
  },

  createEffectivenessReview: async (recallId: number, reviewData: any) => {
    const response = await api.post(`/traceability/recalls/${recallId}/effectiveness-reviews`, reviewData);
    return response.data;
  },

  // Dashboard
  getDashboard: async () => {
    const response = await api.get('/traceability/dashboard/enhanced');
    return response.data;
  },

  // Export functionality
  exportBatches: async (format: string = 'csv', filters?: any) => {
    const response = await api.post('/traceability/export/batches', { format, filters });
    return response.data;
  },

  exportRecalls: async (format: string = 'csv', filters?: any) => {
    const response = await api.post('/traceability/export/recalls', { format, filters });
    return response.data;
  },

  exportTraceabilityReport: async (reportId: number, format: string = 'pdf') => {
    const response = await api.post(`/traceability/reports/${reportId}/export`, { format });
    return response.data;
  },

  // Bulk operations
  bulkUpdateBatches: async (batchIds: number[], updateData: any) => {
    const response = await api.put('/traceability/batches/bulk', { batch_ids: batchIds, ...updateData });
    return response.data;
  },

  bulkDeleteBatches: async (batchIds: number[]) => {
    const response = await api.delete('/traceability/batches/bulk', { data: { batch_ids: batchIds } });
    return response.data;
  },
}; 