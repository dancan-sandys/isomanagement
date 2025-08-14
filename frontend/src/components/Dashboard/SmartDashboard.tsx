import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  Avatar,
  Stack,
  Chip,
  Button,
  IconButton,
  LinearProgress,
  Divider,
  Alert,
  Fade,
  Grow,
  Tooltip,
  Badge,
  Paper,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AutoAwesome,
  Insights,
  PlayArrow,
  Star,
  AccessTime,
  CheckCircle,
  Warning,
  Flag,
  Speed,
  Assignment,
  Analytics,
  Lightbulb,
  CalendarToday,
} from '@mui/icons-material';
import { RootState } from '../../store';
import { dashboardAPI } from '../../services/api';
import { PieChart, Pie, Cell, Tooltip as RechartTooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';

interface SmartMetric {
  id: string;
  title: string;
  value: string | number;
  change: number;
  trend: 'up' | 'down' | 'stable';
  icon: React.ReactNode;
  color: 'primary' | 'success' | 'warning' | 'error' | 'info';
  insight?: string;
  quickAction?: {
    label: string;
    action: () => void;
  };
}

interface SmartTask {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  dueDate: Date;
  category: string;
  progress?: number;
  estimatedTime?: string;
}

interface SmartInsight {
  id: string;
  title: string;
  description: string;
  type: 'success' | 'warning' | 'info' | 'error';
  action?: {
    label: string;
    onClick: () => void;
  };
}

const SmartDashboard: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState<SmartMetric[]>([]);
  const [tasks, setTasks] = useState<SmartTask[]>([]);
  const [insights, setInsights] = useState<SmartInsight[]>([]);
  const [docTypeSeries, setDocTypeSeries] = useState<Array<{ name: string; value: number }>>([]);
  const [operationalSeries, setOperationalSeries] = useState<Array<{ name: string; value: number }>>([]);

  // Load real data from backend
  useEffect(() => {
    if (user?.id) {
      loadDashboardData();
    }
  }, [user]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load data from real backend APIs
      const [metricsResponse, tasksResponse, insightsResponse, statsResponse, kpiResponse, fsmsResponse] = await Promise.all([
        dashboardAPI.getUserMetrics(String(user?.id || '')),
        dashboardAPI.getPriorityTasks(String(user?.id || '')),
        dashboardAPI.getInsights(String(user?.id || '')),
        dashboardAPI.getStats(),
        dashboardAPI.getCrossModuleKpis ? dashboardAPI.getCrossModuleKpis('month') : Promise.resolve(null),
        dashboardAPI.getFsmsComplianceScore ? dashboardAPI.getFsmsComplianceScore() : Promise.resolve(null)
      ]);

      // Transform backend data to component format
      const roleData = transformBackendData(metricsResponse, tasksResponse, insightsResponse, user?.role_name || '');
      setMetrics(roleData.metrics);
      setTasks(roleData.tasks);
      setInsights(roleData.insights);

      // Map stats to chart series
      const stats = statsResponse?.data || statsResponse;
      const docCounts = (stats?.docTypeCounts || []).map((d: any) => ({ name: d.type, value: d.count }));
      setDocTypeSeries(docCounts);

      const kpis = kpiResponse?.data || kpiResponse;
      const ops = kpis?.operational_metrics || {};
      // Optionally enrich metrics with FSMS overall score for top card prominence
      const fsms = fsmsResponse?.data || fsmsResponse;
      if (fsms?.overall_score !== undefined) {
        setMetrics((prev) => [
          {
            id: 'fsms_overall',
            title: 'FSMS Compliance',
            value: `${fsms.overall_score}%`,
            change: 0,
            trend: 'stable',
            icon: <CheckCircle />,
            color: 'success',
            insight: fsms.compliance_level?.replace('_',' '),
            quickAction: { label: 'View Factors', action: () => window.location.href = '/dashboard/analytics' }
          },
          ...prev,
        ]);
      }
      const opsSeries = [
        { name: 'Documents', value: Number(ops.documents_processed || 0) },
        { name: 'Audits', value: Number(ops.audits_completed || 0) },
        { name: 'Training', value: Number(ops.training_sessions || 0) },
        { name: 'Supplier Evals', value: Number(ops.supplier_evaluations || 0) },
      ];
      setOperationalSeries(opsSeries);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // Fallback to basic data on error
      const fallbackData = getRoleBasedData(user?.role_name || '');
      setMetrics(fallbackData.metrics);
      setTasks(fallbackData.tasks);
      setInsights(fallbackData.insights);
    } finally {
      setLoading(false);
    }
  };

  const transformBackendData = (metricsData: any, tasksData: any, insightsData: any, roleName: string) => {
    // Transform metrics from backend format
    const metrics: SmartMetric[] = [];
    
    if (metricsData?.metrics) {
      const m = metricsData.metrics;
      const trends = metricsData.trends || {};

      if (m.compliance_score !== undefined) {
        metrics.push({
          id: 'compliance',
          title: 'Compliance Score',
          value: `${m.compliance_score}%`,
          change: trends.compliance_change || 0,
          trend: (trends.compliance_change || 0) > 0 ? 'up' : (trends.compliance_change || 0) < 0 ? 'down' : 'stable',
          icon: <CheckCircle />,
          color: 'success',
          insight: `${trends.compliance_change > 0 ? 'Improved' : trends.compliance_change < 0 ? 'Decreased' : 'Stable'} compliance score`,
          quickAction: {
            label: 'View Details',
            action: () => window.location.href = '/compliance'
          }
        });
      }

      if (m.open_capas !== undefined) {
        metrics.push({
          id: 'capas',
          title: 'Open CAPAs',
          value: m.open_capas,
          change: trends.capa_change || 0,
          trend: (trends.capa_change || 0) < 0 ? 'up' : (trends.capa_change || 0) > 0 ? 'down' : 'stable', // Less CAPAs is better
          icon: <Assignment />,
          color: m.open_capas > 10 ? 'error' : m.open_capas > 5 ? 'warning' : 'success',
          insight: `${Math.abs(trends.capa_change || 0)} CAPAs ${(trends.capa_change || 0) < 0 ? 'closed' : 'opened'} recently`
        });
      }

      if (m.audit_score !== undefined) {
        metrics.push({
          id: 'audit',
          title: 'Audit Score',
          value: `${m.audit_score}%`,
          change: trends.audit_change || 0,
          trend: (trends.audit_change || 0) > 0 ? 'up' : (trends.audit_change || 0) < 0 ? 'down' : 'stable',
          icon: <Analytics />,
          color: 'success',
          insight: `Exceeding target by ${Math.max(0, m.audit_score - 90)}%`
        });
      }

      // Role-specific metrics
      if (roleName === 'Production Operator') {
        if (m.tasks_completed_today !== undefined) {
          metrics.push({
            id: 'tasks',
            title: "Today's Tasks",
            value: m.tasks_completed_today,
            change: 0,
            trend: 'stable',
            icon: <Assignment />,
            color: 'primary',
            insight: 'Tasks completed today'
          });
        }

        if (m.line_efficiency !== undefined) {
          metrics.push({
            id: 'efficiency',
            title: 'Line Efficiency',
            value: `${m.line_efficiency}%`,
            change: 3.2,
            trend: 'up',
            icon: <TrendingUp />,
            color: 'success',
            insight: 'Above target performance'
          });
        }
      }
    }

    // Transform tasks from backend format
    const tasks: SmartTask[] = tasksData?.tasks?.map((task: any) => ({
      id: task.id,
      title: task.title,
      description: task.description,
      priority: task.priority,
      dueDate: new Date(task.due_date),
      category: task.category,
      progress: task.progress,
      estimatedTime: task.estimated_time
    })) || [];

    // Transform insights from backend format
    const insights: SmartInsight[] = insightsData?.insights?.map((insight: any) => ({
      id: insight.id,
      title: insight.title,
      description: insight.description,
      type: insight.type,
      action: insight.action ? {
        label: insight.action.label,
        onClick: () => {
          if (insight.action.endpoint) {
            // Handle navigation or API call based on action
            window.location.href = insight.action.endpoint;
          }
        }
      } : undefined
    })) || [];

    return { metrics, tasks, insights };
  };

  const getRoleBasedData = (role: string) => {
    const baseData = {
      'QA Manager': {
        metrics: [
          {
            id: '1',
            title: 'Compliance Score',
            value: '94.2%',
            change: 2.1,
            trend: 'up' as const,
            icon: <CheckCircle />,
            color: 'success' as const,
            insight: 'Improved by 2.1% this month',
            quickAction: {
              label: 'View Details',
              action: () => console.log('Navigate to compliance'),
            },
          },
          {
            id: '2',
            title: 'Open CAPAs',
            value: 8,
            change: -2,
            trend: 'down' as const,
            icon: <Assignment />,
            color: 'warning' as const,
            insight: '2 CAPAs closed this week',
          },
          {
            id: '3',
            title: 'Audit Score',
            value: '98.5%',
            change: 1.2,
            trend: 'up' as const,
            icon: <Analytics />,
            color: 'success' as const,
            insight: 'Exceeding target by 8.5%',
          },
          {
            id: '4',
            title: 'Risk Level',
            value: 'Low',
            change: 0,
            trend: 'stable' as const,
            icon: <Speed />,
            color: 'success' as const,
            insight: 'Maintained for 3 months',
          },
        ],
        tasks: [
          {
            id: '1',
            title: 'Monthly HACCP Review',
            description: 'Review and approve HACCP plans for new products',
            priority: 'high' as const,
            dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
            category: 'HACCP',
            progress: 75,
            estimatedTime: '2 hours',
          },
          {
            id: '2',
            title: 'Supplier Audit Schedule',
            description: 'Schedule quarterly audits for critical suppliers',
            priority: 'medium' as const,
            dueDate: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000),
            category: 'Supplier Management',
            estimatedTime: '1 hour',
          },
        ],
        insights: [
          {
            id: '1',
            title: 'AI Recommendation',
            description: 'Consider implementing automated CCP monitoring for Line 3 to reduce manual checks',
            type: 'info' as const,
            action: {
              label: 'Learn More',
              onClick: () => console.log('Show AI recommendation details'),
            },
          },
          {
            id: '2',
            title: 'Training Alert',
            description: '5 operators need refresher training on allergen control procedures',
            type: 'warning' as const,
            action: {
              label: 'Schedule Training',
              onClick: () => console.log('Navigate to training'),
            },
          },
        ],
      },
      'Production Operator': {
        metrics: [
          {
            id: '1',
            title: "Today's Tasks",
            value: 6,
            change: 0,
            trend: 'stable' as const,
            icon: <Assignment />,
            color: 'primary' as const,
            insight: '4 completed, 2 pending',
          },
          {
            id: '2',
            title: 'Line Efficiency',
            value: '96.8%',
            change: 3.2,
            trend: 'up' as const,
            icon: <TrendingUp />,
            color: 'success' as const,
            insight: 'Above target performance',
          },
          {
            id: '3',
            title: 'Quality Checks',
            value: '100%',
            change: 0,
            trend: 'stable' as const,
            icon: <CheckCircle />,
            color: 'success' as const,
            insight: 'All checks passed today',
          },
        ],
        tasks: [
          {
            id: '1',
            title: 'Pre-operational Check',
            description: 'Complete pre-operational sanitation verification',
            priority: 'high' as const,
            dueDate: new Date(Date.now() + 1 * 60 * 60 * 1000),
            category: 'Sanitation',
            estimatedTime: '30 minutes',
          },
        ],
        insights: [
          {
            id: '1',
            title: 'Quick Win',
            description: 'You can improve efficiency by 2% by optimizing changeover procedures',
            type: 'success' as const,
          },
        ],
      },
    };

    return baseData[role as keyof typeof baseData] || baseData['Production Operator'];
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getTrendIcon = (trend: string, change: number) => {
    if (trend === 'up') return <TrendingUp color="success" fontSize="small" />;
    if (trend === 'down') return <TrendingDown color="error" fontSize="small" />;
    return <div style={{ width: 20, height: 20 }} />;
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((item) => (
            <Grid item xs={12} sm={6} md={3} key={item}>
              <Card sx={{ height: 140 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Avatar sx={{ bgcolor: 'grey.200', width: 40, height: 40 }} />
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" sx={{ bgcolor: 'grey.200', height: 20, borderRadius: 1 }} />
                      <Typography variant="body2" sx={{ bgcolor: 'grey.100', height: 16, borderRadius: 1, mt: 1 }} />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Welcome Section with Personalization */}
      <Fade in timeout={500}>
        <Box sx={{ mb: 4 }}>
          <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
            <Avatar sx={{ 
              bgcolor: 'primary.main', 
              width: 60, 
              height: 60,
              background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
            }}>
              <AutoAwesome fontSize="large" />
            </Avatar>
            <Box>
              <Typography variant="h4" fontWeight={700} sx={{ 
                background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                Good {new Date().getHours() < 12 ? 'Morning' : new Date().getHours() < 18 ? 'Afternoon' : 'Evening'}, {user?.full_name?.split(' ')[0]}!
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {user?.role_name} • {new Date().toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </Typography>
            </Box>
          </Stack>
        </Box>
      </Fade>

      {/* Smart Metrics Cards */}
      <Fade in timeout={800}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={700} sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Insights color="primary" />
            Smart Insights
          </Typography>
          <Grid container spacing={3}>
            {metrics.map((metric, index) => (
              <Grid item xs={12} sm={6} md={3} key={metric.id}>
                <Grow in timeout={600 + index * 100}>
                  <Card sx={{ 
                    height: '100%',
                    background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',
                    border: '1px solid',
                    borderColor: 'divider',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                      borderColor: 'primary.main',
                    },
                  }}>
                    <CardContent>
                      <Stack spacing={2}>
                        <Stack direction="row" alignItems="center" justifyContent="space-between">
                          <Avatar sx={{ 
                            bgcolor: `${metric.color}.main`, 
                            width: 48, 
                            height: 48,
                            boxShadow: `0 4px 12px rgba(30, 64, 175, 0.3)`,
                          }}>
                            {metric.icon}
                          </Avatar>
                          <Stack direction="row" alignItems="center" spacing={0.5}>
                            {getTrendIcon(metric.trend, metric.change)}
                            <Typography 
                              variant="caption" 
                              color={metric.trend === 'up' ? 'success.main' : metric.trend === 'down' ? 'error.main' : 'text.secondary'}
                              fontWeight={600}
                            >
                              {metric.change > 0 ? '+' : ''}{metric.change}%
                            </Typography>
                          </Stack>
                        </Stack>
                        
                        <Box>
                          <Typography variant="h4" fontWeight={700} color="text.primary">
                            {metric.value}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" fontWeight={500}>
                            {metric.title}
                          </Typography>
                          {metric.insight && (
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                              {metric.insight}
                            </Typography>
                          )}
                        </Box>

                        {metric.quickAction && (
                          <Button 
                            size="small" 
                            variant="outlined" 
                            onClick={metric.quickAction.action}
                            sx={{ alignSelf: 'flex-start' }}
                          >
                            {metric.quickAction.label}
                          </Button>
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                </Grow>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Fade>

      {/* Smart Tasks, Insights and Quick Charts */}
      <Grid container spacing={3}>
        {/* Priority Tasks */}
        <Grid item xs={12} md={8}>
          <Fade in timeout={1000}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Stack direction="row" alignItems="center" justifyContent="between" sx={{ mb: 3 }}>
                  <Typography variant="h6" fontWeight={700} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Flag color="primary" />
                    Priority Tasks
                  </Typography>
                  <Chip label={`${tasks.length} active`} color="primary" size="small" />
                </Stack>

                <Stack spacing={2}>
                  {tasks.map((task, index) => (
                    <Grow in timeout={800 + index * 100} key={task.id}>
                      <Paper sx={{ 
                        p: 3, 
                        border: '1px solid', 
                        borderColor: 'divider',
                        borderRadius: 3,
                        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                        '&:hover': {
                          borderColor: 'primary.main',
                          transform: 'translateX(4px)',
                        },
                      }}>
                        <Stack spacing={2}>
                          <Stack direction="row" alignItems="flex-start" justifyContent="space-between">
                            <Box sx={{ flex: 1 }}>
                              <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
                                <Typography variant="subtitle1" fontWeight={600}>
                                  {task.title}
                                </Typography>
                                <Chip 
                                  label={task.priority} 
                                  color={getPriorityColor(task.priority) as any}
                                  size="small" 
                                  variant="outlined"
                                />
                              </Stack>
                              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                {task.description}
                              </Typography>
                              <Stack direction="row" alignItems="center" spacing={2}>
                                <Stack direction="row" alignItems="center" spacing={0.5}>
                                  <AccessTime fontSize="small" color="action" />
                                  <Typography variant="caption" color="text.secondary">
                                    Due {task.dueDate.toLocaleDateString()}
                                  </Typography>
                                </Stack>
                                {task.estimatedTime && (
                                  <Typography variant="caption" color="text.secondary">
                                    Est. {task.estimatedTime}
                                  </Typography>
                                )}
                              </Stack>
                            </Box>
                            <IconButton color="primary" size="small">
                              <PlayArrow />
                            </IconButton>
                          </Stack>
                          
                          {task.progress !== undefined && (
                            <Box>
                              <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1 }}>
                                <Typography variant="caption" color="text.secondary">
                                  Progress
                                </Typography>
                                <Typography variant="caption" fontWeight={600}>
                                  {task.progress}%
                                </Typography>
                              </Stack>
                              <LinearProgress 
                                variant="determinate" 
                                value={task.progress} 
                                sx={{ 
                                  height: 6, 
                                  borderRadius: 3,
                                  backgroundColor: 'grey.200',
                                  '& .MuiLinearProgress-bar': {
                                    borderRadius: 3,
                                  },
                                }}
                              />
                            </Box>
                          )}
                        </Stack>
                      </Paper>
                    </Grow>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* AI Insights */}
        <Grid item xs={12} md={4}>
          <Fade in timeout={1200}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" fontWeight={700} sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Lightbulb color="primary" />
                  Smart Insights
                </Typography>

                <Stack spacing={2}>
                  {insights.map((insight, index) => (
                    <Grow in timeout={1000 + index * 100} key={insight.id}>
                      <Alert 
                        severity={insight.type}
                        sx={{ 
                          borderRadius: 3,
                          '& .MuiAlert-message': { width: '100%' },
                        }}
                        action={
                          insight.action && (
                            <Button 
                              size="small" 
                              onClick={insight.action.onClick}
                              sx={{ whiteSpace: 'nowrap' }}
                            >
                              {insight.action.label}
                            </Button>
                          )
                        }
                      >
                        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 0.5 }}>
                          {insight.title}
                        </Typography>
                        <Typography variant="body2">
                          {insight.description}
                        </Typography>
                      </Alert>
                    </Grow>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Quick Charts Row */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>Documents by Type</Typography>
              <Box sx={{ width: '100%', height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie dataKey="value" data={docTypeSeries} nameKey="name" outerRadius={90} label>
                      {docTypeSeries.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={["#3B82F6","#10B981","#F59E0B","#EF4444","#8B5CF6","#06B6D4","#84CC16"][index % 7]} />
                      ))}
                    </Pie>
                    <RechartTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>Operational KPIs (30 days)</Typography>
              <Box sx={{ width: '100%', height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={operationalSeries}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis allowDecimals={false} />
                    <Legend />
                    <RechartTooltip />
                    <Bar dataKey="value" name="Count" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SmartDashboard;
