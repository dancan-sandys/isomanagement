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
  Checkbox
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  QrCode as QrCodeIcon,
  Timeline as TimelineIcon,
  Warning as WarningIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Print as PrintIcon,
  Download as DownloadIcon,
  Assessment as AssessmentIcon,
  Inventory as InventoryIcon,
  Report as ReportIcon,
  Assessment as SimulationIcon,
  Search as SearchIcon2
} from '@mui/icons-material';
import { traceabilityAPI } from '../services/traceabilityAPI';
import { Batch } from '../types/traceability';
import BatchList from '../components/Traceability/BatchList';
import BatchRegistrationForm from '../components/Traceability/BatchRegistrationForm';
import BatchDetail from '../components/Traceability/BatchDetail';
import TraceabilityChain from '../components/Traceability/TraceabilityChain';
import RecallSimulationForm from '../components/Traceability/RecallSimulationForm';
import EnhancedSearchForm from '../components/Traceability/EnhancedSearchForm';

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
  // State management
  const [activeTab, setActiveTab] = useState(0);
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
  const [recallSimulationOpen, setRecallSimulationOpen] = useState(false);
  const [enhancedSearchOpen, setEnhancedSearchOpen] = useState(false);

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

  const [traceForm, setTraceForm] = useState({
    starting_batch_id: '',
    report_type: 'full_trace',
    trace_depth: 5
  });

  // Filter states
  const [batchFilters, setBatchFilters] = useState({
    batch_type: '',
    status: '',
    search: ''
  });

  const [recallFilters, setRecallFilters] = useState({
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
      await traceabilityAPI.createRecall(recallForm);
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

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h3" gutterBottom>
        Traceability & Recall Management
      </Typography>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Dashboard" icon={<AssessmentIcon />} />
          <Tab label="Batch Management" icon={<InventoryIcon />} />
          <Tab label="Recall Management" icon={<WarningIcon />} />
          <Tab label="Traceability Reports" icon={<ReportIcon />} />
          <Tab label="Enhanced Search" icon={<SearchIcon2 />} />
          <Tab label="Recall Simulation" icon={<SimulationIcon />} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Box>
          <Typography variant="h4" gutterBottom>
            Traceability Dashboard
          </Typography>
          {loading && <LinearProgress />}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          {dashboardData && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Card>
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
              <Grid item xs={12} md={3}>
                <Card>
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
              <Grid item xs={12} md={3}>
                <Card>
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
              <Grid item xs={12} md={3}>
                <Card>
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
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">
              Recall Management
            </Typography>
            <Button
              variant="contained"
              color="error"
              startIcon={<WarningIcon />}
              onClick={() => setRecallDialogOpen(true)}
            >
              Create Recall
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Recall Number</TableCell>
                  <TableCell>Title</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Issue Date</TableCell>
                  <TableCell>Quantity Affected</TableCell>
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
                    <TableCell>
                      {new Date(recall.issue_discovered_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>{recall.total_quantity_affected}</TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton size="small">
                        <EditIcon />
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
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">
              Traceability Reports
            </Typography>
            <Button
              variant="contained"
              startIcon={<AssessmentIcon />}
              onClick={() => setTraceDialogOpen(true)}
            >
              Create Trace Report
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Report Number</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Starting Batch</TableCell>
                  <TableCell>Trace Date</TableCell>
                  <TableCell>Summary</TableCell>
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
                    <TableCell>Batch #{report.starting_batch_id}</TableCell>
                    <TableCell>
                      {new Date(report.trace_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>{report.trace_summary}</TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton size="small">
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
          <Typography variant="h4" gutterBottom>
            Recall Simulation
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Simulate recall scenarios to assess impact and plan response strategies.
          </Typography>
          <Button
            variant="contained"
            startIcon={<SimulationIcon />}
            onClick={() => setRecallSimulationOpen(true)}
          >
            Start Recall Simulation
          </Button>
        </Box>
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

      {/* Create Recall Dialog */}
      <Dialog open={recallDialogOpen} onClose={() => setRecallDialogOpen(false)} maxWidth="md" fullWidth>
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
      <Dialog open={traceDialogOpen} onClose={() => setTraceDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Traceability Report</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Starting Batch ID"
                type="number"
                value={traceForm.starting_batch_id}
                onChange={(e) => setTraceForm({ ...traceForm, starting_batch_id: e.target.value })}
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
    </Box>
  );
};

export default Traceability; 