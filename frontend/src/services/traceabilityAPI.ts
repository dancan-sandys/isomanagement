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
    // Clean params: map page/size -> skip/limit and drop empty strings for enums
    const cleaned: any = {};
    if (params) {
      const { page, size, batch_type, status, search, ...rest } = params;
      if (size) cleaned.limit = size;
      if (page) cleaned.skip = (page - 1) * (size || 10);
      if (batch_type) cleaned.batch_type = batch_type; // omit if empty
      if (status) cleaned.status = status; // omit if empty
      if (search && search.trim() !== '') cleaned.search = search;
      Object.entries(rest).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') cleaned[k] = v;
      });
    }
    const response = await api.get('/traceability/batches', { params: cleaned });
    // Support both ResponseModel and raw data
    const payload = response.data?.data || response.data;
    // If server used skip/limit, adapt to page/size for UI
    if (payload && typeof payload.total !== 'undefined' && typeof payload.items !== 'undefined') {
      return payload;
    }
    return { items: payload?.items || [], total: payload?.total || 0 };
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
  // Use backend print data endpoint
  generateBarcode: async (batchId: number) => {
    const response = await api.get(`/traceability/batches/${batchId}/barcode`);
    return response.data;
  },

  generateQRCode: async (batchId: number) => {
    const response = await api.get(`/traceability/batches/${batchId}/qrcode`);
    return response.data;
  },

  printBarcode: async (batchId: number, format: string = 'pdf') => {
    const response = await api.get(`/traceability/batches/${batchId}/barcode/print`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data as Blob;
  },

  // Traceability Chain
  // No generic /trace endpoint on backend; prefer backward/forward
  getTraceabilityChain: async (batchId: number) => {
      const response = await api.get(`/traceability/batches/${batchId}/trace/chain`);
    return response.data?.data || response.data;
  },

  getFullTrace: async (batchId: number, depth: number = 5) => {
    const response = await api.get(`/traceability/batches/${batchId}/trace/full`, { params: { depth } });
    return response.data?.data || response.data;
  },

  createTraceabilityLink: async (linkData: {
    source_batch_id: number;
    target_batch_id: number;
    link_type: string;
    quantity_used: number;
    process_step: string;
  }) => {
    // Not available in backend yet; defer to Phase 3
    throw new Error('Traceability links creation endpoint is not implemented on the backend');
  },

  deleteTraceabilityLink: async (linkId: number) => {
    // Not available in backend yet; defer to Phase 3
    const response = await api.delete(`/traceability/links/${linkId}`);
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

  // Kept for compatibility if backend full-trace is unavailable; backend now exposes /trace/full

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
    const cleaned: any = {};
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') cleaned[k] = v;
      });
    }
    const response = await api.get('/traceability/recalls', { params: cleaned });
    return response.data?.data || response.data;
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
    const cleaned: any = {};
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') cleaned[k] = v;
      });
    }
    const response = await api.get('/traceability/reports', { params: cleaned });
    return response.data?.data || response.data;
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

  deleteCorrectiveAction: async (recallId: number, actionId: number) => {
    const response = await api.delete(`/traceability/recalls/${recallId}/corrective-actions/${actionId}`);
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

  // Optional updates/deletes can be added later if backend supports

  // Preventive Measures
  getPreventiveMeasures: async (recallId: number) => {
    const response = await api.get(`/traceability/recalls/${recallId}/preventive-measures`);
    return response.data;
  },

  createPreventiveMeasure: async (recallId: number, measureData: any) => {
    const response = await api.post(`/traceability/recalls/${recallId}/preventive-measures`, measureData);
    return response.data;
  },

  deletePreventiveMeasure: async (recallId: number, measureId: number) => {
    const response = await api.delete(`/traceability/recalls/${recallId}/preventive-measures/${measureId}`);
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

  deleteVerificationPlan: async (recallId: number, planId: number) => {
    const response = await api.delete(`/traceability/recalls/${recallId}/verification-plans/${planId}`);
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

  deleteEffectivenessReview: async (recallId: number, reviewId: number) => {
    const response = await api.delete(`/traceability/recalls/${recallId}/effectiveness-reviews/${reviewId}`);
    return response.data;
  },

  // Dashboard
  getDashboard: async () => {
    const response = await api.get('/traceability/dashboard/enhanced');
    return response.data?.data || response.data;
  },

  // Export functionality
  exportBatches: async (format: string = 'csv', filters?: any) => {
    // Not supported by backend
    throw new Error('Export batches endpoint is not available on the backend');
  },

  exportRecalls: async (format: string = 'csv', filters?: any) => {
    // Not supported by backend
    throw new Error('Export recalls endpoint is not available on the backend');
  },

  exportTraceabilityReport: async (reportId: number, format: string = 'pdf') => {
    // Not supported by backend
    throw new Error('Export traceability report endpoint is not available on the backend');
  },

  // Bulk operations
  bulkUpdateBatches: async (batchIds: number[], updateData: any) => {
    // Not available on backend; defer to Phase 3
    throw new Error('Bulk update for batches is not implemented on the backend');
  },

  bulkDeleteBatches: async (batchIds: number[]) => {
    // Fallback: delete individually until bulk endpoint exists
    await Promise.all(batchIds.map((id) => api.delete(`/traceability/batches/${id}`)));
    return { success: true, deleted: batchIds.length } as any;
  },
}; 