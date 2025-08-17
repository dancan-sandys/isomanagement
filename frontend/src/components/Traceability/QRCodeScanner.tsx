import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Chip,
  useMediaQuery,
  useTheme
} from '@mui/material';
import {
  QrCode as QrCodeIcon,
  CameraAlt as CameraIcon,
  Close as CloseIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { traceabilityAPI } from '../../services/traceabilityAPI';

interface QRCodeScannerProps {
  onBatchFound?: (batch: any) => void;
  onClose?: () => void;
  open?: boolean;
}

const QRCodeScanner: React.FC<QRCodeScannerProps> = ({
  onBatchFound,
  onClose,
  open = false
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [scanning, setScanning] = useState(false);
  const [currentBatch, setCurrentBatch] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleManualSearch = async (code: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await traceabilityAPI.getBatches({ search: code });
      if (response?.items?.length > 0) {
        const batch = response.items[0];
        setCurrentBatch(batch);
        onBatchFound?.(batch);
      } else {
        setError('No batch found for this code');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to search for batch');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      fullScreen={isMobile}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between'
      }}>
        <Box display="flex" alignItems="center" gap={1}>
          <QrCodeIcon color="primary" />
          <Typography variant="h6">QR Code & Barcode Scanner</Typography>
        </Box>
        <IconButton onClick={onClose} aria-label="Close scanner">
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent>
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" mb={2}>Scanner</Typography>
                
                {error && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                  </Alert>
                )}

                {loading && (
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <CircularProgress size={20} />
                    <Typography>Searching for batch...</Typography>
                  </Box>
                )}

                <Box
                  sx={{
                    width: '100%',
                    height: 300,
                    border: '2px dashed',
                    borderColor: 'divider',
                    borderRadius: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: 'grey.50'
                  }}
                >
                  <Box textAlign="center">
                    <QrCodeIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      Camera scanner will be implemented here
                    </Typography>
                    <Button
                      variant="contained"
                      startIcon={<SearchIcon />}
                      onClick={() => handleManualSearch('BATCH001')}
                    >
                      Test Search
                    </Button>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" mb={2}>Scan Results</Typography>
                
                {currentBatch ? (
                  <Box>
                    <Chip label="Batch Found" color="success" size="small" sx={{ mb: 2 }} />
                    <Typography variant="subtitle1" fontWeight={600}>
                      {currentBatch.batch_number}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {currentBatch.product_name}
                    </Typography>
                    <Button
                      variant="contained"
                      fullWidth
                      sx={{ mt: 2 }}
                      onClick={() => onBatchFound?.(currentBatch)}
                    >
                      View Details
                    </Button>
                  </Box>
                ) : (
                  <Box textAlign="center" py={4}>
                    <QrCodeIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                    <Typography variant="body2" color="text.secondary">
                      Scan a QR code or barcode to find batch information
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default QRCodeScanner;
