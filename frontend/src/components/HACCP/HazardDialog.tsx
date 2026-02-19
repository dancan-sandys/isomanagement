import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography,
  Box,
  Card,
  CardContent,
  IconButton,
  Chip,
  Divider,
  Alert,
  Paper,
  RadioGroup,
  FormControlLabel,
  Radio,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  CheckCircle,
} from '@mui/icons-material';

interface Reference {
  id?: string;
  title: string;
  url: string;
  type: 'document' | 'website' | 'standard' | 'regulation' | 'guideline';
  description?: string;
}

type RiskStrategyType = 'ccp' | 'opprp' | 'use_existing_prps' | 'further_analysis' | '';

interface HazardFormData {
  process_step_id: string;
  hazard_type: 'biological' | 'chemical' | 'physical' | 'allergen';
  hazard_name: string;
  description: string;
  consequences?: string;
  prp_reference_ids: number[];
  references: Reference[];
  likelihood: string;
  severity: string;
  control_measures: string;
  risk_strategy: RiskStrategyType;
  risk_strategy_justification?: string;
  subsequent_step?: string;
}

interface CCPFormData {
  ccp_number: string;
  ccp_name: string;
  description: string;
  critical_limit_min: string;
  critical_limit_max: string;
  critical_limit_unit: string;
  monitoring_frequency: string;
  monitoring_method: string;
  corrective_actions: string;
}

interface OPRPFormData {
  oprp_number: string;
  oprp_name: string;
  description: string;
  objective: string;
  sop_reference: string;
}

interface DecisionTreeAnswers {
  q1_answer?: boolean;
  q2_answer?: boolean;
  q3_answer?: boolean;
  q4_answer?: boolean;
  q5_answer?: boolean;
}

interface HazardDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: HazardFormData & { decision_tree?: DecisionTreeAnswers; ccp?: CCPFormData; oprp?: OPRPFormData }) => void;
  processFlows: Array<{ id: number; step_number: number; step_name: string }>;
  editData?: any;
  viewMode?: boolean; // If true, dialog is read-only
}

const DECISION_TREE_QUESTIONS = [
  {
    question: 'Q1: Based on the Risk Assessment (RA), is this hazard significant (needs to be controlled)?',
    helpText: 'Consider if this hazard requires control measures to ensure food safety.',
    yesAction: 'This is a significant hazard. Proceed to Q2.',
    noAction: 'This is not a significant hazard.',
  },
  {
    question: 'Q2: Will a subsequent processing step, including expected use by consumer, guarantee the removal of this Significant Hazard, or its reduction to an acceptable level?',
    helpText: 'Consider if any later processing step will effectively control this hazard.',
    yesAction: 'Identify and name the subsequent step.',
    noAction: 'No subsequent step controls this hazard. Proceed to Q3.',
  },
  {
    question: 'Q3: Are there control measures or practices in place at this step, and do they exclude, reduce or maintain this Significant Hazard to/at an acceptable level?',
    helpText: 'Evaluate if current control measures at this step are effective.',
    yesAction: 'Control measures are in place. Proceed to Q4.',
    noAction: 'Modify the process or product and return to Q1.',
  },
  {
    question: 'Q4: Is it possible to establish critical limits for the control measure at this step?',
    helpText: 'Determine if measurable critical limits can be established.',
    yesAction: 'Critical limits can be established. Proceed to Q5.',
    noAction: 'This hazard is managed by an OPRP.',
  },
  {
    question: 'Q5: Is it possible to monitor the control measure in such a way that corrective actions can be taken immediately when there is a loss of control?',
    helpText: 'Assess if monitoring allows for immediate corrective action.',
    yesAction: 'This hazard is managed by the HACCP-plan (CCP).',
    noAction: 'This hazard is managed by an OPRP.',
  },
];

const HazardDialog: React.FC<HazardDialogProps> = ({
  open,
  onClose,
  onSave,
  processFlows,
  editData,
  viewMode = false,
}) => {
  const [formData, setFormData] = useState<HazardFormData>({
    process_step_id: '',
    hazard_type: 'biological',
    hazard_name: '',
    description: '',
    consequences: '',
    prp_reference_ids: [],
    references: [],
    likelihood: '1',
    severity: '1',
    control_measures: '',
    risk_strategy: '',  // Empty string to keep RadioGroup controlled
    risk_strategy_justification: '',
    subsequent_step: '',
  });

  const [referenceForm, setReferenceForm] = useState<Reference>({
    title: '',
    url: '',
    type: 'document',
    description: '',
  });

  const [decisionTreeOpen, setDecisionTreeOpen] = useState(false);
  const [decisionTreeAnswers, setDecisionTreeAnswers] = useState<DecisionTreeAnswers>({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [subsequentStepName, setSubsequentStepName] = useState('');
  const [riskScore, setRiskScore] = useState(0);
  const [riskLevel, setRiskLevel] = useState<'low' | 'medium' | 'high' | 'critical'>('low');
  const [autoRiskStrategy, setAutoRiskStrategy] = useState<'ccp' | 'opprp' | 'use_existing_prps' | 'further_analysis'>('use_existing_prps');
  const [strategyLocked, setStrategyLocked] = useState(false);

  // CCP/OPRP Form Data
  const [ccpForm, setCcpForm] = useState<CCPFormData>({
    ccp_number: '',
    ccp_name: '',
    description: '',
    critical_limit_min: '',
    critical_limit_max: '',
    critical_limit_unit: '',
    monitoring_frequency: '',
    monitoring_method: '',
    corrective_actions: '',
  });

  const [oprpForm, setOprpForm] = useState<OPRPFormData>({
    oprp_number: '',
    oprp_name: '',
    description: '',
    objective: '',
    sop_reference: '',
  });

  // Calculate risk score and level when likelihood or severity changes
  useEffect(() => {
    const likelihood = parseInt(formData.likelihood) || 1;
    const severity = parseInt(formData.severity) || 1;
    const score = likelihood * severity;
    setRiskScore(score);

    let level: 'low' | 'medium' | 'high' | 'critical';
    let strategy: 'ccp' | 'opprp' | 'use_existing_prps' | 'further_analysis';

    if (score <= 4) {
      level = 'low';
      strategy = 'use_existing_prps';  // Low risks use existing PRPs
    } else if (score <= 8) {
      level = 'medium';
      strategy = 'opprp';
    } else if (score <= 15) {
      level = 'high';
      strategy = 'further_analysis';
    } else {
      level = 'critical';
      strategy = 'further_analysis';
    }

    setRiskLevel(level);
    setAutoRiskStrategy(strategy);

    // Auto-set risk strategy if not manually changed
    if (!formData.risk_strategy) {
      setFormData(prev => ({ ...prev, risk_strategy: strategy }));
    }
  }, [formData.likelihood, formData.severity, formData.risk_strategy]);

  useEffect(() => {
    if (editData) {
      setFormData({
        process_step_id: editData.process_step_id?.toString() || '',
        hazard_type: editData.hazard_type || 'biological',
        hazard_name: editData.hazard_name || '',
        description: editData.description || '',
        consequences: editData.consequences || '',
        prp_reference_ids: editData.prp_reference_ids || [],
        references: editData.references || [],
        likelihood: editData.likelihood?.toString() || '1',
        severity: editData.severity?.toString() || '1',
        control_measures: editData.control_measures || '',
        risk_strategy: editData.risk_strategy,
        risk_strategy_justification: editData.risk_strategy_justification || '',
        subsequent_step: editData.subsequent_step || '',
      });
      if (editData.risk_strategy) {
        setStrategyLocked(true);
      }
    } else {
      // Reset forms when opening for new hazard
      setCcpForm({
        ccp_number: '',
        ccp_name: '',
        description: '',
        critical_limit_min: '',
        critical_limit_max: '',
        critical_limit_unit: '',
        monitoring_frequency: '',
        monitoring_method: '',
        corrective_actions: '',
      });
      setOprpForm({
        oprp_number: '',
        oprp_name: '',
        description: '',
        objective: '',
        sop_reference: '',
      });
    }
  }, [editData, open]);

  // Auto-populate CCP/OPRP name from hazard name when strategy is locked
  useEffect(() => {
    if (strategyLocked && formData.hazard_name) {
      if (formData.risk_strategy === 'ccp' && !ccpForm.ccp_name) {
        setCcpForm(prev => ({
          ...prev,
          ccp_name: formData.hazard_name,
          description: `CCP for ${formData.hazard_name}`,
        }));
      } else if (formData.risk_strategy === 'opprp' && !oprpForm.oprp_name) {
        setOprpForm(prev => ({
          ...prev,
          oprp_name: formData.hazard_name,
          description: `OPRP for ${formData.hazard_name}`,
        }));
      }
    }
  }, [strategyLocked, formData.hazard_name, formData.risk_strategy, ccpForm.ccp_name, oprpForm.oprp_name]);

  const handleInputChange = (field: keyof HazardFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const addReference = () => {
    if (referenceForm.title.trim() && referenceForm.url.trim()) {
      const newReference = {
        ...referenceForm,
        id: `ref-${Date.now()}`,
      };
      setFormData(prev => ({
        ...prev,
        references: [...prev.references, newReference],
      }));
      setReferenceForm({
        title: '',
        url: '',
        type: 'document',
        description: '',
      });
    }
  };

  const removeReference = (index: number) => {
    setFormData(prev => ({
      ...prev,
      references: prev.references.filter((_, i) => i !== index),
    }));
  };

  const updateReference = (index: number, field: keyof Reference, value: any) => {
    setFormData(prev => ({
      ...prev,
      references: prev.references.map((ref, i) =>
        i === index ? { ...ref, [field]: value } : ref
      ),
    }));
  };

  const handleRiskStrategyChange = (strategy: 'ccp' | 'opprp' | 'use_existing_prps' | 'further_analysis') => {
    if (strategy === 'further_analysis') {
      // Open decision tree dialog
      setDecisionTreeOpen(true);
      setCurrentQuestion(0);
      setSubsequentStepName('');
      setDecisionTreeAnswers({});
    } else {
      // Directly set the strategy and lock it
      setFormData(prev => ({ ...prev, risk_strategy: strategy }));
      setStrategyLocked(true);
    }
  };

  const handleCancelStrategy = () => {
    setFormData(prev => ({ ...prev, risk_strategy: '', risk_strategy_justification: '', subsequent_step: '' }));
    setStrategyLocked(false);
    // Reset CCP/OPRP forms
    setCcpForm({
      ccp_number: '',
      ccp_name: '',
      description: '',
      critical_limit_min: '',
      critical_limit_max: '',
      critical_limit_unit: '',
      monitoring_frequency: '',
      monitoring_method: '',
      corrective_actions: '',
    });
    setOprpForm({
      oprp_number: '',
      oprp_name: '',
      description: '',
      objective: '',
      sop_reference: '',
    });
  };

  // Auto-populate CCP/OPRP form when strategy is locked
  useEffect(() => {
    if (strategyLocked && formData.risk_strategy) {
      if (formData.risk_strategy === 'ccp') {
        setCcpForm(prev => ({
          ...prev,
          ccp_name: prev.ccp_name || formData.hazard_name,
          description: prev.description || `CCP for ${formData.hazard_name}`,
        }));
      } else if (formData.risk_strategy === 'opprp') {
        setOprpForm(prev => ({
          ...prev,
          oprp_name: prev.oprp_name || formData.hazard_name,
          description: prev.description || `OPRP for ${formData.hazard_name}`,
        }));
      }
    }
  }, [strategyLocked, formData.risk_strategy, formData.hazard_name]);

  const handleDecisionTreeAnswer = (answer: boolean) => {
    const questionKey = `q${currentQuestion + 1}_answer` as keyof DecisionTreeAnswers;

    const newAnswers = {
      ...decisionTreeAnswers,
      [questionKey]: answer,
    };

    setDecisionTreeAnswers(newAnswers);

    // Decision tree logic based on the specific questions
    if (currentQuestion === 0 && !answer) {
      // Q1: No - Not a significant hazard (Use Existing PRPs)
      setFormData(prev => ({ 
        ...prev, 
        risk_strategy: 'use_existing_prps',
        risk_strategy_justification: 'Not a significant hazard based on risk assessment.'
      }));
      setStrategyLocked(true);
      setDecisionTreeOpen(false);
      return;
    }

    if (currentQuestion === 1) {
      if (answer) {
        // Q2: Yes - Subsequent step controls (Use Existing PRPs)
        setFormData(prev => ({ 
          ...prev, 
          risk_strategy: 'use_existing_prps',
          risk_strategy_justification: `Subsequent step (${subsequentStepName}) will control this hazard.`,
          subsequent_step: subsequentStepName
        }));
        setStrategyLocked(true);
      setDecisionTreeOpen(false);
      setSubsequentStepName('');
      return;
      }
      // Q2: No - Move to Q3
    }

    if (currentQuestion === 2 && !answer) {
      // Q3: No - Need to modify process
      alert('Control measures are not adequate. Please modify the process or product and reassess.');
      setDecisionTreeOpen(false);
      return;
    }

    if (currentQuestion === 3 && !answer) {
      // Q4: No - Cannot establish critical limits (OPRP)
      setFormData(prev => ({ 
        ...prev, 
        risk_strategy: 'opprp',
        risk_strategy_justification: 'Critical limits cannot be established for this control measure.'
      }));
      setStrategyLocked(true);
      setDecisionTreeOpen(false);
      return;
    }

    if (currentQuestion === 4) {
      // Q5: Final question
      if (answer) {
        // Q5: Yes - Can monitor immediately (CCP)
        setFormData(prev => ({ 
          ...prev, 
          risk_strategy: 'ccp',
          risk_strategy_justification: 'Monitoring allows immediate corrective action - managed by HACCP plan (CCP).'
        }));
      } else {
        // Q5: No - Cannot monitor immediately (OPRP)
        setFormData(prev => ({ 
          ...prev, 
          risk_strategy: 'opprp',
          risk_strategy_justification: 'Immediate monitoring not possible - managed by OPRP.'
        }));
      }
      setStrategyLocked(true);
      setDecisionTreeOpen(false);
      return;
    }

    // Move to next question
    setCurrentQuestion(prev => prev + 1);
  };

  const handleSave = () => {
    // Validate risk strategy is selected
    if (!formData.risk_strategy) {
      alert('Please select a risk strategy');
      return;
    }

    // Validate justification is required when decision tree was used
    if (Object.keys(decisionTreeAnswers).length > 0 && !formData.risk_strategy_justification?.trim()) {
      alert('Justification is required when using Further Analysis (Decision Tree)');
      return;
    }

    // Validate CCP/OPRP data if strategy is set
    if (formData.risk_strategy === 'ccp') {
      if (!ccpForm.ccp_number.trim()) {
        alert('CCP Number is required');
        return;
      }
      if (!ccpForm.ccp_name.trim()) {
        alert('CCP Name is required');
        return;
      }
    } else if (formData.risk_strategy === 'opprp') {
      if (!oprpForm.oprp_number.trim()) {
        alert('OPRP Number is required');
        return;
      }
      if (!oprpForm.oprp_name.trim()) {
        alert('OPRP Name is required');
        return;
      }
    }

    const saveData: HazardFormData & { decision_tree?: DecisionTreeAnswers; ccp?: CCPFormData; oprp?: OPRPFormData } = {
      ...formData,
      risk_strategy: formData.risk_strategy || undefined,  // Convert empty string to undefined for backend
    };

    // Include decision tree answers if further analysis was performed
    if (Object.keys(decisionTreeAnswers).length > 0) {
      saveData.decision_tree = decisionTreeAnswers;
    }

    // Include CCP data if strategy is CCP
    if (formData.risk_strategy === 'ccp') {
      saveData.ccp = ccpForm;
    }

    // Include OPRP data if strategy is OPRP
    if (formData.risk_strategy === 'opprp') {
      saveData.oprp = oprpForm;
    }

    onSave(saveData);
    handleClose();
  };

  const handleClose = () => {
    setFormData({
      process_step_id: '',
      hazard_type: 'biological',
      hazard_name: '',
      description: '',
      consequences: '',
      prp_reference_ids: [],
      references: [],
      likelihood: '1',
      severity: '1',
      control_measures: '',
      risk_strategy: '',
      risk_strategy_justification: '',
      subsequent_step: '',
    });
    setReferenceForm({
      title: '',
      url: '',
      type: 'document',
      description: '',
    });
    setCcpForm({
      ccp_number: '',
      ccp_name: '',
      description: '',
      critical_limit_min: '',
      critical_limit_max: '',
      critical_limit_unit: '',
      monitoring_frequency: '',
      monitoring_method: '',
      corrective_actions: '',
    });
    setOprpForm({
      oprp_number: '',
      oprp_name: '',
      description: '',
      objective: '',
      sop_reference: '',
    });
    setDecisionTreeAnswers({});
    setCurrentQuestion(0);
    setSubsequentStepName('');
    setStrategyLocked(false);
    onClose();
  };

  const getRiskLevelColor = () => {
    switch (riskLevel) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getRiskStrategyLabel = (strategy: string) => {
    switch (strategy) {
      case 'ccp':
        return 'CCP (Critical Control Point)';
      case 'opprp':
        return 'OPRP (Operational PRP)';
      case 'use_existing_prps':
        return 'Use Existing PRPs';
      case 'further_analysis':
        return 'Further Analysis Required';
      default:
        return 'Not Determined';
    }
  };

  return (
    <>
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>{viewMode ? 'View Hazard' : (editData ? 'Edit Hazard' : 'Add Hazard')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Process Step</InputLabel>
                <Select
                  value={formData.process_step_id}
                  label="Process Step"
                  onChange={(e) => handleInputChange('process_step_id', e.target.value)}
                  disabled={viewMode}
                >
                  {processFlows.map((flow) => (
                    <MenuItem key={flow.id} value={flow.id}>
                      {flow.step_number}. {flow.step_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Hazard Type</InputLabel>
                <Select
                  value={formData.hazard_type}
                  label="Hazard Type"
                  onChange={(e) => handleInputChange('hazard_type', e.target.value)}
                  disabled={viewMode}
                >
                  <MenuItem value="biological">Biological</MenuItem>
                  <MenuItem value="chemical">Chemical</MenuItem>
                  <MenuItem value="physical">Physical</MenuItem>
                  <MenuItem value="allergen">Allergen</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Hazard Name"
                value={formData.hazard_name}
                onChange={(e) => handleInputChange('hazard_name', e.target.value)}
                disabled={viewMode}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                disabled={viewMode}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Consequences (if hazard occurs)"
                value={formData.consequences}
                onChange={(e) => handleInputChange('consequences', e.target.value)}
                placeholder="Describe potential consequences if this hazard is not controlled"
                disabled={viewMode}
              />
            </Grid>

            {/* References */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                References
              </Typography>
            </Grid>

            {!viewMode && (
              <Grid item xs={12}>
                <Box sx={{ mb: 2 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        size="small"
                        label="Title"
                        value={referenceForm.title}
                        onChange={(e) => setReferenceForm({ ...referenceForm, title: e.target.value })}
                        placeholder="Reference title"
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        size="small"
                        label="URL"
                        value={referenceForm.url}
                        onChange={(e) => setReferenceForm({ ...referenceForm, url: e.target.value })}
                        placeholder="https://..."
                      />
                    </Grid>
                    <Grid item xs={12} md={2}>
                      <FormControl fullWidth size="small">
                        <InputLabel>Type</InputLabel>
                        <Select
                          value={referenceForm.type}
                          onChange={(e) => setReferenceForm({ ...referenceForm, type: e.target.value as any })}
                          label="Type"
                        >
                          <MenuItem value="document">Document</MenuItem>
                          <MenuItem value="website">Website</MenuItem>
                          <MenuItem value="standard">Standard</MenuItem>
                          <MenuItem value="regulation">Regulation</MenuItem>
                          <MenuItem value="guideline">Guideline</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        size="small"
                        label="Description"
                        value={referenceForm.description}
                        onChange={(e) => setReferenceForm({ ...referenceForm, description: e.target.value })}
                        placeholder="Brief description"
                      />
                    </Grid>
                    <Grid item xs={12} md={1}>
                      <Button
                        variant="contained"
                        size="small"
                        onClick={addReference}
                        disabled={!referenceForm.title.trim() || !referenceForm.url.trim()}
                        sx={{ height: '40px', minWidth: '40px' }}
                      >
                        <AddIcon />
                      </Button>
                    </Grid>
                  </Grid>
                </Box>
              </Grid>
            )}

              {formData.references.length > 0 && (
                <Grid item xs={12}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      {viewMode ? 'References' : `Added References (${formData.references.length})`}
                    </Typography>
                    {formData.references.map((ref, index) => (
                      <Card key={ref.id || index} sx={{ mb: 1, p: 1 }}>
                        <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
                          {viewMode ? (
                            <Box>
                              <Typography variant="body2" fontWeight="bold">{ref.title}</Typography>
                              <Typography variant="caption" color="textSecondary">
                                {ref.type} • {ref.description || 'No description'}
                              </Typography>
                              <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                                <a href={ref.url} target="_blank" rel="noopener noreferrer">{ref.url}</a>
                              </Typography>
                            </Box>
                          ) : (
                            <Grid container spacing={1} alignItems="center">
                              <Grid item xs={12} md={3}>
                                <TextField
                                  fullWidth
                                  size="small"
                                  label="Title"
                                  value={ref.title}
                                  onChange={(e) => updateReference(index, 'title', e.target.value)}
                                />
                              </Grid>
                              <Grid item xs={12} md={3}>
                                <TextField
                                  fullWidth
                                  size="small"
                                  label="URL"
                                  value={ref.url}
                                  onChange={(e) => updateReference(index, 'url', e.target.value)}
                                />
                              </Grid>
                              <Grid item xs={12} md={2}>
                                <FormControl fullWidth size="small">
                                  <InputLabel>Type</InputLabel>
                                  <Select
                                    value={ref.type || 'document'}
                                    onChange={(e) => updateReference(index, 'type', e.target.value)}
                                    label="Type"
                                  >
                                    <MenuItem value="document">Document</MenuItem>
                                    <MenuItem value="website">Website</MenuItem>
                                    <MenuItem value="standard">Standard</MenuItem>
                                    <MenuItem value="regulation">Regulation</MenuItem>
                                    <MenuItem value="guideline">Guideline</MenuItem>
                                  </Select>
                                </FormControl>
                              </Grid>
                              <Grid item xs={12} md={3}>
                                <TextField
                                  fullWidth
                                  size="small"
                                  label="Description"
                                  value={ref.description || ''}
                                  onChange={(e) => updateReference(index, 'description', e.target.value)}
                                />
                              </Grid>
                              <Grid item xs={12} md={1}>
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => removeReference(index)}
                                >
                                  <RemoveIcon />
                                </IconButton>
                              </Grid>
                            </Grid>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </Box>
                </Grid>
              )}

            {/* Risk Assessment */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Risk Assessment
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                required
                type="number"
                label="Likelihood (1-5)"
                value={formData.likelihood}
                onChange={(e) => handleInputChange('likelihood', e.target.value)}
                inputProps={{ min: 1, max: 5 }}
                disabled={viewMode}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                required
                type="number"
                label="Severity (1-5)"
                value={formData.severity}
                onChange={(e) => handleInputChange('severity', e.target.value)}
                inputProps={{ min: 1, max: 5 }}
                disabled={viewMode}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: getRiskLevelColor() === 'error' ? '#ffebee' : getRiskLevelColor() === 'warning' ? '#fff3e0' : getRiskLevelColor() === 'info' ? '#e3f2fd' : '#e8f5e9' }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Risk Score
                </Typography>
                <Typography variant="h4" color={getRiskLevelColor()}>
                  {riskScore}
                </Typography>
                <Chip
                  label={riskLevel.toUpperCase()}
                  color={getRiskLevelColor() as any}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </Paper>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Existing Control Measures"
                value={formData.control_measures}
                onChange={(e) => handleInputChange('control_measures', e.target.value)}
                placeholder="Describe existing control measures in place"
                disabled={viewMode}
              />
            </Grid>

            {/* Risk Strategy Selection */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Risk Strategy
              </Typography>
              {!viewMode && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Based on the risk level ({riskLevel.toUpperCase()}), the recommended strategy is:{' '}
                  <strong>{getRiskStrategyLabel(autoRiskStrategy)}</strong>
                </Alert>
              )}
            </Grid>

            {viewMode ? (
              <>
                <Grid item xs={12}>
                  <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                    <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                      Selected Strategy
                    </Typography>
                    <Chip 
                      label={getRiskStrategyLabel(formData.risk_strategy!)} 
                      color={
                        formData.risk_strategy === 'ccp' ? 'error' : 
                        formData.risk_strategy === 'opprp' ? 'warning' : 
                        'info'
                      }
                      sx={{ mb: 2 }}
                    />
                    
                    {formData.risk_strategy_justification && (
                      <>
                        <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ mt: 2 }}>
                          Justification
                        </Typography>
                        <Typography variant="body2">
                          {formData.risk_strategy_justification}
                        </Typography>
                      </>
                    )}
                    
                    {formData.subsequent_step && (
                      <>
                        <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ mt: 2 }}>
                          Subsequent Control Step
                        </Typography>
                        <Typography variant="body2">
                          {formData.subsequent_step}
                        </Typography>
                      </>
                    )}
                  </Paper>
                </Grid>
              </>
            ) : !strategyLocked ? (
              <Grid item xs={12}>
                <FormControl component="fieldset">
                  <RadioGroup
                    value={formData.risk_strategy}
                    onChange={(e) => handleRiskStrategyChange(e.target.value as any)}
                  >
                    <FormControlLabel
                      value="use_existing_prps"
                      control={<Radio />}
                      label={
                        <Box>
                          <Typography variant="body1">Use Existing PRPs</Typography>
                          <Typography variant="caption" color="textSecondary">
                            Hazard is controlled by existing Prerequisite Programs (recommended for low risks)
                          </Typography>
                        </Box>
                      }
                    />
                    <FormControlLabel
                      value="opprp"
                      control={<Radio />}
                      label={
                        <Box>
                          <Typography variant="body1">OPRP (Operational Prerequisite Program)</Typography>
                          <Typography variant="caption" color="textSecondary">
                            Control measure at a specific step to control a significant hazard
                          </Typography>
                        </Box>
                      }
                    />
                    <FormControlLabel
                      value="ccp"
                      control={<Radio />}
                      label={
                        <Box>
                          <Typography variant="body1">CCP (Critical Control Point)</Typography>
                          <Typography variant="caption" color="textSecondary">
                            Critical step where control is essential to prevent or eliminate a food safety hazard
                          </Typography>
                        </Box>
                      }
                    />
                    <FormControlLabel
                      value="further_analysis"
                      control={<Radio />}
                      label={
                        <Box>
                          <Typography variant="body1">Further Analysis (Decision Tree)</Typography>
                          <Typography variant="caption" color="textSecondary">
                            Use the decision tree to determine the appropriate control strategy
                          </Typography>
                        </Box>
                      }
                    />
                  </RadioGroup>
                </FormControl>
              </Grid>
            ) : (
              <>
                <Grid item xs={12}>
                  <Alert 
                    severity="success" 
                    icon={<CheckCircle />}
                    action={
                      <Button color="inherit" size="small" onClick={handleCancelStrategy}>
                        Change
                      </Button>
                    }
                  >
                    Risk strategy determined: <strong>{getRiskStrategyLabel(formData.risk_strategy!)}</strong>
                  </Alert>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="Risk Strategy Justification"
                    value={formData.risk_strategy_justification || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, risk_strategy_justification: e.target.value }))}
                    placeholder="Provide justification for the selected risk strategy..."
                    helperText={Object.keys(decisionTreeAnswers).length > 0 ? "Required for further analysis" : "Optional, but recommended for documentation purposes"}
                    required={Object.keys(decisionTreeAnswers).length > 0}
                  />
                </Grid>

                {formData.subsequent_step && (
                  <Grid item xs={12}>
                    <Alert severity="info">
                      <Typography variant="subtitle2">Subsequent Step:</Typography>
                      <Typography variant="body2">{formData.subsequent_step}</Typography>
                    </Alert>
                  </Grid>
                )}

                {/* CCP Creation Form */}
                {formData.risk_strategy === 'ccp' && (
                  <>
                    <Grid item xs={12}>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="h6" gutterBottom>
                        Create CCP (Critical Control Point)
                      </Typography>
                      <Alert severity="warning" sx={{ mb: 2 }}>
                        This hazard will be managed as a CCP. Please provide the CCP details below.
                      </Alert>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        required
                        label="CCP Number"
                        value={ccpForm.ccp_number}
                        onChange={(e) => setCcpForm({ ...ccpForm, ccp_number: e.target.value })}
                        placeholder="e.g., CCP-1, CCP-2"
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        required
                        label="CCP Name"
                        value={ccpForm.ccp_name}
                        onChange={(e) => setCcpForm({ ...ccpForm, ccp_name: e.target.value })}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        multiline
                        rows={2}
                        label="CCP Description"
                        value={ccpForm.description}
                        onChange={(e) => setCcpForm({ ...ccpForm, description: e.target.value })}
                      />
                    </Grid>

                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Critical Limit Min"
                        value={ccpForm.critical_limit_min}
                        onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_min: e.target.value })}
                        placeholder="Minimum value"
                      />
                    </Grid>

                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Critical Limit Max"
                        value={ccpForm.critical_limit_max}
                        onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_max: e.target.value })}
                        placeholder="Maximum value"
                      />
                    </Grid>

                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        label="Unit"
                        value={ccpForm.critical_limit_unit}
                        onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_unit: e.target.value })}
                        placeholder="e.g., °C, minutes, pH"
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Monitoring Frequency"
                        value={ccpForm.monitoring_frequency}
                        onChange={(e) => setCcpForm({ ...ccpForm, monitoring_frequency: e.target.value })}
                        placeholder="e.g., Every 30 minutes, Continuous"
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Monitoring Method"
                        value={ccpForm.monitoring_method}
                        onChange={(e) => setCcpForm({ ...ccpForm, monitoring_method: e.target.value })}
                        placeholder="e.g., Temperature probe, Visual inspection"
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        multiline
                        rows={2}
                        label="Corrective Actions"
                        value={ccpForm.corrective_actions}
                        onChange={(e) => setCcpForm({ ...ccpForm, corrective_actions: e.target.value })}
                        placeholder="Actions to take when critical limit is exceeded"
                      />
                    </Grid>
                  </>
                )}

                {/* Note for Use Existing PRPs strategy */}
                {strategyLocked && formData.risk_strategy === 'use_existing_prps' && (
                  <Grid item xs={12}>
                    <Alert severity="success">
                      <Typography variant="subtitle2">Using Existing PRPs</Typography>
                      <Typography variant="body2">
                        This hazard will be managed using existing Prerequisite Programs. 
                        No additional CCP or OPRP creation is required.
                        {formData.subsequent_step && ` The subsequent step "${formData.subsequent_step}" will control this hazard.`}
                      </Typography>
                    </Alert>
                  </Grid>
                )}

                {/* OPRP Creation Form */}
                {strategyLocked && formData.risk_strategy === 'opprp' && (
                  <>
                    <Grid item xs={12}>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="h6" gutterBottom>
                        Create OPRP (Operational Prerequisite Program)
                      </Typography>
                      <Alert severity="info" sx={{ mb: 2 }}>
                        This hazard will be managed as an OPRP. Please provide the OPRP details below.
                      </Alert>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        required
                        label="OPRP Number"
                        value={oprpForm.oprp_number}
                        onChange={(e) => setOprpForm({ ...oprpForm, oprp_number: e.target.value })}
                        placeholder="e.g., OPRP-1, OPRP-2"
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        required
                        label="OPRP Name"
                        value={oprpForm.oprp_name}
                        onChange={(e) => setOprpForm({ ...oprpForm, oprp_name: e.target.value })}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        multiline
                        rows={2}
                        label="Description"
                        value={oprpForm.description}
                        onChange={(e) => setOprpForm({ ...oprpForm, description: e.target.value })}
                        placeholder="Describe the OPRP and how it controls the hazard"
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        multiline
                        rows={2}
                        label="Objective"
                        value={oprpForm.objective}
                        onChange={(e) => setOprpForm({ ...oprpForm, objective: e.target.value })}
                        placeholder="What is the objective of this OPRP?"
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="SOP Reference"
                        value={oprpForm.sop_reference}
                        onChange={(e) => setOprpForm({ ...oprpForm, sop_reference: e.target.value })}
                        placeholder="Reference to Standard Operating Procedure document"
                      />
                    </Grid>
                  </>
                )}
              </>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>{viewMode ? 'Close' : 'Cancel'}</Button>
          {!viewMode && (
            <Button
              variant="contained"
              onClick={handleSave}
              disabled={!formData.process_step_id || !formData.hazard_name || !formData.risk_strategy}
            >
              {formData.risk_strategy === 'ccp' ? 'Save Hazard & CCP' : formData.risk_strategy === 'opprp' ? 'Save Hazard & OPRP' : 'Save Hazard'}
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Decision Tree Dialog */}
      <Dialog
        open={decisionTreeOpen}
        onClose={() => setDecisionTreeOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Decision Tree Analysis</DialogTitle>
        <DialogContent>
          <Stepper activeStep={currentQuestion} orientation="vertical">
            {DECISION_TREE_QUESTIONS.map((q, index) => (
              <Step key={index} completed={index < currentQuestion}>
                <StepLabel>{q.question}</StepLabel>
                <StepContent>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    {q.helpText}
                  </Typography>
                  {index === currentQuestion && (
                    <Box sx={{ mb: 2 }}>
                      {/* For Q2, show subsequent step input if answer is Yes */}
                      {index === 1 && (
                        <TextField
                          fullWidth
                          label="Subsequent Step Name"
                          placeholder="Enter the name of the subsequent step that will control this hazard..."
                          value={subsequentStepName}
                          onChange={(e) => setSubsequentStepName(e.target.value)}
                          sx={{ mb: 2 }}
                          helperText="Required if answering 'Yes' to this question"
                        />
                      )}
                      
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button
                          variant="contained"
                          color="success"
                          onClick={() => {
                            if (index === 1 && !subsequentStepName.trim()) {
                              alert('Please enter the subsequent step name before answering "Yes"');
                              return;
                            }
                            handleDecisionTreeAnswer(true);
                          }}
                        >
                          Yes
                        </Button>
                        <Button
                          variant="contained"
                          color="error"
                          onClick={() => {
                            handleDecisionTreeAnswer(false);
                          }}
                        >
                          No
                        </Button>
                      </Box>
                    </Box>
                  )}
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setDecisionTreeOpen(false);
            setSubsequentStepName('');
          }}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default HazardDialog;

