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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tabs,
  Tab,
  Badge,
  Tooltip,
  Switch,
  FormControlLabel,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Fab,
} from '@mui/material';
import {
  NotificationImportant,
  Warning,
  Error,
  Info,
  CheckCircle,
  Refresh,
  FilterList,
  Delete,
  MarkEmailRead,
  Visibility,
  ExpandMore,
  Settings,
  Add,
  Close,
  Science,
  Security,
  Schedule,
  Assignment,
  TrendingUp,
  PlayArrow,
  Notifications,
  NotificationsActive,
  NotificationsOff,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchProducts } from '../store/slices/haccpSlice';
import { haccpAPI } from '../services/api';
import PageHeader from '../components/UI/PageHeader';
import HACCPBreadcrumbs from '../components/UI/HACCPBreadcrumbs';

interface HACCPAlert {
  id: string;
  type: 'critical' | 'high' | 'medium' | 'low' | 'info';
  category: 'monitoring' | 'verification' | 'calibration' | 'deviation' | 'system' | 'schedule';
  title: string;
  message: string;
  details?: string;
  source: {
    type: 'ccp' | 'product' | 'equipment' | 'schedule' | 'system';
    id?: number;
    name: string;
  };
  timestamp: string;
  isRead: boolean;
  isResolved: boolean;
  requiresAction: boolean;
  actionTaken?: string;
  resolvedBy?: string;
  resolvedAt?: string;
  ccpId?: number;
  productId?: number;
  data?: {
    [key: string]: any;
  };
  notificationsSent: string[];
  escalationLevel: number;
}

interface AlertRule {
  id: string;
  name: string;
  description: string;
  category: string;
  condition: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  isActive: boolean;
  recipients: string[];
  escalationMinutes: number;
  autoResolve: boolean;
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
      id={`alerts-tabpanel-${index}`}
      aria-labelledby={`alerts-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const HACCPAlerts: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { products } = useSelector((state: RootState) => state.haccp);
  const { user } = useSelector((state: RootState) => state.auth);

  const [selectedTab, setSelectedTab] = useState(0);
  const [alerts, setAlerts] = useState<HACCPAlert[]>([]);
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<HACCPAlert | null>(null);
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);
  const [ruleDialogOpen, setRuleDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const [filterForm, setFilterForm] = useState({
    type: 'all',
    category: 'all',
    status: 'all',
    resolved: 'all',
  });

  const [ruleForm, setRuleForm] = useState({
    name: '',
    description: '',
    category: 'monitoring',
    condition: '',
    severity: 'medium' as 'critical' | 'high' | 'medium' | 'low',
    isActive: true,
    recipients: [] as string[],
    escalationMinutes: 60,
    autoResolve: false,
  });

  useEffect(() => {
    dispatch(fetchProducts());
    loadAlerts();
    loadAlertRules();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(loadAlerts, 30000);
    return () => clearInterval(interval);
  }, [dispatch]);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      // Mock data - replace with actual API call
      const mockAlerts: HACCPAlert[] = [
        {
          id: '1',
          type: 'critical',
          category: 'monitoring',
          title: 'Temperature Deviation - CCP-1',
          message: 'Temperature reading 68°C is below critical limit of 70°C',
          details: 'Batch #BC-2024-001 - Temperature measured at 68°C at 14:30. Critical limit: 70-75°C. Immediate corrective action required.',
          source: {
            type: 'ccp',
            id: 1,
            name: 'Temperature Control - Chicken Breast',
          },
          timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          isRead: false,
          isResolved: false,
          requiresAction: true,
          ccpId: 1,
          productId: 1,
          data: {
            measuredValue: 68,
            criticalLimit: { min: 70, max: 75 },
            unit: '°C',
            batchNumber: 'BC-2024-001',
          },
          notificationsSent: ['qa@company.com', 'production@company.com'],
          escalationLevel: 1,
        },
        {
          id: '2',
          type: 'high',
          category: 'verification',
          title: 'Overdue Verification - CCP-2',
          message: 'pH control verification is 2 days overdue',
          details: 'Weekly verification of pH monitoring equipment was due on 2024-01-13. System requires immediate verification to maintain compliance.',
          source: {
            type: 'ccp',
            id: 2,
            name: 'pH Control - Pickled Vegetables',
          },
          timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          isRead: true,
          isResolved: false,
          requiresAction: true,
          ccpId: 2,
          productId: 2,
          data: {
            dueDate: '2024-01-13',
            verificationType: 'equipment_calibration',
          },
          notificationsSent: ['qa@company.com'],
          escalationLevel: 0,
        },
        {
          id: '3',
          type: 'medium',
          category: 'schedule',
          title: 'Monitoring Schedule Missed',
          message: 'Water activity monitoring was missed for scheduled time',
          details: 'Scheduled monitoring at 12:00 was not completed. Next monitoring due at 16:00.',
          source: {
            type: 'schedule',
            id: 3,
            name: 'Water Activity Monitoring Schedule',
          },
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          isRead: true,
          isResolved: true,
          requiresAction: false,
          actionTaken: 'Monitoring completed at 12:15 - minimal delay',
          resolvedBy: user?.username || 'QA Specialist',
          resolvedAt: new Date(Date.now() - 3.5 * 60 * 60 * 1000).toISOString(),
          ccpId: 3,
          productId: 3,
          data: {
            scheduledTime: '12:00',
            completedTime: '12:15',
          },
          notificationsSent: ['qa@company.com'],
          escalationLevel: 0,
        },
        {
          id: '4',
          type: 'low',
          category: 'system',
          title: 'Equipment Calibration Due Soon',
          message: 'Temperature probe calibration due in 3 days',
          details: 'Calibration for temperature monitoring equipment TMP-001 is scheduled for 2024-01-18.',
          source: {
            type: 'equipment',
            id: 1,
            name: 'Temperature Probe TMP-001',
          },
          timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          isRead: false,
          isResolved: false,
          requiresAction: false,
          data: {
            equipmentId: 'TMP-001',
            calibrationDue: '2024-01-18',
          },
          notificationsSent: ['maintenance@company.com'],
          escalationLevel: 0,
        },
        {
          id: '5',
          type: 'info',
          category: 'system',
          title: 'System Backup Completed',
          message: 'Daily HACCP system backup completed successfully',
          details: 'Automated backup of all HACCP data, monitoring logs, and configuration completed at 02:00.',
          source: {
            type: 'system',
            name: 'HACCP Management System',
          },
          timestamp: new Date(Date.now() - 14 * 60 * 60 * 1000).toISOString(),
          isRead: true,
          isResolved: true,
          requiresAction: false,
          data: {
            backupSize: '2.4 GB',
            duration: '15 minutes',
          },
          notificationsSent: ['admin@company.com'],
          escalationLevel: 0,
        },
      ];
      setAlerts(mockAlerts);
    } catch (error) {
      console.error('Error loading alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAlertRules = async () => {
    try {
      // Mock data - replace with actual API call
      const mockRules: AlertRule[] = [
        {
          id: '1',
          name: 'CCP Temperature Deviation',
          description: 'Alert when temperature readings exceed critical limits',
          category: 'monitoring',
          condition: 'temperature < critical_limit_min OR temperature > critical_limit_max',
          severity: 'critical',
          isActive: true,
          recipients: ['qa@company.com', 'production@company.com'],
          escalationMinutes: 15,
          autoResolve: false,
        },
        {
          id: '2',
          name: 'Overdue Verification',
          description: 'Alert when verification tasks are overdue',
          category: 'verification',
          condition: 'verification_due_date < current_date',
          severity: 'high',
          isActive: true,
          recipients: ['qa@company.com'],
          escalationMinutes: 60,
          autoResolve: false,
        },
        {
          id: '3',
          name: 'Missed Monitoring Schedule',
          description: 'Alert when scheduled monitoring is not completed on time',
          category: 'schedule',
          condition: 'scheduled_time + 30_minutes < current_time AND status = pending',
          severity: 'medium',
          isActive: true,
          recipients: ['qa@company.com'],
          escalationMinutes: 120,
          autoResolve: true,
        },
      ];
      setAlertRules(mockRules);
    } catch (error) {
      console.error('Error loading alert rules:', error);
    }
  };

  const handleMarkAsRead = async (alertId: string) => {
    try {
      setAlerts(prev => 
        prev.map(alert => 
          alert.id === alertId ? { ...alert, isRead: true } : alert
        )
      );
    } catch (error) {
      console.error('Error marking alert as read:', error);
    }
  };

  const handleResolveAlert = async (alertId: string, actionTaken: string) => {
    try {
      setAlerts(prev => 
        prev.map(alert => 
          alert.id === alertId 
            ? { 
                ...alert, 
                isResolved: true, 
                actionTaken,
                resolvedBy: user?.username || 'Current User',
                resolvedAt: new Date().toISOString()
              } 
            : alert
        )
      );
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  const handleDeleteAlert = async (alertId: string) => {
    if (!window.confirm('Are you sure you want to delete this alert?')) {
      return;
    }

    try {
      setAlerts(prev => prev.filter(alert => alert.id !== alertId));
    } catch (error) {
      console.error('Error deleting alert:', error);
    }
  };

  const handleCreateRule = () => {
    setRuleForm({
      name: '',
      description: '',
      category: 'monitoring',
      condition: '',
      severity: 'medium',
      isActive: true,
      recipients: [],
      escalationMinutes: 60,
      autoResolve: false,
    });
    setRuleDialogOpen(true);
  };

  const handleSaveRule = async () => {
    if (!ruleForm.name.trim() || !ruleForm.condition.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      const newRule: AlertRule = {
        id: Date.now().toString(),
        ...ruleForm,
      };
      setAlertRules(prev => [...prev, newRule]);
      setRuleDialogOpen(false);
    } catch (error) {
      console.error('Error saving alert rule:', error);
      alert('Failed to save alert rule');
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'critical':
        return <Error color="error" />;
      case 'high':
        return <Warning color="warning" />;
      case 'medium':
        return <NotificationImportant color="info" />;
      case 'low':
        return <Info color="info" />;
      case 'info':
        return <CheckCircle color="success" />;
      default:
        return <Info />;
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'info';
      case 'info':
        return 'success';
      default:
        return 'info';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'monitoring':
        return <Science />;
      case 'verification':
        return <Security />;
      case 'calibration':
        return <Settings />;
      case 'schedule':
        return <Schedule />;
      case 'deviation':
        return <TrendingUp />;
      case 'system':
        return <Assignment />;
      default:
        return <Notifications />;
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    if (filterForm.type !== 'all' && alert.type !== filterForm.type) return false;
    if (filterForm.category !== 'all' && alert.category !== filterForm.category) return false;
    if (filterForm.status !== 'all') {
      if (filterForm.status === 'read' && !alert.isRead) return false;
      if (filterForm.status === 'unread' && alert.isRead) return false;
    }
    if (filterForm.resolved !== 'all') {
      if (filterForm.resolved === 'resolved' && !alert.isResolved) return false;
      if (filterForm.resolved === 'unresolved' && alert.isResolved) return false;
    }
    return true;
  });

  const unreadCount = alerts.filter(a => !a.isRead).length;
  const unresolvedCount = alerts.filter(a => !a.isResolved).length;
  const criticalCount = alerts.filter(a => a.type === 'critical' && !a.isResolved).length;
  const requiresActionCount = alerts.filter(a => a.requiresAction && !a.isResolved).length;

  return (
    <Box sx={{ p: 3 }}>
      <HACCPBreadcrumbs />
      <PageHeader
        title="HACCP Alerts & Notifications"
        subtitle="Monitor and manage critical system alerts and notifications"
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
                    Unread Alerts
                  </Typography>
                  <Typography variant="h4">
                    {unreadCount}
                  </Typography>
                </Box>
                <Badge badgeContent={unreadCount} color="primary">
                  <NotificationsActive color="primary" />
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
                    Critical Alerts
                  </Typography>
                  <Typography variant="h4" color="error">
                    {criticalCount}
                  </Typography>
                </Box>
                <Badge badgeContent={criticalCount} color="error">
                  <Error color="error" />
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
                    Action Required
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {requiresActionCount}
                  </Typography>
                </Box>
                <Badge badgeContent={requiresActionCount} color="warning">
                  <PlayArrow color="warning" />
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
                    Resolved Today
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {alerts.filter(a => 
                      a.isResolved && 
                      a.resolvedAt && 
                      new Date(a.resolvedAt).toDateString() === new Date().toDateString()
                    ).length}
                  </Typography>
                </Box>
                <CheckCircle color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Tabs value={selectedTab} onChange={(_, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab 
          icon={<NotificationImportant />} 
          label={`Active Alerts (${unresolvedCount})`} 
          iconPosition="start"
        />
        <Tab 
          icon={<Assignment />} 
          label="All Alerts" 
          iconPosition="start"
        />
        <Tab 
          icon={<Settings />} 
          label="Alert Rules" 
          iconPosition="start"
        />
      </Tabs>

      <TabPanel value={selectedTab} index={0}>
        {/* Active Alerts */}
        <Card>
          <CardHeader
            title="Active Alerts"
            action={
              <Stack direction="row" spacing={1}>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={loadAlerts}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Stack>
            }
          />
          <CardContent>
            {unresolvedCount === 0 ? (
              <Alert severity="success">
                No active alerts. All systems are operating normally.
              </Alert>
            ) : (
              <List>
                {alerts
                  .filter(alert => !alert.isResolved)
                  .sort((a, b) => {
                    // Sort by severity and timestamp
                    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
                    const aSeverity = severityOrder[a.type as keyof typeof severityOrder] || 5;
                    const bSeverity = severityOrder[b.type as keyof typeof severityOrder] || 5;
                    if (aSeverity !== bSeverity) return aSeverity - bSeverity;
                    return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
                  })
                  .map((alert, index) => (
                    <React.Fragment key={alert.id}>
                      <ListItem>
                        <ListItemIcon>
                          {getAlertIcon(alert.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                              <Typography 
                                variant="h6" 
                                sx={{ 
                                  fontWeight: alert.isRead ? 'normal' : 'bold',
                                  color: alert.isRead ? 'text.primary' : 'text.primary'
                                }}
                              >
                                {alert.title}
                              </Typography>
                              <Chip
                                label={alert.type.toUpperCase()}
                                color={getAlertColor(alert.type) as any}
                                size="small"
                              />
                              <Chip
                                icon={getCategoryIcon(alert.category)}
                                label={alert.category.toUpperCase()}
                                variant="outlined"
                                size="small"
                              />
                              {alert.requiresAction && (
                                <Chip
                                  label="ACTION REQUIRED"
                                  color="error"
                                  size="small"
                                  variant="outlined"
                                />
                              )}
                              {!alert.isRead && (
                                <Chip
                                  label="UNREAD"
                                  color="primary"
                                  size="small"
                                  variant="outlined"
                                />
                              )}
                            </Box>
                          }
                          secondary={
                            <Box sx={{ mt: 1 }}>
                              <Typography variant="body2" color="textSecondary">
                                {alert.message}
                              </Typography>
                              <Typography variant="body2" color="textSecondary" sx={{ mt: 0.5 }}>
                                Source: {alert.source.name} • {new Date(alert.timestamp).toLocaleString()}
                              </Typography>
                              {alert.details && (
                                <Typography variant="body2" color="textSecondary" sx={{ mt: 0.5, fontStyle: 'italic' }}>
                                  {alert.details}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                        <Stack direction="row" spacing={1} sx={{ ml: 2 }}>
                          {!alert.isRead && (
                            <Tooltip title="Mark as Read">
                              <IconButton 
                                size="small" 
                                onClick={() => handleMarkAsRead(alert.id)}
                              >
                                <MarkEmailRead />
                              </IconButton>
                            </Tooltip>
                          )}
                          <Tooltip title="View Details">
                            <IconButton 
                              size="small"
                              onClick={() => {
                                setSelectedAlert(alert);
                                setAlertDialogOpen(true);
                              }}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          {alert.requiresAction && (
                            <Button
                              variant="contained"
                              size="small"
                              color={alert.type === 'critical' ? 'error' : 'primary'}
                              onClick={() => {
                                const action = prompt('Enter action taken to resolve this alert:');
                                if (action) {
                                  handleResolveAlert(alert.id, action);
                                }
                              }}
                            >
                              Resolve
                            </Button>
                          )}
                        </Stack>
                      </ListItem>
                      {index < unresolvedCount - 1 && <Divider />}
                    </React.Fragment>
                  ))}
              </List>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={selectedTab} index={1}>
        {/* All Alerts with Filters */}
        <Card>
          <CardHeader 
            title="All Alerts"
            action={
              <Stack direction="row" spacing={1}>
                <Button
                  variant="outlined"
                  startIcon={<FilterList />}
                  size="small"
                >
                  Filters
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={loadAlerts}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Stack>
            }
          />
          <CardContent>
            {/* Filters */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={filterForm.type}
                    onChange={(e) => setFilterForm(prev => ({ ...prev, type: e.target.value }))}
                    label="Type"
                  >
                    <MenuItem value="all">All Types</MenuItem>
                    <MenuItem value="critical">Critical</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="info">Info</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={filterForm.category}
                    onChange={(e) => setFilterForm(prev => ({ ...prev, category: e.target.value }))}
                    label="Category"
                  >
                    <MenuItem value="all">All Categories</MenuItem>
                    <MenuItem value="monitoring">Monitoring</MenuItem>
                    <MenuItem value="verification">Verification</MenuItem>
                    <MenuItem value="calibration">Calibration</MenuItem>
                    <MenuItem value="deviation">Deviation</MenuItem>
                    <MenuItem value="schedule">Schedule</MenuItem>
                    <MenuItem value="system">System</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={filterForm.status}
                    onChange={(e) => setFilterForm(prev => ({ ...prev, status: e.target.value }))}
                    label="Status"
                  >
                    <MenuItem value="all">All</MenuItem>
                    <MenuItem value="read">Read</MenuItem>
                    <MenuItem value="unread">Unread</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Resolution</InputLabel>
                  <Select
                    value={filterForm.resolved}
                    onChange={(e) => setFilterForm(prev => ({ ...prev, resolved: e.target.value }))}
                    label="Resolution"
                  >
                    <MenuItem value="all">All</MenuItem>
                    <MenuItem value="resolved">Resolved</MenuItem>
                    <MenuItem value="unresolved">Unresolved</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            {/* Alerts Table */}
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Alert</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Source</TableCell>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredAlerts.map((alert) => (
                    <TableRow key={alert.id}>
                      <TableCell>
                        <Box>
                          <Typography 
                            variant="body2" 
                            fontWeight={alert.isRead ? 'normal' : 'bold'}
                          >
                            {alert.title}
                          </Typography>
                          <Typography variant="body2" color="textSecondary" noWrap>
                            {alert.message}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={alert.type.toUpperCase()}
                          color={getAlertColor(alert.type) as any}
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          {getCategoryIcon(alert.category)}
                          <Typography variant="body2">
                            {alert.category}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {alert.source.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {new Date(alert.timestamp).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          {!alert.isRead && (
                            <Chip
                              label="UNREAD"
                              color="primary"
                              size="small"
                              variant="outlined"
                            />
                          )}
                          {alert.isResolved ? (
                            <Chip
                              label="RESOLVED"
                              color="success"
                              size="small"
                            />
                          ) : (
                            <Chip
                              label="ACTIVE"
                              color="warning"
                              size="small"
                            />
                          )}
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          <Tooltip title="View Details">
                            <IconButton 
                              size="small"
                              onClick={() => {
                                setSelectedAlert(alert);
                                setAlertDialogOpen(true);
                              }}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Alert">
                            <IconButton 
                              size="small" 
                              color="error"
                              onClick={() => handleDeleteAlert(alert.id)}
                            >
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={selectedTab} index={2}>
        {/* Alert Rules */}
        <Card>
          <CardHeader 
            title="Alert Rules Configuration"
            action={
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={handleCreateRule}
              >
                Create Rule
              </Button>
            }
          />
          <CardContent>
            {alertRules.map((rule) => (
              <Accordion key={rule.id}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                    <Typography variant="h6">{rule.name}</Typography>
                    <Chip
                      label={rule.severity.toUpperCase()}
                      color={getAlertColor(rule.severity) as any}
                      size="small"
                    />
                    <Chip
                      label={rule.category.toUpperCase()}
                      variant="outlined"
                      size="small"
                    />
                    <Box sx={{ flexGrow: 1 }} />
                    <Switch 
                      checked={rule.isActive} 
                      size="small"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Typography variant="body2" color="textSecondary">
                        {rule.description}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Condition
                      </Typography>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: 'grey.100', p: 1, borderRadius: 1 }}>
                        {rule.condition}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Recipients
                      </Typography>
                      <Typography variant="body2">
                        {rule.recipients.join(', ') || 'None'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Escalation Time
                      </Typography>
                      <Typography variant="body2">
                        {rule.escalationMinutes} minutes
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Auto Resolve
                      </Typography>
                      <Typography variant="body2">
                        {rule.autoResolve ? 'Enabled' : 'Disabled'}
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </CardContent>
        </Card>
      </TabPanel>

      {/* Alert Details Dialog */}
      <Dialog 
        open={alertDialogOpen} 
        onClose={() => setAlertDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6">Alert Details</Typography>
            <IconButton onClick={() => setAlertDialogOpen(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedAlert && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  {getAlertIcon(selectedAlert.type)}
                  <Typography variant="h6">{selectedAlert.title}</Typography>
                  <Chip
                    label={selectedAlert.type.toUpperCase()}
                    color={getAlertColor(selectedAlert.type) as any}
                    size="small"
                  />
                  <Chip
                    icon={getCategoryIcon(selectedAlert.category)}
                    label={selectedAlert.category.toUpperCase()}
                    variant="outlined"
                    size="small"
                  />
                </Box>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body1" gutterBottom>
                  {selectedAlert.message}
                </Typography>
                {selectedAlert.details && (
                  <Typography variant="body2" color="textSecondary" paragraph>
                    {selectedAlert.details}
                  </Typography>
                )}
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Source</Typography>
                <Typography variant="body2">{selectedAlert.source.name}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Timestamp</Typography>
                <Typography variant="body2">{new Date(selectedAlert.timestamp).toLocaleString()}</Typography>
              </Grid>
              {selectedAlert.data && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>Additional Data</Typography>
                  <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1, fontFamily: 'monospace' }}>
                    <pre>{JSON.stringify(selectedAlert.data, null, 2)}</pre>
                  </Box>
                </Grid>
              )}
              {selectedAlert.isResolved && (
                <Grid item xs={12}>
                  <Alert severity="success">
                    <Typography variant="subtitle2">Resolved</Typography>
                    <Typography variant="body2">
                      By: {selectedAlert.resolvedBy} • {selectedAlert.resolvedAt ? new Date(selectedAlert.resolvedAt).toLocaleString() : ''}
                    </Typography>
                    {selectedAlert.actionTaken && (
                      <Typography variant="body2">
                        Action: {selectedAlert.actionTaken}
                      </Typography>
                    )}
                  </Alert>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          {selectedAlert && !selectedAlert.isRead && (
            <Button onClick={() => handleMarkAsRead(selectedAlert.id)}>
              Mark as Read
            </Button>
          )}
          {selectedAlert && selectedAlert.requiresAction && !selectedAlert.isResolved && (
            <Button 
              variant="contained" 
              color={selectedAlert.type === 'critical' ? 'error' : 'primary'}
              onClick={() => {
                const action = prompt('Enter action taken to resolve this alert:');
                if (action) {
                  handleResolveAlert(selectedAlert.id, action);
                  setAlertDialogOpen(false);
                }
              }}
            >
              Resolve Alert
            </Button>
          )}
          <Button onClick={() => setAlertDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Alert Rule Dialog */}
      <Dialog 
        open={ruleDialogOpen} 
        onClose={() => setRuleDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create Alert Rule</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Rule Name"
                value={ruleForm.name}
                onChange={(e) => setRuleForm(prev => ({ ...prev, name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={ruleForm.description}
                onChange={(e) => setRuleForm(prev => ({ ...prev, description: e.target.value }))}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={ruleForm.category}
                  onChange={(e) => setRuleForm(prev => ({ ...prev, category: e.target.value }))}
                  label="Category"
                >
                  <MenuItem value="monitoring">Monitoring</MenuItem>
                  <MenuItem value="verification">Verification</MenuItem>
                  <MenuItem value="calibration">Calibration</MenuItem>
                  <MenuItem value="deviation">Deviation</MenuItem>
                  <MenuItem value="schedule">Schedule</MenuItem>
                  <MenuItem value="system">System</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Severity</InputLabel>
                <Select
                  value={ruleForm.severity}
                  onChange={(e) => setRuleForm(prev => ({ ...prev, severity: e.target.value as any }))}
                  label="Severity"
                >
                  <MenuItem value="critical">Critical</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Condition"
                value={ruleForm.condition}
                onChange={(e) => setRuleForm(prev => ({ ...prev, condition: e.target.value }))}
                placeholder="e.g., temperature < critical_limit_min OR temperature > critical_limit_max"
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Escalation Time (minutes)"
                value={ruleForm.escalationMinutes}
                onChange={(e) => setRuleForm(prev => ({ ...prev, escalationMinutes: Number(e.target.value) }))}
                inputProps={{ min: 1 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={ruleForm.autoResolve}
                    onChange={(e) => setRuleForm(prev => ({ ...prev, autoResolve: e.target.checked }))}
                  />
                }
                label="Auto Resolve"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={ruleForm.isActive}
                    onChange={(e) => setRuleForm(prev => ({ ...prev, isActive: e.target.checked }))}
                  />
                }
                label="Active Rule"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRuleDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleSaveRule}
            disabled={!ruleForm.name.trim() || !ruleForm.condition.trim()}
          >
            Create Rule
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button for Quick Actions */}
      <Fab
        color="primary"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => {
          // Quick action menu or direct action
          alert('Quick actions: Mark all as read, Create alert rule, Export alerts');
        }}
      >
        <Add />
      </Fab>
    </Box>
  );
};

export default HACCPAlerts;