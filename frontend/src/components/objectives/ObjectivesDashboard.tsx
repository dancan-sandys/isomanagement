import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Refresh as RefreshIcon
} from '@mui/icons-material';
import objectivesAPI from '../../services/objectivesAPI';

interface ObjectivesDashboardProps {
  refreshTrigger?: number;
}

const ObjectivesDashboard: React.FC<ObjectivesDashboardProps> = ({ refreshTrigger }) => {
  const [dashboardKPIs, setDashboardKPIs] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, [refreshTrigger]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await objectivesAPI.getDashboardKPIs();
      setDashboardKPIs(response);
    } catch (e) {
      setError('Failed to load dashboard data');
      console.error('Error loading dashboard data:', e);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !dashboardKPIs) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Objectives Dashboard</Typography>
        <Tooltip title="Refresh Dashboard">
          <IconButton onClick={loadDashboardData} color="primary" disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {dashboardKPIs && (
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Objectives
                </Typography>
                <Typography variant="h4" component="div">
                  {dashboardKPIs.total_objectives}
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
                  {dashboardKPIs.performance_breakdown?.on_track || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  At Risk
                </Typography>
                <Typography variant="h4" component="div" color="warning.main">
                  {dashboardKPIs.performance_breakdown?.at_risk || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Off Track
                </Typography>
                <Typography variant="h4" component="div" color="error.main">
                  {dashboardKPIs.performance_breakdown?.off_track || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default ObjectivesDashboard;
