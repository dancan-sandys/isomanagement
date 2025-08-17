import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Grid,
  FormControlLabel,
  Checkbox,
  Radio,
  RadioGroup,
  FormLabel,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  IconButton,
  Tooltip,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Autocomplete,
  Slider,
  Rating,
  alpha,
  useMediaQuery,
  useTheme,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Snackbar,
  Slide,
  Fab,
  AppBar,
  Toolbar
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ArrowBack as ArrowBackIcon,
  ArrowForward as ArrowForwardIcon,
  Save as SaveIcon,
  Send as SendIcon,
  Assessment as AssessmentIcon,
  Business as BusinessIcon,
  LocalShipping as LocalShippingIcon,
  Security as SecurityIcon,
  Timeline as TimelineIcon,
  Notifications as NotificationsIcon,
  VerifiedUser as VerifiedUserIcon,
  QrCode as QrCodeIcon,
  Inventory as InventoryIcon,
  People as PeopleIcon,
  Description as DescriptionIcon,
  Schedule as ScheduleIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
  Keyboard as KeyboardIcon,
  Close as CloseIcon,
  Menu as MenuIcon
} from '@mui/icons-material';
import { traceabilityAPI } from '../../services/traceabilityAPI';

interface SmartRecallWizardProps {
  onComplete?: (recallData: any) => void;
  onCancel?: () => void;
  initialData?: any;
}

interface RecallStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  completed: boolean;
  required: boolean;
}

interface RecallFormData {
  // Step 1: Issue Discovery
  issue_type: string;
  issue_description: string;
  issue_severity: 'low' | 'medium' | 'high' | 'critical';
  issue_detected_date: string;
  issue_detected_by: string;
  issue_location: string;
  
  // Step 2: Risk Assessment
  health_risk_level: 'class_i' | 'class_ii' | 'class_iii';
  affected_population: string;
  potential_health_effects: string;
  risk_factors: string[];
  risk_score: number;
  
  // Step 3: Affected Products
  affected_batches: number[];
  affected_products: string[];
  distribution_locations: string[];
  quantity_affected: number;
  unit_of_measure: string;
  
  // Step 4: Communication Strategy
  stakeholders_to_notify: string[];
  communication_channels: string[];
  urgency_level: 'immediate' | 'urgent' | 'standard';
  regulatory_notification_required: boolean;
  
  // Step 5: Action Plan
  recall_type: 'voluntary' | 'mandatory' | 'market_withdrawal';
  recall_strategy: string;
  timeline: {
    start_date: string;
    target_completion_date: string;
    verification_date: string;
  };
  corrective_actions: string[];
  
  // Step 6: Effectiveness Verification
  verification_methods: string[];
  success_criteria: string[];
  monitoring_frequency: string;
  reporting_requirements: string[];
}

const SmartRecallWizard: React.FC<SmartRecallWizardProps> = ({
  onComplete,
  onCancel,
  initialData
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'lg'));
  
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<RecallFormData>({
    // Step 1: Issue Discovery
    issue_type: '',
    issue_description: '',
    issue_severity: 'medium',
    issue_detected_date: new Date().toISOString().split('T')[0],
    issue_detected_by: '',
    issue_location: '',
    
    // Step 2: Risk Assessment
    health_risk_level: 'class_ii',
    affected_population: '',
    potential_health_effects: '',
    risk_factors: [],
    risk_score: 50,
    
    // Step 3: Affected Products
    affected_batches: [],
    affected_products: [],
    distribution_locations: [],
    quantity_affected: 0,
    unit_of_measure: 'units',
    
    // Step 4: Communication Strategy
    stakeholders_to_notify: [],
    communication_channels: [],
    urgency_level: 'standard',
    regulatory_notification_required: false,
    
    // Step 5: Action Plan
    recall_type: 'voluntary',
    recall_strategy: '',
    timeline: {
      start_date: new Date().toISOString().split('T')[0],
      target_completion_date: '',
      verification_date: ''
    },
    corrective_actions: [],
    
    // Step 6: Effectiveness Verification
    verification_methods: [],
    success_criteria: [],
    monitoring_frequency: 'daily',
    reporting_requirements: []
  });

  const [batches, setBatches] = useState<any[]>([]);
  const [showSummary, setShowSummary] = useState(false);

  // Predefined options
  const issueTypes = [
    'Contamination',
    'Allergen Mislabeling',
    'Quality Defect',
    'Packaging Issue',
    'Temperature Deviation',
    'Cross-Contamination',
    'Foreign Object',
    'Microbiological Issue',
    'Chemical Contamination',
    'Other'
  ];

  const riskFactors = [
    'Vulnerable Populations',
    'Wide Distribution',
    'Long Shelf Life',
    'High Consumption Rate',
    'Previous Incidents',
    'Regulatory Violations',
    'Supplier Issues',
    'Process Failures'
  ];

  const stakeholders = [
    'Customers',
    'Retailers',
    'Distributors',
    'Regulatory Authorities',
    'Media',
    'Healthcare Providers',
    'Consumer Groups',
    'Industry Associations'
  ];

  const communicationChannels = [
    'Press Release',
    'Direct Customer Notification',
    'Social Media',
    'Website Announcement',
    'Email Campaign',
    'Phone Calls',
    'SMS Alerts',
    'Trade Publications'
  ];

  const verificationMethods = [
    'Product Returns Tracking',
    'Customer Feedback Analysis',
    'Sales Data Monitoring',
    'Inventory Audits',
    'Customer Surveys',
    'Regulatory Compliance Checks',
    'Third-Party Verification',
    'Internal Audits'
  ];

  const successCriteria = [
    '95% Product Recovery Rate',
    'Zero Additional Illnesses',
    'Regulatory Compliance',
    'Customer Satisfaction',
    'Timeline Adherence',
    'Cost Control',
    'Reputation Protection',
    'Process Improvement'
  ];

  const steps: RecallStep[] = [
    {
      id: 'discovery',
      title: 'Issue Discovery',
      description: 'Identify and document the safety issue',
      icon: <WarningIcon />,
      completed: false,
      required: true
    },
    {
      id: 'assessment',
      title: 'Risk Assessment',
      description: 'Evaluate health risks and classify recall',
      icon: <AssessmentIcon />,
      completed: false,
      required: true
    },
    {
      id: 'products',
      title: 'Affected Products',
      description: 'Identify impacted batches and products',
      icon: <InventoryIcon />,
      completed: false,
      required: true
    },
    {
      id: 'communication',
      title: 'Communication Strategy',
      description: 'Plan stakeholder notifications',
      icon: <NotificationsIcon />,
      completed: false,
      required: true
    },
    {
      id: 'action',
      title: 'Action Plan',
      description: 'Define recall strategy and timeline',
      icon: <TimelineIcon />,
      completed: false,
      required: true
    },
    {
      id: 'verification',
      title: 'Effectiveness Verification',
      description: 'Set up monitoring and success criteria',
      icon: <VerifiedUserIcon />,
      completed: false,
      required: true
    }
  ];

  useEffect(() => {
    // Load batches for selection
    loadBatches();
  }, []);

  const loadBatches = async () => {
    try {
      const response = await traceabilityAPI.getBatches({ size: 100 });
      setBatches(response.items || []);
    } catch (err) {
      console.error('Failed to load batches:', err);
    }
  };

  const updateFormData = (field: keyof RecallFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const updateNestedFormData = (field: keyof RecallFormData, nestedField: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: {
        ...prev[field],
        [nestedField]: value
      }
    }));
  };

  const validateStep = (stepIndex: number): boolean => {
    const step = steps[stepIndex];
    
    switch (step.id) {
      case 'discovery':
        return !!(formData.issue_type && formData.issue_description && formData.issue_detected_date);
      case 'assessment':
        return !!(formData.health_risk_level && formData.affected_population && formData.potential_health_effects);
      case 'products':
        return !!(formData.affected_batches.length > 0 && formData.affected_products.length > 0);
      case 'communication':
        return !!(formData.stakeholders_to_notify.length > 0 && formData.communication_channels.length > 0);
      case 'action':
        return !!(formData.recall_type && formData.recall_strategy && formData.timeline.target_completion_date);
      case 'verification':
        return !!(formData.verification_methods.length > 0 && formData.success_criteria.length > 0);
      default:
        return true;
    }
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      // Mark current step as completed
      steps[activeStep].completed = true;
      
      if (activeStep === steps.length - 1) {
        setShowSummary(true);
      } else {
        setActiveStep(prev => prev + 1);
      }
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      // Create recall with all the collected data
      const recallData = {
        ...formData,
        status: 'draft',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const response = await traceabilityAPI.createRecall(recallData);
      
      // Classify the recall based on risk assessment
      if (response.data?.id) {
        await traceabilityAPI.classifyRecall(response.data.id, {
          health_risk_level: formData.health_risk_level,
          affected_population: formData.affected_population,
          potential_health_effects: formData.potential_health_effects,
          risk_factors: formData.risk_factors,
          risk_score: formData.risk_score
        });
      }

      onComplete?.(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create recall');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = (stepIndex: number) => {
    const step = steps[stepIndex];
    
    switch (step.id) {
      case 'discovery':
        return (
          <Box>
            <Typography variant="h6" mb={3}>
              Issue Discovery
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Issue Type</InputLabel>
                  <Select
                    value={formData.issue_type}
                    onChange={(e) => updateFormData('issue_type', e.target.value)}
                    label="Issue Type"
                  >
                    {issueTypes.map(type => (
                      <MenuItem key={type} value={type}>{type}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Severity Level</InputLabel>
                  <Select
                    value={formData.issue_severity}
                    onChange={(e) => updateFormData('issue_severity', e.target.value)}
                    label="Severity Level"
                  >
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="critical">Critical</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Issue Description"
                  value={formData.issue_description}
                  onChange={(e) => updateFormData('issue_description', e.target.value)}
                  required
                  helperText="Provide a detailed description of the issue, including any relevant observations or test results"
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Issue Detected Date"
                  value={formData.issue_detected_date}
                  onChange={(e) => updateFormData('issue_detected_date', e.target.value)}
                  required
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Detected By"
                  value={formData.issue_detected_by}
                  onChange={(e) => updateFormData('issue_detected_by', e.target.value)}
                  required
                  helperText="Name or department that discovered the issue"
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Issue Location"
                  value={formData.issue_location}
                  onChange={(e) => updateFormData('issue_location', e.target.value)}
                  helperText="Where the issue was detected (facility, process step, etc.)"
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 'assessment':
        return (
          <Box>
            <Typography variant="h6" mb={3}>
              Risk Assessment
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Health Risk Level</InputLabel>
                  <Select
                    value={formData.health_risk_level}
                    onChange={(e) => updateFormData('health_risk_level', e.target.value)}
                    label="Health Risk Level"
                  >
                    <MenuItem value="class_i">Class I - High Risk</MenuItem>
                    <MenuItem value="class_ii">Class II - Moderate Risk</MenuItem>
                    <MenuItem value="class_iii">Class III - Low Risk</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Affected Population"
                  value={formData.affected_population}
                  onChange={(e) => updateFormData('affected_population', e.target.value)}
                  required
                  helperText="Describe the population at risk"
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Potential Health Effects"
                  value={formData.potential_health_effects}
                  onChange={(e) => updateFormData('potential_health_effects', e.target.value)}
                  required
                  helperText="Describe potential health consequences"
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormLabel component="legend">Risk Factors</FormLabel>
                <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                  {riskFactors.map(factor => (
                    <Chip
                      key={factor}
                      label={factor}
                      onClick={() => {
                        const current = formData.risk_factors;
                        const updated = current.includes(factor)
                          ? current.filter(f => f !== factor)
                          : [...current, factor];
                        updateFormData('risk_factors', updated);
                      }}
                      color={formData.risk_factors.includes(factor) ? 'primary' : 'default'}
                      variant={formData.risk_factors.includes(factor) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
              </Grid>
              
              <Grid item xs={12}>
                <Typography gutterBottom>Risk Score: {formData.risk_score}</Typography>
                <Slider
                  value={formData.risk_score}
                  onChange={(_, value) => updateFormData('risk_score', value)}
                  min={0}
                  max={100}
                  marks={[
                    { value: 0, label: 'Low' },
                    { value: 50, label: 'Medium' },
                    { value: 100, label: 'High' }
                  ]}
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 'products':
        return (
          <Box>
            <Typography variant="h6" mb={3}>
              Affected Products
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Autocomplete
                  multiple
                  options={batches}
                  getOptionLabel={(option) => `${option.batch_number} - ${option.product_name}`}
                  value={batches.filter(batch => formData.affected_batches.includes(batch.id))}
                  onChange={(_, newValue) => {
                    const batchIds = newValue.map(batch => batch.id);
                    const productNames = newValue.map(batch => batch.product_name);
                    updateFormData('affected_batches', batchIds);
                    updateFormData('affected_products', productNames);
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Affected Batches"
                      required
                      helperText="Select all batches affected by this issue"
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Quantity Affected"
                  value={formData.quantity_affected}
                  onChange={(e) => updateFormData('quantity_affected', Number(e.target.value))}
                  required
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Unit of Measure</InputLabel>
                  <Select
                    value={formData.unit_of_measure}
                    onChange={(e) => updateFormData('unit_of_measure', e.target.value)}
                    label="Unit of Measure"
                  >
                    <MenuItem value="units">Units</MenuItem>
                    <MenuItem value="kg">Kilograms</MenuItem>
                    <MenuItem value="liters">Liters</MenuItem>
                    <MenuItem value="cases">Cases</MenuItem>
                    <MenuItem value="pallets">Pallets</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Distribution Locations"
                  value={formData.distribution_locations.join(', ')}
                  onChange={(e) => updateFormData('distribution_locations', e.target.value.split(',').map(s => s.trim()))}
                  helperText="Enter distribution locations separated by commas"
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 'communication':
        return (
          <Box>
            <Typography variant="h6" mb={3}>
              Communication Strategy
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormLabel component="legend">Stakeholders to Notify</FormLabel>
                <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                  {stakeholders.map(stakeholder => (
                    <Chip
                      key={stakeholder}
                      label={stakeholder}
                      onClick={() => {
                        const current = formData.stakeholders_to_notify;
                        const updated = current.includes(stakeholder)
                          ? current.filter(s => s !== stakeholder)
                          : [...current, stakeholder];
                        updateFormData('stakeholders_to_notify', updated);
                      }}
                      color={formData.stakeholders_to_notify.includes(stakeholder) ? 'primary' : 'default'}
                      variant={formData.stakeholders_to_notify.includes(stakeholder) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
              </Grid>
              
              <Grid item xs={12}>
                <FormLabel component="legend">Communication Channels</FormLabel>
                <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                  {communicationChannels.map(channel => (
                    <Chip
                      key={channel}
                      label={channel}
                      onClick={() => {
                        const current = formData.communication_channels;
                        const updated = current.includes(channel)
                          ? current.filter(c => c !== channel)
                          : [...current, channel];
                        updateFormData('communication_channels', updated);
                      }}
                      color={formData.communication_channels.includes(channel) ? 'primary' : 'default'}
                      variant={formData.communication_channels.includes(channel) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Urgency Level</InputLabel>
                  <Select
                    value={formData.urgency_level}
                    onChange={(e) => updateFormData('urgency_level', e.target.value)}
                    label="Urgency Level"
                  >
                    <MenuItem value="immediate">Immediate</MenuItem>
                    <MenuItem value="urgent">Urgent</MenuItem>
                    <MenuItem value="standard">Standard</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.regulatory_notification_required}
                      onChange={(e) => updateFormData('regulatory_notification_required', e.target.checked)}
                    />
                  }
                  label="Regulatory Notification Required"
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 'action':
        return (
          <Box>
            <Typography variant="h6" mb={3}>
              Action Plan
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Recall Type</InputLabel>
                  <Select
                    value={formData.recall_type}
                    onChange={(e) => updateFormData('recall_type', e.target.value)}
                    label="Recall Type"
                  >
                    <MenuItem value="voluntary">Voluntary Recall</MenuItem>
                    <MenuItem value="mandatory">Mandatory Recall</MenuItem>
                    <MenuItem value="market_withdrawal">Market Withdrawal</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Target Completion Date"
                  value={formData.timeline.target_completion_date}
                  onChange={(e) => updateNestedFormData('timeline', 'target_completion_date', e.target.value)}
                  required
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Recall Strategy"
                  value={formData.recall_strategy}
                  onChange={(e) => updateFormData('recall_strategy', e.target.value)}
                  required
                  helperText="Describe the approach for executing the recall, including logistics and coordination"
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Corrective Actions"
                  value={formData.corrective_actions.join('\n')}
                  onChange={(e) => updateFormData('corrective_actions', e.target.value.split('\n').filter(s => s.trim()))}
                  helperText="Enter corrective actions, one per line"
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Verification Date"
                  value={formData.timeline.verification_date}
                  onChange={(e) => updateNestedFormData('timeline', 'verification_date', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 'verification':
        return (
          <Box>
            <Typography variant="h6" mb={3}>
              Effectiveness Verification
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormLabel component="legend">Verification Methods</FormLabel>
                <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                  {verificationMethods.map(method => (
                    <Chip
                      key={method}
                      label={method}
                      onClick={() => {
                        const current = formData.verification_methods;
                        const updated = current.includes(method)
                          ? current.filter(m => m !== method)
                          : [...current, method];
                        updateFormData('verification_methods', updated);
                      }}
                      color={formData.verification_methods.includes(method) ? 'primary' : 'default'}
                      variant={formData.verification_methods.includes(method) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
              </Grid>
              
              <Grid item xs={12}>
                <FormLabel component="legend">Success Criteria</FormLabel>
                <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                  {successCriteria.map(criterion => (
                    <Chip
                      key={criterion}
                      label={criterion}
                      onClick={() => {
                        const current = formData.success_criteria;
                        const updated = current.includes(criterion)
                          ? current.filter(c => c !== criterion)
                          : [...current, criterion];
                        updateFormData('success_criteria', updated);
                      }}
                      color={formData.success_criteria.includes(criterion) ? 'primary' : 'default'}
                      variant={formData.success_criteria.includes(criterion) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Monitoring Frequency</InputLabel>
                  <Select
                    value={formData.monitoring_frequency}
                    onChange={(e) => updateFormData('monitoring_frequency', e.target.value)}
                    label="Monitoring Frequency"
                  >
                    <MenuItem value="hourly">Hourly</MenuItem>
                    <MenuItem value="daily">Daily</MenuItem>
                    <MenuItem value="weekly">Weekly</MenuItem>
                    <MenuItem value="monthly">Monthly</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Reporting Requirements"
                  value={formData.reporting_requirements.join(', ')}
                  onChange={(e) => updateFormData('reporting_requirements', e.target.value.split(',').map(s => s.trim()))}
                  helperText="Enter reporting requirements separated by commas"
                />
              </Grid>
            </Grid>
          </Box>
        );

      default:
        return null;
    }
  };

  const renderSummary = () => (
    <Dialog open={showSummary} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={2}>
          <CheckCircleIcon color="primary" />
          <Typography variant="h6">Recall Summary</Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" mb={2}>Issue Details</Typography>
            <Paper sx={{ p: 2, mb: 2 }}>
              <Typography><strong>Type:</strong> {formData.issue_type}</Typography>
              <Typography><strong>Severity:</strong> {formData.issue_severity}</Typography>
              <Typography><strong>Description:</strong> {formData.issue_description}</Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography variant="h6" mb={2}>Risk Assessment</Typography>
            <Paper sx={{ p: 2 }}>
              <Typography><strong>Health Risk:</strong> {formData.health_risk_level}</Typography>
              <Typography><strong>Risk Score:</strong> {formData.risk_score}</Typography>
              <Typography><strong>Affected Population:</strong> {formData.affected_population}</Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography variant="h6" mb={2}>Products</Typography>
            <Paper sx={{ p: 2 }}>
              <Typography><strong>Batches:</strong> {formData.affected_batches.length}</Typography>
              <Typography><strong>Quantity:</strong> {formData.quantity_affected} {formData.unit_of_measure}</Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="h6" mb={2}>Action Plan</Typography>
            <Paper sx={{ p: 2 }}>
              <Typography><strong>Recall Type:</strong> {formData.recall_type}</Typography>
              <Typography><strong>Strategy:</strong> {formData.recall_strategy}</Typography>
              <Typography><strong>Target Completion:</strong> {formData.timeline.target_completion_date}</Typography>
            </Paper>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowSummary(false)}>Back to Edit</Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
        >
          {loading ? 'Creating Recall...' : 'Create Recall'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Card sx={{ 
      width: '100%',
      borderRadius: { xs: 1, sm: 2 },
      boxShadow: { xs: 1, sm: 2 }
    }}>
      <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
        <Box 
          display="flex" 
          flexDirection={{ xs: 'column', sm: 'row' }}
          alignItems={{ xs: 'flex-start', sm: 'center' }} 
          gap={2} 
          mb={3}
        >
          <WarningIcon 
            color="primary" 
            sx={{ 
              fontSize: { xs: 24, sm: 32 },
              flexShrink: 0
            }} 
            aria-hidden="true"
          />
          <Box flex={1}>
            <Typography 
              variant="h5" 
              fontWeight={600}
              sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem' } }}
            >
              Smart Recall Wizard
            </Typography>
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
            >
              Step-by-step recall creation with intelligent guidance
            </Typography>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Stepper 
          activeStep={activeStep} 
          orientation={isMobile ? "vertical" : "vertical"}
          sx={{
            '& .MuiStepLabel-root': {
              padding: { xs: 1, sm: 2 }
            }
          }}
        >
          {steps.map((step, index) => (
            <Step key={step.id}>
              <StepLabel
                StepIconComponent={() => (
                  <Box
                    sx={{
                      width: { xs: 28, sm: 32 },
                      height: { xs: 28, sm: 32 },
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: step.completed ? 'success.main' : 'primary.main',
                      color: 'white',
                      fontSize: { xs: '0.875rem', sm: '1rem' }
                    }}
                    aria-label={`Step ${index + 1}: ${step.title}`}
                  >
                    {step.completed ? <CheckCircleIcon /> : step.icon}
                  </Box>
                )}
              >
                <Typography 
                  variant="h6"
                  sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
                >
                  {step.title}
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {step.description}
                </Typography>
              </StepLabel>
              <StepContent>
                {renderStepContent(index)}
                
                <Box 
                  sx={{ 
                    mt: 3, 
                    display: 'flex', 
                    flexDirection: { xs: 'column', sm: 'row' },
                    gap: 2 
                  }}
                >
                  <Button
                    disabled={index === 0}
                    onClick={handleBack}
                    startIcon={<ArrowBackIcon />}
                    size={isMobile ? "large" : "medium"}
                    sx={{ 
                      minHeight: { xs: 48, sm: 40 },
                      order: { xs: 2, sm: 1 }
                    }}
                    aria-label="Go to previous step"
                  >
                    Back
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    endIcon={index === steps.length - 1 ? <SaveIcon /> : <ArrowForwardIcon />}
                    disabled={!validateStep(index)}
                    size={isMobile ? "large" : "medium"}
                    sx={{ 
                      minHeight: { xs: 48, sm: 40 },
                      order: { xs: 1, sm: 2 }
                    }}
                    aria-label={index === steps.length - 1 ? "Review and create recall" : "Go to next step"}
                  >
                    {index === steps.length - 1 ? 'Review & Create' : 'Next'}
                  </Button>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>

        {renderSummary()}

        {/* Mobile Speed Dial for Quick Actions */}
        {isMobile && (
          <SpeedDial
            ariaLabel="Quick actions"
            sx={{ 
              position: 'fixed', 
              bottom: 16, 
              right: 16,
              zIndex: theme.zIndex.speedDial
            }}
            icon={<SpeedDialIcon />}
          >
            <SpeedDialAction
              icon={<ArrowBackIcon />}
              tooltipTitle="Previous Step"
              onClick={handleBack}
              disabled={activeStep === 0}
              aria-label="Go to previous step"
            />
            <SpeedDialAction
              icon={<ArrowForwardIcon />}
              tooltipTitle="Next Step"
              onClick={handleNext}
              disabled={!validateStep(activeStep)}
              aria-label="Go to next step"
            />
            <SpeedDialAction
              icon={<SaveIcon />}
              tooltipTitle="Save Progress"
              onClick={() => {/* TODO: Implement save progress */}}
              aria-label="Save progress"
            />
          </SpeedDial>
        )}
      </CardContent>
    </Card>
  );
};

export default SmartRecallWizard;
