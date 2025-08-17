import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Avatar,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  TextField,
  Select,
  FormControl,
  InputLabel,
  Divider,
  Stack,
  Badge,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  CircularProgress,
  useTheme,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Schedule,
  Assessment,
  Security,
  BusinessCenter,
  Group,
  Notifications,
  MoreVert,
  Refresh,
  FilterList,
  Add,
  Visibility,
  Edit,
  Assignment,
  Timeline,
  Analytics,
  AccountBalance,
  Shield,
  Cancel,
  ErrorOutline,
} from '@mui/icons-material';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, AreaChart, Area, ScatterChart, Scatter,
} from 'recharts';
import riskAPI from '../../services/riskAPI';
import RiskCreateDialog from './RiskCreateDialog';
import RiskAssessmentWizard from './RiskAssessmentWizard';
import RiskFrameworkConfig from './RiskFrameworkConfig';
import { ISO_STATUS_COLORS, PROFESSIONAL_COLORS } from '../../theme/designSystem';

// ============================================================================
// ISO 31000:2018 DASHBOARD INTERFACES
// ============================================================================

interface RiskDashboardData {
  risk_summary: {
    total_risks: number;
    total_opportunities: number;
    critical_risks: number;
    high_risks: number;
    overdue_reviews: number;
    pending_treatments: number;
    effectiveness_score: number;
    compliance_score: number;
  };
  risk_trends: Array<{
    period: string;
    new_risks: number;
    resolved_risks: number;
    risk_score_avg: number;
    treatment_effectiveness: number;
  }>;
  risk_distribution: {
    by_category: Array<{ category: string; count: number; high_risk_count: number }>;
    by_status: Array<{ status: string; count: number; percentage: number }>;
    by_severity: Array<{ severity: string; count: number; color: string }>;
    by_treatment_strategy: Array<{ strategy: string; count: number; effectiveness: number }>;
  };
  risk_performance: {
    kpis: Array<{
      name: string;
      current_value: number;
      target: number;
      trend: 'up' | 'down' | 'stable';
      status: 'on_track' | 'at_risk' | 'off_track';
    }>;
    monthly_metrics: Array<{
      month: string;
      risks_identified: number;
      risks_resolved: number;
      avg_resolution_time: number;
      compliance_score: number;
    }>;
  };
  risk_alerts: Array<{
    id: number;
    type: 'overdue_review' | 'high_risk' | 'treatment_overdue' | 'framework_review';
    title: string;
    description: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    created_at: string;
    risk_id?: number;
  }>;
  upcoming_activities: Array<{
    id: number;
    type: 'review' | 'monitoring' | 'treatment' | 'assessment';
    title: string;
    due_date: string;
    assigned_to: string;
    risk_id: number;
    priority: 'low' | 'medium' | 'high';
  }>;
}

interface DashboardFilters {
  timeRange: '7d' | '30d' | '90d' | '1y';
  category?: string;
  riskLevel?: string;
  department?: string;
  showOpportunities: boolean;
}

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================

const RiskDashboard: React.FC = () => {
  const theme = useTheme();
  const [dashboardData, setDashboardData] = useState<RiskDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filters, setFilters] = useState<DashboardFilters>({
    timeRange: '30d',
    showOpportunities: true,
  });
  
  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [assessmentWizardOpen, setAssessmentWizardOpen] = useState(false);
  const [frameworkConfigOpen, setFrameworkConfigOpen] = useState(false);
  const [selectedRiskId, setSelectedRiskId] = useState<number | null>(null);
  
  // Menu states
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // ============================================================================
  // DATA FETCHING & EFFECTS
  // ============================================================================

  const fetchDashboardData = async () => {
    try {
      setRefreshing(true);
      const response = await riskAPI.getDashboard();
      if (response.success) {
        setDashboardData(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Set up auto-refresh every 5 minutes for real-time monitoring
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [filters]);

  // ============================================================================
  // COMPUTED VALUES
  // ============================================================================

  const riskTrendData = useMemo(() => {
    if (!dashboardData?.risk_trends) return [];
    return dashboardData.risk_trends.map(item => ({
      ...item,
      net_risk_change: item.new_risks - item.resolved_risks,
    }));
  }, [dashboardData]);

  const criticalAlerts = useMemo(() => {
    return dashboardData?.risk_alerts.filter(alert => 
      alert.severity === 'critical' || alert.severity === 'high'
    ) || [];
  }, [dashboardData]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleRefresh = () => {
    fetchDashboardData();
  };

  const handleCreateRisk = () => {
    setCreateDialogOpen(true);
  };

  const handleAssessRisk = (riskId?: number) => {
    setSelectedRiskId(riskId || null);
    setAssessmentWizardOpen(true);
  };

  const handleFrameworkConfig = () => {
    setFrameworkConfigOpen(true);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return ISO_STATUS_COLORS.nonConformance;
      case 'high': return ISO_STATUS_COLORS.pending;
      case 'medium': return ISO_STATUS_COLORS.warning;
      case 'low': return ISO_STATUS_COLORS.info;
      default: return ISO_STATUS_COLORS.neutral;
    }
  };

  // ============================================================================
  // LOADING STATE
  // ============================================================================

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading ISO 31000:2018 Risk Management Dashboard...
        </Typography>
      </Box>
    );
  }

  if (!dashboardData) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Failed to load dashboard data. Please check your connection and try again.
      </Alert>
    );
  }

  // ============================================================================
  // RENDER DASHBOARD
  // ============================================================================

  return (
    <Box sx={{ p: 3, bgcolor: PROFESSIONAL_COLORS.background.default, minHeight: '100vh' }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography variant="h4" sx={{ 
              fontWeight: 800, 
              color: PROFESSIONAL_COLORS.text.primary,
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }}>
              <Shield sx={{ fontSize: '2rem', color: PROFESSIONAL_COLORS.primary.main }} />
              ISO 31000:2018 Risk Management
            </Typography>
            <Typography variant="subtitle1" color="textSecondary" sx={{ mt: 0.5 }}>
              Comprehensive Risk & Opportunity Dashboard
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => {/* TODO: Implement filters */}}
              >
                Filters
              </Button>
              <Button
                variant="outlined"
                startIcon={refreshing ? <CircularProgress size={16} /> : <Refresh />}
                onClick={handleRefresh}
                disabled={refreshing}
              >
                Refresh
              </Button>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={handleCreateRisk}
                sx={{ bgcolor: PROFESSIONAL_COLORS.primary.main }}
              >
                New Risk/Opportunity
              </Button>
              <IconButton onClick={handleMenuClick}>
                <MoreVert />
              </IconButton>
            </Stack>
          </Grid>
        </Grid>
      </Box>

      {/* Critical Alerts Bar */}
      {criticalAlerts.length > 0 && (
        <Alert 
          severity="error" 
          sx={{ mb: 3, borderRadius: 2 }}
          action={
            <Button color="inherit" size="small">
              View All
            </Button>
          }
        >
          <Typography variant="subtitle2" fontWeight={600}>
            {criticalAlerts.length} Critical Risk Alert{criticalAlerts.length > 1 ? 's' : ''} Require Attention
          </Typography>
        </Alert>
      )}

      {/* KPI Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            height: '100%', 
            background: `linear-gradient(135deg, ${PROFESSIONAL_COLORS.primary.main}, ${PROFESSIONAL_COLORS.primary.light})`,
            color: 'white',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight={700}>
                    {dashboardData.risk_summary.total_risks}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Total Risks
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                  <ErrorOutline sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
              <Box mt={2} display="flex" alignItems="center">
                <Chip 
                  label={`${dashboardData.risk_summary.critical_risks} Critical`}
                  size="small"
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            height: '100%', 
            background: `linear-gradient(135deg, ${ISO_STATUS_COLORS.compliant}, #10B981)`,
            color: 'white'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight={700}>
                    {dashboardData.risk_summary.total_opportunities}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Opportunities
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                  <TrendingUp sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
              <Box mt={2}>
                <LinearProgress 
                  variant="determinate" 
                  value={dashboardData.risk_summary.effectiveness_score} 
                  sx={{ 
                    bgcolor: 'rgba(255,255,255,0.2)',
                    '& .MuiLinearProgress-bar': { bgcolor: 'white' }
                  }}
                />
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  {dashboardData.risk_summary.effectiveness_score}% Effectiveness
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            height: '100%', 
            background: `linear-gradient(135deg, ${ISO_STATUS_COLORS.warning}, #F59E0B)`,
            color: 'white'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight={700}>
                    {dashboardData.risk_summary.overdue_reviews}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Overdue Reviews
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                  <Schedule sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
              <Box mt={2} display="flex" alignItems="center">
                <Chip 
                  label="Requires Action"
                  size="small"
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            height: '100%', 
            background: `linear-gradient(135deg, ${ISO_STATUS_COLORS.info}, #3B82F6)`,
            color: 'white'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight={700}>
                    {dashboardData.risk_summary.compliance_score}%
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    ISO Compliance
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                  <CheckCircle sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
              <Box mt={2}>
                <LinearProgress 
                  variant="determinate" 
                  value={dashboardData.risk_summary.compliance_score} 
                  sx={{ 
                    bgcolor: 'rgba(255,255,255,0.2)',
                    '& .MuiLinearProgress-bar': { bgcolor: 'white' }
                  }}
                />
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  ISO 31000:2018 & ISO 22000:2018
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content Grid */}
      <Grid container spacing={3}>
        {/* Risk Trends Chart */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ height: 400 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Trends & Performance (ISO 31000:2018 Monitoring)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={riskTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="new_risks" 
                    stroke={ISO_STATUS_COLORS.pending} 
                    strokeWidth={2}
                    name="New Risks"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="resolved_risks" 
                    stroke={ISO_STATUS_COLORS.compliant} 
                    strokeWidth={2}
                    name="Resolved Risks"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="treatment_effectiveness" 
                    stroke={ISO_STATUS_COLORS.info} 
                    strokeWidth={2}
                    name="Treatment Effectiveness %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Alerts & Activities */}
        <Grid item xs={12} lg={4}>
          <Stack spacing={2} sx={{ height: 400 }}>
            {/* Risk Alerts */}
            <Card sx={{ flex: 1 }}>
              <CardContent sx={{ pb: 1 }}>
                <Typography variant="h6" gutterBottom>
                  <Badge badgeContent={criticalAlerts.length} color="error">
                    Risk Alerts
                  </Badge>
                </Typography>
                <List dense sx={{ maxHeight: 120, overflow: 'auto' }}>
                  {dashboardData.risk_alerts.slice(0, 3).map((alert) => (
                    <ListItem key={alert.id} sx={{ px: 0 }}>
                      <ListItemIcon>
                        <Warning sx={{ color: getSeverityColor(alert.severity) }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={alert.title}
                        secondary={alert.description}
                        primaryTypographyProps={{ variant: 'body2' }}
                        secondaryTypographyProps={{ variant: 'caption' }}
                      />
                      <ListItemSecondaryAction>
                        <Chip 
                          label={alert.severity} 
                          size="small" 
                          sx={{ 
                            bgcolor: getSeverityColor(alert.severity), 
                            color: 'white',
                            textTransform: 'uppercase',
                            fontSize: '0.65rem'
                          }} 
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>

            {/* Upcoming Activities */}
            <Card sx={{ flex: 1 }}>
              <CardContent sx={{ pb: 1 }}>
                <Typography variant="h6" gutterBottom>
                  Upcoming Activities
                </Typography>
                <List dense sx={{ maxHeight: 120, overflow: 'auto' }}>
                  {dashboardData.upcoming_activities.slice(0, 3).map((activity) => (
                    <ListItem key={activity.id} sx={{ px: 0 }}>
                      <ListItemIcon>
                        <Schedule sx={{ color: PROFESSIONAL_COLORS.primary.main }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={activity.title}
                        secondary={`Due: ${new Date(activity.due_date).toLocaleDateString()} | ${activity.assigned_to}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                        secondaryTypographyProps={{ variant: 'caption' }}
                      />
                      <ListItemSecondaryAction>
                        <Chip 
                          label={activity.priority} 
                          size="small" 
                          variant="outlined"
                          sx={{ textTransform: 'uppercase', fontSize: '0.65rem' }}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Stack>
        </Grid>

        {/* Risk Distribution Charts */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: 350 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Distribution by Category
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={dashboardData.risk_distribution.by_category}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar dataKey="count" fill={PROFESSIONAL_COLORS.primary.main} />
                  <Bar dataKey="high_risk_count" fill={ISO_STATUS_COLORS.nonConformance} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Status Distribution */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: 350 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Status Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={dashboardData.risk_distribution.by_status}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="count"
                    label={({ status, percentage }) => `${status}: ${percentage}%`}
                  >
                    {dashboardData.risk_distribution.by_status.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={Object.values(ISO_STATUS_COLORS)[index % Object.values(ISO_STATUS_COLORS).length]} 
                      />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => { handleAssessRisk(); handleMenuClose(); }}>
          <Assessment sx={{ mr: 1 }} />
          Risk Assessment Wizard
        </MenuItem>
        <MenuItem onClick={() => { handleFrameworkConfig(); handleMenuClose(); }}>
          <BusinessCenter sx={{ mr: 1 }} />
          Framework Configuration
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleMenuClose}>
          <Analytics sx={{ mr: 1 }} />
          Advanced Analytics
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <Timeline sx={{ mr: 1 }} />
          Risk Reports
        </MenuItem>
      </Menu>

      {/* Dialogs */}
      <RiskCreateDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onCreated={() => {
          setCreateDialogOpen(false);
          fetchDashboardData();
        }}
      />

      <RiskAssessmentWizard
        open={assessmentWizardOpen}
        riskId={selectedRiskId}
        onClose={() => setAssessmentWizardOpen(false)}
        onComplete={() => {
          setAssessmentWizardOpen(false);
          fetchDashboardData();
        }}
      />

      <RiskFrameworkConfig
        open={frameworkConfigOpen}
        onClose={() => setFrameworkConfigOpen(false)}
        onSaved={() => {
          setFrameworkConfigOpen(false);
          fetchDashboardData();
        }}
      />
    </Box>
  );
};

export default RiskDashboard;