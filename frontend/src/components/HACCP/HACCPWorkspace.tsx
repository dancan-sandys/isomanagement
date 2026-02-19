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
  Tooltip,
  Badge,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  CircularProgress,
  Stack,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  Add,
  Warning,
  CheckCircle,
  Error,
  Info,
  Science,
  Security,
  TrendingUp,
  TrendingDown,
  Schedule,
  Notifications,
  Refresh,
  Visibility,
  Edit,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { fetchProducts, fetchDashboard } from '../../store/slices/haccpSlice';
import { haccpAPI } from '../../services/api';
import StatusChip from '../UI/StatusChip';

interface Alert {
  id: string;
  type: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  message: string;
  timestamp: string;
  requiresAction: boolean;
}

interface DashboardMetrics {
  totalProducts: number;
  totalHazards: number;
  totalCCPs: number;
  activeCCPs: number;
  recentMonitoringLogs: number;
  complianceRate: number;
  overdueMonitoring: number;
  pendingVerifications: number;
  highRiskHazards: number;
}

const HACCPWorkspace: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { products, loading, error } = useSelector((state: RootState) => state.haccp);
  
  const [dashboardData, setDashboardData] = useState<DashboardMetrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);

  useEffect(() => {
    loadWorkspaceData();
  }, []);

  const loadWorkspaceData = async () => {
    setLoadingDashboard(true);
    try {
      // Load products
      await dispatch(fetchProducts());
      
      // Load dashboard data
      const dashboardResponse = await haccpAPI.getEnhancedDashboard();
      if (dashboardResponse.success) {
        setDashboardData(dashboardResponse.data.overview);
        setAlerts(dashboardResponse.data.alerts);
      }
    } catch (error) {
      console.error('Error loading workspace data:', error);
    } finally {
      setLoadingDashboard(false);
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'critical':
        return <Error color="error" />;
      case 'high':
        return <Warning color="warning" />;
      case 'medium':
        return <Info color="info" />;
      case 'low':
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
        return 'success';
      default:
        return 'info';
    }
  };

  const handleProductClick = (productId: number) => {
    navigate(`/haccp/products/${productId}`);
  };

  const handleCreateProduct = () => {
    navigate('/haccp/products/new');
  };

  const handleViewAlerts = () => {
    navigate('/haccp/alerts');
  };

  const handleViewDashboard = () => {
    navigate('/haccp/dashboard');
  };

  if (loading || loadingDashboard) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          HACCP Workspace
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadWorkspaceData}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreateProduct}
          >
            New Product
          </Button>
        </Stack>
      </Box>

      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Key Metrics"
              action={
                <IconButton onClick={handleViewDashboard}>
                  <Visibility />
                </IconButton>
              }
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {dashboardData?.totalProducts || 0}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Products
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="secondary">
                      {dashboardData?.totalCCPs || 0}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      CCPs
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="success.main">
                      {dashboardData?.complianceRate || 0}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Compliance
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="warning.main">
                      {dashboardData?.overdueMonitoring || 0}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Overdue
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
              
              {/* Compliance Progress */}
              <Box sx={{ mt: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Overall Compliance</Typography>
                  <Typography variant="body2">{dashboardData?.complianceRate || 0}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={dashboardData?.complianceRate || 0}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: 'grey.200',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 4,
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Quick Actions" />
            <CardContent>
              <Stack spacing={2}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Science />}
                  onClick={() => navigate('/haccp/monitoring')}
                >
                  Monitoring Console
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Security />}
                  onClick={() => navigate('/haccp/verification')}
                >
                  Verification Console
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Schedule />}
                  onClick={() => navigate('/haccp/schedules')}
                >
                  View Schedules
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<TrendingUp />}
                  onClick={() => navigate('/haccp/reports')}
                >
                  Generate Reports
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Alerts */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Badge badgeContent={alerts.length} color="error" sx={{ mr: 1 }}>
                    <Notifications />
                  </Badge>
                  Alerts
                </Box>
              }
              action={
                <IconButton onClick={handleViewAlerts}>
                  <Visibility />
                </IconButton>
              }
            />
            <CardContent>
              {alerts.length === 0 ? (
                <Alert severity="success">
                  No active alerts. All systems are operating normally.
                </Alert>
              ) : (
                <List>
                  {alerts.slice(0, 5).map((alert, index) => (
                    <React.Fragment key={alert.id}>
                      <ListItem>
                        <ListItemIcon>
                          {getAlertIcon(alert.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={alert.title}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary">
                                {alert.message}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                {new Date(alert.timestamp).toLocaleString()}
                              </Typography>
                            </Box>
                          }
                        />
                        {alert.requiresAction && (
                          <Chip
                            label="Action Required"
                            color="error"
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </ListItem>
                      {index < alerts.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Products */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Recent Products"
              action={
                <IconButton onClick={() => navigate('/haccp/products')}>
                  <Visibility />
                </IconButton>
              }
            />
            <CardContent>
              {products.length === 0 ? (
                <Alert severity="info">
                  No products found. Create your first product to get started.
                </Alert>
              ) : (
                <List>
                  {products.slice(0, 5).map((product, index) => (
                    <React.Fragment key={product.id}>
                      <ListItem
                        button
                        onClick={() => handleProductClick(product.id)}
                      >
                        <ListItemIcon>
                          <Avatar sx={{ bgcolor: product.haccp_plan_approved ? 'success.main' : 'warning.main' }}>
                            {product.haccp_plan_approved ? <CheckCircle /> : <Warning />}
                          </Avatar>
                        </ListItemIcon>
                        <ListItemText
                          primary={product.name}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary">
                                {product.product_code}
                              </Typography>
                              <Box sx={{ mt: 1 }}>
                                <StatusChip
                                  status={product.haccp_plan_approved ? 'approved' : 'pending'}
                                  label={product.haccp_plan_approved ? 'Plan Approved' : 'Plan Pending'}
                                />
                              </Box>
                            </Box>
                          }
                        />
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                      </ListItem>
                      {index < products.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Overview */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Risk Overview" />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2} bgcolor="success.light" borderRadius={1}>
                    <Typography variant="h6" color="success.dark">
                      {dashboardData?.totalHazards ? dashboardData.totalHazards - (dashboardData.highRiskHazards || 0) : 0}
                    </Typography>
                    <Typography variant="body2" color="success.dark">
                      Low Risk Hazards
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2} bgcolor="warning.light" borderRadius={1}>
                    <Typography variant="h6" color="warning.dark">
                      {dashboardData?.highRiskHazards || 0}
                    </Typography>
                    <Typography variant="body2" color="warning.dark">
                      High Risk Hazards
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2} bgcolor="info.light" borderRadius={1}>
                    <Typography variant="h6" color="info.dark">
                      {dashboardData?.pendingVerifications || 0}
                    </Typography>
                    <Typography variant="body2" color="info.dark">
                      Pending Verifications
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center" p={2} bgcolor="error.light" borderRadius={1}>
                    <Typography variant="h6" color="error.dark">
                      {dashboardData?.overdueMonitoring || 0}
                    </Typography>
                    <Typography variant="body2" color="error.dark">
                      Overdue Monitoring
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default HACCPWorkspace;
