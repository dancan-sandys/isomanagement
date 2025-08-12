import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { supplierAPI } from '../../services/supplierAPI';
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
  BulkStatusUpdate,
} from '../../types/supplier';

// Async Thunks

// Supplier Management
export const fetchSuppliers = createAsyncThunk(
  'supplier/fetchSuppliers',
  async (params?: SupplierFilters & { page?: number; size?: number }, { rejectWithValue }) => {
    try {
      const response = await supplierAPI.getSuppliers(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch suppliers');
    }
  }
);

export const fetchSupplier = createAsyncThunk(
  'supplier/fetchSupplier',
  async (supplierId: number) => {
    const response = await supplierAPI.getSupplier(supplierId);
    return response.data;
  }
);

export const createSupplier = createAsyncThunk(
  'supplier/createSupplier',
  async (supplierData: SupplierCreate, { rejectWithValue }) => {
    try {
      const response = await supplierAPI.createSupplier(supplierData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create supplier');
    }
  }
);

export const updateSupplier = createAsyncThunk(
  'supplier/updateSupplier',
  async ({ supplierId, supplierData }: { supplierId: number; supplierData: SupplierUpdate }, { rejectWithValue }) => {
    try {
      const response = await supplierAPI.updateSupplier(supplierId, supplierData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update supplier');
    }
  }
);

export const deleteSupplier = createAsyncThunk(
  'supplier/deleteSupplier',
  async (supplierId: number) => {
    const response = await supplierAPI.deleteSupplier(supplierId);
    return { supplierId, message: response.data.message };
  }
);

export const bulkUpdateSupplierStatus = createAsyncThunk(
  'supplier/bulkUpdateStatus',
  async (bulkData: BulkStatusUpdate) => {
    const response = await supplierAPI.bulkUpdateStatus(bulkData);
    return response.data;
  }
);

// Material Management
export const fetchMaterials = createAsyncThunk(
  'supplier/fetchMaterials',
  async (params?: MaterialFilters & { page?: number; size?: number }) => {
    const response = await supplierAPI.getMaterials(params);
    return response.data;
  }
);

export const fetchMaterial = createAsyncThunk(
  'supplier/fetchMaterial',
  async (materialId: number) => {
    const response = await supplierAPI.getMaterial(materialId);
    return response.data;
  }
);

export const createMaterial = createAsyncThunk(
  'supplier/createMaterial',
  async (materialData: MaterialCreate) => {
    const response = await supplierAPI.createMaterial(materialData);
    return response.data;
  }
);

export const updateMaterial = createAsyncThunk(
  'supplier/updateMaterial',
  async ({ materialId, materialData }: { materialId: number; materialData: MaterialUpdate }) => {
    const response = await supplierAPI.updateMaterial(materialId, materialData);
    return response.data;
  }
);

export const deleteMaterial = createAsyncThunk(
  'supplier/deleteMaterial',
  async (materialId: number) => {
    const response = await supplierAPI.deleteMaterial(materialId);
    return { materialId, message: response.data.message };
  }
);

export const approveMaterial = createAsyncThunk(
  'supplier/approveMaterial',
  async ({ materialId, comments }: { materialId: number; comments?: string }) => {
    const response = await supplierAPI.approveMaterial(materialId, comments);
    return response.data;
  }
);

export const rejectMaterial = createAsyncThunk(
  'supplier/rejectMaterial',
  async ({ materialId, rejectionReason }: { materialId: number; rejectionReason: string }) => {
    const response = await supplierAPI.rejectMaterial(materialId, rejectionReason);
    return response.data;
  }
);

export const bulkApproveMaterials = createAsyncThunk(
  'supplier/bulkApproveMaterials',
  async ({ materialIds, comments }: { materialIds: number[]; comments?: string }) => {
    const response = await supplierAPI.bulkApproveMaterials(materialIds, comments);
    return response.data;
  }
);

export const bulkRejectMaterials = createAsyncThunk(
  'supplier/bulkRejectMaterials',
  async ({ materialIds, rejectionReason }: { materialIds: number[]; rejectionReason: string }) => {
    const response = await supplierAPI.bulkRejectMaterials(materialIds, rejectionReason);
    return response.data;
  }
);

// Evaluation Management
export const fetchEvaluations = createAsyncThunk(
  'supplier/fetchEvaluations',
  async (params?: EvaluationFilters & { page?: number; size?: number }) => {
    const response = await supplierAPI.getEvaluations(params);
    return response.data;
  }
);

export const fetchEvaluation = createAsyncThunk(
  'supplier/fetchEvaluation',
  async (evaluationId: number) => {
    const response = await supplierAPI.getEvaluation(evaluationId);
    return response.data;
  }
);

export const createEvaluation = createAsyncThunk(
  'supplier/createEvaluation',
  async (evaluationData: EvaluationCreate) => {
    const response = await supplierAPI.createEvaluation(evaluationData);
    return response.data;
  }
);

export const updateEvaluation = createAsyncThunk(
  'supplier/updateEvaluation',
  async ({ evaluationId, evaluationData }: { evaluationId: number; evaluationData: EvaluationUpdate }) => {
    const response = await supplierAPI.updateEvaluation(evaluationId, evaluationData);
    return response.data;
  }
);

export const deleteEvaluation = createAsyncThunk(
  'supplier/deleteEvaluation',
  async (evaluationId: number) => {
    const response = await supplierAPI.deleteEvaluation(evaluationId);
    return { evaluationId, message: response.data.message };
  }
);

// Delivery Management
export const fetchDeliveries = createAsyncThunk(
  'supplier/fetchDeliveries',
  async (params?: DeliveryFilters & { page?: number; size?: number }) => {
    const response = await supplierAPI.getDeliveries(params);
    return response.data;
  }
);

export const fetchDelivery = createAsyncThunk(
  'supplier/fetchDelivery',
  async (deliveryId: number) => {
    const response = await supplierAPI.getDelivery(deliveryId);
    return response.data;
  }
);

export const createDelivery = createAsyncThunk(
  'supplier/createDelivery',
  async (deliveryData: DeliveryCreate) => {
    const response = await supplierAPI.createDelivery(deliveryData);
    return response.data;
  }
);

export const updateDelivery = createAsyncThunk(
  'supplier/updateDelivery',
  async ({ deliveryId, deliveryData }: { deliveryId: number; deliveryData: DeliveryUpdate }) => {
    const response = await supplierAPI.updateDelivery(deliveryId, deliveryData);
    return response.data;
  }
);

export const deleteDelivery = createAsyncThunk(
  'supplier/deleteDelivery',
  async (deliveryId: number) => {
    const response = await supplierAPI.deleteDelivery(deliveryId);
    return { deliveryId, message: response.data.message };
  }
);

export const inspectDelivery = createAsyncThunk(
  'supplier/inspectDelivery',
  async ({ deliveryId, inspectionData }: { 
    deliveryId: number; 
    inspectionData: { status: 'passed' | 'failed' | 'under_review'; comments?: string } 
  }) => {
    const response = await supplierAPI.inspectDelivery(deliveryId, inspectionData);
    return response.data;
  }
);

export const createQualityAlert = createAsyncThunk(
  'supplier/createQualityAlert',
  async ({ deliveryId, alertData }: { 
    deliveryId: number; 
    alertData: { 
      alert_type: 'temperature' | 'damage' | 'expiry' | 'contamination' | 'documentation' | 'other';
      severity: 'low' | 'medium' | 'high' | 'critical';
      description: string;
    } 
  }) => {
    const response = await supplierAPI.createQualityAlert(deliveryId, alertData);
    return response.data;
  }
);

export const resolveQualityAlert = createAsyncThunk(
  'supplier/resolveQualityAlert',
  async ({ alertId, resolutionData }: { 
    alertId: number; 
    resolutionData: { action_taken: string } 
  }) => {
    const response = await supplierAPI.resolveQualityAlert(alertId, resolutionData);
    return response.data;
  }
);

// Document Management
export const fetchSupplierDocuments = createAsyncThunk(
  'supplier/fetchSupplierDocuments',
  async ({ supplierId, params }: { 
    supplierId: number; 
    params?: { document_type?: string; verification_status?: string; page?: number; size?: number } 
  }) => {
    const response = await supplierAPI.getSupplierDocuments(supplierId, params);
    return response.data;
  }
);

export const uploadSupplierDocument = createAsyncThunk(
  'supplier/uploadSupplierDocument',
  async ({ supplierId, documentData, file }: { 
    supplierId: number; 
    documentData: SupplierDocumentCreate; 
    file: File 
  }) => {
    const response = await supplierAPI.uploadSupplierDocument(supplierId, documentData, file);
    return response.data;
  }
);

export const updateSupplierDocument = createAsyncThunk(
  'supplier/updateSupplierDocument',
  async ({ documentId, documentData }: { 
    documentId: number; 
    documentData: SupplierDocumentUpdate 
  }) => {
    const response = await supplierAPI.updateSupplierDocument(documentId, documentData);
    return response.data;
  }
);

export const deleteSupplierDocument = createAsyncThunk(
  'supplier/deleteSupplierDocument',
  async (documentId: number) => {
    const response = await supplierAPI.deleteSupplierDocument(documentId);
    return { documentId, message: response.data.message };
  }
);

export const verifyDocument = createAsyncThunk(
  'supplier/verifyDocument',
  async ({ documentId, verificationData }: { 
    documentId: number; 
    verificationData: { verification_status: 'verified' | 'rejected'; verification_comments?: string } 
  }) => {
    const response = await supplierAPI.verifyDocument(documentId, verificationData);
    return response.data;
  }
);

// Dashboard and Analytics
export const fetchSupplierDashboard = createAsyncThunk(
  'supplier/fetchDashboard',
  async (_, { rejectWithValue }) => {
    try {
      const response = await supplierAPI.getDashboard();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch dashboard');
    }
  }
);

export const fetchPerformanceAnalytics = createAsyncThunk(
  'supplier/fetchPerformanceAnalytics',
  async (params?: { date_from?: string; date_to?: string; supplier_id?: number }) => {
    const response = await supplierAPI.getPerformanceAnalytics(params);
    return response.data;
  }
);

export const fetchRiskAssessment = createAsyncThunk(
  'supplier/fetchRiskAssessment',
  async () => {
    const response = await supplierAPI.getRiskAssessment();
    return response.data;
  }
);

// Alerts
export const fetchAlerts = createAsyncThunk(
  'supplier/fetchAlerts',
  async (params?: { severity?: 'low' | 'medium' | 'high' | 'critical'; type?: string; resolved?: boolean; page?: number; size?: number }) => {
    const response = await supplierAPI.getAlerts(params);
    return response.data;
  }
);

export const resolveAlert = createAsyncThunk(
  'supplier/resolveAlert',
  async (alertId: number) => {
    const response = await supplierAPI.resolveAlert(alertId);
    return { alertId, message: response.data.message };
  }
);

// Statistics
export const fetchSupplierStats = createAsyncThunk(
  'supplier/fetchSupplierStats',
  async () => {
    const response = await supplierAPI.getSupplierStats();
    return response.data;
  }
);

export const fetchMaterialStats = createAsyncThunk(
  'supplier/fetchMaterialStats',
  async () => {
    const response = await supplierAPI.getMaterialStats();
    return response.data;
  }
);

export const fetchEvaluationStats = createAsyncThunk(
  'supplier/fetchEvaluationStats',
  async () => {
    const response = await supplierAPI.getEvaluationStats();
    return response.data;
  }
);

// State Interface
interface SupplierState {
  // Suppliers
  suppliers: PaginatedResponse<Supplier> | null;
  selectedSupplier: Supplier | null;
  suppliersLoading: boolean;
  suppliersError: string | null;

  // Materials
  materials: PaginatedResponse<Material> | null;
  selectedMaterial: Material | null;
  materialsLoading: boolean;
  materialsError: string | null;

  // Evaluations
  evaluations: PaginatedResponse<Evaluation> | null;
  selectedEvaluation: Evaluation | null;
  evaluationsLoading: boolean;
  evaluationsError: string | null;

  // Deliveries
  deliveries: PaginatedResponse<Delivery> | null;
  selectedDelivery: Delivery | null;
  deliveriesLoading: boolean;
  deliveriesError: string | null;

  // Documents
  supplierDocuments: PaginatedResponse<SupplierDocument> | null;
  documentsLoading: boolean;
  documentsError: string | null;

  // Dashboard
  dashboard: SupplierDashboard | null;
  dashboardLoading: boolean;
  dashboardError: string | null;

  // Analytics
  performanceAnalytics: any | null;
  riskAssessment: any | null;
  analyticsLoading: boolean;
  analyticsError: string | null;

  // Alerts
  alerts: PaginatedResponse<any> | null;
  alertsLoading: boolean;
  alertsError: string | null;

  // Statistics
  supplierStats: any | null;
  materialStats: any | null;
  evaluationStats: any | null;
  statsLoading: boolean;
  statsError: string | null;

  // UI State
  filters: {
    suppliers: SupplierFilters;
    materials: MaterialFilters;
    evaluations: EvaluationFilters;
    deliveries: DeliveryFilters;
  };
  selectedItems: {
    suppliers: number[];
    materials: number[];
    evaluations: number[];
    deliveries: number[];
  };
}

// Initial State
const initialState: SupplierState = {
  // Suppliers
  suppliers: null,
  selectedSupplier: null,
  suppliersLoading: false,
  suppliersError: null,

  // Materials
  materials: null,
  selectedMaterial: null,
  materialsLoading: false,
  materialsError: null,

  // Evaluations
  evaluations: null,
  selectedEvaluation: null,
  evaluationsLoading: false,
  evaluationsError: null,

  // Deliveries
  deliveries: null,
  selectedDelivery: null,
  deliveriesLoading: false,
  deliveriesError: null,

  // Documents
  supplierDocuments: null,
  documentsLoading: false,
  documentsError: null,

  // Dashboard
  dashboard: null,
  dashboardLoading: false,
  dashboardError: null,

  // Analytics
  performanceAnalytics: null,
  riskAssessment: null,
  analyticsLoading: false,
  analyticsError: null,

  // Alerts
  alerts: null,
  alertsLoading: false,
  alertsError: null,

  // Statistics
  supplierStats: null,
  materialStats: null,
  evaluationStats: null,
  statsLoading: false,
  statsError: null,

  // UI State
  filters: {
    suppliers: {},
    materials: {},
    evaluations: {},
    deliveries: {},
  },
  selectedItems: {
    suppliers: [],
    materials: [],
    evaluations: [],
    deliveries: [],
  },
};

// Slice
const supplierSlice = createSlice({
  name: 'supplier',
  initialState,
  reducers: {
    // Clear errors
    clearErrors: (state) => {
      state.suppliersError = null;
      state.materialsError = null;
      state.evaluationsError = null;
      state.deliveriesError = null;
      state.documentsError = null;
      state.dashboardError = null;
      state.analyticsError = null;
      state.alertsError = null;
      state.statsError = null;
    },

    // Set selected items
    setSelectedSuppliers: (state, action: PayloadAction<number[]>) => {
      state.selectedItems.suppliers = action.payload;
    },

    setSelectedMaterials: (state, action: PayloadAction<number[]>) => {
      state.selectedItems.materials = action.payload;
    },

    setSelectedEvaluations: (state, action: PayloadAction<number[]>) => {
      state.selectedItems.evaluations = action.payload;
    },

    setSelectedDeliveries: (state, action: PayloadAction<number[]>) => {
      state.selectedItems.deliveries = action.payload;
    },

    // Set filters
    setSupplierFilters: (state, action: PayloadAction<SupplierFilters>) => {
      state.filters.suppliers = { ...state.filters.suppliers, ...action.payload };
    },

    setMaterialFilters: (state, action: PayloadAction<MaterialFilters>) => {
      state.filters.materials = { ...state.filters.materials, ...action.payload };
    },

    setEvaluationFilters: (state, action: PayloadAction<EvaluationFilters>) => {
      state.filters.evaluations = { ...state.filters.evaluations, ...action.payload };
    },

    setDeliveryFilters: (state, action: PayloadAction<DeliveryFilters>) => {
      state.filters.deliveries = { ...state.filters.deliveries, ...action.payload };
    },

    // Clear filters
    clearSupplierFilters: (state) => {
      state.filters.suppliers = {};
    },

    clearMaterialFilters: (state) => {
      state.filters.materials = {};
    },

    clearEvaluationFilters: (state) => {
      state.filters.evaluations = {};
    },

    clearDeliveryFilters: (state) => {
      state.filters.deliveries = {};
    },

    // Set selected entities
    setSelectedSupplier: (state, action: PayloadAction<Supplier | null>) => {
      state.selectedSupplier = action.payload;
    },

    setSelectedMaterial: (state, action: PayloadAction<Material | null>) => {
      state.selectedMaterial = action.payload;
    },

    setSelectedEvaluation: (state, action: PayloadAction<Evaluation | null>) => {
      state.selectedEvaluation = action.payload;
    },

    setSelectedDelivery: (state, action: PayloadAction<Delivery | null>) => {
      state.selectedDelivery = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Supplier Management
    builder
      .addCase(fetchSuppliers.pending, (state) => {
        state.suppliersLoading = true;
        state.suppliersError = null;
      })
      .addCase(fetchSuppliers.fulfilled, (state, action) => {
        state.suppliersLoading = false;
        state.suppliers = action.payload;
      })
      .addCase(fetchSuppliers.rejected, (state, action) => {
        state.suppliersLoading = false;
        state.suppliersError = action.error.message || 'Failed to fetch suppliers';
      })
      .addCase(fetchSupplier.pending, (state) => {
        state.suppliersLoading = true;
        state.suppliersError = null;
      })
      .addCase(fetchSupplier.fulfilled, (state, action) => {
        state.suppliersLoading = false;
        state.selectedSupplier = action.payload;
      })
      .addCase(fetchSupplier.rejected, (state, action) => {
        state.suppliersLoading = false;
        state.suppliersError = action.error.message || 'Failed to fetch supplier';
      })
      .addCase(createSupplier.fulfilled, (state, action) => {
        if (state.suppliers) {
          state.suppliers.items.unshift(action.payload);
          state.suppliers.total += 1;
        }
      })
      .addCase(updateSupplier.fulfilled, (state, action) => {
        if (state.suppliers) {
          const index = state.suppliers.items.findIndex(s => s.id === action.payload.id);
          if (index !== -1) {
            state.suppliers.items[index] = action.payload;
          }
        }
        if (state.selectedSupplier?.id === action.payload.id) {
          state.selectedSupplier = action.payload;
        }
      })
      .addCase(deleteSupplier.fulfilled, (state, action) => {
        if (state.suppliers) {
          state.suppliers.items = state.suppliers.items.filter(s => s.id !== action.payload.supplierId);
          state.suppliers.total -= 1;
        }
      });

    // Material Management
    builder
      .addCase(fetchMaterials.pending, (state) => {
        state.materialsLoading = true;
        state.materialsError = null;
      })
      .addCase(fetchMaterials.fulfilled, (state, action) => {
        state.materialsLoading = false;
        state.materials = action.payload;
      })
      .addCase(fetchMaterials.rejected, (state, action) => {
        state.materialsLoading = false;
        state.materialsError = action.error.message || 'Failed to fetch materials';
      })
      .addCase(fetchMaterial.pending, (state) => {
        state.materialsLoading = true;
        state.materialsError = null;
      })
      .addCase(fetchMaterial.fulfilled, (state, action) => {
        state.materialsLoading = false;
        state.selectedMaterial = action.payload;
      })
      .addCase(fetchMaterial.rejected, (state, action) => {
        state.materialsLoading = false;
        state.materialsError = action.error.message || 'Failed to fetch material';
      })
      .addCase(createMaterial.fulfilled, (state, action) => {
        if (state.materials) {
          state.materials.items.unshift(action.payload);
          state.materials.total += 1;
        }
      })
      .addCase(updateMaterial.fulfilled, (state, action) => {
        if (state.materials) {
          const index = state.materials.items.findIndex(m => m.id === action.payload.id);
          if (index !== -1) {
            state.materials.items[index] = action.payload;
          }
        }
        if (state.selectedMaterial?.id === action.payload.id) {
          state.selectedMaterial = action.payload;
        }
      })
      .addCase(deleteMaterial.fulfilled, (state, action) => {
        if (state.materials) {
          state.materials.items = state.materials.items.filter(m => m.id !== action.payload.materialId);
          state.materials.total -= 1;
        }
      })
      .addCase(approveMaterial.fulfilled, (state, action) => {
        if (state.materials) {
          const index = state.materials.items.findIndex(m => m.id === action.payload.id);
          if (index !== -1) {
            state.materials.items[index] = action.payload;
          }
        }
        if (state.selectedMaterial?.id === action.payload.id) {
          state.selectedMaterial = action.payload;
        }
      })
      .addCase(rejectMaterial.fulfilled, (state, action) => {
        if (state.materials) {
          const index = state.materials.items.findIndex(m => m.id === action.payload.id);
          if (index !== -1) {
            state.materials.items[index] = action.payload;
          }
        }
        if (state.selectedMaterial?.id === action.payload.id) {
          state.selectedMaterial = action.payload;
        }
      });

    // Evaluation Management
    builder
      .addCase(fetchEvaluations.pending, (state) => {
        state.evaluationsLoading = true;
        state.evaluationsError = null;
      })
      .addCase(fetchEvaluations.fulfilled, (state, action) => {
        state.evaluationsLoading = false;
        state.evaluations = action.payload;
      })
      .addCase(fetchEvaluations.rejected, (state, action) => {
        state.evaluationsLoading = false;
        state.evaluationsError = action.error.message || 'Failed to fetch evaluations';
      })
      .addCase(fetchEvaluation.pending, (state) => {
        state.evaluationsLoading = true;
        state.evaluationsError = null;
      })
      .addCase(fetchEvaluation.fulfilled, (state, action) => {
        state.evaluationsLoading = false;
        state.selectedEvaluation = action.payload;
      })
      .addCase(fetchEvaluation.rejected, (state, action) => {
        state.evaluationsLoading = false;
        state.evaluationsError = action.error.message || 'Failed to fetch evaluation';
      })
      .addCase(createEvaluation.fulfilled, (state, action) => {
        if (state.evaluations) {
          state.evaluations.items.unshift(action.payload);
          state.evaluations.total += 1;
        }
      })
      .addCase(updateEvaluation.fulfilled, (state, action) => {
        if (state.evaluations) {
          const index = state.evaluations.items.findIndex(e => e.id === action.payload.id);
          if (index !== -1) {
            state.evaluations.items[index] = action.payload;
          }
        }
        if (state.selectedEvaluation?.id === action.payload.id) {
          state.selectedEvaluation = action.payload;
        }
      })
      .addCase(deleteEvaluation.fulfilled, (state, action) => {
        if (state.evaluations) {
          state.evaluations.items = state.evaluations.items.filter(e => e.id !== action.payload.evaluationId);
          state.evaluations.total -= 1;
        }
      });

    // Delivery Management
    builder
      .addCase(fetchDeliveries.pending, (state) => {
        state.deliveriesLoading = true;
        state.deliveriesError = null;
      })
      .addCase(fetchDeliveries.fulfilled, (state, action) => {
        state.deliveriesLoading = false;
        state.deliveries = action.payload;
      })
      .addCase(fetchDeliveries.rejected, (state, action) => {
        state.deliveriesLoading = false;
        state.deliveriesError = action.error.message || 'Failed to fetch deliveries';
      })
      .addCase(fetchDelivery.pending, (state) => {
        state.deliveriesLoading = true;
        state.deliveriesError = null;
      })
      .addCase(fetchDelivery.fulfilled, (state, action) => {
        state.deliveriesLoading = false;
        state.selectedDelivery = action.payload;
      })
      .addCase(fetchDelivery.rejected, (state, action) => {
        state.deliveriesLoading = false;
        state.deliveriesError = action.error.message || 'Failed to fetch delivery';
      })
      .addCase(createDelivery.fulfilled, (state, action) => {
        if (state.deliveries) {
          state.deliveries.items.unshift(action.payload);
          state.deliveries.total += 1;
        }
      })
      .addCase(updateDelivery.fulfilled, (state, action) => {
        if (state.deliveries) {
          const index = state.deliveries.items.findIndex(d => d.id === action.payload.id);
          if (index !== -1) {
            state.deliveries.items[index] = action.payload;
          }
        }
        if (state.selectedDelivery?.id === action.payload.id) {
          state.selectedDelivery = action.payload;
        }
      })
      .addCase(deleteDelivery.fulfilled, (state, action) => {
        if (state.deliveries) {
          state.deliveries.items = state.deliveries.items.filter(d => d.id !== action.payload.deliveryId);
          state.deliveries.total -= 1;
        }
      })
      .addCase(inspectDelivery.fulfilled, (state, action) => {
        if (state.deliveries) {
          const index = state.deliveries.items.findIndex(d => d.id === action.payload.id);
          if (index !== -1) {
            state.deliveries.items[index] = action.payload;
          }
        }
        if (state.selectedDelivery?.id === action.payload.id) {
          state.selectedDelivery = action.payload;
        }
      });

    // Document Management
    builder
      .addCase(fetchSupplierDocuments.pending, (state) => {
        state.documentsLoading = true;
        state.documentsError = null;
      })
      .addCase(fetchSupplierDocuments.fulfilled, (state, action) => {
        state.documentsLoading = false;
        state.supplierDocuments = action.payload;
      })
      .addCase(fetchSupplierDocuments.rejected, (state, action) => {
        state.documentsLoading = false;
        state.documentsError = action.error.message || 'Failed to fetch documents';
      })
      .addCase(uploadSupplierDocument.fulfilled, (state, action) => {
        if (state.supplierDocuments) {
          state.supplierDocuments.items.unshift(action.payload);
          state.supplierDocuments.total += 1;
        }
      })
      .addCase(updateSupplierDocument.fulfilled, (state, action) => {
        if (state.supplierDocuments) {
          const index = state.supplierDocuments.items.findIndex(d => d.id === action.payload.id);
          if (index !== -1) {
            state.supplierDocuments.items[index] = action.payload;
          }
        }
      })
      .addCase(deleteSupplierDocument.fulfilled, (state, action) => {
        if (state.supplierDocuments) {
          state.supplierDocuments.items = state.supplierDocuments.items.filter(d => d.id !== action.payload.documentId);
          state.supplierDocuments.total -= 1;
        }
      })
      .addCase(verifyDocument.fulfilled, (state, action) => {
        if (state.supplierDocuments) {
          const index = state.supplierDocuments.items.findIndex(d => d.id === action.payload.id);
          if (index !== -1) {
            state.supplierDocuments.items[index] = action.payload;
          }
        }
      });

    // Dashboard and Analytics
    builder
      .addCase(fetchSupplierDashboard.pending, (state) => {
        state.dashboardLoading = true;
        state.dashboardError = null;
      })
      .addCase(fetchSupplierDashboard.fulfilled, (state, action) => {
        state.dashboardLoading = false;
        state.dashboard = action.payload;
      })
      .addCase(fetchSupplierDashboard.rejected, (state, action) => {
        state.dashboardLoading = false;
        state.dashboardError = action.error.message || 'Failed to fetch dashboard';
      })
      .addCase(fetchPerformanceAnalytics.pending, (state) => {
        state.analyticsLoading = true;
        state.analyticsError = null;
      })
      .addCase(fetchPerformanceAnalytics.fulfilled, (state, action) => {
        state.analyticsLoading = false;
        state.performanceAnalytics = action.payload;
      })
      .addCase(fetchPerformanceAnalytics.rejected, (state, action) => {
        state.analyticsLoading = false;
        state.analyticsError = action.error.message || 'Failed to fetch performance analytics';
      })
      .addCase(fetchRiskAssessment.pending, (state) => {
        state.analyticsLoading = true;
        state.analyticsError = null;
      })
      .addCase(fetchRiskAssessment.fulfilled, (state, action) => {
        state.analyticsLoading = false;
        state.riskAssessment = action.payload;
      })
      .addCase(fetchRiskAssessment.rejected, (state, action) => {
        state.analyticsLoading = false;
        state.analyticsError = action.error.message || 'Failed to fetch risk assessment';
      });

    // Alerts
    builder
      .addCase(fetchAlerts.pending, (state) => {
        state.alertsLoading = true;
        state.alertsError = null;
      })
      .addCase(fetchAlerts.fulfilled, (state, action) => {
        state.alertsLoading = false;
        state.alerts = action.payload;
      })
      .addCase(fetchAlerts.rejected, (state, action) => {
        state.alertsLoading = false;
        state.alertsError = action.error.message || 'Failed to fetch alerts';
      })
      .addCase(resolveAlert.fulfilled, (state, action) => {
        if (state.alerts) {
          const index = state.alerts.items.findIndex(a => a.id === action.payload.alertId);
          if (index !== -1) {
            state.alerts.items[index].resolved = true;
          }
        }
      });

    // Statistics
    builder
      .addCase(fetchSupplierStats.pending, (state) => {
        state.statsLoading = true;
        state.statsError = null;
      })
      .addCase(fetchSupplierStats.fulfilled, (state, action) => {
        state.statsLoading = false;
        state.supplierStats = action.payload;
      })
      .addCase(fetchSupplierStats.rejected, (state, action) => {
        state.statsLoading = false;
        state.statsError = action.error.message || 'Failed to fetch supplier stats';
      })
      .addCase(fetchMaterialStats.pending, (state) => {
        state.statsLoading = true;
        state.statsError = null;
      })
      .addCase(fetchMaterialStats.fulfilled, (state, action) => {
        state.statsLoading = false;
        state.materialStats = action.payload;
      })
      .addCase(fetchMaterialStats.rejected, (state, action) => {
        state.statsLoading = false;
        state.statsError = action.error.message || 'Failed to fetch material stats';
      })
      .addCase(fetchEvaluationStats.pending, (state) => {
        state.statsLoading = true;
        state.statsError = null;
      })
      .addCase(fetchEvaluationStats.fulfilled, (state, action) => {
        state.statsLoading = false;
        state.evaluationStats = action.payload;
      })
      .addCase(fetchEvaluationStats.rejected, (state, action) => {
        state.statsLoading = false;
        state.statsError = action.error.message || 'Failed to fetch evaluation stats';
      });
  },
});

export const {
  clearErrors,
  setSelectedSuppliers,
  setSelectedMaterials,
  setSelectedEvaluations,
  setSelectedDeliveries,
  setSupplierFilters,
  setMaterialFilters,
  setEvaluationFilters,
  setDeliveryFilters,
  clearSupplierFilters,
  clearMaterialFilters,
  clearEvaluationFilters,
  clearDeliveryFilters,
  setSelectedSupplier,
  setSelectedMaterial,
  setSelectedEvaluation,
  setSelectedDelivery,
} = supplierSlice.actions;

export default supplierSlice.reducer; 