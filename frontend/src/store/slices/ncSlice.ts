import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { ncAPI } from '../../services/api';

export interface NcListState<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
  loading: boolean;
  error?: string;
}

export interface NonConformanceSummary {
  id: number;
  nc_number: string;
  title: string;
  status: string;
  severity: string;
  source: string;
  reported_date: string;
}

export interface NonConformanceDetail extends NonConformanceSummary {
  description: string;
  impact_area?: string;
  category?: string;
  batch_reference?: string;
  product_reference?: string;
  process_reference?: string;
  attachments?: any[];
  created_at: string;
  updated_at: string;
}

export interface CapaSummary {
  id: number;
  capa_number: string;
  title: string;
  status: string;
  responsible_person: number;
  target_completion_date: string;
  progress_percentage: number;
}

export interface CapaDetail extends CapaSummary {
  description: string;
  non_conformance_id: number;
  actual_completion_date?: string;
  effectiveness_measured: boolean;
  effectiveness_score?: number;
  created_at: string;
  updated_at: string;
}

export interface NcState {
  list: NcListState<NonConformanceSummary>;
  detail?: NonConformanceDetail;
  capaList: NcListState<CapaSummary>;
  capaDetail?: CapaDetail;
  rcaList: { items: any[]; loading: boolean; error?: string };
}

const initialList = { items: [], total: 0, page: 1, size: 20, pages: 0, loading: false } as NcListState<any>;

const initialState: NcState = {
  list: { ...initialList },
  capaList: { ...initialList },
  rcaList: { items: [], loading: false },
};

// Thunks - NonConformance
export const fetchNonConformances = createAsyncThunk(
  'nc/fetchNonConformances',
  async (params: any) => {
    const res = await ncAPI.getNonConformances(params);
    return res; // expects { items, total, page, size, pages }
  }
);

export const fetchNonConformance = createAsyncThunk(
  'nc/fetchNonConformance',
  async (ncId: number) => {
    const res = await ncAPI.getNonConformance(ncId);
    return res; // NC detail
  }
);

export const createFiveWhys = createAsyncThunk(
  'nc/createFiveWhys',
  async ({ ncId, payload }: { ncId: number; payload: any }) => {
    const res = await ncAPI.persistFiveWhys(ncId, payload);
    return res; // RCA record
  }
);

export const createIshikawa = createAsyncThunk(
  'nc/createIshikawa',
  async ({ ncId, payload }: { ncId: number; payload: any }) => {
    const res = await ncAPI.persistIshikawa(ncId, payload);
    return res; // RCA record
  }
);

// Thunks - CAPA
export const fetchCAPAList = createAsyncThunk(
  'nc/fetchCAPAList',
  async (params: any) => {
    const res = await ncAPI.getCAPAList(params);
    return res; // { items, total, page, size, pages }
  }
);

export const fetchCAPA = createAsyncThunk(
  'nc/fetchCAPA',
  async (capaId: number) => {
    const res = await ncAPI.getCAPA(capaId);
    return res; // CAPA detail
  }
);

export const updateCAPA = createAsyncThunk(
  'nc/updateCAPA',
  async ({ capaId, payload }: { capaId: number; payload: any }) => {
    const res = await ncAPI.updateCAPA(capaId, payload);
    return res; // updated CAPA detail
  }
);

export const updateNonConformance = createAsyncThunk(
  'nc/updateNonConformance',
  async ({ ncId, payload }: { ncId: number; payload: any }) => {
    const res = await ncAPI.updateNonConformance(ncId, payload);
    return res; // updated NC detail
  }
);

export const fetchRCAList = createAsyncThunk(
  'nc/fetchRCAList',
  async (ncId: number) => {
    const res = await ncAPI.getRCAList(ncId);
    return res as any[];
  }
);

const ncSlice = createSlice({
  name: 'nc',
  initialState,
  reducers: {
    resetNcDetail(state) {
      state.detail = undefined;
    },
    resetCapaDetail(state) {
      state.capaDetail = undefined;
    },
  },
  extraReducers: (builder) => {
    builder
      // NC list
      .addCase(fetchNonConformances.pending, (state) => {
        state.list.loading = true;
        state.list.error = undefined;
      })
      .addCase(fetchNonConformances.fulfilled, (state, action: PayloadAction<any>) => {
        state.list.loading = false;
        state.list.items = action.payload.items || [];
        state.list.total = action.payload.total || 0;
        state.list.page = action.payload.page || 1;
        state.list.size = action.payload.size || 20;
        state.list.pages = action.payload.pages || 0;
      })
      .addCase(fetchNonConformances.rejected, (state, action) => {
        state.list.loading = false;
        state.list.error = action.error.message;
      })
      // NC detail
      .addCase(fetchNonConformance.pending, (state) => {
        state.detail = undefined;
      })
      .addCase(fetchNonConformance.fulfilled, (state, action: PayloadAction<any>) => {
        state.detail = action.payload;
      })
      .addCase(fetchNonConformance.rejected, (state) => {
        state.detail = undefined;
      })
      // CAPA list
      .addCase(fetchCAPAList.pending, (state) => {
        state.capaList.loading = true;
        state.capaList.error = undefined;
      })
      .addCase(fetchCAPAList.fulfilled, (state, action: PayloadAction<any>) => {
        state.capaList.loading = false;
        state.capaList.items = action.payload.items || [];
        state.capaList.total = action.payload.total || 0;
        state.capaList.page = action.payload.page || 1;
        state.capaList.size = action.payload.size || 20;
        state.capaList.pages = action.payload.pages || 0;
      })
      .addCase(fetchCAPAList.rejected, (state, action) => {
        state.capaList.loading = false;
        state.capaList.error = action.error.message;
      })
      // CAPA detail
      .addCase(fetchCAPA.fulfilled, (state, action: PayloadAction<any>) => {
        state.capaDetail = action.payload;
      })
      .addCase(updateCAPA.fulfilled, (state, action: PayloadAction<any>) => {
        state.capaDetail = action.payload;
      })
      .addCase(updateNonConformance.fulfilled, (state, action: PayloadAction<any>) => {
        state.detail = action.payload;
      })
      // RCA list
      .addCase(fetchRCAList.pending, (state) => {
        state.rcaList.loading = true;
        state.rcaList.error = undefined;
      })
      .addCase(fetchRCAList.fulfilled, (state, action: PayloadAction<any[]>) => {
        state.rcaList.loading = false;
        state.rcaList.items = action.payload || [];
      })
      .addCase(fetchRCAList.rejected, (state, action) => {
        state.rcaList.loading = false;
        state.rcaList.error = action.error.message;
      });
  }
});

export const { resetNcDetail, resetCapaDetail } = ncSlice.actions;
export default ncSlice.reducer;

