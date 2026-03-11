import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Alert,
  Paper,
  CircularProgress,
} from '@mui/material';
import {
  Download,
  TrendingUp,
  TrendingDown,
  Science,
  CheckCircle,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { haccpAPI } from '../../services/api';

const TIME_RANGES: { value: string; label: string; days: number }[] = [
  { value: '7days', label: 'Last 7 Days', days: 7 },
  { value: '30days', label: 'Last 30 Days', days: 30 },
  { value: '90days', label: 'Last 90 Days', days: 90 },
  { value: '1year', label: 'Last Year', days: 365 },
];

interface TrendItem {
  id: number;
  ccp_id: number;
  ccp_number: string;
  ccp_name: string;
  product_name: string | null;
  monitoring_time: string | null;
  measured_value: number;
  unit: string | null;
  is_within_limits: boolean;
  corrective_action_taken: boolean;
}

interface CcpOption {
  id: number;
  ccp_number: string;
  ccp_name: string;
  product_name: string | null;
}

interface Summary {
  total: number;
  in_spec: number;
  out_of_spec: number;
  corrective_actions: number;
  compliance_pct: number;
}

const MonitoringTrendCharts: React.FC = () => {
  const [selectedCCP, setSelectedCCP] = useState<string>('all');
  const [timeRange, setTimeRange] = useState('30days');
  const [ccpOptions, setCcpOptions] = useState<CcpOption[]>([]);
  const [items, setItems] = useState<TrendItem[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const days = useMemo(() => TIME_RANGES.find((r) => r.value === timeRange)?.days ?? 30, [timeRange]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    const ccpId = selectedCCP === 'all' ? undefined : Number(selectedCCP);
    haccpAPI
      .getMonitoringTrends({ ccp_id: ccpId, days, limit: 500 })
      .then((res: any) => {
        if (cancelled) return;
        const data = res?.data ?? res;
        const rawItems = data?.items ?? [];
        const ccps = data?.ccps ?? [];
        setCcpOptions(ccps);
        setItems(rawItems);
        setSummary(data?.summary ?? null);
      })
      .catch((e: any) => {
        if (!cancelled) {
          setError(e?.response?.data?.detail || e?.message || 'Failed to load trends');
          setItems([]);
          setSummary(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedCCP, timeRange, days]);

  const chartData = useMemo(() => {
    const sorted = [...items].sort(
      (a, b) =>
        new Date(a.monitoring_time || 0).getTime() - new Date(b.monitoring_time || 0).getTime()
    );
    return sorted.map((row) => ({
      time: row.monitoring_time
        ? new Date(row.monitoring_time).toLocaleString(undefined, {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })
        : '',
      fullTime: row.monitoring_time,
      value: row.measured_value,
      inSpec: row.is_within_limits,
      unit: row.unit || '',
      label: `${row.ccp_number}: ${row.ccp_name}`,
    }));
  }, [items]);

  const handleExportPDF = () => {
    console.log('Exporting chart as PDF...');
  };

  const handleExportExcel = () => {
    console.log('Exporting data as Excel...');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card>
        <CardHeader
          title="Monitoring Trend Charts"
          subheader="Track CCP performance and compliance trends over time"
          action={
            <Stack direction="row" spacing={1}>
              <Button variant="outlined" startIcon={<Download />} onClick={handleExportPDF}>
                Export PDF
              </Button>
              <Button variant="outlined" startIcon={<Download />} onClick={handleExportExcel}>
                Export Excel
              </Button>
            </Stack>
          }
        />
        <CardContent>
          {/* Chart Controls */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>CCP Selection</InputLabel>
                  <Select
                    value={selectedCCP}
                    label="CCP Selection"
                    onChange={(e) => setSelectedCCP(e.target.value)}
                  >
                    <MenuItem value="all">All CCPs</MenuItem>
                    {ccpOptions.map((c) => (
                      <MenuItem key={c.id} value={String(c.id)}>
                        {c.ccp_number}: {c.ccp_name}
                        {c.product_name ? ` (${c.product_name})` : ''}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Time Range</InputLabel>
                  <Select
                    value={timeRange}
                    label="Time Range"
                    onChange={(e) => setTimeRange(e.target.value)}
                  >
                    {TIME_RANGES.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Chart */}
          <Paper sx={{ p: 2, mb: 3, height: 400, minHeight: 400 }}>
            {loading ? (
              <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                <CircularProgress />
              </Box>
            ) : chartData.length === 0 ? (
              <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                height="100%"
              >
                <Science sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" gutterBottom>
                  No monitoring data
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  No logs in the selected period. Change CCP or time range, or record monitoring first.
                </Typography>
              </Box>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip
                    formatter={(value: number, name: string, props: any) => [
                      `${value} ${props.payload.unit || ''}`.trim(),
                      props.payload.label || 'Value',
                    ]}
                    labelFormatter={(label, payload) =>
                      payload?.[0]?.payload?.fullTime
                        ? new Date(payload[0].payload.fullTime).toLocaleString()
                        : label
                    }
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="value"
                    name="Measured value"
                    stroke="var(--mui-palette-primary-main)"
                    strokeWidth={2}
                    dot={(props) => {
                      const inSpec = props.payload?.inSpec;
                      return (
                        <circle
                          {...props}
                          r={4}
                          fill={inSpec === false ? 'var(--mui-palette-error-main)' : 'var(--mui-palette-success-main)'}
                        />
                      );
                    }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Paper>

          {/* Summary Statistics */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Summary Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} bgcolor="success.light" borderRadius={1}>
                  <Typography variant="h4" color="success.dark">
                    {summary ? `${summary.compliance_pct}%` : '—'}
                  </Typography>
                  <Typography variant="body2" color="success.dark">
                    Overall Compliance
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} bgcolor="info.light" borderRadius={1}>
                  <Typography variant="h4" color="info.dark">
                    {summary?.total ?? '—'}
                  </Typography>
                  <Typography variant="body2" color="info.dark">
                    Total Monitoring Events
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} bgcolor="warning.light" borderRadius={1}>
                  <Typography variant="h4" color="warning.dark">
                    {summary?.out_of_spec ?? '—'}
                  </Typography>
                  <Typography variant="body2" color="warning.dark">
                    Out of Spec Events
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} bgcolor="error.light" borderRadius={1}>
                  <Typography variant="h4" color="error.dark">
                    {summary?.corrective_actions ?? '—'}
                  </Typography>
                  <Typography variant="body2" color="error.dark">
                    Corrective Actions
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* Key Insights */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Key Insights
            </Typography>
            <Grid container spacing={2}>
              {summary && summary.total > 0 && (
                <>
                  {summary.compliance_pct >= 95 && (
                    <Grid item xs={12} sm={6}>
                      <Alert severity="success" icon={<TrendingUp />}>
                        <Typography variant="body2">
                          <strong>Positive:</strong> Compliance is {summary.compliance_pct}% in the
                          selected period.
                        </Typography>
                      </Alert>
                    </Grid>
                  )}
                  {summary.out_of_spec > 0 && (
                    <Grid item xs={12} sm={6}>
                      <Alert severity="warning" icon={<TrendingDown />}>
                        <Typography variant="body2">
                          <strong>Area of concern:</strong> {summary.out_of_spec} out-of-spec
                          reading(s). Review limits and process.
                        </Typography>
                      </Alert>
                    </Grid>
                  )}
                  {summary.corrective_actions > 0 && (
                    <Grid item xs={12} sm={6}>
                      <Alert severity="info" icon={<Science />}>
                        <Typography variant="body2">
                          <strong>Corrective actions:</strong> {summary.corrective_actions} recorded
                          in this period.
                        </Typography>
                      </Alert>
                    </Grid>
                  )}
                  {summary.compliance_pct >= 95 && summary.out_of_spec === 0 && (
                    <Grid item xs={12} sm={6}>
                      <Alert severity="success" icon={<CheckCircle />}>
                        <Typography variant="body2">
                          <strong>Good practice:</strong> All readings within limits in the selected
                          period.
                        </Typography>
                      </Alert>
                    </Grid>
                  )}
                </>
              )}
              {(!summary || summary.total === 0) && (
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    No insights yet. Record monitoring and select a CCP or time range to see trends.
                  </Typography>
                </Grid>
              )}
            </Grid>
          </Paper>
        </CardContent>
      </Card>
    </Box>
  );
};

export default MonitoringTrendCharts;
