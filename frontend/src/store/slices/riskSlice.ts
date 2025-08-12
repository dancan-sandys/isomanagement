import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import riskAPI, { RiskListParams } from '../../services/riskAPI';

export interface RiskItem {
  id: number;
  risk_number: string;
  item_type: 'risk' | 'opportunity';
  title: string;
  description?: string;
  category: string;
  status: string;
  severity: string;
  likelihood: string;
  impact_score?: number;
  risk_score: number;
  mitigation_plan?: string;
  residual_risk?: string;
  assigned_to?: number;
  due_date?: string;
  next_review_date?: string;
  references?: string;
  created_by: number;
  created_at: string;
  updated_at?: string;
}

export interface RiskStats {
  total: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  by_severity: Record<string, number>;
  by_item_type: Record<string, number>;
}

interface RiskState {
  items: RiskItem[];
  selected: RiskItem | null;
  stats: RiskStats | null;
  loading: boolean;
  error: string | null;
  page: number;
  size: number;
  total: number;
  filters: RiskListParams;
}

const initialState: RiskState = {
  items: [],
  selected: null,
  stats: null,
  loading: false,
  error: null,
  page: 1,
  size: 20,
  total: 0,
  filters: {},
};

export const fetchRiskItems = createAsyncThunk(
  'risk/fetchList',
  async (params: RiskListParams = {}) => {
    const resp = await riskAPI.list(params);
    return resp.data || resp; // ResponseModel or raw
  }
);

export const fetchRiskStats = createAsyncThunk(
  'risk/fetchStats',
  async () => {
    const resp = await riskAPI.stats();
    return resp.data || resp;
  }
);

export const createRisk = createAsyncThunk(
  'risk/create',
  async (payload: Partial<RiskItem>) => {
    const resp = await riskAPI.create(payload);
    return resp.data || resp;
  }
);

export const updateRisk = createAsyncThunk(
  'risk/update',
  async ({ id, payload }: { id: number; payload: Partial<RiskItem> }) => {
    const resp = await riskAPI.update(id, payload);
    return resp.data || resp;
  }
);

export const deleteRisk = createAsyncThunk(
  'risk/delete',
  async (id: number) => {
    const resp = await riskAPI.remove(id);
    return { id, resp };
  }
);

const riskSlice = createSlice({
  name: 'risk',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<Partial<RiskListParams>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    setPage: (state, action: PayloadAction<number>) => {
      state.page = action.payload;
    },
    setSize: (state, action: PayloadAction<number>) => {
      state.size = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    setSelected: (state, action: PayloadAction<RiskItem | null>) => {
      state.selected = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRiskItems.pending, (state) => {
        state.loading = true; state.error = null;
      })
      .addCase(fetchRiskItems.fulfilled, (state, action) => {
        state.loading = false;
        const d = action.payload;
        state.items = d.items || d?.data?.items || [];
        state.total = d.total || d?.data?.total || 0;
        state.page = d.page || d?.data?.page || state.page;
        state.size = d.size || d?.data?.size || state.size;
      })
      .addCase(fetchRiskItems.rejected, (state, action) => {
        state.loading = false; state.error = action.error.message || 'Failed to fetch risks';
      })
      .addCase(fetchRiskStats.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchRiskStats.fulfilled, (state, action) => {
        state.loading = false; state.stats = action.payload || null;
      })
      .addCase(fetchRiskStats.rejected, (state, action) => { state.loading = false; state.error = action.error.message || 'Failed to fetch stats'; })
      .addCase(createRisk.fulfilled, (state) => { /* refresh list elsewhere */ })
      .addCase(updateRisk.fulfilled, (state) => { /* refresh list elsewhere */ })
      .addCase(deleteRisk.fulfilled, (state, action) => {
        state.items = state.items.filter(i => i.id !== action.payload.id);
      });
  }
});

export const { setFilters, setPage, setSize, clearError, setSelected } = riskSlice.actions;
export default riskSlice.reducer;


