import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert,
  Button,
  Skeleton,
} from '@mui/material';
import {
  Description,
  Security,
  Assignment,
  LocalShipping,
  Timeline,
  Warning,
  CheckCircle,
  Schedule,
  Add,
  TrendingUp,
} from '@mui/icons-material';
import { RootState } from '../store';
import { dashboardAPI } from '../services/api';

interface DashboardStats {
  totalDocuments: number;
  totalHaccpPlans: number;
  totalPrpPrograms: number;
  totalSuppliers: number;
  pendingApprovals: number;
}

interface RecentActivity {
  id: number;
  action: string;
  resource_type: string;
  resource_id: number;
  user: string;
  timestamp: string;
}

// Shimmer Loading Components
const StatCardSkeleton = () => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box flex={1}>
          <Skeleton variant="text" width="60%" height={20} />
          <Skeleton variant="text" width="40%" height={40} sx={{ mt: 1 }} />
          <Skeleton variant="text" width="80%" height={16} />
        </Box>
        <Skeleton variant="circular" width={40} height={40} />
      </Box>
    </CardContent>
  </Card>
);

const ActivityItemSkeleton = () => (
  <ListItem divider>
    <ListItemIcon>
      <Skeleton variant="circular" width={24} height={24} />
    </ListItemIcon>
    <ListItemText
      primary={<Skeleton variant="text" width="70%" height={20} />}
      secondary={<Skeleton variant="text" width="40%" height={16} />}
    />
  </ListItem>
);

const SystemStatusSkeleton = () => (
  <Paper sx={{ p: 2, textAlign: 'center' }}>
    <Skeleton variant="circular" width={40} height={40} sx={{ mx: 'auto', mb: 1 }} />
    <Skeleton variant="text" width="60%" height={24} sx={{ mx: 'auto' }} />
    <Skeleton variant="text" width="80%" height={20} sx={{ mx: 'auto' }} />
  </Paper>
);

const DashboardSkeleton = () => (
  <Box p={3}>
    {/* Welcome Section Skeleton */}
    <Box mb={4}>
      <Skeleton variant="text" width="40%" height={40} />
      <Skeleton variant="text" width="60%" height={24} sx={{ mt: 1 }} />
    </Box>

    {/* Statistics Cards Skeleton */}
    <Grid container spacing={3} mb={4}>
      {[1, 2, 3, 4].map((item) => (
        <Grid item xs={12} sm={6} md={3} key={item}>
          <StatCardSkeleton />
        </Grid>
      ))}
    </Grid>

    {/* Alerts and Recent Activity Skeleton */}
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Skeleton variant="text" width="30%" height={32} sx={{ mb: 2 }} />
          <Skeleton variant="text" width="100%" height={20} />
          <Skeleton variant="text" width="80%" height={20} sx={{ mt: 1 }} />
          <Skeleton variant="rectangular" width={120} height={32} sx={{ mt: 2, borderRadius: 1 }} />
        </Paper>
      </Grid>
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Skeleton variant="text" width="30%" height={32} />
            <Skeleton variant="rectangular" width={80} height={24} sx={{ borderRadius: 1 }} />
          </Box>
          <List dense>
            {[1, 2, 3].map((item) => (
              <ActivityItemSkeleton key={item} />
            ))}
          </List>
        </Paper>
      </Grid>
    </Grid>

    {/* Quick Actions Skeleton */}
    <Box mt={4}>
      <Skeleton variant="text" width="20%" height={32} sx={{ mb: 2 }} />
      <Box display="flex" gap={2} flexWrap="wrap">
        {[1, 2, 3, 4].map((item) => (
          <Skeleton key={item} variant="rectangular" width={140} height={32} sx={{ borderRadius: 16 }} />
        ))}
      </Box>
    </Box>

    {/* System Status Skeleton */}
    <Box mt={4}>
      <Skeleton variant="text" width="20%" height={32} sx={{ mb: 2 }} />
      <Grid container spacing={2}>
        {[1, 2, 3, 4].map((item) => (
          <Grid item xs={12} sm={6} md={3} key={item}>
            <SystemStatusSkeleton />
          </Grid>
        ))}
      </Grid>
    </Box>
  </Box>
);

const Dashboard: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch dashboard statistics
        const statsResponse = await dashboardAPI.getStats();
        if (statsResponse.success) {
          setStats(statsResponse.data);
        }
        
        // Fetch recent activities
        const activitiesResponse = await dashboardAPI.getRecentActivity();
        if (activitiesResponse.success) {
          setRecentActivities(activitiesResponse.data.activities || []);
        }
        
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const getStatusColor = (action: string) => {
    switch (action) {
      case 'created':
        return 'primary';
      case 'updated':
        return 'info';
      case 'approved':
        return 'success';
      case 'rejected':
        return 'error';
      default:
        return 'default';
    }
  };

  const getResourceIcon = (resourceType: string) => {
    switch (resourceType) {
      case 'document':
        return <Description />;
      case 'haccp_plan':
        return <Security />;
      case 'prp_program':
        return <Assignment />;
      case 'supplier':
        return <LocalShipping />;
      default:
        return <Timeline />;
    }
  };

  const getResourceTypeLabel = (resourceType: string) => {
    return resourceType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error" action={
          <Button color="inherit" size="small" onClick={() => window.location.reload()}>
            Retry
          </Button>
        }>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      {/* Welcome Section */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          Welcome back, {user?.full_name || 'User'}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what's happening with your ISO 22000 Food Safety Management System today.
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Documents
                  </Typography>
                  <Typography variant="h4">
                    {stats?.totalDocuments || 0}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Manuals, SOPs, Records
                  </Typography>
                </Box>
                <Description color="primary" sx={{ fontSize: 40 }} />
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
                    HACCP Plans
                  </Typography>
                  <Typography variant="h4">
                    {stats?.totalHaccpPlans || 0}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Critical Control Points
                  </Typography>
                </Box>
                <Security color="primary" sx={{ fontSize: 40 }} />
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
                    PRP Programs
                  </Typography>
                  <Typography variant="h4">
                    {stats?.totalPrpPrograms || 0}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Prerequisite Programs
                  </Typography>
                </Box>
                <Assignment color="primary" sx={{ fontSize: 40 }} />
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
                    Suppliers
                  </Typography>
                  <Typography variant="h4">
                    {stats?.totalSuppliers || 0}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Approved Vendors
                  </Typography>
                </Box>
                <LocalShipping color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alerts and Recent Activity */}
      <Grid container spacing={3}>
        {/* Pending Approvals Alert */}
        {stats?.pendingApprovals && stats.pendingApprovals > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, bgcolor: 'warning.light' }}>
              <Box display="flex" alignItems="center" mb={2}>
                <Warning color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Pending Approvals</Typography>
              </Box>
              <Typography variant="body1">
                You have {stats.pendingApprovals} items waiting for your approval.
              </Typography>
              <Button 
                variant="contained" 
                color="warning" 
                size="small" 
                sx={{ mt: 1 }}
                startIcon={<Schedule />}
              >
                Review Now
              </Button>
            </Paper>
          </Grid>
        )}

        {/* Recent Activity */}
        <Grid item xs={12} md={stats?.pendingApprovals && stats.pendingApprovals > 0 ? 6 : 12}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Recent Activity
              </Typography>
              <Chip 
                label={`${recentActivities.length} activities`} 
                size="small" 
                color="primary" 
                variant="outlined"
              />
            </Box>
            <List dense>
              {recentActivities.length > 0 ? (
                recentActivities.map((activity) => (
                  <ListItem key={activity.id} divider>
                    <ListItemIcon>
                      {getResourceIcon(activity.resource_type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body2">
                            {activity.user} {activity.action} a {getResourceTypeLabel(activity.resource_type)}
                          </Typography>
                          <Chip
                            label={activity.action}
                            size="small"
                            color={getStatusColor(activity.action) as any}
                          />
                        </Box>
                      }
                      secondary={new Date(activity.timestamp).toLocaleString()}
                    />
                  </ListItem>
                ))
              ) : (
                <ListItem>
                  <ListItemText
                    primary="No recent activity"
                    secondary="Activities will appear here as they occur"
                  />
                </ListItem>
              )}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Box mt={4}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item>
            <Chip
              icon={<Add />}
              label="Create Document"
              clickable
              color="primary"
              onClick={() => window.location.href = '/documents'}
            />
          </Grid>
          <Grid item>
            <Chip
              icon={<Add />}
              label="New HACCP Plan"
              clickable
              color="primary"
              onClick={() => window.location.href = '/haccp'}
            />
          </Grid>
          <Grid item>
            <Chip
              icon={<Add />}
              label="PRP Checklist"
              clickable
              color="primary"
              onClick={() => window.location.href = '/prp'}
            />
          </Grid>
          <Grid item>
            <Chip
              icon={<Add />}
              label="Add Supplier"
              clickable
              color="primary"
              onClick={() => window.location.href = '/suppliers'}
            />
          </Grid>
        </Grid>
      </Box>

      {/* System Status */}
      <Box mt={4}>
        <Typography variant="h6" gutterBottom>
          System Status
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <CheckCircle color="success" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6" color="success.main">
                System Online
              </Typography>
              <Typography variant="caption" color="textSecondary">
                All services operational
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <TrendingUp color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6" color="primary.main">
                Compliance Score
              </Typography>
              <Typography variant="h4" color="primary.main">
                98%
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Schedule color="info" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6" color="info.main">
                Next Audit
              </Typography>
              <Typography variant="body2">
                {new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString()}
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Warning color="warning" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6" color="warning.main">
                Open Issues
              </Typography>
              <Typography variant="h4" color="warning.main">
                2
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default Dashboard; 