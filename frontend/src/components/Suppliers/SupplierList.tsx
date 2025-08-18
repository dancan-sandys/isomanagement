import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
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
  Checkbox,
  IconButton,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Tooltip,
  Typography,
  LinearProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Business,
  
  Search,
  FilterList,
  Star,
  StarBorder,
  ViewList,
  ViewModule,
  Settings,
  Archive,
  RestoreFromTrash,
  Assessment as AssessmentIcon,
  
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { format, parseISO } from 'date-fns';
import {
  fetchSuppliers,
  setSupplierFilters,
  clearSupplierFilters,
  setSelectedSuppliers,
  bulkUpdateSupplierStatus,
  deleteSupplier,
} from '../../store/slices/supplierSlice';
import { RootState, AppDispatch } from '../../store';
import { Supplier, SupplierFilters } from '../../types/supplier';
import { EnhancedCard } from '../UI';
import { EnhancedStatusChip } from '../UI';
import DataTable from '../UI/DataTable';
import { NotificationToast } from '../UI';

interface SupplierListProps {
  onViewSupplier?: (supplier: Supplier) => void;
  onEditSupplier?: (supplier: Supplier) => void;
  onCreateSupplier?: () => void;
  onBulkAction?: (action: string, supplierIds: number[]) => void;
}

const SupplierList: React.FC<SupplierListProps> = ({
  onViewSupplier,
  onEditSupplier,
  onCreateSupplier,
  onBulkAction,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const {
    suppliers,
    suppliersLoading,
    suppliersError,
    selectedItems,
    filters,
  } = useSelector((state: RootState) => state.supplier);

  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [bulkActionDialog, setBulkActionDialog] = useState(false);
  const [bulkAction, setBulkAction] = useState('');
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ open: false, message: '', severity: 'info' });

  // Filter states
  const [filterCategory, setFilterCategory] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterRiskLevel, setFilterRiskLevel] = useState('');
  const [filterDateFrom, setFilterDateFrom] = useState<Date | null>(null);
  const [filterDateTo, setFilterDateTo] = useState<Date | null>(null);
  const [filterScoreMin, setFilterScoreMin] = useState('');
  const [filterScoreMax, setFilterScoreMax] = useState('');

  useEffect(() => {
    loadSuppliers();
  }, [page, rowsPerPage, filters]);

  useEffect(() => {
    const timer = setTimeout(() => {
      dispatch(setSupplierFilters({ ...filters.suppliers, search: searchTerm } as any));
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm, dispatch]);

  const loadSuppliers = () => {
    dispatch(fetchSuppliers({
      page: page + 1,
      size: rowsPerPage,
      ...filters.suppliers,
    }));
  };

  const handlePageChange = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleFilterChange = () => {
    const newFilters: SupplierFilters = {};
    
    if (filterCategory) newFilters.category = filterCategory;
    if (filterStatus) newFilters.status = filterStatus;
    if (filterRiskLevel) newFilters.risk_level = filterRiskLevel;
    if (filterDateFrom) newFilters.date_from = format(filterDateFrom, 'yyyy-MM-dd');
    if (filterDateTo) newFilters.date_to = format(filterDateTo, 'yyyy-MM-dd');
    if (filterScoreMin) newFilters.score_min = parseFloat(filterScoreMin);
    if (filterScoreMax) newFilters.score_max = parseFloat(filterScoreMax);

    dispatch(setSupplierFilters(newFilters));
    setPage(0);
  };

  const handleClearFilters = () => {
    dispatch(clearSupplierFilters());
    setFilterCategory('');
    setFilterStatus('');
    setFilterRiskLevel('');
    setFilterDateFrom(null);
    setFilterDateTo(null);
    setFilterScoreMin('');
    setFilterScoreMax('');
    setSearchTerm('');
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      const allIds = suppliers?.items.map(s => s.id) || [];
      dispatch(setSelectedSuppliers(allIds));
    } else {
      dispatch(setSelectedSuppliers([]));
    }
  };

  const handleSelectSupplier = (supplierId: number) => {
    const currentSelected = selectedItems.suppliers;
    const newSelected = currentSelected.includes(supplierId)
      ? currentSelected.filter(id => id !== supplierId)
      : [...currentSelected, supplierId];
    dispatch(setSelectedSuppliers(newSelected));
  };

  const handleBulkAction = async () => {
    if (selectedItems.suppliers.length === 0) {
      setNotification({
        open: true,
        message: 'Please select suppliers for bulk action',
        severity: 'warning',
      });
      return;
    }

    try {
      if (bulkAction === 'status_update') {
        await dispatch(bulkUpdateSupplierStatus({
          supplier_ids: selectedItems.suppliers,
          new_status: 'active',
        })).unwrap();
        
        setNotification({
          open: true,
          message: `Updated status for ${selectedItems.suppliers.length} suppliers`,
          severity: 'success',
        });
      }

      dispatch(setSelectedSuppliers([]));
      setBulkActionDialog(false);
      setBulkAction('');
      loadSuppliers();
    } catch (error) {
      setNotification({
        open: true,
        message: 'Failed to perform bulk action',
        severity: 'error',
      });
    }
  };

  const handleDeleteSupplier = async (supplierId: number) => {
    try {
      await dispatch(deleteSupplier(supplierId)).unwrap();
      setNotification({
        open: true,
        message: 'Supplier deleted successfully',
        severity: 'success',
      });
      loadSuppliers();
    } catch (error) {
      setNotification({
        open: true,
        message: 'Failed to delete supplier',
        severity: 'error',
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'suspended': return 'warning';
      case 'pending_approval': return 'info';
      case 'blacklisted': return 'error';
      default: return 'default';
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getCategoryDisplayName = (category: string) => {
    return category?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
  };

  const getStatusDisplayName = (status: string) => {
    return status?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
  };

  // Utility function to safely convert to uppercase
  const safeToUpperCase = (value: string | null | undefined, fallback: string = 'N/A') => {
    return value?.toUpperCase() || fallback;
  };

  const renderTable = () => (
    <TableContainer component={Paper} elevation={2}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox
                indeterminate={selectedItems.suppliers.length > 0 && selectedItems.suppliers.length < (suppliers?.items.length || 0)}
                checked={selectedItems.suppliers.length > 0 && selectedItems.suppliers.length === (suppliers?.items.length || 0)}
                onChange={handleSelectAll}
              />
            </TableCell>
            <TableCell>Supplier</TableCell>
            <TableCell>Category</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Risk Level</TableCell>
            <TableCell>Score</TableCell>
            <TableCell>Materials</TableCell>
            <TableCell>Last Evaluation</TableCell>
            <TableCell>Next Evaluation</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {suppliersLoading ? (
            <TableRow>
              <TableCell colSpan={10} align="center">
                <LinearProgress />
                <Typography sx={{ mt: 1 }}>Loading suppliers...</Typography>
              </TableCell>
            </TableRow>
          ) : suppliers?.items.length === 0 ? (
            <TableRow>
              <TableCell colSpan={10} align="center">
                <Typography variant="body2" color="text.secondary">
                  No suppliers found
                </Typography>
              </TableCell>
            </TableRow>
          ) : (
            suppliers?.items.map((supplier) => (
              <TableRow key={supplier.id} hover>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedItems.suppliers.includes(supplier.id)}
                    onChange={() => handleSelectSupplier(supplier.id)}
                  />
                </TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {supplier.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {supplier.supplier_code}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={getCategoryDisplayName(supplier.category)}
                    size="small"
                    icon={<Business />}
                  />
                </TableCell>
                <TableCell>
                  <EnhancedStatusChip
                    status={supplier.status}
                    label={getStatusDisplayName(supplier.status)}
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={supplier.risk_level?.toUpperCase() || 'N/A'}
                    color={getRiskLevelColor(supplier.risk_level) as any}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Typography variant="body2" fontWeight="bold">
                      {(supplier.overall_score || 0).toFixed(1)}
                    </Typography>
                    {(supplier.overall_score || 0) >= 8 ? (
                      <Star sx={{ color: 'gold', fontSize: 16 }} />
                    ) : (supplier.overall_score || 0) >= 6 ? (
                      <StarBorder sx={{ color: 'gold', fontSize: 16 }} />
                    ) : null}
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={`${supplier.materials_count} materials`}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  {supplier.last_evaluation_date && !isNaN(Date.parse(supplier.last_evaluation_date)) ? (
                    <Typography variant="body2">
                      {format(parseISO(supplier.last_evaluation_date), 'MMM dd, yyyy')}
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Never
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  {supplier.next_evaluation_date && !isNaN(Date.parse(supplier.next_evaluation_date)) ? (
                    <Typography variant="body2">
                      {format(parseISO(supplier.next_evaluation_date), 'MMM dd, yyyy')}
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Not scheduled
                    </Typography>
                  )}
                </TableCell>
                <TableCell align="center">
                  <Box display="flex" gap={1} justifyContent="center">
                    <Tooltip title="View Details">
                      <IconButton
                        size="small"
                        onClick={() => onViewSupplier?.(supplier)}
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit Supplier">
                      <IconButton
                        size="small"
                        onClick={() => onEditSupplier?.(supplier)}
                      >
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Supplier">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteSupplier(supplier.id)}
                      >
                        <Delete />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      {suppliers && (
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={suppliers.total}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handlePageChange}
          onRowsPerPageChange={handleRowsPerPageChange}
        />
      )}
    </TableContainer>
  );

  const renderGrid = () => (
    <Grid container spacing={3}>
      {suppliersLoading ? (
        <Grid item xs={12}>
          <Box display="flex" justifyContent="center" p={3}>
            <LinearProgress sx={{ width: '100%' }} />
          </Box>
        </Grid>
      ) : suppliers?.items.length === 0 ? (
        <Grid item xs={12}>
          <Box display="flex" justifyContent="center" p={3}>
            <Typography variant="body2" color="text.secondary">
              No suppliers found
            </Typography>
          </Box>
        </Grid>
      ) : (
        suppliers?.items.map((supplier) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={supplier.id}>
            <EnhancedCard title={supplier.name || 'Supplier'} borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Box>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      {supplier.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {supplier.supplier_code}
                    </Typography>
                  </Box>
                  <Checkbox
                    checked={selectedItems.suppliers.includes(supplier.id)}
                    onChange={() => handleSelectSupplier(supplier.id)}
                  />
                </Box>

                <Box display="flex" flexDirection="column" gap={1} mb={2}>
                  <Chip
                    label={getCategoryDisplayName(supplier.category)}
                    size="small"
                    icon={<Business />}
                  />
                  <EnhancedStatusChip
                    status={supplier.status}
                    label={getStatusDisplayName(supplier.status)}
                  />
                  <Chip
                    label={supplier.risk_level?.toUpperCase() || 'N/A'}
                    color={getRiskLevelColor(supplier.risk_level) as any}
                    size="small"
                    variant="outlined"
                  />
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">Score:</Typography>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <Typography variant="body2" fontWeight="bold">
                      {(supplier.overall_score || 0).toFixed(1)}
                    </Typography>
                    {(supplier.overall_score || 0) >= 8 ? (
                      <Star sx={{ color: 'gold', fontSize: 16 }} />
                    ) : (supplier.overall_score || 0) >= 6 ? (
                      <StarBorder sx={{ color: 'gold', fontSize: 16 }} />
                    ) : null}
                  </Box>
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">Materials:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {supplier.materials_count}
                  </Typography>
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Contact:</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {supplier.contact_person}
                  </Typography>
                </Box>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  startIcon={<Visibility />}
                  onClick={() => onViewSupplier?.(supplier)}
                >
                  View
                </Button>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => onEditSupplier?.(supplier)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDeleteSupplier(supplier.id)}
                >
                  Delete
                </Button>
              </CardActions>
            </EnhancedCard>
          </Grid>
        ))
      )}
    </Grid>
  );

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            Supplier Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage suppliers, materials, and evaluations
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<ViewList />}
            onClick={() => setViewMode('table')}
            color={viewMode === 'table' ? 'primary' : 'inherit'}
          >
            Table
          </Button>
          <Button
            variant="outlined"
            startIcon={<ViewModule />}
            onClick={() => setViewMode('grid')}
            color={viewMode === 'grid' ? 'primary' : 'inherit'}
          >
            Grid
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={onCreateSupplier}
          >
            New Supplier
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {suppliersError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => {}}>
          {suppliersError}
        </Alert>
      )}

      {/* Search and Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search suppliers..."
              value={searchTerm}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={filterCategory}
                label="Category"
                onChange={(e) => setFilterCategory(e.target.value)}
              >
                <MenuItem value="">All Categories</MenuItem>
                <MenuItem value="raw_milk">Raw Milk</MenuItem>
                <MenuItem value="additives">Additives</MenuItem>
                <MenuItem value="cultures">Cultures</MenuItem>
                <MenuItem value="packaging">Packaging</MenuItem>
                <MenuItem value="equipment">Equipment</MenuItem>
                <MenuItem value="chemicals">Chemicals</MenuItem>
                <MenuItem value="services">Services</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                label="Status"
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
                <MenuItem value="suspended">Suspended</MenuItem>
                <MenuItem value="pending_approval">Pending Approval</MenuItem>
                <MenuItem value="blacklisted">Blacklisted</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Risk Level</InputLabel>
              <Select
                value={filterRiskLevel}
                label="Risk Level"
                onChange={(e) => setFilterRiskLevel(e.target.value)}
              >
                <MenuItem value="">All Risk Levels</MenuItem>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterList />}
              onClick={() => setShowFilters(!showFilters)}
            >
              Filters
            </Button>
          </Grid>
        </Grid>

        {/* Advanced Filters */}
        {showFilters && (
          <Box mt={2} pt={2} borderTop={1} borderColor="divider">
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Date From"
                    value={filterDateFrom}
                    onChange={setFilterDateFrom}
                    slotProps={{ textField: { fullWidth: true } }}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12} md={3}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Date To"
                    value={filterDateTo}
                    onChange={setFilterDateTo}
                    slotProps={{ textField: { fullWidth: true } }}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  label="Min Score"
                  type="number"
                  value={filterScoreMin}
                  onChange={(e) => setFilterScoreMin(e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  label="Max Score"
                  type="number"
                  value={filterScoreMax}
                  onChange={(e) => setFilterScoreMax(e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <Box display="flex" gap={1}>
                  <Button
                    variant="contained"
                    onClick={handleFilterChange}
                    size="small"
                  >
                    Apply
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={handleClearFilters}
                    size="small"
                  >
                    Clear
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>

      {/* Bulk Actions Toolbar */}
      {selectedItems.suppliers.length > 0 && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="body2">
              {selectedItems.suppliers.length} supplier(s) selected
            </Typography>
            <Box display="flex" gap={1}>
              <Button
                size="small"
                variant="outlined"
                onClick={() => setBulkActionDialog(true)}
                sx={{ color: 'inherit', borderColor: 'inherit' }}
              >
                Bulk Actions
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={() => dispatch(setSelectedSuppliers([]))}
                sx={{ color: 'inherit', borderColor: 'inherit' }}
              >
                Clear Selection
              </Button>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Content */}
      {viewMode === 'table' ? renderTable() : renderGrid()}

      {/* Bulk Action Dialog */}
      <Dialog open={bulkActionDialog} onClose={() => setBulkActionDialog(false)}>
        <DialogTitle>Bulk Actions</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 1 }}>
            <InputLabel>Action</InputLabel>
            <Select
              value={bulkAction}
              label="Action"
              onChange={(e) => setBulkAction(e.target.value)}
            >
              <MenuItem value="status_update">Update Status</MenuItem>
              <MenuItem value="evaluation_schedule">Schedule Evaluation</MenuItem>
              <MenuItem value="document_reminder">Send Document Reminder</MenuItem>
              <MenuItem value="risk_assessment">Risk Assessment</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkActionDialog(false)}>Cancel</Button>
          <Button onClick={handleBulkAction} variant="contained">
            Apply
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notification Toast */}
      <NotificationToast
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={() => setNotification({ ...notification, open: false })}
      />
    </Box>
  );
};

export default SupplierList; 