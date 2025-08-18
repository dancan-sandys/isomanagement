import React, { useEffect, useState } from 'react';
import {
  Box, Card, CardContent, Grid, Typography, Paper, Tabs, Tab,
  LinearProgress, Alert, Stack, Chip, Avatar, List, ListItem,
  ListItemText, ListItemIcon, Divider, Button, FormControl,
  InputLabel, Select, MenuItem, IconButton, Tooltip
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon, Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon, Warning as WarningIcon,
  Assignment as AssignmentIcon, Schedule as ScheduleIcon,
  Analytics as AnalyticsIcon, Download as DownloadIcon,
  Refresh as RefreshIcon, DateRange as DateRangeIcon
} from '@mui/icons-material';
import managementReviewAPI from '../services/managementReviewAPI';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ManagementReviewAnalytics: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('12months');
  
  // Analytics data state
  const [executiveSummary, setExecutiveSummary] = useState<any>({});
  const [complianceReport, setComplianceReport] = useState<any>({});
  const [effectivenessAnalysis, setEffectivenessAnalysis] = useState<any>({});
  const [actionTracking, setActionTracking] = useState<any>({});
  const [trendAnalysis, setTrendAnalysis] = useState<any>({});

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      // For now, we'll create mock data since the reporting endpoints aren't implemented yet
      // In the real implementation, these would call the actual reporting APIs
      
      const mockExecutiveSummary = {
        period: { start_date: '2024-01-01', end_date: '2024-12-31', days: 365 },
        review_statistics: {
          total_reviews: 12,
          completed_reviews: 10,
          in_progress_reviews: 1,
          planned_reviews: 1,
          completion_rate: 83.3
        },
        effectiveness_metrics: {
          average_effectiveness_score: 7.8,
          effectiveness_trend: 'improving',
          reviews_with_scores: 10
        },
        action_metrics: {
          total_actions: 45,
          completed_actions: 38,
          overdue_actions: 3,
          action_completion_rate: 84.4
        },
        compliance_metrics: {
          average_compliance_score: 92.5,
          compliant_reviews: 9,
          non_compliant_reviews: 1
        },
        key_insights: [
          'High review completion rate indicates strong management commitment',
          'Effectiveness scores demonstrate valuable review outcomes',
          'Action completion rate shows good follow-through'
        ],
        recommendations: [
          'Address 3 overdue actions immediately',
          'Continue monitoring performance indicators monthly'
        ]
      };

      const mockComplianceReport = {
        overall_compliance: {
          average_compliance_score: 92.5,
          fully_compliant_reviews: 8,
          partially_compliant_reviews: 2,
          non_compliant_reviews: 0
        },
        input_compliance_analysis: {
          input_coverage_rates: {
            audit_results: 95,
            nc_capa_status: 90,
            supplier_performance: 85,
            haccp_performance: 100,
            prp_performance: 95,
            risk_assessment: 80,
            previous_actions: 75
          }
        },
        output_compliance_analysis: {
          output_coverage_rates: {
            improvement_action: 100,
            resource_allocation: 85,
            system_change: 70
          }
        }
      };

      const mockEffectivenessAnalysis = {
        effectiveness_overview: {
          total_reviews_analyzed: 10,
          average_effectiveness_score: 7.8,
          highest_score: 9.2,
          lowest_score: 6.1,
          excellent_reviews: 3,
          good_reviews: 5,
          needs_improvement_reviews: 2
        }
      };

      const mockActionTracking = {
        action_overview: {
          total_actions: 45,
          completed_actions: 38,
          in_progress_actions: 4,
          overdue_actions: 3,
          completion_rate: 84.4,
          average_completion_days: 18.5
        },
        priority_distribution: {
          low: 15,
          medium: 20,
          high: 8,
          critical: 2
        }
      };

      setExecutiveSummary(mockExecutiveSummary);
      setComplianceReport(mockComplianceReport);
      setEffectivenessAnalysis(mockEffectivenessAnalysis);
      setActionTracking(mockActionTracking);
      
    } catch (e: any) {
      setError(e?.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  const getComplianceColor = (score: number) => {
    if (score >= 95) return 'success.main';
    if (score >= 80) return 'warning.main';
    return 'error.main';
  };

  const getEffectivenessColor = (score: number) => {
    if (score >= 8) return 'success.main';
    if (score >= 6) return 'warning.main';
    return 'error.main';
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>Management Review Analytics</Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Comprehensive analytics and ISO 22000:2018 compliance reporting
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              label="Time Range"
            >
              <MenuItem value="3months">Last 3 Months</MenuItem>
              <MenuItem value="6months">Last 6 Months</MenuItem>
              <MenuItem value="12months">Last 12 Months</MenuItem>
              <MenuItem value="24months">Last 24 Months</MenuItem>
            </Select>
          </FormControl>
          <IconButton onClick={loadAnalytics} disabled={loading}>
            <RefreshIcon />
          </IconButton>
          <Button variant="outlined" startIcon={<DownloadIcon />}>
            Export Report
          </Button>
        </Stack>
      </Stack>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Executive Summary" />
          <Tab label="ISO Compliance" />
          <Tab label="Effectiveness Analysis" />
          <Tab label="Action Tracking" />
          <Tab label="Trend Analysis" />
        </Tabs>
      </Paper>

      {/* Executive Summary Tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {/* Key Metrics Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    <AssessmentIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4">{executiveSummary.review_statistics?.total_reviews || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">Total Reviews</Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <Avatar sx={{ bgcolor: 'success.main' }}>
                    <CheckCircleIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4">{executiveSummary.review_statistics?.completion_rate || 0}%</Typography>
                    <Typography variant="body2" color="text.secondary">Completion Rate</Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <Avatar sx={{ bgcolor: 'info.main' }}>
                    <TrendingUpIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4">{executiveSummary.effectiveness_metrics?.average_effectiveness_score || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">Avg Effectiveness</Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <Avatar sx={{ bgcolor: executiveSummary.action_metrics?.overdue_actions > 0 ? 'error.main' : 'success.main' }}>
                    <AssignmentIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4">{executiveSummary.action_metrics?.overdue_actions || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">Overdue Actions</Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          {/* Key Insights */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Key Insights</Typography>
                <List>
                  {(executiveSummary.key_insights || []).map((insight: string, index: number) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CheckCircleIcon color="success" />
                      </ListItemIcon>
                      <ListItemText primary={insight} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Recommendations */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Recommendations</Typography>
                <List>
                  {(executiveSummary.recommendations || []).map((rec: string, index: number) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <WarningIcon color="warning" />
                      </ListItemIcon>
                      <ListItemText primary={rec} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* ISO Compliance Tab */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Overall Compliance</Typography>
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Typography 
                    variant="h2" 
                    color={getComplianceColor(complianceReport.overall_compliance?.average_compliance_score || 0)}
                  >
                    {complianceReport.overall_compliance?.average_compliance_score || 0}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    ISO 22000:2018 Compliance
                  </Typography>
                </Box>
                <Stack spacing={1}>
                  <Stack direction="row" justifyContent="space-between">
                    <Typography variant="body2">Fully Compliant</Typography>
                    <Chip 
                      label={complianceReport.overall_compliance?.fully_compliant_reviews || 0} 
                      color="success" 
                      size="small"
                    />
                  </Stack>
                  <Stack direction="row" justifyContent="space-between">
                    <Typography variant="body2">Partially Compliant</Typography>
                    <Chip 
                      label={complianceReport.overall_compliance?.partially_compliant_reviews || 0} 
                      color="warning" 
                      size="small"
                    />
                  </Stack>
                  <Stack direction="row" justifyContent="space-between">
                    <Typography variant="body2">Non-Compliant</Typography>
                    <Chip 
                      label={complianceReport.overall_compliance?.non_compliant_reviews || 0} 
                      color="error" 
                      size="small"
                    />
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Input Compliance</Typography>
                <Stack spacing={2}>
                  {Object.entries(complianceReport.input_compliance_analysis?.input_coverage_rates || {}).map(([input, rate]) => (
                    <Box key={input}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2">{input.replace('_', ' ')}</Typography>
                        <Typography variant="body2" fontWeight="bold">{String(rate)}%</Typography>
                      </Stack>
                      <LinearProgress 
                        variant="determinate" 
                        value={rate as number} 
                        sx={{ mt: 0.5 }}
                        color={rate >= 90 ? 'success' : rate >= 75 ? 'warning' : 'error'}
                      />
                    </Box>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Output Compliance</Typography>
                <Stack spacing={2}>
                  {Object.entries(complianceReport.output_compliance_analysis?.output_coverage_rates || {}).map(([output, rate]) => (
                    <Box key={output}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2">{output.replace('_', ' ')}</Typography>
                        <Typography variant="body2" fontWeight="bold">{String(rate)}%</Typography>
                      </Stack>
                      <LinearProgress 
                        variant="determinate" 
                        value={rate as number} 
                        sx={{ mt: 0.5 }}
                        color={rate >= 90 ? 'success' : rate >= 75 ? 'warning' : 'error'}
                      />
                    </Box>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Effectiveness Analysis Tab */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Effectiveness Overview</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography 
                        variant="h3" 
                        color={getEffectivenessColor(effectivenessAnalysis.effectiveness_overview?.average_effectiveness_score || 0)}
                      >
                        {effectivenessAnalysis.effectiveness_overview?.average_effectiveness_score || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Average Score</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Stack spacing={1}>
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2">Excellent (8-10)</Typography>
                        <Chip 
                          label={effectivenessAnalysis.effectiveness_overview?.excellent_reviews || 0} 
                          color="success" 
                          size="small"
                        />
                      </Stack>
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2">Good (6-8)</Typography>
                        <Chip 
                          label={effectivenessAnalysis.effectiveness_overview?.good_reviews || 0} 
                          color="info" 
                          size="small"
                        />
                      </Stack>
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2">Needs Improvement (&lt;6)</Typography>
                        <Chip 
                          label={effectivenessAnalysis.effectiveness_overview?.needs_improvement_reviews || 0} 
                          color="warning" 
                          size="small"
                        />
                      </Stack>
                    </Stack>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Effectiveness Distribution</Typography>
                <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Chart visualization would be implemented here
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Action Tracking Tab */}
      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Action Performance Metrics</Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h3" color="primary.main">
                        {actionTracking.action_overview?.total_actions || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Total Actions</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h3" color="success.main">
                        {actionTracking.action_overview?.completion_rate || 0}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Completion Rate</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h3" color="info.main">
                        {actionTracking.action_overview?.average_completion_days || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Avg Days to Complete</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h3" color="error.main">
                        {actionTracking.action_overview?.overdue_actions || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Overdue Actions</Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Priority Distribution</Typography>
                <Stack spacing={2}>
                  {Object.entries(actionTracking.priority_distribution || {}).map(([priority, count]) => (
                    <Stack key={priority} direction="row" justifyContent="space-between" alignItems="center">
                      <Chip 
                        label={priority.charAt(0).toUpperCase() + priority.slice(1)} 
                        size="small"
                        color={
                          priority === 'critical' ? 'error' :
                          priority === 'high' ? 'warning' :
                          priority === 'medium' ? 'info' : 'default'
                        }
                      />
                      <Typography variant="h6">{String(count)}</Typography>
                    </Stack>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Trend Analysis Tab */}
      <TabPanel value={tabValue} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Performance Trends</Typography>
                <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography variant="body1" color="text.secondary">
                    Trend charts will be implemented with charting library (Chart.js or Recharts)
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Review Frequency Analysis</Typography>
                <Typography variant="body2" color="text.secondary">
                  Analysis of review scheduling patterns and frequency compliance
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Improvement Opportunities</Typography>
                <Typography variant="body2" color="text.secondary">
                  Identified opportunities for enhancing review effectiveness
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
};

export default ManagementReviewAnalytics;