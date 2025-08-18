import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  Stack,
  Chip,
  Button,
  IconButton,
  LinearProgress,
  Divider,
  Alert,
  Fade,
  Grow,
  Tooltip,
  Badge,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AutoAwesome,
  Insights,
  PlayArrow,
  Star,
  AccessTime,
  CheckCircle,
  Warning,
  Flag,
  Speed,
  Assignment,
  Analytics,
  Lightbulb,
  CalendarToday,
  Download,
  Schedule,
  Email,
  BarChart,
  PieChart,
  ShowChart,
  Assessment,
  Business,
  School,
  Security,
  BugReport,
  VerifiedUser,
} from '@mui/icons-material';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip as RechartTooltip,
  ResponsiveContainer,
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
  LineChart,
  Line,
  AreaChart,
  Area,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from 'recharts';
import { RootState } from '../../store';
import { dashboardAPI } from '../../services/api';

interface KPIData {
  overallCompliance: number;
  documentControl: {
    compliance: number;
    totalDocuments: number;
    approvedDocuments: number;
  };
  haccp: {
    ccpCompliance: number;
    totalHazards: number;
    controlledHazards: number;
  };
  prp: {
    completion: number;
    totalChecklists: number;
    completedChecklists: number;
  };
  suppliers: {
    performance: number;
    totalSuppliers: number;
    avgScore: number;
  };
  training: {
    completion: number;
    totalUsers: number;
    trainedUsers: number;
  };
  nonConformance: {
    last30Days: number;
    openNC: number;
    openCAPA: number;
  };
  audits: {
    completion: number;
    totalAudits: number;
    completedAudits: number;
  };
}

interface ChartData {
  chart_type: string;
  period: string;
  data: any[];
}

interface DepartmentCompliance {
  [key: string]: {
    document_compliance?: number;
    training_compliance?: number;
    overall_compliance?: number;
    total_documents?: number;
    approved_documents?: number;
    total_users?: number;
    trained_users?: number;
  };
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const EnhancedDashboard: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [loading, setLoading] = useState(true);
  const [kpiData, setKpiData] = useState<KPIData | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [departmentCompliance, setDepartmentCompliance] = useState<DepartmentCompliance>({});
  const [selectedPeriod, setSelectedPeriod] = useState('6m');
  const [selectedChart, setSelectedChart] = useState('nc_trend');
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  const [exportType, setExportType] = useState('kpi_summary');
  const [exportFormat, setExportFormat] = useState('excel');
  const [scheduleData, setScheduleData] = useState({
    reportType: 'kpi_summary',
    frequency: 'weekly',
    recipients: '',
  });

  useEffect(() => {
    loadDashboardData();
  }, [selectedPeriod, selectedChart]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [kpiResponse, chartResponse, deptResponse] = await Promise.all([
        dashboardAPI.getKPIs(),
        dashboardAPI.getChartData(selectedChart, selectedPeriod),
        dashboardAPI.getDepartmentCompliance(),
      ]);

      if (kpiResponse?.data) {
        setKpiData(kpiResponse.data);
      }
      if (chartResponse?.data) {
        setChartData(chartResponse.data);
      }
      if (deptResponse?.data) {
        setDepartmentCompliance(deptResponse.data);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await dashboardAPI.exportData(exportType, exportFormat, selectedPeriod);
      // Handle file download
      const blob = new Blob([response.data], { 
        type: response.headers['content-type'] 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.headers['content-disposition']?.split('filename=')[1] || 'export.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setExportDialogOpen(false);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const handleScheduleReport = async () => {
    try {
      const recipients = scheduleData.recipients.split(',').map(email => email.trim());
      await dashboardAPI.scheduleReport(
        scheduleData.reportType,
        scheduleData.frequency,
        recipients
      );
      setScheduleDialogOpen(false);
      // Show success message
    } catch (error) {
      console.error('Schedule report failed:', error);
    }
  };

  const renderKPICard = (title: string, value: number, subtitle: string, icon: React.ReactNode, color: string) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" color="text.secondary">
            {title}
          </Typography>
          <Box sx={{ color }}>
            {icon}
          </Box>
        </Stack>
        <Typography variant="h4" component="div" sx={{ mb: 1 }}>
          {typeof value === 'number' && title.includes('%') ? `${value}%` : value}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      </CardContent>
    </Card>
  );

  const renderChart = () => {
    if (!chartData?.data) return null;

    switch (selectedChart) {
      case 'nc_trend':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <RechartTooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#8884d8" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'compliance_by_department':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="department" />
              <YAxis />
              <RechartTooltip />
              <Legend />
              <Bar dataKey="compliance" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'supplier_performance':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="score" />
              <YAxis />
              <RechartTooltip />
              <Legend />
              <Area type="monotone" dataKey="count" stroke="#8884d8" fill="#8884d8" />
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'training_completion':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <RechartTooltip />
              <Legend />
              <Line type="monotone" dataKey="completion_rate" stroke="#82ca9d" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'audit_findings':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData.data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {chartData.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <RechartTooltip />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'document_status':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData.data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {chartData.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <RechartTooltip />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <LinearProgress sx={{ width: '50%' }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          FSMS Dashboard
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={() => setExportDialogOpen(true)}
          >
            Export
          </Button>
          <Button
            variant="outlined"
            startIcon={<Schedule />}
            onClick={() => setScheduleDialogOpen(true)}
          >
            Schedule Report
          </Button>
        </Stack>
      </Stack>

      {/* KPI Cards */}
      {kpiData && (
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} sm={6} md={3}>
            {renderKPICard(
              'Overall Compliance',
              kpiData.overallCompliance,
              'FSMS Compliance Score',
              <Assessment />,
              '#1976d2'
            )}
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            {renderKPICard(
              'CCP Compliance',
              kpiData.haccp.ccpCompliance,
              `${kpiData.haccp.controlledHazards}/${kpiData.haccp.totalHazards} Hazards Controlled`,
              <Security />,
              '#2e7d32'
            )}
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            {renderKPICard(
              'PRP Completion',
              kpiData.prp.completion,
              `${kpiData.prp.completedChecklists}/${kpiData.prp.totalChecklists} Checklists`,
              <CheckCircle />,
              '#ed6c02'
            )}
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            {renderKPICard(
              'Training Completion',
              kpiData.training.completion,
              `${kpiData.training.trainedUsers}/${kpiData.training.totalUsers} Users Trained`,
              <School />,
              '#9c27b0'
            )}
          </Grid>
        </Grid>
      )}

      {/* Chart Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" spacing={2} alignItems="center">
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Chart Type</InputLabel>
              <Select
                value={selectedChart}
                label="Chart Type"
                onChange={(e) => setSelectedChart(e.target.value)}
              >
                <MenuItem value="nc_trend">NC Trend</MenuItem>
                <MenuItem value="compliance_by_department">Compliance by Department</MenuItem>
                <MenuItem value="supplier_performance">Supplier Performance</MenuItem>
                <MenuItem value="training_completion">Training Completion</MenuItem>
                <MenuItem value="audit_findings">Audit Findings</MenuItem>
                <MenuItem value="document_status">Document Status</MenuItem>
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Period</InputLabel>
              <Select
                value={selectedPeriod}
                label="Period"
                onChange={(e) => setSelectedPeriod(e.target.value)}
              >
                <MenuItem value="1m">1 Month</MenuItem>
                <MenuItem value="3m">3 Months</MenuItem>
                <MenuItem value="6m">6 Months</MenuItem>
                <MenuItem value="1y">1 Year</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </CardContent>
      </Card>

      {/* Chart */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" mb={2}>
            {selectedChart.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </Typography>
          {renderChart()}
        </CardContent>
      </Card>

      {/* Department Compliance */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Department Compliance
              </Typography>
              <List>
                {Object.entries(departmentCompliance).map(([dept, data]) => (
                  <ListItem key={dept}>
                    <ListItemIcon>
                      <Business />
                    </ListItemIcon>
                    <ListItemText
                      primary={dept}
                      secondary={`Overall: ${data.overall_compliance || 0}%`}
                    />
                    <Chip
                      label={`${data.overall_compliance || 0}%`}
                      color={data.overall_compliance && data.overall_compliance >= 80 ? 'success' : 'warning'}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Recent Activity
              </Typography>
              {kpiData && (
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Non-Conformances (Last 30 Days)
                    </Typography>
                    <Typography variant="h6">
                      {kpiData.nonConformance.last30Days}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Open NC/CAPA
                    </Typography>
                    <Typography variant="h6">
                      {kpiData.nonConformance.openNC} / {kpiData.nonConformance.openCAPA}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Supplier Performance
                    </Typography>
                    <Typography variant="h6">
                      {kpiData.suppliers.performance}%
                    </Typography>
                  </Box>
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Export Dialog */}
      <Dialog open={exportDialogOpen} onClose={() => setExportDialogOpen(false)}>
        <DialogTitle>Export Dashboard Data</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ minWidth: 300 }}>
            <FormControl fullWidth>
              <InputLabel>Export Type</InputLabel>
              <Select
                value={exportType}
                label="Export Type"
                onChange={(e) => setExportType(e.target.value)}
              >
                <MenuItem value="kpi_summary">KPI Summary</MenuItem>
                <MenuItem value="compliance_report">Compliance Report</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Format</InputLabel>
              <Select
                value={exportFormat}
                label="Format"
                onChange={(e) => setExportFormat(e.target.value)}
              >
                <MenuItem value="excel">Excel</MenuItem>
                <MenuItem value="csv">CSV</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleExport} variant="contained">
            Export
          </Button>
        </DialogActions>
      </Dialog>

      {/* Schedule Report Dialog */}
      <Dialog open={scheduleDialogOpen} onClose={() => setScheduleDialogOpen(false)}>
        <DialogTitle>Schedule Automated Report</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ minWidth: 300 }}>
            <FormControl fullWidth>
              <InputLabel>Report Type</InputLabel>
              <Select
                value={scheduleData.reportType}
                label="Report Type"
                onChange={(e) => setScheduleData({ ...scheduleData, reportType: e.target.value })}
              >
                <MenuItem value="kpi_summary">KPI Summary</MenuItem>
                <MenuItem value="compliance_report">Compliance Report</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Frequency</InputLabel>
              <Select
                value={scheduleData.frequency}
                label="Frequency"
                onChange={(e) => setScheduleData({ ...scheduleData, frequency: e.target.value })}
              >
                <MenuItem value="daily">Daily</MenuItem>
                <MenuItem value="weekly">Weekly</MenuItem>
                <MenuItem value="monthly">Monthly</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Recipients (comma-separated emails)"
              value={scheduleData.recipients}
              onChange={(e) => setScheduleData({ ...scheduleData, recipients: e.target.value })}
              placeholder="qa@company.com, manager@company.com"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScheduleDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleScheduleReport} variant="contained">
            Schedule
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EnhancedDashboard;
