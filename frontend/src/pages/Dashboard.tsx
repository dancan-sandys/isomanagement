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
  CircularProgress,
  Alert,
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
} from '@mui/icons-material';
import { RootState } from '../store';
import { dashboardAPI } from '../services/api';

interface DashboardStats {
  totalDocuments: number;
  totalHaccpPlans: number;
  totalPrpPrograms: number;
  totalSuppliers: number;
  pendingApprovals: number;
  recentActivities: Array<{
    id: number;
    action: string;
    resource_type: string;
    resource_id: number;
    user: string;
    timestamp: string;
  }>;
}

const Dashboard: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // For now, we'll use mock data since the backend endpoints aren't implemented yet
        const mockStats: DashboardStats = {
          totalDocuments: 24,
          totalHaccpPlans: 8,
          totalPrpPrograms: 12,
          totalSuppliers: 15,
          pendingApprovals: 3,
          recentActivities: [
            {
              id: 1,
              action: 'created',
              resource_type: 'document',
              resource_id: 123,
              user: 'John Doe',
              timestamp: new Date().toISOString(),
            },
            {
              id: 2,
              action: 'updated',
              resource_type: 'haccp_plan',
              resource_id: 45,
              user: 'Jane Smith',
              timestamp: new Date(Date.now() - 3600000).toISOString(),
            },
            {
              id: 3,
              action: 'approved',
              resource_type: 'document',
              resource_id: 67,
              user: 'Mike Johnson',
              timestamp: new Date(Date.now() - 7200000).toISOString(),
            },
          ],
        };
        
        setStats(mockStats);
      } catch (err) {
        setError('Failed to load dashboard data');
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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
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
            </Paper>
          </Grid>
        )}

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <List dense>
              {stats?.recentActivities.map((activity) => (
                <ListItem key={activity.id} divider>
                  <ListItemIcon>
                    {getResourceIcon(activity.resource_type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body2">
                          {activity.user} {activity.action} a {activity.resource_type.replace('_', ' ')}
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
              ))}
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
              icon={<Description />}
              label="Create Document"
              clickable
              color="primary"
            />
          </Grid>
          <Grid item>
            <Chip
              icon={<Security />}
              label="New HACCP Plan"
              clickable
              color="primary"
            />
          </Grid>
          <Grid item>
            <Chip
              icon={<Assignment />}
              label="PRP Checklist"
              clickable
              color="primary"
            />
          </Grid>
          <Grid item>
            <Chip
              icon={<LocalShipping />}
              label="Add Supplier"
              clickable
              color="primary"
            />
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default Dashboard; 