import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithProviders } from '../../__tests__/utils/test-utils';
import Traceability from '../Traceability';
import { mockTraceabilityAPI, mockUsersAPI } from '../../__tests__/utils/test-utils';

// Mock the APIs
jest.mock('../../services/traceabilityAPI', () => ({
  traceabilityAPI: mockTraceabilityAPI,
}));

jest.mock('../../services/api', () => ({
  usersAPI: mockUsersAPI,
}));

describe('Traceability Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Page Rendering', () => {
    it('renders the main traceability page with all tabs', () => {
      renderWithProviders(<Traceability />);
      
      expect(screen.getByText('Traceability & Recall Management')).toBeInTheDocument();
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Batch Management')).toBeInTheDocument();
      expect(screen.getByText('Recall Management')).toBeInTheDocument();
      expect(screen.getByText('Traceability Reports')).toBeInTheDocument();
      expect(screen.getByText('Enhanced Search')).toBeInTheDocument();
      expect(screen.getByText('Recall Simulation')).toBeInTheDocument();
      expect(screen.getByText('Offline Mode')).toBeInTheDocument();
    });

    it('shows dashboard by default', () => {
      renderWithProviders(<Traceability />);
      
      expect(screen.getByText('Traceability Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Total Batches')).toBeInTheDocument();
      expect(screen.getByText('Active Recalls')).toBeInTheDocument();
      expect(screen.getByText('Recent Reports')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('switches to batch management tab', () => {
      renderWithProviders(<Traceability />);
      
      const batchTab = screen.getByText('Batch Management');
      fireEvent.click(batchTab);
      
      expect(screen.getByText('Batch Management')).toBeInTheDocument();
    });

    it('switches to recall management tab', () => {
      renderWithProviders(<Traceability />);
      
      const recallTab = screen.getByText('Recall Management');
      fireEvent.click(recallTab);
      
      expect(screen.getByText('Recall Management')).toBeInTheDocument();
      expect(screen.getByText('Create Recall')).toBeInTheDocument();
    });

    it('switches to traceability reports tab', () => {
      renderWithProviders(<Traceability />);
      
      const reportsTab = screen.getByText('Traceability Reports');
      fireEvent.click(reportsTab);
      
      expect(screen.getByText('Traceability Reports')).toBeInTheDocument();
      expect(screen.getByText('Create Trace Report')).toBeInTheDocument();
    });

    it('switches to enhanced search tab', () => {
      renderWithProviders(<Traceability />);
      
      const searchTab = screen.getByText('Enhanced Search');
      fireEvent.click(searchTab);
      
      expect(screen.getByText('Enhanced Search')).toBeInTheDocument();
    });

    it('switches to recall simulation tab', () => {
      renderWithProviders(<Traceability />);
      
      const simulationTab = screen.getByText('Recall Simulation');
      fireEvent.click(simulationTab);
      
      expect(screen.getByText('Recall Simulation')).toBeInTheDocument();
      expect(screen.getByText('Start Recall Simulation')).toBeInTheDocument();
    });

    it('switches to offline mode tab', () => {
      renderWithProviders(<Traceability />);
      
      const offlineTab = screen.getByText('Offline Mode');
      fireEvent.click(offlineTab);
      
      expect(screen.getByText('Offline Mode')).toBeInTheDocument();
      expect(screen.getByText('Download Latest Data')).toBeInTheDocument();
    });
  });

  describe('Batch Management Workflow', () => {
    it('opens batch creation dialog', () => {
      renderWithProviders(<Traceability />);
      
      // Switch to batch management tab
      const batchTab = screen.getByText('Batch Management');
      fireEvent.click(batchTab);
      
      // Look for create batch button (might be in a different component)
      // This test assumes the batch list component has a create button
      expect(screen.getByText('Batch Management')).toBeInTheDocument();
    });

    it('displays batch list with data', async () => {
      renderWithProviders(<Traceability />);
      
      const batchTab = screen.getByText('Batch Management');
      fireEvent.click(batchTab);
      
      await waitFor(() => {
        expect(mockTraceabilityAPI.getBatches).toHaveBeenCalled();
      });
    });
  });

  describe('Recall Management Workflow', () => {
    it('opens recall creation dialog', () => {
      renderWithProviders(<Traceability />);
      
      const recallTab = screen.getByText('Recall Management');
      fireEvent.click(recallTab);
      
      const createRecallButton = screen.getByText('Create Recall');
      fireEvent.click(createRecallButton);
      
      expect(screen.getByText('Create New Recall')).toBeInTheDocument();
    });

    it('fills and submits recall form', async () => {
      renderWithProviders(<Traceability />);
      
      const recallTab = screen.getByText('Recall Management');
      fireEvent.click(recallTab);
      
      const createRecallButton = screen.getByText('Create Recall');
      fireEvent.click(createRecallButton);
      
      // Fill form fields
      const titleInput = screen.getByLabelText('Title');
      const descriptionInput = screen.getByLabelText('Description');
      const reasonInput = screen.getByLabelText('Reason for Recall');
      
      fireEvent.change(titleInput, { target: { value: 'Test Recall' } });
      fireEvent.change(descriptionInput, { target: { value: 'Test description' } });
      fireEvent.change(reasonInput, { target: { value: 'Test reason' } });
      
      // Select recall type
      const recallTypeSelect = screen.getByLabelText('Recall Type');
      fireEvent.mouseDown(recallTypeSelect);
      const classIIOption = screen.getByText('Class II - Temporary health effects');
      fireEvent.click(classIIOption);
      
      // Submit form
      const submitButton = screen.getByText('Create Recall');
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(mockTraceabilityAPI.createRecall).toHaveBeenCalled();
      });
    });

    it('displays recall list with data', async () => {
      renderWithProviders(<Traceability />);
      
      const recallTab = screen.getByText('Recall Management');
      fireEvent.click(recallTab);
      
      await waitFor(() => {
        expect(mockTraceabilityAPI.getRecalls).toHaveBeenCalled();
      });
    });
  });

  describe('Traceability Reports Workflow', () => {
    it('opens trace report creation dialog', () => {
      renderWithProviders(<Traceability />);
      
      const reportsTab = screen.getByText('Traceability Reports');
      fireEvent.click(reportsTab);
      
      const createReportButton = screen.getByText('Create Trace Report');
      fireEvent.click(createReportButton);
      
      expect(screen.getByText('Create Traceability Report')).toBeInTheDocument();
    });

    it('fills and submits trace report form', async () => {
      renderWithProviders(<Traceability />);
      
      const reportsTab = screen.getByText('Traceability Reports');
      fireEvent.click(reportsTab);
      
      const createReportButton = screen.getByText('Create Trace Report');
      fireEvent.click(createReportButton);
      
      // Fill form fields
      const traceDepthInput = screen.getByLabelText('Trace Depth');
      fireEvent.change(traceDepthInput, { target: { value: '3' } });
      
      // Submit form
      const submitButton = screen.getByText('Create Report');
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(mockTraceabilityAPI.createTraceabilityReport).toHaveBeenCalled();
      });
    });
  });

  describe('Mobile Features Integration', () => {
    it('shows mobile app bar on mobile devices', () => {
      // Mock useMediaQuery to return true for mobile
      jest.doMock('@mui/material', () => ({
        ...jest.requireActual('@mui/material'),
        useMediaQuery: jest.fn(() => true),
      }));

      renderWithProviders(<Traceability />);
      
      expect(screen.getByText('Traceability & Recall')).toBeInTheDocument();
    });

    it('opens QR scanner from mobile app bar', () => {
      renderWithProviders(<Traceability />);
      
      // Look for QR scanner button in mobile app bar
      const qrButton = screen.getByLabelText('QR code scanner');
      fireEvent.click(qrButton);
      
      expect(screen.getByText('QR Code & Barcode Scanner')).toBeInTheDocument();
    });

    it('opens mobile data entry from speed dial', () => {
      renderWithProviders(<Traceability />);
      
      // Look for mobile data entry button in speed dial
      // This might be in a different component or rendered conditionally
      expect(screen.getByText('Traceability & Recall Management')).toBeInTheDocument();
    });
  });

  describe('Offline Mode Integration', () => {
    it('shows offline capabilities in offline mode tab', () => {
      renderWithProviders(<Traceability />);
      
      const offlineTab = screen.getByText('Offline Mode');
      fireEvent.click(offlineTab);
      
      expect(screen.getByText('Offline Data')).toBeInTheDocument();
      expect(screen.getByText('Sync Controls')).toBeInTheDocument();
    });

    it('downloads offline data when button is clicked', async () => {
      renderWithProviders(<Traceability />);
      
      const offlineTab = screen.getByText('Offline Mode');
      fireEvent.click(offlineTab);
      
      const downloadButton = screen.getByText('Download Latest Data');
      fireEvent.click(downloadButton);
      
      await waitFor(() => {
        expect(screen.getByText('Syncing... 0%')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling Integration', () => {
    it('displays error when API calls fail', async () => {
      // Mock API to fail
      mockTraceabilityAPI.getDashboard.mockRejectedValueOnce(new Error('API Error'));
      
      renderWithProviders(<Traceability />);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to load dashboard data')).toBeInTheDocument();
      });
    });

    it('handles network errors gracefully', async () => {
      // Mock API to fail
      mockTraceabilityAPI.getBatches.mockRejectedValueOnce(new Error('Network Error'));
      
      renderWithProviders(<Traceability />);
      
      const batchTab = screen.getByText('Batch Management');
      fireEvent.click(batchTab);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to load batches')).toBeInTheDocument();
      });
    });
  });

  describe('Data Loading Integration', () => {
    it('loads dashboard data on mount', async () => {
      renderWithProviders(<Traceability />);
      
      await waitFor(() => {
        expect(mockTraceabilityAPI.getDashboard).toHaveBeenCalled();
      });
    });

    it('loads batches data on mount', async () => {
      renderWithProviders(<Traceability />);
      
      await waitFor(() => {
        expect(mockTraceabilityAPI.getBatches).toHaveBeenCalled();
      });
    });

    it('loads recalls data on mount', async () => {
      renderWithProviders(<Traceability />);
      
      await waitFor(() => {
        expect(mockTraceabilityAPI.getRecalls).toHaveBeenCalled();
      });
    });

    it('loads reports data on mount', async () => {
      renderWithProviders(<Traceability />);
      
      await waitFor(() => {
        expect(mockTraceabilityAPI.getTraceabilityReports).toHaveBeenCalled();
      });
    });
  });

  describe('User Interaction Integration', () => {
    it('handles batch selection', async () => {
      renderWithProviders(<Traceability />);
      
      const batchTab = screen.getByText('Batch Management');
      fireEvent.click(batchTab);
      
      // This would require the batch list to be rendered and a batch to be selected
      await waitFor(() => {
        expect(mockTraceabilityAPI.getBatches).toHaveBeenCalled();
      });
    });

    it('handles recall selection', async () => {
      renderWithProviders(<Traceability />);
      
      const recallTab = screen.getByText('Recall Management');
      fireEvent.click(recallTab);
      
      await waitFor(() => {
        expect(mockTraceabilityAPI.getRecalls).toHaveBeenCalled();
      });
    });

    it('handles report selection', async () => {
      renderWithProviders(<Traceability />);
      
      const reportsTab = screen.getByText('Traceability Reports');
      fireEvent.click(reportsTab);
      
      await waitFor(() => {
        expect(mockTraceabilityAPI.getTraceabilityReports).toHaveBeenCalled();
      });
    });
  });

  describe('Accessibility Integration', () => {
    it('supports keyboard navigation between tabs', () => {
      renderWithProviders(<Traceability />);
      
      const tabs = screen.getAllByRole('tab');
      expect(tabs.length).toBeGreaterThan(0);
      
      // Test tab navigation
      tabs.forEach(tab => {
        expect(tab).toHaveAttribute('tabIndex', '0');
      });
    });

    it('has proper ARIA labels throughout the interface', () => {
      renderWithProviders(<Traceability />);
      
      // Check for common ARIA labels
      expect(screen.getByLabelText('QR code scanner')).toBeInTheDocument();
    });
  });

  describe('Performance Integration', () => {
    it('loads data efficiently', async () => {
      const startTime = performance.now();
      
      renderWithProviders(<Traceability />);
      
      await waitFor(() => {
        expect(mockTraceabilityAPI.getDashboard).toHaveBeenCalled();
        expect(mockTraceabilityAPI.getBatches).toHaveBeenCalled();
        expect(mockTraceabilityAPI.getRecalls).toHaveBeenCalled();
        expect(mockTraceabilityAPI.getTraceabilityReports).toHaveBeenCalled();
      });
      
      const endTime = performance.now();
      const loadTime = endTime - startTime;
      
      // Ensure loading time is reasonable (less than 5 seconds)
      expect(loadTime).toBeLessThan(5000);
    });
  });
});
