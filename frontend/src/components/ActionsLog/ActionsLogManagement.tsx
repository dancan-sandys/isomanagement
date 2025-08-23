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
  LinearProgress,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/material';
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

interface ActionLog {
  id: number;
  title: string;
  description?: string;
  source_type: 'interested_party' | 'swot_analysis' | 'pestel_analysis' | 'risk_assessment' | 'manual';
  source_id?: number;
  status: 'open' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assigned_to?: number;
  assigned_by?: number;
  due_date?: string;
  completed_date?: string;
  created_at: string;
  updated_at?: string;
  progress_percentage: number;
  assigned_user_name?: string;
  assigned_by_name?: string;
  source_name?: string;
}

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
    source_type: 'manual',
    priority: 'medium',
    status: 'open',
    due_date: '',
    progress_percentage: 0
  });

  useEffect(() => {
    loadActions();
  }, []);

  const loadActions = async () => {
    try {
      setLoading(true);
      setError(null);
      // Mock data for now - replace with actual API call
      const mockActions: ActionLog[] = [
        {
          id: 1,
          title: 'Implement new food safety training program',
          description: 'Develop and implement comprehensive food safety training for all production staff',
          source_type: 'interested_party',
          source_id: 1,
          status: 'in_progress',
          priority: 'high',
          assigned_to: 1,
          assigned_by: 2,
          due_date: '2025-09-15',
          created_at: '2025-08-20',
          progress_percentage: 65,
          assigned_user_name: 'John Doe',
          assigned_by_name: 'Jane Smith',
          source_name: 'Customer Feedback'
        },
        {
          id: 2,
          title: 'Update HACCP documentation',
          description: 'Review and update all HACCP documentation to ensure compliance',
          source_type: 'risk_assessment',
          source_id: 2,
          status: 'open',
          priority: 'medium',
          assigned_to: 3,
          assigned_by: 1,
          due_date: '2025-08-30',
          created_at: '2025-08-18',
          progress_percentage: 0,
          assigned_user_name: 'Mike Johnson',
          assigned_by_name: 'Admin User',
          source_name: 'Risk Assessment'
        },
        {
          id: 3,
          title: 'Install new temperature monitoring system',
          description: 'Install and configure new temperature monitoring system in production area',
          source_type: 'swot_analysis',
          source_id: 3,
          status: 'completed',
          priority: 'critical',
          assigned_to: 4,
          assigned_by: 1,
          due_date: '2025-08-10',
          completed_date: '2025-08-08',
          created_at: '2025-08-01',
          progress_percentage: 100,
          assigned_user_name: 'Sarah Wilson',
          assigned_by_name: 'Admin User',
          source_name: 'SWOT Analysis'
        }
      ];
      setActions(mockActions);
    } catch (err) {
      setError('Failed to load actions. Please try again.');
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
      source_type: 'manual',
      priority: 'medium',
      status: 'open',
      due_date: '',
      progress_percentage: 0
    });
    setDialogOpen(true);
  };

  const handleEditAction = (action: ActionLog) => {
    setEditingAction(action);
    setFormData({
      title: action.title,
      description: action.description || '',
      source_type: action.source_type,
      priority: action.priority,
      status: action.status,
      due_date: action.due_date || '',
      progress_percentage: action.progress_percentage
    });
    setDialogOpen(true);
  };

  const handleSaveAction = async () => {
    try {
      // Mock save - replace with actual API call
      if (editingAction) {
        const updatedActions = actions.map(action =>
          action.id === editingAction.id
            ? { ...action, ...formData }
            : action
        );
        setActions(updatedActions);
      } else {
        const newAction: ActionLog = {
          id: Math.max(...actions.map(a => a.id)) + 1,
          ...formData,
          created_at: new Date().toISOString(),
          assigned_user_name: 'Current User',
          assigned_by_name: 'Current User',
          source_name: 'Manual Entry'
        };
        setActions([...actions, newAction]);
      }

      setDialogOpen(false);
      if (onRefresh) onRefresh();
    } catch (err) {
      setError('Failed to save action. Please try again.');
      console.error('Error saving action:', err);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'open':
        return 'warning';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
      case 'high':
        return <PriorityHighIcon />;
      case 'low':
        return <PriorityLowIcon />;
      default:
        return <AssignmentIcon />;
    }
  };

  const getSourceIcon = (sourceType: string) => {
    switch (sourceType) {
      case 'interested_party':
        return <PersonIcon />;
      case 'swot_analysis':
        return <BusinessIcon />;
      case 'pestel_analysis':
        return <FlagIcon />;
      case 'risk_assessment':
        return <WarningIcon />;
      default:
        return <AssignmentIcon />;
    }
  };

  const formatSourceType = (sourceType: string) => {
    return sourceType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const filteredActions = () => {
    switch (activeTab) {
      case 0: // All Actions
        return actions;
      case 1: // Open
        return actions.filter(action => action.status === 'open');
      case 2: // In Progress
        return actions.filter(action => action.status === 'in_progress');
      case 3: // Completed
        return actions.filter(action => action.status === 'completed');
      case 4: // Overdue
        return actions.filter(action => 
          action.status !== 'completed' && 
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
                        {getSourceIcon(action.source_type)}
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {action.title}
                        </Typography>
                      </Box>
                      <Chip
                        label={action.status.replace('_', ' ')}
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
                          {action.progress_percentage}%
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={action.progress_percentage}
                        color={action.progress_percentage === 100 ? 'success' : 'primary'}
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
                        label={formatSourceType(action.source_type)}
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
                        {getSourceIcon(action.source_type)}
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {action.title}
                        </Typography>
                      </Box>
                      <Chip
                        label={action.status.replace('_', ' ')}
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
                        {getSourceIcon(action.source_type)}
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {action.title}
                        </Typography>
                      </Box>
                      <Chip
                        label={action.status.replace('_', ' ')}
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
                          {action.progress_percentage}%
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={action.progress_percentage}
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

                    {action.completed_date && (
                      <Box display="flex" alignItems="center" mb={2}>
                        <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                        <Typography variant="body2" color="text.secondary">
                          Completed: {new Date(action.completed_date).toLocaleDateString()}
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
                  value={formData.source_type}
                  onChange={(e) => setFormData({ ...formData, source_type: e.target.value })}
                  label="Source Type"
                >
                  <MenuItem value="manual">Manual Entry</MenuItem>
                  <MenuItem value="interested_party">Interested Party</MenuItem>
                  <MenuItem value="swot_analysis">SWOT Analysis</MenuItem>
                  <MenuItem value="pestel_analysis">PESTEL Analysis</MenuItem>
                  <MenuItem value="risk_assessment">Risk Assessment</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  label="Priority"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  label="Status"
                >
                  <MenuItem value="open">Open</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="cancelled">Cancelled</MenuItem>
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
                value={formData.progress_percentage}
                onChange={(e) => setFormData({ ...formData, progress_percentage: parseInt(e.target.value) })}
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

