import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Paper,
  Tooltip,
  Fab,
  Divider,
  Avatar,
  Badge,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Tabs,
  Tab
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Assessment as AssessmentIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  Timeline as TimelineIcon,
  Public as PublicIcon,
  Lock as LockIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  GetApp as GetAppIcon,
  PictureAsPdf as PdfIcon,
  TableChart as ExcelIcon,
  Description as CsvIcon
} from '@mui/icons-material';
import { analyticsAPI, AnalyticsReport } from '../../services/analyticsAPI';

interface ReportsManagementProps {
  onRefresh?: () => void;
}

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
      id={`reports-tabpanel-${index}`}
      aria-labelledby={`reports-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ReportsManagement: React.FC<ReportsManagementProps> = ({ onRefresh }) => {
  const [reports, setReports] = useState<AnalyticsReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingReport, setEditingReport] = useState<AnalyticsReport | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    report_type: 'kpi_dashboard' as 'kpi_dashboard' | 'compliance_report' | 'performance_report' | 'trend_analysis' | 'audit_report' | 'risk_report' | 'action_report',
    is_public: false,
    export_formats: ['PDF']
  });

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsAPI.getReports();
      setReports(data);
    } catch (err) {
      setError('Failed to load reports. Please try again.');
      console.error('Error loading reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReport = () => {
    setEditingReport(null);
    setFormData({
      title: '',
      description: '',
      report_type: 'kpi_dashboard' as 'kpi_dashboard' | 'compliance_report' | 'performance_report' | 'trend_analysis' | 'audit_report' | 'risk_report' | 'action_report',
      is_public: false,
      export_formats: ['PDF']
    });
    setDialogOpen(true);
  };

  const handleEditReport = (report: AnalyticsReport) => {
    setEditingReport(report);
    setFormData({
      title: report.title,
      description: report.description || '',
      report_type: report.report_type as 'kpi_dashboard' | 'compliance_report' | 'performance_report' | 'trend_analysis' | 'audit_report' | 'risk_report' | 'action_report',
      is_public: report.is_public,
      export_formats: report.export_formats || ['PDF']
    });
    setDialogOpen(true);
  };

  const handleSaveReport = async () => {
    try {
      const reportData = {
        ...formData,
        report_config: editingReport?.report_config || {},
        chart_configs: editingReport?.chart_configs || {}
      };

      if (editingReport) {
        await analyticsAPI.updateReport(editingReport.id, reportData);
      } else {
        await analyticsAPI.createReport(reportData);
      }

      setDialogOpen(false);
      loadReports();
      if (onRefresh) onRefresh();
    } catch (err) {
      setError('Failed to save report. Please try again.');
      console.error('Error saving report:', err);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'success';
      case 'draft':
        return 'warning';
      case 'archived':
        return 'error';
      default:
        return 'default';
    }
  };

  const getReportTypeIcon = (type: string) => {
    switch (type) {
      case 'kpi_dashboard':
        return <BarChartIcon />;
      case 'compliance_report':
        return <AssessmentIcon />;
      case 'performance_report':
        return <TimelineIcon />;
      case 'trend_analysis':
        return <TimelineIcon />;
      case 'audit_report':
        return <AssessmentIcon />;
      case 'risk_report':
        return <WarningIcon />;
      case 'action_report':
        return <CheckCircleIcon />;
      default:
        return <AssessmentIcon />;
    }
  };

  const getExportFormatIcon = (format: string) => {
    switch (format.toLowerCase()) {
      case 'pdf':
        return <PdfIcon />;
      case 'excel':
        return <ExcelIcon />;
      case 'csv':
        return <CsvIcon />;
      default:
        return <GetAppIcon />;
    }
  };

  const formatReportType = (type: string) => {
    return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5" component="h2">
          Reports Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateReport}
        >
          Create Report
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Reports Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="reports tabs">
            <Tab label="All Reports" />
            <Tab label="Published" />
            <Tab label="Drafts" />
            <Tab label="Archived" />
          </Tabs>
        </Box>

        {/* All Reports Tab */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            {reports.map((report) => (
              <Grid item xs={12} sm={6} md={4} key={report.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        {getReportTypeIcon(report.report_type)}
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {report.title}
                        </Typography>
                      </Box>
                      <Box>
                        {report.is_public ? (
                          <PublicIcon color="action" fontSize="small" />
                        ) : (
                          <LockIcon color="action" fontSize="small" />
                        )}
                      </Box>
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {report.description}
                    </Typography>

                    <Box display="flex" alignItems="center" mb={2}>
                      <AssessmentIcon color="action" sx={{ mr: 1 }} />
                      <Typography variant="body2">
                        {formatReportType(report.report_type)}
                      </Typography>
                    </Box>

                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Chip
                        label={report.status}
                        color={getStatusColor(report.status) as any}
                        size="small"
                      />
                      <Box>
                        {report.export_formats?.map((format) => (
                          <Tooltip key={format} title={`Export as ${format}`}>
                            <IconButton size="small">
                              {getExportFormatIcon(format)}
                            </IconButton>
                          </Tooltip>
                        ))}
                      </Box>
                    </Box>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditReport(report)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="info">
                          <VisibilityIcon />
                        </IconButton>
                        <IconButton size="small" color="secondary">
                          <DownloadIcon />
                        </IconButton>
                        <IconButton size="small" color="default">
                          <ShareIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(report.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Published Reports Tab */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            {reports.filter(r => r.status === 'published').map((report) => (
              <Grid item xs={12} sm={6} md={4} key={report.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        {getReportTypeIcon(report.report_type)}
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {report.title}
                        </Typography>
                      </Box>
                      <Chip label="Published" color="success" size="small" />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {report.description}
                    </Typography>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton size="small" color="info">
                          <VisibilityIcon />
                        </IconButton>
                        <IconButton size="small" color="secondary">
                          <DownloadIcon />
                        </IconButton>
                        <IconButton size="small" color="default">
                          <ShareIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(report.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Drafts Tab */}
        <TabPanel value={activeTab} index={2}>
          <Grid container spacing={3}>
            {reports.filter(r => r.status === 'draft').map((report) => (
              <Grid item xs={12} sm={6} md={4} key={report.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        {getReportTypeIcon(report.report_type)}
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {report.title}
                        </Typography>
                      </Box>
                      <Chip label="Draft" color="warning" size="small" />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {report.description}
                    </Typography>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditReport(report)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="info">
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(report.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Archived Tab */}
        <TabPanel value={activeTab} index={3}>
          <Grid container spacing={3}>
            {reports.filter(r => r.status === 'archived').map((report) => (
              <Grid item xs={12} sm={6} md={4} key={report.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        {getReportTypeIcon(report.report_type)}
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {report.title}
                        </Typography>
                      </Box>
                      <Chip label="Archived" color="error" size="small" />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {report.description}
                    </Typography>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton size="small" color="info">
                          <VisibilityIcon />
                        </IconButton>
                        <IconButton size="small" color="secondary">
                          <DownloadIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(report.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>
      </Paper>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingReport ? 'Edit Report' : 'Create New Report'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Report Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                margin="normal"
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Report Type</InputLabel>
                <Select
                  value={formData.report_type}
                  onChange={(e) => setFormData({ ...formData, report_type: e.target.value as 'kpi_dashboard' | 'compliance_report' | 'performance_report' | 'trend_analysis' | 'audit_report' | 'risk_report' | 'action_report' })}
                  label="Report Type"
                >
                  <MenuItem value="kpi_dashboard">KPI Dashboard</MenuItem>
                  <MenuItem value="compliance_report">Compliance Report</MenuItem>
                  <MenuItem value="performance_report">Performance Report</MenuItem>
                  <MenuItem value="trend_analysis">Trend Analysis</MenuItem>
                  <MenuItem value="audit_report">Audit Report</MenuItem>
                  <MenuItem value="risk_report">Risk Report</MenuItem>
                  <MenuItem value="action_report">Action Report</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_public}
                    onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                  />
                }
                label="Public Report"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveReport}>
            {editingReport ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add report"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleCreateReport}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

export default ReportsManagement;

