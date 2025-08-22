import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Upload as UploadIcon
} from '@mui/icons-material';
import { objectivesService } from '../services/objectivesService';
import ObjectivesList from '../components/objectives/ObjectivesList';
import ObjectiveForm from '../components/objectives/ObjectiveForm';
import ProgressChart from '../components/objectives/ProgressChart';
import {
  Objective,
  DashboardKPI,
  PerformanceMetrics,
  ObjectiveAlert
} from '../types/objectives';

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
      id={`objectives-tabpanel-${index}`}
      aria-labelledby={`objectives-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const ObjectivesPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  // Dashboard data
  const [dashboardKPIs, setDashboardKPIs] = useState<DashboardKPI | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics[]>([]);
  const [alerts, setAlerts] = useState<ObjectiveAlert[]>([]);
  
  // Modal states
  const [showForm, setShowForm] = useState(false);
  const [selectedObjective, setSelectedObjective] = useState<Objective | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, [refreshTrigger]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load dashboard data in parallel
      const [kpisResponse, metricsResponse, alertsResponse] = await Promise.all([
        objectivesService.getDashboardKPIs(),
        objectivesService.getPerformanceMetrics(),
        objectivesService.getPerformanceAlerts()
      ]);

      setDashboardKPIs(kpisResponse);
      setPerformanceMetrics(metricsResponse);
      setAlerts(alertsResponse);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const handleFormSubmit = () => {
    setShowForm(false);
    handleRefresh();
  };

  const handleObjectiveSelect = (objective: Objective) => {
    setSelectedObjective(objective);
  };

  const getStatusIcon = (color: string) => {
    switch (color) {
      case 'green': return <CheckCircleIcon color="success" />;
      case 'yellow': return <WarningIcon color="warning" />;
      case 'red': return <ErrorIcon color="error" />;
      default: return <AssessmentIcon color="action" />;
    }
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'improving': return <TrendingUpIcon color="success" />;
      case 'declining': return <TrendingDownIcon color="error" />;
      default: return null;
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h3" component="h1" gutterBottom>
            Objectives Management
          </Typography>
          <Box display="flex" gap={2}>
            <Tooltip title="Refresh Data">
              <IconButton onClick={handleRefresh} color="primary">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setShowForm(true)}
            >
              Add Objective
            </Button>
          </Box>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
      </Box>

      {/* Dashboard KPIs */}
      {dashboardKPIs && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Objectives
                </Typography>
                <Typography variant="h4" component="div">
                  {dashboardKPIs.total_objectives}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Active objectives
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Completed
                </Typography>
                <Typography variant="h4" component="div" color="success.main">
                  {dashboardKPIs.completed_objectives}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {Math.round((dashboardKPIs.completed_objectives / dashboardKPIs.total_objectives) * 100)}% completion rate
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  On Track
                </Typography>
                <Typography variant="h4" component="div" color="success.main">
                  {dashboardKPIs.on_track_objectives}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Performing well
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Behind Schedule
                </Typography>
                <Typography variant="h4" component="div" color="error.main">
                  {dashboardKPIs.behind_schedule_objectives}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Requires attention
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="objectives tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="All Objectives" />
          <Tab label="Performance Overview" />
          <Tab label="Alerts & Notifications" />
        </Tabs>

        {/* All Objectives Tab */}
        <TabPanel value={activeTab} index={0}>
          <ObjectivesList
            onObjectiveSelect={handleObjectiveSelect}
            refreshTrigger={refreshTrigger}
          />
        </TabPanel>

        {/* Performance Overview Tab */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h5" gutterBottom>
                Performance Metrics
              </Typography>
            </Grid>
            
            {performanceMetrics.map((metric) => (
              <Grid item xs={12} md={6} lg={4} key={metric.objective_id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Typography variant="h6" component="div" noWrap sx={{ maxWidth: '70%' }}>
                        {metric.objective_title}
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getStatusIcon(metric.performance_color)}
                        {getTrendIcon(metric.trend_direction)}
                      </Box>
                    </Box>
                    
                    <Typography variant="h4" color="primary" gutterBottom>
                      {Math.round(metric.progress_percentage)}%
                    </Typography>
                    
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      {metric.current_value} / {metric.target_value}
                    </Typography>
                    
                    <Box display="flex" gap={1} flexWrap="wrap" mt={2}>
                      <Chip
                        label={metric.performance_color}
                        color={metric.performance_color === 'green' ? 'success' : 
                               metric.performance_color === 'yellow' ? 'warning' : 'error'}
                        size="small"
                      />
                      <Chip
                        label={metric.trend_direction}
                        variant="outlined"
                        size="small"
                      />
                      {metric.is_overdue && (
                        <Chip
                          label="Overdue"
                          color="error"
                          size="small"
                        />
                      )}
                    </Box>
                    
                    {metric.days_remaining !== null && (
                      <Typography variant="caption" color="textSecondary" display="block" mt={1}>
                        {metric.days_remaining > 0 
                          ? `${metric.days_remaining} days remaining`
                          : `${Math.abs(metric.days_remaining)} days overdue`
                        }
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Alerts & Notifications Tab */}
        <TabPanel value={activeTab} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h5" gutterBottom>
                Alerts & Notifications
              </Typography>
            </Grid>
            
            {alerts.length > 0 ? (
              alerts.map((alert) => (
                <Grid item xs={12} key={alert.id}>
                  <Card>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                        <Box flex={1}>
                          <Typography variant="h6" gutterBottom>
                            {alert.objective_title}
                          </Typography>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            {alert.message}
                          </Typography>
                          <Box display="flex" gap={1} mt={1}>
                            <Chip
                              label={alert.alert_type.replace('_', ' ')}
                              color="primary"
                              size="small"
                            />
                            <Chip
                              label={alert.severity}
                              color={
                                alert.severity === 'critical' ? 'error' :
                                alert.severity === 'high' ? 'warning' :
                                alert.severity === 'medium' ? 'info' : 'default'
                              }
                              size="small"
                            />
                            <Typography variant="caption" color="textSecondary">
                              {new Date(alert.created_at).toLocaleDateString()}
                            </Typography>
                          </Box>
                        </Box>
                        {!alert.is_read && (
                          <Chip label="New" color="error" size="small" />
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))
            ) : (
              <Grid item xs={12}>
                <Alert severity="info">
                  No alerts at this time. All objectives are performing well!
                </Alert>
              </Grid>
            )}
          </Grid>
        </TabPanel>
      </Paper>

      {/* Objective Form Modal */}
      {showForm && (
        <ObjectiveForm
          open={showForm}
          onClose={() => setShowForm(false)}
          onSubmit={handleFormSubmit}
        />
      )}
    </Container>
  );
};

export default ObjectivesPage;
