import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Chip, 
  Stack, 
  Button, 
  CircularProgress, 
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Fab,
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Assessment as AssessmentIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import objectivesAPI from '../services/objectivesAPI';
import { ObjectiveCreatePayload, ObjectiveUpdatePayload, ObjectiveTargetPayload, ObjectiveProgressPayload } from '../services/objectivesAPI';
import ObjectiveDetailView from '../components/objectives/ObjectiveDetailView';
import ObjectivesDashboard from '../components/objectives/ObjectivesDashboard';
import { departmentsAPI } from '../services/departmentsAPI';

interface ObjectiveTarget {
  id: number;
  objective_id: number;
  department_id?: number;
  period_start: string;
  period_end: string;
  target_value: number;
  lower_threshold?: number;
  upper_threshold?: number;
  weight: number;
  is_lower_better: boolean;
  created_at: string;
}

interface ObjectiveProgress {
  id: number;
  objective_id: number;
  department_id?: number;
  period_start: string;
  period_end: string;
  actual_value: number;
  attainment_percent?: number;
  status?: string;
  evidence?: string;
  created_at: string;
}

interface DashboardKPI {
  total_objectives: number;
  corporate_objectives: number;
  departmental_objectives: number;
  operational_objectives: number;
  recent_progress_entries: number;
  on_track_percentage: number;
  performance_breakdown: {
    on_track: number;
    at_risk: number;
    off_track: number;
  };
}

const StatusChip: React.FC<{ status?: string }> = ({ status }) => {
  const color = status === 'on_track' ? 'success' : status === 'at_risk' ? 'warning' : status === 'off_track' ? 'error' : 'default';
  return <Chip label={status || 'unknown'} color={color as 'success' | 'warning' | 'error' | 'default'} size="small" />;
};

const ObjectivesPage: React.FC = () => {
  const [enhancedObjectives, setEnhancedObjectives] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [dashboardKPIs, setDashboardKPIs] = useState<DashboardKPI | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  // Modal states
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showTargetForm, setShowTargetForm] = useState(false);
  const [showProgressForm, setShowProgressForm] = useState(false);
  const [showDetailView, setShowDetailView] = useState(false);
  const [selectedObjective, setSelectedObjective] = useState<any | null>(null); // Changed to any
  const [editingObjective, setEditingObjective] = useState<any | null>(null); // Changed to any
  const [selectedObjectiveId, setSelectedObjectiveId] = useState<number | null>(null);
  const [departments, setDepartments] = useState<any[]>([]);
  const [departmentFilterId, setDepartmentFilterId] = useState<string>('');
  
  // Form states
  const [createFormData, setCreateFormData] = useState<ObjectiveCreatePayload>({
    objective_code: '',
    title: '',
    description: '',
    category: '',
    measurement_unit: '',
    frequency: 'monthly',
    responsible_person_id: 2, // Default to admin user
    review_frequency: 'quarterly',
    created_by: 2
  });

  const [targetFormData, setTargetFormData] = useState<ObjectiveTargetPayload>({
    objective_id: 0,
    period_start: '',
    period_end: '',
    target_value: 0,
    weight: 1.0,
    is_lower_better: false,
    created_by: 2
  });

  const [progressFormData, setProgressFormData] = useState<ObjectiveProgressPayload>({
    objective_id: 0,
    period_start: '',
    period_end: '',
    actual_value: 0,
    evidence: '',
    created_by: 2
  });

  useEffect(() => {
    loadData();
    loadDepartments();
  }, []);

  const loadDepartments = async () => {
    try {
      const res: any = await departmentsAPI.list({ size: 1000 });
      setDepartments(res?.items || res?.data?.items || []);
    } catch (e) {
      setDepartments([]);
    }
  };

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load enhanced objectives
      const enhancedResponse = await objectivesAPI.listEnhancedObjectives({ department_id: departmentFilterId ? Number(departmentFilterId) : undefined });
      setEnhancedObjectives(enhancedResponse?.objectives || []);
      
      // Load dashboard KPIs
      const kpisResponse = await objectivesAPI.getDashboardKPIs();
      setDashboardKPIs(kpisResponse);
      
    } catch (e) {
      setError('Failed to load objectives. Please try again.');
      console.error('Error loading objectives:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
    loadData();
  };
  const handleApplyDepartmentFilter = () => {
    loadData();
  };

  const handleCreateObjective = async () => {
    try {
      setLoading(true);
      await objectivesAPI.createObjective(createFormData);
      setShowCreateForm(false);
      setCreateFormData({
        objective_code: '',
        title: '',
        description: '',
        category: '',
        measurement_unit: '',
        frequency: 'monthly',
        responsible_person_id: 2,
        review_frequency: 'quarterly',
        created_by: 2
      });
      handleRefresh();
    } catch (e) {
      setError('Failed to create objective. Please try again.');
      console.error('Error creating objective:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTarget = async () => {
    try {
      setLoading(true);
      await objectivesAPI.createTarget(targetFormData.objective_id, targetFormData);
      setShowTargetForm(false);
      setTargetFormData({
        objective_id: 0,
        period_start: '',
        period_end: '',
        target_value: 0,
        weight: 1.0,
        is_lower_better: false,
        created_by: 2
      });
      handleRefresh();
    } catch (e) {
      setError('Failed to create target. Please try again.');
      console.error('Error creating target:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProgress = async () => {
    try {
      setLoading(true);
      await objectivesAPI.createProgress(progressFormData.objective_id, progressFormData);
      setShowProgressForm(false);
      setProgressFormData({
        objective_id: 0,
        period_start: '',
        period_end: '',
        actual_value: 0,
        evidence: '',
        created_by: 2
      });
      handleRefresh();
    } catch (e) {
      setError('Failed to create progress. Please try again.');
      console.error('Error creating progress:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const blob = await objectivesAPI.exportObjectives('json');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'objectives-export.json';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (e) {
      setError('Failed to export objectives. Please try again.');
      console.error('Error exporting objectives:', e);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  if (loading && enhancedObjectives.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Food Safety Objectives Management</Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh Data">
            <IconButton onClick={handleRefresh} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export Objectives">
            <IconButton onClick={handleExport} color="primary">
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
            onClick={() => setShowCreateForm(true)}
          >
            New Objective
          </Button>
        </Box>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Dashboard KPIs */}
      {dashboardKPIs && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Objectives
                </Typography>
                <Typography variant="h4" component="div">
                  {dashboardKPIs.total_objectives}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  On Track
                </Typography>
                <Typography variant="h4" component="div" color="success.main">
                  {dashboardKPIs.performance_breakdown.on_track}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  At Risk
                </Typography>
                <Typography variant="h4" component="div" color="warning.main">
                  {dashboardKPIs.performance_breakdown.at_risk}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Off Track
                </Typography>
                <Typography variant="h4" component="div" color="error.main">
                  {dashboardKPIs.performance_breakdown.off_track}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Enhanced Objectives Only */}
      <Paper sx={{ width: '100%' }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="objectives tabs">
          <Tab label="Enhanced Objectives" />
        </Tabs>

        {activeTab === 0 && (
          <Box p={3}>
            <Grid container spacing={2}>
              {enhancedObjectives.map((objective) => (
                <Grid item xs={12} md={6} lg={4} key={objective.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        {objective.objective_code}
                      </Typography>
                      <Typography variant="h6" gutterBottom>
                        {objective.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {objective.description}
                      </Typography>
                      
                      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                        <Typography variant="body2">Type:</Typography>
                        <Chip 
                          label={objective.objective_type || 'N/A'} 
                          size="small" 
                          color={objective.objective_type === 'corporate' ? 'primary' : 'secondary'}
                        />
                      </Stack>
                      
                      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                        <Typography variant="body2">Level:</Typography>
                        <Chip 
                          label={objective.hierarchy_level || 'N/A'} 
                          size="small" 
                          variant="outlined"
                        />
                      </Stack>
                      
                      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                        <Typography variant="body2">Status:</Typography>
                        <StatusChip status={objective.status} />
                      </Stack>
                      
                      <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
                        <Button 
                          size="small" 
                          startIcon={<ViewIcon />}
                          onClick={() => {
                            setSelectedObjectiveId(objective.id);
                            setShowDetailView(true);
                          }}
                        >
                          View Details
                        </Button>
                        <Button 
                          size="small" 
                          startIcon={<EditIcon />}
                          onClick={() => {
                            setEditingObjective(objective);
                          }}
                        >
                          Edit
                        </Button>
                        <Button 
                          size="small" 
                          startIcon={<AddIcon />}
                          onClick={() => {
                            setTargetFormData(prev => ({ ...prev, objective_id: objective.id }));
                            setShowTargetForm(true);
                          }}
                        >
                          Add Target
                        </Button>
                        <Button 
                          size="small" 
                          startIcon={<AddIcon />}
                          onClick={() => {
                            setProgressFormData(prev => ({ ...prev, objective_id: objective.id }));
                            setShowProgressForm(true);
                          }}
                        >
                          Add Progress
                        </Button>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
            
            {(!loading && enhancedObjectives.length === 0) && (
              <Box textAlign="center" py={4}>
                <Typography variant="body2" color="text.secondary">
                  No enhanced objectives found.
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {/* Dashboard Tab removed */}
      </Paper>

      {/* Create Objective Dialog */}
      <Dialog open={showCreateForm} onClose={() => setShowCreateForm(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Objective</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Objective Code"
                value={createFormData.objective_code}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, objective_code: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Title"
                value={createFormData.title}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, title: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={createFormData.description}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, description: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Category"
                value={createFormData.category}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, category: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Measurement Unit"
                value={createFormData.measurement_unit}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, measurement_unit: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Frequency</InputLabel>
                <Select
                  value={createFormData.frequency}
                  onChange={(e) => setCreateFormData(prev => ({ ...prev, frequency: e.target.value }))}
                  label="Frequency"
                >
                  <MenuItem value="daily">Daily</MenuItem>
                  <MenuItem value="weekly">Weekly</MenuItem>
                  <MenuItem value="monthly">Monthly</MenuItem>
                  <MenuItem value="quarterly">Quarterly</MenuItem>
                  <MenuItem value="annually">Annually</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Review Frequency"
                value={createFormData.review_frequency}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, review_frequency: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCreateForm(false)}>Cancel</Button>
          <Button onClick={handleCreateObjective} variant="contained" disabled={loading}>
            {loading ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Target Dialog */}
      <Dialog open={showTargetForm} onClose={() => setShowTargetForm(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Target</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Period Start"
                type="date"
                value={targetFormData.period_start}
                onChange={(e) => setTargetFormData(prev => ({ ...prev, period_start: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Period End"
                type="date"
                value={targetFormData.period_end}
                onChange={(e) => setTargetFormData(prev => ({ ...prev, period_end: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Target Value"
                type="number"
                value={targetFormData.target_value}
                onChange={(e) => setTargetFormData(prev => ({ ...prev, target_value: parseFloat(e.target.value) || 0 }))}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Weight"
                type="number"
                value={targetFormData.weight}
                onChange={(e) => setTargetFormData(prev => ({ ...prev, weight: parseFloat(e.target.value) || 1.0 }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTargetForm(false)}>Cancel</Button>
          <Button onClick={handleCreateTarget} variant="contained" disabled={loading}>
            {loading ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Progress Dialog */}
      <Dialog open={showProgressForm} onClose={() => setShowProgressForm(false)} maxWidth="md" fullWidth>
        <DialogTitle>Record Progress</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Period Start"
                type="date"
                value={progressFormData.period_start}
                onChange={(e) => setProgressFormData(prev => ({ ...prev, period_start: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Period End"
                type="date"
                value={progressFormData.period_end}
                onChange={(e) => setProgressFormData(prev => ({ ...prev, period_end: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Actual Value"
                type="number"
                value={progressFormData.actual_value}
                onChange={(e) => setProgressFormData(prev => ({ ...prev, actual_value: parseFloat(e.target.value) || 0 }))}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Evidence"
                multiline
                rows={3}
                value={progressFormData.evidence}
                onChange={(e) => setProgressFormData(prev => ({ ...prev, evidence: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowProgressForm(false)}>Cancel</Button>
          <Button onClick={handleCreateProgress} variant="contained" disabled={loading}>
            {loading ? 'Recording...' : 'Record'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Objective Detail View */}
      <ObjectiveDetailView
        open={showDetailView}
        objectiveId={selectedObjectiveId}
        onClose={() => {
          setShowDetailView(false);
          setSelectedObjectiveId(null);
        }}
      />
    </Box>
  );
};

export default ObjectivesPage;

