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
  TextField,
  FormControlLabel,
  Switch,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
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
import { useLocation, useNavigate } from 'react-router-dom';
import { AppDispatch, RootState } from '../store';
import {
  fetchProducts,
  fetchProduct,
  createProduct,
  updateProduct,
  deleteProduct,
  createProcessFlow,
  updateProcessFlow,
  deleteProcessFlow,
  createHazard,
  updateHazard,
  deleteHazard,
  createCCP,
  updateCCP,
  deleteCCP,
  fetchDashboard,
  setSelectedProduct,
  setSelectedCCP,
  setSelectedHazard,
  clearError,
} from '../store/slices/haccpSlice';
import { hasRole, isSystemAdministrator } from '../store/slices/authSlice';
import { Autocomplete } from '@mui/material';
import { usersAPI } from '../services/api';
import PageHeader from '../components/UI/PageHeader';
import StatusChip from '../components/UI/StatusChip';
import ProductDialog from '../components/HACCP/ProductDialog';
import HACCPFlowchartBuilder from '../components/HACCP/FlowchartBuilder';

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
  const navigate = useNavigate();
  const location = useLocation();
  const [expanded, setExpanded] = useState<string | false>('panel1');
  const [productDialogOpen, setProductDialogOpen] = useState(false);
  const [processFlowDialogOpen, setProcessFlowDialogOpen] = useState(false);
  const [hazardDialogOpen, setHazardDialogOpen] = useState(false);
  const [ccpDialogOpen, setCcpDialogOpen] = useState(false);
  const [selectedProductForEdit, setSelectedProductForEdit] = useState<any>(null);
  const [selectedFlow, setSelectedFlow] = useState<any>(null);
  const [selectedHazardItem, setSelectedHazardItem] = useState<any>(null);
  const [selectedCcpItem, setSelectedCcpItem] = useState<any>(null);
  const [flowchartBuilderOpen, setFlowchartBuilderOpen] = useState(false);
  const [selectedProductForFlowchart, setSelectedProductForFlowchart] = useState<any>(null);
  const [flowForm, setFlowForm] = useState({
    step_number: '',
    step_name: '',
    description: '',
    equipment: '',
    temperature: '',
    time_minutes: '',
    ph: '',
    aw: '',
  });
  const [hazardForm, setHazardForm] = useState({
    process_step_id: '',
    hazard_type: 'BIOLOGICAL',
    hazard_name: '',
    description: '',
    likelihood: '1',
    severity: '1',
    control_measures: '',
    is_controlled: false as boolean,
    control_effectiveness: '',
    is_ccp: false as boolean,
    ccp_justification: '',
  });
  const [ccpForm, setCcpForm] = useState({
    hazard_id: '',
    ccp_number: '',
    ccp_name: '',
    description: '',
    critical_limit_min: '',
    critical_limit_max: '',
    critical_limit_unit: '',
    monitoring_frequency: '',
    monitoring_method: '',
    monitoring_responsible: '',
    monitoring_equipment: '',
    corrective_actions: '',
    verification_frequency: '',
    verification_method: '',
    verification_responsible: '',
  });
  const [userSearch, setUserSearch] = useState('');
  const [userOptions, setUserOptions] = useState<Array<{ id: number; username: string; full_name?: string }>>([]);
  const [userOpen, setUserOpen] = useState(false);
  const [monitoringUserValue, setMonitoringUserValue] = useState<{ id: number; username: string; full_name?: string } | null>(null);
  const [verificationUserValue, setVerificationUserValue] = useState<{ id: number; username: string; full_name?: string } | null>(null);
  useEffect(() => {
    let active = true;
    // Only search when dropdown is open and the user typed at least 2 characters
    if (!userOpen || (userSearch || '').trim().length < 2) {
      return () => { active = false; };
    }
    const t = setTimeout(async () => {
      try {
        const resp: any = await usersAPI.getUsers({ page: 1, size: 10, search: userSearch });
        const items = (resp?.data?.items || resp?.items || []) as Array<any>;
        if (active) setUserOptions(items.map((u) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch {
        if (active) setUserOptions([]);
      }
    }, 300);
    return () => { active = false; clearTimeout(t); };
  }, [userSearch, userOpen]);

  // Ensure selected user value remains stable even when options refresh
  useEffect(() => {
    const setupSelectedUsers = async () => {
      try {
        if (ccpForm.monitoring_responsible) {
          const idNum = Number(ccpForm.monitoring_responsible);
          if (!monitoringUserValue || monitoringUserValue.id !== idNum) {
            const res: any = await usersAPI.getUser(idNum);
            const u = res?.data || res;
            if (u?.id) setMonitoringUserValue({ id: u.id, username: u.username, full_name: u.full_name });
          }
        } else {
          setMonitoringUserValue(null);
        }
        if (ccpForm.verification_responsible) {
          const idNum = Number(ccpForm.verification_responsible);
          if (!verificationUserValue || verificationUserValue.id !== idNum) {
            const res: any = await usersAPI.getUser(idNum);
            const u = res?.data || res;
            if (u?.id) setVerificationUserValue({ id: u.id, username: u.username, full_name: u.full_name });
          }
        } else {
          setVerificationUserValue(null);
        }
      } catch {}
    };
    setupSelectedUsers();
    // We intentionally depend on the stored ids only
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ccpForm.monitoring_responsible, ccpForm.verification_responsible]);
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
    haccp_plan_approved: false as boolean,
    haccp_plan_version: '',
  });

  const handleInputChange = (key: keyof typeof productForm) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setProductForm(prev => ({ ...prev, [key]: e.target.value }));
  };

  const handleBooleanChange = (key: keyof typeof productForm) => (
    _e: React.ChangeEvent<HTMLInputElement>,
    checked: boolean,
  ) => {
    setProductForm(prev => ({ ...prev, [key]: checked }));
  };

  const handleOpenFlowchartBuilder = (product: any) => {
    setSelectedProductForFlowchart(product);
    setFlowchartBuilderOpen(true);
  };

  const handleCloseFlowchartBuilder = () => {
    setFlowchartBuilderOpen(false);
    setSelectedProductForFlowchart(null);
  };

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

  // Read ?tab= from URL to jump to details
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tabParam = params.get('tab');
    if (tabParam === 'details') {
      setSelectedTab(1);
    } else if (tabParam === 'products') {
      setSelectedTab(1);
    } else if (tabParam === 'dashboard') {
      setSelectedTab(0);
    }
  }, [location.search]);

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

  const handleDeleteFlow = async (flowId: number) => {
    if (!window.confirm('Delete this process step?')) return;
    try {
      await dispatch(deleteProcessFlow(flowId)).unwrap();
      if (selectedProduct) loadProductDetails(selectedProduct.id);
    } catch (e) { /* noop */ }
  };

  const handleDeleteHazard = async (hazardId: number) => {
    if (!window.confirm('Delete this hazard?')) return;
    try {
      await dispatch(deleteHazard(hazardId)).unwrap();
      if (selectedProduct) loadProductDetails(selectedProduct.id);
    } catch (e) { /* noop */ }
  };

  const handleDeleteCCP = async (ccpId: number) => {
    if (!window.confirm('Delete this CCP?')) return;
    try {
      await dispatch(deleteCCP(ccpId)).unwrap();
      if (selectedProduct) loadProductDetails(selectedProduct.id);
    } catch (e) { /* noop */ }
  };

  // Populate flow/hazard/ccp forms on selection
  useEffect(() => {
    if (selectedFlow) {
      setFlowForm({
        step_number: String(selectedFlow.step_number ?? ''),
        step_name: selectedFlow.step_name || '',
        description: selectedFlow.description || '',
        equipment: selectedFlow.equipment || '',
        temperature: String(selectedFlow.temperature ?? ''),
        time_minutes: String(selectedFlow.time_minutes ?? ''),
        ph: String(selectedFlow.ph ?? ''),
        aw: String(selectedFlow.aw ?? ''),
      });
    } else {
      setFlowForm({ step_number: '', step_name: '', description: '', equipment: '', temperature: '', time_minutes: '', ph: '', aw: '' });
    }
  }, [selectedFlow]);

  useEffect(() => {
    if (selectedHazardItem) {
      setHazardForm({
        process_step_id: String(selectedHazardItem.process_step_id ?? ''),
        hazard_type: selectedHazardItem.hazard_type || 'BIOLOGICAL',
        hazard_name: selectedHazardItem.hazard_name || '',
        description: selectedHazardItem.description || '',
        likelihood: String(selectedHazardItem.likelihood ?? '1'),
        severity: String(selectedHazardItem.severity ?? '1'),
        control_measures: selectedHazardItem.control_measures || '',
        is_controlled: !!selectedHazardItem.is_controlled,
        control_effectiveness: String(selectedHazardItem.control_effectiveness ?? ''),
        is_ccp: !!selectedHazardItem.is_ccp,
        ccp_justification: selectedHazardItem.ccp_justification || '',
      });
    } else {
      setHazardForm({ process_step_id: '', hazard_type: 'BIOLOGICAL', hazard_name: '', description: '', likelihood: '1', severity: '1', control_measures: '', is_controlled: false, control_effectiveness: '', is_ccp: false, ccp_justification: '' });
    }
  }, [selectedHazardItem]);

  useEffect(() => {
    if (selectedCcpItem) {
      setCcpForm({
        hazard_id: String(selectedCcpItem.hazard_id ?? ''),
        ccp_number: selectedCcpItem.ccp_number || '',
        ccp_name: selectedCcpItem.ccp_name || '',
        description: selectedCcpItem.description || '',
        critical_limit_min: String(selectedCcpItem.critical_limit_min ?? ''),
        critical_limit_max: String(selectedCcpItem.critical_limit_max ?? ''),
        critical_limit_unit: selectedCcpItem.critical_limit_unit || '',
        monitoring_frequency: selectedCcpItem.monitoring_frequency || '',
        monitoring_method: selectedCcpItem.monitoring_method || '',
        monitoring_responsible: String(selectedCcpItem.monitoring_responsible ?? ''),
        monitoring_equipment: selectedCcpItem.monitoring_equipment || '',
        corrective_actions: selectedCcpItem.corrective_actions || '',
        verification_frequency: selectedCcpItem.verification_frequency || '',
        verification_method: selectedCcpItem.verification_method || '',
        verification_responsible: String(selectedCcpItem.verification_responsible ?? ''),
      });
    } else {
      setCcpForm({ hazard_id: '', ccp_number: '', ccp_name: '', description: '', critical_limit_min: '', critical_limit_max: '', critical_limit_unit: '', monitoring_frequency: '', monitoring_method: '', monitoring_responsible: '', monitoring_equipment: '', corrective_actions: '', verification_frequency: '', verification_method: '', verification_responsible: '' });
    }
  }, [selectedCcpItem]);

  const handleSaveFlow = async () => {
    if (!selectedProduct) return;
    
    // Validate required fields
    if (!flowForm.step_number || flowForm.step_number === '') {
      alert('Step number is required');
      return;
    }
    if (!flowForm.step_name || flowForm.step_name.trim() === '') {
      alert('Step name is required');
      return;
    }
    
    const payload: any = {
      step_number: Number(flowForm.step_number),
      step_name: flowForm.step_name.trim(),
      description: flowForm.description,
      equipment: flowForm.equipment,
      temperature: flowForm.temperature === '' ? null : Number(flowForm.temperature),
      time_minutes: flowForm.time_minutes === '' ? null : Number(flowForm.time_minutes),
      ph: flowForm.ph === '' ? null : Number(flowForm.ph),
      aw: flowForm.aw === '' ? null : Number(flowForm.aw),
    };
    try {
      if (selectedFlow) {
        await dispatch(updateProcessFlow({ flowId: selectedFlow.id, flowData: payload })).unwrap();
      } else {
        await dispatch(createProcessFlow({ productId: selectedProduct.id, flowData: payload })).unwrap();
      }
      setProcessFlowDialogOpen(false);
      setSelectedFlow(null);
      loadProductDetails(selectedProduct.id);
    } catch (e) { /* noop */ }
  };

  const handleSaveHazard = async () => {
    if (!selectedProduct) return;
    
    // Validate required fields
    if (!hazardForm.process_step_id || hazardForm.process_step_id === '') {
      alert('Please select a process step');
      return;
    }
    
    if (!hazardForm.hazard_name || hazardForm.hazard_name.trim() === '') {
      alert('Please enter a hazard name');
      return;
    }
    
    const payload: any = {
      process_step_id: Number(hazardForm.process_step_id),
      hazard_type: hazardForm.hazard_type,
      hazard_name: hazardForm.hazard_name.trim(),
      description: hazardForm.description,
      likelihood: Number(hazardForm.likelihood),
      severity: Number(hazardForm.severity),
      control_measures: hazardForm.control_measures,
      is_controlled: hazardForm.is_controlled,
      control_effectiveness: hazardForm.control_effectiveness === '' ? null : Number(hazardForm.control_effectiveness),
      is_ccp: hazardForm.is_ccp,
      ccp_justification: hazardForm.ccp_justification,
    };
    try {
      if (selectedHazardItem) {
        await dispatch(updateHazard({ hazardId: selectedHazardItem.id, hazardData: payload })).unwrap();
      } else {
        await dispatch(createHazard({ productId: selectedProduct.id, hazardData: payload })).unwrap();
      }
      setHazardDialogOpen(false);
      setSelectedHazardItem(null);
      loadProductDetails(selectedProduct.id);
    } catch (e) { /* noop */ }
  };

  const handleSaveCCP = async () => {
    if (!selectedProduct) return;
    const payload: any = {
      hazard_id: ccpForm.hazard_id === '' ? null : Number(ccpForm.hazard_id),
      ccp_number: ccpForm.ccp_number,
      ccp_name: ccpForm.ccp_name,
      description: ccpForm.description,
      critical_limit_min: ccpForm.critical_limit_min === '' ? null : Number(ccpForm.critical_limit_min),
      critical_limit_max: ccpForm.critical_limit_max === '' ? null : Number(ccpForm.critical_limit_max),
      critical_limit_unit: ccpForm.critical_limit_unit,
      monitoring_frequency: ccpForm.monitoring_frequency,
      monitoring_method: ccpForm.monitoring_method,
      monitoring_responsible: ccpForm.monitoring_responsible === '' ? null : Number(ccpForm.monitoring_responsible),
      monitoring_equipment: ccpForm.monitoring_equipment,
      corrective_actions: ccpForm.corrective_actions,
      verification_frequency: ccpForm.verification_frequency,
      verification_method: ccpForm.verification_method,
      verification_responsible: ccpForm.verification_responsible === '' ? null : Number(ccpForm.verification_responsible),
    };
    try {
      if (selectedCcpItem) {
        await dispatch(updateCCP({ ccpId: selectedCcpItem.id, ccpData: payload })).unwrap();
      } else {
        await dispatch(createCCP({ productId: selectedProduct.id, ccpData: payload })).unwrap();
      }
      setCcpDialogOpen(false);
      setSelectedCcpItem(null);
      loadProductDetails(selectedProduct.id);
    } catch (e) { /* noop */ }
  };

  // Populate form when editing
  useEffect(() => {
    if (selectedProductForEdit) {
      setProductForm({
        product_code: selectedProductForEdit.product_code || '',
        name: selectedProductForEdit.name || '',
        description: selectedProductForEdit.description || '',
        category: selectedProductForEdit.category || '',
        formulation: selectedProductForEdit.formulation || '',
        allergens: selectedProductForEdit.allergens || '',
        shelf_life_days: String(selectedProductForEdit.shelf_life_days ?? ''),
        storage_conditions: selectedProductForEdit.storage_conditions || '',
        packaging_type: selectedProductForEdit.packaging_type || '',
        haccp_plan_approved: !!selectedProductForEdit.haccp_plan_approved,
        haccp_plan_version: selectedProductForEdit.haccp_plan_version || '',
      });
    } else {
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
        haccp_plan_approved: false,
        haccp_plan_version: '',
      });
    }
  }, [selectedProductForEdit]);

  const handleSaveProduct = async () => {
    const payload: any = {
      ...productForm,
      shelf_life_days: productForm.shelf_life_days === '' ? null : Number(productForm.shelf_life_days),
    };
    try {
      if (selectedProductForEdit) {
        await dispatch(updateProduct({ productId: selectedProductForEdit.id, productData: payload })).unwrap();
      } else {
        await dispatch(createProduct(payload)).unwrap();
      }
      setProductDialogOpen(false);
      setSelectedProductForEdit(null);
      loadProducts();
    } catch (e) {
      console.error('Failed to save product', e);
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
              {Array.isArray(dashboardStats?.recent_logs) && dashboardStats!.recent_logs!.length > 0 ? (
                <List>
                  {dashboardStats!.recent_logs!.slice(0, 6).map((log: any, index: number) => {
                    const createdAt = (log.created_at && !isNaN(Date.parse(log.created_at)))
                      ? new Date(log.created_at).toLocaleString()
                      : '';
                    const type = (log.type || log.category || '').toString().toLowerCase();
                    const severity = (log.severity || log.level || '').toString().toLowerCase();
                    const StatusIcon =
                      type.includes('ccp') || type.includes('monitor') ? Warning :
                      type.includes('hazard') ? Security :
                      type.includes('product') ? Add :
                      CheckCircle;
                    const chipColor: any =
                      severity === 'high' || severity === 'critical' ? 'error' :
                      severity === 'medium' ? 'warning' :
                      severity === 'low' ? 'info' : 'default';
                    return (
                      <ListItem key={index} alignItems="flex-start" sx={{ py: 1 }}>
                        <ListItemIcon>
                          <StatusIcon color={chipColor === 'error' ? 'error' : chipColor === 'warning' ? 'warning' : chipColor === 'info' ? 'info' : 'success'} />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Stack direction="row" spacing={1} alignItems="center">
                              <Typography variant="body1" fontWeight={600}>{log.description || 'Activity'}</Typography>
                              {type && <Chip size="small" label={(type || 'update').toString().toUpperCase()} />}
                              {severity && <Chip size="small" color={chipColor} label={(severity || '').toString().toUpperCase()} />}
                            </Stack>
                          }
                          secondary={
                            <Typography variant="caption" color="textSecondary">
                              {createdAt}
                              {log.user ? ` • by ${log.user}` : ''}
                              {log.product_name ? ` • ${log.product_name}` : ''}
                            </Typography>
                          }
                        />
                      </ListItem>
                    );
                  })}
                </List>
              ) : (
                <Typography variant="body2" color="textSecondary">No recent activity</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Alerts */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Out of Specification" />
            <CardContent>
              {Array.isArray(dashboardStats?.out_of_spec_ccps) && dashboardStats!.out_of_spec_ccps!.length > 0 ? (
                <List>
                  {dashboardStats!.out_of_spec_ccps!.map((ccp) => (
                    <ListItem key={ccp.id} alignItems="flex-start">
                      <ListItemIcon>
                        <Warning color="warning" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${ccp.ccp_number || ''} ${ccp.ccp_name || ''}`.trim() || `CCP #${ccp.id}`}
                        secondary={
                          <>
                            <Typography variant="body2" color="textSecondary">
                              {ccp.process_step ? `Step: ${ccp.process_step} • ` : ''}
                              {ccp.measured_at && !isNaN(Date.parse(ccp.measured_at)) ? new Date(ccp.measured_at).toLocaleString() : ''}
                            </Typography>
                            <Typography variant="body2">
                              Measured: {ccp.measured_value}{ccp.unit ? ` ${ccp.unit}` : ''}
                              {typeof ccp.limit_min === 'number' || typeof ccp.limit_max === 'number' ?
                                ` • Limits: ${ccp.limit_min ?? '-'} to ${ccp.limit_max ?? '-'}` : ''}
                            </Typography>
                          </>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Alert severity="warning">
                  {dashboardStats?.out_of_spec_count || 0} CCPs out of specification
                </Alert>
              )}
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
              onClick={() => navigate(`/haccp/products/${product.id}`)}
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
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
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
                {/* Build HACCP Flowchart button removed as per UX guidance */}
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
                onClick={() => { setSelectedFlow(null); setProcessFlowDialogOpen(true); }}
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
                        <Stack direction="row" spacing={1}>
                          <IconButton size="small" onClick={() => { setSelectedFlow(flow); setProcessFlowDialogOpen(true); }}>
                          <Edit />
                        </IconButton>
                          <IconButton size="small" onClick={() => handleDeleteFlow(flow.id)}>
                            <Delete />
                          </IconButton>
                        </Stack>
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
                onClick={() => { setSelectedHazardItem(null); setHazardDialogOpen(true); }}
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
                        <IconButton size="small" onClick={() => { setSelectedHazardItem(hazard); setHazardDialogOpen(true); }}>
                          <Edit />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleDeleteHazard(hazard.id)}>
                          <Delete />
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
                onClick={() => { setSelectedCcpItem(null); setCcpDialogOpen(true); }}
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
                        <IconButton size="small" onClick={() => { setSelectedCcpItem(ccp); setCcpDialogOpen(true); }}>
                          <Edit />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleDeleteCCP(ccp.id)}>
                          <Delete />
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
          <Typography variant="h6" gutterBottom>Monitoring & Verification</Typography>
          <Stack spacing={2} sx={{ maxWidth: 700, mt: 1 }}>
            <Autocomplete
              options={ccps}
              getOptionLabel={(ccp: any) => `${ccp.ccp_number} - ${ccp.ccp_name}`}
              value={ccps.find((c: any) => String(c.id) === (ccpForm as any).monitor_ccp_id) || null}
              onChange={(_, val: any) => setCcpForm({ ...(ccpForm as any), monitor_ccp_id: val ? String(val.id) : '' })}
              isOptionEqualToValue={(opt: any, val: any) => opt.id === val.id}
              renderInput={(params) => <TextField {...params} label="Select CCP" placeholder="Choose CCP for monitoring" />}
            />
            <TextField label="Batch Number" value={(ccpForm as any).monitor_batch || ''} onChange={e => setCcpForm({ ...(ccpForm as any), monitor_batch: e.target.value })} />
            <TextField type="number" label="Measured Value" value={(ccpForm as any).monitor_value || ''} onChange={e => setCcpForm({ ...(ccpForm as any), monitor_value: e.target.value })} />
            <TextField label="Unit" value={(ccpForm as any).monitor_unit || ''} onChange={e => setCcpForm({ ...(ccpForm as any), monitor_unit: e.target.value })} />
            <Stack direction="row" spacing={2}>
              <Button variant="contained" disabled={!selectedProduct || !(ccpForm as any).monitor_ccp_id} onClick={async () => {
                const ccpId = Number((ccpForm as any).monitor_ccp_id);
                if (!ccpId) return;
                try {
                  // Use the API service instead of direct fetch
                  const api = (await import('../services/api')).api;
                  await api.post(`/haccp/ccps/${ccpId}/monitoring-logs/enhanced`, {
                    batch_number: (ccpForm as any).monitor_batch,
                    measured_value: Number((ccpForm as any).monitor_value),
                    unit: (ccpForm as any).monitor_unit,
                  });
                  const res = await api.get(`/nonconformance/haccp/recent-nc?ccp_id=${ccpId}&batch_number=${encodeURIComponent((ccpForm as any).monitor_batch || '')}`);
                  const data = res.data;
                  if (data?.found) {
                    window.open(`/nonconformance/${data.id}`, '_blank');
                  } else {
                    alert('Monitoring saved. No NC auto-created for this reading.');
                  }
                } catch (e) {
                  alert('Failed to create monitoring log');
                }
              }}>Record Monitoring Log</Button>
            </Stack>
            <Typography variant="body2" color="text.secondary">After saving, if out-of-spec, a Non-Conformance will be auto-created and opened.</Typography>
          </Stack>
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
      </Tabs>

      <TabPanel value={selectedTab} index={0}>
        {renderDashboard()}
      </TabPanel>

      <TabPanel value={selectedTab} index={1}>
        {renderProducts()}
      </TabPanel>

      

      {/* Dialogs for creating/editing products, process flows, hazards, and CCPs */}
      <Dialog open={productDialogOpen} onClose={() => { setProductDialogOpen(false); setSelectedProductForEdit(null); }} maxWidth="md" fullWidth>
        <DialogTitle>{selectedProductForEdit ? 'Edit Product' : 'Add Product'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Product Code"
                value={productForm.product_code}
                onChange={handleInputChange('product_code')}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Name"
                value={productForm.name}
                onChange={handleInputChange('name')}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={productForm.description}
                onChange={handleInputChange('description')}
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Category"
                value={productForm.category}
                onChange={handleInputChange('category')}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Formulation"
                value={productForm.formulation}
                onChange={handleInputChange('formulation')}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Allergens"
                value={productForm.allergens}
                onChange={handleInputChange('allergens')}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Shelf Life (days)"
                value={productForm.shelf_life_days}
                onChange={handleInputChange('shelf_life_days')}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Storage Conditions"
                value={productForm.storage_conditions}
                onChange={handleInputChange('storage_conditions')}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Packaging Type"
                value={productForm.packaging_type}
                onChange={handleInputChange('packaging_type')}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={productForm.haccp_plan_approved}
                    onChange={handleBooleanChange('haccp_plan_approved')}
                  />
                }
                label="HACCP Plan Approved"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="HACCP Plan Version"
                value={productForm.haccp_plan_version}
                onChange={handleInputChange('haccp_plan_version')}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setProductDialogOpen(false); setSelectedProductForEdit(null); }}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveProduct}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Process Flow Dialog */}
      <Dialog open={processFlowDialogOpen} onClose={() => { setProcessFlowDialogOpen(false); setSelectedFlow(null); }} maxWidth="md" fullWidth>
        <DialogTitle>{selectedFlow ? 'Edit Process Step' : 'Add Process Step'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={3}>
              <TextField fullWidth type="number" label="Step #" value={flowForm.step_number} onChange={(e) => setFlowForm({ ...flowForm, step_number: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={9}>
              <TextField fullWidth label="Step Name" value={flowForm.step_name} onChange={(e) => setFlowForm({ ...flowForm, step_name: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={3} label="Description" value={flowForm.description} onChange={(e) => setFlowForm({ ...flowForm, description: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Equipment" value={flowForm.equipment} onChange={(e) => setFlowForm({ ...flowForm, equipment: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField fullWidth type="number" label="Temp (°C)" value={flowForm.temperature} onChange={(e) => setFlowForm({ ...flowForm, temperature: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField fullWidth type="number" label="Time (min)" value={flowForm.time_minutes} onChange={(e) => setFlowForm({ ...flowForm, time_minutes: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField fullWidth type="number" label="pH" value={flowForm.ph} onChange={(e) => setFlowForm({ ...flowForm, ph: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField fullWidth type="number" label="aW" value={flowForm.aw} onChange={(e) => setFlowForm({ ...flowForm, aw: e.target.value })} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setProcessFlowDialogOpen(false); setSelectedFlow(null); }}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveFlow}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Hazard Dialog */}
      <Dialog open={hazardDialogOpen} onClose={() => { setHazardDialogOpen(false); setSelectedHazardItem(null); }} maxWidth="md" fullWidth>
        <DialogTitle>{selectedHazardItem ? 'Edit Hazard' : 'Add Hazard'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Process Step</InputLabel>
                <Select
                  value={hazardForm.process_step_id}
                  label="Process Step"
                  onChange={(e) => setHazardForm({ ...hazardForm, process_step_id: e.target.value })}
                >
                  {processFlows.map((flow) => (
                    <MenuItem key={flow.id} value={flow.id}>
                      {flow.step_number}. {flow.step_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Hazard Type</InputLabel>
                <Select
                  value={hazardForm.hazard_type}
                  label="Hazard Type"
                  onChange={(e) => setHazardForm({ ...hazardForm, hazard_type: e.target.value })}
                >
                              <MenuItem value="BIOLOGICAL">Biological</MenuItem>
            <MenuItem value="CHEMICAL">Chemical</MenuItem>
            <MenuItem value="PHYSICAL">Physical</MenuItem>
            <MenuItem value="ALLERGEN">Allergen</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Hazard Name" value={hazardForm.hazard_name} onChange={(e) => setHazardForm({ ...hazardForm, hazard_name: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={3} label="Description" value={hazardForm.description} onChange={(e) => setHazardForm({ ...hazardForm, description: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField fullWidth type="number" label="Likelihood" value={hazardForm.likelihood} onChange={(e) => setHazardForm({ ...hazardForm, likelihood: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField fullWidth type="number" label="Severity" value={hazardForm.severity} onChange={(e) => setHazardForm({ ...hazardForm, severity: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Control Measures" value={hazardForm.control_measures} onChange={(e) => setHazardForm({ ...hazardForm, control_measures: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControlLabel control={<Switch checked={hazardForm.is_controlled} onChange={(_e, c) => setHazardForm({ ...hazardForm, is_controlled: c })} />} label="Is Controlled" />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField fullWidth type="number" label="Control Effectiveness" value={hazardForm.control_effectiveness} onChange={(e) => setHazardForm({ ...hazardForm, control_effectiveness: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControlLabel control={<Switch checked={hazardForm.is_ccp} onChange={(_e, c) => setHazardForm({ ...hazardForm, is_ccp: c })} />} label="Is CCP" />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="CCP Justification" value={hazardForm.ccp_justification} onChange={(e) => setHazardForm({ ...hazardForm, ccp_justification: e.target.value })} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setHazardDialogOpen(false); setSelectedHazardItem(null); }}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveHazard}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* CCP Dialog */}
      <Dialog open={ccpDialogOpen} onClose={() => { setCcpDialogOpen(false); setSelectedCcpItem(null); }} maxWidth="md" fullWidth>
        <DialogTitle>{selectedCcpItem ? 'Edit CCP' : 'Add CCP'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <TextField fullWidth type="number" label="Hazard ID" value={ccpForm.hazard_id} onChange={(e) => setCcpForm({ ...ccpForm, hazard_id: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth label="CCP Number" value={ccpForm.ccp_number} onChange={(e) => setCcpForm({ ...ccpForm, ccp_number: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth label="CCP Name" value={ccpForm.ccp_name} onChange={(e) => setCcpForm({ ...ccpForm, ccp_name: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={3} label="Description" value={ccpForm.description} onChange={(e) => setCcpForm({ ...ccpForm, description: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth type="number" label="Critical Min" value={ccpForm.critical_limit_min} onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_min: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth type="number" label="Critical Max" value={ccpForm.critical_limit_max} onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_max: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth label="Unit" value={ccpForm.critical_limit_unit} onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_unit: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Monitoring Frequency" value={ccpForm.monitoring_frequency} onChange={(e) => setCcpForm({ ...ccpForm, monitoring_frequency: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Monitoring Method" value={ccpForm.monitoring_method} onChange={(e) => setCcpForm({ ...ccpForm, monitoring_method: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <Autocomplete
                options={userOptions}
                getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                value={monitoringUserValue}
                onChange={(_, val) => {
                  setMonitoringUserValue(val);
                  setCcpForm({ ...ccpForm, monitoring_responsible: val ? String(val.id) : '' });
                }}
                onInputChange={(_, val) => setUserSearch(val)}
                onOpen={() => setUserOpen(true)}
                onClose={() => setUserOpen(false)}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
                renderInput={(params) => <TextField {...params} label="Monitoring Responsible" placeholder="Search user..." fullWidth />}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Monitoring Equipment" value={ccpForm.monitoring_equipment} onChange={(e) => setCcpForm({ ...ccpForm, monitoring_equipment: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Corrective Actions" value={ccpForm.corrective_actions} onChange={(e) => setCcpForm({ ...ccpForm, corrective_actions: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Verification Frequency" value={ccpForm.verification_frequency} onChange={(e) => setCcpForm({ ...ccpForm, verification_frequency: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Verification Method" value={ccpForm.verification_method} onChange={(e) => setCcpForm({ ...ccpForm, verification_method: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <Autocomplete
                options={userOptions}
                getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                value={verificationUserValue}
                onChange={(_, val) => {
                  setVerificationUserValue(val);
                  setCcpForm({ ...ccpForm, verification_responsible: val ? String(val.id) : '' });
                }}
                onInputChange={(_, val) => setUserSearch(val)}
                onOpen={() => setUserOpen(true)}
                onClose={() => setUserOpen(false)}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
                renderInput={(params) => <TextField {...params} label="Verification Responsible" placeholder="Search user..." fullWidth />}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setCcpDialogOpen(false); setSelectedCcpItem(null); }}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveCCP}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Simple edit dialogs could be implemented similarly for process flows, hazards, and CCPs. */}
      
      {/* HACCP Flowchart Builder */}
      <HACCPFlowchartBuilder
        open={flowchartBuilderOpen}
        onClose={handleCloseFlowchartBuilder}
        productId={selectedProductForFlowchart?.id?.toString()}
        productName={selectedProductForFlowchart?.name}
        readOnly={!canManageHACCP}
      />
    </Box>
  );
};

export default HACCP; 