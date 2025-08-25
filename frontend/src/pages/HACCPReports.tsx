import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Chip,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tabs,
  Tab,
  
  Checkbox,
  FormControlLabel,
  FormGroup,
  LinearProgress,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Assessment,
  Download,
  Visibility,
  Refresh,
  Add,
  Schedule,
  TrendingUp,
  PieChart,
  BarChart,
  Print,
  Email,
  Share,
  FilterList,
  ExpandMore,
  Science,
  VerifiedUser,
  Security,
  Assignment,
  Timeline,
  Analytics,
  Description,
} from '@mui/icons-material';
import { LocalizationProvider, DatePicker as MUIDatePicker } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchProducts } from '../store/slices/haccpSlice';
import { haccpAPI } from '../services/api';
import PageHeader from '../components/UI/PageHeader';
import HACCPBreadcrumbs from '../components/UI/HACCPBreadcrumbs';
import HACCPPlanReport from '../components/HACCP/HACCPPlanReport';

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  type: 'monitoring' | 'verification' | 'compliance' | 'deviation' | 'custom';
  category: 'ccp' | 'product' | 'system' | 'audit';
  format: 'pdf' | 'excel' | 'csv' | 'html';
  schedule?: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'on-demand';
  parameters: {
    dateRange: boolean;
    products: boolean;
    ccps: boolean;
    status: boolean;
    responsible: boolean;
    customFields?: string[];
  };
  isActive: boolean;
  lastGenerated?: string;
  recipients?: string[];
}

interface GeneratedReport {
  id: string;
  templateId: string;
  name: string;
  type: string;
  format: string;
  generatedAt: string;
  generatedBy: string;
  size: string;
  status: 'generating' | 'completed' | 'failed';
  downloadUrl?: string;
  parameters: any;
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
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const HACCPReports: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { products } = useSelector((state: RootState) => state.haccp);
  const { user } = useSelector((state: RootState) => state.auth);

  const [selectedTab, setSelectedTab] = useState(0);
  const [reportTemplates, setReportTemplates] = useState<ReportTemplate[]>([]);
  const [generatedReports, setGeneratedReports] = useState<GeneratedReport[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null);
  const [reportDialogOpen, setReportDialogOpen] = useState(false);
  const [planReportDialogOpen, setPlanReportDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState<string[]>([]);

  const [reportForm, setReportForm] = useState({
    templateId: '',
    name: '',
    format: 'pdf' as 'pdf' | 'excel' | 'csv' | 'html',
    dateFrom: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    dateTo: new Date(),
    productIds: [] as number[],
    ccpIds: [] as number[],
    includeCharts: true,
    includeTables: true,
    includeAnalysis: true,
    emailReport: false,
    emailRecipients: '' as string,
  });

  useEffect(() => {
    dispatch(fetchProducts());
    loadReportTemplates();
    loadGeneratedReports();
  }, [dispatch]);

  const loadReportTemplates = async () => {
    setLoading(true);
    try {
      // Mock data - replace with actual API call
      const mockTemplates: ReportTemplate[] = [
        {
          id: '1',
          name: 'CCP Monitoring Report',
          description: 'Comprehensive monitoring report for all Critical Control Points',
          type: 'monitoring',
          category: 'ccp',
          format: 'pdf',
          schedule: 'weekly',
          parameters: {
            dateRange: true,
            products: true,
            ccps: true,
            status: true,
            responsible: true,
          },
          isActive: true,
          lastGenerated: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          recipients: ['qa@company.com', 'manager@company.com'],
        },
        {
          id: '2',
          name: 'Verification Summary',
          description: 'Summary of verification activities and results',
          type: 'verification',
          category: 'system',
          format: 'excel',
          schedule: 'monthly',
          parameters: {
            dateRange: true,
            products: false,
            ccps: true,
            status: true,
            responsible: true,
          },
          isActive: true,
          lastGenerated: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
          recipients: ['qa@company.com'],
        },
        {
          id: '3',
          name: 'Compliance Dashboard',
          description: 'Real-time compliance status across all HACCP components',
          type: 'compliance',
          category: 'system',
          format: 'html',
          schedule: 'daily',
          parameters: {
            dateRange: false,
            products: true,
            ccps: true,
            status: true,
            responsible: false,
          },
          isActive: true,
          lastGenerated: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          recipients: ['qa@company.com', 'production@company.com'],
        },
        {
          id: '4',
          name: 'Deviation Analysis',
          description: 'Analysis of deviations and corrective actions',
          type: 'deviation',
          category: 'ccp',
          format: 'pdf',
          schedule: 'on-demand',
          parameters: {
            dateRange: true,
            products: true,
            ccps: true,
            status: true,
            responsible: true,
            customFields: ['severity', 'corrective_action', 'root_cause'],
          },
          isActive: true,
          recipients: ['qa@company.com', 'manager@company.com'],
        },
        {
          id: '5',
          name: 'Product HACCP Plan',
          description: 'Complete HACCP plan documentation for specific products',
          type: 'custom',
          category: 'product',
          format: 'pdf',
          schedule: 'on-demand',
          parameters: {
            dateRange: false,
            products: true,
            ccps: true,
            status: false,
            responsible: true,
          },
          isActive: true,
          recipients: ['qa@company.com'],
        },
      ];
      setReportTemplates(mockTemplates);
    } catch (error) {
      console.error('Error loading report templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadGeneratedReports = async () => {
    try {
      // Mock data - replace with actual API call
      const mockReports: GeneratedReport[] = [
        {
          id: '1',
          templateId: '1',
          name: 'CCP Monitoring Report - Week 3',
          type: 'monitoring',
          format: 'pdf',
          generatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          generatedBy: user?.username || 'QA Manager',
          size: '2.4 MB',
          status: 'completed',
          downloadUrl: '/reports/ccp-monitoring-week3.pdf',
          parameters: {
            dateFrom: '2024-01-15',
            dateTo: '2024-01-21',
            productIds: [1, 2],
            ccpIds: [1, 2, 3],
          },
        },
        {
          id: '2',
          templateId: '2',
          name: 'Verification Summary - December 2023',
          type: 'verification',
          format: 'excel',
          generatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          generatedBy: user?.username || 'QA Specialist',
          size: '1.8 MB',
          status: 'completed',
          downloadUrl: '/reports/verification-summary-dec2023.xlsx',
          parameters: {
            dateFrom: '2023-12-01',
            dateTo: '2023-12-31',
            ccpIds: [1, 2, 3],
          },
        },
        {
          id: '3',
          templateId: '4',
          name: 'Deviation Analysis - Q4 2023',
          type: 'deviation',
          format: 'pdf',
          generatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
          generatedBy: user?.username || 'QA Manager',
          size: '3.2 MB',
          status: 'generating',
          parameters: {
            dateFrom: '2023-10-01',
            dateTo: '2023-12-31',
            productIds: [1, 2, 3],
            ccpIds: [1, 2, 3],
          },
        },
      ];
      setGeneratedReports(mockReports);
    } catch (error) {
      console.error('Error loading generated reports:', error);
    }
  };

  const handleGenerateReport = async () => {
    if (!reportForm.templateId) {
      alert('Please select a report template');
      return;
    }

    const template = reportTemplates.find(t => t.id === reportForm.templateId);
    if (!template) return;

    setGenerating(prev => [...prev, reportForm.templateId]);

    try {
      // Simulate report generation
      const newReport: GeneratedReport = {
        id: Date.now().toString(),
        templateId: reportForm.templateId,
        name: `${template.name} - ${new Date().toLocaleDateString()}`,
        type: template.type,
        format: reportForm.format,
        generatedAt: new Date().toISOString(),
        generatedBy: user?.username || 'Current User',
        size: 'Generating...',
        status: 'generating',
        parameters: {
          dateFrom: reportForm.dateFrom.toISOString().split('T')[0],
          dateTo: reportForm.dateTo.toISOString().split('T')[0],
          productIds: reportForm.productIds,
          ccpIds: reportForm.ccpIds,
        },
      };

      setGeneratedReports(prev => [newReport, ...prev]);

      // Simulate completion after 3 seconds
      setTimeout(() => {
        setGeneratedReports(prev => 
          prev.map(report => 
            report.id === newReport.id 
              ? { 
                  ...report, 
                  status: 'completed', 
                  size: '2.1 MB',
                  downloadUrl: `/reports/${newReport.id}.${reportForm.format}`
                }
              : report
          )
        );
        setGenerating(prev => prev.filter(id => id !== reportForm.templateId));
      }, 3000);

      setReportDialogOpen(false);
    } catch (error) {
      console.error('Error generating report:', error);
      setGenerating(prev => prev.filter(id => id !== reportForm.templateId));
    }
  };

  const handleDownloadReport = (report: GeneratedReport) => {
    if (report.status === 'completed' && report.downloadUrl) {
      // Simulate download
      window.open(report.downloadUrl, '_blank');
    }
  };

  const handleEmailReport = (report: GeneratedReport) => {
    const recipients = prompt('Enter email addresses (comma-separated):');
    if (recipients) {
      alert(`Report "${report.name}" will be emailed to: ${recipients}`);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'monitoring':
        return <Science />;
      case 'verification':
        return <VerifiedUser />;
      case 'compliance':
        return <Security />;
      case 'deviation':
        return <TrendingUp />;
      case 'custom':
        return <Assignment />;
      default:
        return <Assessment />;
    }
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'pdf':
        return <Description />;
      case 'excel':
        return <BarChart />;
      case 'csv':
        return <Timeline />;
      case 'html':
        return <Analytics />;
      default:
        return <Description />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'generating':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <HACCPBreadcrumbs />
      <PageHeader
        title="HACCP Reports & Analytics"
        subtitle="Generate comprehensive reports and analytics for HACCP system"
        showAdd={true}
        onAdd={() => setReportDialogOpen(true)}
      />

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Templates
                  </Typography>
                  <Typography variant="h4">
                    {reportTemplates.length}
                  </Typography>
                </Box>
                <Assessment color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Generating
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {generating.length}
                  </Typography>
                </Box>
                <Schedule color="warning" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Generated Today
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {generatedReports.filter(r => 
                      new Date(r.generatedAt).toDateString() === new Date().toDateString()
                    ).length}
                  </Typography>
                </Box>
                <TrendingUp color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Size
                  </Typography>
                  <Typography variant="h4" color="info.main">
                    12.4 GB
                  </Typography>
                </Box>
                <PieChart color="info" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Tabs value={selectedTab} onChange={(_, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab 
          icon={<Assessment />} 
          label="Templates" 
          iconPosition="start"
        />
        <Tab 
          icon={<Download />} 
          label="Generated Reports" 
          iconPosition="start"
        />
        <Tab 
          icon={<Analytics />} 
          label="Analytics" 
          iconPosition="start"
        />
      </Tabs>

      <TabPanel value={selectedTab} index={0}>
        {/* Report Templates */}
        <Grid container spacing={3}>
          {reportTemplates.map((template) => (
            <Grid item xs={12} md={6} lg={4} key={template.id}>
              <Card>
                <CardHeader
                  avatar={getTypeIcon(template.type)}
                  title={template.name}
                  subheader={template.category.toUpperCase()}
                  action={
                    <Stack direction="row" spacing={1}>
                      <Chip
                        label={template.schedule?.toUpperCase() || 'ON-DEMAND'}
                        size="small"
                        color={template.isActive ? 'success' : 'default'}
                      />
                    </Stack>
                  }
                />
                <CardContent>
                  <Typography variant="body2" color="textSecondary" paragraph>
                    {template.description}
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="textSecondary">
                      Format: {template.format.toUpperCase()}
                    </Typography>
                    {template.lastGenerated && (
                      <Typography variant="caption" color="textSecondary" display="block">
                        Last: {new Date(template.lastGenerated).toLocaleDateString()}
                      </Typography>
                    )}
                  </Box>

                  <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<Add />}
                      onClick={() => {
                        setReportForm(prev => ({ ...prev, templateId: template.id }));
                        setReportDialogOpen(true);
                      }}
                      disabled={generating.includes(template.id)}
                    >
                      Generate
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<Visibility />}
                    >
                      Preview
                    </Button>
                  </Stack>

                  {template.recipients && template.recipients.length > 0 && (
                    <Typography variant="caption" color="textSecondary">
                      Recipients: {template.recipients.join(', ')}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={selectedTab} index={1}>
        {/* Generated Reports */}
        <Card>
          <CardHeader
            title="Generated Reports"
            action={
              <Stack direction="row" spacing={1}>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={loadGeneratedReports}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Stack>
            }
          />
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Report Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Format</TableCell>
                    <TableCell>Generated</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {generatedReports.map((report) => (
                    <TableRow key={report.id}>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {report.name}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            By: {report.generatedBy}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          {getTypeIcon(report.type)}
                          <Typography variant="body2">
                            {report.type}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          {getFormatIcon(report.format)}
                          <Typography variant="body2">
                            {report.format.toUpperCase()}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {new Date(report.generatedAt).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {report.size}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Chip
                            size="small"
                            label={report.status.toUpperCase()}
                            color={getStatusColor(report.status) as any}
                          />
                          {report.status === 'generating' && (
                            <LinearProgress sx={{ mt: 1, width: 100 }} />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          <Button
                            size="small"
                            startIcon={<Download />}
                            onClick={() => handleDownloadReport(report)}
                            disabled={report.status !== 'completed'}
                          >
                            Download
                          </Button>
                          <Button
                            size="small"
                            startIcon={<Email />}
                            onClick={() => handleEmailReport(report)}
                            disabled={report.status !== 'completed'}
                          >
                            Email
                          </Button>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={selectedTab} index={2}>
        {/* Analytics Dashboard */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Report Generation Trends" />
              <CardContent>
                <Alert severity="info">
                  Analytics charts showing:
                  <ul>
                    <li>Report generation frequency over time</li>
                    <li>Most popular report types</li>
                    <li>Usage by department/user</li>
                    <li>Peak generation times</li>
                  </ul>
                </Alert>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Data Insights" />
              <CardContent>
                <Alert severity="info">
                  Key insights and metrics:
                  <ul>
                    <li>Most accessed reports</li>
                    <li>Average report generation time</li>
                    <li>Storage utilization trends</li>
                    <li>User engagement metrics</li>
                  </ul>
                </Alert>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12}>
            <Card>
              <CardHeader title="System Performance" />
              <CardContent>
                <Alert severity="info">
                  Performance monitoring dashboard including:
                  <ul>
                    <li>Report generation queue status</li>
                    <li>System resource utilization</li>
                    <li>Error rates and failure analysis</li>
                    <li>Optimization recommendations</li>
                  </ul>
                </Alert>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Generate Report Dialog */}
      <Dialog 
        open={reportDialogOpen} 
        onClose={() => setReportDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Generate HACCP Report</DialogTitle>
        <DialogContent>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Report Template</InputLabel>
                  <Select
                    value={reportForm.templateId}
                    onChange={(e) => setReportForm(prev => ({ ...prev, templateId: e.target.value }))}
                    label="Report Template"
                  >
                    {reportTemplates.map((template) => (
                      <MenuItem key={template.id} value={template.id}>
                        <Box display="flex" alignItems="center" gap={1}>
                          {getTypeIcon(template.type)}
                          {template.name}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Format</InputLabel>
                  <Select
                    value={reportForm.format}
                    onChange={(e) => setReportForm(prev => ({ ...prev, format: e.target.value as any }))}
                    label="Format"
                  >
                    <MenuItem value="pdf">PDF</MenuItem>
                    <MenuItem value="excel">Excel</MenuItem>
                    <MenuItem value="csv">CSV</MenuItem>
                    <MenuItem value="html">HTML</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Report Name"
                  value={reportForm.name}
                  onChange={(e) => setReportForm(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Custom report name (optional)"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <MUIDatePicker
                  label="From Date"
                  value={reportForm.dateFrom}
                  onChange={(date) => setReportForm(prev => ({ ...prev, dateFrom: date || new Date() }))}
                  
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <MUIDatePicker
                  label="To Date"
                  value={reportForm.dateTo}
                  onChange={(date) => setReportForm(prev => ({ ...prev, dateTo: date || new Date() }))}
                  
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Report Options
                </Typography>
                <FormGroup row>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={reportForm.includeCharts}
                        onChange={(e) => setReportForm(prev => ({ ...prev, includeCharts: e.target.checked }))}
                      />
                    }
                    label="Include Charts"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={reportForm.includeTables}
                        onChange={(e) => setReportForm(prev => ({ ...prev, includeTables: e.target.checked }))}
                      />
                    }
                    label="Include Data Tables"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={reportForm.includeAnalysis}
                        onChange={(e) => setReportForm(prev => ({ ...prev, includeAnalysis: e.target.checked }))}
                      />
                    }
                    label="Include Analysis"
                  />
                </FormGroup>
              </Grid>

              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={reportForm.emailReport}
                      onChange={(e) => setReportForm(prev => ({ ...prev, emailReport: e.target.checked }))}
                    />
                  }
                  label="Email report when ready"
                />
                {reportForm.emailReport && (
                  <TextField
                    fullWidth
                    sx={{ mt: 2 }}
                    label="Email Recipients"
                    value={reportForm.emailRecipients}
                    onChange={(e) => setReportForm(prev => ({ ...prev, emailRecipients: e.target.value }))}
                    placeholder="email1@company.com, email2@company.com"
                    helperText="Comma-separated email addresses"
                  />
                )}
              </Grid>
            </Grid>
          </LocalizationProvider>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReportDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleGenerateReport}
            disabled={!reportForm.templateId}
          >
            Generate Report
          </Button>
        </DialogActions>
      </Dialog>

      {/* HACCP Plan Report */}
      {planReportDialogOpen && (
        <HACCPPlanReport />
      )}

      {/* Quick Actions */}
      <Box sx={{ position: 'fixed', bottom: 16, right: 16 }}>
        <Stack spacing={2}>
          <Button
            variant="contained"
            startIcon={<Description />}
            onClick={() => setPlanReportDialogOpen(true)}
            sx={{ borderRadius: 28 }}
          >
            HACCP Plan Report
          </Button>
        </Stack>
      </Box>
    </Box>
  );
};

export default HACCPReports;