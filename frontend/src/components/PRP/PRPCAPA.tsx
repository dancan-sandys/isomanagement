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
  Autocomplete,
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
import { prpAPI, usersAPI } from '../../services/api';

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
  const [users, setUsers] = useState<any[]>([]);
  
  // Debug users state
  useEffect(() => {
    console.log('Current users state:', users);
  }, [users]);
  
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
    action_code: '',
    trigger_type: 'trend_analysis',
    trigger_description: '',
    action_description: '',
    objective: '',
    responsible_person: 1,
    assigned_to: 1,
    program_id: programId || null,
    implementation_plan: '',
    resources_required: '',
    budget_estimate: 0,
    planned_start_date: '',
    planned_completion_date: '',
    success_criteria: '',
  });

  useEffect(() => {
    fetchData();
  }, [programId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch CAPA data and users
      const [correctiveResponse, preventiveResponse, dashboardResponse] = await Promise.all([
        prpAPI.getCorrectiveActions({}),
        prpAPI.getPreventiveActions({}),
        prpAPI.getCAPADashboard(),
      ]);

      // Fetch users separately to handle potential issues
      let usersResponse;
      try {
        usersResponse = await usersAPI.getUsers({});
        console.log('Users API response:', usersResponse);
        // The users API returns PaginatedResponse directly, not wrapped in ResponseModel
        if (usersResponse.items) {
          console.log('Setting users:', usersResponse.items);
          setUsers(usersResponse.items);
        } else {
          console.error('Users API failed - no items found:', usersResponse);
          setUsers([]);
        }
      } catch (userError) {
        console.error('Error fetching users:', userError);
        setUsers([]);
      }

      if (correctiveResponse.success) {
        setCorrectiveActions(correctiveResponse.data.items || []);
      }

      if (preventiveResponse.success) {
        setPreventiveActions(preventiveResponse.data.items || []);
      }

      if (dashboardResponse.success) {
        setDashboardData(dashboardResponse.data);
      }

      if (usersResponse.success) {
        console.log('Users response:', usersResponse);
        setUsers(usersResponse.data.items || usersResponse.data || []);
      } else {
        console.error('Users API failed:', usersResponse);
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
      action_code: '',
      trigger_type: 'trend_analysis',
      trigger_description: '',
      action_description: '',
      objective: '',
      responsible_person: 1,
      assigned_to: 1,
      program_id: programId || null,
      implementation_plan: '',
      resources_required: '',
      budget_estimate: 0,
      planned_start_date: '',
      planned_completion_date: '',
      success_criteria: '',
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
                    {action.description || 'No description'}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {action.root_cause ? 
                      (action.root_cause.length > 50 ? 
                        `${action.root_cause.substring(0, 50)}...` : 
                        action.root_cause) : 
                      'No root cause'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    icon={getPriorityIcon(action.priority || 'medium')}
                    label={action.priority || 'medium'}
                    color={getPriorityColor(action.priority || 'medium') as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    icon={getStatusIcon(action.status)}
                    label={action.status ? action.status.replace('_', ' ') : 'unknown'}
                    color={getStatusColor(action.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{action.assigned_to || 'Unassigned'}</TableCell>
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
                    label={action.status ? action.status.replace('_', ' ') : 'unknown'}
                    color={getStatusColor(action.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{action.assigned_to || 'Unassigned'}</TableCell>
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
            <Autocomplete
              options={users}
              getOptionLabel={(option) => option.full_name || option.username || ''}
              value={users.find(user => user.id === correctiveForm.responsible_person) || null}
              noOptionsText="No users found"
              loading={users.length === 0}
              loadingText="Loading users..."
              onChange={(event, newValue) => {
                setCorrectiveForm({ 
                  ...correctiveForm, 
                  responsible_person: newValue ? newValue.id : 1 
                });
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Responsible Person"
                  required
                  placeholder="Search for a user..."
                />
              )}
              renderOption={(props, option) => (
                <Box component="li" {...props}>
                  <Box>
                    <Typography variant="body1">{option.full_name || option.username}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {option.email}
                    </Typography>
                  </Box>
                </Box>
              )}
            />
          </Grid>
          <Grid item xs={6}>
            <Autocomplete
              options={users}
              getOptionLabel={(option) => option.full_name || option.username || ''}
              value={users.find(user => user.id === correctiveForm.assigned_to) || null}
              noOptionsText="No users found"
              loading={users.length === 0}
              loadingText="Loading users..."
              onChange={(event, newValue) => {
                setCorrectiveForm({ 
                  ...correctiveForm, 
                  assigned_to: newValue ? newValue.id : 1 
                });
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Assigned To"
                  required
                  placeholder="Search for a user..."
                />
              )}
              renderOption={(props, option) => (
                <Box component="li" {...props}>
                  <Box>
                    <Typography variant="body1">{option.full_name || option.username}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {option.email}
                    </Typography>
                  </Box>
                </Box>
              )}
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
              label="Action Code"
              value={preventiveForm.action_code}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, action_code: e.target.value })}
              placeholder="e.g., PA-2024-001"
              required
            />
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Trigger Type</InputLabel>
              <Select
                value={preventiveForm.trigger_type}
                onChange={(e) => setPreventiveForm({ ...preventiveForm, trigger_type: e.target.value })}
                required
              >
                <MenuItem value="trend_analysis">Trend Analysis</MenuItem>
                <MenuItem value="risk_assessment">Risk Assessment</MenuItem>
                <MenuItem value="audit_finding">Audit Finding</MenuItem>
                <MenuItem value="customer_feedback">Customer Feedback</MenuItem>
                <MenuItem value="regulatory_change">Regulatory Change</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6}>
            <Autocomplete
              options={users}
              getOptionLabel={(option) => option.full_name || option.username || ''}
              value={users.find(user => user.id === preventiveForm.responsible_person) || null}
              noOptionsText="No users found"
              loading={users.length === 0}
              loadingText="Loading users..."
              onChange={(event, newValue) => {
                setPreventiveForm({ 
                  ...preventiveForm, 
                  responsible_person: newValue ? newValue.id : 1 
                });
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Responsible Person"
                  required
                  placeholder="Search for a user..."
                />
              )}
              renderOption={(props, option) => (
                <Box component="li" {...props}>
                  <Box>
                    <Typography variant="body1">{option.full_name || option.username}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {option.email}
                    </Typography>
                  </Box>
                </Box>
              )}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Trigger Description"
              value={preventiveForm.trigger_description}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, trigger_description: e.target.value })}
              multiline
              rows={2}
              placeholder="Describe what triggered this preventive action"
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Action Description"
              value={preventiveForm.action_description}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, action_description: e.target.value })}
              multiline
              rows={3}
              placeholder="Describe the preventive action to be taken"
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Objective"
              value={preventiveForm.objective}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, objective: e.target.value })}
              multiline
              rows={2}
              placeholder="What is the objective of this preventive action?"
              required
            />
          </Grid>
          <Grid item xs={6}>
            <Autocomplete
              options={users}
              getOptionLabel={(option) => option.full_name || option.username || ''}
              value={users.find(user => user.id === preventiveForm.assigned_to) || null}
              noOptionsText="No users found"
              loading={users.length === 0}
              loadingText="Loading users..."
              onChange={(event, newValue) => {
                setPreventiveForm({ 
                  ...preventiveForm, 
                  assigned_to: newValue ? newValue.id : 1 
                });
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Assigned To"
                  required
                  placeholder="Search for a user..."
                />
              )}
              renderOption={(props, option) => (
                <Box component="li" {...props}>
                  <Box>
                    <Typography variant="body1">{option.full_name || option.username}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {option.email}
                    </Typography>
                  </Box>
                </Box>
              )}
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Budget Estimate"
              type="number"
              value={preventiveForm.budget_estimate}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, budget_estimate: parseFloat(e.target.value) || 0 })}
              placeholder="0.00"
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Planned Start Date"
              type="date"
              value={preventiveForm.planned_start_date}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, planned_start_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Planned Completion Date"
              type="date"
              value={preventiveForm.planned_completion_date}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, planned_completion_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Implementation Plan"
              value={preventiveForm.implementation_plan}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, implementation_plan: e.target.value })}
              multiline
              rows={3}
              placeholder="Describe the implementation plan"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Resources Required"
              value={preventiveForm.resources_required}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, resources_required: e.target.value })}
              multiline
              rows={2}
              placeholder="List resources required for implementation"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Success Criteria"
              value={preventiveForm.success_criteria}
              onChange={(e) => setPreventiveForm({ ...preventiveForm, success_criteria: e.target.value })}
              multiline
              rows={2}
              placeholder="Define success criteria for this preventive action"
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
