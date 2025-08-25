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
  Tab
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  Business as BusinessIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

interface SWOTAnalysis {
  id: number;
  title: string;
  description?: string;
  analysis_date: string;
  is_active: boolean;
  strengths_count: number;
  weaknesses_count: number;
  opportunities_count: number;
  threats_count: number;
  actions_generated: number;
  completed_actions: number;
}

interface PESTELAnalysis {
  id: number;
  title: string;
  description?: string;
  analysis_date: string;
  is_active: boolean;
  political_count: number;
  economic_count: number;
  social_count: number;
  technological_count: number;
  environmental_count: number;
  legal_count: number;
  actions_generated: number;
  completed_actions: number;
}

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
  const [swotAnalyses, setSwotAnalyses] = useState<SWOTAnalysis[]>([]);
  const [pestelAnalyses, setPestelAnalyses] = useState<PESTELAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAnalysis, setEditingAnalysis] = useState<SWOTAnalysis | PESTELAnalysis | null>(null);
  const [analysisType, setAnalysisType] = useState<'swot' | 'pestel'>('swot');
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    analysis_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadAnalyses();
  }, []);

  const loadAnalyses = async () => {
    try {
      setLoading(true);
      setError(null);
      // Mock data for now - replace with actual API call
      const mockSWOTAnalyses: SWOTAnalysis[] = [
        {
          id: 1,
          title: 'Q1 2025 SWOT Analysis',
          description: 'Comprehensive SWOT analysis for Q1 2025 business performance',
          analysis_date: '2025-03-31',
          is_active: true,
          strengths_count: 8,
          weaknesses_count: 4,
          opportunities_count: 6,
          threats_count: 3,
          actions_generated: 15,
          completed_actions: 12
        }
      ];

      const mockPESTELAnalyses: PESTELAnalysis[] = [
        {
          id: 1,
          title: 'Q1 2025 PESTEL Analysis',
          description: 'PESTEL analysis for Q1 2025 external environment',
          analysis_date: '2025-03-31',
          is_active: true,
          political_count: 3,
          economic_count: 5,
          social_count: 4,
          technological_count: 6,
          environmental_count: 2,
          legal_count: 4,
          actions_generated: 12,
          completed_actions: 8
        }
      ];

      setSwotAnalyses(mockSWOTAnalyses);
      setPestelAnalyses(mockPESTELAnalyses);
    } catch (err) {
      setError('Failed to load analyses. Please try again.');
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
      analysis_date: new Date().toISOString().split('T')[0]
    });
    setDialogOpen(true);
  };

  const handleEditAnalysis = (analysis: SWOTAnalysis | PESTELAnalysis, type: 'swot' | 'pestel') => {
    setAnalysisType(type);
    setEditingAnalysis(analysis);
    setFormData({
      title: analysis.title,
      description: analysis.description || '',
      analysis_date: analysis.analysis_date
    });
    setDialogOpen(true);
  };

  const handleSaveAnalysis = async () => {
    try {
      // Mock save - replace with actual API call
      if (analysisType === 'swot') {
        if (editingAnalysis) {
          const updatedAnalyses = swotAnalyses.map(analysis =>
            analysis.id === editingAnalysis.id
              ? { ...analysis, ...formData }
              : analysis
          );
          setSwotAnalyses(updatedAnalyses);
        } else {
          const newAnalysis: SWOTAnalysis = {
            id: Math.max(...swotAnalyses.map(a => a.id)) + 1,
            ...formData,
            is_active: true,
            strengths_count: 0,
            weaknesses_count: 0,
            opportunities_count: 0,
            threats_count: 0,
            actions_generated: 0,
            completed_actions: 0
          };
          setSwotAnalyses([...swotAnalyses, newAnalysis]);
        }
      } else {
        if (editingAnalysis) {
          const updatedAnalyses = pestelAnalyses.map(analysis =>
            analysis.id === editingAnalysis.id
              ? { ...analysis, ...formData }
              : analysis
          );
          setPestelAnalyses(updatedAnalyses);
        } else {
          const newAnalysis: PESTELAnalysis = {
            id: Math.max(...pestelAnalyses.map(a => a.id)) + 1,
            ...formData,
            is_active: true,
            political_count: 0,
            economic_count: 0,
            social_count: 0,
            technological_count: 0,
            environmental_count: 0,
            legal_count: 0,
            actions_generated: 0,
            completed_actions: 0
          };
          setPestelAnalyses([...pestelAnalyses, newAnalysis]);
        }
      }

      setDialogOpen(false);
      if (onRefresh) onRefresh();
    } catch (err) {
      setError('Failed to save analysis. Please try again.');
      console.error('Error saving analysis:', err);
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
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
                          label={analysis.is_active ? 'Active' : 'Inactive'}
                          color={analysis.is_active ? 'success' : 'default'}
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
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Analysis Date"
                type="date"
                value={formData.analysis_date}
                onChange={(e) => setFormData({ ...formData, analysis_date: e.target.value })}
                margin="normal"
                InputLabelProps={{ shrink: true }}
              />
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
