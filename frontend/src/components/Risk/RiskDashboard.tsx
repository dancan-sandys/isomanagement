import React, { useState, useEffect, useMemo, useCallback } from 'react';
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
  compliance_status?: {
    compliance_score: number;
    iso_31000_compliance: boolean;
    compliance_checks: {
      fsms_integration: boolean;
      // Add other compliance checks here
    };
    recommendations: Array<string>;
  };
  performance_metrics?: {
    overall_performance: number;
    treatment_efficiency: number;
    resolution_rate: number;
    review_compliance: number;
    total_risks: number;
    overdue_reviews: number;
    pending_treatments: number;
  };
  enhanced_trends?: Array<{
    period: string;
    new_risks: number;
    resolved_risks: number;
    new_opportunities: number;
    avg_risk_score: number;
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
  const [complianceDialogOpen, setComplianceDialogOpen] = useState(false);
  
  // Menu states
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // ============================================================================
  // DATA FETCHING & EFFECTS
  // ============================================================================

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const [dashboardResponse, performanceResponse, complianceResponse, trendsResponse] = await Promise.all([
        riskAPI.getDashboard(),
        riskAPI.getPerformance(),
        riskAPI.getComplianceStatus(),
        riskAPI.getTrends('monthly', 6)
      ]);
      
      if (dashboardResponse.success) {
        setDashboardData(dashboardResponse.data);
      }
      
      // Enhance dashboard data with new analytics
      if (performanceResponse.success) {
        setDashboardData(prev => ({
          ...prev,
          performance_metrics: performanceResponse.data
        }));
      }
      
      if (complianceResponse.success) {
        setDashboardData(prev => ({
          ...prev,
          compliance_status: complianceResponse.data
        }));
      }
      
      if (trendsResponse.success) {
        setDashboardData(prev => ({
          ...prev,
          enhanced_trends: trendsResponse.data.trends
        }));
      }
      
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      // setError('Failed to load dashboard data'); // This line was not in the new_code, so it's removed.
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
    
    // Set up auto-refresh every 5 minutes for real-time monitoring
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchDashboardData]); // Added fetchDashboardData to dependencies

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

        {/* ISO Compliance Status Card */}
        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ 
            height: 140, 
            background: dashboardData.compliance_status?.iso_31000_compliance 
              ? `linear-gradient(135deg, ${ISO_STATUS_COLORS.effective} 0%, ${ISO_STATUS_COLORS.compliant} 100%)`
              : `linear-gradient(135deg, ${ISO_STATUS_COLORS.nonConformance} 0%, ${ISO_STATUS_COLORS.atRisk} 100%)`,
            color: 'white'
          }}>
            <CardContent sx={{ p: 2 }}>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                    ISO 31000:2018 Compliance
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                    {dashboardData.compliance_status?.compliance_score?.toFixed(0) || 0}%
                  </Typography>
                  <Stack direction="row" alignItems="center" spacing={0.5}>
                    {dashboardData.compliance_status?.iso_31000_compliance ? (
                      <CheckCircle sx={{ fontSize: 16 }} />
                    ) : (
                      <Warning sx={{ fontSize: 16 }} />
                    )}
                    <Typography variant="caption">
                      {dashboardData.compliance_status?.iso_31000_compliance ? 'Compliant' : 'Non-Compliant'}
                    </Typography>
                  </Stack>
                </Box>
                <Shield sx={{ fontSize: 40, opacity: 0.7 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics Card */}
        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: 140 }}>
            <CardContent sx={{ p: 2 }}>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Overall Performance
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                    {dashboardData.performance_metrics?.overall_performance?.toFixed(0) || 0}%
                  </Typography>
                  <Stack direction="row" alignItems="center" spacing={0.5}>
                    <TrendingUp sx={{ 
                      fontSize: 16, 
                      color: dashboardData.performance_metrics?.overall_performance >= 75 
                        ? ISO_STATUS_COLORS.effective 
                        : ISO_STATUS_COLORS.atRisk 
                    }} />
                    <Typography variant="caption" color="text.secondary">
                      Treatment Efficiency: {dashboardData.performance_metrics?.treatment_efficiency?.toFixed(0) || 0}%
                    </Typography>
                  </Stack>
                </Box>
                <Analytics sx={{ fontSize: 40, color: PROFESSIONAL_COLORS.accent.main, opacity: 0.7 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* FSMS Integration Status */}
        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: 140 }}>
            <CardContent sx={{ p: 2 }}>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    FSMS Integration
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                    {dashboardData.compliance_status?.compliance_checks?.fsms_integration ? 'Active' : 'Inactive'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    ISO 22000:2018 Risk-based Thinking
                  </Typography>
                </Box>
                <AccountBalance sx={{ 
                  fontSize: 40, 
                  color: dashboardData.compliance_status?.compliance_checks?.fsms_integration 
                    ? ISO_STATUS_COLORS.effective 
                    : ISO_STATUS_COLORS.atRisk,
                  opacity: 0.7 
                }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Compliance Recommendations Alert */}
        {dashboardData.compliance_status?.recommendations?.length > 0 && (
          <Grid item xs={12}>
            <Alert 
              severity="warning" 
              sx={{ mb: 2 }}
              action={
                <Button size="small" onClick={() => setComplianceDialogOpen(true)}>
                  View Details
                </Button>
              }
            >
              <Typography variant="body2">
                {dashboardData.compliance_status.recommendations.length} compliance recommendations available.
                Current compliance score: {dashboardData.compliance_status.compliance_score?.toFixed(1)}%
              </Typography>
            </Alert>
          </Grid>
        )}

        {/* Enhanced Risk Trends Chart */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: 400 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Management Trends (ISO 31000:2018)
              </Typography>
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={dashboardData.enhanced_trends || dashboardData.risk_trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="new_risks" 
                    stroke={ISO_STATUS_COLORS.nonConformance} 
                    name="New Risks"
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="resolved_risks" 
                    stroke={ISO_STATUS_COLORS.effective} 
                    name="Resolved Risks"
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="new_opportunities" 
                    stroke={PROFESSIONAL_COLORS.accent.main} 
                    name="New Opportunities"
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="avg_risk_score" 
                    stroke={PROFESSIONAL_COLORS.secondary.main} 
                    name="Avg Risk Score"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Performance Metrics */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: 400 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Resolution Rate
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={dashboardData.performance_metrics?.resolution_rate || 0} 
                    sx={{ height: 8, borderRadius: 4, mb: 1 }}
                  />
                  <Typography variant="caption">
                    {dashboardData.performance_metrics?.resolution_rate?.toFixed(1) || 0}%
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Review Compliance
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={dashboardData.performance_metrics?.review_compliance || 0} 
                    sx={{ height: 8, borderRadius: 4, mb: 1 }}
                  />
                  <Typography variant="caption">
                    {dashboardData.performance_metrics?.review_compliance?.toFixed(1) || 0}%
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Treatment Efficiency
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={dashboardData.performance_metrics?.treatment_efficiency || 0} 
                    sx={{ height: 8, borderRadius: 4, mb: 1 }}
                  />
                  <Typography variant="caption">
                    {dashboardData.performance_metrics?.treatment_efficiency?.toFixed(1) || 0}%
                  </Typography>
                </Box>

                <Divider />
                
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Total Risks:
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {dashboardData.performance_metrics?.total_risks || 0}
                  </Typography>
                </Stack>
                
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Overdue Reviews:
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" color={
                    (dashboardData.performance_metrics?.overdue_reviews || 0) > 0 
                      ? 'error.main' 
                      : 'success.main'
                  }>
                    {dashboardData.performance_metrics?.overdue_reviews || 0}
                  </Typography>
                </Stack>
                
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Pending Treatments:
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {dashboardData.performance_metrics?.pending_treatments || 0}
                  </Typography>
                </Stack>
              </Stack>
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