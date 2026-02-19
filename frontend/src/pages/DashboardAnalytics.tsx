import React, { useEffect, useMemo, useState } from 'react';
import { Box, Grid, Card, CardContent, Typography, CircularProgress, Alert, Divider, Stack, Chip } from '@mui/material';
import { dashboardAPI } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, Legend, LineChart, Line, CartesianGrid } from 'recharts';

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
          dashboardAPI.getComplianceMetrics(),
          dashboardAPI.getSystemStatus(),
        ]);
        const metricsData = metricsResp?.data || metricsResp; // backend may wrap under data
        const systemData = systemResp?.data || systemResp;
        setMetrics(metricsData);
        setSystem(systemData);
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load analytics');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Transform compliance metrics for charts
  const complianceBreakdown = useMemo(() => {
    if (!metrics) return [] as Array<{ name: string; score: number }>;
    const items: Array<{ name: string; score: number }> = [];
    if (metrics.documentControl) items.push({ name: 'Document Control', score: metrics.documentControl.score });
    if (metrics.haccpImplementation) items.push({ name: 'HACCP', score: metrics.haccpImplementation.score });
    if (metrics.prpPrograms) items.push({ name: 'PRP', score: metrics.prpPrograms.score });
    if (metrics.supplierManagement) items.push({ name: 'Suppliers', score: metrics.supplierManagement.score });
    return items;
  }, [metrics]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
        <CircularProgress />
      </Box>
    );
  }

  const COLORS = ['#1E40AF', '#16A34A', '#EA580C', '#2563EB', '#9333EA'];

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
        {/* Overall Compliance and Breakdown */}
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
                <Typography variant="h6">Compliance Breakdown</Typography>
                {metrics?.overallCompliance !== undefined && (
                  <Chip label={`Overall: ${Math.round(metrics.overallCompliance)}%`} color="primary" />
                )}
              </Stack>
              <Box sx={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                  <BarChart data={complianceBreakdown}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                    <RechartsTooltip formatter={(v: any) => `${v}%`} />
                    <Legend />
                    <Bar dataKey="score" name="Compliance Score" fill="#1E40AF" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Status Summary */}
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Database</Typography>
                  <Chip label={system?.database || 'unknown'} color={system?.database === 'healthy' ? 'success' : 'error'} size="small" />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">API</Typography>
                  <Chip label={system?.api || 'unknown'} color={system?.api === 'healthy' ? 'success' : 'error'} size="small" />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Auth</Typography>
                  <Chip label={system?.authentication || 'unknown'} color={system?.authentication === 'healthy' ? 'success' : 'error'} size="small" />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Storage</Typography>
                  <Chip label={system?.fileStorage || 'unknown'} color={system?.fileStorage === 'healthy' ? 'success' : 'error'} size="small" />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Users</Typography>
                  <Typography variant="h6">{system?.activeUsers ?? 0} / {system?.totalUsers ?? 0}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Uptime</Typography>
                  <Typography variant="h6">{system?.uptime || '—'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Last Backup</Typography>
                  <Typography variant="body2">{system?.lastBackup ? new Date(system.lastBackup).toLocaleString() : '—'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Version</Typography>
                  <Typography variant="body2">{system?.version || '—'}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Raw payloads (collapsible) for debugging only in dev */}
        {process.env.NODE_ENV === 'development' && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>Raw API payloads (dev only)</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(metrics, null, 2)}</pre>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(system, null, 2)}</pre>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default DashboardAnalytics;


