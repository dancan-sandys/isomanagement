import React, { useState, useEffect, useMemo } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
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
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  Slider,
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
  Tooltip,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormHelperText,
  CircularProgress,
  useTheme,
} from '@mui/material';
import {
  ExpandMore,
  Info,
  Warning,
  CheckCircle,
  Cancel,
  Assessment,
  Security,
  TrendingUp,
  Schedule,
  Assignment,
  MonitorHeart,
  Gavel,
  Save,
  Send,
  Help,
  AutorenewOutlined,
  Add,
} from '@mui/icons-material';
import riskAPI, { RiskAssessmentData, RiskTreatmentData } from '../../services/riskAPI';
import { ISO_STATUS_COLORS, PROFESSIONAL_COLORS } from '../../theme/designSystem';

// ============================================================================
// ISO 31000:2018 RISK ASSESSMENT INTERFACES
// ============================================================================

interface RiskAssessmentWizardProps {
  open: boolean;
  riskId?: number | null;
  onClose: () => void;
  onComplete: (assessmentId?: number) => void;
}

interface AssessmentStep {
  id: string;
  label: string;
  description: string;
  required: boolean;
  completed: boolean;
}

interface RiskAssessmentState {
  // Step 1: Risk Context
  organizational_context: string;
  external_factors: string[];
  internal_factors: string[];
  stakeholders: string[];
  
  // Step 2: Risk Identification
  risk_id?: number;
  risk_title: string;
  risk_description: string;
  risk_category: string;
  risk_source: string;
  potential_causes: string[];
  potential_consequences: string[];
  
  // Step 3: Risk Analysis
  severity: number;
  likelihood: number;
  detectability: number;
  impact_areas: string[];
  time_horizon: string;
  risk_velocity: number;
  
  // Step 4: Risk Evaluation
  risk_score: number;
  risk_level: string;
  risk_tolerance_met: boolean;
  risk_appetite_alignment: string;
  regulatory_implications: string;
  
  // Step 5: Risk Treatment
  treatment_strategy: 'avoid' | 'transfer' | 'mitigate' | 'accept';
  treatment_actions: Array<{
    action: string;
    responsible: string;
    timeline: string;
    cost_estimate: number;
  }>;
  treatment_cost_benefit: string;
  residual_risk_level: string;
  
  // Step 6: Monitoring & Review
  monitoring_frequency: string;
  monitoring_methods: string[];
  key_indicators: string[];
  review_schedule: string;
  escalation_criteria: string;
  responsible_parties: string[];
}

// ============================================================================
// RISK MATRIX CONFIGURATION (ISO 31000:2018 Compliant)
// ============================================================================

const RISK_MATRIX = {
  severity: [
    { value: 1, label: 'Negligible', description: 'Minimal impact on objectives', color: '#10B981' },
    { value: 2, label: 'Minor', description: 'Small impact on objectives', color: '#F59E0B' },
    { value: 3, label: 'Moderate', description: 'Significant impact on objectives', color: '#EF4444' },
    { value: 4, label: 'Major', description: 'Serious impact on objectives', color: '#DC2626' },
    { value: 5, label: 'Catastrophic', description: 'Critical impact on objectives', color: '#7F1D1D' },
  ],
  likelihood: [
    { value: 1, label: 'Rare', description: 'May occur only in exceptional circumstances (< 5%)', color: '#10B981' },
    { value: 2, label: 'Unlikely', description: 'Could occur at some time (5-25%)', color: '#F59E0B' },
    { value: 3, label: 'Possible', description: 'Might occur at some time (25-50%)', color: '#EF4444' },
    { value: 4, label: 'Likely', description: 'Will probably occur in most circumstances (50-75%)', color: '#DC2626' },
    { value: 5, label: 'Almost Certain', description: 'Expected to occur in most circumstances (> 75%)', color: '#7F1D1D' },
  ],
  detectability: [
    { value: 1, label: 'Very High', description: 'Almost certain to detect', color: '#10B981' },
    { value: 2, label: 'High', description: 'High chance of detection', color: '#F59E0B' },
    { value: 3, label: 'Moderate', description: 'Moderate chance of detection', color: '#EF4444' },
    { value: 4, label: 'Low', description: 'Low chance of detection', color: '#DC2626' },
    { value: 5, label: 'Very Low', description: 'Remote chance of detection', color: '#7F1D1D' },
  ],
};

const ASSESSMENT_STEPS: AssessmentStep[] = [
  {
    id: 'context',
    label: 'Risk Context',
    description: 'Establish organizational context and scope (ISO 31000:2018 - 6.3.2)',
    required: true,
    completed: false,
  },
  {
    id: 'identification',
    label: 'Risk Identification',
    description: 'Systematic identification of risk sources and events (ISO 31000:2018 - 6.4.2)',
    required: true,
    completed: false,
  },
  {
    id: 'analysis',
    label: 'Risk Analysis',
    description: 'Develop understanding of risk likelihood and consequences (ISO 31000:2018 - 6.4.3)',
    required: true,
    completed: false,
  },
  {
    id: 'evaluation',
    label: 'Risk Evaluation',
    description: 'Compare analysis results with risk criteria (ISO 31000:2018 - 6.4.4)',
    required: true,
    completed: false,
  },
  {
    id: 'treatment',
    label: 'Risk Treatment',
    description: 'Select and implement risk treatment options (ISO 31000:2018 - 6.5)',
    required: true,
    completed: false,
  },
  {
    id: 'monitoring',
    label: 'Monitoring & Review',
    description: 'Establish monitoring and review framework (ISO 31000:2018 - 6.6)',
    required: true,
    completed: false,
  },
];

// ============================================================================
// MAIN WIZARD COMPONENT
// ============================================================================

const RiskAssessmentWizard: React.FC<RiskAssessmentWizardProps> = ({
  open,
  riskId,
  onClose,
  onComplete,
}) => {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [steps, setSteps] = useState<AssessmentStep[]>(ASSESSMENT_STEPS);
  
  const [assessmentData, setAssessmentData] = useState<RiskAssessmentState>({
    organizational_context: '',
    external_factors: [],
    internal_factors: [],
    stakeholders: [],
    risk_title: '',
    risk_description: '',
    risk_category: 'process',
    risk_source: '',
    potential_causes: [],
    potential_consequences: [],
    severity: 1,
    likelihood: 1,
    detectability: 1,
    impact_areas: [],
    time_horizon: 'short_term',
    risk_velocity: 1,
    risk_score: 1,
    risk_level: 'low',
    risk_tolerance_met: true,
    risk_appetite_alignment: 'aligned',
    regulatory_implications: '',
    treatment_strategy: 'mitigate',
    treatment_actions: [],
    treatment_cost_benefit: '',
    residual_risk_level: 'low',
    monitoring_frequency: 'monthly',
    monitoring_methods: [],
    key_indicators: [],
    review_schedule: 'quarterly',
    escalation_criteria: '',
    responsible_parties: [],
  });

  // ============================================================================
  // EFFECTS & DATA LOADING
  // ============================================================================

  useEffect(() => {
    if (open && riskId) {
      loadExistingRisk();
    } else if (open) {
      resetWizard();
    }
  }, [open, riskId]);

  // Calculate risk score using useMemo to avoid infinite loops
  const calculatedRiskScore = useMemo(() => {
    const riskScore = assessmentData.severity * assessmentData.likelihood * (assessmentData.detectability / 5);
    const riskLevel = getRiskLevel(riskScore);
    return { risk_score: Math.round(riskScore), risk_level: riskLevel };
  }, [assessmentData.severity, assessmentData.likelihood, assessmentData.detectability]);

  // Update assessment data when calculated values change
  useEffect(() => {
    setAssessmentData(prev => ({
      ...prev,
      risk_score: calculatedRiskScore.risk_score,
      risk_level: calculatedRiskScore.risk_level,
    }));
  }, [calculatedRiskScore]);

  // ============================================================================
  // HELPER FUNCTIONS
  // ============================================================================

  const loadExistingRisk = async () => {
    if (!riskId) return;
    
    try {
      setLoading(true);
      const response = await riskAPI.get(riskId);
      if (response.success) {
        const risk = response.data;
        setAssessmentData(prev => ({
          ...prev,
          risk_id: risk.id,
          risk_title: risk.title || '',
          risk_description: risk.description || '',
          risk_category: risk.category || 'process',
          severity: getSeverityValue(risk.severity) || 1,
          likelihood: getLikelihoodValue(risk.likelihood) || 1,
          detectability: getDetectabilityValue(risk.detectability) || 1,
        }));
      }
    } catch (error) {
      console.error('Failed to load existing risk:', error);
    } finally {
      setLoading(false);
    }
  };

  const resetWizard = () => {
    setActiveStep(0);
    setSteps(ASSESSMENT_STEPS.map(step => ({ ...step, completed: false })));
    setAssessmentData({
      organizational_context: '',
      external_factors: [],
      internal_factors: [],
      stakeholders: [],
      risk_title: '',
      risk_description: '',
      risk_category: 'process',
      risk_source: '',
      potential_causes: [],
      potential_consequences: [],
      severity: 1,
      likelihood: 1,
      detectability: 1,
      impact_areas: [],
      time_horizon: 'short_term',
      risk_velocity: 1,
      risk_score: 1,
      risk_level: 'low',
      risk_tolerance_met: true,
      risk_appetite_alignment: 'aligned',
      regulatory_implications: '',
      treatment_strategy: 'mitigate',
      treatment_actions: [],
      treatment_cost_benefit: '',
      residual_risk_level: 'low',
      monitoring_frequency: 'monthly',
      monitoring_methods: [],
      key_indicators: [],
      review_schedule: 'quarterly',
      escalation_criteria: '',
      responsible_parties: [],
    });
  };

  const getRiskLevel = (score: number): string => {
    if (score <= 4) return 'low';
    if (score <= 12) return 'medium';
    if (score <= 20) return 'high';
    return 'critical';
  };

  const getRiskLevelColor = (level: string): string => {
    switch (level) {
      case 'low': return ISO_STATUS_COLORS.compliant;
      case 'medium': return ISO_STATUS_COLORS.warning;
      case 'high': return ISO_STATUS_COLORS.pending;
      case 'critical': return ISO_STATUS_COLORS.nonConformance;
      default: return ISO_STATUS_COLORS.neutral;
    }
  };

  const getSeverityValue = (severity: string): number => {
    const severityMap: Record<string, number> = {
      negligible: 1, minor: 2, moderate: 3, major: 4, catastrophic: 5,
      low: 1, medium: 3, high: 4, critical: 5
    };
    return severityMap[severity?.toLowerCase()] || 1;
  };

  const getLikelihoodValue = (likelihood: string): number => {
    const likelihoodMap: Record<string, number> = {
      rare: 1, unlikely: 2, possible: 3, likely: 4, almost_certain: 5
    };
    return likelihoodMap[likelihood?.toLowerCase()] || 1;
  };

  const getDetectabilityValue = (detectability: string): number => {
    const detectabilityMap: Record<string, number> = {
      easily_detectable: 1, moderately_detectable: 2, difficult: 3, 
      very_difficult: 4, almost_undetectable: 5
    };
    return detectabilityMap[detectability?.toLowerCase()] || 1;
  };

  // ============================================================================
  // STEP VALIDATION
  // ============================================================================

  const validateStep = (stepIndex: number): boolean => {
    switch (stepIndex) {
      case 0: // Context
        return !!(assessmentData.organizational_context && 
                 assessmentData.external_factors.length > 0 && 
                 assessmentData.internal_factors.length > 0);
      case 1: // Identification
        return !!(assessmentData.risk_title && 
                 assessmentData.risk_description && 
                 assessmentData.potential_causes.length > 0 && 
                 assessmentData.potential_consequences.length > 0);
      case 2: // Analysis
        return !!(assessmentData.severity > 0 && 
                 assessmentData.likelihood > 0 && 
                 assessmentData.detectability > 0 && 
                 assessmentData.impact_areas.length > 0);
      case 3: // Evaluation
        return !!(assessmentData.risk_level && 
                 assessmentData.risk_appetite_alignment);
      case 4: // Treatment
        return !!(assessmentData.treatment_strategy && 
                 assessmentData.treatment_actions.length > 0);
      case 5: // Monitoring
        return !!(assessmentData.monitoring_frequency && 
                 assessmentData.monitoring_methods.length > 0 && 
                 assessmentData.key_indicators.length > 0);
      default:
        return true;
    }
  };

  // ============================================================================
  // NAVIGATION HANDLERS
  // ============================================================================

  const handleNext = () => {
    if (validateStep(activeStep)) {
      // Mark current step as completed
      setSteps(prev => prev.map((step, index) => 
        index === activeStep ? { ...step, completed: true } : step
      ));
      
      if (activeStep < steps.length - 1) {
        setActiveStep(prev => prev + 1);
      }
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleStepClick = (stepIndex: number) => {
    // Allow navigation to previous steps or current step
    if (stepIndex <= activeStep) {
      setActiveStep(stepIndex);
    }
  };

  // ============================================================================
  // FORM HANDLERS
  // ============================================================================

  const updateAssessmentData = (field: keyof RiskAssessmentState, value: any) => {
    setAssessmentData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const addToArray = (field: keyof RiskAssessmentState, value: string) => {
    setAssessmentData(prev => ({
      ...prev,
      [field]: [...(prev[field] as string[]), value],
    }));
  };

  const removeFromArray = (field: keyof RiskAssessmentState, index: number) => {
    setAssessmentData(prev => ({
      ...prev,
      [field]: (prev[field] as string[]).filter((_, i) => i !== index),
    }));
  };

  // ============================================================================
  // SUBMISSION HANDLERS
  // ============================================================================

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      
      // Prepare assessment data for API
      const assessmentPayload: RiskAssessmentData = {
        risk_assessment_method: 'ISO_31000_2018_SYSTEMATIC',
        severity: RISK_MATRIX.severity[assessmentData.severity - 1]?.label.toLowerCase(),
        likelihood: RISK_MATRIX.likelihood[assessmentData.likelihood - 1]?.label.toLowerCase(),
        detectability: RISK_MATRIX.detectability[assessmentData.detectability - 1]?.label.toLowerCase(),
        impact_score: assessmentData.risk_score,
        risk_treatment_strategy: assessmentData.treatment_strategy,
        risk_treatment_plan: assessmentData.treatment_actions.map(action => action.action).join('; '),
        monitoring_frequency: assessmentData.monitoring_frequency,
        review_frequency: assessmentData.review_schedule,
      };

      let response;
      
      if (assessmentData.risk_id) {
        // Update existing risk assessment
        response = await riskAPI.assessRisk(assessmentData.risk_id, assessmentPayload);
      } else {
        // Create new risk first, then assess
        const createResponse = await riskAPI.create({
          item_type: 'risk',
          title: assessmentData.risk_title,
          description: assessmentData.risk_description,
          category: assessmentData.risk_category,
          severity: RISK_MATRIX.severity[assessmentData.severity - 1]?.label.toLowerCase(),
          likelihood: RISK_MATRIX.likelihood[assessmentData.likelihood - 1]?.label.toLowerCase(),
          detectability: RISK_MATRIX.detectability[assessmentData.detectability - 1]?.label.toLowerCase(),
        });
        
        if (createResponse.success) {
          response = await riskAPI.assessRisk(createResponse.data.id, assessmentPayload);
        }
      }

      if (response?.success) {
        onComplete(response.data.risk_id);
      }
    } catch (error) {
      console.error('Failed to submit risk assessment:', error);
    } finally {
      setSubmitting(false);
    }
  };

  // ============================================================================
  // RENDER STEP CONTENT
  // ============================================================================

  const renderStepContent = (stepIndex: number) => {
    switch (stepIndex) {
      case 0:
        return renderContextStep();
      case 1:
        return renderIdentificationStep();
      case 2:
        return renderAnalysisStep();
      case 3:
        return renderEvaluationStep();
      case 4:
        return renderTreatmentStep();
      case 5:
        return renderMonitoringStep();
      default:
        return null;
    }
  };

  const renderContextStep = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Alert severity="info" icon={<Info />}>
          <Typography variant="subtitle2" fontWeight={600}>
            ISO 31000:2018 - Risk Context Establishment
          </Typography>
          <Typography variant="body2">
            Define the organizational context that will inform risk criteria and assessment scope.
            This step ensures alignment with organizational objectives and stakeholder expectations.
          </Typography>
        </Alert>
      </Grid>
      
      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={4}
          label="Organizational Context"
          placeholder="Describe the organization's purpose, objectives, and strategic direction relevant to this risk assessment..."
          value={assessmentData.organizational_context}
          onChange={(e) => updateAssessmentData('organizational_context', e.target.value)}
          required
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <Typography variant="h6" gutterBottom>
          External Factors
        </Typography>
        <Stack spacing={1}>
          {assessmentData.external_factors.map((factor, index) => (
            <Chip
              key={index}
              label={factor}
              onDelete={() => removeFromArray('external_factors', index)}
              variant="outlined"
            />
          ))}
          <TextField
            size="small"
            placeholder="Add external factor (e.g., regulatory changes, market conditions)"
            onKeyDown={(e) => {
              const target = e.target as HTMLInputElement;
              if (e.key === 'Enter' && target.value) {
                addToArray('external_factors', target.value);
                target.value = '';
              }
            }}
          />
        </Stack>
      </Grid>

      <Grid item xs={12} md={6}>
        <Typography variant="h6" gutterBottom>
          Internal Factors
        </Typography>
        <Stack spacing={1}>
          {assessmentData.internal_factors.map((factor, index) => (
            <Chip
              key={index}
              label={factor}
              onDelete={() => removeFromArray('internal_factors', index)}
              variant="outlined"
            />
          ))}
          <TextField
            size="small"
            placeholder="Add internal factor (e.g., capabilities, resources, culture)"
            onKeyDown={(e) => {
              const target = e.target as HTMLInputElement;
              if (e.key === 'Enter' && target.value) {
                addToArray('internal_factors', target.value);
                target.value = '';
              }
            }}
          />
        </Stack>
      </Grid>

      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Key Stakeholders
        </Typography>
        <Stack spacing={1}>
          {assessmentData.stakeholders.map((stakeholder, index) => (
            <Chip
              key={index}
              label={stakeholder}
              onDelete={() => removeFromArray('stakeholders', index)}
              variant="outlined"
            />
          ))}
          <TextField
            size="small"
            placeholder="Add stakeholder (e.g., customers, regulators, suppliers)"
            onKeyDown={(e) => {
              const target = e.target as HTMLInputElement;
              if (e.key === 'Enter' && target.value) {
                addToArray('stakeholders', target.value);
                target.value = '';
              }
            }}
          />
        </Stack>
      </Grid>
    </Grid>
  );

  const renderIdentificationStep = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Alert severity="info" icon={<Info />}>
          <Typography variant="subtitle2" fontWeight={600}>
            ISO 31000:2018 - Risk Identification
          </Typography>
          <Typography variant="body2">
            Systematically identify risk sources, areas of impact, events, causes and potential consequences.
            Consider what might happen, when, where, why and how.
          </Typography>
        </Alert>
      </Grid>

      <Grid item xs={12} md={8}>
        <TextField
          fullWidth
          label="Risk Title"
          placeholder="Concise, descriptive title for the risk"
          value={assessmentData.risk_title}
          onChange={(e) => updateAssessmentData('risk_title', e.target.value)}
          required
        />
      </Grid>

      <Grid item xs={12} md={4}>
        <FormControl fullWidth>
          <InputLabel>Risk Category</InputLabel>
          <Select
            value={assessmentData.risk_category}
            onChange={(e) => updateAssessmentData('risk_category', e.target.value)}
            label="Risk Category"
          >
            <MenuItem value="strategic">Strategic</MenuItem>
            <MenuItem value="financial">Financial</MenuItem>
            <MenuItem value="operational">Operational</MenuItem>
            <MenuItem value="compliance">Compliance</MenuItem>
            <MenuItem value="reputational">Reputational</MenuItem>
            <MenuItem value="process">Process</MenuItem>
            <MenuItem value="supplier">Supplier</MenuItem>
            <MenuItem value="haccp">HACCP</MenuItem>
            <MenuItem value="prp">PRP</MenuItem>
            <MenuItem value="equipment">Equipment</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={4}
          label="Risk Description"
          placeholder="Detailed description of the risk, including context and scope..."
          value={assessmentData.risk_description}
          onChange={(e) => updateAssessmentData('risk_description', e.target.value)}
          required
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <Typography variant="h6" gutterBottom>
          Potential Causes
        </Typography>
        <Stack spacing={1}>
          {assessmentData.potential_causes.map((cause, index) => (
            <Chip
              key={index}
              label={cause}
              onDelete={() => removeFromArray('potential_causes', index)}
              variant="outlined"
              color="error"
            />
          ))}
          <TextField
            size="small"
            placeholder="Add potential cause (what could trigger this risk?)"
            onKeyDown={(e) => {
              const target = e.target as HTMLInputElement;
              if (e.key === 'Enter' && target.value) {
                addToArray('potential_causes', target.value);
                target.value = '';
              }
            }}
          />
        </Stack>
      </Grid>

      <Grid item xs={12} md={6}>
        <Typography variant="h6" gutterBottom>
          Potential Consequences
        </Typography>
        <Stack spacing={1}>
          {assessmentData.potential_consequences.map((consequence, index) => (
            <Chip
              key={index}
              label={consequence}
              onDelete={() => removeFromArray('potential_consequences', index)}
              variant="outlined"
              color="warning"
            />
          ))}
          <TextField
            size="small"
            placeholder="Add potential consequence (what could happen if risk occurs?)"
            onKeyDown={(e) => {
              const target = e.target as HTMLInputElement;
              if (e.key === 'Enter' && target.value) {
                addToArray('potential_consequences', target.value);
                target.value = '';
              }
            }}
          />
        </Stack>
      </Grid>
    </Grid>
  );

  const renderAnalysisStep = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Alert severity="info" icon={<Info />}>
          <Typography variant="subtitle2" fontWeight={600}>
            ISO 31000:2018 - Risk Analysis
          </Typography>
          <Typography variant="body2">
            Develop understanding of the risk through analysis of likelihood, consequences, and detectability.
            This quantitative assessment forms the basis for risk evaluation and treatment decisions.
          </Typography>
        </Alert>
      </Grid>

      {/* Risk Matrix */}
      <Grid item xs={12}>
        <Card sx={{ bgcolor: 'rgba(255,255,255,0.8)' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Risk Analysis Matrix (ISO 31000:2018)
            </Typography>
            
            <Grid container spacing={4}>
              {/* Severity */}
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Severity of Consequences
                </Typography>
                <Box sx={{ px: 2 }}>
                  <Slider
                    value={assessmentData.severity}
                    onChange={(_, value) => updateAssessmentData('severity', value as number)}
                    step={1}
                    marks={RISK_MATRIX.severity.map((item, index) => ({
                      value: index + 1,
                      label: item.label,
                    }))}
                    min={1}
                    max={5}
                    valueLabelDisplay="on"
                    sx={{
                      '& .MuiSlider-thumb': {
                        bgcolor: RISK_MATRIX.severity[assessmentData.severity - 1]?.color,
                      },
                      '& .MuiSlider-track': {
                        bgcolor: RISK_MATRIX.severity[assessmentData.severity - 1]?.color,
                      },
                    }}
                  />
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  {RISK_MATRIX.severity[assessmentData.severity - 1]?.description}
                </Typography>
              </Grid>

              {/* Likelihood */}
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Likelihood of Occurrence
                </Typography>
                <Box sx={{ px: 2 }}>
                  <Slider
                    value={assessmentData.likelihood}
                    onChange={(_, value) => updateAssessmentData('likelihood', value as number)}
                    step={1}
                    marks={RISK_MATRIX.likelihood.map((item, index) => ({
                      value: index + 1,
                      label: item.label,
                    }))}
                    min={1}
                    max={5}
                    valueLabelDisplay="on"
                    sx={{
                      '& .MuiSlider-thumb': {
                        bgcolor: RISK_MATRIX.likelihood[assessmentData.likelihood - 1]?.color,
                      },
                      '& .MuiSlider-track': {
                        bgcolor: RISK_MATRIX.likelihood[assessmentData.likelihood - 1]?.color,
                      },
                    }}
                  />
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  {RISK_MATRIX.likelihood[assessmentData.likelihood - 1]?.description}
                </Typography>
              </Grid>

              {/* Detectability */}
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Detectability (Inverse)
                </Typography>
                <Box sx={{ px: 2 }}>
                  <Slider
                    value={assessmentData.detectability}
                    onChange={(_, value) => updateAssessmentData('detectability', value as number)}
                    step={1}
                    marks={RISK_MATRIX.detectability.map((item, index) => ({
                      value: index + 1,
                      label: item.label,
                    }))}
                    min={1}
                    max={5}
                    valueLabelDisplay="on"
                    sx={{
                      '& .MuiSlider-thumb': {
                        bgcolor: RISK_MATRIX.detectability[assessmentData.detectability - 1]?.color,
                      },
                      '& .MuiSlider-track': {
                        bgcolor: RISK_MATRIX.detectability[assessmentData.detectability - 1]?.color,
                      },
                    }}
                  />
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  {RISK_MATRIX.detectability[assessmentData.detectability - 1]?.description}
                </Typography>
              </Grid>
            </Grid>

            {/* Risk Score Display */}
            <Box sx={{ mt: 3, p: 2, bgcolor: getRiskLevelColor(assessmentData.risk_level), borderRadius: 2 }}>
              <Typography variant="h4" sx={{ color: 'white', textAlign: 'center', fontWeight: 700 }}>
                Risk Score: {assessmentData.risk_score}
              </Typography>
              <Typography variant="h6" sx={{ color: 'white', textAlign: 'center', textTransform: 'uppercase' }}>
                {assessmentData.risk_level} Risk Level
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Additional Analysis */}
      <Grid item xs={12} md={6}>
        <Typography variant="h6" gutterBottom>
          Impact Areas
        </Typography>
        <Stack spacing={1}>
          {assessmentData.impact_areas.map((area, index) => (
            <Chip
              key={index}
              label={area}
              onDelete={() => removeFromArray('impact_areas', index)}
              variant="outlined"
            />
          ))}
          <TextField
            size="small"
            placeholder="Add impact area (e.g., financial, operational, reputational)"
            onKeyDown={(e) => {
              const target = e.target as HTMLInputElement;
              if (e.key === 'Enter' && target.value) {
                addToArray('impact_areas', target.value);
                target.value = '';
              }
            }}
          />
        </Stack>
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Time Horizon</InputLabel>
          <Select
            value={assessmentData.time_horizon}
            onChange={(e) => updateAssessmentData('time_horizon', e.target.value)}
            label="Time Horizon"
          >
            <MenuItem value="immediate">Immediate (0-1 month)</MenuItem>
            <MenuItem value="short_term">Short Term (1-6 months)</MenuItem>
            <MenuItem value="medium_term">Medium Term (6-18 months)</MenuItem>
            <MenuItem value="long_term">Long Term (18+ months)</MenuItem>
          </Select>
        </FormControl>
      </Grid>
    </Grid>
  );

  const renderEvaluationStep = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Alert severity="info" icon={<Info />}>
          <Typography variant="subtitle2" fontWeight={600}>
            ISO 31000:2018 - Risk Evaluation
          </Typography>
          <Typography variant="body2">
            Compare risk analysis results with established risk criteria to determine risk significance
            and support decision making about risk treatment priorities.
          </Typography>
        </Alert>
      </Grid>

      <Grid item xs={12}>
        <Card sx={{ bgcolor: getRiskLevelColor(assessmentData.risk_level), color: 'white' }}>
          <CardContent>
            <Typography variant="h5" fontWeight={700} gutterBottom>
              Risk Evaluation Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>Risk Score</Typography>
                <Typography variant="h3" fontWeight={700}>{assessmentData.risk_score}</Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>Risk Level</Typography>
                <Typography variant="h4" fontWeight={600} sx={{ textTransform: 'uppercase' }}>
                  {assessmentData.risk_level}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>Evaluation Components</Typography>
                <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                  <Chip label={`Severity: ${RISK_MATRIX.severity[assessmentData.severity - 1]?.label}`} sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }} />
                  <Chip label={`Likelihood: ${RISK_MATRIX.likelihood[assessmentData.likelihood - 1]?.label}`} sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }} />
                  <Chip label={`Detectability: ${RISK_MATRIX.detectability[assessmentData.detectability - 1]?.label}`} sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }} />
                </Stack>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl component="fieldset">
          <Typography variant="h6" gutterBottom>
            Risk Tolerance Assessment
          </Typography>
          <RadioGroup
            value={assessmentData.risk_tolerance_met ? 'yes' : 'no'}
            onChange={(e) => updateAssessmentData('risk_tolerance_met', e.target.value === 'yes')}
          >
            <FormControlLabel 
              value="yes" 
              control={<Radio />} 
              label="Risk level is within organizational tolerance" 
            />
            <FormControlLabel 
              value="no" 
              control={<Radio />} 
              label="Risk level exceeds organizational tolerance" 
            />
          </RadioGroup>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Risk Appetite Alignment</InputLabel>
          <Select
            value={assessmentData.risk_appetite_alignment}
            onChange={(e) => updateAssessmentData('risk_appetite_alignment', e.target.value)}
            label="Risk Appetite Alignment"
          >
            <MenuItem value="aligned">Fully Aligned</MenuItem>
            <MenuItem value="partially_aligned">Partially Aligned</MenuItem>
            <MenuItem value="misaligned">Misaligned</MenuItem>
            <MenuItem value="requires_review">Requires Review</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={3}
          label="Regulatory & Compliance Implications"
          placeholder="Describe any regulatory requirements, compliance obligations, or legal implications..."
          value={assessmentData.regulatory_implications}
          onChange={(e) => updateAssessmentData('regulatory_implications', e.target.value)}
        />
      </Grid>

      {/* Risk Decision Matrix */}
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Risk Treatment Priority Matrix
        </Typography>
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Risk Level</TableCell>
                <TableCell>Recommended Action</TableCell>
                <TableCell>Timeline</TableCell>
                <TableCell>Authority Level</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow sx={{ bgcolor: assessmentData.risk_level === 'critical' ? 'rgba(220, 38, 38, 0.1)' : 'inherit' }}>
                <TableCell>Critical</TableCell>
                <TableCell>Immediate action required</TableCell>
                <TableCell>24-48 hours</TableCell>
                <TableCell>Senior Management</TableCell>
              </TableRow>
              <TableRow sx={{ bgcolor: assessmentData.risk_level === 'high' ? 'rgba(239, 68, 68, 0.1)' : 'inherit' }}>
                <TableCell>High</TableCell>
                <TableCell>Urgent treatment needed</TableCell>
                <TableCell>1-2 weeks</TableCell>
                <TableCell>Department Head</TableCell>
              </TableRow>
              <TableRow sx={{ bgcolor: assessmentData.risk_level === 'medium' ? 'rgba(245, 158, 11, 0.1)' : 'inherit' }}>
                <TableCell>Medium</TableCell>
                <TableCell>Treatment plan required</TableCell>
                <TableCell>1-3 months</TableCell>
                <TableCell>Risk Owner</TableCell>
              </TableRow>
              <TableRow sx={{ bgcolor: assessmentData.risk_level === 'low' ? 'rgba(16, 185, 129, 0.1)' : 'inherit' }}>
                <TableCell>Low</TableCell>
                <TableCell>Monitor and review</TableCell>
                <TableCell>Quarterly review</TableCell>
                <TableCell>Risk Owner</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Grid>
    </Grid>
  );

  const renderTreatmentStep = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Alert severity="info" icon={<Info />}>
          <Typography variant="subtitle2" fontWeight={600}>
            ISO 31000:2018 - Risk Treatment
          </Typography>
          <Typography variant="body2">
            Select and plan appropriate risk treatment options. Consider the four main strategies:
            Avoid, Transfer, Mitigate, or Accept the risk based on cost-benefit analysis.
          </Typography>
        </Alert>
      </Grid>

      <Grid item xs={12}>
        <FormControl component="fieldset">
          <Typography variant="h6" gutterBottom>
            Risk Treatment Strategy
          </Typography>
          <RadioGroup
            value={assessmentData.treatment_strategy}
            onChange={(e) => updateAssessmentData('treatment_strategy', e.target.value as any)}
          >
            <FormControlLabel 
              value="avoid" 
              control={<Radio />} 
              label={
                <Box>
                  <Typography variant="body1" fontWeight={600}>Avoid</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Eliminate the risk by not engaging in the activity or changing the process
                  </Typography>
                </Box>
              } 
            />
            <FormControlLabel 
              value="transfer" 
              control={<Radio />} 
              label={
                <Box>
                  <Typography variant="body1" fontWeight={600}>Transfer</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Share or shift the risk to another party (insurance, outsourcing, contracts)
                  </Typography>
                </Box>
              } 
            />
            <FormControlLabel 
              value="mitigate" 
              control={<Radio />} 
              label={
                <Box>
                  <Typography variant="body1" fontWeight={600}>Mitigate</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Reduce likelihood or impact through controls and safeguards
                  </Typography>
                </Box>
              } 
            />
            <FormControlLabel 
              value="accept" 
              control={<Radio />} 
              label={
                <Box>
                  <Typography variant="body1" fontWeight={600}>Accept</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Accept the risk level and manage through monitoring and contingency planning
                  </Typography>
                </Box>
              } 
            />
          </RadioGroup>
        </FormControl>
      </Grid>

      {/* Treatment Actions */}
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Treatment Actions
        </Typography>
        {assessmentData.treatment_actions.map((action, index) => (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Action Description"
                    value={action.action}
                    onChange={(e) => {
                      const updatedActions = [...assessmentData.treatment_actions];
                      updatedActions[index].action = e.target.value;
                      updateAssessmentData('treatment_actions', updatedActions);
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Responsible"
                    value={action.responsible}
                    onChange={(e) => {
                      const updatedActions = [...assessmentData.treatment_actions];
                      updatedActions[index].responsible = e.target.value;
                      updateAssessmentData('treatment_actions', updatedActions);
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Timeline"
                    value={action.timeline}
                    onChange={(e) => {
                      const updatedActions = [...assessmentData.treatment_actions];
                      updatedActions[index].timeline = e.target.value;
                      updateAssessmentData('treatment_actions', updatedActions);
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Cost Estimate"
                    type="number"
                    value={action.cost_estimate}
                    onChange={(e) => {
                      const updatedActions = [...assessmentData.treatment_actions];
                      updatedActions[index].cost_estimate = Number(e.target.value);
                      updateAssessmentData('treatment_actions', updatedActions);
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <IconButton
                    color="error"
                    onClick={() => {
                      const updatedActions = assessmentData.treatment_actions.filter((_, i) => i !== index);
                      updateAssessmentData('treatment_actions', updatedActions);
                    }}
                  >
                    <Cancel />
                  </IconButton>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        ))}
        
        <Button
          variant="outlined"
          startIcon={<Add />}
          onClick={() => {
            const newAction = { action: '', responsible: '', timeline: '', cost_estimate: 0 };
            updateAssessmentData('treatment_actions', [...assessmentData.treatment_actions, newAction]);
          }}
        >
          Add Treatment Action
        </Button>
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={3}
          label="Cost-Benefit Analysis"
          placeholder="Analyze the costs of treatment vs. benefits gained and residual risk reduction..."
          value={assessmentData.treatment_cost_benefit}
          onChange={(e) => updateAssessmentData('treatment_cost_benefit', e.target.value)}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Expected Residual Risk Level</InputLabel>
          <Select
            value={assessmentData.residual_risk_level}
            onChange={(e) => updateAssessmentData('residual_risk_level', e.target.value)}
            label="Expected Residual Risk Level"
          >
            <MenuItem value="low">Low</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="high">High</MenuItem>
            <MenuItem value="critical">Critical</MenuItem>
          </Select>
        </FormControl>
      </Grid>
    </Grid>
  );

  const renderMonitoringStep = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Alert severity="info" icon={<Info />}>
          <Typography variant="subtitle2" fontWeight={600}>
            ISO 31000:2018 - Monitoring and Review
          </Typography>
          <Typography variant="body2">
            Establish systematic monitoring and review processes to track risk treatment effectiveness,
            identify changes in risk profile, and ensure continuous improvement of the risk management process.
          </Typography>
        </Alert>
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Monitoring Frequency</InputLabel>
          <Select
            value={assessmentData.monitoring_frequency}
            onChange={(e) => updateAssessmentData('monitoring_frequency', e.target.value)}
            label="Monitoring Frequency"
          >
            <MenuItem value="daily">Daily</MenuItem>
            <MenuItem value="weekly">Weekly</MenuItem>
            <MenuItem value="monthly">Monthly</MenuItem>
            <MenuItem value="quarterly">Quarterly</MenuItem>
            <MenuItem value="semi_annually">Semi-Annually</MenuItem>
            <MenuItem value="annually">Annually</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Review Schedule</InputLabel>
          <Select
            value={assessmentData.review_schedule}
            onChange={(e) => updateAssessmentData('review_schedule', e.target.value)}
            label="Review Schedule"
          >
            <MenuItem value="monthly">Monthly</MenuItem>
            <MenuItem value="quarterly">Quarterly</MenuItem>
            <MenuItem value="semi_annually">Semi-Annually</MenuItem>
            <MenuItem value="annually">Annually</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <Typography variant="h6" gutterBottom>
          Monitoring Methods
        </Typography>
        <Stack spacing={1}>
          {assessmentData.monitoring_methods.map((method, index) => (
            <Chip
              key={index}
              label={method}
              onDelete={() => removeFromArray('monitoring_methods', index)}
              variant="outlined"
              color="primary"
            />
          ))}
          <TextField
            size="small"
            placeholder="Add monitoring method (e.g., audits, KPIs, reports)"
            onKeyDown={(e) => {
              const target = e.target as HTMLInputElement;
              if (e.key === 'Enter' && target.value) {
                addToArray('monitoring_methods', target.value);
                target.value = '';
              }
            }}
          />
        </Stack>
      </Grid>

      <Grid item xs={12} md={6}>
        <Typography variant="h6" gutterBottom>
          Key Risk Indicators
        </Typography>
        <Stack spacing={1}>
          {assessmentData.key_indicators.map((indicator, index) => (
            <Chip
              key={index}
              label={indicator}
              onDelete={() => removeFromArray('key_indicators', index)}
              variant="outlined"
              color="secondary"
            />
          ))}
          <TextField
            size="small"
            placeholder="Add key indicator (metrics to track risk status)"
            onKeyDown={(e) => {
              const target = e.target as HTMLInputElement;
              if (e.key === 'Enter' && target.value) {
                addToArray('key_indicators', target.value);
                target.value = '';
              }
            }}
          />
        </Stack>
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={3}
          label="Escalation Criteria"
          placeholder="Define conditions that would trigger escalation or reassessment..."
          value={assessmentData.escalation_criteria}
          onChange={(e) => updateAssessmentData('escalation_criteria', e.target.value)}
        />
      </Grid>

      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Responsible Parties
        </Typography>
        <Stack spacing={1}>
          {assessmentData.responsible_parties.map((party, index) => (
            <Chip
              key={index}
              label={party}
              onDelete={() => removeFromArray('responsible_parties', index)}
              variant="outlined"
            />
          ))}
          <TextField
            size="small"
            placeholder="Add responsible party (who will monitor and review?)"
            onKeyDown={(e) => {
              const target = e.target as HTMLInputElement;
              if (e.key === 'Enter' && target.value) {
                addToArray('responsible_parties', target.value);
                target.value = '';
              }
            }}
          />
        </Stack>
      </Grid>
    </Grid>
  );

  // ============================================================================
  // RENDER MAIN DIALOG
  // ============================================================================

  if (loading) {
    return (
      <Dialog open={open} maxWidth="md" fullWidth>
        <DialogContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
            <Typography variant="h6" sx={{ ml: 2 }}>
              Loading Risk Assessment Wizard...
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
      maxWidth="lg" 
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
        <Assessment />
        <Box>
          <Typography variant="h6" fontWeight={700}>
            ISO 31000:2018 Risk Assessment Wizard
          </Typography>
          <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>
            Systematic Risk Management Process
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        {/* Progress Indicator */}
        <Box sx={{ p: 2, bgcolor: 'rgba(0,0,0,0.02)' }}>
          <LinearProgress 
            variant="determinate" 
            value={(activeStep + 1) / steps.length * 100}
            sx={{ mb: 1 }}
          />
          <Typography variant="body2" color="textSecondary" textAlign="center">
            Step {activeStep + 1} of {steps.length}: {steps[activeStep]?.label}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex' }}>
          {/* Step Navigation */}
          <Box sx={{ width: 300, bgcolor: 'rgba(0,0,0,0.03)', p: 2 }}>
            <Stepper orientation="vertical" activeStep={activeStep}>
              {steps.map((step, index) => (
                <Step key={step.id} completed={step.completed}>
                  <StepLabel 
                    onClick={() => handleStepClick(index)}
                    sx={{ cursor: index <= activeStep ? 'pointer' : 'default' }}
                    icon={
                      step.completed ? (
                        <CheckCircle sx={{ color: ISO_STATUS_COLORS.compliant }} />
                      ) : (
                        <Box 
                          sx={{ 
                            width: 24, 
                            height: 24, 
                            borderRadius: '50%',
                            bgcolor: index === activeStep ? PROFESSIONAL_COLORS.primary.main : 'rgba(0,0,0,0.1)',
                            color: 'white',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '0.75rem',
                            fontWeight: 600
                          }}
                        >
                          {index + 1}
                        </Box>
                      )
                    }
                  >
                    <Typography variant="body2" fontWeight={600}>
                      {step.label}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {step.description}
                    </Typography>
                  </StepLabel>
                </Step>
              ))}
            </Stepper>
          </Box>

          {/* Step Content */}
          <Box sx={{ flex: 1, p: 3 }}>
            {renderStepContent(activeStep)}
          </Box>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, bgcolor: 'rgba(0,0,0,0.02)' }}>
        <Button onClick={onClose}>
          Cancel
        </Button>
        
        <Box sx={{ flex: 1 }} />
        
        {activeStep > 0 && (
          <Button onClick={handleBack}>
            Back
          </Button>
        )}
        
        {activeStep < steps.length - 1 ? (
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={!validateStep(activeStep)}
            sx={{ bgcolor: PROFESSIONAL_COLORS.primary.main }}
          >
            Next
          </Button>
        ) : (
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={!validateStep(activeStep) || submitting}
            startIcon={submitting ? <CircularProgress size={16} /> : <Save />}
            sx={{ bgcolor: ISO_STATUS_COLORS.compliant }}
          >
            {submitting ? 'Submitting...' : 'Complete Assessment'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default RiskAssessmentWizard;