import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
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
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Skeleton,
  Tooltip,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Security,
  Warning,
  CheckCircle,
  Error,
  Refresh,
  Science,
  Verified,
  Monitor,
  BugReport,
  Timeline,
} from '@mui/icons-material';
import { haccpAPI } from '../services/api';

interface Product {
  id: number;
  product_code: string;
  name: string;
  description?: string;
  category?: string;
  haccp_plan_approved: boolean;
  haccp_plan_version?: string;
  ccp_count: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

const HACCP: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Dialog states
  const [openProductDialog, setOpenProductDialog] = useState(false);
  
  // Form data
  const [productForm, setProductForm] = useState({
    product_code: '',
    name: '',
    description: '',
    category: '',
    formulation: '',
    allergens: '',
    shelf_life_days: '',
    storage_conditions: '',
    packaging_type: '',
  });

  // Dashboard data
  const [dashboardData, setDashboardData] = useState({
    total_products: 0,
    approved_plans: 0,
    total_ccps: 0,
    active_ccps: 0,
    out_of_spec_count: 0,
    recent_logs: [],
  });

  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await haccpAPI.getProducts({
        search: searchTerm || undefined,
      });
      
      if (response.success) {
        setProducts(response.data.items);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load products');
      console.error('HACCP error:', err);
    } finally {
      setLoading(false);
    }
  }, [searchTerm]);

  const fetchDashboard = useCallback(async () => {
    try {
      const response = await haccpAPI.getDashboard();
      if (response.success) {
        setDashboardData(response.data);
      }
    } catch (err: any) {
      console.error('Dashboard error:', err);
    }
  }, []);

  useEffect(() => {
    fetchProducts();
    fetchDashboard();
  }, [fetchProducts, fetchDashboard]);

  const handleCreateProduct = async () => {
    try {
      const response = await haccpAPI.createProduct(productForm);
      if (response.success) {
        setSuccess('Product created successfully');
        setOpenProductDialog(false);
        setProductForm({
          product_code: '',
          name: '',
          description: '',
          category: '',
          formulation: '',
          allergens: '',
          shelf_life_days: '',
          storage_conditions: '',
          packaging_type: '',
        });
        fetchProducts();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create product');
    }
  };

  const handleCloseSnackbar = () => {
    setError(null);
    setSuccess(null);
  };

  return (
    <Box p={3}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            HACCP Plans
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Hazard Analysis and Critical Control Points Management
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenProductDialog(true)}
          size="large"
        >
          New Product
        </Button>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={handleCloseSnackbar}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={handleCloseSnackbar}>
          {success}
        </Alert>
      )}

      {/* Dashboard Statistics */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Products
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData.total_products}
                  </Typography>
                </Box>
                <Science color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Approved Plans
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData.approved_plans}
                  </Typography>
                </Box>
                <Verified color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active CCPs
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData.active_ccps}
                  </Typography>
                </Box>
                <Monitor color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Out of Spec
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData.out_of_spec_count}
                  </Typography>
                </Box>
                <Warning color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
          <TextField
            label="Search products"
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ minWidth: 200 }}
          />

          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchProducts}
            size="small"
          >
            Refresh
          </Button>
        </Box>
      </Paper>

      {/* Products Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Product Code</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>HACCP Status</TableCell>
                <TableCell>CCPs</TableCell>
                <TableCell>Created By</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                Array.from({ length: rowsPerPage }).map((_, index) => (
                  <TableRow key={index}>
                    <TableCell><Skeleton variant="text" width="80%" /></TableCell>
                    <TableCell><Skeleton variant="text" width="90%" /></TableCell>
                    <TableCell><Skeleton variant="text" width="60%" /></TableCell>
                    <TableCell><Skeleton variant="rectangular" width={60} height={24} sx={{ borderRadius: 1 }} /></TableCell>
                    <TableCell><Skeleton variant="text" width="40%" /></TableCell>
                    <TableCell><Skeleton variant="text" width="70%" /></TableCell>
                    <TableCell><Skeleton variant="text" width="60%" /></TableCell>
                    <TableCell><Skeleton variant="circular" width={32} height={32} /></TableCell>
                  </TableRow>
                ))
              ) : products.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                      No products found
                    </Typography>
                    <Button
                      variant="outlined"
                      startIcon={<Add />}
                      onClick={() => setOpenProductDialog(true)}
                      sx={{ mt: 2 }}
                    >
                      Create First Product
                    </Button>
                  </TableCell>
                </TableRow>
              ) : (
                products.map((product) => (
                  <TableRow key={product.id} hover>
                    <TableCell>{product.product_code}</TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {product.name}
                        </Typography>
                        {product.description && (
                          <Typography variant="caption" color="text.secondary">
                            {product.description.substring(0, 50)}...
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>{product.category}</TableCell>
                    <TableCell>
                      <Chip
                        label={product.haccp_plan_approved ? 'Approved' : 'Draft'}
                        color={product.haccp_plan_approved ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Security color="primary" fontSize="small" />
                        <Typography variant="body2">
                          {product.ccp_count} CCPs
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{product.created_by}</TableCell>
                    <TableCell>
                      {new Date(product.updated_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="View Details">
                        <IconButton size="small">
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Add Process Flow">
                        <IconButton size="small">
                          <Timeline />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Add Hazard">
                        <IconButton size="small">
                          <BugReport />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Add CCP">
                        <IconButton size="small">
                          <Security />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={products.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Paper>

      {/* Product Creation Dialog */}
      <Dialog open={openProductDialog} onClose={() => setOpenProductDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Product</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} pt={1}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Product Code"
                  fullWidth
                  value={productForm.product_code}
                  onChange={(e) => setProductForm({ ...productForm, product_code: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Product Name"
                  fullWidth
                  value={productForm.name}
                  onChange={(e) => setProductForm({ ...productForm, name: e.target.value })}
                  required
                />
              </Grid>
            </Grid>
            
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={productForm.description}
              onChange={(e) => setProductForm({ ...productForm, description: e.target.value })}
            />
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={productForm.category}
                    label="Category"
                    onChange={(e) => setProductForm({ ...productForm, category: e.target.value })}
                  >
                    <MenuItem value="milk">Milk</MenuItem>
                    <MenuItem value="yogurt">Yogurt</MenuItem>
                    <MenuItem value="cheese">Cheese</MenuItem>
                    <MenuItem value="butter">Butter</MenuItem>
                    <MenuItem value="cream">Cream</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Packaging Type"
                  fullWidth
                  value={productForm.packaging_type}
                  onChange={(e) => setProductForm({ ...productForm, packaging_type: e.target.value })}
                />
              </Grid>
            </Grid>
            
            <TextField
              label="Formulation"
              fullWidth
              multiline
              rows={2}
              value={productForm.formulation}
              onChange={(e) => setProductForm({ ...productForm, formulation: e.target.value })}
              placeholder="List ingredients and proportions..."
            />
            
            <TextField
              label="Allergens"
              fullWidth
              value={productForm.allergens}
              onChange={(e) => setProductForm({ ...productForm, allergens: e.target.value })}
              placeholder="e.g., Milk, Soy, Nuts..."
            />
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Shelf Life (days)"
                  fullWidth
                  type="number"
                  value={productForm.shelf_life_days}
                  onChange={(e) => setProductForm({ ...productForm, shelf_life_days: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Storage Conditions"
                  fullWidth
                  value={productForm.storage_conditions}
                  onChange={(e) => setProductForm({ ...productForm, storage_conditions: e.target.value })}
                  placeholder="e.g., Refrigerated at 2-4°C"
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenProductDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateProduct} variant="contained">
            Create Product
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HACCP; 