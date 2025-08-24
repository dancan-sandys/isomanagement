import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Paper,
  Tooltip,
  Fab,
  Divider,
  Avatar,
  Badge,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Tabs,
  Tab,
  LinearProgress
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import { actionsLogAPI } from '../../services/actionsLogAPI';
import { 
  ActionLog, 
  ActionLogCreate, 
  ActionLogUpdate, 
  ActionStatus, 
  ActionPriority, 
  ActionSource 
} from '../../types/actionsLog';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  Flag as FlagIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Timeline as TimelineIcon,
  FilterList as FilterIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  KeyboardArrowUp as PriorityHighIcon,
  KeyboardArrowDown as PriorityLowIcon
} from '@mui/icons-material';

// ActionLog interface is now imported from types

interface ActionsLogManagementProps {
  onRefresh?: () => void;
}

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
      id={`actions-tabpanel-${index}`}
      aria-labelledby={`actions-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ActionsLogManagement: React.FC<ActionsLogManagementProps> = ({ onRefresh }) => {
  const [actions, setActions] = useState<ActionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAction, setEditingAction] = useState<ActionLog | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    action_source: ActionSource.CONTINUOUS_IMPROVEMENT,
    priority: ActionPriority.MEDIUM,
    status: ActionStatus.PENDING,
    due_date: '',
    progress_percent: 0
  });

  useEffect(() => {
    loadActions();
  }, []);

  const loadActions = async () => {
    try {
      setLoading(true);
      setError(null);
      const actionsData = await actionsLogAPI.getActions();
      setActions(actionsData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load actions. Please try again.');
      console.error('Error loading actions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAction = () => {
    setEditingAction(null);
    setFormData({
      title: '',
      description: '',
      action_source: ActionSource.CONTINUOUS_IMPROVEMENT,
      priority: ActionPriority.MEDIUM,
      status: ActionStatus.PENDING,
      due_date: '',
      progress_percent: 0
    });
    setDialogOpen(true);
  };

  const handleEditAction = (action: ActionLog) => {
    setEditingAction(action);
    setFormData({
      title: action.title,
      description: action.description || '',
      action_source: action.action_source,
      priority: action.priority,
      status: action.status,
      due_date: action.due_date || '',
      progress_percent: action.progress_percent
    });
    setDialogOpen(true);
  };

  const handleSaveAction = async () => {
    try {
      if (editingAction) {
        // Update existing action
        const updateData: ActionLogUpdate = {
          title: formData.title,
          description: formData.description,
          status: formData.status,
          priority: formData.priority,
          due_date: formData.due_date || undefined,
          progress_percent: formData.progress_percent
        };
        const updatedAction = await actionsLogAPI.updateAction(editingAction.id, updateData);
        setActions(actions.map(action =>
          action.id === editingAction.id ? updatedAction : action
        ));
      } else {
        // Create new action
        const createData: ActionLogCreate = {
          title: formData.title,
          description: formData.description,
          action_source: formData.action_source,
          priority: formData.priority,
          due_date: formData.due_date || undefined,
          assigned_by: 1 // TODO: Get current user ID from auth context
        };
        const newAction = await actionsLogAPI.createAction(createData);
        setActions([...actions, newAction]);
      }

      setDialogOpen(false);
      if (onRefresh) onRefresh();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save action. Please try again.');
      console.error('Error saving action:', err);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const getStatusColor = (status: ActionStatus) => {
    switch (status) {
      case ActionStatus.COMPLETED:
        return 'success';
      case ActionStatus.IN_PROGRESS:
        return 'primary';
      case ActionStatus.PENDING:
        return 'warning';
      case ActionStatus.CANCELLED:
        return 'error';
      case ActionStatus.OVERDUE:
        return 'error';
      case ActionStatus.ON_HOLD:
        return 'info';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority: ActionPriority) => {
    switch (priority) {
      case ActionPriority.CRITICAL:
      case ActionPriority.URGENT:
        return 'error';
      case ActionPriority.HIGH:
        return 'warning';
      case ActionPriority.MEDIUM:
        return 'info';
      case ActionPriority.LOW:
        return 'success';
      default:
        return 'default';
    }
  };

  const getPriorityIcon = (priority: ActionPriority) => {
    switch (priority) {
      case ActionPriority.CRITICAL:
      case ActionPriority.URGENT:
      case ActionPriority.HIGH:
        return <PriorityHighIcon />;
      case ActionPriority.LOW:
        return <PriorityLowIcon />;
      default:
        return <AssignmentIcon />;
    }
  };

  const getSourceIcon = (sourceType: ActionSource) => {
    switch (sourceType) {
      case ActionSource.INTERESTED_PARTY:
        return <PersonIcon />;
      case ActionSource.SWOT_ANALYSIS:
        return <BusinessIcon />;
      case ActionSource.PESTEL_ANALYSIS:
        return <FlagIcon />;
      case ActionSource.RISK_ASSESSMENT:
        return <WarningIcon />;
      default:
        return <AssignmentIcon />;
    }
  };

  const formatSourceType = (sourceType: ActionSource) => {
    return sourceType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const filteredActions = () => {
    switch (activeTab) {
      case 0: // All Actions
        return actions;
      case 1: // Open
        return actions.filter(action => action.status === ActionStatus.PENDING);
      case 2: // In Progress
        return actions.filter(action => action.status === ActionStatus.IN_PROGRESS);
      case 3: // Completed
        return actions.filter(action => action.status === ActionStatus.COMPLETED);
      case 4: // Overdue
        return actions.filter(action => 
          action.status !== ActionStatus.COMPLETED && 
          action.due_date && 
          new Date(action.due_date) < new Date()
        );
      default:
        return actions;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5" component="h2">
          Actions Log Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateAction}
        >
          Create Action
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Actions Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="actions tabs">
            <Tab label="All Actions" />
            <Tab label="Open" />
            <Tab label="In Progress" />
            <Tab label="Completed" />
            <Tab label="Overdue" />
          </Tabs>
        </Box>

        {/* All Actions Tab */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            {filteredActions().map((action) => (
              <Grid item xs={12} sm={6} md={4} key={action.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        {getSourceIcon(action.action_source)}
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {action.title}
                        </Typography>
                      </Box>
                      <Chip
                        label={action.status.replace(/_/g, ' ')}
                        color={getStatusColor(action.status) as any}
                        size="small"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {action.description}
                    </Typography>

                    <Box display="flex" alignItems="center" mb={2}>
                      <AssignmentIcon color="action" sx={{ mr: 1 }} />
                      <Typography variant="body2">
                        {action.assigned_user_name || 'Unassigned'}
                      </Typography>
                    </Box>

                    <Box mb={2}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="body2" color="text.secondary">
                          Progress
                        </Typography>
                        <Typography variant="body2">
                          {action.progress_percent}%
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={action.progress_percent}
                        color={action.progress_percent === 100 ? 'success' : 'primary'}
                      />
                    </Box>

                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Chip
                        icon={getPriorityIcon(action.priority)}
                        label={action.priority}
                        color={getPriorityColor(action.priority) as any}
                        size="small"
                      />
                      <Chip
                        label={formatSourceType(action.action_source)}
                        size="small"
                        variant="outlined"
                      />
                    </Box>

                    {action.due_date && (
                      <Box display="flex" alignItems="center" mb={2}>
                        <ScheduleIcon color="action" sx={{ mr: 1 }} />
                        <Typography variant="body2" color="text.secondary">
                          Due: {new Date(action.due_date).toLocaleDateString()}
                        </Typography>
                      </Box>
                    )}

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditAction(action)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="info">
                          <VisibilityIcon />
                        </IconButton>
                        <IconButton size="small" color="secondary">
                          <AssignmentIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(action.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Other tabs show the same filtered data */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            {filteredActions().map((action) => (
              <Grid item xs={12} sm={6} md={4} key={action.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        {getSourceIcon(action.action_source)}
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {action.title}
                        </Typography>
                      </Box>
                      <Chip
                        label={action.status.replace(/_/g, ' ')}
                        color={getStatusColor(action.status) as any}
                        size="small"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {action.description}
                    </Typography>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditAction(action)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="info">
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                      <Chip
                        icon={getPriorityIcon(action.priority)}
                        label={action.priority}
                        color={getPriorityColor(action.priority) as any}
                        size="small"
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Grid container spacing={3}>
            {filteredActions().map((action) => (
              <Grid item xs={12} sm={6} md={4} key={action.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        {getSourceIcon(action.action_source)}
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {action.title}
                        </Typography>
                      </Box>
                      <Chip
                        label={action.status.replace(/_/g, ' ')}
                        color={getStatusColor(action.status) as any}
                        size="small"
                      />
                    </Box>

                    <Box mb={2}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="body2" color="text.secondary">
                          Progress
                        </Typography>
                        <Typography variant="body2">
                          {action.progress_percent}%
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={action.progress_percent}
                        color="primary"
                      />
                    </Box>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditAction(action)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="info">
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(action.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <Grid container spacing={3}>
            {filteredActions().map((action) => (
              <Grid item xs={12} sm={6} md={4} key={action.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        <CheckCircleIcon color="success" />
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {action.title}
                        </Typography>
                      </Box>
                      <Chip
                        label="Completed"
                        color="success"
                        size="small"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {action.description}
                    </Typography>

                    {action.completed_at && (
                      <Box display="flex" alignItems="center" mb={2}>
                        <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                        <Typography variant="body2" color="text.secondary">
                          Completed: {new Date(action.completed_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    )}

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton size="small" color="info">
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(action.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={4}>
          <Grid container spacing={3}>
            {filteredActions().map((action) => (
              <Grid item xs={12} sm={6} md={4} key={action.id}>
                <Card sx={{ border: '2px solid #f44336' }}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        <ErrorIcon color="error" />
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {action.title}
                        </Typography>
                      </Box>
                      <Chip
                        label="Overdue"
                        color="error"
                        size="small"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {action.description}
                    </Typography>

                    {action.due_date && (
                      <Box display="flex" alignItems="center" mb={2}>
                        <ErrorIcon color="error" sx={{ mr: 1 }} />
                        <Typography variant="body2" color="error">
                          Overdue since: {new Date(action.due_date).toLocaleDateString()}
                        </Typography>
                      </Box>
                    )}

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditAction(action)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="error">
                          <PriorityHighIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" color="error">
                        URGENT
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>
      </Paper>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingAction ? 'Edit Action' : 'Create New Action'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Action Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                margin="normal"
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Source Type</InputLabel>
                <Select
                  value={formData.action_source}
                  onChange={(e) => setFormData({ ...formData, action_source: e.target.value as ActionSource })}
                  label="Source Type"
                >
                  <MenuItem value={ActionSource.CONTINUOUS_IMPROVEMENT}>Continuous Improvement</MenuItem>
                  <MenuItem value={ActionSource.INTERESTED_PARTY}>Interested Party</MenuItem>
                  <MenuItem value={ActionSource.SWOT_ANALYSIS}>SWOT Analysis</MenuItem>
                  <MenuItem value={ActionSource.PESTEL_ANALYSIS}>PESTEL Analysis</MenuItem>
                  <MenuItem value={ActionSource.RISK_ASSESSMENT}>Risk Assessment</MenuItem>
                  <MenuItem value={ActionSource.AUDIT_FINDING}>Audit Finding</MenuItem>
                  <MenuItem value={ActionSource.NON_CONFORMANCE}>Non Conformance</MenuItem>
                  <MenuItem value={ActionSource.MANAGEMENT_REVIEW}>Management Review</MenuItem>
                  <MenuItem value={ActionSource.COMPLAINT}>Complaint</MenuItem>
                  <MenuItem value={ActionSource.REGULATORY}>Regulatory</MenuItem>
                  <MenuItem value={ActionSource.STRATEGIC_PLANNING}>Strategic Planning</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value as ActionPriority })}
                  label="Priority"
                >
                  <MenuItem value={ActionPriority.LOW}>Low</MenuItem>
                  <MenuItem value={ActionPriority.MEDIUM}>Medium</MenuItem>
                  <MenuItem value={ActionPriority.HIGH}>High</MenuItem>
                  <MenuItem value={ActionPriority.CRITICAL}>Critical</MenuItem>
                  <MenuItem value={ActionPriority.URGENT}>Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value as ActionStatus })}
                  label="Status"
                >
                  <MenuItem value={ActionStatus.PENDING}>Pending</MenuItem>
                  <MenuItem value={ActionStatus.IN_PROGRESS}>In Progress</MenuItem>
                  <MenuItem value={ActionStatus.COMPLETED}>Completed</MenuItem>
                  <MenuItem value={ActionStatus.CANCELLED}>Cancelled</MenuItem>
                  <MenuItem value={ActionStatus.ON_HOLD}>On Hold</MenuItem>
                  <MenuItem value={ActionStatus.OVERDUE}>Overdue</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Due Date"
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                margin="normal"
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Progress Percentage"
                type="number"
                value={formData.progress_percent}
                onChange={(e) => setFormData({ ...formData, progress_percent: parseInt(e.target.value) })}
                margin="normal"
                inputProps={{ min: 0, max: 100 }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveAction}>
            {editingAction ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add action"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleCreateAction}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

export default ActionsLogManagement;

