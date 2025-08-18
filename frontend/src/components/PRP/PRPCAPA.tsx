import React, { useState, useEffect } from 'react';
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
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Card,
  CardContent,
  Alert,
  LinearProgress,
  Tooltip,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Rating,
  Badge,
} from '@mui/material';
import {
  Add,
  Visibility,
  Edit,
  Delete,
  Warning,
  CheckCircle,
  Error,
  Info,
  Refresh,
  Assignment,
  Schedule,
  TrendingUp,
  TrendingDown,
  Assessment,
  Build,
  Security,
  ExpandMore,
  PlayArrow,
  Stop,
  Done,
  Pending,
  PriorityHigh,
  LowPriority,
  AttachMoney,
  Timeline,
  Person,
  CalendarToday,
} from '@mui/icons-material';
import { prpAPI } from '../../services/api';

interface CorrectiveAction {
  id: number;
  action_code: string;
  title: string;
  description: string;
  root_cause: string;
  action_type: string;
  priority: string;
  status: string;
  assigned_to: string;
  due_date: string;
  completion_date?: string;
  effectiveness_rating?: number;
  cost_estimate?: number;
  actual_cost?: number;
  verification_method: string;
  verification_date?: string;
  verified_by?: string;
  program_id: number;
  program_name: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

interface PreventiveAction {
  id: number;
  action_code: string;
  title: string;
  description: string;
  potential_issue: string;
  action_type: string;
  priority: string;
  status: string;
  assigned_to: string;
  start_date?: string;
  due_date: string;
  completion_date?: string;
  effectiveness_rating?: number;
  cost_estimate?: number;
  actual_cost?: number;
  verification_method: string;
  verification_date?: string;
  verified_by?: string;
  program_id: number;
  program_name: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

interface CAPADashboard {
  total_corrective_actions: number;
  total_preventive_actions: number;
  completed_actions: number;
  overdue_actions: number;
  in_progress_actions: number;
  pending_actions: number;
  average_completion_time: number;
  effectiveness_rating: number;
  cost_summary: {
    total_estimated: number;
    total_actual: number;
    variance: number;
  };
  recent_actions: Array<CorrectiveAction | PreventiveAction>;
  overdue_actions_list: Array<CorrectiveAction | PreventiveAction>;
}

const PRPCAPA: React.FC<{ programId?: number }> = ({ programId }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [correctiveActions, setCorrectiveActions] = useState<CorrectiveAction[]>([]);
  const [preventiveActions, setPreventiveActions] = useState<PreventiveAction[]>([]);
  const [dashboardData, setDashboardData] = useState<CAPADashboard | null>({
    total_corrective_actions: 0,
    total_preventive_actions: 0,
    completed_actions: 0,
    overdue_actions: 0,
    average_completion_time: 0,
    effectiveness_rating: 0,
    cost_summary: {
      total_estimated: 0,
      total_actual: 0,
      variance: 0
    },
    overdue_actions_list: []
  } as CAPADashboard);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Dialog states
  const [openCorrectiveDialog, setOpenCorrectiveDialog] = useState(false);
  const [openPreventiveDialog, setOpenPreventiveDialog] = useState(false);
  const [selectedAction, setSelectedAction] = useState<CorrectiveAction | PreventiveAction | null>(null);

  // Form states
  const [correctiveForm, setCorrectiveForm] = useState({
    action_code: '',
    source_type: 'inspection',
    source_id: 1,
    checklist_id: null,
    program_id: programId || null,
    non_conformance_description: '',
    non_conformance_date: new Date().toISOString().split('T')[0],
    severity: 'medium',
    immediate_cause: '',
    root_cause_analysis: '',
    root_cause_category: '',
    action_description: '',
    action_type: 'corrective',
    responsible_person: 1,
    assigned_to: 1,
    target_completion_date: '',
    cost_estimate: 0,
    verification_method: '',
    effectiveness_rating: 3,
  });

  const [preventiveForm, setPreventiveForm] = useState({
    title: '',
    description: '',
    potential_issue: '',
    action_type: '',
    priority: 'medium',
    assigned_to: '',
    start_date: '',
    due_date: '',
    effectiveness_rating: 3,
    cost_estimate: 0,
    verification_method: '',
  });

  useEffect(() => {
    fetchData();
  }, [programId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch CAPA data
      const [correctiveResponse, preventiveResponse, dashboardResponse] = await Promise.all([
        prpAPI.getCorrectiveActions({}),
        prpAPI.getPreventiveActions({}),
        prpAPI.getCAPADashboard(),
      ]);

      if (correctiveResponse.success) {
        setCorrectiveActions(correctiveResponse.data.items || []);
      }

      if (preventiveResponse.success) {
        setPreventiveActions(preventiveResponse.data.items || []);
      }

      if (dashboardResponse.success) {
        setDashboardData(dashboardResponse.data);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load CAPA data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCorrectiveAction = async () => {
    try {
      const response = await prpAPI.createCorrectiveAction(correctiveForm);
      if (response.success) {
        setSuccess('Corrective action created successfully');
        setOpenCorrectiveDialog(false);
        resetCorrectiveForm();
        fetchData();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create corrective action');
    }
  };

  const handleCreatePreventiveAction = async () => {
    try {
      const response = await prpAPI.createPreventiveAction(preventiveForm);
      if (response.success) {
        setSuccess('Preventive action created successfully');
        setOpenPreventiveDialog(false);
        resetPreventiveForm();
        fetchData();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create preventive action');
    }
  };

  const handleCompleteAction = async (actionId: number, actionType: 'corrective' | 'preventive') => {
    try {
      const response = actionType === 'corrective' 
        ? await prpAPI.completeCorrectiveAction(actionId, {})
        : await prpAPI.completePreventiveAction(actionId, {});
      
      if (response.success) {
        setSuccess(`${actionType === 'corrective' ? 'Corrective' : 'Preventive'} action completed successfully`);
        fetchData();
      }
    } catch (err: any) {
      setError(err.message || `Failed to complete ${actionType} action`);
    }
  };

  const handleStartPreventiveAction = async (actionId: number) => {
    try {
      const response = await prpAPI.startPreventiveAction(actionId);
      if (response.success) {
        setSuccess('Preventive action started successfully');
        fetchData();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to start preventive action');
    }
  };

  const resetCorrectiveForm = () => {
    setCorrectiveForm({
      action_code: '',
      source_type: 'inspection',
      source_id: 1,
      checklist_id: null,
      program_id: programId || null,
      non_conformance_description: '',
      non_conformance_date: new Date().toISOString().split('T')[0],
      severity: 'medium',
      immediate_cause: '',
      root_cause_analysis: '',
      root_cause_category: '',
      action_description: '',
      action_type: 'corrective',
      responsible_person: 1,
      assigned_to: 1,
      target_completion_date: '',
      cost_estimate: 0,
      verification_method: '',
      effectiveness_rating: 3,
    });
  };

  const resetPreventiveForm = () => {
    setPreventiveForm({
      title: '',
      description: '',
      potential_issue: '',
      action_type: '',
      priority: 'medium',
      assigned_to: '',
      start_date: '',
      due_date: '',
      effectiveness_rating: 3,
      cost_estimate: 0,
      verification_method: '',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'success';
      case 'in_progress': return 'info';
      case 'pending': return 'warning';
      case 'overdue': return 'error';
      case 'not_started': return 'default';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'high':
      case 'critical':
        return <PriorityHigh />;
      case 'medium':
        return <LowPriority />;
      case 'low':
        return <LowPriority />;
      default:
        return <LowPriority />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return <CheckCircle />;
      case 'in_progress':
        return <PlayArrow />;
      case 'pending':
        return <Pending />;
      case 'overdue':
        return <Error />;
      case 'not_started':
        return <Stop />;
      default:
        return <Info />;
    }
  };

  const renderDashboard = () => {
    if (!dashboardData) return null;

    return (
      <Box>
        <Typography variant="h6" gutterBottom>CAPA Dashboard</Typography>
        
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Actions
                    </Typography>
                    <Typography variant="h4">
                      {(dashboardData.total_corrective_actions || 0) + (dashboardData.total_preventive_actions || 0)}
                    </Typography>
                  </Box>
                  <Assessment color="primary" />
                </Box>
                <Typography variant="body2" color="textSecondary">
                  {dashboardData.completed_actions || 0} completed
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Overdue Actions
                    </Typography>
                    <Typography variant="h4" color="error">
                      {dashboardData.overdue_actions || 0}
                    </Typography>
                  </Box>
                  <Warning color="error" />
                </Box>
                <Typography variant="body2" color="textSecondary">
                  Requires attention
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Avg Completion Time
                    </Typography>
                    <Typography variant="h4">
                      {dashboardData.average_completion_time ? dashboardData.average_completion_time.toFixed(1) : '0.0'}d
                    </Typography>
                  </Box>
                  <Timeline color="primary" />
                </Box>
                <Typography variant="body2" color="textSecondary">
                  Days to complete
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Effectiveness
                    </Typography>
                    <Typography variant="h4">
                      {dashboardData.effectiveness_rating ? dashboardData.effectiveness_rating.toFixed(1) : '0.0'}
                    </Typography>
                  </Box>
                  <TrendingUp color="success" />
                </Box>
                <Typography variant="body2" color="textSecondary">
                  Average rating
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Cost Summary</Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <AttachMoney />
                    </ListItemIcon>
                    <ListItemText
                      primary="Total Estimated Cost"
                      secondary={`$${dashboardData.cost_summary?.total_estimated?.toLocaleString() || '0'}`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <AttachMoney />
                    </ListItemIcon>
                    <ListItemText
                      primary="Total Actual Cost"
                      secondary={`$${dashboardData.cost_summary?.total_actual?.toLocaleString() || '0'}`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <TrendingDown />
                    </ListItemIcon>
                    <ListItemText
                      primary="Variance"
                      secondary={`$${dashboardData.cost_summary?.variance?.toLocaleString() || '0'}`}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Overdue Actions</Typography>
                <List>
                  {(dashboardData.overdue_actions_list || []).slice(0, 5).map((action) => (
                    <ListItem key={action.id}>
                      <ListItemIcon>
                        <Warning color="error" />
                      </ListItemIcon>
                      <ListItemText
                        primary={action.title}
                        secondary={`Due: ${new Date(action.due_date).toLocaleDateString()}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderCorrectiveActions = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Corrective Actions</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenCorrectiveDialog(true)}
        >
          New Corrective Action
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Action Code</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Assigned To</TableCell>
              <TableCell>Target Date</TableCell>
              <TableCell>Effectiveness</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {correctiveActions.map((action) => (
              <TableRow key={action.id}>
                <TableCell>{action.action_code}</TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold">
                    {action.action_description || 'No description'}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {action.non_conformance_description ? 
                      (action.non_conformance_description.length > 50 ? 
                        `${action.non_conformance_description.substring(0, 50)}...` : 
                        action.non_conformance_description) : 
                      'No non-conformance description'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    icon={getPriorityIcon(action.priority)}
                    label={action.priority}
                    color={getPriorityColor(action.priority) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    icon={getStatusIcon(action.status)}
                    label={action.status.replace('_', ' ')}
                    color={getStatusColor(action.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{action.assigned_to}</TableCell>
                <TableCell>
                  {new Date(action.due_date).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  {action.effectiveness_rating ? (
                    <Rating value={action.effectiveness_rating} readOnly size="small" />
                  ) : (
                    <Typography variant="caption">Not rated</Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    <Tooltip title="View Details">
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    {action.status !== 'completed' && (
                      <Tooltip title="Mark Complete">
                        <IconButton 
                          size="small"
                          onClick={() => handleCompleteAction(action.id, 'corrective')}
                        >
                          <Done />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderPreventiveActions = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Preventive Actions</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenPreventiveDialog(true)}
        >
          New Preventive Action
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Action Code</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Assigned To</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell>Effectiveness</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {preventiveActions.map((action) => (
              <TableRow key={action.id}>
                <TableCell>{action.action_code}</TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold">
                    {action.title}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {action.description ? 
                      (action.description.length > 50 ? 
                        `${action.description.substring(0, 50)}...` : 
                        action.description) : 
                      'No description'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    icon={getPriorityIcon(action.priority)}
                    label={action.priority}
                    color={getPriorityColor(action.priority) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    icon={getStatusIcon(action.status)}
                    label={action.status.replace('_', ' ')}
                    color={getStatusColor(action.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{action.assigned_to}</TableCell>
                <TableCell>
                  {new Date(action.due_date).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  {action.effectiveness_rating ? (
                    <Rating value={action.effectiveness_rating} readOnly size="small" />
                  ) : (
                    <Typography variant="caption">Not rated</Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    <Tooltip title="View Details">
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    {action.status === 'not_started' && (
                      <Tooltip title="Start Action">
                        <IconButton 
                          size="small"
                          onClick={() => handleStartPreventiveAction(action.id)}
                        >
                          <PlayArrow />
                        </IconButton>
                      </Tooltip>
                    )}
                    {action.status !== 'completed' && action.status !== 'not_started' && (
                      <Tooltip title="Mark Complete">
                        <IconButton 
                          size="small"
                          onClick={() => handleCompleteAction(action.id, 'preventive')}
                        >
                          <Done />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderCorrectiveDialog = () => (
    <Dialog open={openCorrectiveDialog} onClose={() => setOpenCorrectiveDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>Create Corrective Action</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Action Code"
              value={correctiveForm.action_code}
              onChange={(e) => setCorrectiveForm({ ...correctiveForm, action_code: e.target.value })}
              placeholder="e.g., CA-001"
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Non-Conformance Description"
              value={correctiveForm.non_conformance_description}
              onChange={(e) => setCorrectiveForm({ ...correctiveForm, non_conformance_description: e.target.value })}
              multiline
              rows={3}
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Action Description"
              value={correctiveForm.action_description}
              onChange={(e) => setCorrectiveForm({ ...correctiveForm, action_description: e.target.value })}
              multiline
              rows={2}
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Root Cause Analysis"
              value={correctiveForm.root_cause_analysis}
              onChange={(e) => setCorrectiveForm({ ...correctiveForm, root_cause_analysis: e.target.value })}
              multiline
              rows={2}
            />
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Severity</InputLabel>
              <Select
                value={correctiveForm.severity}
                onChange={(e) => setCorrectiveForm({ ...correctiveForm, severity: e.target.value })}
                required
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Non-Conformance Date"
              type="date"
              value={correctiveForm.non_conformance_date}
              onChange={(e) => setCorrectiveForm({ ...correctiveForm, non_conformance_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Target Completion Date"
              type="date"
              value={correctiveForm.target_completion_date}
              onChange={(e) => setCorrectiveForm({ ...correctiveForm, target_completion_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Cost Estimate"
              type="number"
              value={correctiveForm.cost_estimate}
              onChange={(e) => setCorrectiveForm({ ...correctiveForm, cost_estimate: parseFloat(e.target.value) || 0 })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Verification Method"
              value={correctiveForm.verification_method}
              onChange={(e) => setCorrectiveForm({ ...correctiveForm, verification_method: e.target.value })}
              multiline
              rows={2}
              required
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setOpenCorrectiveDialog(false)}>Cancel</Button>
        <Button onClick={handleCreateCorrectiveAction} variant="contained">
          Create Action
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderPreventiveDialog = () => (
    <Dialog open={openPreventiveDialog} onClose={() => setOpenPreventiveDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>Create Preventive Action</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Title"
              value={preventiveForm.title}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, title: e.target.value })}
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              value={preventiveForm.description}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, description: e.target.value })}
              multiline
              rows={3}
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Potential Issue"
              value={preventiveForm.potential_issue}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, potential_issue: e.target.value })}
              multiline
              rows={2}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Action Type</InputLabel>
              <Select
                value={preventiveForm.action_type}
                onChange={(e) => setPreventiveForm({ ...preventiveForm, action_type: e.target.value })}
                required
              >
                <MenuItem value="proactive">Proactive</MenuItem>
                <MenuItem value="predictive">Predictive</MenuItem>
                <MenuItem value="preventive">Preventive</MenuItem>
                <MenuItem value="improvement">Improvement</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={preventiveForm.priority}
                onChange={(e) => setPreventiveForm({ ...preventiveForm, priority: e.target.value })}
                required
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Assigned To"
              value={preventiveForm.assigned_to}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, assigned_to: e.target.value })}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Start Date"
              type="date"
              value={preventiveForm.start_date}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, start_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Due Date"
              type="date"
              value={preventiveForm.due_date}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, due_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Cost Estimate"
              type="number"
              value={preventiveForm.cost_estimate}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, cost_estimate: parseFloat(e.target.value) || 0 })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Verification Method"
              value={preventiveForm.verification_method}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, verification_method: e.target.value })}
              multiline
              rows={2}
              required
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setOpenPreventiveDialog(false)}>Cancel</Button>
        <Button onClick={handleCreatePreventiveAction} variant="contained">
          Create Action
        </Button>
      </DialogActions>
    </Dialog>
  );

  if (loading) {
    return (
      <Box>
        <LinearProgress />
        <Typography>Loading CAPA data...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Dashboard" icon={<Assessment />} />
          <Tab label="Corrective Actions" icon={<Build />} />
          <Tab label="Preventive Actions" icon={<Security />} />
        </Tabs>
      </Box>

      {activeTab === 0 && renderDashboard()}
      {activeTab === 1 && renderCorrectiveActions()}
      {activeTab === 2 && renderPreventiveActions()}

      {renderCorrectiveDialog()}
      {renderPreventiveDialog()}
    </Box>
  );
};

export default PRPCAPA;
