import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithProviders } from '../../../utils/test-utils';
import MobileDataEntry from '../MobileDataEntry';
import { mockLocalStorage, mockGeolocation } from '../../../utils/test-utils';

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

// Mock navigator.geolocation
Object.defineProperty(navigator, 'geolocation', {
  value: mockGeolocation,
  writable: true,
});

// Mock webkitSpeechRecognition
Object.defineProperty(window, 'webkitSpeechRecognition', {
  value: jest.fn().mockImplementation(() => ({
    continuous: false,
    interimResults: false,
    onstart: jest.fn(),
    onresult: jest.fn(),
    onerror: jest.fn(),
    onend: jest.fn(),
    start: jest.fn(),
    stop: jest.fn(),
  })),
  writable: true,
});

describe('MobileDataEntry', () => {
  const defaultProps = {
    onSave: jest.fn(),
    onClose: jest.fn(),
    open: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue('{}');
    mockLocalStorage.setItem.mockClear();
  });

  describe('Rendering', () => {
    it('renders the mobile data entry dialog when open', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      expect(screen.getByText('Mobile Data Entry')).toBeInTheDocument();
      expect(screen.getByText('Batch Number')).toBeInTheDocument();
      expect(screen.getByText('Product Name')).toBeInTheDocument();
      expect(screen.getByText('Quantity')).toBeInTheDocument();
      expect(screen.getByText('Location')).toBeInTheDocument();
      expect(screen.getByText('Notes')).toBeInTheDocument();
    });

    it('does not render when closed', () => {
      render(<MobileDataEntry {...defaultProps} open={false} />);
      
      expect(screen.queryByText('Mobile Data Entry')).not.toBeInTheDocument();
    });

    it('shows online status when connected', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      expect(screen.getByText('Online - Data will sync immediately')).toBeInTheDocument();
    });

    it('shows offline status when disconnected', () => {
      // Mock navigator.onLine to return false
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        writable: true,
      });

      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      expect(screen.getByText('Offline - Data will sync when online')).toBeInTheDocument();
    });
  });

  describe('Form Input', () => {
    it('allows entering batch number', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const batchNumberInput = screen.getByLabelText('Batch Number');
      fireEvent.change(batchNumberInput, { target: { value: 'BATCH123' } });
      
      expect(batchNumberInput).toHaveValue('BATCH123');
    });

    it('allows entering product name', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const productNameInput = screen.getByLabelText('Product Name');
      fireEvent.change(productNameInput, { target: { value: 'Test Product' } });
      
      expect(productNameInput).toHaveValue('Test Product');
    });

    it('allows entering quantity', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const quantityInput = screen.getByLabelText('Quantity');
      fireEvent.change(quantityInput, { target: { value: '100' } });
      
      expect(quantityInput).toHaveValue(100);
    });

    it('allows selecting unit', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const unitSelect = screen.getByLabelText('Unit');
      fireEvent.mouseDown(unitSelect);
      
      const kgOption = screen.getByText('Kilograms');
      fireEvent.click(kgOption);
      
      expect(unitSelect).toHaveValue('kg');
    });

    it('allows entering location', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const locationInput = screen.getByLabelText('Location');
      fireEvent.change(locationInput, { target: { value: 'Warehouse A' } });
      
      expect(locationInput).toHaveValue('Warehouse A');
    });

    it('allows entering notes', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const notesInput = screen.getByLabelText('Notes');
      fireEvent.change(notesInput, { target: { value: 'Test notes' } });
      
      expect(notesInput).toHaveValue('Test notes');
    });
  });

  describe('Batch Number Generation', () => {
    it('generates batch number when button is clicked', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const generateButton = screen.getByText('Generate Batch Number');
      fireEvent.click(generateButton);
      
      const batchNumberInput = screen.getByLabelText('Batch Number');
      expect(batchNumberInput).toHaveValue(expect.stringMatching(/^BATCH\d{9}$/));
    });
  });

  describe('GPS Location', () => {
    it('captures GPS location when auto-location is enabled', async () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      await waitFor(() => {
        expect(mockGeolocation.getCurrentPosition).toHaveBeenCalled();
      });
    });

    it('displays GPS coordinates when available', async () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText(/GPS: 40\.7128, -74\.0060/)).toBeInTheDocument();
      });
    });

    it('allows manual location capture', async () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const locationInput = screen.getByLabelText('Location');
      fireEvent.change(locationInput, { target: { value: 'Manual Location' } });
      
      expect(locationInput).toHaveValue('Manual Location');
    });
  });

  describe('Voice Input', () => {
    it('starts voice recording when voice input button is clicked', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const voiceButton = screen.getByText('Voice Input');
      fireEvent.click(voiceButton);
      
      expect(voiceButton).toHaveTextContent('Stop Recording');
    });

    it('stops voice recording when stop button is clicked', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const voiceButton = screen.getByText('Voice Input');
      fireEvent.click(voiceButton); // Start recording
      fireEvent.click(voiceButton); // Stop recording
      
      expect(voiceButton).toHaveTextContent('Voice Input');
    });

    it('shows error when voice recognition is not supported', () => {
      // Mock webkitSpeechRecognition to be undefined
      Object.defineProperty(window, 'webkitSpeechRecognition', {
        value: undefined,
        writable: true,
      });

      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const voiceButton = screen.getByText('Voice Input');
      fireEvent.click(voiceButton);
      
      expect(screen.getByText('Voice recognition not supported in this browser')).toBeInTheDocument();
    });
  });

  describe('Photo Capture', () => {
    it('adds photo when take photo button is clicked', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const photoButton = screen.getByText('Take Photo (0)');
      fireEvent.click(photoButton);
      
      expect(screen.getByText('Take Photo (1)')).toBeInTheDocument();
    });

    it('displays photo list when photos are taken', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const photoButton = screen.getByText('Take Photo (0)');
      fireEvent.click(photoButton);
      fireEvent.click(photoButton);
      
      expect(screen.getByText('Photos (2)')).toBeInTheDocument();
      expect(screen.getByText(/photo_\d+\.jpg/)).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('requires batch number and product name', async () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const saveButton = screen.getByText('Save Data');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(screen.getByText('Please fill in all required fields')).toBeInTheDocument();
      });
    });

    it('allows saving when required fields are filled', async () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      // Fill required fields
      const batchNumberInput = screen.getByLabelText('Batch Number');
      const productNameInput = screen.getByLabelText('Product Name');
      
      fireEvent.change(batchNumberInput, { target: { value: 'BATCH123' } });
      fireEvent.change(productNameInput, { target: { value: 'Test Product' } });
      
      const saveButton = screen.getByText('Save Data');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(defaultProps.onSave).toHaveBeenCalled();
      });
    });
  });

  describe('Data Saving', () => {
    it('saves data to localStorage', async () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      // Fill required fields
      const batchNumberInput = screen.getByLabelText('Batch Number');
      const productNameInput = screen.getByLabelText('Product Name');
      
      fireEvent.change(batchNumberInput, { target: { value: 'BATCH123' } });
      fireEvent.change(productNameInput, { target: { value: 'Test Product' } });
      
      const saveButton = screen.getByText('Save Data');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
          'traceability-offline-data',
          expect.stringContaining('BATCH123')
        );
      });
    });

    it('calls onSave callback with form data', async () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      // Fill required fields
      const batchNumberInput = screen.getByLabelText('Batch Number');
      const productNameInput = screen.getByLabelText('Product Name');
      
      fireEvent.change(batchNumberInput, { target: { value: 'BATCH123' } });
      fireEvent.change(productNameInput, { target: { value: 'Test Product' } });
      
      const saveButton = screen.getByText('Save Data');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(defaultProps.onSave).toHaveBeenCalledWith(
          expect.objectContaining({
            batch_number: 'BATCH123',
            product_name: 'Test Product',
          })
        );
      });
    });

    it('resets form after successful save', async () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      // Fill required fields
      const batchNumberInput = screen.getByLabelText('Batch Number');
      const productNameInput = screen.getByLabelText('Product Name');
      
      fireEvent.change(batchNumberInput, { target: { value: 'BATCH123' } });
      fireEvent.change(productNameInput, { target: { value: 'Test Product' } });
      
      const saveButton = screen.getByText('Save Data');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(batchNumberInput).toHaveValue('');
        expect(productNameInput).toHaveValue('');
      });
    });
  });

  describe('Dialog Controls', () => {
    it('calls onClose when close button is clicked', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const closeButton = screen.getByLabelText('Close');
      fireEvent.click(closeButton);
      
      expect(defaultProps.onClose).toHaveBeenCalled();
    });

    it('calls onClose when cancel button is clicked', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const cancelButton = screen.getByText('Cancel');
      fireEvent.click(cancelButton);
      
      expect(defaultProps.onClose).toHaveBeenCalled();
    });
  });

  describe('Loading States', () => {
    it('shows loading indicator during save', async () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      // Fill required fields
      const batchNumberInput = screen.getByLabelText('Batch Number');
      const productNameInput = screen.getByLabelText('Product Name');
      
      fireEvent.change(batchNumberInput, { target: { value: 'BATCH123' } });
      fireEvent.change(productNameInput, { target: { value: 'Test Product' } });
      
      const saveButton = screen.getByText('Save Data');
      fireEvent.click(saveButton);
      
      expect(screen.getByText('Saving...')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('displays error message when save fails', async () => {
      // Mock console.error to prevent test noise
      const originalError = console.error;
      console.error = jest.fn();

      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      // Fill required fields
      const batchNumberInput = screen.getByLabelText('Batch Number');
      const productNameInput = screen.getByLabelText('Product Name');
      
      fireEvent.change(batchNumberInput, { target: { value: 'BATCH123' } });
      fireEvent.change(productNameInput, { target: { value: 'Test Product' } });
      
      const saveButton = screen.getByText('Save Data');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to save data')).toBeInTheDocument();
      });

      console.error = originalError;
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      expect(screen.getByLabelText('Close')).toBeInTheDocument();
      expect(screen.getByLabelText('Batch Number')).toBeInTheDocument();
      expect(screen.getByLabelText('Product Name')).toBeInTheDocument();
    });

    it('supports keyboard navigation', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const closeButton = screen.getByLabelText('Close');
      expect(closeButton).toHaveAttribute('tabIndex', '0');
    });
  });

  describe('Mobile Features', () => {
    it('renders with mobile-specific styling', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      // Check that the dialog has fullScreen prop when on mobile
      const dialog = screen.getByRole('dialog');
      expect(dialog).toBeInTheDocument();
    });

    it('has touch-friendly button sizes', () => {
      renderWithProviders(<MobileDataEntry {...defaultProps} />);
      
      const saveButton = screen.getByText('Save Data');
      expect(saveButton).toBeInTheDocument();
    });
  });
});
