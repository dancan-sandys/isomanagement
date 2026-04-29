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
import { hasPermission } from '../store/slices/authSlice';
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
  const { user: currentUser } = useSelector((state: RootState) => state.auth);
  const assignmentRoles = new Set(
    (currentUser?.haccp_assignment_roles || []).map((role) => role.toLowerCase())
  );
  const hasMonitoringAssignment = assignmentRoles.has('monitoring');
  const canViewMonitoring = !!currentUser && (
    hasPermission(currentUser, 'haccp', 'view') ||
    hasPermission(currentUser, 'haccp', 'update') ||
    hasPermission(currentUser, 'haccp', 'manage_program') ||
    hasMonitoringAssignment
  );
  const canCreateLogs = !!currentUser && hasPermission(currentUser, 'haccp', 'create');

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
  const [batchOpen, setBatchOpen] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);
  const [monitoringHistory, setMonitoringHistory] = useState<any[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    dispatch(fetchProducts());
    loadMonitoringTasks();
    loadMonitoringHistory();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(() => {
      loadMonitoringTasks();
      loadMonitoringHistory();
    }, 30000);
    setRefreshInterval(interval);
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [dispatch]);

  // Fetch batches when dropdown opens or search text changes (scoped to selected task's product when available)
  useEffect(() => {
    let active = true;
    if (!batchOpen) return () => { active = false; };
    const t = setTimeout(async () => {
      try {
        const params: any = { search: batchSearch, size: 10 };
        if (selectedTask?.productId && Number.isInteger(selectedTask.productId)) params.product_id = selectedTask.productId;
        const resp: any = await traceabilityAPI.getBatches(params);
        const items = resp?.data?.items || resp?.items || [];
        if (active) setBatchOptions(items);
      } catch (e) {
        if (active) setBatchOptions([]);
      }
    }, 250);
    return () => { active = false; clearTimeout(t); };
  }, [batchOpen, batchSearch, selectedTask?.productId]);

  const loadMonitoringTasks = async () => {
    setLoading(true);
    try {
      const res: any = await haccpAPI.getMonitoringTasks();
      const payload = res?.data ?? res;
      const items = payload?.items ?? payload ?? [];

      const tasks: MonitoringTask[] = items.map((item: any) => {
        const status = (item.status === 'overdue' || item.status === 'due' || item.status === 'completed'
          ? item.status
          : 'due') as MonitoringTask['status'];
        let priority: MonitoringTask['priority'] = 'medium';
        if (status === 'overdue') priority = 'critical';
        else if (status === 'due') priority = 'high';
        return {
          id: String(item.id ?? item.ccp_id),
          ccpId: item.ccp_id,
          ccpName: item.ccp_name,
          ccpNumber: item.ccp_number ?? '',
          productName: item.product_name ?? '',
          productId: item.product_id ?? 0,
          status,
          priority,
          dueTime: item.next_due_time || new Date().toISOString(),
          frequency: item.frequency || '',
          lastMonitored: item.last_monitoring_time || undefined,
          measuredValue: item.last_measured_value,
          unit: item.unit || item.critical_limits?.unit || '',
          criticalLimits: {
            min: item.critical_limits?.min,
            max: item.critical_limits?.max,
            unit: item.critical_limits?.unit || '',
          },
          responsible: currentUser?.username,
        };
      });

      setMonitoringTasks(tasks);
    } catch (error) {
      console.error('Error loading monitoring tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMonitoringHistory = async () => {
    setHistoryLoading(true);
    try {
      const res: any = await haccpAPI.getMonitoringHistory({ limit: 100 });
      const data = res?.data ?? res;
      const items = data?.items ?? [];
      setMonitoringHistory(Array.isArray(items) ? items : []);
    } catch (error) {
      console.error('Error loading monitoring history:', error);
      setMonitoringHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleStartMonitoring = (task: MonitoringTask) => {
    setSelectedTask(task);
    setMonitoringForm({
      batchNumber: '',
      measuredValue: task.measuredValue != null ? String(task.measuredValue) : '',
      unit: task.criticalLimits.unit || '',
      notes: '',
      conditions: '',
    });
    setBatchSearch('');
    setBatchOpen(false);
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
    } catch (error: any) {
      console.error('Error submitting monitoring:', error);
      const detail = error?.response?.data?.detail;
      const message =
        (Array.isArray(detail) ? detail.map((d: any) => d?.msg || d).join(', ') : detail) ||
        error?.message ||
        'Failed to submit monitoring log';
      alert(message);
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

  const dueTasks = monitoringTasks.filter(task => task.status === 'due');
  const overdueTasks = monitoringTasks.filter(task => task.status === 'overdue');
  const completedTasks = monitoringTasks.filter(task => task.status === 'completed');

  if (!canViewMonitoring) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          You are not authorized to access HACCP Monitoring.
        </Alert>
      </Box>
    );
  }

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
                    Completed
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
          label={`Tasks (${monitoringTasks.length})`} 
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
            {monitoringTasks.length === 0 ? (
              <Alert severity="success">
                No monitoring tasks. Assign CCPs with monitoring responsibility or add active CCPs to products.
              </Alert>
            ) : (
              <List>
                {monitoringTasks.map((task) => (
                  <ListItem
                    key={task.id}
                    divider
                    onClick={() => handleStartMonitoring(task)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <ListItemIcon>
                      {getStatusIcon(task.status)}
                    </ListItemIcon>
                    <ListItemText
                      primaryTypographyProps={{ component: 'div' }}
                      secondaryTypographyProps={{ component: 'div' }}
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
                    {canCreateLogs && (
                      <Button
                        variant="contained"
                        startIcon={<Science />}
                        color={task.status === 'overdue' ? 'error' : 'primary'}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleStartMonitoring(task);
                        }}
                        sx={{ ml: 2 }}
                      >
                        Start Monitoring
                      </Button>
                    )}
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
        {/* Monitoring History – actual monitoring logs (verification logs) */}
        <Card>
          <CardHeader
            title="Recent Monitoring History"
            action={
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => loadMonitoringHistory()}
                disabled={historyLoading}
              >
                Refresh
              </Button>
            }
          />
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
                    <TableCell>Spec</TableCell>
                    <TableCell>Verification</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {historyLoading ? (
                    <TableRow>
                      <TableCell colSpan={9} align="center">
                        Loading…
                      </TableCell>
                    </TableRow>
                  ) : monitoringHistory.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={9} align="center">
                        No monitoring records yet. Records appear here after you submit monitoring from the Tasks tab.
                      </TableCell>
                    </TableRow>
                  ) : (
                    monitoringHistory.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell>
                          {log.monitoring_time ? new Date(log.monitoring_time).toLocaleString() : log.created_at ? new Date(log.created_at).toLocaleString() : '—'}
                        </TableCell>
                        <TableCell>
                          {log.ccp_number ? `${log.ccp_number}: ${log.ccp_name || ''}`.trim() : log.ccp_name || '—'}
                        </TableCell>
                        <TableCell>{log.product_name ?? '—'}</TableCell>
                        <TableCell>{log.batch_number ?? '—'}</TableCell>
                        <TableCell align="right">{log.measured_value ?? '—'}</TableCell>
                        <TableCell>{log.unit ?? '—'}</TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            color={log.is_within_limits ? 'success' : 'error'}
                            label={log.is_within_limits ? 'In Spec' : 'Out of Spec'}
                          />
                        </TableCell>
                        <TableCell>
                          {log.is_verified ? (
                            <Chip
                              size="small"
                              color={log.verification_is_compliant !== false ? 'success' : 'error'}
                              label={log.verification_is_compliant !== false ? 'Verified' : 'Rejected'}
                              variant="outlined"
                            />
                          ) : (
                            <Chip size="small" label="Pending" variant="outlined" />
                          )}
                        </TableCell>
                        <TableCell>
                          <IconButton size="small" aria-label="View">
                            <Visibility />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Monitoring Dialog - viewable by anyone who sees tasks; only users with create permission can submit */}
      <Dialog 
        open={monitoringDialogOpen} 
        onClose={() => {
          setMonitoringDialogOpen(false);
          setBatchOpen(false);
          setBatchSearch('');
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {canCreateLogs ? 'Record Monitoring' : 'Monitoring Details'} - {selectedTask?.ccpNumber}: {selectedTask?.ccpName}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {!canCreateLogs && selectedTask?.lastMonitored && (
              <Grid item xs={12}>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    Last recorded: {new Date(selectedTask.lastMonitored).toLocaleString()} — Value: {selectedTask.measuredValue ?? '-'} {selectedTask.unit ?? ''}
                  </Typography>
                </Alert>
              </Grid>
            )}
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
                options={batchOptions}
                open={batchOpen}
                onOpen={() => setBatchOpen(true)}
                onClose={() => setBatchOpen(false)}
                getOptionLabel={(b: any) => b?.batch_number ?? ''}
                value={batchOptions.find((b: any) => (b?.batch_number || '') === monitoringForm.batchNumber) || null}
                onChange={(_, val: any) => setMonitoringForm(prev => ({ ...prev, batchNumber: val ? (val.batch_number || '') : '' }))}
                inputValue={batchSearch}
                onInputChange={(_, val) => setBatchSearch(val)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Batch Number"
                    placeholder="Search batches..."
                    fullWidth
                    disabled={!canCreateLogs}
                  />
                )}
                disabled={!canCreateLogs}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                type="number"
                label="Measured Value"
                value={monitoringForm.measuredValue}
                onChange={(e) => setMonitoringForm(prev => ({ ...prev, measuredValue: e.target.value }))}
                required={canCreateLogs}
                disabled={!canCreateLogs}
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
                disabled={!canCreateLogs}
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
                disabled={!canCreateLogs}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMonitoringDialogOpen(false)}>
            {canCreateLogs ? 'Cancel' : 'Close'}
          </Button>
          {canCreateLogs && (
            <Button 
              variant="contained" 
              onClick={handleSubmitMonitoring}
              disabled={!monitoringForm.measuredValue}
            >
              Submit Monitoring
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HACCPMonitoring;