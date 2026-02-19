import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Speed as SpeedIcon,
  Timeline as TimelineIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { performanceMonitor, PerformanceMetric } from '../../utils/performance';

interface PerformanceSummary {
  totalMetrics: number;
  averageAPITime: number;
  averageNavigationTime: number;
  slowOperations: number;
  apiCalls: number;
  navigations: number;
}

const PerformanceDashboard: React.FC = () => {
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [recentMetrics, setRecentMetrics] = useState<PerformanceMetric[]>([]);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const updateMetrics = () => {
    const performanceData = performanceMonitor.getPerformanceSummary();
    setSummary(performanceData);
    
    const now = Date.now();
    const last10Minutes = now - 10 * 60 * 1000;
    const recent = performanceMonitor.getMetrics(undefined, { start: last10Minutes, end: now });
    setRecentMetrics(recent.slice(-20)); // Last 20 metrics
  };

  useEffect(() => {
    updateMetrics();
    
    if (autoRefresh) {
      const interval = setInterval(updateMetrics, 5000); // Update every 5 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getPerformanceColor = (value: number, threshold: number) => {
    if (value < threshold * 0.5) return 'success';
    if (value < threshold) return 'warning';
    return 'error';
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms.toFixed(1)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const clearMetrics = () => {
    performanceMonitor.clearMetrics();
    updateMetrics();
  };

  if (!summary) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading performance data...</Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Performance Dashboard
        </Typography>
        <Box>
          <Tooltip title="Refresh metrics">
            <IconButton onClick={updateMetrics} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Clear metrics">
            <IconButton onClick={clearMetrics} color="secondary">
              <ClearIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Performance Overview Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <SpeedIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">API Performance</Typography>
              </Box>
              <Typography variant="h4" color={getPerformanceColor(summary.averageAPITime, 100)}>
                {formatDuration(summary.averageAPITime)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Average API response time
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((summary.averageAPITime / 100) * 100, 100)}
                color={getPerformanceColor(summary.averageAPITime, 100) as any}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TimelineIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Navigation</Typography>
              </Box>
              <Typography variant="h4" color={getPerformanceColor(summary.averageNavigationTime, 1000)}>
                {formatDuration(summary.averageNavigationTime)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Average page load time
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((summary.averageNavigationTime / 1000) * 100, 100)}
                color={getPerformanceColor(summary.averageNavigationTime, 1000) as any}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <WarningIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Slow Operations</Typography>
              </Box>
              <Typography variant="h4" color={summary.slowOperations > 0 ? 'warning' : 'success'}>
                {summary.slowOperations}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Operations &gt; 100ms
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TimelineIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Metrics</Typography>
              </Box>
              <Typography variant="h4" color="info">
                {summary.totalMetrics}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Tracked in last 5 minutes
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Activity Summary */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>Activity Summary</Typography>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography>API Calls:</Typography>
                <Chip label={summary.apiCalls} color="primary" size="small" />
              </Box>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography>Page Navigations:</Typography>
                <Chip label={summary.navigations} color="secondary" size="small" />
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography>Performance Score:</Typography>
                <Chip 
                  label={`${Math.max(0, 100 - Math.floor(summary.averageAPITime / 10))}%`}
                  color={getPerformanceColor(summary.averageAPITime, 100)}
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>Performance Recommendations</Typography>
              {summary.averageAPITime > 100 && (
                <Typography variant="body2" color="warning" mb={1}>
                  • Consider implementing API response caching
                </Typography>
              )}
              {summary.averageNavigationTime > 1000 && (
                <Typography variant="body2" color="warning" mb={1}>
                  • Optimize page load times with code splitting
                </Typography>
              )}
              {summary.slowOperations > 5 && (
                <Typography variant="body2" color="warning" mb={1}>
                  • Investigate slow operations in recent metrics
                </Typography>
              )}
              {summary.averageAPITime <= 100 && summary.averageNavigationTime <= 1000 && (
                <Typography variant="body2" color="success">
                  • Performance is within acceptable ranges
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Metrics Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" mb={2}>Recent Performance Metrics</Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Operation</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Timestamp</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentMetrics.map((metric, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {metric.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={metric.category} 
                        size="small" 
                        color={metric.category === 'api' ? 'primary' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography 
                        variant="body2" 
                        color={metric.duration > 100 ? 'error' : 'textPrimary'}
                      >
                        {formatDuration(metric.duration)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={metric.duration > 100 ? 'Slow' : 'Good'} 
                        size="small" 
                        color={metric.duration > 100 ? 'error' : 'success'}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {new Date(metric.timestamp).toLocaleTimeString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default PerformanceDashboard;
