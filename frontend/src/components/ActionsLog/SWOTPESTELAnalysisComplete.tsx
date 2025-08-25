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
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Business as BusinessIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  ExpandMore as ExpandMoreIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  Lightbulb as LightbulbIcon,
  Security as SecurityIcon
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

interface SWOTItem {
  id: number;
  analysis_id: number;
  category: 'strengths' | 'weaknesses' | 'opportunities' | 'threats';
  description: string;
  impact_level: 'high' | 'medium' | 'low';
  priority: 'high' | 'medium' | 'low';
  notes?: string;
  created_at: string;
}

interface PESTELItem {
  id: number;
  analysis_id: number;
  category: 'political' | 'economic' | 'social' | 'technological' | 'environmental' | 'legal';
  description: string;
  impact_level: 'high' | 'medium' | 'low';
  priority: 'high' | 'medium' | 'low';
  notes?: string;
  created_at: string;
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
  const [swotItems, setSwotItems] = useState<SWOTItem[]>([]);
  const [pestelItems, setPestelItems] = useState<PESTELItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [itemDialogOpen, setItemDialogOpen] = useState(false);
  const [editingAnalysis, setEditingAnalysis] = useState<SWOTAnalysis | PESTELAnalysis | null>(null);
  const [editingItem, setEditingItem] = useState<SWOTItem | PESTELItem | null>(null);
  const [analysisType, setAnalysisType] = useState<'swot' | 'pestel'>('swot');
  const [activeTab, setActiveTab] = useState(0);
  const [selectedAnalysis, setSelectedAnalysis] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    analysis_date: new Date().toISOString().split('T')[0]
  });
  const [itemFormData, setItemFormData] = useState({
    category: '',
    description: '',
    impact_level: 'medium',
    priority: 'medium',
    notes: ''
  });

  useEffect(() => {
    loadAnalyses();
  }, []);

  const loadAnalyses = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Mock data for SWOT analyses
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
        },
        {
          id: 2,
          title: 'Q4 2024 SWOT Analysis',
          description: 'End of year SWOT analysis for strategic planning',
          analysis_date: '2024-12-31',
          is_active: false,
          strengths_count: 6,
          weaknesses_count: 5,
          opportunities_count: 4,
          threats_count: 4,
          actions_generated: 12,
          completed_actions: 10
        }
      ];

      // Mock data for PESTEL analyses
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

      // Mock data for SWOT items
      const mockSWOTItems: SWOTItem[] = [
        {
          id: 1,
          analysis_id: 1,
          category: 'strengths',
          description: 'Strong brand reputation in dairy industry',
          impact_level: 'high',
          priority: 'high',
          notes: 'Key competitive advantage',
          created_at: '2025-01-15'
        },
        {
          id: 2,
          analysis_id: 1,
          category: 'strengths',
          description: 'Advanced food safety management system',
          impact_level: 'high',
          priority: 'high',
          notes: 'ISO 22000 certified',
          created_at: '2025-01-15'
        },
        {
          id: 3,
          analysis_id: 1,
          category: 'weaknesses',
          description: 'Limited geographic presence',
          impact_level: 'medium',
          priority: 'medium',
          notes: 'Focus on local markets',
          created_at: '2025-01-15'
        },
        {
          id: 4,
          analysis_id: 1,
          category: 'opportunities',
          description: 'Growing demand for organic dairy products',
          impact_level: 'high',
          priority: 'high',
          notes: 'Market expansion opportunity',
          created_at: '2025-01-15'
        },
        {
          id: 5,
          analysis_id: 1,
          category: 'threats',
          description: 'Increasing raw material costs',
          impact_level: 'high',
          priority: 'high',
          notes: 'Monitor supplier relationships',
          created_at: '2025-01-15'
        }
      ];

      // Mock data for PESTEL items
      const mockPESTELItems: PESTELItem[] = [
        {
          id: 1,
          analysis_id: 1,
          category: 'political',
          description: 'New food safety regulations',
          impact_level: 'high',
          priority: 'high',
          notes: 'Compliance requirements',
          created_at: '2025-01-15'
        },
        {
          id: 2,
          analysis_id: 1,
          category: 'economic',
          description: 'Inflation affecting production costs',
          impact_level: 'high',
          priority: 'high',
          notes: 'Price pressure',
          created_at: '2025-01-15'
        },
        {
          id: 3,
          analysis_id: 1,
          category: 'social',
          description: 'Growing health consciousness',
          impact_level: 'medium',
          priority: 'medium',
          notes: 'Product development opportunity',
          created_at: '2025-01-15'
        },
        {
          id: 4,
          analysis_id: 1,
          category: 'technological',
          description: 'Automation in dairy processing',
          impact_level: 'high',
          priority: 'high',
          notes: 'Investment opportunity',
          created_at: '2025-01-15'
        }
      ];

      setSwotAnalyses(mockSWOTAnalyses);
      setPestelAnalyses(mockPESTELAnalyses);
      setSwotItems(mockSWOTItems);
      setPestelItems(mockPESTELItems);
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
      setEditingAnalysis(null);
    } catch (err) {
      setError('Failed to save analysis. Please try again.');
      console.error('Error saving analysis:', err);
    }
  };

  const handleCreateItem = (analysisId: number, type: 'swot' | 'pestel') => {
    setAnalysisType(type);
    setSelectedAnalysis(analysisId);
    setEditingItem(null);
    setItemFormData({
      category: '',
      description: '',
      impact_level: 'medium',
      priority: 'medium',
      notes: ''
    });
    setItemDialogOpen(true);
  };

  const handleEditItem = (item: SWOTItem | PESTELItem, type: 'swot' | 'pestel') => {
    setAnalysisType(type);
    setEditingItem(item);
    setItemFormData({
      category: item.category,
      description: item.description,
      impact_level: item.impact_level,
      priority: item.priority,
      notes: item.notes || ''
    });
    setItemDialogOpen(true);
  };

  const handleSaveItem = async () => {
    try {
      if (analysisType === 'swot') {
        if (editingItem) {
          const updatedItems = swotItems.map(item =>
            item.id === editingItem.id
              ? {
                  ...item,
                  category: itemFormData.category as 'strengths' | 'weaknesses' | 'opportunities' | 'threats',
                  description: itemFormData.description,
                  impact_level: itemFormData.impact_level as 'high' | 'medium' | 'low',
                  priority: itemFormData.priority as 'high' | 'medium' | 'low',
                  notes: itemFormData.notes
                }
              : item
          );
          setSwotItems(updatedItems);
        } else {
          const newItem: SWOTItem = {
            id: Math.max(...swotItems.map(i => i.id)) + 1,
            analysis_id: selectedAnalysis!,
            category: itemFormData.category as 'strengths' | 'weaknesses' | 'opportunities' | 'threats',
            description: itemFormData.description,
            impact_level: itemFormData.impact_level as 'high' | 'medium' | 'low',
            priority: itemFormData.priority as 'high' | 'medium' | 'low',
            notes: itemFormData.notes,
            created_at: new Date().toISOString().split('T')[0]
          };
          setSwotItems([...swotItems, newItem]);
        }
      } else {
        if (editingItem) {
          const updatedItems = pestelItems.map(item =>
            item.id === editingItem.id
              ? {
                  ...item,
                  category: itemFormData.category as 'political' | 'economic' | 'social' | 'technological' | 'environmental' | 'legal',
                  description: itemFormData.description,
                  impact_level: itemFormData.impact_level as 'high' | 'medium' | 'low',
                  priority: itemFormData.priority as 'high' | 'medium' | 'low',
                  notes: itemFormData.notes
                }
              : item
          );
          setPestelItems(updatedItems);
        } else {
          const newItem: PESTELItem = {
            id: Math.max(...pestelItems.map(i => i.id)) + 1,
            analysis_id: selectedAnalysis!,
            category: itemFormData.category as 'political' | 'economic' | 'social' | 'technological' | 'environmental' | 'legal',
            description: itemFormData.description,
            impact_level: itemFormData.impact_level as 'high' | 'medium' | 'low',
            priority: itemFormData.priority as 'high' | 'medium' | 'low',
            notes: itemFormData.notes,
            created_at: new Date().toISOString().split('T')[0]
          };
          setPestelItems([...pestelItems, newItem]);
        }
      }
      setItemDialogOpen(false);
      setEditingItem(null);
      setSelectedAnalysis(null);
    } catch (err) {
      setError('Failed to save item. Please try again.');
      console.error('Error saving item:', err);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'strengths':
        return <CheckCircleIcon color="success" />;
      case 'weaknesses':
        return <WarningIcon color="warning" />;
      case 'opportunities':
        return <LightbulbIcon color="info" />;
      case 'threats':
        return <SecurityIcon color="error" />;
      default:
        return <BusinessIcon />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'strengths':
        return 'success';
      case 'weaknesses':
        return 'warning';
      case 'opportunities':
        return 'info';
      case 'threats':
        return 'error';
      case 'political':
        return 'primary';
      case 'economic':
        return 'secondary';
      case 'social':
        return 'success';
      case 'technological':
        return 'info';
      case 'environmental':
        return 'warning';
      case 'legal':
        return 'error';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
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
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="SWOT Analysis" />
          <Tab label="PESTEL Analysis" />
        </Tabs>
      </Box>

      <TabPanel value={activeTab} index={0}>
        <Box sx={{ mb: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5" component="h2">
              SWOT Analysis
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleCreateAnalysis('swot')}
            >
              New SWOT Analysis
            </Button>
          </Box>
          
          <Grid container spacing={3}>
            {swotAnalyses.map((analysis) => (
              <Grid item xs={12} md={6} key={analysis.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box>
                        <Typography variant="h6" component="h3">
                          {analysis.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {analysis.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Date: {analysis.analysis_date}
                        </Typography>
                      </Box>
                      <Box>
                        <Chip
                          label={analysis.is_active ? 'Active' : 'Inactive'}
                          color={analysis.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </Box>
                    </Box>
                    
                    <Grid container spacing={1} mb={2}>
                      <Grid item xs={3}>
                        <Box textAlign="center">
                          <Typography variant="h6" color="success.main">
                            {analysis.strengths_count}
                          </Typography>
                          <Typography variant="caption">Strengths</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={3}>
                        <Box textAlign="center">
                          <Typography variant="h6" color="warning.main">
                            {analysis.weaknesses_count}
                          </Typography>
                          <Typography variant="caption">Weaknesses</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={3}>
                        <Box textAlign="center">
                          <Typography variant="h6" color="info.main">
                            {analysis.opportunities_count}
                          </Typography>
                          <Typography variant="caption">Opportunities</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={3}>
                        <Box textAlign="center">
                          <Typography variant="h6" color="error.main">
                            {analysis.threats_count}
                          </Typography>
                          <Typography variant="caption">Threats</Typography>
                        </Box>
                      </Grid>
                    </Grid>
                    
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">
                        Actions: {analysis.completed_actions}/{analysis.actions_generated}
                      </Typography>
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditAnalysis(analysis, 'swot')}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => setSelectedAnalysis(analysis.id)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {selectedAnalysis && (
          <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Analysis Details
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => handleCreateItem(selectedAnalysis, 'swot')}
              >
                Add Item
              </Button>
            </Box>
            
            <Grid container spacing={2}>
              {(['strengths', 'weaknesses', 'opportunities', 'threats'] as const).map((category) => {
                const categoryItems = swotItems.filter(item => 
                  item.analysis_id === selectedAnalysis && item.category === category
                );
                
                return (
                  <Grid item xs={12} md={6} key={category}>
                    <Card>
                      <CardContent>
                        <Box display="flex" alignItems="center" mb={2}>
                          {getCategoryIcon(category)}
                          <Typography variant="h6" sx={{ ml: 1, textTransform: 'capitalize' }}>
                            {category}
                          </Typography>
                          <Chip
                            label={categoryItems.length}
                            size="small"
                            sx={{ ml: 'auto' }}
                          />
                        </Box>
                        
                        <List dense>
                          {categoryItems.map((item) => (
                            <ListItem key={item.id} sx={{ px: 0 }}>
                              <ListItemText
                                primary={item.description}
                                secondary={
                                  <Box>
                                    <Chip
                                      label={item.impact_level}
                                      size="small"
                                      color={getPriorityColor(item.impact_level)}
                                      sx={{ mr: 1 }}
                                    />
                                    <Chip
                                      label={item.priority}
                                      size="small"
                                      color={getPriorityColor(item.priority)}
                                    />
                                    {item.notes && (
                                      <Typography variant="caption" display="block" mt={1}>
                                        {item.notes}
                                      </Typography>
                                    )}
                                  </Box>
                                }
                              />
                              <ListItemSecondaryAction>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditItem(item, 'swot')}
                                >
                                  <EditIcon />
                                </IconButton>
                              </ListItemSecondaryAction>
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </Box>
        )}
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Box sx={{ mb: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5" component="h2">
              PESTEL Analysis
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleCreateAnalysis('pestel')}
            >
              New PESTEL Analysis
            </Button>
          </Box>
          
          <Grid container spacing={3}>
            {pestelAnalyses.map((analysis) => (
              <Grid item xs={12} md={6} key={analysis.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box>
                        <Typography variant="h6" component="h3">
                          {analysis.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {analysis.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Date: {analysis.analysis_date}
                        </Typography>
                      </Box>
                      <Box>
                        <Chip
                          label={analysis.is_active ? 'Active' : 'Inactive'}
                          color={analysis.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </Box>
                    </Box>
                    
                    <Grid container spacing={1} mb={2}>
                      <Grid item xs={2}>
                        <Box textAlign="center">
                          <Typography variant="h6" color="primary.main">
                            {analysis.political_count}
                          </Typography>
                          <Typography variant="caption">Political</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={2}>
                        <Box textAlign="center">
                          <Typography variant="h6" color="secondary.main">
                            {analysis.economic_count}
                          </Typography>
                          <Typography variant="caption">Economic</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={2}>
                        <Box textAlign="center">
                          <Typography variant="h6" color="success.main">
                            {analysis.social_count}
                          </Typography>
                          <Typography variant="caption">Social</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={2}>
                        <Box textAlign="center">
                          <Typography variant="h6" color="info.main">
                            {analysis.technological_count}
                          </Typography>
                          <Typography variant="caption">Technological</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={2}>
                        <Box textAlign="center">
                          <Typography variant="h6" color="warning.main">
                            {analysis.environmental_count}
                          </Typography>
                          <Typography variant="caption">Environmental</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={2}>
                        <Box textAlign="center">
                          <Typography variant="h6" color="error.main">
                            {analysis.legal_count}
                          </Typography>
                          <Typography variant="caption">Legal</Typography>
                        </Box>
                      </Grid>
                    </Grid>
                    
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">
                        Actions: {analysis.completed_actions}/{analysis.actions_generated}
                      </Typography>
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditAnalysis(analysis, 'pestel')}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => setSelectedAnalysis(analysis.id)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {selectedAnalysis && (
          <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Analysis Details
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => handleCreateItem(selectedAnalysis, 'pestel')}
              >
                Add Item
              </Button>
            </Box>
            
            <Grid container spacing={2}>
              {(['political', 'economic', 'social', 'technological', 'environmental', 'legal'] as const).map((category) => {
                const categoryItems = pestelItems.filter(item => 
                  item.analysis_id === selectedAnalysis && item.category === category
                );
                
                return (
                  <Grid item xs={12} md={6} key={category}>
                    <Card>
                      <CardContent>
                        <Box display="flex" alignItems="center" mb={2}>
                          <Chip
                            label={category}
                            color={getCategoryColor(category)}
                            size="small"
                          />
                          <Chip
                            label={categoryItems.length}
                            size="small"
                            sx={{ ml: 'auto' }}
                          />
                        </Box>
                        
                        <List dense>
                          {categoryItems.map((item) => (
                            <ListItem key={item.id} sx={{ px: 0 }}>
                              <ListItemText
                                primary={item.description}
                                secondary={
                                  <Box>
                                    <Chip
                                      label={item.impact_level}
                                      size="small"
                                      color={getPriorityColor(item.impact_level)}
                                      sx={{ mr: 1 }}
                                    />
                                    <Chip
                                      label={item.priority}
                                      size="small"
                                      color={getPriorityColor(item.priority)}
                                    />
                                    {item.notes && (
                                      <Typography variant="caption" display="block" mt={1}>
                                        {item.notes}
                                      </Typography>
                                    )}
                                  </Box>
                                }
                              />
                              <ListItemSecondaryAction>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditItem(item, 'pestel')}
                                >
                                  <EditIcon />
                                </IconButton>
                              </ListItemSecondaryAction>
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </Box>
        )}
      </TabPanel>

      {/* Analysis Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingAnalysis ? 'Edit Analysis' : 'New Analysis'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="normal"
            multiline
            rows={3}
          />
          <TextField
            fullWidth
            label="Analysis Date"
            type="date"
            value={formData.analysis_date}
            onChange={(e) => setFormData({ ...formData, analysis_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveAnalysis} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Item Dialog */}
      <Dialog open={itemDialogOpen} onClose={() => setItemDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingItem ? 'Edit Item' : 'New Item'}
        </DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal" required>
            <InputLabel>Category</InputLabel>
            <Select
              value={itemFormData.category}
              onChange={(e) => setItemFormData({ ...itemFormData, category: e.target.value })}
              label="Category"
            >
              {analysisType === 'swot' ? (
                <>
                  <MenuItem value="strengths">Strengths</MenuItem>
                  <MenuItem value="weaknesses">Weaknesses</MenuItem>
                  <MenuItem value="opportunities">Opportunities</MenuItem>
                  <MenuItem value="threats">Threats</MenuItem>
                </>
              ) : (
                <>
                  <MenuItem value="political">Political</MenuItem>
                  <MenuItem value="economic">Economic</MenuItem>
                  <MenuItem value="social">Social</MenuItem>
                  <MenuItem value="technological">Technological</MenuItem>
                  <MenuItem value="environmental">Environmental</MenuItem>
                  <MenuItem value="legal">Legal</MenuItem>
                </>
              )}
            </Select>
          </FormControl>
          
          <TextField
            fullWidth
            label="Description"
            value={itemFormData.description}
            onChange={(e) => setItemFormData({ ...itemFormData, description: e.target.value })}
            margin="normal"
            multiline
            rows={3}
            required
          />
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Impact Level</InputLabel>
            <Select
              value={itemFormData.impact_level}
              onChange={(e) => setItemFormData({ ...itemFormData, impact_level: e.target.value })}
              label="Impact Level"
            >
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Priority</InputLabel>
            <Select
              value={itemFormData.priority}
              onChange={(e) => setItemFormData({ ...itemFormData, priority: e.target.value })}
              label="Priority"
            >
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            fullWidth
            label="Notes"
            value={itemFormData.notes}
            onChange={(e) => setItemFormData({ ...itemFormData, notes: e.target.value })}
            margin="normal"
            multiline
            rows={2}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setItemDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveItem} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SWOTPESTELAnalysis;
