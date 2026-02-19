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
  Stack,
  Alert,
  IconButton,
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Security,
  Warning,
  CheckCircle,
  Add,
  Edit,
  Visibility,
  Science,
  Delete,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { AppDispatch, RootState } from '../store';
import {
  fetchProducts,
  fetchProduct,
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
  fetchOPRPs,
  createOPRP,
  updateOPRP,
  deleteOPRP,
  fetchDashboard,
  setSelectedProduct,
  clearError,
} from '../store/slices/haccpSlice';
import { hasRole, isSystemAdministrator, hasPermission } from '../store/slices/authSlice';
import { Autocomplete } from '@mui/material';
import { usersAPI } from '../services/api';
import PageHeader from '../components/UI/PageHeader';
import StatusChip from '../components/UI/StatusChip';
import ProductDialog from '../components/HACCP/ProductDialog';
import HACCPFlowchartBuilder from '../components/HACCP/FlowchartBuilder';
import HazardViewDialog from '../components/HACCP/HazardViewDialog';

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
    oprps,
    dashboardStats, 
    loading, 
    error 
  } = useSelector((state: RootState) => state.haccp);
  
  const [selectedTab, setSelectedTab] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();
  const [productDialogOpen, setProductDialogOpen] = useState(false);
  const [processFlowDialogOpen, setProcessFlowDialogOpen] = useState(false);
  const [hazardDialogOpen, setHazardDialogOpen] = useState(false);
  const [hazardViewDialogOpen, setHazardViewDialogOpen] = useState(false);
  const [ccpDialogOpen, setCcpDialogOpen] = useState(false);
  const [selectedProductForEdit, setSelectedProductForEdit] = useState<any>(null);
  const [selectedFlow, setSelectedFlow] = useState<any>(null);
  const [selectedHazardItem, setSelectedHazardItem] = useState<any>(null);
  const [selectedCcpItem, setSelectedCcpItem] = useState<any>(null);
  const [selectedOprpItem, setSelectedOprpItem] = useState<any>(null);
  const [oprpDialogOpen, setOprpDialogOpen] = useState(false);
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
    hazard_type: 'biological',
    hazard_name: '',
    description: '',
    consequences: '',
    likelihood: '1',
    severity: '1',
    control_measures: '',
    is_controlled: false as boolean,
    control_effectiveness: '',
    risk_strategy: 'not_determined',
    is_ccp: false as boolean,
    ccp_justification: '',
    opprp_justification: '',
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
  const [oprpForm, setOprpForm] = useState({
    hazard_id: '',
    oprp_number: '',
    oprp_name: '',
    description: '',
    operational_limit_min: '',
    operational_limit_max: '',
    operational_limit_unit: '',
    monitoring_frequency: '',
    monitoring_method: '',
    monitoring_responsible: '',
    monitoring_equipment: '',
    corrective_actions: '',
    verification_frequency: '',
    verification_method: '',
    verification_responsible: '',
    justification: '',
    effectiveness_validation: '',
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
  // Removed productForm state and handlers - now using ProductDialog component

  const handleCloseFlowchartBuilder = () => {
    setFlowchartBuilderOpen(false);
    setSelectedProductForFlowchart(null);
  };

  const handleFlowchartSaved = () => {
    // Reload products to show updated process flows
    loadProducts();
    // Optionally reload product details if viewing a specific product
    if (selectedProductForFlowchart?.id) {
      loadProductDetails(selectedProductForFlowchart.id);
    }
  };

  // Role-based permissions: allow access if user has haccp:view permission or legacy role-based access
  const hasHaccpView = (currentUser?.permissions as string[] | undefined)?.includes('haccp:view') ?? false;
  const canManageHACCP = hasHaccpView ||
                         hasRole(currentUser, 'QA Manager') ||
                         hasRole(currentUser, 'QA Specialist') ||
                         hasRole(currentUser, 'HACCP Logger') ||
                         isSystemAdministrator(currentUser);

  // Program-level create/update/delete (products, process flow, hazards, CCPs, OPRPs) — requires manage_program
  const canManageProgram = !!currentUser && (
    hasPermission(currentUser, 'haccp', 'manage_program') ||
    isSystemAdministrator(currentUser)
  );
  // Logs tab only: creating monitoring/verification logs requires haccp:create (no manage_program needed)
  const canCreateLogs = !!currentUser && hasPermission(currentUser, 'haccp', 'create');
  const canCreateProducts = canManageProgram;
  const canUpdateHACCP = canManageProgram;
  const canDeleteHACCP = canManageProgram;
  const canEditPlan = canManageProgram; // Add Step, Add Hazard, Edit/Delete CCP/OPRP, etc.

  const hasAssignmentAccess = Boolean(currentUser?.has_haccp_assignment);
  const canAccessHACCP = canManageHACCP || hasAssignmentAccess;

  const showDashboardTab = canManageHACCP;
  const dashboardTabIndex = 0;
  const productsTabIndex = showDashboardTab ? 1 : 0;

  useEffect(() => {
    loadDashboard();
    loadProducts();
  }, [dispatch]);

  // Read ?tab= from URL to jump to details
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tabParam = params.get('tab');
    if (tabParam === 'details' || tabParam === 'products') {
      setSelectedTab(productsTabIndex);
    } else if (tabParam === 'dashboard' && showDashboardTab) {
      setSelectedTab(dashboardTabIndex);
    }
  }, [location.search, productsTabIndex, dashboardTabIndex, showDashboardTab]);

  const loadDashboard = () => {
    dispatch(fetchDashboard());
  };

  const loadProducts = () => {
    dispatch(fetchProducts());
  };

  const loadProductDetails = (productId: number) => {
    dispatch(fetchProduct(productId));
    dispatch(fetchOPRPs(productId));
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
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
      alert('Hazard deleted successfully!');
    } catch (error: any) {
      console.error('Failed to delete hazard:', error);
      alert(`Failed to delete hazard: ${error}`);
    }
  };

  const handleDeleteCCP = async (ccpId: number) => {
    if (!window.confirm('Delete this CCP?')) return;
    try {
      await dispatch(deleteCCP(ccpId)).unwrap();
      if (selectedProduct) loadProductDetails(selectedProduct.id);
    } catch (e) { /* noop */ }
  };

  const handleDeleteOPRP = async (oprpId: number) => {
    if (!window.confirm('Delete this OPRP?')) return;
    try {
      await dispatch(deleteOPRP(oprpId)).unwrap();
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
        hazard_type: selectedHazardItem.hazard_type || 'biological',
        hazard_name: selectedHazardItem.hazard_name || '',
        description: selectedHazardItem.description || '',
        consequences: selectedHazardItem.consequences || '',
        likelihood: String(selectedHazardItem.likelihood ?? '1'),
        severity: String(selectedHazardItem.severity ?? '1'),
        control_measures: selectedHazardItem.control_measures || '',
        is_controlled: !!selectedHazardItem.is_controlled,
        control_effectiveness: String(selectedHazardItem.control_effectiveness ?? ''),
        risk_strategy: selectedHazardItem.risk_strategy || 'not_determined',
        is_ccp: !!selectedHazardItem.is_ccp,
        ccp_justification: selectedHazardItem.ccp_justification || '',
        opprp_justification: selectedHazardItem.opprp_justification || '',
      });
    } else {
      setHazardForm({ 
        process_step_id: '', 
        hazard_type: 'biological', 
        hazard_name: '', 
        description: '', 
        consequences: '',
        likelihood: '1', 
        severity: '1', 
        control_measures: '', 
        is_controlled: false, 
        control_effectiveness: '', 
        risk_strategy: 'not_determined',
        is_ccp: false, 
        ccp_justification: '',
        opprp_justification: ''
      });
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

  useEffect(() => {
    if (selectedOprpItem) {
      setOprpForm({
        hazard_id: String(selectedOprpItem.hazard_id ?? ''),
        oprp_number: selectedOprpItem.oprp_number || '',
        oprp_name: selectedOprpItem.oprp_name || '',
        description: selectedOprpItem.description || '',
        operational_limit_min: String(selectedOprpItem.operational_limit_min ?? ''),
        operational_limit_max: String(selectedOprpItem.operational_limit_max ?? ''),
        operational_limit_unit: selectedOprpItem.operational_limit_unit || '',
        monitoring_frequency: selectedOprpItem.monitoring_frequency || '',
        monitoring_method: selectedOprpItem.monitoring_method || '',
        monitoring_responsible: String(selectedOprpItem.monitoring_responsible ?? ''),
        monitoring_equipment: selectedOprpItem.monitoring_equipment || '',
        corrective_actions: selectedOprpItem.corrective_actions || '',
        verification_frequency: selectedOprpItem.verification_frequency || '',
        verification_method: selectedOprpItem.verification_method || '',
        verification_responsible: String(selectedOprpItem.verification_responsible ?? ''),
        justification: selectedOprpItem.justification || '',
        effectiveness_validation: selectedOprpItem.effectiveness_validation || '',
      });
    } else {
      setOprpForm({ hazard_id: '', oprp_number: '', oprp_name: '', description: '', operational_limit_min: '', operational_limit_max: '', operational_limit_unit: '', monitoring_frequency: '', monitoring_method: '', monitoring_responsible: '', monitoring_equipment: '', corrective_actions: '', verification_frequency: '', verification_method: '', verification_responsible: '', justification: '', effectiveness_validation: '' });
    }
  }, [selectedOprpItem]);

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
      consequences: hazardForm.consequences,
      likelihood: Number(hazardForm.likelihood),
      severity: Number(hazardForm.severity),
      control_measures: hazardForm.control_measures,
      is_controlled: hazardForm.is_controlled,
      control_effectiveness: hazardForm.control_effectiveness === '' ? null : Number(hazardForm.control_effectiveness),
      risk_strategy: hazardForm.risk_strategy,
      is_ccp: hazardForm.is_ccp,
      ccp_justification: hazardForm.ccp_justification,
      opprp_justification: hazardForm.opprp_justification,
    };
    try {
      let hazardId;
      if (selectedHazardItem) {
        const result = await dispatch(updateHazard({ hazardId: selectedHazardItem.id, hazardData: payload })).unwrap();
        hazardId = selectedHazardItem.id;
      } else {
        const result = await dispatch(createHazard({ productId: selectedProduct.id, hazardData: payload })).unwrap();
        hazardId = result.data.id;
      }
      
      // If risk strategy is OPPRP, create an OPRP
      if (hazardForm.risk_strategy === 'opprp' && hazardId) {
        const oprpPayload = {
          hazard_id: hazardId,
          oprp_number: `OPRP-${hazardId}`,
          oprp_name: `OPRP for ${hazardForm.hazard_name}`,
          description: `Operational prerequisite program for ${hazardForm.hazard_name}`,
          justification: hazardForm.opprp_justification || 'Operational prerequisite program as determined by risk assessment',
          monitoring_frequency: 'As per monitoring schedule',
          monitoring_method: 'Visual inspection and measurement',
          corrective_actions: 'Implement corrective actions as per SOP',
          verification_frequency: 'Monthly',
          verification_method: 'Review of monitoring records and effectiveness',
        };
        
        try {
          await dispatch(createOPRP({ productId: selectedProduct.id, oprpData: oprpPayload })).unwrap();
        } catch (oprpError) {
          console.error('Failed to create OPRP:', oprpError);
          // Don't fail the hazard creation if OPRP creation fails
        }
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

  const handleSaveOPRP = async () => {
    if (!selectedProduct) return;
    const payload: any = {
      hazard_id: oprpForm.hazard_id === '' ? null : Number(oprpForm.hazard_id),
      oprp_number: oprpForm.oprp_number,
      oprp_name: oprpForm.oprp_name,
      description: oprpForm.description,
      operational_limit_min: oprpForm.operational_limit_min === '' ? null : Number(oprpForm.operational_limit_min),
      operational_limit_max: oprpForm.operational_limit_max === '' ? null : Number(oprpForm.operational_limit_max),
      operational_limit_unit: oprpForm.operational_limit_unit,
      monitoring_frequency: oprpForm.monitoring_frequency,
      monitoring_method: oprpForm.monitoring_method,
      monitoring_responsible: oprpForm.monitoring_responsible === '' ? null : Number(oprpForm.monitoring_responsible),
      monitoring_equipment: oprpForm.monitoring_equipment,
      corrective_actions: oprpForm.corrective_actions,
      verification_frequency: oprpForm.verification_frequency,
      verification_method: oprpForm.verification_method,
      verification_responsible: oprpForm.verification_responsible === '' ? null : Number(oprpForm.verification_responsible),
      justification: oprpForm.justification,
      effectiveness_validation: oprpForm.effectiveness_validation,
    };
    try {
      if (selectedOprpItem) {
        await dispatch(updateOPRP({ oprpId: selectedOprpItem.id, oprpData: payload })).unwrap();
      } else {
        await dispatch(createOPRP({ productId: selectedProduct.id, oprpData: payload })).unwrap();
      }
      setOprpDialogOpen(false);
      setSelectedOprpItem(null);
      loadProductDetails(selectedProduct.id);
    } catch (e) { /* noop */ }
  };

  // Removed product form handlers - now using ProductDialog component



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
                  <Box sx={{ display: 'flex', gap: 0 }}>
                    {canUpdateHACCP && (
                      <IconButton size="small" onClick={(e) => {
                        e.stopPropagation();
                        setSelectedProductForEdit(product);
                        setProductDialogOpen(true);
                      }}>
                        <Edit />
                      </IconButton>
                    )}
                    {canDeleteHACCP && (
                      <IconButton size="small" onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteProduct(product.id);
                      }}>
                        <Delete />
                      </IconButton>
                    )}
                  </Box>
                </Box>
                {/* Build HACCP Flowchart button removed as per UX guidance */}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  if (!canAccessHACCP) {
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

      {hasAssignmentAccess && !canManageHACCP && (
        <Alert severity="info" sx={{ mb: 3 }}>
          You are viewing only the HACCP products assigned to you. Contact QA for broader access.
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => dispatch(clearError())}>
          {error}
        </Alert>
      )}

      {loading && <CircularProgress sx={{ display: 'block', margin: '20px auto' }} />}

      <Tabs value={selectedTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        {showDashboardTab && <Tab label="Dashboard" value={dashboardTabIndex} />}
        <Tab
          label={hasAssignmentAccess && !canManageHACCP ? 'Assigned Products' : 'Products'}
          value={productsTabIndex}
        />
      </Tabs>

      {showDashboardTab && (
        <TabPanel value={selectedTab} index={dashboardTabIndex}>
          {renderDashboard()}
        </TabPanel>
      )}

      <TabPanel value={selectedTab} index={productsTabIndex}>
        {renderProducts()}
      </TabPanel>

      {/* Product Dialog */}
      <ProductDialog 
        open={productDialogOpen} 
        onClose={() => { setProductDialogOpen(false); setSelectedProductForEdit(null); }} 
        product={selectedProductForEdit}
        onSuccess={() => {
          setProductDialogOpen(false);
          setSelectedProductForEdit(null);
          loadProducts();
        }}
      />

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
        <DialogTitle>{selectedHazardItem ? 'View Hazard' : 'Add Hazard'}</DialogTitle>
        <DialogContent>
          {selectedHazardItem && (
            <Alert severity="info" sx={{ mb: 2 }}>
              This is a read-only view of the hazard information.
            </Alert>
          )}
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Process Step</InputLabel>
                <Select
                  value={hazardForm.process_step_id}
                  label="Process Step"
                  onChange={(e) => setHazardForm({ ...hazardForm, process_step_id: e.target.value })}
                  disabled={!!selectedHazardItem}
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
                  disabled={!!selectedHazardItem}
                >
                              <MenuItem value="biological">Biological</MenuItem>
            <MenuItem value="chemical">Chemical</MenuItem>
            <MenuItem value="physical">Physical</MenuItem>
            <MenuItem value="allergen">Allergen</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Hazard Name" value={hazardForm.hazard_name} onChange={(e) => setHazardForm({ ...hazardForm, hazard_name: e.target.value })} disabled={!!selectedHazardItem} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={3} label="Description" value={hazardForm.description} onChange={(e) => setHazardForm({ ...hazardForm, description: e.target.value })} disabled={!!selectedHazardItem} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={3} label="Consequences" helperText="Potential consequences if this hazard occurs" value={hazardForm.consequences} onChange={(e) => setHazardForm({ ...hazardForm, consequences: e.target.value })} />
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
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Risk Strategy</InputLabel>
                <Select
                  value={hazardForm.risk_strategy}
                  label="Risk Strategy"
                  onChange={(e) => setHazardForm({ ...hazardForm, risk_strategy: e.target.value })}
                >
                  <MenuItem value="not_determined">Not Determined</MenuItem>
                  <MenuItem value="ccp">CCP - Critical Control Point</MenuItem>
                  <MenuItem value="opprp">OPPRP - Operational PRP</MenuItem>
                  <MenuItem value="accept">Accept Risk</MenuItem>
                  <MenuItem value="further_analysis">Further Analysis (Decision Tree)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControlLabel control={<Switch checked={hazardForm.is_controlled} onChange={(_e, c) => setHazardForm({ ...hazardForm, is_controlled: c })} />} label="Is Controlled" />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField fullWidth type="number" label="Control Effectiveness" value={hazardForm.control_effectiveness} onChange={(e) => setHazardForm({ ...hazardForm, control_effectiveness: e.target.value })} />
            </Grid>
            {hazardForm.risk_strategy === 'ccp' && (
              <>
                <Grid item xs={12} md={3}>
                  <FormControlLabel control={<Switch checked={hazardForm.is_ccp} onChange={(_e, c) => setHazardForm({ ...hazardForm, is_ccp: c })} />} label="Is CCP" />
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth label="CCP Justification" value={hazardForm.ccp_justification} onChange={(e) => setHazardForm({ ...hazardForm, ccp_justification: e.target.value })} />
                </Grid>
              </>
            )}
            {hazardForm.risk_strategy === 'opprp' && (
              <Grid item xs={12}>
                <TextField fullWidth label="OPPRP Justification" multiline rows={2} value={hazardForm.opprp_justification} onChange={(e) => setHazardForm({ ...hazardForm, opprp_justification: e.target.value })} />
              </Grid>
            )}
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
              <TextField 
                fullWidth 
                type="number" 
                label="Hazard ID" 
                value={ccpForm.hazard_id} 
                onChange={(e) => setCcpForm({ ...ccpForm, hazard_id: e.target.value })} 
                disabled
                helperText="Hazard ID cannot be changed after creation"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField 
                fullWidth 
                label="CCP Number" 
                value={ccpForm.ccp_number} 
                onChange={(e) => setCcpForm({ ...ccpForm, ccp_number: e.target.value })} 
                disabled={!!selectedCcpItem}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField 
                fullWidth 
                label="CCP Name" 
                value={ccpForm.ccp_name} 
                onChange={(e) => setCcpForm({ ...ccpForm, ccp_name: e.target.value })} 
                disabled={!!selectedCcpItem}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField 
                fullWidth 
                multiline 
                rows={3} 
                label="Description" 
                value={ccpForm.description} 
                onChange={(e) => setCcpForm({ ...ccpForm, description: e.target.value })} 
                disabled={!!selectedCcpItem}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField 
                fullWidth 
                type="number" 
                label="Critical Min" 
                value={ccpForm.critical_limit_min} 
                onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_min: e.target.value })} 
                disabled={!!selectedCcpItem}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField 
                fullWidth 
                type="number" 
                label="Critical Max" 
                value={ccpForm.critical_limit_max} 
                onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_max: e.target.value })} 
                disabled={!!selectedCcpItem}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField 
                fullWidth 
                label="Unit" 
                value={ccpForm.critical_limit_unit} 
                onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_unit: e.target.value })} 
                disabled={!!selectedCcpItem}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField 
                fullWidth 
                label="Monitoring Frequency" 
                value={ccpForm.monitoring_frequency} 
                onChange={(e) => setCcpForm({ ...ccpForm, monitoring_frequency: e.target.value })} 
                disabled={!!selectedCcpItem}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField 
                fullWidth 
                label="Monitoring Method" 
                value={ccpForm.monitoring_method} 
                onChange={(e) => setCcpForm({ ...ccpForm, monitoring_method: e.target.value })} 
                disabled={!!selectedCcpItem}
              />
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
              <TextField 
                fullWidth 
                label="Corrective Actions" 
                value={ccpForm.corrective_actions} 
                onChange={(e) => setCcpForm({ ...ccpForm, corrective_actions: e.target.value })} 
                disabled={!!selectedCcpItem}
              />
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

      {/* OPRP Dialog */}
      <Dialog open={oprpDialogOpen} onClose={() => { setOprpDialogOpen(false); setSelectedOprpItem(null); }} maxWidth="md" fullWidth>
        <DialogTitle>{selectedOprpItem ? 'Edit OPRP' : 'Add OPRP'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <TextField fullWidth type="number" label="Hazard ID" value={oprpForm.hazard_id} onChange={(e) => setOprpForm({ ...oprpForm, hazard_id: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth label="OPRP Number" value={oprpForm.oprp_number} onChange={(e) => setOprpForm({ ...oprpForm, oprp_number: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth label="OPRP Name" value={oprpForm.oprp_name} onChange={(e) => setOprpForm({ ...oprpForm, oprp_name: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={3} label="Description" value={oprpForm.description} onChange={(e) => setOprpForm({ ...oprpForm, description: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth type="number" label="Operational Min" value={oprpForm.operational_limit_min} onChange={(e) => setOprpForm({ ...oprpForm, operational_limit_min: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth type="number" label="Operational Max" value={oprpForm.operational_limit_max} onChange={(e) => setOprpForm({ ...oprpForm, operational_limit_max: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField fullWidth label="Unit" value={oprpForm.operational_limit_unit} onChange={(e) => setOprpForm({ ...oprpForm, operational_limit_unit: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Monitoring Frequency" value={oprpForm.monitoring_frequency} onChange={(e) => setOprpForm({ ...oprpForm, monitoring_frequency: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Monitoring Method" value={oprpForm.monitoring_method} onChange={(e) => setOprpForm({ ...oprpForm, monitoring_method: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <Autocomplete
                options={userOptions}
                getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                value={monitoringUserValue}
                onChange={(_, val) => {
                  setMonitoringUserValue(val);
                  setOprpForm({ ...oprpForm, monitoring_responsible: val ? String(val.id) : '' });
                }}
                onInputChange={(_, val) => setUserSearch(val)}
                onOpen={() => setUserOpen(true)}
                onClose={() => setUserOpen(false)}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
                renderInput={(params) => <TextField {...params} label="Monitoring Responsible" placeholder="Search user..." fullWidth />}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Monitoring Equipment" value={oprpForm.monitoring_equipment} onChange={(e) => setOprpForm({ ...oprpForm, monitoring_equipment: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Corrective Actions" value={oprpForm.corrective_actions} onChange={(e) => setOprpForm({ ...oprpForm, corrective_actions: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Verification Frequency" value={oprpForm.verification_frequency} onChange={(e) => setOprpForm({ ...oprpForm, verification_frequency: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Verification Method" value={oprpForm.verification_method} onChange={(e) => setOprpForm({ ...oprpForm, verification_method: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <Autocomplete
                options={userOptions}
                getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                value={verificationUserValue}
                onChange={(_, val) => {
                  setVerificationUserValue(val);
                  setOprpForm({ ...oprpForm, verification_responsible: val ? String(val.id) : '' });
                }}
                onInputChange={(_, val) => setUserSearch(val)}
                onOpen={() => setUserOpen(true)}
                onClose={() => setUserOpen(false)}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
                renderInput={(params) => <TextField {...params} label="Verification Responsible" placeholder="Search user..." fullWidth />}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Justification" multiline rows={2} value={oprpForm.justification} onChange={(e) => setOprpForm({ ...oprpForm, justification: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Effectiveness Validation" multiline rows={2} value={oprpForm.effectiveness_validation} onChange={(e) => setOprpForm({ ...oprpForm, effectiveness_validation: e.target.value })} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setOprpDialogOpen(false); setSelectedOprpItem(null); }}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveOPRP}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Hazard View Dialog - For Viewing Existing Hazards */}
      <HazardViewDialog
        open={hazardViewDialogOpen}
        onClose={() => {
          setHazardViewDialogOpen(false);
          setSelectedHazardItem(null);
        }}
        hazardData={selectedHazardItem}
        processFlows={processFlows}
      />

      {/* Simple edit dialogs could be implemented similarly for process flows, hazards, and CCPs. */}
      
      {/* HACCP Flowchart Builder */}
      <HACCPFlowchartBuilder
        open={flowchartBuilderOpen}
        onClose={handleCloseFlowchartBuilder}
        onSuccess={handleFlowchartSaved}
        productId={selectedProductForFlowchart?.id?.toString()}
        productName={selectedProductForFlowchart?.name}
        hazards={hazards}
        ccps={ccps}
        readOnly={!canManageHACCP}
      />
    </Box>
  );
};

export default HACCP; 