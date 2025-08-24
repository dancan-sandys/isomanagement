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
  Alert,
  CircularProgress,
  Paper,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Badge,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  Business as BusinessIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  Security as SecurityIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
  Link as LinkIcon,
  Assignment as AssignmentIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/material-icons';

import {
  SWOTAnalysisResponse,
  PESTELAnalysisResponse,
  SWOTAnalysisCreate,
  PESTELAnalysisCreate,
  AnalysisScope,
  ReviewFrequency,
  ISOComplianceMetrics,
  SWOTAnalytics,
  PESTELAnalytics
} from '../../types/swotPestel';
import SWOTPESTELApiService from '../../services/swotPestelApi';

interface SWOTPESTELAnalysisProps {
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
      id={`analysis-tabpanel-${index}`}
      aria-labelledby={`analysis-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const SWOTPESTELAnalysis: React.FC<SWOTPESTELAnalysisProps> = ({ onRefresh }) => {
  const [swotAnalyses, setSwotAnalyses] = useState<SWOTAnalysisResponse[]>([]);
  const [pestelAnalyses, setPestelAnalyses] = useState<PESTELAnalysisResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAnalysis, setEditingAnalysis] = useState<SWOTAnalysisResponse | PESTELAnalysisResponse | null>(null);
  const [analysisType, setAnalysisType] = useState<'swot' | 'pestel'>('swot');
  const [activeTab, setActiveTab] = useState(0);
  const [isoMetrics, setIsoMetrics] = useState<ISOComplianceMetrics | null>(null);
  const [swotAnalytics, setSwotAnalytics] = useState<SWOTAnalytics | null>(null);
  const [pestelAnalytics, setPestelAnalytics] = useState<PESTELAnalytics | null>(null);
  const [formData, setFormData] = useState<{
    title: string;
    description: string;
    analysis_date: string;
    scope: AnalysisScope;
    review_frequency: ReviewFrequency;
    iso_clause_reference: string[];
    compliance_notes: string;
  }>({
    title: '',
    description: '',
    analysis_date: new Date().toISOString().split('T')[0],
    scope: AnalysisScope.ORGANIZATION_WIDE,
    review_frequency: ReviewFrequency.ANNUALLY,
    iso_clause_reference: ['4.1'],
    compliance_notes: ''
  });

  useEffect(() => {
    loadAnalyses();
  }, []);

  const loadAnalyses = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load all data in parallel for better performance
      const [
        swotData,
        pestelData,
        isoMetricsData,
        swotAnalyticsData,
        pestelAnalyticsData
      ] = await Promise.all([
        SWOTPESTELApiService.getSWOTAnalyses(),
        SWOTPESTELApiService.getPESTELAnalyses(),
        SWOTPESTELApiService.getISOComplianceMetrics(),
        SWOTPESTELApiService.getSWOTAnalytics(),
        SWOTPESTELApiService.getPESTELAnalytics()
      ]);

      setSwotAnalyses(swotData);
      setPestelAnalyses(pestelData);
      setIsoMetrics(isoMetricsData);
      setSwotAnalytics(swotAnalyticsData);
      setPestelAnalytics(pestelAnalyticsData);
    } catch (err) {
      const errorMessage = SWOTPESTELApiService.handleApiError(err);
      setError(`Failed to load analyses: ${errorMessage}`);
      console.error('Error loading analyses:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAnalysis = (type: 'swot' | 'pestel') => {
    setAnalysisType(type);
    setEditingAnalysis(null);
    setFormData({
      title: '',
      description: '',
      analysis_date: new Date().toISOString().split('T')[0],
      scope: AnalysisScope.ORGANIZATION_WIDE,
      review_frequency: ReviewFrequency.ANNUALLY,
      iso_clause_reference: ['4.1'],
      compliance_notes: ''
    });
    setDialogOpen(true);
  };

  const handleEditAnalysis = (analysis: SWOTAnalysisResponse | PESTELAnalysisResponse, type: 'swot' | 'pestel') => {
    setAnalysisType(type);
    setEditingAnalysis(analysis);
    setFormData({
      title: analysis.title,
      description: analysis.description || '',
      analysis_date: analysis.analysis_date,
      scope: analysis.scope || AnalysisScope.ORGANIZATION_WIDE,
      review_frequency: analysis.review_frequency || ReviewFrequency.ANNUALLY,
      iso_clause_reference: analysis.iso_clause_reference || ['4.1'],
      compliance_notes: analysis.compliance_notes || ''
    });
    setDialogOpen(true);
  };

  const handleSaveAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);

      if (analysisType === 'swot') {
        if (editingAnalysis) {
          // Update existing SWOT analysis
          await SWOTPESTELApiService.updateSWOTAnalysis(editingAnalysis.id, formData);
        } else {
          // Create new SWOT analysis
          const createData: SWOTAnalysisCreate = {
            ...formData,
            is_active: true,
            risk_factors_identified: 0
          };
          await SWOTPESTELApiService.createSWOTAnalysis(createData);
        }
      } else {
        if (editingAnalysis) {
          // Update existing PESTEL analysis
          await SWOTPESTELApiService.updatePESTELAnalysis(editingAnalysis.id, formData);
        } else {
          // Create new PESTEL analysis
          const createData: PESTELAnalysisCreate = {
            ...formData,
            is_active: true,
            external_risk_factors: 0
          };
          await SWOTPESTELApiService.createPESTELAnalysis(createData);
        }
      }

      setDialogOpen(false);
      
      // Reload all data to reflect changes
      await loadAnalyses();
      
      if (onRefresh) onRefresh();
    } catch (err) {
      const errorMessage = SWOTPESTELApiService.handleApiError(err);
      setError(`Failed to save analysis: ${errorMessage}`);
      console.error('Error saving analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const filteredAnalyses = () => {
    switch (activeTab) {
      case 0: // All Analyses
        return [...swotAnalyses, ...pestelAnalyses];
      case 1: // SWOT
        return swotAnalyses;
      case 2: // PESTEL
        return pestelAnalyses;
      case 3: // Active
        return [...swotAnalyses, ...pestelAnalyses].filter(analysis => analysis.is_active);
      default:
        return [...swotAnalyses, ...pestelAnalyses];
    }
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
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h2">
            SWOT & PESTEL Analysis
          </Typography>
          <Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleCreateAnalysis('swot')}
              sx={{ mr: 1 }}
            >
              New SWOT
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleCreateAnalysis('pestel')}
            >
              New PESTEL
            </Button>
          </Box>
        </Box>

        {/* ISO Compliance Summary */}
        {isoMetrics && (
          <Paper sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <SecurityIcon sx={{ mr: 1 }} color="primary" />
              ISO 9001:2015 Compliance Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Clause 4.1 Compliance:
                  </Typography>
                  <Chip 
                    label={`${isoMetrics.clause_4_1_compliance_rate.toFixed(1)}%`}
                    color={isoMetrics.clause_4_1_compliance_rate >= 80 ? 'success' : 'warning'}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Risk Integration:
                  </Typography>
                  <Chip 
                    label={`${isoMetrics.risk_integration_rate.toFixed(1)}%`}
                    color={isoMetrics.risk_integration_rate >= 70 ? 'success' : 'warning'}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Overdue Reviews:
                  </Typography>
                  <Badge 
                    badgeContent={isoMetrics.overdue_reviews} 
                    color={isoMetrics.overdue_reviews > 0 ? 'error' : 'success'}
                    sx={{ ml: 1 }}
                  >
                    <ScheduleIcon color={isoMetrics.overdue_reviews > 0 ? 'error' : 'success'} />
                  </Badge>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Strategic Alignment:
                  </Typography>
                  <Chip 
                    label={`${isoMetrics.strategic_alignment_rate.toFixed(1)}%`}
                    color={isoMetrics.strategic_alignment_rate >= 70 ? 'success' : 'warning'}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

              {/* Analysis Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="analysis tabs">
            <Tab label="All Analyses" />
            <Tab label="SWOT" />
            <Tab label="PESTEL" />
            <Tab label="Active" />
            <Tab label="ISO Dashboard" />
            <Tab label="Analytics" />
          </Tabs>
        </Box>

        {/* All Analyses Tab */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            {filteredAnalyses().map((analysis) => {
              const isSWOT = 'strengths_count' in analysis;
              return (
                <Grid item xs={12} sm={6} md={4} key={analysis.id}>
                  <Card>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                        <Box display="flex" alignItems="center">
                          {isSWOT ? <BusinessIcon /> : <AssessmentIcon />}
                          <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                            {analysis.title}
                          </Typography>
                        </Box>
                        <Chip
                          label={isSWOT ? 'SWOT' : 'PESTEL'}
                          color={isSWOT ? 'primary' : 'secondary'}
                          size="small"
                        />
                      </Box>

                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {analysis.description}
                      </Typography>

                      {isSWOT ? (
                        <Box mb={2}>
                          <Grid container spacing={1}>
                            <Grid item xs={6}>
                              <Chip
                                label={`${analysis.strengths_count} Strengths`}
                                color="success"
                                size="small"
                                variant="outlined"
                              />
                            </Grid>
                            <Grid item xs={6}>
                              <Chip
                                label={`${analysis.weaknesses_count} Weaknesses`}
                                color="error"
                                size="small"
                                variant="outlined"
                              />
                            </Grid>
                            <Grid item xs={6}>
                              <Chip
                                label={`${analysis.opportunities_count} Opportunities`}
                                color="primary"
                                size="small"
                                variant="outlined"
                              />
                            </Grid>
                            <Grid item xs={6}>
                              <Chip
                                label={`${analysis.threats_count} Threats`}
                                color="warning"
                                size="small"
                                variant="outlined"
                              />
                            </Grid>
                          </Grid>
                        </Box>
                      ) : (
                        <Box mb={2}>
                          <Grid container spacing={1}>
                            <Grid item xs={4}>
                              <Chip
                                label={`${analysis.political_count} Political`}
                                color="error"
                                size="small"
                                variant="outlined"
                              />
                            </Grid>
                            <Grid item xs={4}>
                              <Chip
                                label={`${analysis.economic_count} Economic`}
                                color="warning"
                                size="small"
                                variant="outlined"
                              />
                            </Grid>
                            <Grid item xs={4}>
                              <Chip
                                label={`${analysis.social_count} Social`}
                                color="info"
                                size="small"
                                variant="outlined"
                              />
                            </Grid>
                            <Grid item xs={4}>
                              <Chip
                                label={`${analysis.technological_count} Tech`}
                                color="primary"
                                size="small"
                                variant="outlined"
                              />
                            </Grid>
                            <Grid item xs={4}>
                              <Chip
                                label={`${analysis.environmental_count} Env`}
                                color="success"
                                size="small"
                                variant="outlined"
                              />
                            </Grid>
                            <Grid item xs={4}>
                              <Chip
                                label={`${analysis.legal_count} Legal`}
                                color="secondary"
                                size="small"
                                variant="outlined"
                              />
                            </Grid>
                          </Grid>
                        </Box>
                      )}

                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Chip
                          label={`${analysis.completed_actions}/${analysis.actions_generated} actions`}
                          size="small"
                          color={analysis.completed_actions === analysis.actions_generated ? 'success' : 'warning'}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {new Date(analysis.analysis_date).toLocaleDateString()}
                        </Typography>
                      </Box>

                      {/* ISO Compliance Indicators */}
                      <Box sx={{ mb: 1 }}>
                        <Grid container spacing={1}>
                          <Grid item xs={6}>
                            <Tooltip title="Strategic Context Defined">
                              <Chip
                                label="Context"
                                size="small"
                                color={analysis.strategic_context ? 'success' : 'warning'}
                                icon={<SecurityIcon />}
                                variant="outlined"
                              />
                            </Tooltip>
                          </Grid>
                          <Grid item xs={6}>
                            <Tooltip title="Risk Assessment Linked">
                              <Chip
                                label="Risk"
                                size="small"
                                color={analysis.risk_assessment_id ? 'success' : 'default'}
                                icon={<LinkIcon />}
                                variant="outlined"
                              />
                            </Tooltip>
                          </Grid>
                        </Grid>
                      </Box>

                      {/* Review Schedule Indicator */}
                      {analysis.next_review_date && (
                        <Box sx={{ mb: 1 }}>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center' }}>
                            <ScheduleIcon sx={{ fontSize: 16, mr: 0.5 }} />
                            Next Review: {new Date(analysis.next_review_date).toLocaleDateString()}
                          </Typography>
                        </Box>
                      )}

                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <IconButton
                            size="small"
                            onClick={() => handleEditAnalysis(analysis, isSWOT ? 'swot' : 'pestel')}
                            color="primary"
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton size="small" color="info">
                            <VisibilityIcon />
                          </IconButton>
                          <Tooltip title="ISO Compliance Review">
                            <IconButton size="small" color="secondary">
                              <AssignmentIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip
                            label={analysis.scope || 'Organization'}
                            size="small"
                            variant="outlined"
                          />
                          <Chip
                            label={analysis.is_active ? 'Active' : 'Inactive'}
                            color={analysis.is_active ? 'success' : 'default'}
                            size="small"
                          />
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </TabPanel>

        {/* SWOT Tab */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            {swotAnalyses.map((analysis) => (
              <Grid item xs={12} sm={6} md={4} key={analysis.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        <BusinessIcon />
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {analysis.title}
                        </Typography>
                      </Box>
                      <Chip label="SWOT" color="primary" size="small" />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {analysis.description}
                    </Typography>

                    <Box mb={2}>
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Chip
                            label={`${analysis.strengths_count} Strengths`}
                            color="success"
                            size="small"
                            variant="outlined"
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <Chip
                            label={`${analysis.weaknesses_count} Weaknesses`}
                            color="error"
                            size="small"
                            variant="outlined"
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <Chip
                            label={`${analysis.opportunities_count} Opportunities`}
                            color="primary"
                            size="small"
                            variant="outlined"
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <Chip
                            label={`${analysis.threats_count} Threats`}
                            color="warning"
                            size="small"
                            variant="outlined"
                          />
                        </Grid>
                      </Grid>
                    </Box>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditAnalysis(analysis, 'swot')}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="info">
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(analysis.analysis_date).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* PESTEL Tab */}
        <TabPanel value={activeTab} index={2}>
          <Grid container spacing={3}>
            {pestelAnalyses.map((analysis) => (
              <Grid item xs={12} sm={6} md={4} key={analysis.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        <AssessmentIcon />
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {analysis.title}
                        </Typography>
                      </Box>
                      <Chip label="PESTEL" color="secondary" size="small" />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {analysis.description}
                    </Typography>

                    <Box mb={2}>
                      <Grid container spacing={1}>
                        <Grid item xs={4}>
                          <Chip
                            label={`${analysis.political_count} Political`}
                            color="error"
                            size="small"
                            variant="outlined"
                          />
                        </Grid>
                        <Grid item xs={4}>
                          <Chip
                            label={`${analysis.economic_count} Economic`}
                            color="warning"
                            size="small"
                            variant="outlined"
                          />
                        </Grid>
                        <Grid item xs={4}>
                          <Chip
                            label={`${analysis.social_count} Social`}
                            color="info"
                            size="small"
                            variant="outlined"
                          />
                        </Grid>
                        <Grid item xs={4}>
                          <Chip
                            label={`${analysis.technological_count} Tech`}
                            color="primary"
                            size="small"
                            variant="outlined"
                          />
                        </Grid>
                        <Grid item xs={4}>
                          <Chip
                            label={`${analysis.environmental_count} Env`}
                            color="success"
                            size="small"
                            variant="outlined"
                          />
                        </Grid>
                        <Grid item xs={4}>
                          <Chip
                            label={`${analysis.legal_count} Legal`}
                            color="secondary"
                            size="small"
                            variant="outlined"
                          />
                        </Grid>
                      </Grid>
                    </Box>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditAnalysis(analysis, 'pestel')}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="info">
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(analysis.analysis_date).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Active Tab */}
        <TabPanel value={activeTab} index={3}>
          <Grid container spacing={3}>
            {filteredAnalyses().map((analysis) => {
              const isSWOT = 'strengths_count' in analysis;
              return (
                <Grid item xs={12} sm={6} md={4} key={analysis.id}>
                  <Card sx={{ border: '2px solid #4caf50' }}>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                        <Box display="flex" alignItems="center">
                          <CheckCircleIcon color="success" />
                          <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                            {analysis.title}
                          </Typography>
                        </Box>
                        <Chip
                          label="Active"
                          color="success"
                          size="small"
                        />
                      </Box>

                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {analysis.description}
                      </Typography>

                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <IconButton
                            size="small"
                            onClick={() => handleEditAnalysis(analysis, isSWOT ? 'swot' : 'pestel')}
                            color="primary"
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton size="small" color="info">
                            <VisibilityIcon />
                          </IconButton>
                        </Box>
                        <Chip
                          label={isSWOT ? 'SWOT' : 'PESTEL'}
                          color={isSWOT ? 'primary' : 'secondary'}
                          size="small"
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </TabPanel>

        {/* ISO Dashboard Tab */}
        <TabPanel value={activeTab} index={4}>
          <Grid container spacing={3}>
            {/* ISO Compliance Overview */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <SecurityIcon sx={{ mr: 1 }} color="primary" />
                    ISO 9001:2015 Compliance Dashboard
                  </Typography>
                  
                  {isoMetrics && (
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={12} md={6}>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" gutterBottom>
                            Clause 4.1 Compliance Rate
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={isoMetrics.clause_4_1_compliance_rate} 
                            color={isoMetrics.clause_4_1_compliance_rate >= 80 ? 'success' : 'warning'}
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {isoMetrics.clause_4_1_compliance_rate.toFixed(1)}% - Understanding organizational context
                          </Typography>
                        </Box>
                      </Grid>

                      <Grid item xs={12} md={6}>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" gutterBottom>
                            Risk Integration Rate
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={isoMetrics.risk_integration_rate} 
                            color={isoMetrics.risk_integration_rate >= 70 ? 'success' : 'warning'}
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {isoMetrics.risk_integration_rate.toFixed(1)}% - Risk-based thinking integration
                          </Typography>
                        </Box>
                      </Grid>

                      <Grid item xs={12} md={6}>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" gutterBottom>
                            Strategic Alignment Rate
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={isoMetrics.strategic_alignment_rate} 
                            color={isoMetrics.strategic_alignment_rate >= 70 ? 'success' : 'warning'}
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {isoMetrics.strategic_alignment_rate.toFixed(1)}% - Strategic objectives alignment
                          </Typography>
                        </Box>
                      </Grid>

                      <Grid item xs={12} md={6}>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" gutterBottom>
                            Documentation Evidence Rate
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={isoMetrics.documented_evidence_rate} 
                            color={isoMetrics.documented_evidence_rate >= 80 ? 'success' : 'warning'}
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {isoMetrics.documented_evidence_rate.toFixed(1)}% - Evidence documentation completeness
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  )}

                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Key ISO Requirements Status:
                    </Typography>
                    <Grid container spacing={1}>
                      <Grid item>
                        <Chip 
                          label="Context Understanding" 
                          color={isoMetrics && isoMetrics.clause_4_1_compliance_rate >= 80 ? 'success' : 'warning'}
                          size="small"
                        />
                      </Grid>
                      <Grid item>
                        <Chip 
                          label="Risk-based Thinking" 
                          color={isoMetrics && isoMetrics.risk_integration_rate >= 70 ? 'success' : 'warning'}
                          size="small"
                        />
                      </Grid>
                      <Grid item>
                        <Chip 
                          label="Continuous Monitoring" 
                          color={isoMetrics && isoMetrics.overdue_reviews === 0 ? 'success' : 'error'}
                          size="small"
                        />
                      </Grid>
                      <Grid item>
                        <Chip 
                          label="Documentation" 
                          color={isoMetrics && isoMetrics.documented_evidence_rate >= 80 ? 'success' : 'warning'}
                          size="small"
                        />
                      </Grid>
                    </Grid>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Action Items */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <WarningIcon sx={{ mr: 1 }} color="warning" />
                    Compliance Action Items
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    {isoMetrics && isoMetrics.overdue_reviews > 0 && (
                      <Alert severity="error" sx={{ mb: 1 }}>
                        {isoMetrics.overdue_reviews} analyses have overdue reviews
                      </Alert>
                    )}
                    {isoMetrics && isoMetrics.clause_4_1_compliance_rate < 80 && (
                      <Alert severity="warning" sx={{ mb: 1 }}>
                        ISO 9001:2015 Clause 4.1 compliance below 80%
                      </Alert>
                    )}
                    {isoMetrics && isoMetrics.risk_integration_rate < 70 && (
                      <Alert severity="info" sx={{ mb: 1 }}>
                        Consider improving risk integration rate
                      </Alert>
                    )}
                    {(!isoMetrics || (isoMetrics.overdue_reviews === 0 && isoMetrics.clause_4_1_compliance_rate >= 80 && isoMetrics.risk_integration_rate >= 70)) && (
                      <Alert severity="success">
                        All compliance metrics are meeting targets
                      </Alert>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* ISO Resources */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    ISO 9001:2015 Resources
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<AssignmentIcon />}
                      sx={{ mb: 1 }}
                    >
                      Generate Management Review Input
                    </Button>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<TrendingUpIcon />}
                      sx={{ mb: 1 }}
                    >
                      Strategic Context Assessment
                    </Button>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<SecurityIcon />}
                    >
                      ISO Compliance Report
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Analytics Tab */}
        <TabPanel value={activeTab} index={5}>
          <Grid container spacing={3}>
            {/* SWOT Analytics */}
            {swotAnalytics && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                      <BusinessIcon sx={{ mr: 1 }} color="primary" />
                      SWOT Analytics
                    </Typography>
                    
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={6}>
                        <Typography variant="h4" color="primary">{swotAnalytics.total_analyses}</Typography>
                        <Typography variant="caption">Total Analyses</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="h4" color="success.main">{swotAnalytics.active_analyses}</Typography>
                        <Typography variant="caption">Active Analyses</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="h4" color="info.main">{swotAnalytics.total_items}</Typography>
                        <Typography variant="caption">Total Items</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="h4" color="secondary.main">{swotAnalytics.completion_rate.toFixed(1)}%</Typography>
                        <Typography variant="caption">Completion Rate</Typography>
                      </Grid>
                    </Grid>

                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>Item Distribution:</Typography>
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Chip label={`${swotAnalytics.strengths_count} Strengths`} color="success" size="small" />
                        </Grid>
                        <Grid item xs={6}>
                          <Chip label={`${swotAnalytics.weaknesses_count} Weaknesses`} color="error" size="small" />
                        </Grid>
                        <Grid item xs={6}>
                          <Chip label={`${swotAnalytics.opportunities_count} Opportunities`} color="primary" size="small" />
                        </Grid>
                        <Grid item xs={6}>
                          <Chip label={`${swotAnalytics.threats_count} Threats`} color="warning" size="small" />
                        </Grid>
                      </Grid>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* PESTEL Analytics */}
            {pestelAnalytics && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                      <AssessmentIcon sx={{ mr: 1 }} color="secondary" />
                      PESTEL Analytics
                    </Typography>
                    
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={6}>
                        <Typography variant="h4" color="secondary">{pestelAnalytics.total_analyses}</Typography>
                        <Typography variant="caption">Total Analyses</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="h4" color="success.main">{pestelAnalytics.active_analyses}</Typography>
                        <Typography variant="caption">Active Analyses</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="h4" color="info.main">{pestelAnalytics.total_items}</Typography>
                        <Typography variant="caption">Total Items</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="h4" color="secondary.main">{pestelAnalytics.completion_rate.toFixed(1)}%</Typography>
                        <Typography variant="caption">Completion Rate</Typography>
                      </Grid>
                    </Grid>

                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>Factor Distribution:</Typography>
                      <Grid container spacing={1}>
                        <Grid item xs={4}>
                          <Chip label={`${pestelAnalytics.political_count} Political`} color="error" size="small" />
                        </Grid>
                        <Grid item xs={4}>
                          <Chip label={`${pestelAnalytics.economic_count} Economic`} color="warning" size="small" />
                        </Grid>
                        <Grid item xs={4}>
                          <Chip label={`${pestelAnalytics.social_count} Social`} color="info" size="small" />
                        </Grid>
                        <Grid item xs={4}>
                          <Chip label={`${pestelAnalytics.technological_count} Tech`} color="primary" size="small" />
                        </Grid>
                        <Grid item xs={4}>
                          <Chip label={`${pestelAnalytics.environmental_count} Env`} color="success" size="small" />
                        </Grid>
                        <Grid item xs={4}>
                          <Chip label={`${pestelAnalytics.legal_count} Legal`} color="secondary" size="small" />
                        </Grid>
                      </Grid>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        </TabPanel>
      </Paper>

      {/* Create/Edit Analysis Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingAnalysis ? `Edit ${analysisType.toUpperCase()} Analysis` : `Create New ${analysisType.toUpperCase()} Analysis`}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Analysis Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                margin="normal"
                required
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
              <TextField
                fullWidth
                label="Analysis Date"
                type="date"
                value={formData.analysis_date}
                onChange={(e) => setFormData({ ...formData, analysis_date: e.target.value })}
                margin="normal"
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Analysis Scope</InputLabel>
                <Select
                  value={formData.scope}
                  label="Analysis Scope"
                  onChange={(e) => setFormData({ ...formData, scope: e.target.value as AnalysisScope })}
                >
                  <MenuItem value={AnalysisScope.ORGANIZATION_WIDE}>Organization Wide</MenuItem>
                  <MenuItem value={AnalysisScope.DEPARTMENT}>Department</MenuItem>
                  <MenuItem value={AnalysisScope.PROCESS}>Process</MenuItem>
                  <MenuItem value={AnalysisScope.PROJECT}>Project</MenuItem>
                  <MenuItem value={AnalysisScope.PRODUCT_SERVICE}>Product/Service</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Review Frequency</InputLabel>
                <Select
                  value={formData.review_frequency}
                  label="Review Frequency"
                  onChange={(e) => setFormData({ ...formData, review_frequency: e.target.value as ReviewFrequency })}
                >
                  <MenuItem value={ReviewFrequency.MONTHLY}>Monthly</MenuItem>
                  <MenuItem value={ReviewFrequency.QUARTERLY}>Quarterly</MenuItem>
                  <MenuItem value={ReviewFrequency.SEMI_ANNUALLY}>Semi-Annually</MenuItem>
                  <MenuItem value={ReviewFrequency.ANNUALLY}>Annually</MenuItem>
                  <MenuItem value={ReviewFrequency.AS_NEEDED}>As Needed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="ISO Clause References"
                value={formData.iso_clause_reference.join(', ')}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  iso_clause_reference: e.target.value.split(',').map(s => s.trim()) 
                })}
                margin="normal"
                placeholder="4.1, 6.1, 9.1"
                helperText="Comma-separated ISO clause references"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="ISO Compliance Notes"
                value={formData.compliance_notes}
                onChange={(e) => setFormData({ ...formData, compliance_notes: e.target.value })}
                margin="normal"
                multiline
                rows={2}
                placeholder="Notes on ISO 9001:2015 compliance requirements and context understanding"
              />
            </Grid>
            
            {/* ISO Information Section */}
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center' }}>
                    <SecurityIcon sx={{ mr: 1 }} color="primary" />
                    ISO 9001:2015 Clause 4.1 Requirements
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    <strong>Understanding the organization and its context:</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary" component="div">
                    <ul>
                      <li>Determine external and internal issues relevant to purpose and strategic direction</li>
                      <li>Monitor and review information about these external and internal issues</li>
                      <li>Consider the impact of these issues on the intended results of the QMS</li>
                    </ul>
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    This {analysisType.toUpperCase()} analysis contributes to understanding organizational context 
                    by identifying {analysisType === 'swot' ? 'internal strengths/weaknesses and external opportunities/threats' : 'external macro-environmental factors'}.
                  </Typography>
                </AccordionDetails>
              </Accordion>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveAnalysis}>
            {editingAnalysis ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SWOTPESTELAnalysis;
