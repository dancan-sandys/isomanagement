import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { haccpAPI } from '../../services/haccpAPI';

// Types
export interface Product {
  id: number;
  product_code: string;
  name: string;
  description?: string;
  category?: string;
  formulation?: string;
  allergens?: string;
  shelf_life_days?: number;
  storage_conditions?: string;
  packaging_type?: string;
  haccp_plan_approved: boolean;
  haccp_plan_version?: string;
  ccp_count: number;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

export interface ProcessFlow {
  id: number;
  step_number: number;
  step_name: string;
  description?: string;
  equipment?: string;
  temperature?: number;
  time_minutes?: number;
  ph?: number;
  aw?: number;
  parameters?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface Hazard {
  id: number;
  process_step_id: number;
  hazard_type: 'biological' | 'chemical' | 'physical' | 'allergen';
  hazard_name: string;
  description?: string;
  likelihood: number;
  severity: number;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  control_measures?: string;
  is_controlled: boolean;
  control_effectiveness?: number;
  is_ccp: boolean;
  ccp_justification?: string;
  created_at: string;
  updated_at?: string;
}

export interface CCP {
  id: number;
  ccp_number: string;
  ccp_name: string;
  description?: string;
  status: 'active' | 'inactive' | 'suspended';
  critical_limit_min?: number;
  critical_limit_max?: number;
  critical_limit_unit?: string;
  critical_limit_description?: string;
  monitoring_frequency?: string;
  monitoring_method?: string;
  monitoring_responsible?: number;
  monitoring_equipment?: string;
  corrective_actions?: string;
  verification_frequency?: string;
  verification_method?: string;
  verification_responsible?: number;
  created_at: string;
  updated_at?: string;
}

export interface MonitoringLog {
  id: number;
  batch_number: string;
  monitoring_time: string;
  measured_value: number;
  unit?: string;
  is_within_limits: boolean;
  additional_parameters?: Record<string, any>;
  observations?: string;
  evidence_files?: string;
  corrective_action_taken: boolean;
  corrective_action_description?: string;
  created_by: string;
  created_at: string;
}

export interface VerificationLog {
  id: number;
  verification_date: string;
  verification_method?: string;
  verification_result?: string;
  is_compliant: boolean;
  samples_tested?: number;
  test_results?: Record<string, any>;
  equipment_calibration?: boolean;
  calibration_date?: string;
  evidence_files?: string;
  created_by: string;
  created_at: string;
}

export interface HACCPDashboardStats {
  total_products: number;
  approved_plans: number;
  total_ccps: number;
  active_ccps: number;
  out_of_spec_count: number;
  recent_logs: Array<Record<string, any>>;
}

export interface HACCPState {
  products: Product[];
  selectedProduct: Product | null;
  processFlows: ProcessFlow[];
  hazards: Hazard[];
  ccps: CCP[];
  monitoringLogs: MonitoringLog[];
  verificationLogs: VerificationLog[];
  dashboardStats: HACCPDashboardStats | null;
  loading: boolean;
  error: string | null;
  selectedCCP: CCP | null;
  selectedHazard: Hazard | null;
}

const initialState: HACCPState = {
  products: [],
  selectedProduct: null,
  processFlows: [],
  hazards: [],
  ccps: [],
  monitoringLogs: [],
  verificationLogs: [],
  dashboardStats: null,
  loading: false,
  error: null,
  selectedCCP: null,
  selectedHazard: null,
};

// Async thunks
export const fetchProducts = createAsyncThunk(
  'haccp/fetchProducts',
  async (_, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.getProducts();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch products');
    }
  }
);

export const fetchProduct = createAsyncThunk(
  'haccp/fetchProduct',
  async (productId: number, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.getProduct(productId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch product');
    }
  }
);

export const createProduct = createAsyncThunk(
  'haccp/createProduct',
  async (productData: any, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.createProduct(productData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create product');
    }
  }
);

export const updateProduct = createAsyncThunk(
  'haccp/updateProduct',
  async ({ productId, productData }: { productId: number; productData: any }, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.updateProduct(productId, productData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update product');
    }
  }
);

export const deleteProduct = createAsyncThunk(
  'haccp/deleteProduct',
  async (productId: number, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.deleteProduct(productId);
      return { productId, response };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete product');
    }
  }
);

export const createProcessFlow = createAsyncThunk(
  'haccp/createProcessFlow',
  async ({ productId, flowData }: { productId: number; flowData: any }, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.createProcessFlow(productId, flowData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create process flow');
    }
  }
);

export const updateProcessFlow = createAsyncThunk(
  'haccp/updateProcessFlow',
  async ({ flowId, flowData }: { flowId: number; flowData: any }, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.updateProcessFlow(flowId, flowData);
      return { id: flowId, response };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update process flow');
    }
  }
);

export const deleteProcessFlow = createAsyncThunk(
  'haccp/deleteProcessFlow',
  async (flowId: number, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.deleteProcessFlow(flowId);
      return { id: flowId, response };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete process flow');
    }
  }
);

export const createHazard = createAsyncThunk(
  'haccp/createHazard',
  async ({ productId, hazardData }: { productId: number; hazardData: any }, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.createHazard(productId, hazardData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create hazard');
    }
  }
);

export const updateHazard = createAsyncThunk(
  'haccp/updateHazard',
  async ({ hazardId, hazardData }: { hazardId: number; hazardData: any }, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.updateHazard(hazardId, hazardData);
      return { id: hazardId, response };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update hazard');
    }
  }
);

export const deleteHazard = createAsyncThunk(
  'haccp/deleteHazard',
  async (hazardId: number, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.deleteHazard(hazardId);
      return { id: hazardId, response };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete hazard');
    }
  }
);

export const createCCP = createAsyncThunk(
  'haccp/createCCP',
  async ({ productId, ccpData }: { productId: number; ccpData: any }, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.createCCP(productId, ccpData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create CCP');
    }
  }
);

export const updateCCP = createAsyncThunk(
  'haccp/updateCCP',
  async ({ ccpId, ccpData }: { ccpId: number; ccpData: any }, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.updateCCP(ccpId, ccpData);
      return { id: ccpId, response };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update CCP');
    }
  }
);

export const deleteCCP = createAsyncThunk(
  'haccp/deleteCCP',
  async (ccpId: number, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.deleteCCP(ccpId);
      return { id: ccpId, response };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete CCP');
    }
  }
);

export const createMonitoringLog = createAsyncThunk(
  'haccp/createMonitoringLog',
  async ({ ccpId, logData }: { ccpId: number; logData: any }, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.createMonitoringLog(ccpId, logData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create monitoring log');
    }
  }
);

export const createVerificationLog = createAsyncThunk(
  'haccp/createVerificationLog',
  async ({ ccpId, logData }: { ccpId: number; logData: any }, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.createVerificationLog(ccpId, logData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create verification log');
    }
  }
);

export const fetchDashboard = createAsyncThunk(
  'haccp/fetchDashboard',
  async (_, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.getDashboard();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch dashboard');
    }
  }
);

export const runDecisionTree = createAsyncThunk(
  'haccp/runDecisionTree',
  async (hazardId: number, { rejectWithValue }) => {
    try {
      const response = await haccpAPI.runDecisionTree(hazardId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to run decision tree');
    }
  }
);

// Slice
const haccpSlice = createSlice({
  name: 'haccp',
  initialState,
  reducers: {
    setSelectedProduct: (state, action: PayloadAction<Product | null>) => {
      state.selectedProduct = action.payload;
    },
    setSelectedCCP: (state, action: PayloadAction<CCP | null>) => {
      state.selectedCCP = action.payload;
    },
    setSelectedHazard: (state, action: PayloadAction<Hazard | null>) => {
      state.selectedHazard = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // fetchProducts
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.products = action.payload.data.items || [];
        state.error = null;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // fetchProduct
    builder
      .addCase(fetchProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProduct.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedProduct = action.payload.data;
        state.processFlows = action.payload.data.process_flows || [];
        state.hazards = action.payload.data.hazards || [];
        state.ccps = action.payload.data.ccps || [];
        state.error = null;
      })
      .addCase(fetchProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // createProduct
    builder
      .addCase(createProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createProduct.fulfilled, (state, action) => {
        state.loading = false;
        const newProduct = {
          ...action.payload.data,
          ccp_count: 0 // Add default ccp_count for new products
        };
        state.products.unshift(newProduct);
        state.error = null;
      })
      .addCase(createProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // updateProduct
    builder
      .addCase(updateProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProduct.fulfilled, (state, action) => {
        state.loading = false;
        const updatedProduct = {
          ...action.payload.data,
          ccp_count: state.products.find(p => p.id === action.payload.data.id)?.ccp_count || 0
        };
        const index = state.products.findIndex(p => p.id === updatedProduct.id);
        if (index !== -1) {
          state.products[index] = updatedProduct;
        }
        if (state.selectedProduct?.id === updatedProduct.id) {
          state.selectedProduct = updatedProduct;
        }
        state.error = null;
      })
      .addCase(updateProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // deleteProduct
    builder
      .addCase(deleteProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteProduct.fulfilled, (state, action) => {
        state.loading = false;
        const { productId } = action.payload;
        state.products = state.products.filter(p => p.id !== productId);
        if (state.selectedProduct?.id === productId) {
          state.selectedProduct = null;
        }
        state.error = null;
      })
      .addCase(deleteProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // createProcessFlow
    builder
      .addCase(createProcessFlow.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createProcessFlow.fulfilled, (state, action) => {
        state.loading = false;
        state.processFlows.push(action.payload.data);
        state.error = null;
      })
      .addCase(createProcessFlow.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // updateProcessFlow
    builder
      .addCase(updateProcessFlow.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProcessFlow.fulfilled, (state) => {
        state.loading = false;
        state.error = null;
      })
      .addCase(updateProcessFlow.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // deleteProcessFlow
    builder
      .addCase(deleteProcessFlow.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteProcessFlow.fulfilled, (state, action) => {
        state.loading = false;
        const id = action.payload.id;
        state.processFlows = state.processFlows.filter(f => f.id !== id);
        state.error = null;
      })
      .addCase(deleteProcessFlow.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // createHazard
    builder
      .addCase(createHazard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createHazard.fulfilled, (state, action) => {
        state.loading = false;
        state.hazards.push(action.payload.data);
        state.error = null;
      })
      .addCase(createHazard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // updateHazard
    builder
      .addCase(updateHazard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateHazard.fulfilled, (state) => {
        state.loading = false;
        state.error = null;
      })
      .addCase(updateHazard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // deleteHazard
    builder
      .addCase(deleteHazard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteHazard.fulfilled, (state, action) => {
        state.loading = false;
        const id = action.payload.id;
        state.hazards = state.hazards.filter(h => h.id !== id);
        state.error = null;
      })
      .addCase(deleteHazard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // createCCP
    builder
      .addCase(createCCP.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createCCP.fulfilled, (state, action) => {
        state.loading = false;
        state.ccps.push(action.payload.data);
        state.error = null;
      })
      .addCase(createCCP.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // updateCCP
    builder
      .addCase(updateCCP.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateCCP.fulfilled, (state) => {
        state.loading = false;
        state.error = null;
      })
      .addCase(updateCCP.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // deleteCCP
    builder
      .addCase(deleteCCP.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteCCP.fulfilled, (state, action) => {
        state.loading = false;
        const id = action.payload.id;
        state.ccps = state.ccps.filter(c => c.id !== id);
        state.error = null;
      })
      .addCase(deleteCCP.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // createMonitoringLog
    builder
      .addCase(createMonitoringLog.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createMonitoringLog.fulfilled, (state, action) => {
        state.loading = false;
        state.monitoringLogs.push(action.payload.data);
        state.error = null;
      })
      .addCase(createMonitoringLog.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // createVerificationLog
    builder
      .addCase(createVerificationLog.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createVerificationLog.fulfilled, (state, action) => {
        state.loading = false;
        state.verificationLogs.push(action.payload.data);
        state.error = null;
      })
      .addCase(createVerificationLog.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // fetchDashboard
    builder
      .addCase(fetchDashboard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboard.fulfilled, (state, action) => {
        state.loading = false;
        state.dashboardStats = action.payload.data;
        state.error = null;
      })
      .addCase(fetchDashboard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // runDecisionTree
    builder
      .addCase(runDecisionTree.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(runDecisionTree.fulfilled, (state, action) => {
        state.loading = false;
        state.error = null;
      })
      .addCase(runDecisionTree.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setSelectedProduct, setSelectedCCP, setSelectedHazard, clearError } = haccpSlice.actions;
export default haccpSlice.reducer; 