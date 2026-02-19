import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { traceabilityAPI } from '../../services/traceabilityAPI';
import { 
  Batch, 
  Recall, 
  TraceabilityReport, 
  TraceabilityDashboard,
  SearchFilters,
  SearchResult,
  TraceAnalysis,
  RecallSimulation
} from '../../types/traceability';

// Async thunks
export const fetchBatches = createAsyncThunk(
  'traceability/fetchBatches',
  async (params?: SearchFilters) => {
    const response = await traceabilityAPI.getBatches(params);
    return response;
  }
);

export const createBatch = createAsyncThunk(
  'traceability/createBatch',
  async (batchData: any) => {
    const response = await traceabilityAPI.createBatch(batchData);
    return response;
  }
);

export const updateBatch = createAsyncThunk(
  'traceability/updateBatch',
  async ({ batchId, batchData }: { batchId: number; batchData: any }) => {
    const response = await traceabilityAPI.updateBatch(batchId, batchData);
    return response;
  }
);

export const deleteBatch = createAsyncThunk(
  'traceability/deleteBatch',
  async (batchId: number) => {
    await traceabilityAPI.deleteBatch(batchId);
    return batchId;
  }
);

export const fetchRecalls = createAsyncThunk(
  'traceability/fetchRecalls',
  async (params?: any) => {
    const response = await traceabilityAPI.getRecalls(params);
    return response;
  }
);

export const createRecall = createAsyncThunk(
  'traceability/createRecall',
  async (recallData: any) => {
    const response = await traceabilityAPI.createRecall(recallData);
    return response;
  }
);

export const fetchTraceabilityReports = createAsyncThunk(
  'traceability/fetchTraceabilityReports',
  async (params?: any) => {
    const response = await traceabilityAPI.getTraceabilityReports(params);
    return response;
  }
);

export const createTraceabilityReport = createAsyncThunk(
  'traceability/createTraceabilityReport',
  async (reportData: any) => {
    const response = await traceabilityAPI.createTraceabilityReport(reportData);
    return response;
  }
);

export const fetchDashboard = createAsyncThunk(
  'traceability/fetchDashboard',
  async () => {
    const response = await traceabilityAPI.getDashboard();
    return response;
  }
);

export const searchBatches = createAsyncThunk(
  'traceability/searchBatches',
  async (searchParams: SearchFilters) => {
    const response = await traceabilityAPI.searchBatches(searchParams);
    return response;
  }
);

export const getTraceAnalysis = createAsyncThunk(
  'traceability/getTraceAnalysis',
  async ({ batchId, traceType, depth }: { batchId: number; traceType: 'backward' | 'forward' | 'full'; depth: number }) => {
    let response;
    switch (traceType) {
      case 'backward':
        response = await traceabilityAPI.getBackwardTrace(batchId, depth);
        break;
      case 'forward':
        response = await traceabilityAPI.getForwardTrace(batchId, depth);
        break;
      case 'full':
        response = await traceabilityAPI.getFullTrace(batchId, depth);
        break;
      default:
        throw new Error('Invalid trace type');
    }
    return response;
  }
);

export const simulateRecall = createAsyncThunk(
  'traceability/simulateRecall',
  async (simulationData: any) => {
    const response = await traceabilityAPI.simulateRecall(simulationData);
    return response;
  }
);

// State interface
interface TraceabilityState {
  // Batches
  batches: Batch[];
  batchesLoading: boolean;
  batchesError: string | null;
  selectedBatch: Batch | null;
  
  // Recalls
  recalls: Recall[];
  recallsLoading: boolean;
  recallsError: string | null;
  selectedRecall: Recall | null;
  
  // Reports
  reports: TraceabilityReport[];
  reportsLoading: boolean;
  reportsError: string | null;
  
  // Dashboard
  dashboard: TraceabilityDashboard | null;
  dashboardLoading: boolean;
  dashboardError: string | null;
  
  // Search
  searchResults: SearchResult<Batch> | null;
  searchLoading: boolean;
  searchError: string | null;
  
  // Trace Analysis
  traceAnalysis: TraceAnalysis | null;
  traceAnalysisLoading: boolean;
  traceAnalysisError: string | null;
  
  // Recall Simulation
  recallSimulation: RecallSimulation | null;
  simulationLoading: boolean;
  simulationError: string | null;
  
  // UI State
  activeTab: number;
  filters: SearchFilters;
  selectedBatches: number[];
  selectedRecalls: number[];
}

// Initial state
const initialState: TraceabilityState = {
  // Batches
  batches: [],
  batchesLoading: false,
  batchesError: null,
  selectedBatch: null,
  
  // Recalls
  recalls: [],
  recallsLoading: false,
  recallsError: null,
  selectedRecall: null,
  
  // Reports
  reports: [],
  reportsLoading: false,
  reportsError: null,
  
  // Dashboard
  dashboard: null,
  dashboardLoading: false,
  dashboardError: null,
  
  // Search
  searchResults: null,
  searchLoading: false,
  searchError: null,
  
  // Trace Analysis
  traceAnalysis: null,
  traceAnalysisLoading: false,
  traceAnalysisError: null,
  
  // Recall Simulation
  recallSimulation: null,
  simulationLoading: false,
  simulationError: null,
  
  // UI State
  activeTab: 0,
  filters: {
    query: '',
    batch_type: '',
    status: '',
    quality_status: '',
    date_from: '',
    date_to: '',
    product_name: '',
    supplier_id: undefined,
    page: 1,
    size: 20
  },
  selectedBatches: [],
  selectedRecalls: []
};

// Slice
const traceabilitySlice = createSlice({
  name: 'traceability',
  initialState,
  reducers: {
    // UI Actions
    setActiveTab: (state, action: PayloadAction<number>) => {
      state.activeTab = action.payload;
    },
    
    setSelectedBatch: (state, action: PayloadAction<Batch | null>) => {
      state.selectedBatch = action.payload;
    },
    
    setSelectedRecall: (state, action: PayloadAction<Recall | null>) => {
      state.selectedRecall = action.payload;
    },
    
    setFilters: (state, action: PayloadAction<Partial<SearchFilters>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    
    clearFilters: (state) => {
      state.filters = initialState.filters;
    },
    
    setSelectedBatches: (state, action: PayloadAction<number[]>) => {
      state.selectedBatches = action.payload;
    },
    
    setSelectedRecalls: (state, action: PayloadAction<number[]>) => {
      state.selectedRecalls = action.payload;
    },
    
    toggleBatchSelection: (state, action: PayloadAction<number>) => {
      const batchId = action.payload;
      const index = state.selectedBatches.indexOf(batchId);
      if (index > -1) {
        state.selectedBatches.splice(index, 1);
      } else {
        state.selectedBatches.push(batchId);
      }
    },
    
    toggleRecallSelection: (state, action: PayloadAction<number>) => {
      const recallId = action.payload;
      const index = state.selectedRecalls.indexOf(recallId);
      if (index > -1) {
        state.selectedRecalls.splice(index, 1);
      } else {
        state.selectedRecalls.push(recallId);
      }
    },
    
    clearSearchResults: (state) => {
      state.searchResults = null;
      state.searchError = null;
    },
    
    clearTraceAnalysis: (state) => {
      state.traceAnalysis = null;
      state.traceAnalysisError = null;
    },
    
    clearSimulation: (state) => {
      state.recallSimulation = null;
      state.simulationError = null;
    }
  },
  extraReducers: (builder) => {
    // Fetch batches
    builder
      .addCase(fetchBatches.pending, (state) => {
        state.batchesLoading = true;
        state.batchesError = null;
      })
      .addCase(fetchBatches.fulfilled, (state, action) => {
        state.batchesLoading = false;
        state.batches = action.payload.items || [];
      })
      .addCase(fetchBatches.rejected, (state, action) => {
        state.batchesLoading = false;
        state.batchesError = action.error.message || 'Failed to fetch batches';
      });
    
    // Create batch
    builder
      .addCase(createBatch.fulfilled, (state, action) => {
        state.batches.unshift(action.payload);
      });
    
    // Update batch
    builder
      .addCase(updateBatch.fulfilled, (state, action) => {
        const index = state.batches.findIndex(batch => batch.id === action.payload.id);
        if (index !== -1) {
          state.batches[index] = action.payload;
        }
      });
    
    // Delete batch
    builder
      .addCase(deleteBatch.fulfilled, (state, action) => {
        state.batches = state.batches.filter(batch => batch.id !== action.payload);
      });
    
    // Fetch recalls
    builder
      .addCase(fetchRecalls.pending, (state) => {
        state.recallsLoading = true;
        state.recallsError = null;
      })
      .addCase(fetchRecalls.fulfilled, (state, action) => {
        state.recallsLoading = false;
        state.recalls = action.payload.items || [];
      })
      .addCase(fetchRecalls.rejected, (state, action) => {
        state.recallsLoading = false;
        state.recallsError = action.error.message || 'Failed to fetch recalls';
      });
    
    // Create recall
    builder
      .addCase(createRecall.fulfilled, (state, action) => {
        state.recalls.unshift(action.payload);
      });
    
    // Fetch reports
    builder
      .addCase(fetchTraceabilityReports.pending, (state) => {
        state.reportsLoading = true;
        state.reportsError = null;
      })
      .addCase(fetchTraceabilityReports.fulfilled, (state, action) => {
        state.reportsLoading = false;
        state.reports = action.payload.items || [];
      })
      .addCase(fetchTraceabilityReports.rejected, (state, action) => {
        state.reportsLoading = false;
        state.reportsError = action.error.message || 'Failed to fetch reports';
      });
    
    // Create report
    builder
      .addCase(createTraceabilityReport.fulfilled, (state, action) => {
        state.reports.unshift(action.payload);
      });
    
    // Fetch dashboard
    builder
      .addCase(fetchDashboard.pending, (state) => {
        state.dashboardLoading = true;
        state.dashboardError = null;
      })
      .addCase(fetchDashboard.fulfilled, (state, action) => {
        state.dashboardLoading = false;
        state.dashboard = action.payload;
      })
      .addCase(fetchDashboard.rejected, (state, action) => {
        state.dashboardLoading = false;
        state.dashboardError = action.error.message || 'Failed to fetch dashboard';
      });
    
    // Search batches
    builder
      .addCase(searchBatches.pending, (state) => {
        state.searchLoading = true;
        state.searchError = null;
      })
      .addCase(searchBatches.fulfilled, (state, action) => {
        state.searchLoading = false;
        state.searchResults = action.payload;
      })
      .addCase(searchBatches.rejected, (state, action) => {
        state.searchLoading = false;
        state.searchError = action.error.message || 'Search failed';
      });
    
    // Trace analysis
    builder
      .addCase(getTraceAnalysis.pending, (state) => {
        state.traceAnalysisLoading = true;
        state.traceAnalysisError = null;
      })
      .addCase(getTraceAnalysis.fulfilled, (state, action) => {
        state.traceAnalysisLoading = false;
        state.traceAnalysis = action.payload;
      })
      .addCase(getTraceAnalysis.rejected, (state, action) => {
        state.traceAnalysisLoading = false;
        state.traceAnalysisError = action.error.message || 'Trace analysis failed';
      });
    
    // Recall simulation
    builder
      .addCase(simulateRecall.pending, (state) => {
        state.simulationLoading = true;
        state.simulationError = null;
      })
      .addCase(simulateRecall.fulfilled, (state, action) => {
        state.simulationLoading = false;
        state.recallSimulation = action.payload;
      })
      .addCase(simulateRecall.rejected, (state, action) => {
        state.simulationLoading = false;
        state.simulationError = action.error.message || 'Simulation failed';
      });
  }
});

// Export actions
export const {
  setActiveTab,
  setSelectedBatch,
  setSelectedRecall,
  setFilters,
  clearFilters,
  setSelectedBatches,
  setSelectedRecalls,
  toggleBatchSelection,
  toggleRecallSelection,
  clearSearchResults,
  clearTraceAnalysis,
  clearSimulation
} = traceabilitySlice.actions;

// Export reducer
export default traceabilitySlice.reducer;

// Export selectors
export const selectBatches = (state: { traceability: TraceabilityState }) => state.traceability.batches;
export const selectBatchesLoading = (state: { traceability: TraceabilityState }) => state.traceability.batchesLoading;
export const selectBatchesError = (state: { traceability: TraceabilityState }) => state.traceability.batchesError;
export const selectSelectedBatch = (state: { traceability: TraceabilityState }) => state.traceability.selectedBatch;

export const selectRecalls = (state: { traceability: TraceabilityState }) => state.traceability.recalls;
export const selectRecallsLoading = (state: { traceability: TraceabilityState }) => state.traceability.recallsLoading;
export const selectRecallsError = (state: { traceability: TraceabilityState }) => state.traceability.recallsError;
export const selectSelectedRecall = (state: { traceability: TraceabilityState }) => state.traceability.selectedRecall;

export const selectReports = (state: { traceability: TraceabilityState }) => state.traceability.reports;
export const selectReportsLoading = (state: { traceability: TraceabilityState }) => state.traceability.reportsLoading;
export const selectReportsError = (state: { traceability: TraceabilityState }) => state.traceability.reportsError;

export const selectDashboard = (state: { traceability: TraceabilityState }) => state.traceability.dashboard;
export const selectDashboardLoading = (state: { traceability: TraceabilityState }) => state.traceability.dashboardLoading;
export const selectDashboardError = (state: { traceability: TraceabilityState }) => state.traceability.dashboardError;

export const selectSearchResults = (state: { traceability: TraceabilityState }) => state.traceability.searchResults;
export const selectSearchLoading = (state: { traceability: TraceabilityState }) => state.traceability.searchLoading;
export const selectSearchError = (state: { traceability: TraceabilityState }) => state.traceability.searchError;

export const selectTraceAnalysis = (state: { traceability: TraceabilityState }) => state.traceability.traceAnalysis;
export const selectTraceAnalysisLoading = (state: { traceability: TraceabilityState }) => state.traceability.traceAnalysisLoading;
export const selectTraceAnalysisError = (state: { traceability: TraceabilityState }) => state.traceability.traceAnalysisError;

export const selectRecallSimulation = (state: { traceability: TraceabilityState }) => state.traceability.recallSimulation;
export const selectSimulationLoading = (state: { traceability: TraceabilityState }) => state.traceability.simulationLoading;
export const selectSimulationError = (state: { traceability: TraceabilityState }) => state.traceability.simulationError;

export const selectActiveTab = (state: { traceability: TraceabilityState }) => state.traceability.activeTab;
export const selectFilters = (state: { traceability: TraceabilityState }) => state.traceability.filters;
export const selectSelectedBatches = (state: { traceability: TraceabilityState }) => state.traceability.selectedBatches;
export const selectSelectedRecalls = (state: { traceability: TraceabilityState }) => state.traceability.selectedRecalls; 