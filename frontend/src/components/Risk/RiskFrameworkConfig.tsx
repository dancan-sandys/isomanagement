import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Alert,
  Chip,
  Divider,
  Stack,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Slider,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  CircularProgress,
  useTheme,
} from '@mui/material';
import {
  ExpandMore,
  Info,
  Save,
  Settings,
  Security,
  Assessment,
  BusinessCenter,
  Gavel,
  Timeline,
  TrendingUp,
  Edit,
  Delete,
  Add,
  CheckCircle,
  Warning,
  Help,
} from '@mui/icons-material';
import riskAPI, { RiskFramework, RiskContext } from '../../services/riskAPI';
import { ISO_STATUS_COLORS, PROFESSIONAL_COLORS } from '../../theme/designSystem';

// ============================================================================
// RISK FRAMEWORK CONFIGURATION INTERFACES
// ============================================================================

interface RiskFrameworkConfigProps {
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

interface RiskCriterion {
  id: string;
  name: string;
  description: string;
  type: 'qualitative' | 'quantitative';
  scale: string[];
  threshold_values: number[];
}

interface TreatmentStrategy {
  id: string;
  name: string;
  description: string;
  applicability: string;
  cost_effectiveness: number;
  implementation_complexity: number;
}

// ============================================================================
// TAB PANEL COMPONENT
// ============================================================================

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`risk-framework-tabpanel-${index}`}
      aria-labelledby={`risk-framework-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

const RiskFrameworkConfig: React.FC<RiskFrameworkConfigProps> = ({
  open,
  onClose,
  onSaved,
}) => {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  
  // Framework data states
  const [framework, setFramework] = useState<Partial<RiskFramework>>({
    policy_statement: '',
    risk_appetite_statement: '',
    risk_tolerance_levels: {},
    risk_criteria: {},
    risk_assessment_methodology: '',
    risk_treatment_strategies: {},
    monitoring_review_frequency: 'quarterly',
    communication_plan: '',
    review_cycle: 'annually',
  });

  const [context, setContext] = useState<Partial<RiskContext>>({
    organizational_context: '',
    external_context: '',
    internal_context: '',
    risk_management_context: '',
    stakeholder_analysis: {},
    risk_criteria: {},
    review_frequency: 'quarterly',
  });

  const [riskCriteria, setRiskCriteria] = useState<RiskCriterion[]>([
    {
      id: 'financial_impact',
      name: 'Financial Impact',
      description: 'Potential financial loss or cost',
      type: 'quantitative',
      scale: ['< $10K', '$10K-$50K', '$50K-$100K', '$100K-$500K', '> $500K'],
      threshold_values: [10000, 50000, 100000, 500000, 1000000],
    },
    {
      id: 'operational_impact',
      name: 'Operational Impact',
      description: 'Disruption to business operations',
      type: 'qualitative',
      scale: ['Minimal', 'Minor', 'Moderate', 'Major', 'Severe'],
      threshold_values: [1, 2, 3, 4, 5],
    },
    {
      id: 'reputational_impact',
      name: 'Reputational Impact',
      description: 'Impact on organization reputation',
      type: 'qualitative',
      scale: ['Negligible', 'Limited', 'Significant', 'Serious', 'Critical'],
      threshold_values: [1, 2, 3, 4, 5],
    },
  ]);

  const [treatmentStrategies, setTreatmentStrategies] = useState<TreatmentStrategy[]>([
    {
      id: 'avoid',
      name: 'Avoid',
      description: 'Eliminate the risk by not engaging in the activity',
      applicability: 'High-risk activities that can be discontinued',
      cost_effectiveness: 5,
      implementation_complexity: 2,
    },
    {
      id: 'transfer',
      name: 'Transfer',
      description: 'Share or shift risk to another party',
      applicability: 'Risks that can be insured or outsourced',
      cost_effectiveness: 4,
      implementation_complexity: 3,
    },
    {
      id: 'mitigate',
      name: 'Mitigate',
      description: 'Reduce likelihood or impact through controls',
      applicability: 'Most operational and process risks',
      cost_effectiveness: 3,
      implementation_complexity: 4,
    },
    {
      id: 'accept',
      name: 'Accept',
      description: 'Accept the risk and manage through monitoring',
      applicability: 'Low-level risks within tolerance',
      cost_effectiveness: 5,
      implementation_complexity: 1,
    },
  ]);

  // ============================================================================
  // EFFECTS & DATA LOADING
  // ============================================================================

  useEffect(() => {
    if (open) {
      loadExistingFramework();
    }
  }, [open]);

  const loadExistingFramework = async () => {
    try {
      setLoading(true);
      
      // Load framework and context in parallel
      const [frameworkResponse, contextResponse] = await Promise.all([
        riskAPI.getFramework(),
        riskAPI.getContext(),
      ]);

      if (frameworkResponse.success && frameworkResponse.data) {
        setFramework(frameworkResponse.data);
      }

      if (contextResponse.success && contextResponse.data) {
        setContext(contextResponse.data);
      }
    } catch (error) {
      console.error('Failed to load existing framework:', error);
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const updateFramework = (field: keyof RiskFramework, value: any) => {
    setFramework(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const updateContext = (field: keyof RiskContext, value: any) => {
    setContext(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const addRiskCriterion = () => {
    const newCriterion: RiskCriterion = {
      id: `criterion_${Date.now()}`,
      name: '',
      description: '',
      type: 'qualitative',
      scale: ['Low', 'Medium', 'High'],
      threshold_values: [1, 2, 3],
    };
    setRiskCriteria(prev => [...prev, newCriterion]);
  };

  const updateRiskCriterion = (index: number, field: keyof RiskCriterion, value: any) => {
    setRiskCriteria(prev => prev.map((criterion, i) => 
      i === index ? { ...criterion, [field]: value } : criterion
    ));
  };

  const removeRiskCriterion = (index: number) => {
    setRiskCriteria(prev => prev.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    try {
      setSaving(true);

      // Prepare framework data with risk criteria and treatment strategies
      const frameworkData: Partial<RiskFramework> = {
        ...framework,
        risk_criteria: {
          criteria: riskCriteria,
          matrix_configuration: {
            severity_levels: 5,
            likelihood_levels: 5,
            detectability_levels: 5,
          },
        },
        risk_treatment_strategies: {
          strategies: treatmentStrategies,
          selection_criteria: 'cost_effectiveness_and_feasibility',
        },
      };

      // Save framework and context
      const [frameworkResponse, contextResponse] = await Promise.all([
        riskAPI.createFramework(frameworkData),
        riskAPI.createContext(context),
      ]);

      if (frameworkResponse.success && contextResponse.success) {
        onSaved();
      }
    } catch (error) {
      console.error('Failed to save framework:', error);
    } finally {
      setSaving(false);
    }
  };

  // ============================================================================
  // RENDER POLICY TAB
  // ============================================================================

  const renderPolicyTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Alert severity="info" icon={<Info />}>
          <Typography variant="subtitle2" fontWeight={600}>
            ISO 31000:2018 Risk Management Policy
          </Typography>
          <Typography variant="body2">
            Establish the organization's intentions and direction related to risk management.
            The policy should be aligned with organizational context and provide framework for setting objectives.
          </Typography>
        </Alert>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Risk Management Policy Statement
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={6}
              placeholder="Define the organization's commitment to risk management, including objectives, principles, and accountability..."
              value={framework.policy_statement}
              onChange={(e) => updateFramework('policy_statement', e.target.value)}
              helperText="This policy statement should be approved by top management and communicated throughout the organization."
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Risk Appetite Statement
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              placeholder="Define the level of risk the organization is willing to accept in pursuit of its objectives..."
              value={framework.risk_appetite_statement}
              onChange={(e) => updateFramework('risk_appetite_statement', e.target.value)}
              helperText="Risk appetite should be expressed in measurable terms where possible."
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Communication Plan
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              placeholder="Describe how risk information will be communicated internally and externally..."
              value={framework.communication_plan}
              onChange={(e) => updateFramework('communication_plan', e.target.value)}
              helperText="Include stakeholder engagement and reporting requirements."
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Review and Update Schedule
            </Typography>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Review Cycle</InputLabel>
                  <Select
                    value={framework.review_cycle}
                    onChange={(e) => updateFramework('review_cycle', e.target.value)}
                    label="Review Cycle"
                  >
                    <MenuItem value="quarterly">Quarterly</MenuItem>
                    <MenuItem value="semi_annually">Semi-Annually</MenuItem>
                    <MenuItem value="annually">Annually</MenuItem>
                    <MenuItem value="bi_annually">Bi-Annually</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Monitoring Frequency</InputLabel>
                  <Select
                    value={framework.monitoring_review_frequency}
                    onChange={(e) => updateFramework('monitoring_review_frequency', e.target.value)}
                    label="Monitoring Frequency"
                  >
                    <MenuItem value="monthly">Monthly</MenuItem>
                    <MenuItem value="quarterly">Quarterly</MenuItem>
                    <MenuItem value="semi_annually">Semi-Annually</MenuItem>
                    <MenuItem value="annually">Annually</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  type="date"
                  label="Next Review Date"
                  InputLabelProps={{ shrink: true }}
                  value={framework.next_review_date ? framework.next_review_date.split('T')[0] : ''}
                  onChange={(e) => updateFramework('next_review_date', e.target.value)}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // ============================================================================
  // RENDER CONTEXT TAB
  // ============================================================================

  const renderContextTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Alert severity="info" icon={<Info />}>
          <Typography variant="subtitle2" fontWeight={600}>
            ISO 31000:2018 Organizational Context
          </Typography>
          <Typography variant="body2">
            Establish the external and internal parameters within which the organization manages risk.
            This context sets the scope and risk criteria for the risk management process.
          </Typography>
        </Alert>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Organizational Context
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              placeholder="Describe the organization's purpose, vision, mission, and strategic objectives relevant to risk management..."
              value={context.organizational_context}
              onChange={(e) => updateContext('organizational_context', e.target.value)}
              helperText="Include the organization's governance, structure, roles, and accountabilities."
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              External Context
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={5}
              placeholder="Define the external environment in which the organization operates (regulatory, technological, competitive, market, cultural, social, economic factors)..."
              value={context.external_context}
              onChange={(e) => updateContext('external_context', e.target.value)}
              helperText="Consider relationships with external stakeholders and their perceptions and values."
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Internal Context
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={5}
              placeholder="Define the internal environment (governance, organizational structure, roles, accountabilities, policies, objectives, strategies, capabilities, knowledge, resources, relationships, information systems, processes, culture)..."
              value={context.internal_context}
              onChange={(e) => updateContext('internal_context', e.target.value)}
              helperText="Include capabilities in terms of resources and knowledge."
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Risk Management Context
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              placeholder="Specify the goals, strategies, scope, and parameters of the activities where risk management is being applied..."
              value={context.risk_management_context}
              onChange={(e) => updateContext('risk_management_context', e.target.value)}
              helperText="Define the relationship between the risk management project and other projects or parts of the organization."
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Review Settings
            </Typography>
            <FormControl fullWidth>
              <InputLabel>Context Review Frequency</InputLabel>
              <Select
                value={context.review_frequency}
                onChange={(e) => updateContext('review_frequency', e.target.value)}
                label="Context Review Frequency"
              >
                <MenuItem value="quarterly">Quarterly</MenuItem>
                <MenuItem value="semi_annually">Semi-Annually</MenuItem>
                <MenuItem value="annually">Annually</MenuItem>
                <MenuItem value="bi_annually">Bi-Annually</MenuItem>
              </Select>
            </FormControl>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // ============================================================================
  // RENDER CRITERIA TAB
  // ============================================================================

  const renderCriteriaTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Alert severity="info" icon={<Info />}>
          <Typography variant="subtitle2" fontWeight={600}>
            ISO 31000:2018 Risk Criteria
          </Typography>
          <Typography variant="body2">
            Define the terms of reference against which the significance of risk is evaluated.
            Risk criteria should be aligned with the risk management framework and customized to specific circumstances.
          </Typography>
        </Alert>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Risk Assessment Criteria
              </Typography>
              <Button
                variant="outlined"
                startIcon={<Add />}
                onClick={addRiskCriterion}
              >
                Add Criterion
              </Button>
            </Box>

            {riskCriteria.map((criterion, index) => (
              <Accordion key={criterion.id} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="subtitle1" fontWeight={600}>
                    {criterion.name || `Criterion ${index + 1}`}
                  </Typography>
                  <Chip 
                    label={criterion.type} 
                    size="small" 
                    sx={{ ml: 2 }}
                    color={criterion.type === 'quantitative' ? 'primary' : 'secondary'}
                  />
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Criterion Name"
                        value={criterion.name}
                        onChange={(e) => updateRiskCriterion(index, 'name', e.target.value)}
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <FormControl fullWidth>
                        <InputLabel>Type</InputLabel>
                        <Select
                          value={criterion.type}
                          onChange={(e) => updateRiskCriterion(index, 'type', e.target.value)}
                          label="Type"
                        >
                          <MenuItem value="qualitative">Qualitative</MenuItem>
                          <MenuItem value="quantitative">Quantitative</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Box display="flex" justifyContent="flex-end">
                        <IconButton
                          color="error"
                          onClick={() => removeRiskCriterion(index)}
                        >
                          <Delete />
                        </IconButton>
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        multiline
                        rows={2}
                        label="Description"
                        value={criterion.description}
                        onChange={(e) => updateRiskCriterion(index, 'description', e.target.value)}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="body2" gutterBottom>
                        Scale Definition (Level 1 to 5):
                      </Typography>
                      <Grid container spacing={1}>
                        {criterion.scale.map((level, levelIndex) => (
                          <Grid item xs={12} md={2.4} key={levelIndex}>
                            <TextField
                              fullWidth
                              size="small"
                              label={`Level ${levelIndex + 1}`}
                              value={level}
                              onChange={(e) => {
                                const newScale = [...criterion.scale];
                                newScale[levelIndex] = e.target.value;
                                updateRiskCriterion(index, 'scale', newScale);
                              }}
                            />
                          </Grid>
                        ))}
                      </Grid>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Risk Assessment Methodology
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              placeholder="Define the systematic approach for risk assessment including methods, tools, and techniques to be used..."
              value={framework.risk_assessment_methodology}
              onChange={(e) => updateFramework('risk_assessment_methodology', e.target.value)}
              helperText="Specify whether qualitative, semi-quantitative, or quantitative methods will be used and under what circumstances."
            />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // ============================================================================
  // RENDER TREATMENT TAB
  // ============================================================================

  const renderTreatmentTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Alert severity="info" icon={<Info />}>
          <Typography variant="subtitle2" fontWeight={600}>
            ISO 31000:2018 Risk Treatment Strategies
          </Typography>
          <Typography variant="body2">
            Define the available risk treatment options and selection criteria.
            Treatment strategies should be cost-effective and aligned with organizational objectives.
          </Typography>
        </Alert>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Risk Treatment Strategies
            </Typography>
            
            {treatmentStrategies.map((strategy, index) => (
              <Card key={strategy.id} variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={3}>
                      <Typography variant="h6" color="primary">
                        {strategy.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {strategy.description}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" gutterBottom>
                        Applicability:
                      </Typography>
                      <Typography variant="body2">
                        {strategy.applicability}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" gutterBottom>
                        Cost Effectiveness:
                      </Typography>
                      <Box display="flex" alignItems="center">
                        <Slider
                          value={strategy.cost_effectiveness}
                          min={1}
                          max={5}
                          marks
                          valueLabelDisplay="auto"
                          size="small"
                          sx={{ mr: 2 }}
                          disabled
                        />
                        <Typography variant="body2">
                          {strategy.cost_effectiveness}/5
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" gutterBottom>
                        Implementation Complexity:
                      </Typography>
                      <Box display="flex" alignItems="center">
                        <Slider
                          value={strategy.implementation_complexity}
                          min={1}
                          max={5}
                          marks
                          valueLabelDisplay="auto"
                          size="small"
                          sx={{ mr: 2 }}
                          disabled
                        />
                        <Typography variant="body2">
                          {strategy.implementation_complexity}/5
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            ))}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Treatment Selection Matrix
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Risk Level</TableCell>
                    <TableCell>Primary Strategy</TableCell>
                    <TableCell>Secondary Options</TableCell>
                    <TableCell>Authority Level</TableCell>
                    <TableCell>Timeline</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>
                      <Chip label="Critical" size="small" sx={{ bgcolor: ISO_STATUS_COLORS.nonConformance, color: 'white' }} />
                    </TableCell>
                    <TableCell>Avoid / Mitigate</TableCell>
                    <TableCell>Transfer</TableCell>
                    <TableCell>Senior Management</TableCell>
                    <TableCell>Immediate</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>
                      <Chip label="High" size="small" sx={{ bgcolor: ISO_STATUS_COLORS.pending, color: 'white' }} />
                    </TableCell>
                    <TableCell>Mitigate</TableCell>
                    <TableCell>Transfer / Avoid</TableCell>
                    <TableCell>Department Head</TableCell>
                    <TableCell>1-2 weeks</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>
                      <Chip label="Medium" size="small" sx={{ bgcolor: ISO_STATUS_COLORS.warning, color: 'white' }} />
                    </TableCell>
                    <TableCell>Mitigate</TableCell>
                    <TableCell>Transfer / Accept</TableCell>
                    <TableCell>Risk Owner</TableCell>
                    <TableCell>1-3 months</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>
                      <Chip label="Low" size="small" sx={{ bgcolor: ISO_STATUS_COLORS.compliant, color: 'white' }} />
                    </TableCell>
                    <TableCell>Accept</TableCell>
                    <TableCell>Mitigate</TableCell>
                    <TableCell>Risk Owner</TableCell>
                    <TableCell>Ongoing</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // ============================================================================
  // RENDER MAIN DIALOG
  // ============================================================================

  if (loading) {
    return (
      <Dialog open={open} maxWidth="lg" fullWidth>
        <DialogContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
            <Typography variant="h6" sx={{ ml: 2 }}>
              Loading Risk Framework Configuration...
            </Typography>
          </Box>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="xl" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '80vh' }
      }}
    >
      <DialogTitle sx={{ 
        bgcolor: PROFESSIONAL_COLORS.primary.main, 
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        gap: 1
      }}>
        <BusinessCenter />
        <Box>
          <Typography variant="h6" fontWeight={700}>
            ISO 31000:2018 Risk Management Framework Configuration
          </Typography>
          <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>
            Establish organizational risk management principles and structure
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            variant="fullWidth"
            sx={{
              '& .MuiTab-root': {
                textTransform: 'none',
                minHeight: 64,
                fontWeight: 600,
              },
            }}
          >
            <Tab 
              icon={<Gavel />} 
              label="Policy & Governance" 
              id="risk-framework-tab-0"
              aria-controls="risk-framework-tabpanel-0"
            />
            <Tab 
              icon={<BusinessCenter />} 
              label="Organizational Context" 
              id="risk-framework-tab-1"
              aria-controls="risk-framework-tabpanel-1"
            />
            <Tab 
              icon={<Assessment />} 
              label="Risk Criteria" 
              id="risk-framework-tab-2"
              aria-controls="risk-framework-tabpanel-2"
            />
            <Tab 
              icon={<Security />} 
              label="Treatment Strategies" 
              id="risk-framework-tab-3"
              aria-controls="risk-framework-tabpanel-3"
            />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          {renderPolicyTab()}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {renderContextTab()}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {renderCriteriaTab()}
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {renderTreatmentTab()}
        </TabPanel>
      </DialogContent>

      <DialogActions sx={{ p: 3, bgcolor: 'rgba(0,0,0,0.02)' }}>
        <Button onClick={onClose}>
          Cancel
        </Button>
        
        <Box sx={{ flex: 1 }} />
        
        <Alert severity="info" sx={{ mr: 2 }}>
          <Typography variant="caption">
            Framework configuration requires management approval before becoming effective
          </Typography>
        </Alert>
        
        <Button
          variant="contained"
          onClick={handleSave}
          disabled={saving}
          startIcon={saving ? <CircularProgress size={16} /> : <Save />}
          sx={{ bgcolor: PROFESSIONAL_COLORS.primary.main }}
        >
          {saving ? 'Saving...' : 'Save Framework'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RiskFrameworkConfig;