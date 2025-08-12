import React, { useEffect, useState } from 'react';
import { Box, Grid, Card, CardContent, Typography, CircularProgress, Alert } from '@mui/material';
import api from '../services/api';

const DashboardAnalytics: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [system, setSystem] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [metricsResp, systemResp] = await Promise.all([
          api.get('/dashboard/compliance-metrics'),
          api.get('/dashboard/system-status'),
        ]);
        setMetrics(metricsResp?.data?.data || metricsResp?.data || {});
        setSystem(systemResp?.data?.data || systemResp?.data || {});
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load analytics');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Analytics Overview
      </Typography>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Compliance Metrics
              </Typography>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(metrics, null, 2)}</pre>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(system, null, 2)}</pre>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardAnalytics;


