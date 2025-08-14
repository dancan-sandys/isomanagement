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
  
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Search,
  FilterList,
  ViewList,
  ViewModule,
  AddCircle,
  Inventory2,
  Cancel,
  Coronavirus as Allergen,
  Inventory,
  Science,
  Build,
  Support,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { format, parseISO } from 'date-fns';
import {
  fetchMaterials,
  setMaterialFilters,
  clearMaterialFilters,
  setSelectedMaterials,
  approveMaterial,
  rejectMaterial,
  bulkApproveMaterials,
  bulkRejectMaterials,
  deleteMaterial,
} from '../../store/slices/supplierSlice';
import { RootState, AppDispatch } from '../../store';
import { Material, MaterialFilters } from '../../types/supplier';
import { EnhancedCard } from '../UI';
import { EnhancedStatusChip } from '../UI';
// import DataTable from '../UI/DataTable';
import { NotificationToast } from '../UI';

interface MaterialListProps {
  onViewMaterial?: (material: Material) => void;
  onEditMaterial?: (material: Material) => void;
  onCreateMaterial?: () => void;
  onBulkAction?: (action: string, materialIds: number[]) => void;
}

const MaterialList: React.FC<MaterialListProps> = ({
  onViewMaterial,
  onEditMaterial,
  onCreateMaterial,
  onBulkAction,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const {
    materials,
    materialsLoading,
    materialsError,
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
  const [approvalDialog, setApprovalDialog] = useState(false);
  const [selectedMaterial, setSelectedMaterial] = useState<Material | null>(null);
  const [approvalComments, setApprovalComments] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ open: false, message: '', severity: 'info' });

  // Filter states
  const [filterCategory, setFilterCategory] = useState('');
  const [filterSupplier, setFilterSupplier] = useState('');
  const [filterApprovalStatus, setFilterApprovalStatus] = useState('');
  const [filterAllergens, setFilterAllergens] = useState<string[]>([]);
  const [filterDateFrom, setFilterDateFrom] = useState<Date | null>(null);
  const [filterDateTo, setFilterDateTo] = useState<Date | null>(null);

  useEffect(() => {
    loadMaterials();
  }, [page, rowsPerPage, filters]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm !== (filters.materials as any)?.search) {
        dispatch(setMaterialFilters({ ...(filters.materials || {}), search: searchTerm } as any));
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm, dispatch, filters.materials]);

  const loadMaterials = () => {
    dispatch(fetchMaterials({
      page: page + 1,
      size: rowsPerPage,
      ...filters.materials,
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
    const newFilters: MaterialFilters & { date_from?: string; date_to?: string } = {};
    
    if (filterCategory) newFilters.category = filterCategory;
    if (filterSupplier) newFilters.supplier_id = parseInt(filterSupplier);
    if (filterApprovalStatus) newFilters.approval_status = filterApprovalStatus;
    if (filterAllergens.length > 0) newFilters.allergens = filterAllergens;
    if (filterDateFrom) (newFilters as any).date_from = format(filterDateFrom, 'yyyy-MM-dd');
    if (filterDateTo) (newFilters as any).date_to = format(filterDateTo, 'yyyy-MM-dd');

    // Cast to any because store typing for MaterialFilters currently omits date range
    dispatch(setMaterialFilters(newFilters as any));
    setPage(0);
  };

  const handleClearFilters = () => {
    dispatch(clearMaterialFilters());
    setFilterCategory('');
    setFilterSupplier('');
    setFilterApprovalStatus('');
    setFilterAllergens([]);
    setFilterDateFrom(null);
    setFilterDateTo(null);
    setSearchTerm('');
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      const allIds = materials?.items.map(m => m.id) || [];
      dispatch(setSelectedMaterials(allIds));
    } else {
      dispatch(setSelectedMaterials([]));
    }
  };

  const handleSelectMaterial = (materialId: number) => {
    const currentSelected = selectedItems.materials;
    const newSelected = currentSelected.includes(materialId)
      ? currentSelected.filter(id => id !== materialId)
      : [...currentSelected, materialId];
    dispatch(setSelectedMaterials(newSelected));
  };

  const handleBulkAction = async () => {
    if (selectedItems.materials.length === 0) {
      setNotification({
        open: true,
        message: 'Please select materials for bulk action',
        severity: 'warning',
      });
      return;
    }

    try {
      if (bulkAction === 'approve') {
        await dispatch(bulkApproveMaterials({
          materialIds: selectedItems.materials,
          comments: approvalComments,
        })).unwrap();
        
        setNotification({
          open: true,
          message: `Approved ${selectedItems.materials.length} materials`,
          severity: 'success',
        });
      } else if (bulkAction === 'reject') {
        await dispatch(bulkRejectMaterials({
          materialIds: selectedItems.materials,
          rejectionReason,
        })).unwrap();
        
        setNotification({
          open: true,
          message: `Rejected ${selectedItems.materials.length} materials`,
          severity: 'success',
        });
      }

      dispatch(setSelectedMaterials([]));
      setBulkActionDialog(false);
      setBulkAction('');
      setApprovalComments('');
      setRejectionReason('');
      loadMaterials();
    } catch (error) {
      setNotification({
        open: true,
        message: 'Failed to perform bulk action',
        severity: 'error',
      });
    }
  };

  const handleApproveMaterial = async (material: Material) => {
    setSelectedMaterial(material);
    setApprovalDialog(true);
  };

  const handleRejectMaterial = async (material: Material) => {
    setSelectedMaterial(material);
    setApprovalDialog(true);
  };

  const handleApprovalSubmit = async () => {
    if (!selectedMaterial) return;

    try {
      if (approvalComments) {
        await dispatch(approveMaterial({
          materialId: selectedMaterial.id,
          comments: approvalComments,
        })).unwrap();
        
        setNotification({
          open: true,
          message: 'Material approved successfully',
          severity: 'success',
        });
      } else if (rejectionReason) {
        await dispatch(rejectMaterial({
          materialId: selectedMaterial.id,
          rejectionReason,
        })).unwrap();
        
        setNotification({
          open: true,
          message: 'Material rejected successfully',
          severity: 'success',
        });
      }

      setApprovalDialog(false);
      setSelectedMaterial(null);
      setApprovalComments('');
      setRejectionReason('');
      loadMaterials();
    } catch (error) {
      setNotification({
        open: true,
        message: 'Failed to update material status',
        severity: 'error',
      });
    }
  };

  const handleDeleteMaterial = async (materialId: number) => {
    try {
      await dispatch(deleteMaterial(materialId)).unwrap();
      setNotification({
        open: true,
        message: 'Material deleted successfully',
        severity: 'success',
      });
      loadMaterials();
    } catch (error) {
      setNotification({
        open: true,
        message: 'Failed to delete material',
        severity: 'error',
      });
    }
  };

  const getApprovalStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      case 'under_review': return 'info';
      default: return 'default';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'raw_milk': return <Inventory2 />;
      case 'additives': return <AddCircle />;
      case 'cultures': return <Allergen />;
      case 'packaging': return <Inventory2 />;
      case 'equipment': return <Inventory2 />;
      case 'chemicals': return <Allergen />;
      case 'services': return <Inventory2 />;
      default: return <Inventory2 />;
    }
  };

  const getCategoryDisplayName = (category: string) => {
    return category?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
  };

  const getApprovalStatusDisplayName = (status: string) => {
    return status?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
  };

  const renderTable = () => (
    <TableContainer component={Paper} elevation={2}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox
                indeterminate={selectedItems.materials.length > 0 && selectedItems.materials.length < (materials?.items.length || 0)}
                checked={selectedItems.materials.length > 0 && selectedItems.materials.length === (materials?.items.length || 0)}
                onChange={handleSelectAll}
              />
            </TableCell>
            <TableCell>Material</TableCell>
            <TableCell>Category</TableCell>
            <TableCell>Supplier</TableCell>
            <TableCell>Approval Status</TableCell>
            <TableCell>Allergens</TableCell>
            <TableCell>Storage Conditions</TableCell>
            <TableCell>Shelf Life</TableCell>
            <TableCell>Created</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {materialsLoading ? (
            <TableRow>
              <TableCell colSpan={10} align="center">
                <LinearProgress />
                <Typography sx={{ mt: 1 }}>Loading materials...</Typography>
              </TableCell>
            </TableRow>
          ) : materials?.items.length === 0 ? (
            <TableRow>
              <TableCell colSpan={10} align="center">
                <Typography variant="body2" color="text.secondary">
                  No materials found
                </Typography>
              </TableCell>
            </TableRow>
          ) : (
            materials?.items.map((material) => (
              <TableRow key={material.id} hover>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedItems.materials.includes(material.id)}
                    onChange={() => handleSelectMaterial(material.id)}
                  />
                </TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {material.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {material.material_code}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={getCategoryDisplayName(material.category)}
                    size="small"
                    icon={getCategoryIcon(material.category)}
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold">
                    {material.supplier_name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <EnhancedStatusChip
                    status={material.approval_status as any}
                    label={getApprovalStatusDisplayName(material.approval_status)}
                  />
                </TableCell>
                <TableCell>
                  {material.allergens.length > 0 ? (
                    <Box display="flex" gap={0.5} flexWrap="wrap">
                      {material.allergens.slice(0, 2).map((allergen, index) => (
                        <Chip
                          key={index}
                          label={allergen}
                          size="small"
                          variant="outlined"
                          icon={<Allergen />}
                        />
                      ))}
                      {material.allergens.length > 2 && (
                        <Chip
                          label={`+${material.allergens.length - 2}`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      None
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Typography variant="body2" noWrap>
                    {material.storage_conditions}
                  </Typography>
                </TableCell>
                <TableCell>
                  {material.shelf_life_days ? (
                    <Typography variant="body2">
                      {material.shelf_life_days} days
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Not specified
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {format(parseISO(material.created_at), 'MMM dd, yyyy')}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Box display="flex" gap={1} justifyContent="center">
                    <Tooltip title="View Details">
                      <IconButton
                        size="small"
                        onClick={() => onViewMaterial?.(material)}
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit Material">
                      <IconButton
                        size="small"
                        onClick={() => onEditMaterial?.(material)}
                      >
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    {material.approval_status === 'pending' && (
                      <>
                        <Tooltip title="Approve Material">
                          <IconButton
                            size="small"
                            color="success"
                            onClick={() => handleApproveMaterial(material)}
                          >
                            <CheckCircle />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Reject Material">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleRejectMaterial(material)}
                          >
                            <Cancel />
                          </IconButton>
                        </Tooltip>
                      </>
                    )}
                    <Tooltip title="Delete Material">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteMaterial(material.id)}
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
      {materials && (
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={materials.total}
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
      {materialsLoading ? (
        <Grid item xs={12}>
          <Box display="flex" justifyContent="center" p={3}>
            <LinearProgress sx={{ width: '100%' }} />
          </Box>
        </Grid>
      ) : materials?.items.length === 0 ? (
        <Grid item xs={12}>
          <Box display="flex" justifyContent="center" p={3}>
            <Typography variant="body2" color="text.secondary">
              No materials found
            </Typography>
          </Box>
        </Grid>
      ) : (
        materials?.items.map((material) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={material.id}>
            <EnhancedCard title={material.name || 'Material'}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Box>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      {material.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {material.material_code}
                    </Typography>
                  </Box>
                  <Checkbox
                    checked={selectedItems.materials.includes(material.id)}
                    onChange={() => handleSelectMaterial(material.id)}
                  />
                </Box>

                <Box display="flex" flexDirection="column" gap={1} mb={2}>
                  <Chip
                    label={getCategoryDisplayName(material.category)}
                    size="small"
                    icon={getCategoryIcon(material.category)}
                  />
                  <Typography variant="body2" fontWeight="bold">
                    {material.supplier_name}
                  </Typography>
                  <EnhancedStatusChip
                    status={material.approval_status as any}
                    label={getApprovalStatusDisplayName(material.approval_status)}
                  />
                </Box>

                {material.allergens.length > 0 && (
                  <Box mb={2}>
                    <Typography variant="body2" fontWeight="bold" gutterBottom>
                      Allergens:
                    </Typography>
                    <Box display="flex" gap={0.5} flexWrap="wrap">
                      {material.allergens.slice(0, 3).map((allergen, index) => (
                        <Chip
                          key={index}
                          label={allergen}
                          size="small"
                          variant="outlined"
                          icon={<Allergen />}
                        />
                      ))}
                      {material.allergens.length > 3 && (
                        <Chip
                          label={`+${material.allergens.length - 3}`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </Box>
                )}

                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">Storage:</Typography>
                  <Typography variant="body2" color="text.secondary" noWrap>
                    {material.storage_conditions}
                  </Typography>
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Shelf Life:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {material.shelf_life_days ? `${material.shelf_life_days} days` : 'Not specified'}
                  </Typography>
                </Box>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  startIcon={<Visibility />}
                  onClick={() => onViewMaterial?.(material)}
                >
                  View
                </Button>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => onEditMaterial?.(material)}
                >
                  Edit
                </Button>
                {material.approval_status === 'pending' && (
                  <>
                    <Button
                      size="small"
                      color="success"
                      startIcon={<CheckCircle />}
                      onClick={() => handleApproveMaterial(material)}
                    >
                      Approve
                    </Button>
                    <Button
                      size="small"
                      color="error"
                      startIcon={<Cancel />}
                      onClick={() => handleRejectMaterial(material)}
                    >
                      Reject
                    </Button>
                  </>
                )}
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDeleteMaterial(material.id)}
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
            Material Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage materials, specifications, and approval workflows
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
            onClick={onCreateMaterial}
          >
            New Material
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {materialsError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => {}}>
          {materialsError}
        </Alert>
      )}

      {/* Search and Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search materials..."
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
              <InputLabel>Approval Status</InputLabel>
              <Select
                value={filterApprovalStatus}
                label="Approval Status"
                onChange={(e) => setFilterApprovalStatus(e.target.value)}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="approved">Approved</MenuItem>
                <MenuItem value="rejected">Rejected</MenuItem>
                <MenuItem value="under_review">Under Review</MenuItem>
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
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Allergens</InputLabel>
                  <Select
                    multiple
                    value={filterAllergens}
                    label="Allergens"
                    onChange={(e) => setFilterAllergens(e.target.value as string[])}
                  >
                    <MenuItem value="milk">Milk</MenuItem>
                    <MenuItem value="eggs">Eggs</MenuItem>
                    <MenuItem value="fish">Fish</MenuItem>
                    <MenuItem value="shellfish">Shellfish</MenuItem>
                    <MenuItem value="tree_nuts">Tree Nuts</MenuItem>
                    <MenuItem value="peanuts">Peanuts</MenuItem>
                    <MenuItem value="wheat">Wheat</MenuItem>
                    <MenuItem value="soybeans">Soybeans</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={3}>
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
      {selectedItems.materials.length > 0 && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="body2">
              {selectedItems.materials.length} material(s) selected
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
                onClick={() => dispatch(setSelectedMaterials([]))}
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
              <MenuItem value="approve">Approve Materials</MenuItem>
              <MenuItem value="reject">Reject Materials</MenuItem>
              <MenuItem value="export">Export Materials</MenuItem>
              <MenuItem value="archive">Archive Materials</MenuItem>
            </Select>
          </FormControl>
          {bulkAction === 'approve' && (
            <TextField
              fullWidth
              label="Approval Comments"
              multiline
              rows={3}
              value={approvalComments}
              onChange={(e) => setApprovalComments(e.target.value)}
              sx={{ mt: 2 }}
            />
          )}
          {bulkAction === 'reject' && (
            <TextField
              fullWidth
              label="Rejection Reason"
              multiline
              rows={3}
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              sx={{ mt: 2 }}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkActionDialog(false)}>Cancel</Button>
          <Button onClick={handleBulkAction} variant="contained">
            Apply
          </Button>
        </DialogActions>
      </Dialog>

      {/* Approval Dialog */}
      <Dialog open={approvalDialog} onClose={() => setApprovalDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {approvalComments ? 'Approve Material' : rejectionReason ? 'Reject Material' : 'Material Action'}
        </DialogTitle>
        <DialogContent>
          {selectedMaterial && (
            <Box mb={2}>
              <Typography variant="subtitle1" fontWeight="bold">
                {selectedMaterial.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {selectedMaterial.material_code}
              </Typography>
            </Box>
          )}
          <TextField
            fullWidth
            label={approvalComments ? "Approval Comments" : "Rejection Reason"}
            multiline
            rows={4}
            value={approvalComments || rejectionReason}
            onChange={(e) => {
              if (approvalComments !== undefined) {
                setApprovalComments(e.target.value);
              } else {
                setRejectionReason(e.target.value);
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApprovalDialog(false)}>Cancel</Button>
          <Button onClick={handleApprovalSubmit} variant="contained">
            {approvalComments ? 'Approve' : 'Reject'}
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

export default MaterialList; 