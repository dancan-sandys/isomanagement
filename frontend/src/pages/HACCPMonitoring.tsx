import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  TextField,
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
  Paper,
  Stack,
  Autocomplete,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Badge,
} from '@mui/material';
import {
  Science,
  Warning,
  CheckCircle,
  Error,
  Timer,
  Refresh,
  Add,
  Visibility,
  TrendingUp,
  Assignment,
  NotificationImportant,
  Schedule,
  Assessment,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchProducts } from '../store/slices/haccpSlice';
import { haccpAPI, traceabilityAPI } from '../services/api';
import PageHeader from '../components/UI/PageHeader';
import HACCPBreadcrumbs from '../components/UI/HACCPBreadcrumbs';
import MonitoringTrendCharts from '../components/HACCP/MonitoringTrendCharts';

interface MonitoringTask {
  id: string;
  ccpId: number;
  ccpName: string;
  ccpNumber: string;
  productName: string;
  productId: number;
  status: 'due' | 'overdue' | 'completed' | 'in_progress';
  priority: 'low' | 'medium' | 'high' | 'critical';
  dueTime: string;
  frequency: string;
  lastMonitored?: string;
  measuredValue?: number;
  unit?: string;
  criticalLimits: {
    min?: number;
    max?: number;
    unit: string;
  };
  responsible?: string;
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
      id={`monitoring-tabpanel-${index}`}
      aria-labelledby={`monitoring-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const HACCPMonitoring: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { products } = useSelector((state: RootState) => state.haccp);
  const { user } = useSelector((state: RootState) => state.auth);

  const [selectedTab, setSelectedTab] = useState(0);
  const [monitoringTasks, setMonitoringTasks] = useState<MonitoringTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<MonitoringTask | null>(null);
  const [monitoringDialogOpen, setMonitoringDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [monitoringForm, setMonitoringForm] = useState({
    batchNumber: '',
    measuredValue: '',
    unit: '',
    notes: '',
    conditions: '',
  });

  const [batchOptions, setBatchOptions] = useState<any[]>([]);
  const [batchSearch, setBatchSearch] = useState('');
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    dispatch(fetchProducts());
    loadMonitoringTasks();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(loadMonitoringTasks, 30000);
    setRefreshInterval(interval);
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [dispatch]);

  useEffect(() => {
    if (batchSearch.length > 2) {
      loadBatches();
    }
  }, [batchSearch]);

  const loadMonitoringTasks = async () => {
    setLoading(true);
    try {
      // Mock data - replace with actual API call
      const mockTasks: MonitoringTask[] = [
        {
          id: '1',
          ccpId: 1,
          ccpName: 'Temperature Control',
          ccpNumber: 'CCP-1',
          productName: 'Chicken Breast',
          productId: 1,
          status: 'due',
          priority: 'high',
          dueTime: new Date(Date.now() + 30 * 60 * 1000).toISOString(), // 30 minutes from now
          frequency: 'Every 2 hours',
          criticalLimits: { min: 70, max: 75, unit: '°C' },
          responsible: user?.username,
        },
        {
          id: '2',
          ccpId: 2,
          ccpName: 'pH Control',
          ccpNumber: 'CCP-2',
          productName: 'Pickled Vegetables',
          productId: 2,
          status: 'overdue',
          priority: 'critical',
          dueTime: new Date(Date.now() - 15 * 60 * 1000).toISOString(), // 15 minutes ago
          frequency: 'Every hour',
          lastMonitored: new Date(Date.now() - 75 * 60 * 1000).toISOString(),
          criticalLimits: { min: 3.8, max: 4.2, unit: 'pH' },
          responsible: user?.username,
        },
        {
          id: '3',
          ccpId: 3,
          ccpName: 'Water Activity',
          ccpNumber: 'CCP-3',
          productName: 'Dried Fruits',
          productId: 3,
          status: 'completed',
          priority: 'medium',
          dueTime: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          frequency: 'Every 4 hours',
          lastMonitored: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
          measuredValue: 0.65,
          unit: 'aw',
          criticalLimits: { max: 0.7, unit: 'aw' },
          responsible: user?.username,
        },
      ];
      setMonitoringTasks(mockTasks);
    } catch (error) {
      console.error('Error loading monitoring tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadBatches = async () => {
    try {
      const response = await traceabilityAPI.getBatches({ search: batchSearch, size: 10 });
      setBatchOptions(response.data?.items || []);
    } catch (error) {
      console.error('Error loading batches:', error);
      setBatchOptions([]);
    }
  };

  const handleStartMonitoring = (task: MonitoringTask) => {
    setSelectedTask(task);
    setMonitoringForm({
      batchNumber: '',
      measuredValue: '',
      unit: task.criticalLimits.unit || '',
      notes: '',
      conditions: '',
    });
    setMonitoringDialogOpen(true);
  };

  const handleSubmitMonitoring = async () => {
    if (!selectedTask || !monitoringForm.measuredValue) {
      alert('Please enter a measured value');
      return;
    }

    try {
      const payload = {
        batch_number: monitoringForm.batchNumber,
        measured_value: Number(monitoringForm.measuredValue),
        unit: monitoringForm.unit,
        notes: monitoringForm.notes,
        monitoring_conditions: monitoringForm.conditions,
      };

      // Submit monitoring log
      await haccpAPI.createMonitoringLog(selectedTask.ccpId, payload);

      // Update task status
      setMonitoringTasks(prev => 
        prev.map(task => 
          task.id === selectedTask.id 
            ? { 
                ...task, 
                status: 'completed', 
                lastMonitored: new Date().toISOString(),
                measuredValue: Number(monitoringForm.measuredValue),
                unit: monitoringForm.unit
              }
            : task
        )
      );

      setMonitoringDialogOpen(false);
      setSelectedTask(null);
      
      // Check if NC should be created
      const measuredValue = Number(monitoringForm.measuredValue);
      const { min, max } = selectedTask.criticalLimits;
      const isOutOfSpec = (min !== undefined && measuredValue < min) || 
                         (max !== undefined && measuredValue > max);
      
      if (isOutOfSpec && monitoringForm.batchNumber) {
        // Try to open NC if one was created
        try {
          const ncResponse = await haccpAPI.getRecentNonConformance(selectedTask.ccpId, monitoringForm.batchNumber);
          if (ncResponse.data?.found) {
            window.open(`/nonconformance/${ncResponse.data.id}`, '_blank');
          }
        } catch (error) {
          console.error('Error checking for NC:', error);
        }
      }
    } catch (error) {
      console.error('Error submitting monitoring:', error);
      alert('Failed to submit monitoring log');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'due':
        return <Timer color="info" />;
      case 'overdue':
        return <Warning color="error" />;
      case 'completed':
        return <CheckCircle color="success" />;
      case 'in_progress':
        return <Science color="primary" />;
      default:
        return <Timer />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'due':
        return 'info';
      case 'overdue':
        return 'error';
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
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

  const formatTimeRemaining = (dueTime: string) => {
    const now = new Date();
    const due = new Date(dueTime);
    const diffMs = due.getTime() - now.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 0) {
      return `${Math.abs(diffMins)} minutes overdue`;
    } else if (diffMins < 60) {
      return `${diffMins} minutes remaining`;
    } else {
      const hours = Math.floor(diffMins / 60);
      const mins = diffMins % 60;
      return `${hours}h ${mins}m remaining`;
    }
  };

  const dueTasks = monitoringTasks.filter(task => task.status === 'due' || task.status === 'overdue');
  const completedTasks = monitoringTasks.filter(task => task.status === 'completed');
  const overdueTasks = monitoringTasks.filter(task => task.status === 'overdue');

  return (
    <Box sx={{ p: 3 }}>
      <HACCPBreadcrumbs />
      <PageHeader
        title="HACCP Monitoring Console"
        subtitle="Real-time monitoring of Critical Control Points"
        showAdd={false}
      />

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Tasks Due
                  </Typography>
                  <Typography variant="h4">
                    {dueTasks.length}
                  </Typography>
                </Box>
                <Badge badgeContent={dueTasks.length} color="primary">
                  <Assignment color="primary" />
                </Badge>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Overdue
                  </Typography>
                  <Typography variant="h4" color="error">
                    {overdueTasks.length}
                  </Typography>
                </Box>
                <Badge badgeContent={overdueTasks.length} color="error">
                  <NotificationImportant color="error" />
                </Badge>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Completed Today
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {completedTasks.length}
                  </Typography>
                </Box>
                <CheckCircle color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active CCPs
                  </Typography>
                  <Typography variant="h4">
                    {new Set(monitoringTasks.map(t => t.ccpId)).size}
                  </Typography>
                </Box>
                <Science color="info" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Tabs value={selectedTab} onChange={(_, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab 
          icon={<Assignment />} 
          label={`Tasks (${dueTasks.length})`} 
          iconPosition="start"
        />
        <Tab 
          icon={<TrendingUp />} 
          label="Trends" 
          iconPosition="start"
        />
        <Tab 
          icon={<Assessment />} 
          label="History" 
          iconPosition="start"
        />
      </Tabs>

      <TabPanel value={selectedTab} index={0}>
        {/* Monitoring Tasks */}
        <Card>
          <CardHeader
            title="Monitoring Tasks"
            action={
              <Stack direction="row" spacing={1}>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={loadMonitoringTasks}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Stack>
            }
          />
          <CardContent>
            {dueTasks.length === 0 ? (
              <Alert severity="success">
                No monitoring tasks due at this time. All systems are up to date.
              </Alert>
            ) : (
              <List>
                {dueTasks.map((task) => (
                  <ListItem key={task.id} divider>
                    <ListItemIcon>
                      {getStatusIcon(task.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                          <Typography variant="h6">
                            {task.ccpNumber}: {task.ccpName}
                          </Typography>
                          <Chip
                            label={task.status.toUpperCase()}
                            color={getStatusColor(task.status) as any}
                            size="small"
                          />
                          <Chip
                            label={task.priority.toUpperCase()}
                            color={getPriorityColor(task.priority) as any}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary">
                            Product: {task.productName} • Frequency: {task.frequency}
                          </Typography>
                          <Typography variant="body2" color={task.status === 'overdue' ? 'error' : 'textSecondary'}>
                            {formatTimeRemaining(task.dueTime)}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            Limits: {task.criticalLimits.min ? `${task.criticalLimits.min} - ` : '≤ '}
                            {task.criticalLimits.max} {task.criticalLimits.unit}
                          </Typography>
                        </Box>
                      }
                    />
                    <Button
                      variant="contained"
                      startIcon={<Science />}
                      color={task.status === 'overdue' ? 'error' : 'primary'}
                      onClick={() => handleStartMonitoring(task)}
                      sx={{ ml: 2 }}
                    >
                      Start Monitoring
                    </Button>
                  </ListItem>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={selectedTab} index={1}>
        {/* Monitoring Trends */}
        <MonitoringTrendCharts />
      </TabPanel>

      <TabPanel value={selectedTab} index={2}>
        {/* Monitoring History */}
        <Card>
          <CardHeader title="Recent Monitoring History" />
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date/Time</TableCell>
                    <TableCell>CCP</TableCell>
                    <TableCell>Product</TableCell>
                    <TableCell>Batch</TableCell>
                    <TableCell align="right">Value</TableCell>
                    <TableCell>Unit</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {completedTasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell>{task.lastMonitored ? new Date(task.lastMonitored).toLocaleString() : '-'}</TableCell>
                      <TableCell>{task.ccpNumber}</TableCell>
                      <TableCell>{task.productName}</TableCell>
                      <TableCell>-</TableCell>
                      <TableCell align="right">{task.measuredValue || '-'}</TableCell>
                      <TableCell>{task.unit || '-'}</TableCell>
                      <TableCell>
                        <Chip 
                          size="small" 
                          color="success" 
                          label="In Spec" 
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton size="small">
                          <Visibility />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Monitoring Dialog */}
      <Dialog 
        open={monitoringDialogOpen} 
        onClose={() => setMonitoringDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Record Monitoring - {selectedTask?.ccpNumber}: {selectedTask?.ccpName}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  Critical Limits: {selectedTask?.criticalLimits.min ? `${selectedTask.criticalLimits.min} - ` : '≤ '}
                  {selectedTask?.criticalLimits.max} {selectedTask?.criticalLimits.unit}
                </Typography>
              </Alert>
            </Grid>
            <Grid item xs={12} md={6}>
              <Autocomplete
                freeSolo
                options={batchOptions}
                getOptionLabel={(option: any) => option?.batch_number || option}
                value={monitoringForm.batchNumber}
                onInputChange={(_, value) => {
                  setMonitoringForm(prev => ({ ...prev, batchNumber: value || '' }));
                  setBatchSearch(value || '');
                }}
                renderInput={(params) => (
                  <TextField 
                    {...params} 
                    label="Batch Number" 
                    placeholder="Enter or search batch..."
                    fullWidth
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                type="number"
                label="Measured Value"
                value={monitoringForm.measuredValue}
                onChange={(e) => setMonitoringForm(prev => ({ ...prev, measuredValue: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Unit"
                value={monitoringForm.unit}
                onChange={(e) => setMonitoringForm(prev => ({ ...prev, unit: e.target.value }))}
                disabled
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Monitoring Conditions"
                value={monitoringForm.conditions}
                onChange={(e) => setMonitoringForm(prev => ({ ...prev, conditions: e.target.value }))}
                placeholder="Temperature, humidity, equipment used, etc."
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Notes"
                value={monitoringForm.notes}
                onChange={(e) => setMonitoringForm(prev => ({ ...prev, notes: e.target.value }))}
                placeholder="Any observations or comments..."
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMonitoringDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleSubmitMonitoring}
            disabled={!monitoringForm.measuredValue}
          >
            Submit Monitoring
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HACCPMonitoring;