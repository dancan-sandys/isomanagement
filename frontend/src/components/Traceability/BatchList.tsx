import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Tooltip,
  Checkbox,
  alpha
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  QrCode as QrCodeIcon,
  Timeline as TimelineIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Print as PrintIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import { Batch, SearchFilters } from '../../types/traceability';
import { traceabilityAPI } from '../../services/traceabilityAPI';
import BatchRegistrationForm from './BatchRegistrationForm';
import BatchDetail from './BatchDetail';

interface BatchListProps {
  onBatchSelect?: (batch: Batch) => void;
  showActions?: boolean;
}

const BATCH_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'raw_milk', label: 'Raw Milk' },
  { value: 'additive', label: 'Additive' },
  { value: 'culture', label: 'Culture' },
  { value: 'packaging', label: 'Packaging' },
  { value: 'final_product', label: 'Final Product' },
  { value: 'intermediate', label: 'Intermediate' }
];

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'in_production', label: 'In Production' },
  { value: 'completed', label: 'Completed' },
  { value: 'quarantined', label: 'Quarantined' },
  { value: 'released', label: 'Released' },
  { value: 'recalled', label: 'Recalled' },
  { value: 'disposed', label: 'Disposed' }
];

const QUALITY_STATUS_OPTIONS = [
  { value: '', label: 'All Quality Statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'passed', label: 'Passed' },
  { value: 'failed', label: 'Failed' }
];

const BatchList: React.FC<BatchListProps> = ({
  onBatchSelect,
  showActions = true
}) => {
  // State management
  const [batches, setBatches] = useState<Batch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedBatches, setSelectedBatches] = useState<number[]>([]);

  // Filter states
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    batch_type: '',
    status: '',
    quality_status: '',
    date_from: '',
    date_to: '',
    product_name: '',
    page: 1,
    size: 10
  });

  // Dialog states
  const [batchFormOpen, setBatchFormOpen] = useState(false);
  const [batchDetailOpen, setBatchDetailOpen] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState<Batch | null>(null);

  // Load batches on component mount and filter changes
  useEffect(() => {
    fetchBatches();
  }, [filters, page, rowsPerPage]);

  const fetchBatches = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        ...filters,
        page: page + 1,
        size: rowsPerPage
      };

      const response = await traceabilityAPI.getBatches(params);
      setBatches(response.items || []);
      setTotal(response.total || 0);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load batches');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query: string) => {
    setFilters(prev => ({ ...prev, query }));
    setPage(0);
  };

  const handleFilterChange = (field: keyof SearchFilters, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPage(0);
  };

  const handleClearFilters = () => {
    setFilters({
      query: '',
      batch_type: '',
      status: '',
      quality_status: '',
      date_from: '',
      date_to: '',
      product_name: '',
      page: 1,
      size: 10
    });
    setPage(0);
  };

  const handleBatchSelect = (batch: Batch) => {
    setSelectedBatch(batch);
    setBatchDetailOpen(true);
    onBatchSelect?.(batch);
  };

  const handleBatchEdit = (batch: Batch) => {
    setSelectedBatch(batch);
    setBatchFormOpen(true);
  };

  const handleBatchDelete = async (batchId: number) => {
    if (!window.confirm('Are you sure you want to delete this batch?')) {
      return;
    }

    try {
      await traceabilityAPI.deleteBatch(batchId);
      fetchBatches();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to delete batch');
    }
  };

  const handleBulkDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete ${selectedBatches.length} batches?`)) {
      return;
    }

    try {
      await traceabilityAPI.bulkDeleteBatches(selectedBatches);
      setSelectedBatches([]);
      fetchBatches();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to delete batches');
    }
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedBatches(batches.map(batch => batch.id));
    } else {
      setSelectedBatches([]);
    }
  };

  const handleSelectBatch = (batchId: number) => {
    setSelectedBatches(prev => 
      prev.includes(batchId) 
        ? prev.filter(id => id !== batchId)
        : [...prev, batchId]
    );
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
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5" component="h2">
          Batch Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setBatchFormOpen(true)}
        >
          Add New Batch
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Search batches..."
                value={filters.query}
                onChange={(e) => handleSearch(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Batch Type</InputLabel>
                <Select
                  value={filters.batch_type}
                  onChange={(e) => handleFilterChange('batch_type', e.target.value)}
                  label="Batch Type"
                >
                  {BATCH_TYPES.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  label="Status"
                >
                  {STATUS_OPTIONS.map((status) => (
                    <MenuItem key={status.value} value={status.value}>
                      {status.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Quality Status</InputLabel>
                <Select
                  value={filters.quality_status}
                  onChange={(e) => handleFilterChange('quality_status', e.target.value)}
                  label="Quality Status"
                >
                  {QUALITY_STATUS_OPTIONS.map((status) => (
                    <MenuItem key={status.value} value={status.value}>
                      {status.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box display="flex" gap={1}>
                <Button
                  variant="outlined"
                  startIcon={<ClearIcon />}
                  onClick={handleClearFilters}
                >
                  Clear
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={fetchBatches}
                >
                  Refresh
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Batch Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {showActions && (
                  <TableCell padding="checkbox">
                    <Checkbox
                      indeterminate={selectedBatches.length > 0 && selectedBatches.length < batches.length}
                      checked={batches.length > 0 && selectedBatches.length === batches.length}
                      onChange={handleSelectAll}
                    />
                  </TableCell>
                )}
                <TableCell>Batch Number</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Product</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Production Date</TableCell>
                <TableCell>Quality Status</TableCell>
                {showActions && <TableCell>Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={showActions ? 9 : 8} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : batches.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={showActions ? 9 : 8} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No batches found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                batches.map((batch) => (
                  <TableRow key={batch.id} hover>
                    {showActions && (
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedBatches.includes(batch.id)}
                          onChange={() => handleSelectBatch(batch.id)}
                        />
                      </TableCell>
                    )}
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {batch.batch_number}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={batch.batch_type.replace('_', ' ').toUpperCase()} 
                        color={getBatchTypeColor(batch.batch_type)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{batch.product_name}</TableCell>
                    <TableCell>
                      <Chip 
                        label={batch.status.replace('_', ' ').toUpperCase()} 
                        color={getStatusColor(batch.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {batch.quantity} {batch.unit}
                    </TableCell>
                    <TableCell>
                      {new Date(batch.production_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={batch.quality_status.toUpperCase()} 
                        color={getQualityStatusColor(batch.quality_status)}
                        size="small"
                      />
                    </TableCell>
                    {showActions && (
                      <TableCell>
                        <Box display="flex" gap={1}>
                          <Tooltip title="View Details">
                            <IconButton size="small" onClick={() => handleBatchSelect(batch)}>
                              <VisibilityIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit Batch">
                            <IconButton size="small" onClick={() => handleBatchEdit(batch)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Trace Chain">
                            <IconButton size="small">
                              <TimelineIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Generate QR Code">
                            <IconButton size="small">
                              <QrCodeIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Print Label">
                            <IconButton size="small">
                              <PrintIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Batch">
                            <IconButton 
                              size="small" 
                              color="error"
                              onClick={() => handleBatchDelete(batch.id)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    )}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        <TablePagination
          component="div"
          count={total}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
      </Paper>

      {/* Bulk Actions */}
      {selectedBatches.length > 0 && (
        <Box sx={{ mt: 2, p: 2, bgcolor: alpha('#1976d2', 0.1), borderRadius: 1 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            {selectedBatches.length} batch(es) selected
          </Typography>
          <Box display="flex" gap={1}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<DownloadIcon />}
            >
              Export Selected
            </Button>
            <Button
              variant="outlined"
              size="small"
              startIcon={<PrintIcon />}
            >
              Print Selected
            </Button>
            <Button
              variant="outlined"
              color="error"
              size="small"
              startIcon={<DeleteIcon />}
              onClick={handleBulkDelete}
            >
              Delete Selected
            </Button>
          </Box>
        </Box>
      )}

      {/* Dialogs */}
      <BatchRegistrationForm
        open={batchFormOpen}
        onClose={() => setBatchFormOpen(false)}
        onSuccess={fetchBatches}
        initialData={selectedBatch ? {
          batch_type: selectedBatch.batch_type,
          product_name: selectedBatch.product_name,
          quantity: selectedBatch.quantity.toString(),
          unit: selectedBatch.unit,
          production_date: selectedBatch.production_date,
          expiry_date: selectedBatch.expiry_date || '',
          lot_number: selectedBatch.lot_number || '',
          storage_location: selectedBatch.storage_location || '',
          storage_conditions: selectedBatch.storage_conditions || '',
          supplier_id: selectedBatch.supplier_id
        } : undefined}
        isEdit={!!selectedBatch}
      />

      {selectedBatch && (
        <BatchDetail
          open={batchDetailOpen}
          onClose={() => setBatchDetailOpen(false)}
          batch={selectedBatch}
        />
      )}
    </Box>
  );
};

export default BatchList; 