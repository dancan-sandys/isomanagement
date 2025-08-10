import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Typography,
  Chip,
  Box,
  Card,
  CardContent,
  Divider,
  IconButton,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import {
  Close as CloseIcon,
  QrCode as QrCodeIcon,
  Print as PrintIcon,
  Download as DownloadIcon,
  Timeline as TimelineIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { Batch, BarcodeData, QRCodeData } from '../../types/traceability';
import { traceabilityAPI } from '../../services/traceabilityAPI';
import BarcodeDisplay from './BarcodeDisplay';
import QRCodeDisplay from './QRCodeDisplay';

interface BatchDetailProps {
  open: boolean;
  onClose: () => void;
  batch: Batch;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`batch-tabpanel-${index}`}
      aria-labelledby={`batch-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const BatchDetail: React.FC<BatchDetailProps> = ({
  open,
  onClose,
  batch
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [barcodeData, setBarcodeData] = useState<BarcodeData | null>(null);
  const [qrCodeData, setQrCodeData] = useState<QRCodeData | null>(null);

  useEffect(() => {
    if (open && batch) {
      loadBarcodeData();
      loadQRCodeData();
    }
  }, [open, batch]);

  const loadBarcodeData = async () => {
    try {
      setLoading(true);
      const data = await traceabilityAPI.generateBarcode(batch.id);
      setBarcodeData(data);
    } catch (err: any) {
      console.error('Failed to load barcode data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadQRCodeData = async () => {
    try {
      setLoading(true);
      const data = await traceabilityAPI.generateQRCode(batch.id);
      setQrCodeData(data);
    } catch (err: any) {
      console.error('Failed to load QR code data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePrintLabel = async () => {
    try {
      setLoading(true);
      await traceabilityAPI.printBarcode(batch.id, 'pdf');
      // Handle print response
    } catch (err: any) {
      setError('Failed to print label');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'in_production': return 'primary';
      case 'completed': return 'success';
      case 'quarantined': return 'warning';
      case 'released': return 'info';
      case 'recalled': return 'error';
      case 'disposed': return 'default';
      default: return 'default';
    }
  };

  const getBatchTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'raw_milk': return 'primary';
      case 'additive': return 'secondary';
      case 'culture': return 'success';
      case 'packaging': return 'warning';
      case 'final_product': return 'info';
      case 'intermediate': return 'default';
      default: return 'default';
    }
  };

  const getQualityStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'passed': return 'success';
      case 'failed': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            Batch Details - {batch.batch_number}
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Header Information */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Basic Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Batch Number
                    </Typography>
                    <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                      {batch.batch_number}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Product Name
                    </Typography>
                    <Typography variant="body1">
                      {batch.product_name}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Batch Type
                    </Typography>
                    <Chip 
                      label={batch.batch_type.replace('_', ' ').toUpperCase()} 
                      color={getBatchTypeColor(batch.batch_type)}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Status
                    </Typography>
                    <Chip 
                      label={batch.status.replace('_', ' ').toUpperCase()} 
                      color={getStatusColor(batch.status)}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Quantity
                    </Typography>
                    <Typography variant="body1">
                      {batch.quantity} {batch.unit}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Quality Status
                    </Typography>
                    <Chip 
                      label={batch.quality_status.toUpperCase()} 
                      color={getQualityStatusColor(batch.quality_status)}
                      size="small"
                    />
                  </Grid>
                </Grid>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Additional Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Production Date
                    </Typography>
                    <Typography variant="body1">
                      {new Date(batch.production_date).toLocaleDateString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Expiry Date
                    </Typography>
                    <Typography variant="body1">
                      {batch.expiry_date 
                        ? new Date(batch.expiry_date).toLocaleDateString()
                        : 'Not specified'
                      }
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Lot Number
                    </Typography>
                    <Typography variant="body1">
                      {batch.lot_number || 'Not specified'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Storage Location
                    </Typography>
                    <Typography variant="body1">
                      {batch.storage_location || 'Not specified'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Storage Conditions
                    </Typography>
                    <Typography variant="body1">
                      {batch.storage_conditions 
                        ? batch.storage_conditions.replace('_', ' ').toUpperCase()
                        : 'Not specified'
                      }
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Supplier
                    </Typography>
                    <Typography variant="body1">
                      {batch.supplier_name || 'Not specified'}
                    </Typography>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Barcode & QR Code" />
            <Tab label="Traceability Chain" />
            <Tab label="Process History" />
            <Tab label="Quality Records" />
          </Tabs>
        </Box>

        {/* Tab Content */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Barcode
              </Typography>
              {loading ? (
                <CircularProgress />
              ) : barcodeData ? (
                <BarcodeDisplay barcodeData={barcodeData} />
              ) : (
                <Typography color="text.secondary">
                  No barcode data available
                </Typography>
              )}
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                QR Code
              </Typography>
              {loading ? (
                <CircularProgress />
              ) : qrCodeData ? (
                <QRCodeDisplay qrCodeData={qrCodeData} />
              ) : (
                <Typography color="text.secondary">
                  No QR code data available
                </Typography>
              )}
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <Typography variant="h6" gutterBottom>
            Traceability Chain
          </Typography>
          <Typography color="text.secondary">
            Traceability chain visualization will be implemented here.
          </Typography>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Typography variant="h6" gutterBottom>
            Process History
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Process Step</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Operator</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    <Typography color="text.secondary">
                      No process history available
                    </Typography>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <Typography variant="h6" gutterBottom>
            Quality Records
          </Typography>
          <Typography color="text.secondary">
            Quality records and test results will be displayed here.
          </Typography>
        </TabPanel>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>
          Close
        </Button>
        <Button
          variant="outlined"
          startIcon={<TimelineIcon />}
        >
          View Trace Chain
        </Button>
        <Button
          variant="outlined"
          startIcon={<PrintIcon />}
          onClick={handlePrintLabel}
          disabled={loading}
        >
          Print Label
        </Button>
        <Button
          variant="contained"
          startIcon={<EditIcon />}
        >
          Edit Batch
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BatchDetail; 