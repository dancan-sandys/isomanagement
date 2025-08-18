import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import { createISOTheme } from '../theme/designSystem';

// Import your reducers
import authReducer from '../store/slices/authSlice';

// Create a test store
const createTestStore = () => {
  return configureStore({
    reducer: {
      auth: authReducer,
    },
    preloadedState: {
      auth: {
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          full_name: 'Test User',
          role_id: 1,
          role_name: 'admin',
          status: 'active',
          is_active: true,
          is_verified: true,
        },
        token: 'test-token',
        refreshToken: 'test-refresh-token',
        isAuthenticated: true,
        isLoading: false,
        error: null,
      },
    },
  });
};

// Custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const store = createTestStore();
  const theme = createISOTheme('light');

  return (
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {children}
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Mock data for tests
export const mockBatch = {
  id: 1,
  batch_number: 'BATCH001',
  product_name: 'Test Product',
  batch_type: 'final_product',
  status: 'completed',
  quantity: 100,
  unit: 'units',
  production_date: '2024-01-01T00:00:00Z',
  expiry_date: '2024-12-31T00:00:00Z',
  lot_number: 'LOT001',
  quality_status: 'approved',
  storage_location: 'Warehouse A',
  barcode: '123456789',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

export const mockRecall = {
  id: 1,
  recall_number: 'RECALL001',
  recall_type: 'class_ii',
  status: 'initiated',
  title: 'Test Recall',
  description: 'Test recall description',
  reason: 'Quality issue',
  hazard_description: 'Potential contamination',
  affected_products: '["Product A", "Product B"]',
  affected_batches: '["BATCH001", "BATCH002"]',
  total_quantity_affected: 500,
  quantity_in_distribution: 200,
  quantity_recalled: 150,
  issue_discovered_date: '2024-01-01T00:00:00Z',
  recall_initiated_date: '2024-01-02T00:00:00Z',
  regulatory_notification_required: true,
  regulatory_notification_sent: false,
  assigned_to: 1,
  assigned_to_name: 'Test User',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

export const mockTraceabilityReport = {
  id: 1,
  report_number: 'REPORT001',
  report_type: 'full_trace',
  starting_batch_id: 1,
  trace_date: '2024-01-01T00:00:00Z',
  trace_depth: 5,
  trace_summary: 'Complete traceability analysis completed',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

export const mockDashboardData = {
  batch_counts: {
    completed: 50,
    in_production: 20,
    quarantined: 5,
    released: 30,
  },
  status_counts: {
    active: 75,
    inactive: 25,
  },
  recent_batches: 10,
  active_recalls: 2,
  recent_reports: 5,
  quality_breakdown: {
    approved: 80,
    pending: 15,
    rejected: 5,
  },
};

// Mock API responses
export const mockApiResponses = {
  batches: {
    items: [mockBatch],
    total: 1,
    page: 1,
    size: 10,
  },
  recalls: {
    items: [mockRecall],
    total: 1,
    page: 1,
    size: 10,
  },
  reports: {
    items: [mockTraceabilityReport],
    total: 1,
    page: 1,
    size: 10,
  },
  dashboard: mockDashboardData,
};

// Mock traceabilityAPI
export const mockTraceabilityAPI = {
  getBatches: jest.fn().mockResolvedValue(mockApiResponses.batches),
  getRecalls: jest.fn().mockResolvedValue(mockApiResponses.recalls),
  getTraceabilityReports: jest.fn().mockResolvedValue(mockApiResponses.reports),
  getDashboard: jest.fn().mockResolvedValue(mockApiResponses.dashboard),
  createBatch: jest.fn().mockResolvedValue({ data: mockBatch }),
  createRecall: jest.fn().mockResolvedValue({ data: mockRecall }),
  createTraceabilityReport: jest.fn().mockResolvedValue({ data: mockTraceabilityReport }),
  getOneUpOneBackTrace: jest.fn().mockResolvedValue({
    data: {
      upstream_trace: [],
      downstream_trace: [],
    },
  }),
  getTraceCompleteness: jest.fn().mockResolvedValue({
    data: {
      completeness_score: 85,
      missing_links: 3,
      total_links: 20,
    },
  }),
  getTraceVerificationStatus: jest.fn().mockResolvedValue({
    data: {
      verification_status: 'pending',
      verification_date: null,
      verified_by: null,
    },
  }),
  getCCPTraceabilityAlerts: jest.fn().mockResolvedValue({
    data: {
      items: [],
      total: 0,
    },
  }),
};

// Mock usersAPI
export const mockUsersAPI = {
  getUsers: jest.fn().mockResolvedValue({
    items: [
      {
        id: 1,
        username: 'testuser',
        full_name: 'Test User',
        email: 'test@example.com',
        role: 'admin',
        is_active: true,
      },
    ],
    total: 1,
    page: 1,
    size: 10,
  }),
};

// Helper function to wait for async operations
export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Helper function to mock localStorage
export const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Helper function to mock sessionStorage
export const mockSessionStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Helper function to mock geolocation
export const mockGeolocation = {
  getCurrentPosition: jest.fn().mockImplementation((success) =>
    success({
      coords: {
        latitude: 40.7128,
        longitude: -74.0060,
        accuracy: 10,
      },
    })
  ),
  watchPosition: jest.fn(),
  clearWatch: jest.fn(),
};

// Helper function to mock navigator.share
export const mockNavigatorShare = jest.fn().mockResolvedValue(undefined);

// Re-export everything from testing library
export * from '@testing-library/react';
export { customRender as render };
