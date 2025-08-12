import api from './api';
import {
  Supplier,
  SupplierCreate,
  SupplierUpdate,
  Material,
  MaterialCreate,
  MaterialUpdate,
  Evaluation,
  EvaluationCreate,
  EvaluationUpdate,
  Delivery,
  DeliveryCreate,
  DeliveryUpdate,
  SupplierDocument,
  SupplierDocumentCreate,
  SupplierDocumentUpdate,
  SupplierDashboard,
  SupplierFilters,
  MaterialFilters,
  EvaluationFilters,
  DeliveryFilters,
  PaginatedResponse,
  ApiResponse,
  BulkStatusUpdate,
  QualityAlert,
} from '../types/supplier';

// Remove empty strings, null, and undefined from params
const cleanParams = (obj?: Record<string, any>) => {
  if (!obj) return undefined;
  const out: Record<string, any> = {};
  Object.entries(obj).forEach(([k, v]) => {
    if (v === undefined || v === null) return;
    if (typeof v === 'string' && v.trim() === '') return;
    if (Array.isArray(v) && v.length === 0) return;
    out[k] = v;
  });
  return out;
};

// Enhanced Supplier API
export const supplierAPI = {
  // Supplier Management
  getSuppliers: async (params?: SupplierFilters & { page?: number; size?: number }) => {
    const response = await api.get('/suppliers', { params: cleanParams(params) });
    return response.data as ApiResponse<PaginatedResponse<Supplier>>;
  },

  getSupplier: async (supplierId: number) => {
    const response = await api.get(`/suppliers/${supplierId}`);
    return response.data as ApiResponse<Supplier>;
  },

  createSupplier: async (supplierData: SupplierCreate) => {
    const response = await api.post('/suppliers', supplierData);
    return response.data as ApiResponse<Supplier>;
  },

  updateSupplier: async (supplierId: number, supplierData: SupplierUpdate) => {
    const response = await api.put(`/suppliers/${supplierId}`, supplierData);
    return response.data as ApiResponse<Supplier>;
  },

  deleteSupplier: async (supplierId: number) => {
    const response = await api.delete(`/suppliers/${supplierId}`);
    return response.data as ApiResponse<{ message: string }>;
  },

  // Bulk Operations
  bulkUpdateStatus: async (bulkData: BulkStatusUpdate) => {
    const response = await api.post('/suppliers/bulk/action', bulkData);
    return response.data as ApiResponse<{ updated_count: number }>;
  },

  bulkScheduleEvaluation: async (supplierIds: number[], evaluationDate: string) => {
    const response = await api.post('/suppliers/bulk/evaluation-schedule', {
      supplier_ids: supplierIds,
      evaluation_date: evaluationDate,
    });
    return response.data as ApiResponse<{ scheduled_count: number }>;
  },

  // Material Management
  getMaterials: async (params?: MaterialFilters & { page?: number; size?: number }) => {
    const response = await api.get('/suppliers/materials', { params: cleanParams(params) });
    return response.data as ApiResponse<PaginatedResponse<Material>>;
  },

  getMaterial: async (materialId: number) => {
    const response = await api.get(`/suppliers/materials/${materialId}`);
    return response.data as ApiResponse<Material>;
  },

  createMaterial: async (materialData: MaterialCreate) => {
    const response = await api.post('/suppliers/materials', materialData);
    return response.data as ApiResponse<Material>;
  },

  updateMaterial: async (materialId: number, materialData: MaterialUpdate) => {
    const response = await api.put(`/suppliers/materials/${materialId}`, materialData);
    return response.data as ApiResponse<Material>;
  },

  deleteMaterial: async (materialId: number) => {
    const response = await api.delete(`/suppliers/materials/${materialId}`);
    return response.data as ApiResponse<{ message: string }>;
  },

  // Material Approval
  approveMaterial: async (materialId: number, comments?: string) => {
    const response = await api.post(`/suppliers/materials/${materialId}/approve`, {
      comments,
    });
    return response.data as ApiResponse<Material>;
  },

  rejectMaterial: async (materialId: number, rejectionReason: string) => {
    const response = await api.post(`/suppliers/materials/${materialId}/reject`, {
      rejection_reason: rejectionReason,
    });
    return response.data as ApiResponse<Material>;
  },

  bulkApproveMaterials: async (materialIds: number[], comments?: string) => {
    const response = await api.post('/suppliers/materials/bulk/approve', {
      material_ids: materialIds,
      comments,
    });
    return response.data as ApiResponse<{ approved_count: number }>;
  },

  bulkRejectMaterials: async (materialIds: number[], rejectionReason: string) => {
    const response = await api.post('/suppliers/materials/bulk/reject', {
      material_ids: materialIds,
      rejection_reason: rejectionReason,
    });
    return response.data as ApiResponse<{ rejected_count: number }>;
  },

  // Evaluation System
  getEvaluations: async (params?: EvaluationFilters & { page?: number; size?: number }) => {
    const response = await api.get('/suppliers/evaluations', { params: cleanParams(params) });
    return response.data as ApiResponse<PaginatedResponse<Evaluation>>;
  },

  getEvaluation: async (evaluationId: number) => {
    const response = await api.get(`/suppliers/evaluations/${evaluationId}`);
    return response.data as ApiResponse<Evaluation>;
  },

  createEvaluation: async (evaluationData: EvaluationCreate) => {
    const response = await api.post('/suppliers/evaluations', evaluationData);
    return response.data as ApiResponse<Evaluation>;
  },

  updateEvaluation: async (evaluationId: number, evaluationData: EvaluationUpdate) => {
    const response = await api.put(`/suppliers/evaluations/${evaluationId}`, evaluationData);
    return response.data as ApiResponse<Evaluation>;
  },

  deleteEvaluation: async (evaluationId: number) => {
    const response = await api.delete(`/suppliers/evaluations/${evaluationId}`);
    return response.data as ApiResponse<{ message: string }>;
  },

  // Supplier Evaluations
  getSupplierEvaluations: async (supplierId: number) => {
    const response = await api.get(`/suppliers/${supplierId}/evaluations`);
    return response.data as ApiResponse<Evaluation[]>;
  },

  // Delivery Management
  getDeliveries: async (params?: DeliveryFilters & { page?: number; size?: number }) => {
    const response = await api.get('/suppliers/deliveries', { params: cleanParams(params) });
    return response.data as ApiResponse<PaginatedResponse<Delivery>>;
  },

  getDelivery: async (deliveryId: number) => {
    const response = await api.get(`/suppliers/deliveries/${deliveryId}`);
    return response.data as ApiResponse<Delivery>;
  },

  createDelivery: async (deliveryData: DeliveryCreate) => {
    const response = await api.post('/suppliers/deliveries', deliveryData);
    return response.data as ApiResponse<Delivery>;
  },

  updateDelivery: async (deliveryId: number, deliveryData: DeliveryUpdate) => {
    const response = await api.put(`/suppliers/deliveries/${deliveryId}`, deliveryData);
    return response.data as ApiResponse<Delivery>;
  },

  deleteDelivery: async (deliveryId: number) => {
    const response = await api.delete(`/suppliers/deliveries/${deliveryId}`);
    return response.data as ApiResponse<{ message: string }>;
  },

  // Quality Control
  inspectDelivery: async (deliveryId: number, inspectionData: {
    status: 'passed' | 'failed' | 'under_review';
    comments?: string;
  }) => {
    const response = await api.post(`/suppliers/deliveries/${deliveryId}/inspect`, inspectionData);
    return response.data as ApiResponse<Delivery>;
  },

  // Quality Alerts
  createQualityAlert: async (deliveryId: number, alertData: {
    alert_type: 'temperature' | 'damage' | 'expiry' | 'contamination' | 'documentation' | 'other';
    severity: 'low' | 'medium' | 'high' | 'critical';
    description: string;
  }) => {
    const response = await api.post(`/suppliers/deliveries/${deliveryId}/alerts`, alertData);
    return response.data as ApiResponse<QualityAlert>;
  },

  resolveQualityAlert: async (alertId: number, resolutionData: {
    action_taken: string;
  }) => {
    const response = await api.post(`/suppliers/alerts/${alertId}/resolve`, resolutionData);
    return response.data as ApiResponse<QualityAlert>;
  },

  // COA Upload
  uploadCOA: async (deliveryId: number, file: File) => {
    const formData = new FormData();
    formData.append('coa_file', file);
    
    const response = await api.post(`/suppliers/deliveries/${deliveryId}/coa`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data as ApiResponse<{ file_path: string }>;
  },

  downloadCOA: async (deliveryId: number) => {
    const response = await api.get(`/suppliers/deliveries/${deliveryId}/coa/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Delivery → Batch linkage
  createBatchFromDelivery: async (
    deliveryId: number,
    options?: { link_to_batch_id?: number; link_relationship_type?: 'ingredient' | 'parent' | 'child' | 'packaging' }
  ) => {
    const params: any = {};
    if (options?.link_to_batch_id) params.link_to_batch_id = options.link_to_batch_id;
    if (options?.link_relationship_type) params.link_relationship_type = options.link_relationship_type;
    const response = await api.post(`/suppliers/deliveries/${deliveryId}/create-batch`, null, { params });
    return response.data as ApiResponse<{ batch_id: number; link_id?: number | null }>;
  },

  // Document Management
  getSupplierDocuments: async (supplierId: number, params?: {
    document_type?: string;
    verification_status?: string;
    page?: number;
    size?: number;
  }) => {
    const response = await api.get(`/suppliers/${supplierId}/documents`, { params });
    return response.data as ApiResponse<PaginatedResponse<SupplierDocument>>;
  },

  getSupplierDocument: async (documentId: number) => {
    const response = await api.get(`/suppliers/documents/${documentId}`);
    return response.data as ApiResponse<SupplierDocument>;
  },

  uploadSupplierDocument: async (supplierId: number, documentData: SupplierDocumentCreate, file: File) => {
    const formData = new FormData();
    formData.append('document_type', documentData.document_type);
    formData.append('document_name', documentData.document_name);
    if (documentData.expiry_date) {
      formData.append('expiry_date', documentData.expiry_date);
    }
    formData.append('file', file);
    
    const response = await api.post(`/suppliers/${supplierId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data as ApiResponse<SupplierDocument>;
  },

  updateSupplierDocument: async (documentId: number, documentData: SupplierDocumentUpdate) => {
    const response = await api.put(`/suppliers/documents/${documentId}`, documentData);
    return response.data as ApiResponse<SupplierDocument>;
  },

  deleteSupplierDocument: async (documentId: number) => {
    const response = await api.delete(`/suppliers/documents/${documentId}`);
    return response.data as ApiResponse<{ message: string }>;
  },

  downloadSupplierDocument: async (documentId: number) => {
    const response = await api.get(`/suppliers/documents/${documentId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Document Verification
  verifyDocument: async (documentId: number, verificationData: {
    verification_status: 'verified' | 'rejected';
    verification_comments?: string;
  }) => {
    const response = await api.post(`/suppliers/documents/${documentId}/verify`, verificationData);
    return response.data as ApiResponse<SupplierDocument>;
  },

  // Dashboard and Analytics
  getDashboard: async () => {
    const response = await api.get('/suppliers/dashboard/stats');
    return response.data as ApiResponse<SupplierDashboard>;
  },

  getPerformanceAnalytics: async (params?: {
    date_from?: string;
    date_to?: string;
    supplier_id?: number;
  }) => {
    const response = await api.get('/suppliers/analytics/performance', { params: cleanParams(params) });
    return response.data as ApiResponse<{
      trends: Array<{ date: string; average_score: number }>;
      category_performance: Array<{ category: string; average_score: number }>;
      risk_distribution: Array<{ risk_level: string; count: number }>;
    }>;
  },

  getRiskAssessment: async () => {
    const response = await api.get('/suppliers/analytics/risk-assessment');
    return response.data as ApiResponse<{
      risk_matrix: Array<{ risk_level: string; count: number; percentage: number }>;
      high_risk_suppliers: Supplier[];
      risk_trends: Array<{ date: string; high_risk_count: number }>;
    }>;
  },

  // Alerts and Notifications
  getAlerts: async (params?: {
    severity?: 'low' | 'medium' | 'high' | 'critical';
    type?: string;
    resolved?: boolean;
    page?: number;
    size?: number;
  }) => {
    const response = await api.get('/suppliers/alerts', { params: cleanParams(params) });
    return response.data as ApiResponse<PaginatedResponse<{
      id: number;
      type: string;
      severity: string;
      title: string;
      description: string;
      created_at: string;
      resolved: boolean;
    }>>;
  },

  resolveAlert: async (alertId: number) => {
    const response = await api.post(`/suppliers/alerts/${alertId}/resolve`);
    return response.data as ApiResponse<{ message: string }>;
  },

  // Reports and Export
  generateSupplierReport: async (params?: {
    supplier_ids?: number[];
    date_from?: string;
    date_to?: string;
    report_type: 'evaluation' | 'delivery' | 'performance' | 'comprehensive';
  }) => {
    const response = await api.post('/suppliers/reports/generate', params);
    return response.data as ApiResponse<{ report_url: string }>;
  },

  exportSuppliers: async (params?: SupplierFilters) => {
    const response = await api.get('/suppliers/export', { 
      params: cleanParams(params),
      responseType: 'blob',
    });
    return response.data;
  },

  exportMaterials: async (params?: MaterialFilters) => {
    const response = await api.get('/suppliers/materials/export', { 
      params: cleanParams(params),
      responseType: 'blob',
    });
    return response.data;
  },

  exportEvaluations: async (params?: EvaluationFilters) => {
    const response = await api.get('/suppliers/evaluations/export', { 
      params: cleanParams(params),
      responseType: 'blob',
    });
    return response.data;
  },

  // Search and Filter
  searchSuppliers: async (query: string, params?: {
    category?: string;
    status?: string;
    risk_level?: string;
    limit?: number;
  }) => {
    const response = await api.get('/suppliers/search', { 
      params: cleanParams({ query, ...params })
    });
    return response.data as ApiResponse<Supplier[]>;
  },

  searchMaterials: async (query: string, params?: {
    category?: string;
    supplier_id?: number;
    approval_status?: string;
    limit?: number;
  }) => {
    const response = await api.get('/suppliers/materials/search', { 
      params: cleanParams({ query, ...params })
    });
    return response.data as ApiResponse<Material[]>;
  },

  // Statistics
  getSupplierStats: async () => {
    const response = await api.get('/suppliers/stats');
    return response.data as ApiResponse<{
      total_suppliers: number;
      active_suppliers: number;
      pending_approval: number;
      suspended_suppliers: number;
      blacklisted_suppliers: number;
      overdue_evaluations: number;
      upcoming_evaluations: number;
      recent_deliveries: number;
      quality_alerts: number;
    }>;
  },

  getMaterialStats: async () => {
    const response = await api.get('/suppliers/materials/stats');
    return response.data as ApiResponse<{
      total_materials: number;
      approved_materials: number;
      pending_materials: number;
      rejected_materials: number;
      materials_by_category: Array<{ category: string; count: number }>;
      materials_by_supplier: Array<{ supplier_name: string; count: number }>;
    }>;
  },

  getEvaluationStats: async () => {
    const response = await api.get('/suppliers/evaluations/stats');
    return response.data as ApiResponse<{
      total_evaluations: number;
      completed_evaluations: number;
      in_progress_evaluations: number;
      scheduled_evaluations: number;
      overdue_evaluations: number;
      average_score: number;
      evaluations_by_month: Array<{ month: string; count: number; average_score: number }>;
    }>;
  },
}; 