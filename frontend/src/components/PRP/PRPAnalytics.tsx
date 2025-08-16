import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  Alert,
  LinearProgress,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Assessment,
  Analytics,
  Dashboard,
  Report,
  Search,
  FilterList,
  Download,
  Refresh,
  Visibility,
  Warning,
  CheckCircle,
  Error,
  Info,
  ExpandMore,
  Schedule,
  Person,
  AttachMoney,
  Timeline,
  Speed,
  TrendingFlat,
  AutoGraph,
  Insights,
  Psychology,
  Lightbulb,
  BarChart,
  PieChart,
  ShowChart,
  TableChart,
  GetApp,
  Print,
  Share,
  Settings,
  Optimization,
  AutoFixHigh,
  TrendingUpOutlined,
  TrendingDownOutlined,
  TrendingFlatOutlined,
} from '@mui/icons-material';
import { prpAPI } from '../../services/api';

interface ProgramAnalytics {
  program_info: {
    id: number;
    name: string;
    category: string;
    status: string;
  };
  period: {
    start_date: string;
    end_date: string;
    period_type: string;
  };
  checklist_analytics: {
    total_checklists: number;
    completed_checklists: number;
    failed_checklists: number;
    overdue_checklists: number;
    completion_rate: number;
    average_compliance: number;
    on_time_completion_rate: number;
  };
  risk_analytics: {
    total_assessments: number;
    high_risk_count: number;
    escalated_count: number;
    average_risk_score: number;
  };
  capa_analytics: {
    total_corrective_actions: number;
    completed_actions: number;
    overdue_actions: number;
    average_completion_time: number;
  };
}

interface PerformanceTrends {
  trends: Array<{
    period: string;
    completion_rate: number;
    compliance_rate: number;
    risk_score: number;
    efficiency_score: number;
  }>;
  direction: 'improving' | 'declining' | 'stable';
  insights: string[];
  recommendations: string[];
}

interface PerformanceMetrics {
  overall_compliance: number;
  average_completion_time: number;
  risk_exposure_score: number;
  efficiency_rating: number;
  quality_score: number;
  cost_effectiveness: number;
  benchmark_status: 'excellent' | 'good' | 'average' | 'below_average' | 'poor';
  benchmark_comparison: {
    industry_average: number;
    best_practice: number;
    current_performance: number;
  };
}

interface PredictiveAnalytics {
  compliance_forecast: {
    next_month: number;
    next_quarter: number;
    next_year: number;
    confidence_level: number;
  };
  risk_predictions: {
    high_risk_probability: number;
    potential_failures: string[];
    risk_trend: 'increasing' | 'decreasing' | 'stable';
  };
  optimization_opportunities: {
    schedule_optimization: number;
    resource_optimization: number;
    cost_savings: number;
    efficiency_gains: number;
  };
}

interface AnalyticalInsights {
  key_findings: string[];
  performance_gaps: string[];
  optimization_opportunities: string[];
  risk_patterns: string[];
  compliance_issues: string[];
  recommendations: string[];
  action_items: string[];
}

const PRPAnalytics: React.FC<{ programId?: number }> = ({ programId }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Data states
  const [programAnalytics, setProgramAnalytics] = useState<ProgramAnalytics | null>(null);
  const [performanceTrends, setPerformanceTrends] = useState<PerformanceTrends | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [predictiveAnalytics, setPredictiveAnalytics] = useState<PredictiveAnalytics | null>(null);
  const [analyticalInsights, setAnalyticalInsights] = useState<AnalyticalInsights | null>(null);
  
  // Filter states
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  // Dialog states
  const [openReportDialog, setOpenReportDialog] = useState(false);
  const [openOptimizationDialog, setOpenOptimizationDialog] = useState(false);
  const [reportType, setReportType] = useState('comprehensive');

  useEffect(() => {
    fetchAnalyticsData();
  }, [programId, selectedPeriod, selectedCategory]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      
      if (programId) {
        // Fetch program-specific analytics
        const [analyticsResponse, trendsResponse] = await Promise.all([
          prpAPI.getProgramAnalytics(programId, selectedPeriod),
          prpAPI.getProgramPerformanceTrends(programId, selectedPeriod),
        ]);

        if (analyticsResponse.success) {
          setProgramAnalytics(analyticsResponse.data);
        }

        if (trendsResponse.success) {
          setPerformanceTrends(trendsResponse.data);
        }
      } else {
        // Fetch global analytics
        const [metricsResponse, predictiveResponse, insightsResponse] = await Promise.all([
          prpAPI.getPerformanceMetrics(),
          prpAPI.getPredictiveAnalytics(),
          prpAPI.generateInsights(),
        ]);

        if (metricsResponse.success) {
          setPerformanceMetrics(metricsResponse.data);
        }

        if (predictiveResponse.success) {
          setPredictiveAnalytics(predictiveResponse.data);
        }

        if (insightsResponse.success) {
          setAnalyticalInsights(insightsResponse.data);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    try {
      const response = await prpAPI.generateComprehensiveReport({
        report_type: reportType,
        period: selectedPeriod,
        category: selectedCategory,
        include_charts: true,
        include_recommendations: true,
      });

      if (response.success) {
        setSuccess('Report generated successfully');
        setOpenReportDialog(false);
        // Handle report download or display
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate report');
    }
  };

  const handleOptimizePerformance = async () => {
    try {
      const response = await prpAPI.optimizePerformance({
        optimization_type: 'comprehensive',
        target_areas: ['schedule', 'resources', 'costs'],
        constraints: {
          budget_limit: 10000,
          timeline_constraint: '30d',
        },
      });

      if (response.success) {
        setSuccess('Performance optimization completed successfully');
        setOpenOptimizationDialog(false);
        fetchAnalyticsData();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to optimize performance');
    }
  };

  const getTrendDirectionIcon = (direction: string) => {
    switch (direction) {
      case 'improving':
        return <TrendingUp color="success" />;
      case 'declining':
        return <TrendingDown color="error" />;
      case 'stable':
        return <TrendingFlat color="warning" />;
      default:
        return <TrendingFlat />;
    }
  };

  const getBenchmarkColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'success';
      case 'good': return 'success';
      case 'average': return 'warning';
      case 'below_average': return 'warning';
      case 'poor': return 'error';
      default: return 'default';
    }
  };

  const renderProgramAnalytics = () => {
    if (!programAnalytics) return null;

    return (
      <Box>
        <Typography variant="h6" gutterBottom>Program Analytics</Typography>
        
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Checklist Analytics</Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Assessment />
                    </ListItemIcon>
                    <ListItemText
                      primary="Total Checklists"
                      secondary={programAnalytics.checklist_analytics.total_checklists}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <CheckCircle color="success" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Completed Checklists"
                      secondary={`${programAnalytics.checklist_analytics.completed_checklists} (${programAnalytics.checklist_analytics.completion_rate.toFixed(1)}%)`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Error color="error" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Failed Checklists"
                      secondary={programAnalytics.checklist_analytics.failed_checklists}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Warning color="warning" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Overdue Checklists"
                      secondary={programAnalytics.checklist_analytics.overdue_checklists}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Risk Analytics</Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Assessment />
                    </ListItemIcon>
                    <ListItemText
                      primary="Total Risk Assessments"
                      secondary={programAnalytics.risk_analytics.total_assessments}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Warning color="error" />
                    </ListItemIcon>
                    <ListItemText
                      primary="High Risk Count"
                      secondary={programAnalytics.risk_analytics.high_risk_count}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <TrendingUp color="warning" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Escalated Risks"
                      secondary={programAnalytics.risk_analytics.escalated_count}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Analytics />
                    </ListItemIcon>
                    <ListItemText
                      primary="Average Risk Score"
                      secondary={programAnalytics.risk_analytics.average_risk_score.toFixed(1)}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>CAPA Analytics</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="primary">
                        {programAnalytics.capa_analytics.total_corrective_actions}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Total Actions
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="success">
                        {programAnalytics.capa_analytics.completed_actions}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Completed
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="error">
                        {programAnalytics.capa_analytics.overdue_actions}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Overdue
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="info">
                        {programAnalytics.capa_analytics.average_completion_time.toFixed(1)}d
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Avg Completion Time
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

  const renderPerformanceTrends = () => {
    if (!performanceTrends) return null;

    return (
      <Box>
        <Typography variant="h6" gutterBottom>Performance Trends</Typography>
        
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Typography variant="h6">Trend Direction</Typography>
                  {getTrendDirectionIcon(performanceTrends.direction)}
                </Box>
                <Chip
                  label={performanceTrends.direction.toUpperCase()}
                  color={performanceTrends.direction === 'improving' ? 'success' : performanceTrends.direction === 'declining' ? 'error' : 'warning'}
                  variant="outlined"
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Key Insights</Typography>
                <List dense>
                  {performanceTrends.insights.slice(0, 3).map((insight, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Lightbulb color="primary" />
                      </ListItemIcon>
                      <ListItemText primary={insight} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Trend Data</Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Period</TableCell>
                        <TableCell>Completion Rate (%)</TableCell>
                        <TableCell>Compliance Rate (%)</TableCell>
                        <TableCell>Risk Score</TableCell>
                        <TableCell>Efficiency Score</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {performanceTrends.trends.map((trend, index) => (
                        <TableRow key={index}>
                          <TableCell>{trend.period}</TableCell>
                          <TableCell>{trend.completion_rate.toFixed(1)}</TableCell>
                          <TableCell>{trend.compliance_rate.toFixed(1)}</TableCell>
                          <TableCell>{trend.risk_score.toFixed(1)}</TableCell>
                          <TableCell>{trend.efficiency_score.toFixed(1)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderPerformanceMetrics = () => {
    if (!performanceMetrics) return null;

    return (
      <Box>
        <Typography variant="h6" gutterBottom>Performance Metrics</Typography>
        
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {performanceMetrics.overall_compliance.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Overall Compliance
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box textAlign="center">
                  <Typography variant="h4" color="info">
                    {performanceMetrics.average_completion_time.toFixed(1)}d
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Avg Completion Time
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning">
                    {performanceMetrics.risk_exposure_score.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Risk Exposure Score
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box textAlign="center">
                  <Typography variant="h4" color="success">
                    {performanceMetrics.efficiency_rating.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Efficiency Rating
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Benchmark Comparison</Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <TrendingUp color="success" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Best Practice"
                      secondary={`${performanceMetrics.benchmark_comparison.best_practice.toFixed(1)}%`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <TrendingFlat color="warning" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Industry Average"
                      secondary={`${performanceMetrics.benchmark_comparison.industry_average.toFixed(1)}%`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Assessment />
                    </ListItemIcon>
                    <ListItemText
                      primary="Current Performance"
                      secondary={`${performanceMetrics.benchmark_comparison.current_performance.toFixed(1)}%`}
                    />
                  </ListItem>
                </List>
                <Box mt={2}>
                  <Chip
                    label={`Benchmark Status: ${performanceMetrics.benchmark_status.replace('_', ' ').toUpperCase()}`}
                    color={getBenchmarkColor(performanceMetrics.benchmark_status) as any}
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Quality & Cost Metrics</Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Assessment />
                    </ListItemIcon>
                    <ListItemText
                      primary="Quality Score"
                      secondary={`${performanceMetrics.quality_score.toFixed(1)}/10`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <AttachMoney />
                    </ListItemIcon>
                    <ListItemText
                      primary="Cost Effectiveness"
                      secondary={`${performanceMetrics.cost_effectiveness.toFixed(1)}%`}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderPredictiveAnalytics = () => {
    if (!predictiveAnalytics) return null;

    return (
      <Box>
        <Typography variant="h6" gutterBottom>Predictive Analytics</Typography>
        
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Compliance Forecast</Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Next Month"
                      secondary={`${predictiveAnalytics.compliance_forecast.next_month.toFixed(1)}%`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Next Quarter"
                      secondary={`${predictiveAnalytics.compliance_forecast.next_quarter.toFixed(1)}%`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Next Year"
                      secondary={`${predictiveAnalytics.compliance_forecast.next_year.toFixed(1)}%`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Confidence Level"
                      secondary={`${predictiveAnalytics.compliance_forecast.confidence_level.toFixed(1)}%`}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Risk Predictions</Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Warning color="error" />
                    </ListItemIcon>
                    <ListItemText
                      primary="High Risk Probability"
                      secondary={`${predictiveAnalytics.risk_predictions.high_risk_probability.toFixed(1)}%`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      {getTrendDirectionIcon(predictiveAnalytics.risk_predictions.risk_trend)}
                    </ListItemIcon>
                    <ListItemText
                      primary="Risk Trend"
                      secondary={predictiveAnalytics.risk_predictions.risk_trend.toUpperCase()}
                    />
                  </ListItem>
                </List>
                <Typography variant="subtitle2" gutterBottom>
                  Potential Failures:
                </Typography>
                <List dense>
                  {predictiveAnalytics.risk_predictions.potential_failures.slice(0, 3).map((failure, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Error color="error" />
                      </ListItemIcon>
                      <ListItemText primary={failure} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Optimization Opportunities</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="primary">
                        {predictiveAnalytics.optimization_opportunities.schedule_optimization.toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Schedule Optimization
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="success">
                        {predictiveAnalytics.optimization_opportunities.resource_optimization.toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Resource Optimization
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="info">
                        ${predictiveAnalytics.optimization_opportunities.cost_savings.toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Potential Cost Savings
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="warning">
                        {predictiveAnalytics.optimization_opportunities.efficiency_gains.toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Efficiency Gains
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

  const renderAnalyticalInsights = () => {
    if (!analyticalInsights) return null;

    return (
      <Box>
        <Typography variant="h6" gutterBottom>Analytical Insights</Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Key Findings</Typography>
                <List dense>
                  {analyticalInsights.key_findings.slice(0, 5).map((finding, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Insights color="primary" />
                      </ListItemIcon>
                      <ListItemText primary={finding} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Performance Gaps</Typography>
                <List dense>
                  {analyticalInsights.performance_gaps.slice(0, 5).map((gap, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Warning color="warning" />
                      </ListItemIcon>
                      <ListItemText primary={gap} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Optimization Opportunities</Typography>
                <List dense>
                  {analyticalInsights.optimization_opportunities.slice(0, 5).map((opportunity, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <AutoFixHigh color="success" />
                      </ListItemIcon>
                      <ListItemText primary={opportunity} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Risk Patterns</Typography>
                <List dense>
                  {analyticalInsights.risk_patterns.slice(0, 5).map((pattern, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Psychology color="error" />
                      </ListItemIcon>
                      <ListItemText primary={pattern} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3} mt={2}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Recommendations & Action Items</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>Recommendations</Typography>
                    <List dense>
                      {analyticalInsights.recommendations.slice(0, 5).map((recommendation, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <Lightbulb color="primary" />
                          </ListItemIcon>
                          <ListItemText primary={recommendation} />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>Action Items</Typography>
                    <List dense>
                      {analyticalInsights.action_items.slice(0, 5).map((action, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <CheckCircle color="success" />
                          </ListItemIcon>
                          <ListItemText primary={action} />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderReportDialog = () => (
    <Dialog open={openReportDialog} onClose={() => setOpenReportDialog(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Generate Report</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Report Type</InputLabel>
              <Select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
              >
                <MenuItem value="comprehensive">Comprehensive Report</MenuItem>
                <MenuItem value="compliance_summary">Compliance Summary</MenuItem>
                <MenuItem value="risk_exposure">Risk Exposure Report</MenuItem>
                <MenuItem value="performance_metrics">Performance Metrics</MenuItem>
                <MenuItem value="trend_analysis">Trend Analysis</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Period</InputLabel>
              <Select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
              >
                <MenuItem value="7d">Last 7 Days</MenuItem>
                <MenuItem value="30d">Last 30 Days</MenuItem>
                <MenuItem value="90d">Last 90 Days</MenuItem>
                <MenuItem value="1y">Last Year</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setOpenReportDialog(false)}>Cancel</Button>
        <Button onClick={handleGenerateReport} variant="contained">
          Generate Report
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderOptimizationDialog = () => (
    <Dialog open={openOptimizationDialog} onClose={() => setOpenOptimizationDialog(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Performance Optimization</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          This will analyze your current performance and provide optimization recommendations.
        </Typography>
        <Typography variant="body2">
          The optimization process will consider:
        </Typography>
        <List dense>
          <ListItem>
            <ListItemIcon>
              <Schedule />
            </ListItemIcon>
            <ListItemText primary="Schedule optimization" />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <Person />
            </ListItemIcon>
            <ListItemText primary="Resource allocation" />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <AttachMoney />
            </ListItemIcon>
            <ListItemText primary="Cost optimization" />
          </ListItem>
        </List>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setOpenOptimizationDialog(false)}>Cancel</Button>
        <Button onClick={handleOptimizePerformance} variant="contained">
          Run Optimization
        </Button>
      </DialogActions>
    </Dialog>
  );

  if (loading) {
    return (
      <Box>
        <LinearProgress />
        <Typography>Loading analytics data...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">PRP Analytics & Insights</Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Report />}
            onClick={() => setOpenReportDialog(true)}
          >
            Generate Report
          </Button>
          <Button
            variant="outlined"
            startIcon={<Optimization />}
            onClick={() => setOpenOptimizationDialog(true)}
          >
            Optimize Performance
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchAnalyticsData}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          {programId ? (
            <>
              <Tab label="Program Analytics" icon={<Assessment />} />
              <Tab label="Performance Trends" icon={<TrendingUp />} />
            </>
          ) : (
            <>
              <Tab label="Performance Metrics" icon={<Dashboard />} />
              <Tab label="Predictive Analytics" icon={<AutoGraph />} />
              <Tab label="Analytical Insights" icon={<Insights />} />
            </>
          )}
        </Tabs>
      </Box>

      {programId ? (
        <>
          {activeTab === 0 && renderProgramAnalytics()}
          {activeTab === 1 && renderPerformanceTrends()}
        </>
      ) : (
        <>
          {activeTab === 0 && renderPerformanceMetrics()}
          {activeTab === 1 && renderPredictiveAnalytics()}
          {activeTab === 2 && renderAnalyticalInsights()}
        </>
      )}

      {renderReportDialog()}
      {renderOptimizationDialog()}
    </Box>
  );
};

export default PRPAnalytics;
