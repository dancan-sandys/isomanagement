import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, CardContent, Grid, CircularProgress, Alert } from '@mui/material';
import api from '../services/api';

const SuppliersMetrics: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const resp = await api.get('/suppliers/dashboard/stats');
        setStats(resp?.data || resp);
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load supplier metrics');
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
        Supplier Metrics
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Overview</Typography>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(stats, null, 2)}</pre>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SuppliersMetrics;


