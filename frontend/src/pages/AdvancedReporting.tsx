import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Stack,
  Button,
  Card,
  CardContent,
  Grid,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Checkbox,
  FormControlLabel,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Switch,
  Slider,
  InputAdornment,
  FormHelperText,
  Badge,
  CircularProgress,
  CardActions,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  Schedule as ScheduleIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Analytics as AnalyticsIcon,
  Dashboard as DashboardIcon,
  Report as ReportIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CalendarToday as CalendarIcon,
  Email as EmailIcon,
  FileCopy as FileCopyIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Sort as SortIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`reporting-tabpanel-${index}`}
      aria-labelledby={`reporting-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AdvancedReporting: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [reports, setReports] = useState<any[]>([]);
  const [scheduledReports, setScheduledReports] = useState<any[]>([]);
  const [reportTemplates, setReportTemplates] = useState<any[]>([]);
  const [complianceScore, setComplianceScore] = useState(85);
  const [kpiData, setKpiData] = useState<any>({});

  // Report Builder Dialog
  const [reportBuilderDialog, setReportBuilderDialog] = useState(false);
  const [reportForm, setReportForm] = useState({
    name: '',
    description: '',
    type: 'custom',
    modules: [] as string[],
    filters: {} as any,
    format: 'pdf',
    schedule: 'manual',
    recipients: [] as string[],
  });

  // Schedule Report Dialog
  const [scheduleDialog, setScheduleDialog] = useState(false);
  const [scheduleForm, setScheduleForm] = useState({
    report_id: '',
    frequency: 'weekly',
    day_of_week: 'monday',
    day_of_month: 1,
    time: '09:00',
    recipients: [] as string[],
    enabled: true,
  });

  // Executive Dashboard Data
  const [executiveData, setExecutiveData] = useState({
    complianceMetrics: {
      overall: 85,
      haccp: 92,
      prp: 78,
      supplier: 88,
      training: 91,
    },
    riskMetrics: {
      high: 3,
      medium: 12,
      low: 45,
    },
    performanceMetrics: {
      ncCount: 8,
      capaCount: 15,
      auditCount: 6,
      trainingCount: 24,
    },
    trendData: [
      { month: 'Jan', compliance: 82, incidents: 5, training: 18 },
      { month: 'Feb', compliance: 84, incidents: 4, training: 20 },
      { month: 'Mar', compliance: 86, incidents: 3, training: 22 },
      { month: 'Apr', compliance: 85, incidents: 6, training: 19 },
      { month: 'May', compliance: 88, incidents: 2, training: 25 },
      { month: 'Jun', compliance: 85, incidents: 8, training: 24 },
    ],
  });

  const availableModules = [
    'documents', 'haccp', 'prp', 'suppliers', 'traceability', 'nonconformance',
    'audits', 'training', 'risks', 'management_review', 'complaints', 'equipment'
  ];

  const reportTypes = [
    { value: 'compliance', label: 'Compliance Report', icon: <CheckIcon /> },
    { value: 'performance', label: 'Performance Report', icon: <TrendingUpIcon /> },
    { value: 'risk', label: 'Risk Assessment', icon: <WarningIcon /> },
    { value: 'audit', label: 'Audit Summary', icon: <AssessmentIcon /> },
    { value: 'training', label: 'Training Report', icon: <AnalyticsIcon /> },
    { value: 'custom', label: 'Custom Report', icon: <ReportIcon /> },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  const loadData = async () => {
    setLoading(true);
    try {
      // Simulate API calls for now
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data
      setReports([
        { id: 1, name: 'Monthly Compliance Report', type: 'compliance', lastGenerated: '2024-12-01', status: 'active' },
        { id: 2, name: 'HACCP Performance Summary', type: 'performance', lastGenerated: '2024-11-28', status: 'active' },
        { id: 3, name: 'Supplier Risk Assessment', type: 'risk', lastGenerated: '2024-11-25', status: 'draft' },
      ]);

      setScheduledReports([
        { id: 1, name: 'Weekly Compliance Report', frequency: 'weekly', nextRun: '2024-12-08', status: 'active' },
        { id: 2, name: 'Monthly Executive Summary', frequency: 'monthly', nextRun: '2024-12-31', status: 'active' },
        { id: 3, name: 'Quarterly Risk Assessment', frequency: 'quarterly', nextRun: '2025-01-31', status: 'paused' },
      ]);

      setReportTemplates([
        { id: 1, name: 'ISO 22000 Compliance Template', type: 'compliance', description: 'Standard compliance report template' },
        { id: 2, name: 'Executive Dashboard Template', type: 'performance', description: 'Executive summary dashboard' },
        { id: 3, name: 'Risk Assessment Template', type: 'risk', description: 'Comprehensive risk assessment report' },
      ]);

    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleReportSubmit = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setReportBuilderDialog(false);
      setReportForm({
        name: '',
        description: '',
        type: 'custom',
        modules: [],
        filters: {},
        format: 'pdf',
        schedule: 'manual',
        recipients: [],
      });
      loadData();
    } catch (error) {
      console.error('Error creating report:', error);
    }
  };

  const handleScheduleSubmit = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setScheduleDialog(false);
      setScheduleForm({
        report_id: '',
        frequency: 'weekly',
        day_of_week: 'monday',
        day_of_month: 1,
        time: '09:00',
        recipients: [],
        enabled: true,
      });
      loadData();
    } catch (error) {
      console.error('Error scheduling report:', error);
    }
  };

  const getComplianceColor = (score: number) => {
    if (score >= 90) return 'success';
    if (score >= 75) return 'warning';
    return 'error';
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Box p={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight="bold" color="primary">
          Advanced Reporting & Analytics
        </Typography>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<ScheduleIcon />}
            onClick={() => setScheduleDialog(true)}
          >
            Schedule Report
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setReportBuilderDialog(true)}
          >
            Create Report
          </Button>
        </Stack>
      </Stack>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="reporting tabs">
            <Tab
              icon={<DashboardIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Executive Dashboard</span>
                  <Badge badgeContent={1} color="primary" />
                </Stack>
              }
            />
            <Tab
              icon={<ReportIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Custom Reports</span>
                  <Badge badgeContent={reports.length} color="secondary" />
                </Stack>
              }
            />
            <Tab
              icon={<ScheduleIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Scheduled Reports</span>
                  <Badge badgeContent={scheduledReports.length} color="info" />
                </Stack>
              }
            />
            <Tab
              icon={<AnalyticsIcon />}
              label="Analytics"
            />
            <Tab
              icon={<SettingsIcon />}
              label="Templates"
            />
          </Tabs>
        </Box>

        {/* Executive Dashboard Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            {/* Compliance Score Card */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                    <Typography variant="h6" color="text.secondary">
                      Overall Compliance
                    </Typography>
                    <Chip
                      label={`${executiveData.complianceMetrics.overall}%`}
                      color={getComplianceColor(executiveData.complianceMetrics.overall)}
                      size="small"
                    />
                  </Stack>
                  <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                    <CircularProgress
                      variant="determinate"
                      value={executiveData.complianceMetrics.overall}
                      size={80}
                      color={getComplianceColor(executiveData.complianceMetrics.overall) as any}
                    />
                    <Box
                      sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Typography variant="h6" component="div" color="text.secondary">
                        {executiveData.complianceMetrics.overall}%
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Risk Metrics Card */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                    Risk Distribution
                  </Typography>
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">High Risk</Typography>
                      <Chip label={executiveData.riskMetrics.high} color="error" size="small" />
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Medium Risk</Typography>
                      <Chip label={executiveData.riskMetrics.medium} color="warning" size="small" />
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Low Risk</Typography>
                      <Chip label={executiveData.riskMetrics.low} color="success" size="small" />
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            {/* Performance Metrics Card */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                    Performance Metrics
                  </Typography>
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Non-Conformances</Typography>
                      <Typography variant="h6">{executiveData.performanceMetrics.ncCount}</Typography>
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">CAPA Actions</Typography>
                      <Typography variant="h6">{executiveData.performanceMetrics.capaCount}</Typography>
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Audits</Typography>
                      <Typography variant="h6">{executiveData.performanceMetrics.auditCount}</Typography>
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            {/* Training Metrics Card */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                    Training Status
                  </Typography>
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Completed</Typography>
                      <Typography variant="h6" color="success.main">
                        {executiveData.performanceMetrics.trainingCount}
                      </Typography>
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Pending</Typography>
                      <Typography variant="h6" color="warning.main">5</Typography>
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Overdue</Typography>
                      <Typography variant="h6" color="error.main">2</Typography>
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            {/* Compliance Trend Chart */}
            <Grid item xs={12} lg={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Compliance Trend</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={executiveData.trendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      <Line type="monotone" dataKey="compliance" stroke="#8884d8" strokeWidth={2} />
                      <Line type="monotone" dataKey="incidents" stroke="#82ca9d" strokeWidth={2} />
                      <Line type="monotone" dataKey="training" stroke="#ffc658" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Module Compliance Chart */}
            <Grid item xs={12} lg={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Module Compliance</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'HACCP', value: executiveData.complianceMetrics.haccp },
                          { name: 'PRP', value: executiveData.complianceMetrics.prp },
                          { name: 'Supplier', value: executiveData.complianceMetrics.supplier },
                          { name: 'Training', value: executiveData.complianceMetrics.training },
                        ]}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {[
                          { name: 'HACCP', value: executiveData.complianceMetrics.haccp },
                          { name: 'PRP', value: executiveData.complianceMetrics.prp },
                          { name: 'Supplier', value: executiveData.complianceMetrics.supplier },
                          { name: 'Training', value: executiveData.complianceMetrics.training },
                        ].map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Custom Reports Tab */}
        <TabPanel value={tabValue} index={1}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">Custom Reports</Typography>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => setReportBuilderDialog(true)}
            >
              Create New Report
            </Button>
          </Stack>
          <Grid container spacing={3}>
            {reports.map((report) => (
              <Grid item xs={12} md={6} lg={4} key={report.id}>
                <Card>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                      <Typography variant="h6" fontWeight="bold">
                        {report.name}
                      </Typography>
                      <Chip
                        label={report.type}
                        color={report.type === 'compliance' ? 'success' : report.type === 'performance' ? 'primary' : 'warning'}
                        size="small"
                      />
                    </Stack>
                    <Stack spacing={1}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Last Generated:</strong> {new Date(report.lastGenerated).toLocaleDateString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Status:</strong> {report.status}
                      </Typography>
                    </Stack>
                  </CardContent>
                  <CardActions>
                    <Button size="small" startIcon={<ViewIcon />}>
                      View
                    </Button>
                    <Button size="small" startIcon={<DownloadIcon />}>
                      Download
                    </Button>
                    <Button size="small" startIcon={<EditIcon />}>
                      Edit
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Scheduled Reports Tab */}
        <TabPanel value={tabValue} index={2}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">Scheduled Reports</Typography>
            <Button
              variant="outlined"
              startIcon={<ScheduleIcon />}
              onClick={() => setScheduleDialog(true)}
            >
              Schedule New Report
            </Button>
          </Stack>
          <Grid container spacing={3}>
            {scheduledReports.map((report) => (
              <Grid item xs={12} md={6} lg={4} key={report.id}>
                <Card>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                      <Typography variant="h6" fontWeight="bold">
                        {report.name}
                      </Typography>
                      <Chip
                        label={report.status}
                        color={report.status === 'active' ? 'success' : 'default'}
                        size="small"
                      />
                    </Stack>
                    <Stack spacing={1}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Frequency:</strong> {report.frequency}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Next Run:</strong> {new Date(report.nextRun).toLocaleDateString()}
                      </Typography>
                    </Stack>
                  </CardContent>
                  <CardActions>
                    <Button size="small" startIcon={<ViewIcon />}>
                      View Schedule
                    </Button>
                    <Button size="small" startIcon={<EditIcon />}>
                      Edit
                    </Button>
                    <Button size="small" startIcon={<DeleteIcon />}>
                      Delete
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Analytics Tab */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" sx={{ mb: 2 }}>Advanced Analytics</Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Non-Conformance Trends</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={executiveData.trendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <RechartsTooltip />
                      <Area type="monotone" dataKey="incidents" stackId="1" stroke="#8884d8" fill="#8884d8" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} lg={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Training Completion</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={executiveData.trendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="training" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Templates Tab */}
        <TabPanel value={tabValue} index={4}>
          <Typography variant="h6" sx={{ mb: 2 }}>Report Templates</Typography>
          <Grid container spacing={3}>
            {reportTemplates.map((template) => (
              <Grid item xs={12} md={6} lg={4} key={template.id}>
                <Card>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                      <Typography variant="h6" fontWeight="bold">
                        {template.name}
                      </Typography>
                      <Chip
                        label={template.type}
                        color={template.type === 'compliance' ? 'success' : template.type === 'performance' ? 'primary' : 'warning'}
                        size="small"
                      />
                    </Stack>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {template.description}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" startIcon={<ViewIcon />}>
                      Preview
                    </Button>
                    <Button size="small" startIcon={<FileCopyIcon />}>
                      Use Template
                    </Button>
                    <Button size="small" startIcon={<EditIcon />}>
                      Edit
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>
      </Paper>

      {/* Report Builder Dialog */}
      <Dialog open={reportBuilderDialog} onClose={() => setReportBuilderDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Custom Report</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                label="Report Name"
                value={reportForm.name}
                onChange={(e) => setReportForm({ ...reportForm, name: e.target.value })}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Report Type</InputLabel>
                <Select
                  label="Report Type"
                  value={reportForm.type}
                  onChange={(e) => setReportForm({ ...reportForm, type: e.target.value })}
                >
                  {reportTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      <Stack direction="row" spacing={1} alignItems="center">
                        {type.icon}
                        <span>{type.label}</span>
                      </Stack>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                value={reportForm.description}
                onChange={(e) => setReportForm({ ...reportForm, description: e.target.value })}
                fullWidth
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Include Modules</Typography>
              <Grid container spacing={1}>
                {availableModules.map((module) => (
                  <Grid item xs={6} md={4} key={module}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={reportForm.modules.includes(module)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setReportForm({
                                ...reportForm,
                                modules: [...reportForm.modules, module]
                              });
                            } else {
                              setReportForm({
                                ...reportForm,
                                modules: reportForm.modules.filter(m => m !== module)
                              });
                            }
                          }}
                        />
                      }
                      label={module.charAt(0).toUpperCase() + module.slice(1)}
                    />
                  </Grid>
                ))}
              </Grid>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Output Format</InputLabel>
                <Select
                  label="Output Format"
                  value={reportForm.format}
                  onChange={(e) => setReportForm({ ...reportForm, format: e.target.value })}
                >
                  <MenuItem value="pdf">PDF</MenuItem>
                  <MenuItem value="excel">Excel</MenuItem>
                  <MenuItem value="csv">CSV</MenuItem>
                  <MenuItem value="html">HTML</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Schedule</InputLabel>
                <Select
                  label="Schedule"
                  value={reportForm.schedule}
                  onChange={(e) => setReportForm({ ...reportForm, schedule: e.target.value })}
                >
                  <MenuItem value="manual">Manual</MenuItem>
                  <MenuItem value="daily">Daily</MenuItem>
                  <MenuItem value="weekly">Weekly</MenuItem>
                  <MenuItem value="monthly">Monthly</MenuItem>
                  <MenuItem value="quarterly">Quarterly</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReportBuilderDialog(false)}>Cancel</Button>
          <Button onClick={handleReportSubmit} variant="contained">Create Report</Button>
        </DialogActions>
      </Dialog>

      {/* Schedule Report Dialog */}
      <Dialog open={scheduleDialog} onClose={() => setScheduleDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Schedule Report</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>Report</InputLabel>
                <Select
                  label="Report"
                  value={scheduleForm.report_id}
                  onChange={(e) => setScheduleForm({ ...scheduleForm, report_id: e.target.value })}
                >
                  {reports.map((report) => (
                    <MenuItem key={report.id} value={report.id}>{report.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Frequency</InputLabel>
                <Select
                  label="Frequency"
                  value={scheduleForm.frequency}
                  onChange={(e) => setScheduleForm({ ...scheduleForm, frequency: e.target.value })}
                >
                  <MenuItem value="daily">Daily</MenuItem>
                  <MenuItem value="weekly">Weekly</MenuItem>
                  <MenuItem value="monthly">Monthly</MenuItem>
                  <MenuItem value="quarterly">Quarterly</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Time"
                type="time"
                value={scheduleForm.time}
                onChange={(e) => setScheduleForm({ ...scheduleForm, time: e.target.value })}
                fullWidth
                required
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={scheduleForm.enabled}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, enabled: e.target.checked })}
                  />
                }
                label="Enable Schedule"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScheduleDialog(false)}>Cancel</Button>
          <Button onClick={handleScheduleSubmit} variant="contained">Schedule Report</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdvancedReporting;
