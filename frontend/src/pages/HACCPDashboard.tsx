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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Stack,
  LinearProgress,
  CircularProgress,
  Badge,
  Divider,
  Avatar,
  Tooltip,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  Dashboard,
  Science,
  VerifiedUser,
  Security,
  Warning,
  CheckCircle,
  Error,
  TrendingUp,
  TrendingDown,
  Refresh,
  FilterList,
  Visibility,
  NotificationImportant,
  Schedule,
  Assignment,
  Timeline,
  Analytics,
  Speed,
  Assessment,
  PlayArrow,
  Pause,
  Stop,
  Help,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchProducts, fetchDashboard } from '../store/slices/haccpSlice';
import { haccpAPI } from '../services/api';
import PageHeader from '../components/UI/PageHeader';
import HACCPBreadcrumbs from '../components/UI/HACCPBreadcrumbs';
import StatusChip from '../components/UI/StatusChip';

interface DashboardMetrics {
  overview: {
    totalProducts: number;
    totalCCPs: number;
    activeCCPs: number;
    complianceRate: number;
    lastUpdated: string;
  };
  monitoring: {
    dueToday: number;
    overdue: number;
    completed: number;
    inProgress: number;
    avgCompletionTime: number;
  };
  verification: {
    dueThisWeek: number;
    overdue: number;
    completed: number;
    passRate: number;
  };
  alerts: {
    critical: number;
    high: number;
    medium: number;
    unresolved: number;
  };
  trends: {
    complianceTrend: 'up' | 'down' | 'stable';
    monitoringTrend: 'up' | 'down' | 'stable';
    deviationTrend: 'up' | 'down' | 'stable';
  };
}

interface RecentActivity {
  id: string;
  type: 'monitoring' | 'verification' | 'deviation' | 'alert';
  title: string;
  description: string;
  timestamp: string;
  user: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  status: 'completed' | 'pending' | 'failed';
  ccpId?: number;
  productId?: number;
}

interface CCPStatus {
  id: number;
  name: string;
  number: string;
  productName: string;
  status: 'in_spec' | 'out_of_spec' | 'warning' | 'unknown';
  lastMonitored: string;
  nextMonitoring: string;
  compliance: number;
  recentDeviation?: boolean;
}

const HACCPDashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { products, loading } = useSelector((state: RootState) => state.haccp);
  const { user } = useSelector((state: RootState) => state.auth);

  const [dashboardData, setDashboardData] = useState<DashboardMetrics | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [ccpStatuses, setCcpStatuses] = useState<CCPStatus[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [timeRange, setTimeRange] = useState('24h');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadDashboardData();
    dispatch(fetchProducts());
    
    // Set up auto-refresh
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(loadDashboardData, 30000); // 30 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [dispatch, timeRange, autoRefresh]);

  const loadDashboardData = async () => {
    setRefreshing(true);
    try {
      // Mock data - replace with actual API calls
      const mockMetrics: DashboardMetrics = {
        overview: {
          totalProducts: 12,
          totalCCPs: 24,
          activeCCPs: 22,
          complianceRate: 94.5,
          lastUpdated: new Date().toISOString(),
        },
        monitoring: {
          dueToday: 8,
          overdue: 2,
          completed: 24,
          inProgress: 3,
          avgCompletionTime: 15, // minutes
        },
        verification: {
          dueThisWeek: 4,
          overdue: 1,
          completed: 12,
          passRate: 91.7,
        },
        alerts: {
          critical: 1,
          high: 3,
          medium: 7,
          unresolved: 11,
        },
        trends: {
          complianceTrend: 'up',
          monitoringTrend: 'stable',
          deviationTrend: 'down',
        },
      };
      setDashboardData(mockMetrics);

      const mockActivity: RecentActivity[] = [
        {
          id: '1',
          type: 'deviation',
          title: 'Temperature Deviation Detected',
          description: 'CCP-1 temperature reading 68°C below critical limit',
          timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          user: 'Production Operator',
          severity: 'critical',
          status: 'pending',
          ccpId: 1,
          productId: 1,
        },
        {
          id: '2',
          type: 'monitoring',
          title: 'pH Monitoring Completed',
          description: 'CCP-2 pH verified at 4.1 - within limits',
          timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
          user: 'QA Specialist',
          status: 'completed',
          ccpId: 2,
          productId: 2,
        },
        {
          id: '3',
          type: 'verification',
          title: 'Equipment Calibration Verified',
          description: 'Temperature probe TMP-001 calibrated successfully',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          user: 'QA Manager',
          status: 'completed',
        },
        {
          id: '4',
          type: 'alert',
          title: 'Monitoring Schedule Missed',
          description: 'Water activity monitoring was missed at 12:00',
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          user: 'System',
          severity: 'medium',
          status: 'pending',
          ccpId: 3,
          productId: 3,
        },
        {
          id: '5',
          type: 'monitoring',
          title: 'Metal Detection Test Passed',
          description: 'CCP-4 metal detection system functioning correctly',
          timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          user: 'Production Supervisor',
          status: 'completed',
          ccpId: 4,
          productId: 1,
        },
      ];
      setRecentActivity(mockActivity);

      const mockCCPStatuses: CCPStatus[] = [
        {
          id: 1,
          name: 'Temperature Control',
          number: 'CCP-1',
          productName: 'Chicken Breast',
          status: 'out_of_spec',
          lastMonitored: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          nextMonitoring: new Date(Date.now() + 115 * 60 * 1000).toISOString(),
          compliance: 85.2,
          recentDeviation: true,
        },
        {
          id: 2,
          name: 'pH Control',
          number: 'CCP-2',
          productName: 'Pickled Vegetables',
          status: 'in_spec',
          lastMonitored: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
          nextMonitoring: new Date(Date.now() + 45 * 60 * 1000).toISOString(),
          compliance: 98.1,
        },
        {
          id: 3,
          name: 'Water Activity',
          number: 'CCP-3',
          productName: 'Dried Fruits',
          status: 'warning',
          lastMonitored: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          nextMonitoring: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
          compliance: 91.5,
        },
        {
          id: 4,
          name: 'Metal Detection',
          number: 'CCP-4',
          productName: 'Packaged Snacks',
          status: 'in_spec',
          lastMonitored: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          nextMonitoring: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
          compliance: 99.3,
        },
      ];
      setCcpStatuses(mockCCPStatuses);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'monitoring':
        return <Science />;
      case 'verification':
        return <VerifiedUser />;
      case 'deviation':
        return <Warning />;
      case 'alert':
        return <NotificationImportant />;
      default:
        return <Assignment />;
    }
  };

  const getActivityColor = (severity?: string, status?: string) => {
    if (status === 'failed') return 'error';
    if (severity === 'critical') return 'error';
    if (severity === 'high') return 'warning';
    if (severity === 'medium') return 'info';
    if (status === 'completed') return 'success';
    return 'default';
  };

  const getCCPStatusIcon = (status: string) => {
    switch (status) {
      case 'in_spec':
        return <CheckCircle color="success" />;
      case 'out_of_spec':
        return <Error color="error" />;
      case 'warning':
        return <Warning color="warning" />;
      case 'unknown':
        return <Help color="disabled" />;
      default:
        return <CheckCircle />;
    }
  };

  const getCCPStatusColor = (status: string) => {
    switch (status) {
      case 'in_spec':
        return 'success';
      case 'out_of_spec':
        return 'error';
      case 'warning':
        return 'warning';
      case 'unknown':
        return 'default';
      default:
        return 'default';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp color="success" />;
      case 'down':
        return <TrendingDown color="error" />;
      case 'stable':
        return <Timeline color="info" />;
      default:
        return <Timeline />;
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const formatNextMonitoring = (timestamp: string) => {
    const now = new Date();
    const next = new Date(timestamp);
    const diffMs = next.getTime() - now.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);

    if (diffMs < 0) return 'Overdue';
    if (diffMins < 60) return `${diffMins}m`;
    return `${diffHours}h`;
  };

  if (loading || !dashboardData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <HACCPBreadcrumbs />
      <PageHeader
        title="HACCP Dashboard"
        subtitle="Real-time monitoring and control of HACCP system"
        showAdd={false}
      />

      {/* Header Controls */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <ToggleButtonGroup
            value={timeRange}
            exclusive
            onChange={(_, value) => value && setTimeRange(value)}
            size="small"
          >
            <ToggleButton value="24h">24H</ToggleButton>
            <ToggleButton value="7d">7D</ToggleButton>
            <ToggleButton value="30d">30D</ToggleButton>
          </ToggleButtonGroup>
          
          <Typography variant="body2" color="textSecondary">
            Last updated: {formatTimeAgo(dashboardData.overview.lastUpdated)}
          </Typography>
        </Stack>

        <Stack direction="row" spacing={1}>
          <Tooltip title={autoRefresh ? 'Disable auto-refresh' : 'Enable auto-refresh'}>
            <IconButton
              onClick={() => setAutoRefresh(!autoRefresh)}
              color={autoRefresh ? 'primary' : 'default'}
            >
              {autoRefresh ? <PlayArrow /> : <Pause />}
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadDashboardData}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </Button>
        </Stack>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Overall Compliance
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {dashboardData.overview.complianceRate}%
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1} mt={1}>
                    {getTrendIcon(dashboardData.trends.complianceTrend)}
                    <Typography variant="body2" color="textSecondary">
                      vs last period
                    </Typography>
                  </Box>
                </Box>
                <Speed color="primary" sx={{ fontSize: 40 }} />
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
                    {dashboardData.overview.activeCCPs}/{dashboardData.overview.totalCCPs}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={(dashboardData.overview.activeCCPs / dashboardData.overview.totalCCPs) * 100}
                    sx={{ mt: 1, height: 6, borderRadius: 3 }}
                  />
                </Box>
                <Security color="secondary" sx={{ fontSize: 40 }} />
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
                    {dashboardData.alerts.critical}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {dashboardData.alerts.unresolved} unresolved
                  </Typography>
                </Box>
                <Badge badgeContent={dashboardData.alerts.critical} color="error">
                  <NotificationImportant color="error" sx={{ fontSize: 40 }} />
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
                    Monitoring Tasks
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {dashboardData.monitoring.dueToday}
                  </Typography>
                  <Typography variant="body2" color="error">
                    {dashboardData.monitoring.overdue} overdue
                  </Typography>
                </Box>
                <Badge badgeContent={dashboardData.monitoring.overdue} color="error">
                  <Schedule color="warning" sx={{ fontSize: 40 }} />
                </Badge>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* CCP Status Overview */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardHeader 
              title="CCP Status Overview"
              action={
                <IconButton onClick={() => window.open('/haccp/monitoring', '_blank')}>
                  <Visibility />
                </IconButton>
              }
            />
            <CardContent>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>CCP</TableCell>
                      <TableCell>Product</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Last Monitored</TableCell>
                      <TableCell>Next Due</TableCell>
                      <TableCell>Compliance</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {ccpStatuses.map((ccp) => (
                      <TableRow key={ccp.id}>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            {getCCPStatusIcon(ccp.status)}
                            <Typography variant="body2" fontWeight="medium">
                              {ccp.number}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              {ccp.name}
                            </Typography>
                            <Typography variant="caption" color="textSecondary">
                              {ccp.productName}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Stack direction="row" spacing={1} alignItems="center">
                            <StatusChip 
                              status={ccp.status} 
                              label={ccp.status.replace('_', ' ').toUpperCase()} 
                            />
                            {ccp.recentDeviation && (
                              <Chip
                                size="small"
                                label="DEVIATION"
                                color="error"
                                variant="outlined"
                              />
                            )}
                          </Stack>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {formatTimeAgo(ccp.lastMonitored)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography 
                            variant="body2"
                            color={new Date(ccp.nextMonitoring).getTime() < Date.now() ? 'error' : 'textPrimary'}
                          >
                            {formatNextMonitoring(ccp.nextMonitoring)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <LinearProgress
                              variant="determinate"
                              value={ccp.compliance}
                              sx={{ 
                                width: 60, 
                                height: 6, 
                                borderRadius: 3,
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: ccp.compliance >= 95 ? '#4caf50' : 
                                                 ccp.compliance >= 85 ? '#ff9800' : '#f44336'
                                }
                              }}
                            />
                            <Typography variant="body2">
                              {ccp.compliance.toFixed(1)}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <IconButton 
                            size="small"
                            onClick={() => window.open(`/haccp/products/${ccp.id}`, '_blank')}
                          >
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
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardHeader 
              title="Recent Activity"
              subheader={`${recentActivity.length} recent events`}
            />
            <CardContent sx={{ maxHeight: 400, overflow: 'auto' }}>
              <List dense>
                {recentActivity.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem alignItems="flex-start" sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <Avatar 
                          sx={{ 
                            width: 28, 
                            height: 28,
                            bgcolor: `${getActivityColor(activity.severity, activity.status)}.main`,
                            color: 'white'
                          }}
                        >
                          {getActivityIcon(activity.type)}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2" fontWeight="medium">
                            {activity.title}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                              {activity.description}
                            </Typography>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="caption" color="textSecondary">
                                {formatTimeAgo(activity.timestamp)} • {activity.user}
                              </Typography>
                              {activity.severity && (
                                <Chip
                                  size="small"
                                  label={activity.severity.toUpperCase()}
                                  color={getActivityColor(activity.severity) as any}
                                  variant="outlined"
                                />
                              )}
                            </Box>
                          </Box>
                        }
                      />
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </ListItem>
                    {index < recentActivity.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Monitoring Performance" />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="success.main">
                      {dashboardData.monitoring.completed}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Completed Today
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="primary">
                      {dashboardData.monitoring.avgCompletionTime}m
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Avg Completion Time
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="info.main">
                      {dashboardData.monitoring.inProgress}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      In Progress
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="error.main">
                      {dashboardData.monitoring.overdue}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Overdue
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Verification Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Verification Status" />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="success.main">
                      {dashboardData.verification.completed}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Completed
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="primary">
                      {dashboardData.verification.passRate}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Pass Rate
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="warning.main">
                      {dashboardData.verification.dueThisWeek}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Due This Week
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="error.main">
                      {dashboardData.verification.overdue}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Overdue
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Box sx={{ position: 'fixed', bottom: 16, right: 16 }}>
        <Stack spacing={2}>
          <Button
            variant="contained"
            startIcon={<Science />}
            onClick={() => window.open('/haccp/monitoring', '_blank')}
            sx={{ borderRadius: 28 }}
          >
            Monitoring Console
          </Button>
        </Stack>
      </Box>
    </Box>
  );
};

export default HACCPDashboard;