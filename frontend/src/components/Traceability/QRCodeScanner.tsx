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
  useTheme,
  TextField
} from '@mui/material';
import {
  QrCode as QrCodeIcon,
  CameraAlt as CameraIcon,
  Close as CloseIcon,
  Search as SearchIcon,
  Stop as StopIcon
} from '@mui/icons-material';
import { Html5QrcodeScanner, Html5QrcodeSupportedFormats } from 'html5-qrcode';
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
  const [manualCode, setManualCode] = useState('');
  const [scannerInstance, setScannerInstance] = useState<Html5QrcodeScanner | null>(null);
  const scannerRef = useRef<HTMLDivElement>(null);

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

  const handleScanSuccess = (decodedText: string) => {
    setError(null);
    handleManualSearch(decodedText);
    stopScanning();
  };

  const handleScanError = (errorMessage: string) => {
    // Don't show scan errors as they happen frequently during scanning
    console.log('Scan error:', errorMessage);
  };

  const startScanning = () => {
    if (!scannerRef.current || scannerInstance) return;

    const config: Html5QrcodeScannerConfig = {
      fps: 10,
      qrbox: { width: 250, height: 250 },
      aspectRatio: 1.0,
      supportedScanTypes: [Html5QrcodeSupportedFormats.QR_CODE, Html5QrcodeSupportedFormats.CODE_128, Html5QrcodeSupportedFormats.CODE_39],
      showTorchButtonIfSupported: true,
      showZoomSliderIfSupported: true,
    };

    const scanner = new Html5QrcodeScanner(
      "qr-reader",
      config,
      false
    );

    scanner.render(handleScanSuccess, handleScanError);
    setScannerInstance(scanner);
    setScanning(true);
    setError(null);
  };

  const stopScanning = () => {
    if (scannerInstance) {
      scannerInstance.clear().catch(console.error);
      setScannerInstance(null);
    }
    setScanning(false);
  };

  useEffect(() => {
    return () => {
      if (scannerInstance) {
        scannerInstance.clear().catch(console.error);
      }
    };
  }, [scannerInstance]);

  useEffect(() => {
    if (!open && scanning) {
      stopScanning();
    }
  }, [open, scanning]);

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

                <Box sx={{ mb: 2 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Button
                        variant={scanning ? "outlined" : "contained"}
                        fullWidth
                        startIcon={scanning ? <StopIcon /> : <CameraIcon />}
                        onClick={scanning ? stopScanning : startScanning}
                        disabled={loading}
                      >
                        {scanning ? 'Stop Scanner' : 'Start Camera Scanner'}
                      </Button>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Manual Code Entry"
                        variant="outlined"
                        value={manualCode}
                        onChange={(e) => setManualCode(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && manualCode.trim()) {
                            handleManualSearch(manualCode.trim());
                          }
                        }}
                        InputProps={{
                          endAdornment: (
                            <IconButton
                              onClick={() => manualCode.trim() && handleManualSearch(manualCode.trim())}
                              disabled={!manualCode.trim() || loading}
                            >
                              <SearchIcon />
                            </IconButton>
                          )
                        }}
                      />
                    </Grid>
                  </Grid>
                </Box>

                <Box
                  id="qr-reader"
                  ref={scannerRef}
                  sx={{
                    width: '100%',
                    minHeight: scanning ? 300 : 200,
                    border: '2px dashed',
                    borderColor: scanning ? 'primary.main' : 'divider',
                    borderRadius: 1,
                    display: scanning ? 'block' : 'flex',
                    alignItems: scanning ? 'stretch' : 'center',
                    justifyContent: scanning ? 'stretch' : 'center',
                    backgroundColor: scanning ? 'transparent' : 'grey.50',
                    '& > div': {
                      border: 'none !important'
                    }
                  }}
                >
                  {!scanning && (
                    <Box textAlign="center">
                      <QrCodeIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
                      <Typography variant="body2" color="text.secondary" mb={2}>
                        Click "Start Camera Scanner" to scan QR codes and barcodes
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Supports QR codes, Code 128, and Code 39 barcodes
                      </Typography>
                    </Box>
                  )}
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
