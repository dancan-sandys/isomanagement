import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import {
  Box,
  Grid,
  Typography,
  Stack,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Chip,
  Button,
  Alert,
  Paper,
  Card,
  CardContent,
  CircularProgress,
  LinearProgress,
  Divider,
  Skeleton,
  Badge,
  Tooltip,
  IconButton,
  Avatar,
  Fade,
  Grow,
  Slide,
} from '@mui/material';
import {
  Warning,
  CheckCircle,
  Schedule,
  Assignment,
  TrendingUp,
  TrendingDown,
  Security,
  Description,
  Timeline,
  Person,
  Notifications,
  Add,
  People,
  Assessment,
  Business,
  LocalShipping,
  Settings,
  Dashboard as DashboardIcon,
  PlayArrow,
  MoreVert,
  Star,
  Bookmark,
  Speed,
  Analytics,
  Task,
  CheckBox,
  RadioButtonUnchecked,
  Flag,
  AccessTime,
  CalendarToday,
  Insights,
  AutoAwesome,
  Lightbulb,
} from '@mui/icons-material';
import PageHeader from '../components/UI/PageHeader';
import DashboardCard from '../components/Dashboard/DashboardCard';
import StatusChip from '../components/UI/StatusChip';
import SmartDashboard from '../components/Dashboard/SmartDashboard';
import SmartOnboarding from '../components/Onboarding/SmartOnboarding';
import { RootState } from '../store';
import { hasRole, isSystemAdministrator, canManageUsers } from '../store/slices/authSlice';
import { dashboardAPI } from '../services/api';

const Dashboard: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [loading, setLoading] = useState(false);
<<<<<<< HEAD
  const [error, setError] = useState<string | null>(null);

  // Real data from API
=======
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [isFirstTime, setIsFirstTime] = useState(false);

>>>>>>> 740e8e962475a924a3ab6bffb60355e98e0abbbc
  const [dashboardData, setDashboardData] = useState<any>(null);

  useEffect(() => {
    // Load dashboard data based on user role
    loadDashboardData();
  }, [user]);

  // Check if this is user's first time (must be before any early returns)
  useEffect(() => {
    const hasSeenOnboarding = localStorage.getItem('hasSeenOnboarding');
    if (!hasSeenOnboarding && user) {
      setIsFirstTime(true);
      setShowOnboarding(true);
    }
  }, [user]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
<<<<<<< HEAD
      // Use real API call
      const response = await dashboardAPI.getDashboard();
      setDashboardData(response.data);
    } catch (error: any) {
      console.error('Failed to load dashboard data:', error);
      setError(error.response?.data?.detail || 'Failed to load dashboard data');
      // Fallback to mock data if API fails
      const mockData = getMockDashboardData();
      setDashboardData(mockData);
    } finally {
      setLoading(false);
    }
  };

  const getMockDashboardData = () => {
    if (isSystemAdministrator(user)) {
      return {
        totalDocuments: 25,
        totalHaccpPlans: 5,
        totalPrpPrograms: 8,
        totalSuppliers: 12,
        pendingApprovals: 3,
        complianceScore: 98,
        openIssues: 2,
        totalUsers: 25,
        activeUsers: 20,
        systemStatus: 'online',
        nextAuditDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        recentDocuments: [
          { id: 1, title: 'Quality Manual v2.1', category: 'manual', created_at: new Date().toISOString(), status: 'active' },
          { id: 2, title: 'HACCP Plan - Milk Processing', category: 'haccp', created_at: new Date().toISOString(), status: 'active' },
        ]
      };
    } else if (hasRole(user, 'QA Manager')) {
      return {
        openNCs: 12,
        capaCompletion: 87,
        documentUpdates: 5,
        auditSchedule: 2,
        ncTrends: [
          { id: 1, title: 'Temperature Deviation', status: 'open', priority: 'high', assignedTo: 'John Doe', dueDate: '2024-01-15' },
          { id: 2, title: 'Document Version Mismatch', status: 'pending', priority: 'medium', assignedTo: 'Jane Smith', dueDate: '2024-01-20' },
        ],
        capaDeadlines: [
          { id: 1, title: 'Equipment Calibration', dueDate: '2024-01-18', status: 'in_progress' },
          { id: 2, title: 'Staff Training Update', dueDate: '2024-01-25', status: 'pending' },
        ]
      };
    } else {
      return {
        dailyTasks: 8,
        completedTasks: 6,
        pendingReviews: 2,
        upcomingDeadlines: 3,
        recentActivities: [
          { id: 1, action: 'Completed daily checklist', time: '2 hours ago', type: 'success' },
          { id: 2, title: 'Updated process log', time: '4 hours ago', type: 'info' },
        ]
      };
=======
      const [statsResp, activityResp] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getRecentActivity(),
      ]);

      const stats = statsResp?.data || statsResp; // some services wrap data
      const activitiesWrapper = activityResp?.data || activityResp;
      const activities = activitiesWrapper?.activities || activitiesWrapper?.data?.activities || [];

      // Map backend stats to UI-friendly structure
      const mapped = {
        totalUsers: stats?.totalUsers ?? 0,
        activeUsers: stats?.activeUsers ?? 0,
        pendingApprovals: stats?.pendingApprovals ?? 0,
        systemAlerts: stats?.openIssues ?? 0,
        systemHealth: {
          database: 'healthy', // use dashboard/system-status later if needed
          storage: 'n/a',
          performance: 'ok',
          security: 'ok',
        },
        recentActivities: activities.map((a: any, idx: number) => ({
          id: a.id ?? idx,
          action: a.title ? `${a.action}: ${a.title}` : a.action,
          time: a.timestamp ?? '',
          type: 'info',
        })),
      };

      // Default welcome block for non-admins
      if (!isSystemAdministrator(user)) {
        (mapped as any).welcomeMessage = `Welcome, ${user?.full_name || user?.username || 'User'}!`;
        (mapped as any).quickActions = [
          { title: 'View Documents', path: '/documents', icon: Description },
          { title: 'Check Notifications', path: '/notifications', icon: Notifications },
          { title: 'Update Profile', path: '/profile', icon: Person },
        ];
      }

      setDashboardData(mapped);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setDashboardData(null);
    } finally {
      setLoading(false);
>>>>>>> 740e8e962475a924a3ab6bffb60355e98e0abbbc
    }
  };

  const renderSystemAdministratorDashboard = () => (
    <Grid container spacing={3}>
      {/* System Overview Cards */}
      <Grid item xs={12} md={3}>
        <DashboardCard
          title="Total Users"
          value={dashboardData?.totalUsers?.toString() || '0'}
          trend={{ value: 5, direction: 'up', label: 'vs last month' }}
          status={{ type: 'info', label: 'Active' }}
          variant="metric"
          icon={<People />}
        />
      </Grid>
      <Grid item xs={12} md={3}>
        <DashboardCard
          title="Active Users"
          value={dashboardData?.activeUsers?.toString() || '0'}
          trend={{ value: 2, direction: 'up', label: 'today' }}
          status={{ type: 'compliant', label: 'Online' }}
          variant="metric"
          icon={<Person />}
        />
      </Grid>
      <Grid item xs={12} md={3}>
        <DashboardCard
          title="Pending Approvals"
          value={dashboardData?.pendingApprovals?.toString() || '0'}
          trend={{ value: 1, direction: 'down', label: 'vs yesterday' }}
          status={{ type: 'warning', label: 'Needs Review' }}
          variant="metric"
          icon={<Assignment />}
        />
      </Grid>
      <Grid item xs={12} md={3}>
        <DashboardCard
          title="System Alerts"
          value={dashboardData?.systemAlerts?.toString() || '0'}
          trend={{ value: 0, direction: 'neutral', label: 'stable' }}
          status={{ type: 'warning', label: 'Monitor' }}
          variant="metric"
          icon={<Security />}
        />
      </Grid>

      {/* System Health */}
      <Grid item xs={12} md={6}>
        <DashboardCard
          title="System Health"
          subtitle="Current system status"
          variant="default"
        >
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h6" color="success.main">
                  Database
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {dashboardData?.systemHealth?.database || 'Unknown'}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h6" color="warning.main">
                  Storage
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {dashboardData?.systemHealth?.storage || 'Unknown'}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h6" color="success.main">
                  Performance
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {dashboardData?.systemHealth?.performance || 'Unknown'}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h6" color="success.main">
                  Security
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {dashboardData?.systemHealth?.security || 'Unknown'}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </DashboardCard>
      </Grid>

      {/* Recent Activities */}
      <Grid item xs={12} md={6}>
        <DashboardCard
          title="Recent System Activities"
          subtitle="Latest system events"
          variant="list"
        >
          <List dense>
            {dashboardData?.recentActivities?.map((activity: any) => (
              <ListItem key={activity.id} divider>
                <ListItemIcon>
                  {activity.type === 'success' ? (
                    <CheckCircle color="success" fontSize="small" />
                  ) : activity.type === 'warning' ? (
                    <Warning color="warning" fontSize="small" />
                  ) : (
                    <Description color="info" fontSize="small" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={activity.action}
                  secondary={activity.time}
                />
              </ListItem>
            ))}
          </List>
        </DashboardCard>
      </Grid>

      {/* Quick Actions */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
            <Button variant="contained" startIcon={<People />} onClick={() => window.location.href = '/users'}>
              Manage Users
            </Button>
            <Button variant="outlined" startIcon={<Settings />} onClick={() => window.location.href = '/settings'}>
              System Settings
            </Button>
            <Button variant="outlined" startIcon={<Assessment />} onClick={() => window.location.href = '/rbac'}>
              Roles & Permissions
            </Button>
          </Stack>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderQAManagerDashboard = () => (
    <Grid container spacing={3}>
      {/* Key Metrics */}
      <Grid item xs={12} md={3}>
        <DashboardCard
          title="Open NCs"
          value={dashboardData?.openNCs?.toString() || '0'}
          trend={{ value: 8, direction: 'down', label: 'vs last month' }}
          status={{ type: 'warning', label: 'Needs Attention' }}
          variant="metric"
          onClick={() => console.log('Navigate to NCs')}
        />
      </Grid>
      <Grid item xs={12} md={3}>
        <DashboardCard
          title="CAPA Completion"
          value={`${dashboardData?.capaCompletion || 0}%`}
          trend={{ value: 5, direction: 'up', label: 'vs last month' }}
          progress={{ value: dashboardData?.capaCompletion || 0, label: 'On Track' }}
          variant="metric"
        />
      </Grid>
      <Grid item xs={12} md={3}>
        <DashboardCard
          title="Document Updates"
          value={dashboardData?.documentUpdates?.toString() || '0'}
          trend={{ value: 2, direction: 'up', label: 'pending review' }}
          status={{ type: 'pending', label: 'In Review' }}
          variant="metric"
        />
      </Grid>
      <Grid item xs={12} md={3}>
        <DashboardCard
          title="Audit Schedule"
          value={dashboardData?.auditSchedule?.toString() || '0'}
          trend={{ value: 0, direction: 'neutral', label: 'this week' }}
          status={{ type: 'info', label: 'Scheduled' }}
          variant="metric"
        />
      </Grid>

      {/* NC Trends */}
      <Grid item xs={12} md={6}>
        <DashboardCard
          title="Non-Conformance Trends"
          subtitle="Recent NCs requiring attention"
          variant="list"
        >
          <List dense>
            {dashboardData?.ncTrends?.map((nc: any) => (
              <ListItem key={nc.id} divider>
                <ListItemIcon>
                  <Warning color="error" fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary={nc.title}
                  secondary={`Assigned to ${nc.assignedTo} • Due ${nc.dueDate}`}
                />
                <ListItemSecondaryAction>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Chip
                      label={nc.priority}
                      size="small"
                      color={nc.priority === 'high' ? 'error' : nc.priority === 'medium' ? 'warning' : 'default'}
                    />
                    <StatusChip
                      status={nc.status === 'open' ? 'nonConformance' : nc.status === 'pending' ? 'pending' : 'compliant'}
                      label={nc.status}
                    />
                  </Stack>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </DashboardCard>
      </Grid>

      {/* CAPA Deadlines */}
      <Grid item xs={12} md={6}>
        <DashboardCard
          title="CAPA Deadlines"
          subtitle="Upcoming corrective action deadlines"
          variant="list"
        >
          <List dense>
            {dashboardData?.capaDeadlines?.map((capa: any) => (
              <ListItem key={capa.id} divider>
                <ListItemIcon>
                  <Assignment color="primary" fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary={capa.title}
                  secondary={`Due: ${capa.dueDate}`}
                />
                <ListItemSecondaryAction>
                  <StatusChip
                    status={capa.status === 'in_progress' ? 'pending' : 'warning'}
                    label={capa.status.replace('_', ' ')}
                  />
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </DashboardCard>
      </Grid>
    </Grid>
  );

  const renderOperatorDashboard = () => (
    <Grid container spacing={3}>
      {/* Today's Tasks */}
      <Grid item xs={12} md={6}>
        <DashboardCard
          title="Today's Tasks"
          subtitle="Your daily checklist"
          variant="list"
        >
          <List dense>
            {dashboardData?.todayTasks?.map((task: any) => (
              <ListItem key={task.id} divider>
                <ListItemIcon>
                  {task.completed ? (
                    <CheckCircle color="success" fontSize="small" />
                  ) : (
                    <Schedule color="warning" fontSize="small" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={task.title}
                  secondary={`Scheduled: ${task.time}`}
                />
                <ListItemSecondaryAction>
                  <Chip
                    label={task.completed ? 'Completed' : 'Pending'}
                    size="small"
                    color={task.completed ? 'success' : 'warning'}
                  />
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Button variant="outlined" startIcon={<Add />}>
              Add Task
            </Button>
          </Box>
        </DashboardCard>
      </Grid>

      {/* Recent Activities */}
      <Grid item xs={12} md={6}>
        <DashboardCard
          title="Recent Activities"
          subtitle="Your latest actions"
          variant="list"
        >
          <List dense>
            {dashboardData?.recentActivities?.map((activity: any) => (
              <ListItem key={activity.id} divider>
                <ListItemIcon>
                  {activity.status === 'success' ? (
                    <CheckCircle color="success" fontSize="small" />
                  ) : (
                    <Warning color="warning" fontSize="small" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={activity.action}
                  secondary={activity.time}
                />
              </ListItem>
            ))}
          </List>
        </DashboardCard>
      </Grid>

      {/* Quick Actions */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
            <Button variant="contained" startIcon={<Add />}>
              Report Issue
            </Button>
            <Button variant="outlined" startIcon={<Description />}>
              View Procedures
            </Button>
            <Button variant="outlined" startIcon={<Notifications />}>
              Request Training
            </Button>
          </Stack>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderAuditorDashboard = () => (
    <Grid container spacing={3}>
      {/* Compliance Scorecard */}
      <Grid item xs={12} md={4}>
        <DashboardCard
          title="Compliance Score"
          value={`${dashboardData?.complianceScore || 0}%`}
          trend={{ value: 2, direction: 'up', label: 'vs last audit' }}
          progress={{ value: dashboardData?.complianceScore || 0, label: 'Overall Compliance' }}
          variant="metric"
        />
      </Grid>

      {/* Audit Findings */}
      <Grid item xs={12} md={8}>
        <DashboardCard
          title="Recent Audit Findings"
          subtitle="Latest compliance issues"
          variant="list"
        >
          <List dense>
            {dashboardData?.auditFindings?.map((finding: any) => (
              <ListItem key={finding.id} divider>
                <ListItemIcon>
                  <Warning 
                    color={finding.severity === 'high' ? 'error' : 'warning'} 
                    fontSize="small" 
                  />
                </ListItemIcon>
                <ListItemText
                  primary={finding.finding}
                  secondary={`Severity: ${finding.severity}`}
                />
                <ListItemSecondaryAction>
                  <StatusChip
                    status={finding.status === 'open' ? 'nonConformance' : 'pending'}
                    label={finding.status}
                  />
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </DashboardCard>
      </Grid>

      {/* Evidence Review */}
      <Grid item xs={12}>
        <DashboardCard
          title="Evidence Review Panel"
          subtitle="Documents and records requiring review"
          variant="default"
        >
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              5 documents pending review • 12 records verified today
            </Typography>
          </Alert>
          <Stack direction="row" spacing={2}>
            <Button variant="contained" startIcon={<Description />}>
              Review Documents
            </Button>
            <Button variant="outlined" startIcon={<Timeline />}>
              View Audit Log
            </Button>
          </Stack>
        </DashboardCard>
      </Grid>
    </Grid>
  );

  const renderDefaultDashboard = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <DashboardIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" gutterBottom>
              {dashboardData?.welcomeMessage || 'Welcome to ISO 22000 FSMS'}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Your personalized dashboard is being configured. Please contact your system administrator for role-specific access.
            </Typography>
            
            <Stack direction="row" spacing={2} justifyContent="center" flexWrap="wrap" useFlexGap>
              {dashboardData?.quickActions?.map((action: any) => (
                <Button
                  key={action.title}
                  variant="outlined"
                  startIcon={<action.icon />}
                  onClick={() => window.location.href = action.path}
                >
                  {action.title}
                </Button>
              ))}
            </Stack>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const getDashboardTitle = () => {
    if (isSystemAdministrator(user)) {
      return 'System Administrator Dashboard';
    } else if (hasRole(user, 'QA Manager')) {
      return 'QA Manager Dashboard';
    } else if (hasRole(user, 'Production Operator')) {
      return 'Production Operator Dashboard';
    } else if (hasRole(user, 'Auditor')) {
      return 'Auditor Dashboard';
    } else {
      return 'Dashboard';
    }
  };

  const getDashboardSubtitle = () => {
    if (isSystemAdministrator(user)) {
      return 'System administration and user management overview';
    } else if (hasRole(user, 'QA Manager')) {
      return 'Quality assurance and compliance management';
    } else if (hasRole(user, 'Production Operator')) {
      return 'Daily operations and task management';
    } else if (hasRole(user, 'Auditor')) {
      return 'Audit and compliance monitoring';
    } else {
      return 'ISO 22000 Food Safety Management System Overview';
    }
  };

  const renderDashboard = () => {
    if (isSystemAdministrator(user)) {
      return renderSystemAdministratorDashboard();
    } else if (hasRole(user, 'QA Manager')) {
      return renderQAManagerDashboard();
    } else if (hasRole(user, 'Production Operator')) {
      return renderOperatorDashboard();
    } else if (hasRole(user, 'Auditor')) {
      return renderAuditorDashboard();
    } else {
      return renderDefaultDashboard();
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  

  const handleOnboardingComplete = () => {
    localStorage.setItem('hasSeenOnboarding', 'true');
    setShowOnboarding(false);
    setIsFirstTime(false);
  };

  return (
    <Box>
      {/* Smart Onboarding */}
      <SmartOnboarding
        open={showOnboarding}
        onClose={() => setShowOnboarding(false)}
        onComplete={handleOnboardingComplete}
        isFirstTime={isFirstTime}
      />

<<<<<<< HEAD
      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {error} - Showing fallback data
        </Alert>
      )}

      {renderDashboard()}
=======
      {/* Modern Smart Dashboard */}
      <SmartDashboard />

      {/* Optional: Legacy Dashboard Toggle for comparison */}
      {process.env.NODE_ENV === 'development' && (
        <Box sx={{ position: 'fixed', top: 100, right: 20, zIndex: 1000 }}>
          <Tooltip title="Show onboarding again">
            <IconButton
              onClick={() => setShowOnboarding(true)}
              sx={{
                bgcolor: 'primary.main',
                color: 'white',
                '&:hover': { bgcolor: 'primary.dark' },
                boxShadow: 3,
              }}
            >
              <AutoAwesome />
            </IconButton>
          </Tooltip>
        </Box>
      )}
>>>>>>> 740e8e962475a924a3ab6bffb60355e98e0abbbc
    </Box>
  );
};

export default Dashboard; 