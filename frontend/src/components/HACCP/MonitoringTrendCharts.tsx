import React, { useState } from 'react';
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
} from '@mui/material';
import {
  Download,
  TrendingUp,
  TrendingDown,
  Science,
  CheckCircle,
} from '@mui/icons-material';

const MonitoringTrendCharts: React.FC = () => {
  const [selectedCCP, setSelectedCCP] = useState('all');
  const [timeRange, setTimeRange] = useState('30days');

  const ccpOptions = [
    { value: 'all', label: 'All CCPs' },
    { value: 'ccp1', label: 'CCP 1: Cooking Temperature' },
    { value: 'ccp2', label: 'CCP 2: Cooling Temperature' },
  ];

  const timeRangeOptions = [
    { value: '7days', label: 'Last 7 Days' },
    { value: '30days', label: 'Last 30 Days' },
    { value: '90days', label: 'Last 90 Days' },
    { value: '1year', label: 'Last Year' },
  ];

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
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleExportPDF}
              >
                Export PDF
              </Button>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleExportExcel}
              >
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
                    {ccpOptions.map(option => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
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
                    {timeRangeOptions.map(option => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>

          {/* Chart Placeholder */}
          <Paper sx={{ p: 2, mb: 3, height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Box textAlign="center">
              <Science sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} />
              <Typography variant="h6" gutterBottom>
                Monitoring Trend Chart
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Interactive charts will be displayed here showing CCP performance trends
              </Typography>
            </Box>
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
                    98%
                  </Typography>
                  <Typography variant="body2" color="success.dark">
                    Overall Compliance
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} bgcolor="info.light" borderRadius={1}>
                  <Typography variant="h4" color="info.dark">
                    156
                  </Typography>
                  <Typography variant="body2" color="info.dark">
                    Total Monitoring Events
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} bgcolor="warning.light" borderRadius={1}>
                  <Typography variant="h4" color="warning.dark">
                    6
                  </Typography>
                  <Typography variant="body2" color="warning.dark">
                    Out of Spec Events
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} bgcolor="error.light" borderRadius={1}>
                  <Typography variant="h4" color="error.dark">
                    2
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
              <Grid item xs={12} sm={6}>
                <Alert severity="success" icon={<TrendingUp />}>
                  <Typography variant="body2">
                    <strong>Positive Trend:</strong> Overall compliance has improved from 94% to 98% over the last 6 months.
                  </Typography>
                </Alert>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Alert severity="warning" icon={<TrendingDown />}>
                  <Typography variant="body2">
                    <strong>Area of Concern:</strong> CCP 2 (Cooling) shows occasional deviations above 4 hours.
                  </Typography>
                </Alert>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Alert severity="info" icon={<Science />}>
                  <Typography variant="body2">
                    <strong>Recommendation:</strong> Review cooling process parameters and equipment calibration.
                  </Typography>
                </Alert>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Alert severity="success" icon={<CheckCircle />}>
                  <Typography variant="body2">
                    <strong>Good Practice:</strong> All corrective actions were implemented within required timeframes.
                  </Typography>
                </Alert>
              </Grid>
            </Grid>
          </Paper>
        </CardContent>
      </Card>
    </Box>
  );
};

export default MonitoringTrendCharts;
