import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  useMediaQuery,
  useTheme,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Snackbar,
  Slider,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Save as SaveIcon,
  Mic as MicIcon,
  CameraAlt as CameraIcon,
  LocationOn as LocationIcon,
  CloudUpload as CloudUploadIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Close as CloseIcon,
  Settings as SettingsIcon,
  VoiceOverOff as VoiceOverOffIcon,
  RecordVoiceOver as VoiceOverIcon
} from '@mui/icons-material';

interface MobileDataEntryProps {
  onSave?: (data: any) => void;
  onClose?: () => void;
  open?: boolean;
}

interface FieldData {
  batch_number: string;
  product_name: string;
  quantity: number;
  unit: string;
  location: string;
  notes: string;
  photos: string[];
  voice_notes: string[];
  gps_coordinates?: {
    latitude: number;
    longitude: number;
  };
  timestamp: string;
}

const MobileDataEntry: React.FC<MobileDataEntryProps> = ({
  onSave,
  onClose,
  open = false
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [formData, setFormData] = useState<FieldData>({
    batch_number: '',
    product_name: '',
    quantity: 0,
    unit: 'units',
    location: '',
    notes: '',
    photos: [],
    voice_notes: [],
    timestamp: new Date().toISOString()
  });
  
  const [isRecording, setIsRecording] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [autoLocation, setAutoLocation] = useState(true);
  const [voiceInput, setVoiceInput] = useState(false);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    if (autoLocation && open) {
      getCurrentLocation();
    }
  }, [autoLocation, open]);

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            gps_coordinates: {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude
            }
          }));
        },
        (error) => {
          console.error('Location error:', error);
        }
      );
    }
  };

  const handleInputChange = (field: keyof FieldData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const startVoiceRecording = () => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      
      recognition.onstart = () => {
        setIsRecording(true);
      };
      
      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0])
          .map(result => result.transcript)
          .join('');
        
        handleInputChange('notes', formData.notes + ' ' + transcript);
      };
      
      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };
      
      recognition.onend = () => {
        setIsRecording(false);
      };
      
      recognition.start();
    } else {
      setError('Voice recognition not supported in this browser');
    }
  };

  const stopVoiceRecording = () => {
    setIsRecording(false);
  };

  const takePhoto = () => {
    // Simulate photo capture
    const mockPhoto = `photo_${Date.now()}.jpg`;
    handleInputChange('photos', [...formData.photos, mockPhoto]);
  };

  const saveData = async () => {
    try {
      setSaving(true);
      setError(null);

      // Validate required fields
      if (!formData.batch_number || !formData.product_name) {
        throw new Error('Please fill in all required fields');
      }

      // Save to localStorage for offline storage
      const offlineData = JSON.parse(localStorage.getItem('traceability-offline-data') || '{}');
      const pendingChanges = offlineData.pendingChanges || [];
      pendingChanges.push({
        type: 'field_data',
        data: formData,
        timestamp: new Date().toISOString()
      });
      
      localStorage.setItem('traceability-offline-data', JSON.stringify({
        ...offlineData,
        pendingChanges
      }));

      // If online, try to save to server
      if (isOnline) {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      onSave?.(formData);
      
      // Reset form
      setFormData({
        batch_number: '',
        product_name: '',
        quantity: 0,
        unit: 'units',
        location: '',
        notes: '',
        photos: [],
        voice_notes: [],
        timestamp: new Date().toISOString()
      });

    } catch (err: any) {
      setError(err.message || 'Failed to save data');
    } finally {
      setSaving(false);
    }
  };

  const generateBatchNumber = () => {
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    const batchNumber = `BATCH${timestamp}${random}`;
    handleInputChange('batch_number', batchNumber);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      fullScreen={isMobile}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between'
      }}>
        <Box display="flex" alignItems="center" gap={1}>
          <AddIcon color="primary" />
          <Typography variant="h6">Mobile Data Entry</Typography>
        </Box>
        <IconButton onClick={onClose} aria-label="Close">
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent>
        <Alert 
          severity={isOnline ? 'success' : 'warning'} 
          sx={{ mb: 2 }}
        >
          {isOnline ? 'Online - Data will sync immediately' : 'Offline - Data will sync when online'}
        </Alert>

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Batch Number"
              value={formData.batch_number}
              onChange={(e) => handleInputChange('batch_number', e.target.value)}
              helperText="Enter or generate batch number"
              sx={{ mb: 2 }}
            />
            <Button
              variant="outlined"
              onClick={generateBatchNumber}
              size="small"
              fullWidth
            >
              Generate Batch Number
            </Button>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Product Name"
              value={formData.product_name}
              onChange={(e) => handleInputChange('product_name', e.target.value)}
              sx={{ mb: 2 }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Quantity"
              type="number"
              value={formData.quantity}
              onChange={(e) => handleInputChange('quantity', parseFloat(e.target.value) || 0)}
              sx={{ mb: 2 }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Unit</InputLabel>
              <Select
                value={formData.unit}
                onChange={(e) => handleInputChange('unit', e.target.value)}
                label="Unit"
              >
                <MenuItem value="units">Units</MenuItem>
                <MenuItem value="kg">Kilograms</MenuItem>
                <MenuItem value="liters">Liters</MenuItem>
                <MenuItem value="pieces">Pieces</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Location"
              value={formData.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
              helperText={formData.gps_coordinates ? 
                `GPS: ${formData.gps_coordinates.latitude.toFixed(4)}, ${formData.gps_coordinates.longitude.toFixed(4)}` : 
                'Location will be captured automatically'
              }
              sx={{ mb: 2 }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Notes"
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              helperText="Add notes or use voice input"
              sx={{ mb: 2 }}
            />
            
            <Box display="flex" gap={1} mb={2}>
              <Button
                variant="outlined"
                startIcon={isRecording ? <VoiceOverOffIcon /> : <MicIcon />}
                onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                color={isRecording ? 'error' : 'primary'}
                size="small"
              >
                {isRecording ? 'Stop Recording' : 'Voice Input'}
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<CameraIcon />}
                onClick={takePhoto}
                size="small"
              >
                Take Photo ({formData.photos.length})
              </Button>
            </Box>
          </Grid>

          {/* Photos List */}
          {formData.photos.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" mb={1}>
                Photos ({formData.photos.length})
              </Typography>
              <List dense>
                {formData.photos.map((photo, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <CameraIcon />
                    </ListItemIcon>
                    <ListItemText primary={photo} />
                  </ListItem>
                ))}
              </List>
            </Grid>
          )}

          {/* GPS Coordinates */}
          {formData.gps_coordinates && (
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" mb={1}>
                    GPS Coordinates
                  </Typography>
                  <Typography variant="body2">
                    Latitude: {formData.gps_coordinates.latitude.toFixed(6)}
                  </Typography>
                  <Typography variant="body2">
                    Longitude: {formData.gps_coordinates.longitude.toFixed(6)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
          onClick={saveData}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Data'}
        </Button>
      </DialogActions>

      {/* Mobile Speed Dial */}
      {isMobile && (
        <SpeedDial
          ariaLabel="Data entry actions"
          sx={{ 
            position: 'fixed', 
            bottom: 16, 
            right: 16,
            zIndex: theme.zIndex.speedDial
          }}
          icon={<SpeedDialIcon />}
        >
          <SpeedDialAction
            icon={<MicIcon />}
            tooltipTitle="Voice Input"
            onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
          />
          <SpeedDialAction
            icon={<CameraIcon />}
            tooltipTitle="Take Photo"
            onClick={takePhoto}
          />
          <SpeedDialAction
            icon={<LocationIcon />}
            tooltipTitle="Get Location"
            onClick={getCurrentLocation}
          />
          <SpeedDialAction
            icon={<SaveIcon />}
            tooltipTitle="Save Data"
            onClick={saveData}
          />
        </SpeedDial>
      )}

      {/* Settings Dialog */}
      <Dialog
        open={showSettings}
        onClose={() => setShowSettings(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Mobile Settings</DialogTitle>
        <DialogContent>
          <FormControlLabel
            control={
              <Switch
                checked={autoLocation}
                onChange={(e) => setAutoLocation(e.target.checked)}
              />
            }
            label="Auto-capture GPS location"
          />
          <FormControlLabel
            control={
              <Switch
                checked={voiceInput}
                onChange={(e) => setVoiceInput(e.target.checked)}
              />
            }
            label="Enable voice input"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Dialog>
  );
};

export default MobileDataEntry;
