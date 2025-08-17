import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Chip,
  IconButton,
  Alert,
  LinearProgress,
  CircularProgress,
  FormControlLabel,
  Checkbox,
  Autocomplete,
  useMediaQuery,
  useTheme,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  AppBar,
  Toolbar,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  SwipeableDrawer,
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  Warning as WarningIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Download as DownloadIcon,
  Assessment as AssessmentIcon,
  Inventory as InventoryIcon,
  Report as ReportIcon,
  Assessment as SimulationIcon,
  Search as SearchIcon2,
  Menu as MenuIcon,
  Close as CloseIcon,
  Dashboard as DashboardIcon,
  Inventory as BatchIcon,
  Warning as RecallIcon,
  Timeline as TimelineIcon,
  QrCode as QrCodeIcon,
  Settings as SettingsIcon,
  CloudOff as CloudOffIcon
} from '@mui/icons-material';
import { traceabilityAPI } from '../services/traceabilityAPI';
import { usersAPI } from '../services/api';
import { Batch } from '../types/traceability';
import BatchList from '../components/Traceability/BatchList';
import BatchRegistrationForm from '../components/Traceability/BatchRegistrationForm';
import BatchDetail from '../components/Traceability/BatchDetail';
import RecallDetail from '../components/Traceability/RecallDetail';
import TraceabilityChain from '../components/Traceability/TraceabilityChain';
import RecallSimulationForm from '../components/Traceability/RecallSimulationForm';
import EnhancedSearchForm from '../components/Traceability/EnhancedSearchForm';
import QRCodeScanner from '../components/Traceability/QRCodeScanner';
import OfflineCapabilities from '../components/Traceability/OfflineCapabilities';
import MobileDataEntry from '../components/Traceability/MobileDataEntry';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

// Interfaces
interface Recall {
  id: number;
  recall_number: string;
  recall_type: string;
  status: string;
  title: string;
  reason: string;
  issue_discovered_date: string;
  recall_initiated_date?: string;
  total_quantity_affected: number;
  quantity_recalled: number;
  assigned_to: number;
  created_at: string;
}

interface TraceabilityReport {
  id: number;
  report_number: string;
  report_type: string;
  starting_batch_id: number;
  trace_date: string;
  trace_depth: number;
  trace_summary: string;
  created_at: string;
}

interface DashboardData {
  batch_counts: Record<string, number>;
  status_counts: Record<string, number>;
  recent_batches: number;
  active_recalls: number;
  recent_reports: number;
  quality_breakdown: Record<string, number>;
}

const Traceability: React.FC = () => {
  const { user: currentUser } = useSelector((state: RootState) => state.auth);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'lg'));
  
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [recalls, setRecalls] = useState<Recall[]>([]);
  const [reports, setReports] = useState<TraceabilityReport[]>([]);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Dialog states
  const [batchDialogOpen, setBatchDialogOpen] = useState(false);
  const [recallDialogOpen, setRecallDialogOpen] = useState(false);
  const [traceDialogOpen, setTraceDialogOpen] = useState(false);
  const [batchDetailOpen, setBatchDetailOpen] = useState(false);
  const [traceabilityChainOpen, setTraceabilityChainOpen] = useState(false);
  const [recallDetailOpen, setRecallDetailOpen] = useState(false);
  const [selectedRecall, setSelectedRecall] = useState<Recall | null>(null);
  const [recallSimulationOpen, setRecallSimulationOpen] = useState(false);
  const [enhancedSearchOpen, setEnhancedSearchOpen] = useState(false);
  const [qrScannerOpen, setQrScannerOpen] = useState(false);
  const [offlineCapabilitiesOpen, setOfflineCapabilitiesOpen] = useState(false);
  const [mobileDataEntryOpen, setMobileDataEntryOpen] = useState(false);

  // Selected items
  const [selectedBatch, setSelectedBatch] = useState<Batch | null>(null);

  // Form states
  const [batchForm, setBatchForm] = useState({
    batch_type: '',
    product_name: '',
    quantity: '',
    unit: '',
    production_date: '',
    expiry_date: '',
    lot_number: '',
    storage_location: '',
    storage_conditions: ''
  });

  const [recallForm, setRecallForm] = useState({
    recall_type: '',
    title: '',
    description: '',
    reason: '',
    hazard_description: '',
    affected_products: '',
    affected_batches: '',
    total_quantity_affected: '',
    quantity_in_distribution: '',
    issue_discovered_date: '',
    regulatory_notification_required: false
  });

  // Assigned-to user search state
  const [assigneeInput, setAssigneeInput] = useState('');
  const [assigneeOptions, setAssigneeOptions] = useState<Array<{ id: number; username: string; full_name?: string }>>([]);
  const [selectedAssignee, setSelectedAssignee] = useState<{ id: number; username: string; full_name?: string } | null>(null);
  useEffect(() => {
    let active = true;
    const t = setTimeout(async () => {
      try {
        const resp = await usersAPI.getUsers({ page: 1, size: 10, search: assigneeInput });
        const items = (resp?.items || []) as Array<any>;
        if (active) setAssigneeOptions(items.map((u) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch {
        if (active) setAssigneeOptions([]);
      }
    }, 300);
    return () => { active = false; clearTimeout(t); };
  }, [assigneeInput]);

  const [traceForm, setTraceForm] = useState({
    starting_batch_id: '',
    report_type: 'full_trace',
    trace_depth: 5
  });

  // Filter states
  const [batchFilters] = useState({
    batch_type: '',
    status: '',
    search: ''
  });

  const [recallFilters] = useState({
    status: '',
    recall_type: '',
    search: ''
  });

  // Load data on component mount
  useEffect(() => {
    fetchDashboardData();
    fetchBatches();
    fetchRecalls();
    fetchReports();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // API calls
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await traceabilityAPI.getDashboard();
      setDashboardData(data);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchBatches = async () => {
    try {
      setLoading(true);
      const data = await traceabilityAPI.getBatches({
        page: 1,
        size: 100,
        ...batchFilters
      });
      setBatches(data.items || []);
    } catch (err) {
      setError('Failed to load batches');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecalls = async () => {
    try {
      setLoading(true);
      const data = await traceabilityAPI.getRecalls({
        page: 1,
        size: 100,
        ...recallFilters
      });
      setRecalls(data.items || []);
    } catch (err) {
      setError('Failed to load recalls');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchReports = async () => {
    try {
      setLoading(true);
      const data = await traceabilityAPI.getTraceabilityReports({
        page: 1,
        size: 100
      });
      setReports(data.items || []);
    } catch (err) {
      setError('Failed to load traceability reports');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Form handlers
  const handleCreateBatch = async () => {
    try {
      setLoading(true);
      await traceabilityAPI.createBatch(batchForm);
      setBatchDialogOpen(false);
      setBatchForm({
        batch_type: '',
        product_name: '',
        quantity: '',
        unit: '',
        production_date: '',
        expiry_date: '',
        lot_number: '',
        storage_location: '',
        storage_conditions: ''
      });
      fetchBatches();
    } catch (err) {
      setError('Failed to create batch');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRecall = async () => {
    try {
      setLoading(true);
      // Clean payload to match backend schema
      const payload: any = {
        recall_type: recallForm.recall_type,
        title: recallForm.title,
        description: recallForm.description,
        reason: recallForm.reason,
        issue_discovered_date: recallForm.issue_discovered_date,
        total_quantity_affected: recallForm.total_quantity_affected === '' ? undefined : parseFloat(recallForm.total_quantity_affected as any),
        quantity_in_distribution: recallForm.quantity_in_distribution === '' ? undefined : parseFloat(recallForm.quantity_in_distribution as any),
        regulatory_notification_required: recallForm.regulatory_notification_required,
        assigned_to: selectedAssignee?.id,
      };
      // Omit optional string lists if empty
      if (recallForm.hazard_description && recallForm.hazard_description.trim() !== '') {
        payload.hazard_description = recallForm.hazard_description;
      }
      if (recallForm.affected_products && recallForm.affected_products.trim() !== '') {
        try { payload.affected_products = JSON.parse(recallForm.affected_products); } catch { /* ignore */ }
      }
      if (recallForm.affected_batches && recallForm.affected_batches.trim() !== '') {
        try { payload.affected_batches = JSON.parse(recallForm.affected_batches); } catch { /* ignore */ }
      }

      if (!payload.assigned_to) {
        throw new Error('Please select an assignee for this recall');
      }

      await traceabilityAPI.createRecall(payload);
      setRecallDialogOpen(false);
      setRecallForm({
        recall_type: '',
        title: '',
        description: '',
        reason: '',
        hazard_description: '',
        affected_products: '',
        affected_batches: '',
        total_quantity_affected: '',
        quantity_in_distribution: '',
        issue_discovered_date: '',
        regulatory_notification_required: false
      });
      setSelectedAssignee(null);
      setAssigneeInput('');
      fetchRecalls();
    } catch (err) {
      setError('Failed to create recall');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTraceReport = async () => {
    try {
      setLoading(true);
      await traceabilityAPI.createTraceabilityReport(traceForm);
      setTraceDialogOpen(false);
      setTraceForm({
        starting_batch_id: '',
        report_type: 'full_trace',
        trace_depth: 5
      });
      fetchReports();
    } catch (err) {
      setError('Failed to create traceability report');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchSelect = (batch: Batch) => {
    setSelectedBatch(batch);
    setBatchDetailOpen(true);
  };

  const handleTraceabilityChain = (batch: Batch) => {
    setSelectedBatch(batch);
    setTraceabilityChainOpen(true);
  };

  // Utility functions
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

  const getRecallTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'class_i': return 'error';
      case 'class_ii': return 'warning';
      case 'class_iii': return 'info';
      default: return 'default';
    }
  };

  const getRecallStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'draft': return 'default';
      case 'initiated': return 'warning';
      case 'in_progress': return 'primary';
      case 'completed': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  // Mobile navigation tabs
  const mobileTabs = [
    { label: 'Dashboard', icon: <DashboardIcon />, value: 0 },
    { label: 'Batches', icon: <BatchIcon />, value: 1 },
    { label: 'Recalls', icon: <RecallIcon />, value: 2 },
    { label: 'Reports', icon: <TimelineIcon />, value: 3 },
    { label: 'Search', icon: <SearchIcon2 />, value: 4 },
    { label: 'Simulation', icon: <SimulationIcon />, value: 5 },
    { label: 'Offline', icon: <CloudOffIcon />, value: 6 }
  ];

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    if (isMobile) {
      setMobileDrawerOpen(false);
    }
  };

  return (
    <Box sx={{ 
      p: { xs: 1, sm: 2, md: 3 },
      minHeight: '100vh',
      backgroundColor: theme.palette.background.default
    }}>
      {/* Mobile App Bar */}
      {isMobile && (
        <AppBar 
          position="sticky" 
          sx={{ 
            top: 0, 
            zIndex: theme.zIndex.drawer + 1,
            backgroundColor: theme.palette.primary.main
          }}
        >
          <Toolbar>
            <IconButton
              edge="start"
              color="inherit"
              aria-label="open navigation menu"
              onClick={() => setMobileDrawerOpen(true)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>
              Traceability & Recall
            </Typography>
            <IconButton
              color="inherit"
              aria-label="QR code scanner"
              onClick={() => setQrScannerOpen(true)}
            >
              <QrCodeIcon />
            </IconButton>
          </Toolbar>
        </AppBar>
      )}

      {/* Desktop Header */}
      {!isMobile && (
        <Typography 
          variant="h3" 
          gutterBottom 
          sx={{ 
            mb: 3,
            fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' }
          }}
        >
          Traceability & Recall Management
        </Typography>
      )}

      {/* Mobile Navigation Drawer */}
      <SwipeableDrawer
        anchor="left"
        open={mobileDrawerOpen}
        onClose={() => setMobileDrawerOpen(false)}
        onOpen={() => setMobileDrawerOpen(true)}
        sx={{
          '& .MuiDrawer-paper': {
            width: 280,
            boxSizing: 'border-box',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              Navigation
            </Typography>
            <IconButton onClick={() => setMobileDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
          <Divider sx={{ mb: 2 }} />
          <List>
            {mobileTabs.map((tab) => (
              <ListItem key={tab.value} disablePadding>
                <ListItemButton
                  selected={activeTab === tab.value}
                  onClick={() => handleTabChange({} as React.SyntheticEvent, tab.value)}
                  sx={{
                    borderRadius: 1,
                    mb: 0.5,
                    '&.Mui-selected': {
                      backgroundColor: theme.palette.primary.light,
                      color: theme.palette.primary.contrastText,
                    }
                  }}
                >
                  <ListItemIcon sx={{ color: 'inherit' }}>
                    {tab.icon}
                  </ListItemIcon>
                  <ListItemText primary={tab.label} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </SwipeableDrawer>

      {/* Desktop Tabs */}
      {!isMobile && (
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                minHeight: 64,
                fontSize: '0.875rem',
                fontWeight: 500,
              }
            }}
          >
            <Tab label="Dashboard" icon={<AssessmentIcon />} />
            <Tab label="Batch Management" icon={<InventoryIcon />} />
            <Tab label="Recall Management" icon={<WarningIcon />} />
            <Tab label="Traceability Reports" icon={<ReportIcon />} />
                      <Tab label="Enhanced Search" icon={<SearchIcon2 />} />
          <Tab label="Recall Simulation" icon={<SimulationIcon />} />
          <Tab label="Offline Mode" icon={<CloudOffIcon />} />
          </Tabs>
        </Box>
      )}

      {/* Tab Content */}
      {activeTab === 0 && (
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2rem' } }}>
            Traceability Dashboard
          </Typography>
          {loading && <LinearProgress />}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          {dashboardData && (
            <Grid container spacing={{ xs: 1, sm: 2, md: 3 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Total Batches
                    </Typography>
                    <Typography variant="h4">
                      {Object.values(dashboardData.batch_counts).reduce((a, b) => a + b, 0)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Active Recalls
                    </Typography>
                    <Typography variant="h4" color="error">
                      {dashboardData.active_recalls}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Recent Reports
                    </Typography>
                    <Typography variant="h4" color="primary">
                      {dashboardData.recent_reports}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Recent Batches
                    </Typography>
                    <Typography variant="h4" color="success.main">
                      {dashboardData.recent_batches}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </Box>
      )}

      {activeTab === 1 && (
        <BatchList 
          onBatchSelect={handleBatchSelect}
          showActions={true}
        />
      )}

      {activeTab === 2 && (
        <Box>
          <Box sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between', 
            alignItems: { xs: 'stretch', sm: 'center' }, 
            mb: 3,
            gap: { xs: 2, sm: 0 }
          }}>
            <Typography variant="h4" sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2rem' } }}>
              Recall Management
            </Typography>
            <Button
              variant="contained"
              color="error"
              startIcon={<WarningIcon />}
              onClick={() => setRecallDialogOpen(true)}
              sx={{ 
                minWidth: { xs: '100%', sm: 'auto' },
                height: { xs: 48, sm: 40 }
              }}
            >
              Create Recall
            </Button>
          </Box>

          <TableContainer 
            component={Paper} 
            sx={{ 
              maxHeight: { xs: 400, sm: 600 },
              overflow: 'auto'
            }}
          >
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Recall Number</TableCell>
                  <TableCell>Title</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>Issue Date</TableCell>
                  <TableCell sx={{ display: { xs: 'none', lg: 'table-cell' } }}>Quantity Affected</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recalls.map((recall) => (
                  <TableRow key={recall.id}>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {recall.recall_number}
                      </Typography>
                    </TableCell>
                    <TableCell>{recall.title}</TableCell>
                    <TableCell>
                      <Chip 
                        label={recall.recall_type.replace('_', ' ').toUpperCase()} 
                        color={getRecallTypeColor(recall.recall_type)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={recall.status.replace('_', ' ').toUpperCase()} 
                        color={getRecallStatusColor(recall.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>
                      {new Date(recall.issue_discovered_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell sx={{ display: { xs: 'none', lg: 'table-cell' } }}>{recall.total_quantity_affected}</TableCell>
                    <TableCell>
                      <IconButton 
                        size="small" 
                        onClick={() => { setSelectedRecall(recall); setRecallDetailOpen(true); }}
                        aria-label={`View details for recall ${recall.recall_number}`}
                      >
                        <VisibilityIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {activeTab === 3 && (
        <Box>
          <Box sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between', 
            alignItems: { xs: 'stretch', sm: 'center' }, 
            mb: 3,
            gap: { xs: 2, sm: 0 }
          }}>
            <Typography variant="h4" sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2rem' } }}>
              Traceability Reports
            </Typography>
            <Button
              variant="contained"
              startIcon={<AssessmentIcon />}
              onClick={() => setTraceDialogOpen(true)}
              sx={{ 
                minWidth: { xs: '100%', sm: 'auto' },
                height: { xs: 48, sm: 40 }
              }}
            >
              Create Trace Report
            </Button>
          </Box>

          <TableContainer 
            component={Paper}
            sx={{ 
              maxHeight: { xs: 400, sm: 600 },
              overflow: 'auto'
            }}
          >
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Report Number</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>Starting Batch</TableCell>
                  <TableCell sx={{ display: { xs: 'none', lg: 'table-cell' } }}>Trace Date</TableCell>
                  <TableCell sx={{ display: { xs: 'none', xl: 'table-cell' } }}>Summary</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {reports.map((report) => (
                  <TableRow key={report.id}>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {report.report_number}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={report.report_type.replace('_', ' ').toUpperCase()} 
                        color="primary"
                        size="small"
                      />
                    </TableCell>
                    <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>Batch #{report.starting_batch_id}</TableCell>
                    <TableCell sx={{ display: { xs: 'none', lg: 'table-cell' } }}>
                      {new Date(report.trace_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell sx={{ display: { xs: 'none', xl: 'table-cell' } }}>{report.trace_summary}</TableCell>
                    <TableCell>
                      <IconButton 
                        size="small"
                        aria-label={`View report ${report.report_number}`}
                      >
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton 
                        size="small"
                        aria-label={`Download report ${report.report_number}`}
                      >
                        <DownloadIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {activeTab === 4 && (
        <EnhancedSearchForm 
          onSearchResults={(results) => {
            console.log('Search results:', results);
          }}
        />
      )}

      {activeTab === 5 && (
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2rem' } }}>
            Recall Simulation
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Simulate recall scenarios to assess impact and plan response strategies.
          </Typography>
          <Button
            variant="contained"
            startIcon={<SimulationIcon />}
            onClick={() => setRecallSimulationOpen(true)}
            sx={{ 
              minWidth: { xs: '100%', sm: 'auto' },
              height: { xs: 48, sm: 40 }
            }}
          >
            Start Recall Simulation
          </Button>
        </Box>
      )}

      {activeTab === 6 && (
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem', md: '2rem' } }}>
            Offline Mode
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Manage offline data storage and synchronization for mobile field operations.
          </Typography>
          <OfflineCapabilities 
            onSyncComplete={() => {
              fetchBatches();
              fetchRecalls();
              fetchReports();
            }}
          />
        </Box>
      )}

      {/* Mobile Speed Dial for Quick Actions */}
      {isMobile && (
        <SpeedDial
          ariaLabel="Quick actions"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          icon={<SpeedDialIcon />}
        >
          <SpeedDialAction
            icon={<QrCodeIcon />}
            tooltipTitle="QR Scanner"
            onClick={() => setQrScannerOpen(true)}
          />
          <SpeedDialAction
            icon={<AddIcon />}
            tooltipTitle="Mobile Data Entry"
            onClick={() => setMobileDataEntryOpen(true)}
          />
          <SpeedDialAction
            icon={<AddIcon />}
            tooltipTitle="Create Batch"
            onClick={() => setBatchDialogOpen(true)}
          />
          <SpeedDialAction
            icon={<WarningIcon />}
            tooltipTitle="Create Recall"
            onClick={() => setRecallDialogOpen(true)}
          />
          <SpeedDialAction
            icon={<AssessmentIcon />}
            tooltipTitle="Create Report"
            onClick={() => setTraceDialogOpen(true)}
          />
          <SpeedDialAction
            icon={<CloudOffIcon />}
            tooltipTitle="Offline Mode"
            onClick={() => setActiveTab(6)}
          />
        </SpeedDial>
      )}

      {/* Dialogs */}
      <BatchRegistrationForm
        open={batchDialogOpen}
        onClose={() => setBatchDialogOpen(false)}
        onSuccess={fetchBatches}
      />

      {selectedBatch && (
        <>
          <BatchDetail
            open={batchDetailOpen}
            onClose={() => setBatchDetailOpen(false)}
            batch={selectedBatch}
          />
          <Dialog 
            open={traceabilityChainOpen} 
            onClose={() => setTraceabilityChainOpen(false)}
            maxWidth="lg"
            fullWidth
            fullScreen={isMobile}
          >
            <DialogTitle>Traceability Chain - {selectedBatch.batch_number}</DialogTitle>
            <DialogContent>
              <TraceabilityChain batchId={selectedBatch.id} />
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setTraceabilityChainOpen(false)}>
                Close
              </Button>
            </DialogActions>
          </Dialog>
        </>
      )}

      <RecallSimulationForm
        open={recallSimulationOpen}
        onClose={() => setRecallSimulationOpen(false)}
        onSimulationComplete={(simulation) => {
          console.log('Simulation completed:', simulation);
        }}
      />

      {selectedRecall && (
        <RecallDetail
          open={recallDetailOpen}
          onClose={() => { setRecallDetailOpen(false); fetchRecalls(); }}
          recallId={selectedRecall.id}
          recallTitle={selectedRecall.title}
        />
      )}

      {/* Create Recall Dialog */}
      <Dialog 
        open={recallDialogOpen} 
        onClose={() => setRecallDialogOpen(false)} 
        maxWidth="md" 
        fullWidth
        fullScreen={isMobile}
      >
        <DialogTitle>Create New Recall</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Recall Type</InputLabel>
                <Select
                  value={recallForm.recall_type}
                  onChange={(e) => setRecallForm({ ...recallForm, recall_type: e.target.value })}
                >
                  <MenuItem value="class_i">Class I - Life-threatening</MenuItem>
                  <MenuItem value="class_ii">Class II - Temporary health effects</MenuItem>
                  <MenuItem value="class_iii">Class III - No health effects</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <Autocomplete
                options={assigneeOptions}
                getOptionLabel={(option) => option.full_name ? `${option.full_name} (${option.username})` : option.username}
                value={selectedAssignee}
                onChange={(_, val) => setSelectedAssignee(val)}
                onInputChange={(_, val) => setAssigneeInput(val)}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
                renderInput={(params) => (
                  <TextField {...params} label="Assign To User" placeholder="Type to search users..." />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Title"
                value={recallForm.title}
                onChange={(e) => setRecallForm({ ...recallForm, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={recallForm.description}
                onChange={(e) => setRecallForm({ ...recallForm, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Reason for Recall"
                multiline
                rows={3}
                value={recallForm.reason}
                onChange={(e) => setRecallForm({ ...recallForm, reason: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Total Quantity Affected"
                type="number"
                value={recallForm.total_quantity_affected}
                onChange={(e) => setRecallForm({ ...recallForm, total_quantity_affected: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Issue Discovered Date"
                type="date"
                value={recallForm.issue_discovered_date}
                onChange={(e) => setRecallForm({ ...recallForm, issue_discovered_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRecallDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateRecall} variant="contained" color="error" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Create Recall'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Trace Report Dialog */}
      <Dialog 
        open={traceDialogOpen} 
        onClose={() => setTraceDialogOpen(false)} 
        maxWidth="sm" 
        fullWidth
        fullScreen={isMobile}
      >
        <DialogTitle>Create Traceability Report</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Autocomplete
                options={batches}
                getOptionLabel={(b: any) => (b.batch_number ? `${b.batch_number} — ${b.product_name}` : String(b.id))}
                value={batches.find(b => String(b.id) === String(traceForm.starting_batch_id)) || null}
                onChange={(_, val) => setTraceForm({ ...traceForm, starting_batch_id: val ? String(val.id) : '' })}
                onInputChange={(_, val) => {
                  // lightweight client filter; could wire backend soon
                  if (!val) return;
                  const lc = val.toLowerCase();
                  const filtered = (batches || []).filter(b => (b.batch_number || '').toLowerCase().includes(lc) || (b.product_name || '').toLowerCase().includes(lc));
                  if (filtered.length > 0) setBatches(filtered as any);
                }}
                renderInput={(params) => (
                  <TextField {...params} label="Starting Batch" placeholder="Search batch number or product" fullWidth />
                )}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Report Type</InputLabel>
                <Select
                  value={traceForm.report_type}
                  onChange={(e) => setTraceForm({ ...traceForm, report_type: e.target.value })}
                >
                  <MenuItem value="full_trace">Full Trace (Forward & Backward)</MenuItem>
                  <MenuItem value="forward_trace">Forward Trace (Products)</MenuItem>
                  <MenuItem value="backward_trace">Backward Trace (Ingredients)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Trace Depth"
                type="number"
                value={traceForm.trace_depth}
                onChange={(e) => setTraceForm({ ...traceForm, trace_depth: parseInt(e.target.value) })}
                helperText="Number of levels to trace (1-10)"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTraceDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateTraceReport} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Create Report'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* QR Code Scanner Dialog */}
      <QRCodeScanner
        open={qrScannerOpen}
        onClose={() => setQrScannerOpen(false)}
        onBatchFound={(batch) => {
          setSelectedBatch(batch);
          setBatchDetailOpen(true);
          setQrScannerOpen(false);
        }}
      />

      {/* Mobile Data Entry Dialog */}
      <MobileDataEntry
        open={mobileDataEntryOpen}
        onClose={() => setMobileDataEntryOpen(false)}
        onSave={(data) => {
          console.log('Mobile data saved:', data);
          setMobileDataEntryOpen(false);
          // Refresh data after save
          fetchBatches();
        }}
      />
    </Box>
  );
};

export default Traceability; 