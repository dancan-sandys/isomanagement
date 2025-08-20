import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Skeleton,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Fullscreen as FullscreenIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { useInView } from 'react-intersection-observer';
import { performanceUtils } from '../../utils/performance';

// Mock data - replace with real API calls
const mockDashboardData = {
  compliance: {
    score: 94,
    trend: 'up',
    status: 'excellent',
    lastUpdated: new Date(),
  },
  haccp: {
    activePlans: 12,
    criticalIssues: 2,
    status: 'good',
  },
  audits: {
    completed: 45,
    pending: 8,
    overdue: 3,
    status: 'warning',
  },
  suppliers: {
    total: 156,
    approved: 142,
    pending: 14,
    status: 'good',
  },
  training: {
    completed: 89,
    inProgress: 23,
    overdue: 5,
    status: 'warning',
  },
  incidents: {
    total: 12,
    resolved: 10,
    open: 2,
    status: 'good',
  },
};

interface DashboardMetric {
  title: string;
  value: number;
  subtitle: string;
  status: 'excellent' | 'good' | 'warning' | 'error';
  trend?: 'up' | 'down' | 'stable';
  icon: React.ReactNode;
  color: string;
}

const EnhancedDashboard: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [isLoading, setIsLoading] = useState(true);
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Intersection observer for animations
  const [ref, inView] = useInView({
    threshold: 0.1,
    triggerOnce: true,
  });

  // Performance monitoring
  const loadDashboard = async () => {
    return performanceUtils.measureTimeAsync('dashboard-load', async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      return mockDashboardData;
    });
  };

  useEffect(() => {
    const initializeDashboard = async () => {
      try {
        await loadDashboard();
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to load dashboard:', error);
        setIsLoading(false);
      }
    };

    initializeDashboard();
  }, []);

  const metrics: DashboardMetric[] = useMemo(() => [
    {
      title: 'Compliance Score',
      value: mockDashboardData.compliance.score,
      subtitle: 'Overall ISO 22000 compliance',
      status: mockDashboardData.compliance.status as any,
      trend: mockDashboardData.compliance.trend as 'up' | 'down' | 'stable',
      icon: <AssessmentIcon />,
      color: theme.palette.success.main,
    },
    {
      title: 'HACCP Plans',
      value: mockDashboardData.haccp.activePlans,
      subtitle: `${mockDashboardData.haccp.criticalIssues} critical issues`,
      status: mockDashboardData.haccp.status as any,
      icon: <SecurityIcon />,
      color: theme.palette.primary.main,
    },
    {
      title: 'Audits',
      value: mockDashboardData.audits.completed,
      subtitle: `${mockDashboardData.audits.pending} pending, ${mockDashboardData.audits.overdue} overdue`,
      status: mockDashboardData.audits.status as any,
      icon: <TimelineIcon />,
      color: theme.palette.warning.main,
    },
    {
      title: 'Suppliers',
      value: mockDashboardData.suppliers.total,
      subtitle: `${mockDashboardData.suppliers.approved} approved`,
      status: mockDashboardData.suppliers.status as any,
      icon: <CheckCircleIcon />,
      color: theme.palette.info.main,
    },
    {
      title: 'Training',
      value: mockDashboardData.training.completed,
      subtitle: `${mockDashboardData.training.inProgress} in progress`,
      status: mockDashboardData.training.status as any,
      icon: <TrendingUpIcon />,
      color: theme.palette.secondary.main,
    },
    {
      title: 'Incidents',
      value: mockDashboardData.incidents.total,
      subtitle: `${mockDashboardData.incidents.open} open cases`,
      status: mockDashboardData.incidents.status as any,
      icon: <WarningIcon />,
      color: theme.palette.error.main,
    },
  ], [theme]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return theme.palette.success.main;
      case 'good': return theme.palette.success.light;
      case 'warning': return theme.palette.warning.main;
      case 'error': return theme.palette.error.main;
      default: return theme.palette.grey[500];
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent': return <CheckCircleIcon color="success" />;
      case 'good': return <CheckCircleIcon color="success" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'error': return <ErrorIcon color="error" />;
      default: return <CheckCircleIcon />;
    }
  };

  const handleRefresh = () => {
    setSnackbarMessage('Dashboard refreshed successfully');
    setShowSnackbar(true);
  };

  const handleExport = () => {
    setSnackbarMessage('Dashboard exported successfully');
    setShowSnackbar(true);
  };

  const handleShare = () => {
    setSnackbarMessage('Dashboard shared successfully');
    setShowSnackbar(true);
  };

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    setSnackbarMessage(isFullscreen ? 'Exited fullscreen' : 'Entered fullscreen');
    setShowSnackbar(true);
  };

  const speedDialActions = [
    { icon: <RefreshIcon />, name: 'Refresh', action: handleRefresh },
    { icon: <DownloadIcon />, name: 'Export', action: handleExport },
    { icon: <ShareIcon />, name: 'Share', action: handleShare },
    { icon: <FullscreenIcon />, name: 'Fullscreen', action: handleFullscreen },
  ];

  if (isLoading) {
    return (
      <Box p={3}>
        <Grid container spacing={3}>
          {Array.from({ length: 6 }).map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="60%" height={32} />
                  <Skeleton variant="text" width="40%" height={24} />
                  <Skeleton variant="rectangular" width="100%" height={60} sx={{ mt: 2 }} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box 
      p={isMobile ? 2 : 3} 
      sx={{ 
        minHeight: '100vh',
        backgroundColor: theme.palette.background.default,
        transition: 'all 0.3s ease-in-out',
      }}
    >
      {/* Header */}
      <Box 
        display="flex" 
        justifyContent="space-between" 
        alignItems="center" 
        mb={3}
        sx={{ 
          opacity: inView ? 1 : 0,
          transform: inView ? 'translateY(0)' : 'translateY(-20px)',
          transition: 'all 0.6s ease-out',
        }}
        ref={ref}
      >
        <Box display="flex" alignItems="center">
          <DashboardIcon sx={{ mr: 2, fontSize: 32, color: theme.palette.primary.main }} />
          <Box>
            <Typography variant="h4" component="h1" fontWeight="bold">
              ISO 22000 Dashboard
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Last updated: {new Date().toLocaleString()}
        </Typography>
          </Box>
        </Box>
        
        {!isMobile && (
          <Box display="flex" gap={1}>
            <Tooltip title="Refresh Dashboard">
              <IconButton onClick={handleRefresh} color="primary">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export Data">
              <IconButton onClick={handleExport} color="primary">
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Share Dashboard">
              <IconButton onClick={handleShare} color="primary">
                <ShareIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Fullscreen">
              <IconButton onClick={handleFullscreen} color="primary">
                <FullscreenIcon />
              </IconButton>
            </Tooltip>
          </Box>
        )}
      </Box>

      {/* Metrics Grid */}
      <Grid container spacing={3} mb={4}>
        {metrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card
              sx={{
                height: '100%',
                transition: 'all 0.3s ease-in-out',
                transform: inView ? 'translateY(0)' : 'translateY(20px)',
                opacity: inView ? 1 : 0,
                animationDelay: `${index * 0.1}s`,
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.shadows[8],
                },
              }}
            >
        <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Box>
                    <Typography variant="h3" component="div" fontWeight="bold" color={metric.color}>
                      {metric.value}
                    </Typography>
                    <Typography variant="h6" component="div" mb={1}>
                      {metric.title}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {metric.subtitle}
                    </Typography>
                  </Box>
                  <Box display="flex" alignItems="center" gap={1}>
                    {getStatusIcon(metric.status)}
                    {metric.trend && (
                      <Chip
                        label={metric.trend === 'up' ? '↗' : metric.trend === 'down' ? '↘' : '→'}
                        size="small"
                        color={metric.trend === 'up' ? 'success' : metric.trend === 'down' ? 'error' : 'default'}
                      />
                    )}
                  </Box>
                </Box>
                
                <LinearProgress
                  variant="determinate"
                  value={metric.status === 'excellent' ? 100 : metric.status === 'good' ? 75 : metric.status === 'warning' ? 50 : 25}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: theme.palette.grey[200],
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getStatusColor(metric.status),
                    },
                  }}
                />
            </CardContent>
          </Card>
        </Grid>
        ))}
      </Grid>

      {/* Quick Actions */}
      <Box mb={4}>
        <Typography variant="h6" mb={2}>Quick Actions</Typography>
        <Grid container spacing={2}>
          <Grid item xs={6} sm={3}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: theme.shadows[4] } }}>
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <NotificationsIcon color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="body2">View Alerts</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: theme.shadows[4] } }}>
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <AssessmentIcon color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="body2">Run Report</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: theme.shadows[4] } }}>
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <SettingsIcon color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="body2">Settings</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: theme.shadows[4] } }}>
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <SecurityIcon color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="body2">Security</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Mobile Speed Dial */}
      {isMobile && (
        <SpeedDial
          ariaLabel="Dashboard actions"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          icon={<SpeedDialIcon />}
        >
          {speedDialActions.map((action) => (
            <SpeedDialAction
              key={action.name}
              icon={action.icon}
              tooltipTitle={action.name}
              onClick={action.action}
            />
          ))}
        </SpeedDial>
      )}

      {/* Snackbar for notifications */}
      <Snackbar
        open={showSnackbar}
        autoHideDuration={3000}
        onClose={() => setShowSnackbar(false)}
        message={snackbarMessage}
      />
    </Box>
  );
};

export default EnhancedDashboard;
