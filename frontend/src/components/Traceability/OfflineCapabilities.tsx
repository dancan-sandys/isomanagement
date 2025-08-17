import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  useMediaQuery,
  useTheme,
  Snackbar
} from '@mui/material';
import {
  CloudOff as CloudOffIcon,
  CloudSync as CloudSyncIcon,
  Storage as StorageIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

interface OfflineCapabilitiesProps {
  onSyncComplete?: () => void;
}

interface OfflineData {
  batches: any[];
  recalls: any[];
  reports: any[];
  lastSync: string;
  pendingChanges: any[];
}

const OfflineCapabilities: React.FC<OfflineCapabilitiesProps> = ({
  onSyncComplete
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [offlineData, setOfflineData] = useState<OfflineData>({
    batches: [],
    recalls: [],
    reports: [],
    lastSync: '',
    pendingChanges: []
  });
  const [syncing, setSyncing] = useState(false);
  const [syncProgress, setSyncProgress] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Load offline data from localStorage
    loadOfflineData();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const loadOfflineData = () => {
    try {
      const stored = localStorage.getItem('traceability-offline-data');
      if (stored) {
        const data = JSON.parse(stored);
        setOfflineData(data);
      }
    } catch (err) {
      console.error('Failed to load offline data:', err);
    }
  };

  const saveOfflineData = (data: OfflineData) => {
    try {
      localStorage.setItem('traceability-offline-data', JSON.stringify(data));
      setOfflineData(data);
    } catch (err) {
      console.error('Failed to save offline data:', err);
    }
  };

  const downloadOfflineData = async () => {
    try {
      setSyncing(true);
      setSyncProgress(0);

      // Simulate downloading data in chunks
      const dataTypes = ['batches', 'recalls', 'reports'];
      
      for (let i = 0; i < dataTypes.length; i++) {
        const type = dataTypes[i];
        setSyncProgress((i / dataTypes.length) * 100);
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data - in real implementation, this would be API calls
        const mockData = {
          batches: [
            { id: 1, batch_number: 'BATCH001', product_name: 'Milk Product A', status: 'completed' },
            { id: 2, batch_number: 'BATCH002', product_name: 'Milk Product B', status: 'in_production' }
          ],
          recalls: [
            { id: 1, recall_number: 'RECALL001', title: 'Quality Issue', status: 'initiated' }
          ],
          reports: [
            { id: 1, report_number: 'REPORT001', report_type: 'full_trace', trace_date: new Date().toISOString() }
          ]
        };

        const updatedData = {
          ...offlineData,
          [type]: mockData[type as keyof typeof mockData],
          lastSync: new Date().toISOString()
        };

        saveOfflineData(updatedData);
      }

      setSyncProgress(100);
      onSyncComplete?.();
      
      setTimeout(() => {
        setSyncing(false);
        setSyncProgress(0);
      }, 500);

    } catch (err: any) {
      setError(err.message || 'Failed to download offline data');
      setSyncing(false);
      setSyncProgress(0);
    }
  };

  const uploadPendingChanges = async () => {
    try {
      setSyncing(true);
      setSyncProgress(0);

      const pendingChanges = offlineData.pendingChanges;
      
      for (let i = 0; i < pendingChanges.length; i++) {
        setSyncProgress((i / pendingChanges.length) * 100);
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // Clear pending changes after successful upload
      const updatedData = {
        ...offlineData,
        pendingChanges: []
      };
      saveOfflineData(updatedData);

      setSyncProgress(100);
      
      setTimeout(() => {
        setSyncing(false);
        setSyncProgress(0);
      }, 500);

    } catch (err: any) {
      setError(err.message || 'Failed to upload pending changes');
      setSyncing(false);
      setSyncProgress(0);
    }
  };

  const clearOfflineData = () => {
    try {
      localStorage.removeItem('traceability-offline-data');
      setOfflineData({
        batches: [],
        recalls: [],
        reports: [],
        lastSync: '',
        pendingChanges: []
      });
    } catch (err) {
      console.error('Failed to clear offline data:', err);
    }
  };

  const getStorageUsage = () => {
    try {
      const data = localStorage.getItem('traceability-offline-data');
      if (data) {
        return Math.round((data.length * 2) / 1024); // Approximate size in KB
      }
      return 0;
    } catch (err) {
      return 0;
    }
  };

  return (
    <Box>
      {/* Online/Offline Status */}
      <Alert 
        severity={isOnline ? 'success' : 'warning'} 
        icon={isOnline ? <CheckCircleIcon /> : <CloudOffIcon />}
        sx={{ mb: 2 }}
      >
        {isOnline ? 'Online - All features available' : 'Offline - Limited functionality available'}
      </Alert>

      <Grid container spacing={2}>
        {/* Offline Data Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <StorageIcon color="primary" />
                <Typography variant="h6">Offline Data</Typography>
              </Box>

              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`${offlineData.batches.length} Batches`}
                    secondary="Available offline"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`${offlineData.recalls.length} Recalls`}
                    secondary="Available offline"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`${offlineData.reports.length} Reports`}
                    secondary="Available offline"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    {offlineData.pendingChanges.length > 0 ? (
                      <WarningIcon color="warning" />
                    ) : (
                      <CheckCircleIcon color="success" />
                    )}
                  </ListItemIcon>
                  <ListItemText 
                    primary={`${offlineData.pendingChanges.length} Pending Changes`}
                    secondary={offlineData.pendingChanges.length > 0 ? "Waiting to sync" : "All synced"}
                  />
                </ListItem>
              </List>

              {offlineData.lastSync && (
                <Typography variant="body2" color="text.secondary" mt={2}>
                  Last sync: {new Date(offlineData.lastSync).toLocaleString()}
                </Typography>
              )}

              <Typography variant="body2" color="text.secondary">
                Storage used: {getStorageUsage()} KB
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Sync Controls */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <CloudSyncIcon color="primary" />
                <Typography variant="h6">Sync Controls</Typography>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              {syncing && (
                <Box mb={2}>
                  <Typography variant="body2" mb={1}>
                    Syncing... {Math.round(syncProgress)}%
                  </Typography>
                  <CircularProgress 
                    variant="determinate" 
                    value={syncProgress} 
                    size={24}
                  />
                </Box>
              )}

              <Box display="flex" flexDirection="column" gap={1}>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={downloadOfflineData}
                  disabled={syncing || !isOnline}
                  fullWidth
                >
                  Download Latest Data
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<UploadIcon />}
                  onClick={uploadPendingChanges}
                  disabled={syncing || !isOnline || offlineData.pendingChanges.length === 0}
                  fullWidth
                >
                  Upload Pending Changes ({offlineData.pendingChanges.length})
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={() => {
                    loadOfflineData();
                    setError(null);
                  }}
                  disabled={syncing}
                  fullWidth
                >
                  Refresh Status
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<SettingsIcon />}
                  onClick={() => setShowSettings(true)}
                  fullWidth
                >
                  Offline Settings
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Offline Settings Dialog */}
      <Dialog
        open={showSettings}
        onClose={() => setShowSettings(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Offline Settings</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Configure offline data storage and sync preferences.
          </Typography>

          <Box display="flex" flexDirection="column" gap={2}>
            <Box>
              <Typography variant="subtitle2" mb={1}>
                Storage Usage
              </Typography>
              <Typography variant="body2">
                Current usage: {getStorageUsage()} KB
              </Typography>
            </Box>

            <Box>
              <Typography variant="subtitle2" mb={1}>
                Last Sync
              </Typography>
              <Typography variant="body2">
                {offlineData.lastSync ? 
                  new Date(offlineData.lastSync).toLocaleString() : 
                  'Never synced'
                }
              </Typography>
            </Box>

            <Box>
              <Typography variant="subtitle2" mb={1}>
                Pending Changes
              </Typography>
              <Typography variant="body2">
                {offlineData.pendingChanges.length} changes waiting to sync
              </Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={clearOfflineData}
            color="error"
            variant="outlined"
          >
            Clear All Data
          </Button>
          <Button onClick={() => setShowSettings(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        message={error}
      />
    </Box>
  );
};

export default OfflineCapabilities;
