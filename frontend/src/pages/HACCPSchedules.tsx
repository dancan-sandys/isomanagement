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
  Calendar,
  Badge,
  Tooltip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Schedule,
  Add,
  Edit,
  Delete,
  Visibility,
  Refresh,
  CalendarToday,
  Assignment,
  NotificationImportant,
  Settings,
  PlayArrow,
  Pause,
  Stop,
  Event,
  AccessTime,
  Person,
  Science,
  VerifiedUser,
  Warning,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchProducts } from '../store/slices/haccpSlice';
import { haccpAPI } from '../services/api';
import PageHeader from '../components/UI/PageHeader';
import HACCPBreadcrumbs from '../components/UI/HACCPBreadcrumbs';

interface HACCPSchedule {
  id: string;
  name: string;
  type: 'monitoring' | 'verification' | 'calibration' | 'review';
  ccpId?: number;
  ccpName?: string;
  productId?: number;
  productName?: string;
  frequency: string;
  interval: number;
  intervalUnit: 'minutes' | 'hours' | 'days' | 'weeks' | 'months';
  startDate: string;
  endDate?: string;
  isActive: boolean;
  responsible: string;
  description: string;
  lastExecution?: string;
  nextExecution: string;
  executionCount: number;
  missedCount: number;
  notifications: {
    enabled: boolean;
    advanceMinutes: number;
    recipients: string[];
  };
  parameters?: {
    [key: string]: any;
  };
}

interface ScheduleExecution {
  id: string;
  scheduleId: string;
  scheduledTime: string;
  executedTime?: string;
  status: 'pending' | 'completed' | 'missed' | 'failed';
  executedBy?: string;
  notes?: string;
  result?: any;
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
      id={`schedules-tabpanel-${index}`}
      aria-labelledby={`schedules-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const HACCPSchedules: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { products } = useSelector((state: RootState) => state.haccp);
  const { user } = useSelector((state: RootState) => state.auth);

  const [selectedTab, setSelectedTab] = useState(0);
  const [schedules, setSchedules] = useState<HACCPSchedule[]>([]);
  const [executions, setExecutions] = useState<ScheduleExecution[]>([]);
  const [selectedSchedule, setSelectedSchedule] = useState<HACCPSchedule | null>(null);
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const [scheduleForm, setScheduleForm] = useState({
    name: '',
    type: 'monitoring' as 'monitoring' | 'verification' | 'calibration' | 'review',
    ccpId: '',
    productId: '',
    frequency: '',
    interval: 1,
    intervalUnit: 'hours' as 'minutes' | 'hours' | 'days' | 'weeks' | 'months',
    startDate: '',
    endDate: '',
    responsible: '',
    description: '',
    isActive: true,
    notifications: {
      enabled: true,
      advanceMinutes: 30,
      recipients: [] as string[],
    },
  });

  useEffect(() => {
    dispatch(fetchProducts());
    loadSchedules();
    loadExecutions();
  }, [dispatch]);

  const loadSchedules = async () => {
    setLoading(true);
    try {
      // Mock data - replace with actual API call
      const mockSchedules: HACCPSchedule[] = [
        {
          id: '1',
          name: 'Temperature Monitoring - Chicken Breast',
          type: 'monitoring',
          ccpId: 1,
          ccpName: 'Temperature Control',
          productId: 1,
          productName: 'Chicken Breast',
          frequency: 'Every 2 hours',
          interval: 2,
          intervalUnit: 'hours',
          startDate: '2024-01-01T00:00:00.000Z',
          isActive: true,
          responsible: user?.username || 'QA Specialist',
          description: 'Monitor temperature at CCP-1 for chicken breast processing',
          lastExecution: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          nextExecution: new Date(Date.now() + 30 * 60 * 1000).toISOString(),
          executionCount: 156,
          missedCount: 2,
          notifications: {
            enabled: true,
            advanceMinutes: 15,
            recipients: ['qa@company.com'],
          },
        },
        {
          id: '2',
          name: 'pH Verification - Pickled Vegetables',
          type: 'verification',
          ccpId: 2,
          ccpName: 'pH Control',
          productId: 2,
          productName: 'Pickled Vegetables',
          frequency: 'Weekly',
          interval: 1,
          intervalUnit: 'weeks',
          startDate: '2024-01-01T00:00:00.000Z',
          isActive: true,
          responsible: user?.username || 'QA Manager',
          description: 'Weekly verification of pH monitoring equipment and procedures',
          lastExecution: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          nextExecution: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
          executionCount: 12,
          missedCount: 0,
          notifications: {
            enabled: true,
            advanceMinutes: 60,
            recipients: ['qa@company.com', 'manager@company.com'],
          },
        },
        {
          id: '3',
          name: 'Equipment Calibration Schedule',
          type: 'calibration',
          frequency: 'Monthly',
          interval: 1,
          intervalUnit: 'months',
          startDate: '2024-01-01T00:00:00.000Z',
          isActive: true,
          responsible: user?.username || 'Maintenance Team',
          description: 'Monthly calibration of all monitoring equipment',
          lastExecution: new Date(Date.now() - 25 * 24 * 60 * 60 * 1000).toISOString(),
          nextExecution: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
          executionCount: 6,
          missedCount: 1,
          notifications: {
            enabled: true,
            advanceMinutes: 1440, // 24 hours
            recipients: ['maintenance@company.com'],
          },
        },
        {
          id: '4',
          name: 'HACCP System Review',
          type: 'review',
          frequency: 'Quarterly',
          interval: 3,
          intervalUnit: 'months',
          startDate: '2024-01-01T00:00:00.000Z',
          isActive: false,
          responsible: user?.username || 'HACCP Team',
          description: 'Comprehensive review of HACCP system effectiveness',
          lastExecution: new Date(Date.now() - 80 * 24 * 60 * 60 * 1000).toISOString(),
          nextExecution: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString(),
          executionCount: 2,
          missedCount: 0,
          notifications: {
            enabled: true,
            advanceMinutes: 7200, // 5 days
            recipients: ['haccp-team@company.com'],
          },
        },
      ];
      setSchedules(mockSchedules);
    } catch (error) {
      console.error('Error loading schedules:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadExecutions = async () => {
    try {
      // Mock data - replace with actual API call
      const mockExecutions: ScheduleExecution[] = [
        {
          id: '1',
          scheduleId: '1',
          scheduledTime: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          executedTime: new Date(Date.now() - 2 * 60 * 60 * 1000 + 5 * 60 * 1000).toISOString(),
          status: 'completed',
          executedBy: user?.username || 'QA Specialist',
          notes: 'Temperature within limits',
          result: { temperature: 72.5, unit: '°C', withinLimits: true },
        },
        {
          id: '2',
          scheduleId: '1',
          scheduledTime: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          status: 'missed',
          notes: 'Staff unavailable due to shift change',
        },
        {
          id: '3',
          scheduleId: '2',
          scheduledTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          executedTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000 + 30 * 60 * 1000).toISOString(),
          status: 'completed',
          executedBy: user?.username || 'QA Manager',
          notes: 'Verification passed, equipment functioning correctly',
          result: { verification: 'pass', issues: 0 },
        },
      ];
      setExecutions(mockExecutions);
    } catch (error) {
      console.error('Error loading executions:', error);
    }
  };

  const handleCreateSchedule = () => {
    setSelectedSchedule(null);
    setScheduleForm({
      name: '',
      type: 'monitoring',
      ccpId: '',
      productId: '',
      frequency: '',
      interval: 1,
      intervalUnit: 'hours',
      startDate: new Date().toISOString().split('T')[0],
      endDate: '',
      responsible: user?.username || '',
      description: '',
      isActive: true,
      notifications: {
        enabled: true,
        advanceMinutes: 30,
        recipients: [],
      },
    });
    setScheduleDialogOpen(true);
  };

  const handleEditSchedule = (schedule: HACCPSchedule) => {
    setSelectedSchedule(schedule);
    setScheduleForm({
      name: schedule.name,
      type: schedule.type,
      ccpId: schedule.ccpId?.toString() || '',
      productId: schedule.productId?.toString() || '',
      frequency: schedule.frequency,
      interval: schedule.interval,
      intervalUnit: schedule.intervalUnit,
      startDate: schedule.startDate.split('T')[0],
      endDate: schedule.endDate?.split('T')[0] || '',
      responsible: schedule.responsible,
      description: schedule.description,
      isActive: schedule.isActive,
      notifications: schedule.notifications,
    });
    setScheduleDialogOpen(true);
  };

  const handleSaveSchedule = async () => {
    if (!scheduleForm.name.trim() || !scheduleForm.responsible.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      const payload = {
        ...scheduleForm,
        ccpId: scheduleForm.ccpId ? Number(scheduleForm.ccpId) : undefined,
        productId: scheduleForm.productId ? Number(scheduleForm.productId) : undefined,
        startDate: new Date(scheduleForm.startDate).toISOString(),
        endDate: scheduleForm.endDate ? new Date(scheduleForm.endDate).toISOString() : undefined,
      };

      if (selectedSchedule) {
        // Update existing schedule
        const updatedSchedule = { ...selectedSchedule, ...payload };
        setSchedules(prev => prev.map(s => s.id === selectedSchedule.id ? updatedSchedule : s));
      } else {
        // Create new schedule
        const newSchedule: HACCPSchedule = {
          id: Date.now().toString(),
          ...payload,
          executionCount: 0,
          missedCount: 0,
          nextExecution: new Date(Date.now() + scheduleForm.interval * getIntervalMilliseconds(scheduleForm.intervalUnit)).toISOString(),
        };
        setSchedules(prev => [...prev, newSchedule]);
      }

      setScheduleDialogOpen(false);
      setSelectedSchedule(null);
    } catch (error) {
      console.error('Error saving schedule:', error);
      alert('Failed to save schedule');
    }
  };

  const handleToggleSchedule = async (scheduleId: string, isActive: boolean) => {
    try {
      setSchedules(prev => 
        prev.map(s => 
          s.id === scheduleId ? { ...s, isActive } : s
        )
      );
    } catch (error) {
      console.error('Error toggling schedule:', error);
    }
  };

  const handleDeleteSchedule = async (scheduleId: string) => {
    if (!window.confirm('Are you sure you want to delete this schedule?')) {
      return;
    }

    try {
      setSchedules(prev => prev.filter(s => s.id !== scheduleId));
    } catch (error) {
      console.error('Error deleting schedule:', error);
    }
  };

  const getIntervalMilliseconds = (unit: string) => {
    switch (unit) {
      case 'minutes':
        return 60 * 1000;
      case 'hours':
        return 60 * 60 * 1000;
      case 'days':
        return 24 * 60 * 60 * 1000;
      case 'weeks':
        return 7 * 24 * 60 * 60 * 1000;
      case 'months':
        return 30 * 24 * 60 * 60 * 1000;
      default:
        return 60 * 60 * 1000;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'monitoring':
        return <Science />;
      case 'verification':
        return <VerifiedUser />;
      case 'calibration':
        return <Settings />;
      case 'review':
        return <Assignment />;
      default:
        return <Schedule />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'missed':
        return 'error';
      case 'failed':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatTimeRemaining = (nextExecution: string) => {
    const now = new Date();
    const next = new Date(nextExecution);
    const diffMs = next.getTime() - now.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMs < 0) {
      return 'Overdue';
    } else if (diffDays > 0) {
      return `${diffDays} days`;
    } else if (diffHours > 0) {
      return `${diffHours} hours`;
    } else {
      const diffMins = Math.floor(diffMs / (1000 * 60));
      return `${diffMins} minutes`;
    }
  };

  const activeSchedules = schedules.filter(s => s.isActive);
  const inactiveSchedules = schedules.filter(s => !s.isActive);
  const upcomingExecutions = schedules
    .filter(s => s.isActive)
    .sort((a, b) => new Date(a.nextExecution).getTime() - new Date(b.nextExecution).getTime())
    .slice(0, 10);

  return (
    <Box sx={{ p: 3 }}>
      <HACCPBreadcrumbs />
      <PageHeader
        title="HACCP Schedules"
        subtitle="Automated scheduling and tracking of HACCP activities"
        showAdd={true}
        onAdd={handleCreateSchedule}
        addButtonText="Create Schedule"
      />

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Schedules
                  </Typography>
                  <Typography variant="h4">
                    {activeSchedules.length}
                  </Typography>
                </Box>
                <Badge badgeContent={activeSchedules.length} color="primary">
                  <PlayArrow color="primary" />
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
                    Upcoming (24h)
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {upcomingExecutions.filter(s => 
                      new Date(s.nextExecution).getTime() - Date.now() < 24 * 60 * 60 * 1000
                    ).length}
                  </Typography>
                </Box>
                <AccessTime color="warning" />
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
                    {executions.filter(e => 
                      e.status === 'completed' && 
                      e.executedTime &&
                      new Date(e.executedTime).toDateString() === new Date().toDateString()
                    ).length}
                  </Typography>
                </Box>
                <Event color="success" />
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
                    Missed Tasks
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {schedules.reduce((sum, s) => sum + s.missedCount, 0)}
                  </Typography>
                </Box>
                <NotificationImportant color="error" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Tabs value={selectedTab} onChange={(_, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab 
          icon={<Schedule />} 
          label={`Schedules (${schedules.length})`} 
          iconPosition="start"
        />
        <Tab 
          icon={<CalendarToday />} 
          label="Upcoming" 
          iconPosition="start"
        />
        <Tab 
          icon={<Assignment />} 
          label="Execution History" 
          iconPosition="start"
        />
      </Tabs>

      <TabPanel value={selectedTab} index={0}>
        {/* Schedules List */}
        <Card>
          <CardHeader
            title="HACCP Schedules"
            action={
              <Stack direction="row" spacing={1}>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={loadSchedules}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Stack>
            }
          />
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Schedule</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>CCP/Product</TableCell>
                    <TableCell>Frequency</TableCell>
                    <TableCell>Next Execution</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {schedules.map((schedule) => (
                    <TableRow key={schedule.id}>
                      <TableCell>
                        <Box>
                          <Typography variant="body1" fontWeight="medium">
                            {schedule.name}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            Responsible: {schedule.responsible}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          {getTypeIcon(schedule.type)}
                          <Typography variant="body2">
                            {schedule.type.charAt(0).toUpperCase() + schedule.type.slice(1)}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box>
                          {schedule.ccpName && (
                            <Typography variant="body2">
                              {schedule.ccpName}
                            </Typography>
                          )}
                          {schedule.productName && (
                            <Typography variant="body2" color="textSecondary">
                              {schedule.productName}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {schedule.frequency}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">
                            {new Date(schedule.nextExecution).toLocaleString()}
                          </Typography>
                          <Typography 
                            variant="body2" 
                            color={new Date(schedule.nextExecution).getTime() < Date.now() ? 'error' : 'textSecondary'}
                          >
                            {formatTimeRemaining(schedule.nextExecution)}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Switch
                            checked={schedule.isActive}
                            onChange={(e) => handleToggleSchedule(schedule.id, e.target.checked)}
                            size="small"
                          />
                          <Chip
                            size="small"
                            label={schedule.isActive ? 'Active' : 'Inactive'}
                            color={schedule.isActive ? 'success' : 'default'}
                          />
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          <Tooltip title="View Details">
                            <IconButton size="small">
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit Schedule">
                            <IconButton 
                              size="small" 
                              onClick={() => handleEditSchedule(schedule)}
                            >
                              <Edit />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Schedule">
                            <IconButton 
                              size="small" 
                              color="error"
                              onClick={() => handleDeleteSchedule(schedule.id)}
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

      <TabPanel value={selectedTab} index={1}>
        {/* Upcoming Executions */}
        <Card>
          <CardHeader title="Upcoming Executions (Next 7 Days)" />
          <CardContent>
            {upcomingExecutions.length === 0 ? (
              <Alert severity="info">
                No scheduled executions in the next 7 days.
              </Alert>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Scheduled Time</TableCell>
                      <TableCell>Schedule</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Responsible</TableCell>
                      <TableCell>Time Remaining</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {upcomingExecutions
                      .filter(s => new Date(s.nextExecution).getTime() - Date.now() < 7 * 24 * 60 * 60 * 1000)
                      .map((schedule) => (
                        <TableRow key={schedule.id}>
                          <TableCell>
                            {new Date(schedule.nextExecution).toLocaleString()}
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {schedule.name}
                            </Typography>
                            {schedule.ccpName && (
                              <Typography variant="body2" color="textSecondary">
                                {schedule.ccpName}
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell>
                            <Box display="flex" alignItems="center" gap={1}>
                              {getTypeIcon(schedule.type)}
                              <Typography variant="body2">
                                {schedule.type.charAt(0).toUpperCase() + schedule.type.slice(1)}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Person fontSize="small" />
                              <Typography variant="body2">
                                {schedule.responsible}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography 
                              variant="body2"
                              color={new Date(schedule.nextExecution).getTime() < Date.now() ? 'error' : 'textSecondary'}
                            >
                              {formatTimeRemaining(schedule.nextExecution)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              variant="outlined"
                              startIcon={<PlayArrow />}
                              onClick={() => {
                                // Navigate to appropriate execution page
                                if (schedule.type === 'monitoring') {
                                  window.open('/haccp/monitoring', '_blank');
                                } else if (schedule.type === 'verification') {
                                  window.open('/haccp/verification', '_blank');
                                }
                              }}
                            >
                              Execute Now
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={selectedTab} index={2}>
        {/* Execution History */}
        <Card>
          <CardHeader title="Recent Execution History" />
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Scheduled Time</TableCell>
                    <TableCell>Executed Time</TableCell>
                    <TableCell>Schedule</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Executed By</TableCell>
                    <TableCell>Notes</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {executions.map((execution) => {
                    const schedule = schedules.find(s => s.id === execution.scheduleId);
                    return (
                      <TableRow key={execution.id}>
                        <TableCell>
                          {new Date(execution.scheduledTime).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          {execution.executedTime 
                            ? new Date(execution.executedTime).toLocaleString()
                            : '-'
                          }
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {schedule?.name || 'Unknown Schedule'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={execution.status.toUpperCase()}
                            color={getStatusColor(execution.status) as any}
                          />
                        </TableCell>
                        <TableCell>
                          {execution.executedBy || '-'}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap>
                            {execution.notes || '-'}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Schedule Dialog */}
      <Dialog 
        open={scheduleDialogOpen} 
        onClose={() => setScheduleDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedSchedule ? 'Edit Schedule' : 'Create New Schedule'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Schedule Name"
                value={scheduleForm.name}
                onChange={(e) => setScheduleForm(prev => ({ ...prev, name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={scheduleForm.type}
                  onChange={(e) => setScheduleForm(prev => ({ ...prev, type: e.target.value as any }))}
                  label="Type"
                >
                  <MenuItem value="monitoring">Monitoring</MenuItem>
                  <MenuItem value="verification">Verification</MenuItem>
                  <MenuItem value="calibration">Calibration</MenuItem>
                  <MenuItem value="review">Review</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Responsible Person"
                value={scheduleForm.responsible}
                onChange={(e) => setScheduleForm(prev => ({ ...prev, responsible: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Interval"
                value={scheduleForm.interval}
                onChange={(e) => setScheduleForm(prev => ({ ...prev, interval: Number(e.target.value) }))}
                inputProps={{ min: 1 }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Unit</InputLabel>
                <Select
                  value={scheduleForm.intervalUnit}
                  onChange={(e) => setScheduleForm(prev => ({ ...prev, intervalUnit: e.target.value as any }))}
                  label="Unit"
                >
                  <MenuItem value="minutes">Minutes</MenuItem>
                  <MenuItem value="hours">Hours</MenuItem>
                  <MenuItem value="days">Days</MenuItem>
                  <MenuItem value="weeks">Weeks</MenuItem>
                  <MenuItem value="months">Months</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Frequency Description"
                value={scheduleForm.frequency}
                onChange={(e) => setScheduleForm(prev => ({ ...prev, frequency: e.target.value }))}
                placeholder="e.g., Every 2 hours"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="date"
                label="Start Date"
                value={scheduleForm.startDate}
                onChange={(e) => setScheduleForm(prev => ({ ...prev, startDate: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="date"
                label="End Date (Optional)"
                value={scheduleForm.endDate}
                onChange={(e) => setScheduleForm(prev => ({ ...prev, endDate: e.target.value }))}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={scheduleForm.description}
                onChange={(e) => setScheduleForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe what this schedule does..."
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={scheduleForm.isActive}
                    onChange={(e) => setScheduleForm(prev => ({ ...prev, isActive: e.target.checked }))}
                  />
                }
                label="Active Schedule"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScheduleDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleSaveSchedule}
            disabled={!scheduleForm.name.trim() || !scheduleForm.responsible.trim()}
          >
            {selectedSchedule ? 'Update' : 'Create'} Schedule
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HACCPSchedules;