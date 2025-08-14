import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemAvatar,
  Avatar,
  Divider,
  Badge,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
} from '@mui/material';
import {
  Business,
  CheckCircle,
  Warning,
  LocalShipping,
  Refresh,
  Add,
  Inventory,
  Science,
  Build,
  Support,
  Assessment,
  Notifications,
  Schedule,
  Error as ErrorIcon,
  Info,
  Analytics,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format, parseISO, subDays, startOfDay, endOfDay } from 'date-fns';
import {
  fetchSupplierDashboard,
  fetchPerformanceAnalytics,
  fetchRiskAssessment,
  fetchAlerts,
  fetchSupplierStats,
  fetchMaterialStats,
  fetchEvaluationStats,
} from '../../store/slices/supplierSlice';
import { fetchSuppliers, fetchMaterials, fetchEvaluations, fetchDeliveries } from '../../store/slices/supplierSlice';
import { RootState, AppDispatch } from '../../store';
import { Supplier, SupplierDashboard as DashboardData } from '../../types/supplier';
import { EnhancedCard } from '../UI';
import { EnhancedStatusChip } from '../UI';
import { NotificationToast } from '../UI';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const SupplierDashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const {
    dashboard,
    dashboardLoading,
    dashboardError,
    performanceAnalytics,
    riskAssessment,
    alerts,
    supplierStats,
    materialStats,
    evaluationStats,
    analyticsLoading,
    alertsLoading,
    statsLoading,
  } = useSelector((state: RootState) => state.supplier);

  const [timeRange, setTimeRange] = useState('30');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ open: false, message: '', severity: 'info' });

  // Load once on mount only; no polling, no re-fetch on state changes
  const loadedOnceRef = React.useRef(false);
  useEffect(() => {
    if (loadedOnceRef.current) return;
    loadedOnceRef.current = true;
    loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadDashboardData = async () => {
    try {
      await Promise.all([
        dispatch(fetchSupplierDashboard()),
        dispatch(fetchSuppliers({} as any)),
        dispatch(fetchMaterials({} as any)),
        dispatch(fetchEvaluations({} as any)),
        dispatch(fetchDeliveries({} as any)),
        dispatch(fetchPerformanceAnalytics({ date_from: getDateFrom() })),
        dispatch(fetchRiskAssessment()),
        dispatch(fetchAlerts({ resolved: false, page: 1, size: 10 })),
        dispatch(fetchSupplierStats()),
        dispatch(fetchMaterialStats()),
        dispatch(fetchEvaluationStats()),
      ]);
    } catch (error) {
      setNotification({
        open: true,
        message: 'Failed to load dashboard data',
        severity: 'error',
      });
    }
  };

  const getDateFrom = () => {
    const days = parseInt(timeRange);
    return format(subDays(new Date(), days), 'yyyy-MM-dd');
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'suspended': return 'warning';
      case 'pending_approval': return 'info';
      case 'blacklisted': return 'error';
      default: return 'default';
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'raw_milk': return <Inventory />;
      case 'additives': return <Add />;
      case 'cultures': return <Science />;
      case 'packaging': return <Inventory />;
      case 'equipment': return <Build />;
      case 'chemicals': return <Science />;
      case 'services': return <Support />;
      default: return <Business />;
    }
  };

  const renderStatisticsCards = () => (
    <Grid container spacing={3} mb={3}>
      {/* Total Suppliers */}
      <Grid item xs={12} sm={6} md={3}>
        <EnhancedCard title="Suppliers Overview" borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h4" fontWeight="bold" color="primary">
                  {dashboard?.total_suppliers || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Suppliers
                </Typography>
              </Box>
              <Avatar sx={{ bgcolor: 'primary.main' }}>
                <Business />
              </Avatar>
            </Box>
          </CardContent>
        </EnhancedCard>
      </Grid>

      {/* Active Suppliers */}
      <Grid item xs={12} sm={6} md={3}>
        <EnhancedCard title="Category Breakdown" borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {dashboard?.active_suppliers || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Suppliers
                </Typography>
              </Box>
              <Avatar sx={{ bgcolor: 'success.main' }}>
                <CheckCircle />
              </Avatar>
            </Box>
          </CardContent>
        </EnhancedCard>
      </Grid>

      {/* Overdue Evaluations */}
      <Grid item xs={12} sm={6} md={3}>
        <EnhancedCard title="Risk Distribution" borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h4" fontWeight="bold" color="warning.main">
                  {dashboard?.overdue_evaluations || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Overdue Evaluations
                </Typography>
              </Box>
              <Avatar sx={{ bgcolor: 'warning.main' }}>
                <Warning />
              </Avatar>
            </Box>
          </CardContent>
        </EnhancedCard>
      </Grid>

      {/* Recent Deliveries */}
      <Grid item xs={12} sm={6} md={3}>
        <EnhancedCard title="Upcoming Evaluations" borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h4" fontWeight="bold" color="info.main">
                  {dashboard?.recent_deliveries?.length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Recent Deliveries
                </Typography>
              </Box>
              <Avatar sx={{ bgcolor: 'info.main' }}>
                <LocalShipping />
              </Avatar>
            </Box>
          </CardContent>
        </EnhancedCard>
      </Grid>
    </Grid>
  );

  const renderCategoryDistribution = () => (
    <Grid container spacing={3} mb={3}>
      <Grid item xs={12} md={6}>
        <EnhancedCard title="Recent Deliveries" borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Suppliers by Category
            </Typography>
            {dashboard?.suppliers_by_category && (
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={dashboard.suppliers_by_category}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {dashboard.suppliers_by_category.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </EnhancedCard>
      </Grid>

      <Grid item xs={12} md={6}>
        <EnhancedCard title="Quality Alerts" borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Suppliers by Risk Level
            </Typography>
            {dashboard?.suppliers_by_risk && (
              <ResponsiveContainer width="100%" height={300}>
                <RechartsBarChart data={dashboard.suppliers_by_risk}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="risk_level" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </RechartsBarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </EnhancedCard>
      </Grid>
    </Grid>
  );

  const renderPerformanceTrends = () => (
    <Grid container spacing={3} mb={3}>
      <Grid item xs={12}>
        <EnhancedCard title="Performance Trends" borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Performance Trends
            </Typography>
            {performanceAnalytics?.trends && (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceAnalytics.trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="average_score"
                    stroke="#8884d8"
                    strokeWidth={2}
                    name="Average Score"
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </EnhancedCard>
      </Grid>
    </Grid>
  );

  const renderRecentActivity = () => (
    <Grid container spacing={3} mb={3}>
      <Grid item xs={12} md={6}>
        <EnhancedCard title="Top Suppliers" borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Recent Evaluations
            </Typography>
            <List>
              {dashboard?.recent_evaluations?.slice(0, 5).map((evaluation, index) => (
                <React.Fragment key={evaluation.id}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.main' }}>
                        <Assessment />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={evaluation.supplier_name}
                      secondary={`Score: ${evaluation.overall_score.toFixed(1)} | ${format(parseISO(evaluation.evaluation_date), 'MMM dd, yyyy')}`}
                    />
                    <Chip
                      label={`${evaluation.overall_score.toFixed(1)}`}
                      color={evaluation.overall_score >= 8 ? 'success' : evaluation.overall_score >= 6 ? 'warning' : 'error'}
                      size="small"
                    />
                  </ListItem>
                  {index < 4 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </EnhancedCard>
      </Grid>

      <Grid item xs={12} md={6}>
        <EnhancedCard title="Actions" borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Recent Deliveries
            </Typography>
            <List>
              {dashboard?.recent_deliveries?.slice(0, 5).map((delivery, index) => (
                <React.Fragment key={delivery.id}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'info.main' }}>
                        <LocalShipping />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={delivery.supplier_name}
                      secondary={`${delivery.material_name} | ${format(parseISO(delivery.delivery_date), 'MMM dd, yyyy')}`}
                    />
                      <EnhancedStatusChip
                        status={delivery.inspection_status as any}
                        label={delivery.inspection_status.replace('_', ' ')}
                      />
                  </ListItem>
                  {index < 4 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </EnhancedCard>
      </Grid>
    </Grid>
  );

  const renderAlerts = () => (
    <Grid container spacing={3} mb={3}>
      <Grid item xs={12}>
        <EnhancedCard title="Notifications" borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" fontWeight="bold">
                Recent Alerts
              </Typography>
              <Button
                size="small"
                startIcon={<Notifications />}
                onClick={() => {/* Navigate to alerts page */}}
              >
                View All
              </Button>
            </Box>
            {alerts?.items && alerts.items.length > 0 ? (
              <List>
                {alerts.items.slice(0, 5).map((alert, index) => (
                  <React.Fragment key={alert.id}>
                    <ListItem>
                      <ListItemIcon>
                        <Avatar sx={{ bgcolor: getAlertColor(alert.severity) }}>
                          {getAlertIcon(alert.type)}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={alert.title}
                        secondary={`${alert.description} | ${format(parseISO(alert.created_at), 'MMM dd, yyyy HH:mm')}`}
                      />
                      <Chip
                        label={alert.severity.toUpperCase()}
                        color={getAlertColor(alert.severity) as any}
                        size="small"
                      />
                    </ListItem>
                    {index < 4 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Box display="flex" justifyContent="center" p={3}>
                <Typography variant="body2" color="text.secondary">
                  No recent alerts
                </Typography>
              </Box>
            )}
          </CardContent>
        </EnhancedCard>
      </Grid>
    </Grid>
  );

  const getAlertColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'info';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'expired_certificate': return <Warning />;
      case 'overdue_evaluation': return <Schedule />;
      case 'quality_alert': return <ErrorIcon />;
      case 'expired_material': return <Inventory />;
      default: return <Info />;
    }
  };

  const renderQuickActions = () => (
    <Grid container spacing={3} mb={3}>
      <Grid item xs={12}>
        <EnhancedCard title="Exports" borderRadius={0} sx={{ background: 'white', borderRadius: 0 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={() => {/* Navigate to create supplier */}}
                >
                  New Supplier
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Assessment />}
                  onClick={() => {/* Navigate to evaluations */}}
                >
                  Schedule Evaluation
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<LocalShipping />}
                  onClick={() => {/* Navigate to deliveries */}}
                >
                  Register Delivery
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Analytics />}
                  onClick={() => {/* Navigate to reports */}}
                >
                  Generate Report
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </EnhancedCard>
      </Grid>
    </Grid>
  );

  if (dashboardLoading) {
    return (
      <Box>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Loading dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Supplier Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Overview of supplier management and performance metrics
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <FormControl size="small">
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="7">Last 7 days</MenuItem>
              <MenuItem value="30">Last 30 days</MenuItem>
              <MenuItem value="90">Last 90 days</MenuItem>
              <MenuItem value="365">Last year</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadDashboardData}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {dashboardError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => {}}>
          {dashboardError}
        </Alert>
      )}

      {/* Statistics Cards */}
      {renderStatisticsCards()}

      {/* Category Distribution */}
      {renderCategoryDistribution()}

      {/* Performance Trends */}
      {renderPerformanceTrends()}

      {/* Recent Activity */}
      {renderRecentActivity()}

      {/* Alerts */}
      {renderAlerts()}

      {/* Quick Actions */}
      {renderQuickActions()}

      {/* Notification Toast */}
      <NotificationToast
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={() => setNotification({ ...notification, open: false })}
      />
    </Box>
  );
};

export default SupplierDashboard; 