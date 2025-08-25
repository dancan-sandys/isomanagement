import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import QRCodeScanner from '../QRCodeScanner';
import { traceabilityAPI } from '../../../services/traceabilityAPI';

// Mock the html5-qrcode library
jest.mock('html5-qrcode', () => ({
  Html5QrcodeScanner: jest.fn().mockImplementation(() => ({
    render: jest.fn(),
    clear: jest.fn().mockResolvedValue(undefined),
  })),
  Html5QrcodeScannerConfig: {},
  Html5QrcodeSupportedFormats: {
    QR_CODE: 'QR_CODE',
    CODE_128: 'CODE_128',
    CODE_39: 'CODE_39',
  },
}));

// Mock the traceability API
jest.mock('../../../services/traceabilityAPI', () => ({
  traceabilityAPI: {
    getBatches: jest.fn(),
  },
}));

// Create a mock store
const mockStore = configureStore({
  reducer: {
    traceability: (state = {}) => state,
  },
});

const renderWithProvider = (ui: React.ReactElement) => {
  return render(
    <Provider store={mockStore}>
      {ui}
    </Provider>
  );
};

describe('Enhanced QRCodeScanner', () => {
  const mockOnBatchFound = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the scanner dialog when open', () => {
    renderWithProvider(
      <QRCodeScanner
        open={true}
        onBatchFound={mockOnBatchFound}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('QR Code & Barcode Scanner')).toBeInTheDocument();
    expect(screen.getByText('Start Camera Scanner')).toBeInTheDocument();
    expect(screen.getByLabelText('Manual Code Entry')).toBeInTheDocument();
  });

  it('shows the scanner interface with camera and manual entry options', () => {
    renderWithProvider(
      <QRCodeScanner
        open={true}
        onBatchFound={mockOnBatchFound}
        onClose={mockOnClose}
      />
    );

    // Check for camera scanner button
    const cameraButton = screen.getByText('Start Camera Scanner');
    expect(cameraButton).toBeInTheDocument();

    // Check for manual input field
    const manualInput = screen.getByLabelText('Manual Code Entry');
    expect(manualInput).toBeInTheDocument();

    // Check for supported formats text
    expect(screen.getByText(/Supports QR codes, Code 128, and Code 39 barcodes/)).toBeInTheDocument();
  });

  it('handles manual code entry and search', async () => {
    const mockBatch = {
      id: 1,
      batch_number: 'BATCH-001',
      product_name: 'Test Product',
    };

    (traceabilityAPI.getBatches as jest.Mock).mockResolvedValueOnce({
      items: [mockBatch],
    });

    renderWithProvider(
      <QRCodeScanner
        open={true}
        onBatchFound={mockOnBatchFound}
        onClose={mockOnClose}
      />
    );

    const manualInput = screen.getByLabelText('Manual Code Entry');
    const searchButton = screen.getByRole('button', { name: /search/i });

    // Enter a code manually
    fireEvent.change(manualInput, { target: { value: 'BATCH-001' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(traceabilityAPI.getBatches).toHaveBeenCalledWith({ search: 'BATCH-001' });
      expect(mockOnBatchFound).toHaveBeenCalledWith(mockBatch);
    });
  });

  it('handles manual code entry with Enter key', async () => {
    const mockBatch = {
      id: 1,
      batch_number: 'BATCH-001',
      product_name: 'Test Product',
    };

    (traceabilityAPI.getBatches as jest.Mock).mockResolvedValueOnce({
      items: [mockBatch],
    });

    renderWithProvider(
      <QRCodeScanner
        open={true}
        onBatchFound={mockOnBatchFound}
        onClose={mockOnClose}
      />
    );

    const manualInput = screen.getByLabelText('Manual Code Entry');

    // Enter a code manually and press Enter
    fireEvent.change(manualInput, { target: { value: 'BATCH-001' } });
    fireEvent.keyPress(manualInput, { key: 'Enter', code: 'Enter', charCode: 13 });

    await waitFor(() => {
      expect(traceabilityAPI.getBatches).toHaveBeenCalledWith({ search: 'BATCH-001' });
      expect(mockOnBatchFound).toHaveBeenCalledWith(mockBatch);
    });
  });

  it('displays error when no batch is found', async () => {
    (traceabilityAPI.getBatches as jest.Mock).mockResolvedValueOnce({
      items: [],
    });

    renderWithProvider(
      <QRCodeScanner
        open={true}
        onBatchFound={mockOnBatchFound}
        onClose={mockOnClose}
      />
    );

    const manualInput = screen.getByLabelText('Manual Code Entry');
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(manualInput, { target: { value: 'INVALID-CODE' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText('No batch found for this code')).toBeInTheDocument();
    });
  });

  it('displays batch information when found', async () => {
    const mockBatch = {
      id: 1,
      batch_number: 'BATCH-001',
      product_name: 'Test Cheese',
    };

    (traceabilityAPI.getBatches as jest.Mock).mockResolvedValueOnce({
      items: [mockBatch],
    });

    renderWithProvider(
      <QRCodeScanner
        open={true}
        onBatchFound={mockOnBatchFound}
        onClose={mockOnClose}
      />
    );

    const manualInput = screen.getByLabelText('Manual Code Entry');
    fireEvent.change(manualInput, { target: { value: 'BATCH-001' } });
    fireEvent.keyPress(manualInput, { key: 'Enter', code: 'Enter', charCode: 13 });

    await waitFor(() => {
      expect(screen.getByText('BATCH-001')).toBeInTheDocument();
      expect(screen.getByText('Test Cheese')).toBeInTheDocument();
      expect(screen.getByText('View Details')).toBeInTheDocument();
    });
  });

  it('shows loading state during search', async () => {
    (traceabilityAPI.getBatches as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    renderWithProvider(
      <QRCodeScanner
        open={true}
        onBatchFound={mockOnBatchFound}
        onClose={mockOnClose}
      />
    );

    const manualInput = screen.getByLabelText('Manual Code Entry');
    fireEvent.change(manualInput, { target: { value: 'BATCH-001' } });
    fireEvent.keyPress(manualInput, { key: 'Enter', code: 'Enter', charCode: 13 });

    // Should show loading state
    expect(screen.getByText('Searching for batch...')).toBeInTheDocument();
  });

  it('handles camera scanner start button click', () => {
    renderWithProvider(
      <QRCodeScanner
        open={true}
        onBatchFound={mockOnBatchFound}
        onClose={mockOnClose}
      />
    );

    const startButton = screen.getByText('Start Camera Scanner');
    fireEvent.click(startButton);

    // After clicking, button should change to "Stop Scanner"
    expect(screen.getByText('Stop Scanner')).toBeInTheDocument();
  });

  it('closes scanner when dialog is closed', () => {
    renderWithProvider(
      <QRCodeScanner
        open={true}
        onBatchFound={mockOnBatchFound}
        onClose={mockOnClose}
      />
    );

    const closeButton = screen.getByRole('button', { name: /close scanner/i });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('disables buttons during loading', async () => {
    (traceabilityAPI.getBatches as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    renderWithProvider(
      <QRCodeScanner
        open={true}
        onBatchFound={mockOnBatchFound}
        onClose={mockOnClose}
      />
    );

    const manualInput = screen.getByLabelText('Manual Code Entry');
    const startCameraButton = screen.getByText('Start Camera Scanner');

    fireEvent.change(manualInput, { target: { value: 'BATCH-001' } });
    fireEvent.keyPress(manualInput, { key: 'Enter', code: 'Enter', charCode: 13 });

    // Buttons should be disabled during loading
    expect(startCameraButton).toBeDisabled();
  });
});