import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithProviders } from '../../../utils/test-utils';
import OfflineCapabilities from '../OfflineCapabilities';
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

describe('OfflineCapabilities', () => {
  const defaultProps = {
    onSyncComplete: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Reset localStorage mock
    mockLocalStorage.getItem.mockReturnValue(null);
    mockLocalStorage.setItem.mockClear();
    mockLocalStorage.removeItem.mockClear();
    mockLocalStorage.clear.mockClear();
  });

  describe('Rendering', () => {
    it('renders the offline capabilities component', () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      expect(screen.getByText('Offline Data')).toBeInTheDocument();
      expect(screen.getByText('Sync Controls')).toBeInTheDocument();
      expect(screen.getByText('Download Latest Data')).toBeInTheDocument();
      expect(screen.getByText('Upload Pending Changes (0)')).toBeInTheDocument();
    });

    it('shows online status when connected', () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      expect(screen.getByText('Online - All features available')).toBeInTheDocument();
    });

    it('shows offline status when disconnected', () => {
      // Mock navigator.onLine to return false
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        writable: true,
      });

      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      expect(screen.getByText('Offline - Limited functionality available')).toBeInTheDocument();
    });
  });

  describe('Offline Data Display', () => {
    it('displays offline data counts from localStorage', () => {
      const mockOfflineData = {
        batches: [{ id: 1 }, { id: 2 }],
        recalls: [{ id: 1 }],
        reports: [{ id: 1 }, { id: 2 }, { id: 3 }],
        pendingChanges: [{ id: 1 }],
        lastSync: '2024-01-01T00:00:00Z',
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockOfflineData));

      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      expect(screen.getByText('2 Batches')).toBeInTheDocument();
      expect(screen.getByText('1 Recalls')).toBeInTheDocument();
      expect(screen.getByText('3 Reports')).toBeInTheDocument();
      expect(screen.getByText('1 Pending Changes')).toBeInTheDocument();
    });

    it('shows last sync time when available', () => {
      const mockOfflineData = {
        batches: [],
        recalls: [],
        reports: [],
        pendingChanges: [],
        lastSync: '2024-01-01T12:00:00Z',
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockOfflineData));

      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      expect(screen.getByText(/Last sync:/)).toBeInTheDocument();
    });

    it('shows storage usage information', () => {
      const mockOfflineData = {
        batches: [{ id: 1, data: 'test' }],
        recalls: [],
        reports: [],
        pendingChanges: [],
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockOfflineData));

      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      expect(screen.getByText(/Storage used:/)).toBeInTheDocument();
    });
  });

  describe('Download Functionality', () => {
    it('downloads offline data when button is clicked', async () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const downloadButton = screen.getByText('Download Latest Data');
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(screen.getByText('Syncing... 0%')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText('Syncing... 100%')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(defaultProps.onSyncComplete).toHaveBeenCalled();
      });
    });

    it('disables download button when offline', () => {
      // Mock navigator.onLine to return false
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        writable: true,
      });

      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const downloadButton = screen.getByText('Download Latest Data');
      expect(downloadButton).toBeDisabled();
    });

    it('disables download button while syncing', async () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const downloadButton = screen.getByText('Download Latest Data');
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(downloadButton).toBeDisabled();
      });
    });
  });

  describe('Upload Functionality', () => {
    it('uploads pending changes when button is clicked', async () => {
      const mockOfflineData = {
        batches: [],
        recalls: [],
        reports: [],
        pendingChanges: [{ id: 1 }, { id: 2 }],
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockOfflineData));

      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const uploadButton = screen.getByText('Upload Pending Changes (2)');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByText('Syncing... 0%')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText('Syncing... 100%')).toBeInTheDocument();
      });
    });

    it('disables upload button when no pending changes', () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const uploadButton = screen.getByText('Upload Pending Changes (0)');
      expect(uploadButton).toBeDisabled();
    });

    it('disables upload button when offline', () => {
      // Mock navigator.onLine to return false
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        writable: true,
      });

      const mockOfflineData = {
        batches: [],
        recalls: [],
        reports: [],
        pendingChanges: [{ id: 1 }],
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockOfflineData));

      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const uploadButton = screen.getByText('Upload Pending Changes (1)');
      expect(uploadButton).toBeDisabled();
    });
  });

  describe('Settings Dialog', () => {
    it('opens settings dialog when button is clicked', () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const settingsButton = screen.getByText('Offline Settings');
      fireEvent.click(settingsButton);

      expect(screen.getByText('Offline Settings')).toBeInTheDocument();
      expect(screen.getByText('Configure offline data storage and sync preferences.')).toBeInTheDocument();
    });

    it('displays storage usage in settings', () => {
      const mockOfflineData = {
        batches: [{ id: 1, data: 'test data' }],
        recalls: [],
        reports: [],
        pendingChanges: [],
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockOfflineData));

      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const settingsButton = screen.getByText('Offline Settings');
      fireEvent.click(settingsButton);

      expect(screen.getByText('Storage Usage')).toBeInTheDocument();
      expect(screen.getByText(/Current usage:/)).toBeInTheDocument();
    });

    it('clears all data when clear button is clicked', () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const settingsButton = screen.getByText('Offline Settings');
      fireEvent.click(settingsButton);

      const clearButton = screen.getByText('Clear All Data');
      fireEvent.click(clearButton);

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('traceability-offline-data');
    });
  });

  describe('Error Handling', () => {
    it('displays error message when download fails', async () => {
      // Mock console.error to prevent test noise
      const originalError = console.error;
      console.error = jest.fn();

      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const downloadButton = screen.getByText('Download Latest Data');
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to download offline data')).toBeInTheDocument();
      });

      console.error = originalError;
    });

    it('displays error message when upload fails', async () => {
      const mockOfflineData = {
        batches: [],
        recalls: [],
        reports: [],
        pendingChanges: [{ id: 1 }],
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockOfflineData));

      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const uploadButton = screen.getByText('Upload Pending Changes (1)');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to upload pending changes')).toBeInTheDocument();
      });
    });

    it('clears error when refresh button is clicked', async () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const downloadButton = screen.getByText('Download Latest Data');
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to download offline data')).toBeInTheDocument();
      });

      const refreshButton = screen.getByText('Refresh Status');
      fireEvent.click(refreshButton);

      await waitFor(() => {
        expect(screen.queryByText('Failed to download offline data')).not.toBeInTheDocument();
      });
    });
  });

  describe('Progress Tracking', () => {
    it('shows progress during download', async () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const downloadButton = screen.getByText('Download Latest Data');
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(screen.getByText('Syncing... 0%')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText('Syncing... 33%')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText('Syncing... 66%')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText('Syncing... 100%')).toBeInTheDocument();
      });
    });

    it('shows progress during upload', async () => {
      const mockOfflineData = {
        batches: [],
        recalls: [],
        reports: [],
        pendingChanges: [{ id: 1 }, { id: 2 }],
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockOfflineData));

      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const uploadButton = screen.getByText('Upload Pending Changes (2)');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByText('Syncing... 0%')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText('Syncing... 50%')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText('Syncing... 100%')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels and roles', () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Offline Data')).toBeInTheDocument();
      expect(screen.getByText('Sync Controls')).toBeInTheDocument();
    });

    it('supports keyboard navigation', () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      const downloadButton = screen.getByText('Download Latest Data');
      expect(downloadButton).toHaveAttribute('tabIndex', '0');
    });
  });

  describe('Mobile Responsiveness', () => {
    it('renders with mobile-specific styling', () => {
      renderWithProviders(<OfflineCapabilities {...defaultProps} />);
      
      // Check that the grid layout is responsive
      const gridContainer = screen.getByText('Offline Data').closest('.MuiGrid-container');
      expect(gridContainer).toBeInTheDocument();
    });
  });
});
