import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Stack,
  Alert,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  ExpandMore,
  Security,
  Warning,
  CheckCircle,
  Add,
  Edit,
  Science,
  Delete,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { AppDispatch, RootState } from '../store';
import {
  fetchProducts,
  fetchProduct,
  createProduct,
  updateProduct,
  deleteProduct,
  createProcessFlow,
  createHazard,
  createCCP,
  fetchDashboard,
  setSelectedProduct,
  setSelectedCCP,
  setSelectedHazard,
  clearError,
} from '../store/slices/haccpSlice';
import { hasRole, isSystemAdministrator } from '../store/slices/authSlice';
import PageHeader from '../components/UI/PageHeader';
import StatusChip from '../components/UI/StatusChip';
import ProductDialog from '../components/HACCP/ProductDialog';

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
      id={`haccp-tabpanel-${index}`}
      aria-labelledby={`haccp-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const HACCP: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { user: currentUser } = useSelector((state: RootState) => state.auth);
  const { 
    products, 
    selectedProduct, 
    processFlows, 
    hazards, 
    ccps, 
    dashboardStats, 
    loading, 
    error 
  } = useSelector((state: RootState) => state.haccp);
  
  const [selectedTab, setSelectedTab] = useState(0);
  const [expanded, setExpanded] = useState<string | false>('panel1');
  const [productDialogOpen, setProductDialogOpen] = useState(false);
  const [processFlowDialogOpen, setProcessFlowDialogOpen] = useState(false);
  const [hazardDialogOpen, setHazardDialogOpen] = useState(false);
  const [ccpDialogOpen, setCcpDialogOpen] = useState(false);
  const [selectedProductForEdit, setSelectedProductForEdit] = useState<any>(null);

  // Role-based permissions
  const canManageHACCP = hasRole(currentUser, 'QA Manager') || 
                         hasRole(currentUser, 'QA Specialist') || 
                         isSystemAdministrator(currentUser);

  const canCreateProducts = hasRole(currentUser, 'QA Manager') || 
                           isSystemAdministrator(currentUser);

  useEffect(() => {
    loadDashboard();
    loadProducts();
  }, [dispatch]);

  const loadDashboard = () => {
    dispatch(fetchDashboard());
  };

  const loadProducts = () => {
    dispatch(fetchProducts());
  };

  const loadProductDetails = (productId: number) => {
    dispatch(fetchProduct(productId));
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const handleProductSelect = (product: any) => {
    dispatch(setSelectedProduct(product));
    loadProductDetails(product.id);
  };

  const handleDeleteProduct = async (productId: number) => {
    if (!window.confirm('Are you sure you want to delete this product?')) {
      return;
    }
    try {
      await dispatch(deleteProduct(productId)).unwrap();
      loadProducts();
    } catch (error) {
      console.error('Failed to delete product:', error);
    }
  };



  const getRiskLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };



  const getHazardTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'biological': return <Science />;
      case 'chemical': return <Warning />;
      case 'physical': return <Security />;
      case 'allergen': return <Warning />;
      default: return <Security />;
    }
  };

  const renderDashboard = () => (
    <Box>
      <Grid container spacing={3}>
        {/* Statistics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Products
              </Typography>
              <Typography variant="h4">
                {dashboardStats?.total_products || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Approved Plans
              </Typography>
              <Typography variant="h4">
                {dashboardStats?.approved_plans || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total CCPs
              </Typography>
              <Typography variant="h4">
                {dashboardStats?.total_ccps || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active CCPs
              </Typography>
              <Typography variant="h4">
                {dashboardStats?.active_ccps || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Recent Activity" />
            <CardContent>
              <List>
                {dashboardStats?.recent_logs?.slice(0, 5).map((log: any, index: number) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <CheckCircle color="success" />
                    </ListItemIcon>
                    <ListItemText
                      primary={log.description}
                      secondary={new Date(log.created_at).toLocaleDateString()}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Alerts */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Out of Specification" />
            <CardContent>
              <Alert severity="warning">
                {dashboardStats?.out_of_spec_count || 0} CCPs out of specification
              </Alert>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderProducts = () => (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">Products</Typography>
        {canCreateProducts && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setProductDialogOpen(true)}
          >
            Add Product
          </Button>
        )}
      </Box>

      <Grid container spacing={3}>
        {products.map((product) => (
          <Grid item xs={12} sm={6} md={4} key={product.id}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                '&:hover': { boxShadow: 3 }
              }}
              onClick={() => handleProductSelect(product)}
            >
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {product.name}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  {product.product_code}
                </Typography>
                <Typography variant="body2" paragraph>
                  {product.description}
                </Typography>
                <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                  <Chip
                    label={product.haccp_plan_approved ? 'Approved' : 'Pending'}
                    color={product.haccp_plan_approved ? 'success' : 'warning'}
                    size="small"
                  />
                  <Chip
                    label={`${product.ccp_count} CCPs`}
                    color="primary"
                    size="small"
                  />
                </Stack>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" color="textSecondary">
                    Created by {product.created_by}
                  </Typography>
                  {canManageHACCP && (
                    <Box>
                      <IconButton size="small" onClick={(e) => {
                        e.stopPropagation();
                        setSelectedProductForEdit(product);
                        setProductDialogOpen(true);
                      }}>
                        <Edit />
                      </IconButton>
                      <IconButton size="small" onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteProduct(product.id);
                      }}>
                        <Delete />
                      </IconButton>
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderProductDetails = () => {
    if (!selectedProduct) {
      return (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="textSecondary">
            Select a product to view details
          </Typography>
        </Box>
      );
    }

    return (
      <Box>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            {selectedProduct.name}
          </Typography>
          <Typography color="textSecondary" gutterBottom>
            {selectedProduct.product_code}
          </Typography>
          <Typography variant="body1" paragraph>
            {selectedProduct.description}
          </Typography>
          <Stack direction="row" spacing={2}>
            <Chip
              label={selectedProduct.haccp_plan_approved ? 'Plan Approved' : 'Plan Pending'}
              color={selectedProduct.haccp_plan_approved ? 'success' : 'warning'}
            />
            <Chip
              label={`${ccps.length} CCPs`}
              color="primary"
            />
            <Chip
              label={`${hazards.length} Hazards`}
              color="secondary"
            />
          </Stack>
        </Box>

        <Tabs value={selectedTab} onChange={handleTabChange}>
          <Tab label="Process Flow" />
          <Tab label="Hazards" />
          <Tab label="CCPs" />
          <Tab label="Monitoring" />
        </Tabs>

        <TabPanel value={selectedTab} index={0}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Process Flow</Typography>
            {canManageHACCP && (
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setProcessFlowDialogOpen(true)}
              >
                Add Step
              </Button>
            )}
          </Box>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Step</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Equipment</TableCell>
                  <TableCell>Temperature</TableCell>
                  <TableCell>Time</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {processFlows.map((flow) => (
                  <TableRow key={flow.id}>
                    <TableCell>{flow.step_number}</TableCell>
                    <TableCell>{flow.step_name}</TableCell>
                    <TableCell>{flow.equipment}</TableCell>
                    <TableCell>{flow.temperature}°C</TableCell>
                    <TableCell>{flow.time_minutes} min</TableCell>
                    <TableCell>
                      {canManageHACCP && (
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={selectedTab} index={1}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Hazards</Typography>
            {canManageHACCP && (
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setHazardDialogOpen(true)}
              >
                Add Hazard
              </Button>
            )}
          </Box>
          <Grid container spacing={2}>
            {hazards.map((hazard) => (
              <Grid item xs={12} sm={6} md={4} key={hazard.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      {getHazardTypeIcon(hazard.hazard_type)}
                      <Typography variant="h6" sx={{ ml: 1 }}>
                        {hazard.hazard_name}
                      </Typography>
                    </Box>
                    <Typography color="textSecondary" gutterBottom>
                      {hazard.hazard_type}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      {hazard.description}
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                      <Chip
                        label={`Risk: ${hazard.risk_level}`}
                        color={getRiskLevelColor(hazard.risk_level) as any}
                        size="small"
                      />
                      <Chip
                        label={`Score: ${hazard.risk_score}`}
                        color="primary"
                        size="small"
                      />
                      {hazard.is_ccp && (
                        <Chip
                          label="CCP"
                          color="error"
                          size="small"
                        />
                      )}
                    </Stack>
                    {canManageHACCP && (
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={selectedTab} index={2}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Critical Control Points</Typography>
            {canManageHACCP && (
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setCcpDialogOpen(true)}
              >
                Add CCP
              </Button>
            )}
          </Box>
          <Grid container spacing={2}>
            {ccps.map((ccp) => (
              <Grid item xs={12} sm={6} md={4} key={ccp.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {ccp.ccp_name}
                    </Typography>
                    <Typography color="textSecondary" gutterBottom>
                      {ccp.ccp_number}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      {ccp.description}
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                      <StatusChip status={ccp.status} label={ccp.status} />
                    </Stack>
                    {ccp.critical_limit_min && ccp.critical_limit_max && (
                      <Typography variant="body2" color="textSecondary">
                        Limits: {ccp.critical_limit_min} - {ccp.critical_limit_max} {ccp.critical_limit_unit}
                      </Typography>
                    )}
                    {canManageHACCP && (
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={selectedTab} index={3}>
          <Typography variant="h6" gutterBottom>
            Monitoring & Verification
          </Typography>
          <Typography color="textSecondary">
            Monitoring and verification logs will be displayed here.
          </Typography>
        </TabPanel>
      </Box>
    );
  };

  if (!canManageHACCP) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          <Typography variant="h6">Access Denied</Typography>
          <Typography variant="body2">
            You don't have permission to access HACCP management. Please contact your system administrator.
          </Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <PageHeader
        title="HACCP Management"
        subtitle="Hazard Analysis and Critical Control Points"
        showAdd={canCreateProducts}
        onAdd={() => setProductDialogOpen(true)}
      />

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => dispatch(clearError())}>
          {error}
        </Alert>
      )}

      {loading && <CircularProgress sx={{ display: 'block', margin: '20px auto' }} />}

      <Tabs value={selectedTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Dashboard" />
        <Tab label="Products" />
        <Tab label="Product Details" />
      </Tabs>

      <TabPanel value={selectedTab} index={0}>
        {renderDashboard()}
      </TabPanel>

      <TabPanel value={selectedTab} index={1}>
        {renderProducts()}
      </TabPanel>

      <TabPanel value={selectedTab} index={2}>
        {renderProductDetails()}
      </TabPanel>

      {/* Dialogs */}
      <ProductDialog
        open={productDialogOpen}
        onClose={() => setProductDialogOpen(false)}
        product={selectedProductForEdit}
      />
    </Box>
  );
};

export default HACCP; 