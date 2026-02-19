import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  IconButton,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Badge,
  Tooltip,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  SelectChangeEvent
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  Dashboard as DashboardIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  Timeline as TimelineIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  Memory as MemoryIcon,
  NetworkCheck as NetworkCheckIcon
} from '@mui/icons-material';
import { analyticsAPI, AnalyticsSummary, KPI, AnalyticsDashboard, AnalyticsReport, TrendAnalysis } from '../services/analyticsAPI';

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
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const Analytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [dashboards, setDashboards] = useState<AnalyticsDashboard[]>([]);
  const [reports, setReports] = useState<AnalyticsReport[]>([]);
  const [trendAnalyses, setTrendAnalyses] = useState<TrendAnalysis[]>([]);
  const [systemHealth, setSystemHealth] = useState<any>(null);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createType, setCreateType] = useState<'kpi' | 'dashboard' | 'report' | 'trend'>('kpi');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all data concurrently
      const [summaryData, kpisData, dashboardsData, reportsData, trendData, healthData] = await Promise.all([
        analyticsAPI.getAnalyticsSummary(),
        analyticsAPI.getKPIs({ limit: 10 }),
        analyticsAPI.getDashboards({ limit: 5 }),
        analyticsAPI.getReports({ limit: 5 }),
        analyticsAPI.getTrendAnalyses({ limit: 5 }),
        analyticsAPI.getSystemHealth()
      ]);

      setSummary(summaryData);
      setKpis(kpisData);
      setDashboards(dashboardsData);
      setReports(reportsData);
      setTrendAnalyses(trendData);
      setSystemHealth(healthData);
    } catch (err) {
      setError('Failed to load analytics data. Please try again.');
      console.error('Error loading analytics data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleCreate = (type: 'kpi' | 'dashboard' | 'report' | 'trend') => {
    setCreateType(type);
    setCreateDialogOpen(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
      case 'completed':
        return 'success';
      case 'draft':
      case 'pending':
        return 'warning';
      case 'archived':
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUpIcon color="success" />;
      case 'decreasing':
        return <TrendingUpIcon sx={{ transform: 'rotate(180deg)' }} color="error" />;
      default:
        return <TimelineIcon color="action" />;
    }
  };

  const getPerformanceColor = (status: string) => {
    switch (status) {
      case 'on_target':
        return 'success';
      case 'below_target':
        return 'error';
      case 'above_target':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={loadData}>
          Retry
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          <AnalyticsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Analytics & Reporting
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive analytics, KPIs, dashboards, and reporting for your ISO 22000 FSMS
        </Typography>
      </Box>

      {/* System Health Overview */}
      {systemHealth && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            System Health
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Box display="flex" alignItems="center">
                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Typography variant="h6">
                    {systemHealth.status}
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box display="flex" alignItems="center">
                <SpeedIcon color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Uptime
                  </Typography>
                  <Typography variant="h6">
                    {systemHealth.uptime}
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box display="flex" alignItems="center">
                <StorageIcon color="info" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Version
                  </Typography>
                  <Typography variant="h6">
                    {systemHealth.version}
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box display="flex" alignItems="center">
                <NetworkCheckIcon color="success" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Last Updated
                  </Typography>
                  <Typography variant="h6">
                    {new Date(systemHealth.timestamp).toLocaleString()}
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Summary Cards */}
      {summary && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <AssessmentIcon color="primary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h4">{summary.total_reports}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Reports
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <BarChartIcon color="secondary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h4">{summary.total_kpis}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Active KPIs
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <DashboardIcon color="success" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h4">{summary.total_dashboards}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Dashboards
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <TrendingUpIcon color="info" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h4">{summary.active_trend_analyses}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Trend Analyses
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Main Content Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="analytics tabs">
            <Tab label="Overview" />
            <Tab label="KPIs" />
            <Tab label="Dashboards" />
            <Tab label="Reports" />
            <Tab label="Trend Analysis" />
          </Tabs>
        </Box>

        {/* Overview Tab */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            {/* Recent Reports */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Reports
                  </Typography>
                  <List>
                    {reports.slice(0, 5).map((report) => (
                      <ListItem key={report.id} divider>
                        <ListItemIcon>
                          <AssessmentIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={report.title}
                          secondary={`${report.report_type} • ${report.status}`}
                        />
                        <Chip
                          label={report.status}
                          color={getStatusColor(report.status) as any}
                          size="small"
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Top KPIs */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Top KPIs
                  </Typography>
                  <List>
                    {kpis.slice(0, 5).map((kpi) => (
                      <ListItem key={kpi.id} divider>
                        <ListItemIcon>
                          {getTrendIcon(kpi.trend)}
                        </ListItemIcon>
                        <ListItemText
                          primary={kpi.display_name}
                          secondary={`${kpi.category} • ${kpi.module}`}
                        />
                        <Box textAlign="right">
                          <Typography variant="h6">
                            {kpi.current_value || 0}{kpi.unit}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Target: {kpi.target_value || 'N/A'}
                          </Typography>
                        </Box>
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* KPIs Tab */}
        <TabPanel value={activeTab} index={1}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Key Performance Indicators</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleCreate('kpi')}
            >
              Create KPI
            </Button>
          </Box>
          <Grid container spacing={3}>
            {kpis.map((kpi) => (
              <Grid item xs={12} sm={6} md={4} key={kpi.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Typography variant="h6" noWrap>
                        {kpi.display_name}
                      </Typography>
                      <Chip
                        label={kpi.is_active ? 'Active' : 'Inactive'}
                        color={kpi.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {kpi.description}
                    </Typography>
                    <Box display="flex" alignItems="center" mb={1}>
                      {getTrendIcon(kpi.trend)}
                      <Typography variant="h4" sx={{ ml: 1 }}>
                        {kpi.current_value || 0}
                      </Typography>
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        {kpi.unit}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Target: {kpi.target_value || 'N/A'}
                    </Typography>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                      <Chip label={kpi.category} size="small" />
                      <Box>
                        <IconButton size="small">
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small">
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Dashboards Tab */}
        <TabPanel value={activeTab} index={2}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Analytics Dashboards</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleCreate('dashboard')}
            >
              Create Dashboard
            </Button>
          </Box>
          <Grid container spacing={3}>
            {dashboards.map((dashboard) => (
              <Grid item xs={12} sm={6} md={4} key={dashboard.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Typography variant="h6" noWrap>
                        {dashboard.name}
                      </Typography>
                      <Chip
                        label={dashboard.is_default ? 'Default' : 'Custom'}
                        color={dashboard.is_default ? 'primary' : 'default'}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {dashboard.description}
                    </Typography>
                    <Box display="flex" alignItems="center" mb={2}>
                      <DashboardIcon color="action" sx={{ mr: 1 }} />
                      <Typography variant="body2">
                        {dashboard.widgets_count || 0} widgets
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Chip
                        label={dashboard.theme}
                        size="small"
                        variant="outlined"
                      />
                      <Box>
                        <IconButton size="small">
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small">
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Reports Tab */}
        <TabPanel value={activeTab} index={3}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Analytics Reports</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleCreate('report')}
            >
              Create Report
            </Button>
          </Box>
          <Grid container spacing={3}>
            {reports.map((report) => (
              <Grid item xs={12} sm={6} md={4} key={report.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Typography variant="h6" noWrap>
                        {report.title}
                      </Typography>
                      <Chip
                        label={report.status}
                        color={getStatusColor(report.status) as any}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {report.description}
                    </Typography>
                    <Box display="flex" alignItems="center" mb={2}>
                      <AssessmentIcon color="action" sx={{ mr: 1 }} />
                      <Typography variant="body2">
                        {report.report_type.replace('_', ' ')}
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Chip
                        label={report.is_public ? 'Public' : 'Private'}
                        size="small"
                        variant="outlined"
                      />
                      <Box>
                        <IconButton size="small">
                          <DownloadIcon />
                        </IconButton>
                        <IconButton size="small">
                          <ShareIcon />
                        </IconButton>
                        <IconButton size="small">
                          <EditIcon />
                        </IconButton>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Trend Analysis Tab */}
        <TabPanel value={activeTab} index={4}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Trend Analysis</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleCreate('trend')}
            >
              Create Analysis
            </Button>
          </Box>
          <Grid container spacing={3}>
            {trendAnalyses.map((analysis) => (
              <Grid item xs={12} sm={6} md={4} key={analysis.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Typography variant="h6" noWrap>
                        {analysis.name}
                      </Typography>
                      <Chip
                        label={analysis.is_active ? 'Active' : 'Inactive'}
                        color={analysis.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {analysis.description}
                    </Typography>
                    <Box display="flex" alignItems="center" mb={2}>
                      <TrendingUpIcon color="action" sx={{ mr: 1 }} />
                      <Typography variant="body2">
                        {analysis.analysis_type} • {analysis.time_period}
                      </Typography>
                    </Box>
                    {analysis.trend_direction && (
                      <Box display="flex" alignItems="center" mb={2}>
                        {getTrendIcon(analysis.trend_direction)}
                        <Typography variant="body2" sx={{ ml: 1 }}>
                          {analysis.trend_direction} trend
                        </Typography>
                      </Box>
                    )}
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Chip
                        label={`${(analysis.confidence_level * 100).toFixed(0)}% confidence`}
                        size="small"
                        variant="outlined"
                      />
                      <Box>
                        <IconButton size="small">
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small">
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>
      </Paper>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setCreateDialogOpen(true)}
      >
        <AddIcon />
      </Fab>

      {/* Create Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Create New {createType.toUpperCase()}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Create a new {createType} for your analytics system.
          </Typography>
          {/* Add form fields based on createType */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Analytics;
