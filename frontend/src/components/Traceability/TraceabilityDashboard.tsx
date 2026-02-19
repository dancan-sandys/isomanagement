import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  alpha,
  LinearProgress
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Security as SecurityIcon,
  VerifiedUser as VerifiedUserIcon,
  QrCode as QrCodeIcon,
  Business as BusinessIcon,
  LocalShipping as LocalShippingIcon,
  Inventory as InventoryIcon,
  Notifications as NotificationsIcon,
  Assessment as AssessmentIcon,
  Schedule as ScheduleIcon,
  People as PeopleIcon,
  Description as DescriptionIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon,
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { traceabilityAPI } from '../../services/traceabilityAPI';

interface TraceabilityDashboardProps {
  onBatchSelect?: (batch: any) => void;
  onRecallSelect?: (recall: any) => void;
}

interface DashboardData {
  summary: {
    total_batches: number;
    active_recalls: number;
    trace_completeness_avg: number;
    verification_pending: number;
    ccp_alerts: number;
    recent_activities: any[];
  };
  traceability: {
    completeness_trend: any[];
    verification_status: any[];
    ccp_compliance: any[];
    recent_traces: any[];
  };
  recalls: {
    by_status: any[];
    by_type: any[];
    effectiveness_scores: any[];
    recent_recalls: any[];
  };
  alerts: {
    high_priority: any[];
    medium_priority: any[];
    low_priority: any[];
  };
}

const TraceabilityDashboard: React.FC<TraceabilityDashboardProps> = ({
  onBatchSelect,
  onRecallSelect
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedView, setSelectedView] = useState('overview');

  useEffect(() => {
    loadDashboardData();
  }, [timeRange]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load dashboard data from API
      const response = await traceabilityAPI.getDashboard();
      
      // Transform the data for the dashboard
      const transformedData: DashboardData = {
        summary: {
          total_batches: response?.total_batches || 0,
          active_recalls: response?.active_recalls || 0,
          trace_completeness_avg: response?.trace_completeness_avg || 0,
          verification_pending: response?.verification_pending || 0,
          ccp_alerts: response?.ccp_alerts || 0,
          recent_activities: response?.recent_activities || []
        },
        traceability: {
          completeness_trend: response?.completeness_trend || [],
          verification_status: response?.verification_status || [],
          ccp_compliance: response?.ccp_compliance || [],
          recent_traces: response?.recent_traces || []
        },
        recalls: {
          by_status: response?.recalls_by_status || [],
          by_type: response?.recalls_by_type || [],
          effectiveness_scores: response?.effectiveness_scores || [],
          recent_recalls: response?.recent_recalls || []
        },
        alerts: {
          high_priority: response?.high_priority_alerts || [],
          medium_priority: response?.medium_priority_alerts || [],
          low_priority: response?.low_priority_alerts || []
        }
      };

      setDashboardData(transformedData);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'verified':
      case 'passed':
        return 'success';
      case 'pending':
      case 'in_progress':
        return 'warning';
      case 'failed':
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const renderSummaryCards = () => (
    <Grid container spacing={3} mb={3}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="text.secondary" gutterBottom>
                  Total Batches
                </Typography>
                <Typography variant="h4" fontWeight={700}>
                  {dashboardData?.summary.total_batches || 0}
                </Typography>
              </Box>
              <InventoryIcon color="primary" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="text.secondary" gutterBottom>
                  Active Recalls
                </Typography>
                <Typography variant="h4" fontWeight={700} color="warning.main">
                  {dashboardData?.summary.active_recalls || 0}
                </Typography>
              </Box>
              <WarningIcon color="warning" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="text.secondary" gutterBottom>
                  Trace Completeness
                </Typography>
                <Typography variant="h4" fontWeight={700} color="success.main">
                  {dashboardData?.summary.trace_completeness_avg || 0}%
                </Typography>
              </Box>
              <TimelineIcon color="success" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="text.secondary" gutterBottom>
                  CCP Alerts
                </Typography>
                <Typography variant="h4" fontWeight={700} color="error.main">
                  {dashboardData?.summary.ccp_alerts || 0}
                </Typography>
              </Box>
              <SecurityIcon color="error" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderTraceabilityOverview = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Typography variant="h6" fontWeight={600}>
                Verification Status
              </Typography>
              <IconButton size="small" onClick={loadDashboardData}>
                <RefreshIcon />
              </IconButton>
            </Box>
            
            {dashboardData?.traceability.verification_status?.map((item: any, index: number) => (
              <Box key={index} mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">{item.status}</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {item.count}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={(item.count / dashboardData.summary.total_batches) * 100}
                  color={getStatusColor(item.status) as any}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Recent Trace Activities
            </Typography>
            
            <List dense>
              {dashboardData?.traceability.recent_traces?.slice(0, 5).map((trace: any, index: number) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemIcon>
                    <TimelineIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={trace.batch_number}
                    secondary={`${trace.action} - ${trace.timestamp}`}
                  />
                  <Chip
                    label={trace.status}
                    size="small"
                    color={getStatusColor(trace.status) as any}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderRecallManagement = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Recalls by Status
            </Typography>
            
            {dashboardData?.recalls.by_status?.map((item: any, index: number) => (
              <Box key={index} mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">{item.status}</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {item.count}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={(item.count / dashboardData.summary.active_recalls) * 100}
                  color={getStatusColor(item.status) as any}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Recent Recalls
            </Typography>
            
            <List dense>
              {dashboardData?.recalls.recent_recalls?.slice(0, 5).map((recall: any, index: number) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemIcon>
                    <WarningIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary={recall.issue_type}
                    secondary={`${recall.recall_type} - ${recall.created_at}`}
                  />
                  <Chip
                    label={recall.status}
                    size="small"
                    color={getStatusColor(recall.status) as any}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderAlertsAndNotifications = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={600} mb={2} color="error.main">
              High Priority Alerts
            </Typography>
            
            <List dense>
              {dashboardData?.alerts.high_priority?.slice(0, 3).map((alert: any, index: number) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemIcon>
                    <ErrorIcon color="error" />
                  </ListItemIcon>
                  <ListItemText
                    primary={alert.title}
                    secondary={alert.description}
                  />
                </ListItem>
              ))}
              {(!dashboardData?.alerts.high_priority || dashboardData.alerts.high_priority.length === 0) && (
                <ListItem>
                  <ListItemText
                    primary="No high priority alerts"
                    secondary="All systems operating normally"
                  />
                </ListItem>
              )}
            </List>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={600} mb={2} color="warning.main">
              Medium Priority Alerts
            </Typography>
            
            <List dense>
              {dashboardData?.alerts.medium_priority?.slice(0, 3).map((alert: any, index: number) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemIcon>
                    <WarningIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary={alert.title}
                    secondary={alert.description}
                  />
                </ListItem>
              ))}
              {(!dashboardData?.alerts.medium_priority || dashboardData.alerts.medium_priority.length === 0) && (
                <ListItem>
                  <ListItemText
                    primary="No medium priority alerts"
                    secondary="All systems operating normally"
                  />
                </ListItem>
              )}
            </List>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={600} mb={2} color="info.main">
              Recent Activities
            </Typography>
            
            <List dense>
              {dashboardData?.summary.recent_activities?.slice(0, 5).map((activity: any, index: number) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemIcon>
                    <InfoIcon color="info" />
                  </ListItemIcon>
                  <ListItemText
                    primary={activity.action}
                    secondary={activity.timestamp}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderFilters = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
          <Typography variant="h6" fontWeight={600}>
            <FilterIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Dashboard Filters
          </Typography>
          
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              label="Time Range"
            >
              <MenuItem value="1d">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last 90 Days</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>View</InputLabel>
            <Select
              value={selectedView}
              onChange={(e) => setSelectedView(e.target.value)}
              label="View"
            >
              <MenuItem value="overview">Overview</MenuItem>
              <MenuItem value="traceability">Traceability</MenuItem>
              <MenuItem value="recalls">Recalls</MenuItem>
              <MenuItem value="alerts">Alerts</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadDashboardData}
            size="small"
          >
            Refresh
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={48} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <TimelineIcon color="primary" sx={{ fontSize: 32 }} />
        <Box flex={1}>
          <Typography variant="h4" fontWeight={600}>
            Traceability Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time monitoring and analytics for traceability and recall management
          </Typography>
        </Box>
      </Box>

      {renderFilters()}

      {renderSummaryCards()}

      {selectedView === 'overview' && (
        <>
          <Typography variant="h5" fontWeight={600} mb={3}>
            Traceability Overview
          </Typography>
          {renderTraceabilityOverview()}

          <Typography variant="h5" fontWeight={600} mb={3} mt={4}>
            Recall Management
          </Typography>
          {renderRecallManagement()}

          <Typography variant="h5" fontWeight={600} mb={3} mt={4}>
            Alerts & Notifications
          </Typography>
          {renderAlertsAndNotifications()}
        </>
      )}

      {selectedView === 'traceability' && (
        <>
          <Typography variant="h5" fontWeight={600} mb={3}>
            Traceability Analytics
          </Typography>
          {renderTraceabilityOverview()}
        </>
      )}

      {selectedView === 'recalls' && (
        <>
          <Typography variant="h5" fontWeight={600} mb={3}>
            Recall Management
          </Typography>
          {renderRecallManagement()}
        </>
      )}

      {selectedView === 'alerts' && (
        <>
          <Typography variant="h5" fontWeight={600} mb={3}>
            Alerts & Notifications
          </Typography>
          {renderAlertsAndNotifications()}
        </>
      )}
    </Box>
  );
};

export default TraceabilityDashboard;
