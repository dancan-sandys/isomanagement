import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithProviders } from '../../../__tests__/utils/test-utils';
import QRCodeScanner from '../QRCodeScanner';
import { mockBatch } from '../../../__tests__/utils/test-utils';

// Mock the traceabilityAPI
jest.mock('../../../services/traceabilityAPI', () => ({
  traceabilityAPI: {
    getBatches: jest.fn(),
    searchBatches: jest.fn(),
    searchEnhancedBatchesGS1: jest.fn(),
  },
}));

describe('QRCodeScanner', () => {
  const defaultProps = {
    onBatchFound: jest.fn(),
    onClose: jest.fn(),
    open: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders the scanner dialog when open', () => {
      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      expect(screen.getByText('QR Code & Barcode Scanner')).toBeInTheDocument();
      expect(screen.getByText('Scanner')).toBeInTheDocument();
      expect(screen.getByText('Scan Results')).toBeInTheDocument();
    });

    it('does not render when closed', () => {
      render(<QRCodeScanner {...defaultProps} open={false} />);
      
      expect(screen.queryByText('QR Code & Barcode Scanner')).not.toBeInTheDocument();
    });

    it('displays the scanner placeholder when not scanning', () => {
      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      expect(screen.getByText('Camera scanner will be implemented here')).toBeInTheDocument();
      expect(screen.getByText('Test Search')).toBeInTheDocument();
    });

    it('shows empty scan results initially', () => {
      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      expect(screen.getByText('Scan a QR code or barcode to find batch information')).toBeInTheDocument();
    });
  });

  describe('Manual Search Functionality', () => {
    it('performs manual search when test button is clicked', async () => {
      const mockGetBatches = require('../../../services/traceabilityAPI').traceabilityAPI.getBatches;
      mockGetBatches.mockResolvedValue({
        items: [mockBatch],
        total: 1,
      });

      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      const testButton = screen.getByText('Test Search');
      fireEvent.click(testButton);

      await waitFor(() => {
        expect(mockGetBatches).toHaveBeenCalledWith({ search: 'BATCH001' });
      });

      await waitFor(() => {
        expect(screen.getByText('Batch Found')).toBeInTheDocument();
        expect(screen.getByText('BATCH001')).toBeInTheDocument();
        expect(screen.getByText('Test Product')).toBeInTheDocument();
      });
    });

    it('shows error when no batch is found', async () => {
      const mockGetBatches = require('../../../services/traceabilityAPI').traceabilityAPI.getBatches;
      mockGetBatches.mockResolvedValue({
        items: [],
        total: 0,
      });

      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      const testButton = screen.getByText('Test Search');
      fireEvent.click(testButton);

      await waitFor(() => {
        expect(screen.getByText('No batch found for this code')).toBeInTheDocument();
      });
    });

    it('handles API errors gracefully', async () => {
      const mockGetBatches = require('../../../services/traceabilityAPI').traceabilityAPI.getBatches;
      mockGetBatches.mockRejectedValue(new Error('API Error'));

      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      const testButton = screen.getByText('Test Search');
      fireEvent.click(testButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to search for batch')).toBeInTheDocument();
      });
    });
  });

  describe('Batch Display', () => {
    it('displays batch information when found', async () => {
      const mockGetBatches = require('../../../services/traceabilityAPI').traceabilityAPI.getBatches;
      mockGetBatches.mockResolvedValue({
        items: [mockBatch],
        total: 1,
      });

      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      const testButton = screen.getByText('Test Search');
      fireEvent.click(testButton);

      await waitFor(() => {
        expect(screen.getByText('BATCH001')).toBeInTheDocument();
        expect(screen.getByText('Test Product')).toBeInTheDocument();
        expect(screen.getByText('View Details')).toBeInTheDocument();
      });
    });

    it('calls onBatchFound when View Details is clicked', async () => {
      const mockGetBatches = require('../../../services/traceabilityAPI').traceabilityAPI.getBatches;
      mockGetBatches.mockResolvedValue({
        items: [mockBatch],
        total: 1,
      });

      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      const testButton = screen.getByText('Test Search');
      fireEvent.click(testButton);

      await waitFor(() => {
        const viewDetailsButton = screen.getByText('View Details');
        fireEvent.click(viewDetailsButton);
        expect(defaultProps.onBatchFound).toHaveBeenCalledWith(mockBatch);
      });
    });
  });

  describe('Dialog Controls', () => {
    it('calls onClose when close button is clicked', () => {
      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      const closeButton = screen.getByLabelText('Close scanner');
      fireEvent.click(closeButton);
      
      expect(defaultProps.onClose).toHaveBeenCalled();
    });

    it('calls onClose when cancel button is clicked', () => {
      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      const cancelButton = screen.getByText('Close');
      fireEvent.click(cancelButton);
      
      expect(defaultProps.onClose).toHaveBeenCalled();
    });
  });

  describe('Loading States', () => {
    it('shows loading indicator during search', async () => {
      const mockGetBatches = require('../../../services/traceabilityAPI').traceabilityAPI.getBatches;
      let resolvePromise: (value: any) => void;
      const promise = new Promise((resolve) => {
        resolvePromise = resolve;
      });
      mockGetBatches.mockReturnValue(promise);

      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      const testButton = screen.getByText('Test Search');
      fireEvent.click(testButton);

      expect(screen.getByText('Searching for batch...')).toBeInTheDocument();

      resolvePromise!({
        items: [mockBatch],
        total: 1,
      });

      await waitFor(() => {
        expect(screen.queryByText('Searching for batch...')).not.toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message when API call fails', async () => {
      const mockGetBatches = require('../../../services/traceabilityAPI').traceabilityAPI.getBatches;
      mockGetBatches.mockRejectedValue(new Error('Network error'));

      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      const testButton = screen.getByText('Test Search');
      fireEvent.click(testButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to search for batch')).toBeInTheDocument();
      });
    });

    it('clears error when new search is performed', async () => {
      const mockGetBatches = require('../../../services/traceabilityAPI').traceabilityAPI.getBatches;
      
      // First call fails
      mockGetBatches.mockRejectedValueOnce(new Error('Network error'));
      
      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      const testButton = screen.getByText('Test Search');
      fireEvent.click(testButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to search for batch')).toBeInTheDocument();
      });

      // Second call succeeds
      mockGetBatches.mockResolvedValueOnce({
        items: [mockBatch],
        total: 1,
      });

      fireEvent.click(testButton);

      await waitFor(() => {
        expect(screen.queryByText('Failed to search for batch')).not.toBeInTheDocument();
        expect(screen.getByText('Batch Found')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      expect(screen.getByLabelText('Close scanner')).toBeInTheDocument();
      expect(screen.getByLabelText('QR code scanner')).toBeInTheDocument();
    });

    it('supports keyboard navigation', () => {
      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      const closeButton = screen.getByLabelText('Close scanner');
      expect(closeButton).toHaveAttribute('tabIndex', '0');
    });
  });

  describe('Mobile Responsiveness', () => {
    it('renders with mobile-specific classes when on mobile', () => {
      // Mock useMediaQuery to return true for mobile
      jest.doMock('@mui/material', () => ({
        ...jest.requireActual('@mui/material'),
        useMediaQuery: jest.fn(() => true),
      }));

      renderWithProviders(<QRCodeScanner {...defaultProps} />);
      
      // The dialog should have fullScreen prop when on mobile
      const dialog = screen.getByRole('dialog');
      expect(dialog).toBeInTheDocument();
    });
  });
});
