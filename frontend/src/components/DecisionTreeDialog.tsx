import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  FormControl,
  FormControlLabel,
  RadioGroup,
  Radio,
  Checkbox,
  TextField,
  Card,
  CardContent,
  Alert,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  HelpOutline,
  Info,
  Warning,
  Science,
  Security,
  Close,
} from '@mui/icons-material';
import { haccpAPI } from '../services/api';

interface DecisionPoint {
  id: string;
  question: string;
  description?: string;
  type: 'yes_no' | 'multiple_choice' | 'assessment';
  options?: string[];
  helpText?: string;
  criticalFactor?: boolean;
}

interface DecisionTreeDialogProps {
  open: boolean;
  onClose: () => void;
  hazardId: number;
  hazardName: string;
  onDecisionComplete: (isCCP: boolean, reasoning: string) => void;
}

const DecisionTreeDialog: React.FC<DecisionTreeDialogProps> = ({
  open,
  onClose,
  hazardId,
  hazardName,
  onDecisionComplete,
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [answers, setAnswers] = useState<{ [key: string]: string }>({});
  const [reasoning, setReasoning] = useState<string[]>([]);
  const [finalDecision, setFinalDecision] = useState<{
    isCCP: boolean;
    confidence: number;
    justification: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);

  // ISO 22000 / Codex HACCP Decision Tree Questions
  const decisionPoints: DecisionPoint[] = [
    {
      id: 'q1',
      question: 'Do preventive control measures exist for the identified hazard?',
      description: 'Consider if there are any measures in place to prevent, eliminate, or reduce the hazard to an acceptable level.',
      type: 'yes_no',
      helpText: 'Preventive control measures include PRPs, operational PRPs, or other controls that address the hazard before this step.',
      criticalFactor: true,
    },
    {
      id: 'q1_modify',
      question: 'Can the step be modified to include a preventive control measure?',
      description: 'If no preventive measures exist, determine if the process step can be modified to include appropriate controls.',
      type: 'yes_no',
      helpText: 'Consider changes to temperature, time, pH, processing method, or addition of control steps.',
    },
    {
      id: 'q2',
      question: 'Is the step specifically designed to eliminate or reduce the likely occurrence of the hazard to an acceptable level?',
      description: 'Evaluate if this specific step is intended as a control measure for the identified hazard.',
      type: 'yes_no',
      helpText: 'This refers to steps like cooking, pasteurization, metal detection, or pH adjustment that are specifically implemented for hazard control.',
      criticalFactor: true,
    },
    {
      id: 'q3',
      question: 'Could contamination with the identified hazard occur at this step or increase to unacceptable levels?',
      description: 'Assess if the hazard could be introduced or if existing contamination could increase.',
      type: 'yes_no',
      helpText: 'Consider sources of contamination, cross-contamination potential, or conditions that could allow hazard growth.',
      criticalFactor: true,
    },
    {
      id: 'q4',
      question: 'Will a subsequent step eliminate the identified hazard or reduce its likely occurrence to an acceptable level?',
      description: 'Determine if later processing steps will adequately control this hazard.',
      type: 'yes_no',
      helpText: 'Consider all subsequent steps in the process, including cooking, treatment, or other control measures.',
      criticalFactor: true,
    },
    {
      id: 'severity_assessment',
      question: 'What is the severity of the potential health impact?',
      description: 'Assess the potential consequences if this hazard is not controlled.',
      type: 'multiple_choice',
      options: ['Low (minor illness)', 'Moderate (illness, no long-term effects)', 'High (serious illness or long-term effects)', 'Severe (life-threatening)'],
      helpText: 'Consider the target consumer population, including vulnerable groups.',
    },
    {
      id: 'likelihood_assessment',
      question: 'What is the likelihood of occurrence if not controlled?',
      description: 'Evaluate the probability that the hazard will occur and cause harm.',
      type: 'multiple_choice',
      options: ['Very Low', 'Low', 'Moderate', 'High', 'Very High'],
      helpText: 'Consider historical data, process variability, and environmental factors.',
    },
  ];

  useEffect(() => {
    if (open) {
      // Reset state when dialog opens
      setActiveStep(0);
      setAnswers({});
      setReasoning([]);
      setFinalDecision(null);
    }
  }, [open]);

  const getCurrentQuestion = () => {
    return decisionPoints[activeStep];
  };

  const handleAnswer = (questionId: string, answer: string) => {
    const newAnswers = { ...answers, [questionId]: answer };
    setAnswers(newAnswers);
    
    // Add to reasoning
    const question = decisionPoints.find(q => q.id === questionId);
    if (question) {
      const newReasoning = [...reasoning];
      newReasoning[activeStep] = `${question.question} Answer: ${answer}`;
      setReasoning(newReasoning);
    }
  };

  const getNextStep = () => {
    const currentQ = getCurrentQuestion();
    const currentAnswer = answers[currentQ.id];

    // Decision tree logic based on Codex HACCP
    switch (currentQ.id) {
      case 'q1':
        if (currentAnswer === 'No') {
          return 'q1_modify';
        }
        return 'q2';
      
      case 'q1_modify':
        if (currentAnswer === 'Yes') {
          return 'q2';
        }
        // If no modification possible, not a CCP at this point
        return 'complete_not_ccp_no_control';
      
      case 'q2':
        if (currentAnswer === 'Yes') {
          return 'complete_is_ccp';
        }
        return 'q3';
      
      case 'q3':
        if (currentAnswer === 'No') {
          return 'complete_not_ccp_no_contamination';
        }
        return 'q4';
      
      case 'q4':
        if (currentAnswer === 'Yes') {
          return 'complete_not_ccp_subsequent_control';
        }
        return 'severity_assessment';
      
      case 'severity_assessment':
        return 'likelihood_assessment';
      
      case 'likelihood_assessment':
        return 'complete_assessment';
      
      default:
        return null;
    }
  };

  const handleNext = () => {
    const nextStep = getNextStep();
    
    if (nextStep?.startsWith('complete_')) {
      // Generate final decision
      generateFinalDecision(nextStep);
    } else if (nextStep) {
      // Find the index of the next question
      const nextIndex = decisionPoints.findIndex(q => q.id === nextStep);
      if (nextIndex >= 0) {
        setActiveStep(nextIndex);
      }
    }
  };

  const generateFinalDecision = (endpoint: string) => {
    let isCCP = false;
    let confidence = 0;
    let justification = '';

    switch (endpoint) {
      case 'complete_is_ccp':
        isCCP = true;
        confidence = 95;
        justification = 'This step is specifically designed to eliminate or reduce the hazard to an acceptable level. It meets the definition of a Critical Control Point.';
        break;
      
      case 'complete_not_ccp_no_control':
        isCCP = false;
        confidence = 90;
        justification = 'No preventive control measures exist and the step cannot be modified to include controls. This point requires prerequisite program enhancement rather than CCP designation.';
        break;
      
      case 'complete_not_ccp_no_contamination':
        isCCP = false;
        confidence = 85;
        justification = 'Contamination with this hazard is not likely to occur at this step. Control is not critical at this point.';
        break;
      
      case 'complete_not_ccp_subsequent_control':
        isCCP = false;
        confidence = 90;
        justification = 'A subsequent step will eliminate or adequately reduce this hazard. Control at this step is not critical.';
        break;
      
      case 'complete_assessment':
        // Base decision on severity and likelihood
        const severity = answers['severity_assessment'];
        const likelihood = answers['likelihood_assessment'];
        
        const severityScore = ['Low (minor illness)', 'Moderate (illness, no long-term effects)', 'High (serious illness or long-term effects)', 'Severe (life-threatening)'].indexOf(severity) + 1;
        const likelihoodScore = ['Very Low', 'Low', 'Moderate', 'High', 'Very High'].indexOf(likelihood) + 1;
        
        const riskScore = severityScore * likelihoodScore;
        
        if (riskScore >= 12) {
          isCCP = true;
          confidence = 80;
          justification = `High risk scenario (Risk Score: ${riskScore}). The combination of ${severity.toLowerCase()} severity and ${likelihood.toLowerCase()} likelihood requires critical control.`;
        } else if (riskScore >= 8) {
          isCCP = true;
          confidence = 65;
          justification = `Moderate-high risk scenario (Risk Score: ${riskScore}). Consider implementing as CCP with robust monitoring.`;
        } else {
          isCCP = false;
          confidence = 75;
          justification = `Lower risk scenario (Risk Score: ${riskScore}). May be adequately controlled through prerequisite programs.`;
        }
        break;
      
      default:
        isCCP = false;
        confidence = 50;
        justification = 'Unable to determine CCP status. Further analysis required.';
    }

    setFinalDecision({
      isCCP,
      confidence,
      justification: `${justification}\n\nReasoning:\n${reasoning.join('\n')}`,
    });
  };

  const handleComplete = async () => {
    if (!finalDecision) return;

    setLoading(true);
    try {
      // Save decision to backend
      await haccpAPI.updateHazard(hazardId, {
        is_ccp: finalDecision.isCCP,
        ccp_justification: finalDecision.justification,
        decision_tree_confidence: finalDecision.confidence,
        decision_tree_completed: true,
      });

      onDecisionComplete(finalDecision.isCCP, finalDecision.justification);
      onClose();
    } catch (error) {
      console.error('Error saving CCP decision:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1);
      // Remove the reasoning for the current step
      const newReasoning = [...reasoning];
      newReasoning.splice(activeStep);
      setReasoning(newReasoning);
    }
  };

  const isLastStep = () => {
    return !getNextStep() || getNextStep()?.startsWith('complete_');
  };

  if (!open) return null;

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '600px' }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="h6">HACCP Decision Tree</Typography>
            <Typography variant="body2" color="textSecondary">
              Hazard: {hazardName}
            </Typography>
          </Box>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {!finalDecision ? (
          <Box>
            <Stepper activeStep={activeStep} orientation="vertical">
              {decisionPoints.map((point, index) => (
                <Step key={point.id} expanded={index === activeStep}>
                  <StepLabel>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2" fontWeight="medium">
                        Question {index + 1}
                      </Typography>
                      {point.criticalFactor && (
                        <Chip size="small" label="Critical" color="warning" />
                      )}
                    </Box>
                  </StepLabel>
                  <StepContent>
                    <Card variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {point.question}
                        </Typography>
                        
                        {point.description && (
                          <Typography variant="body2" color="textSecondary" paragraph>
                            {point.description}
                          </Typography>
                        )}

                        {point.helpText && (
                          <Alert severity="info" sx={{ mb: 2 }}>
                            <Typography variant="body2">
                              {point.helpText}
                            </Typography>
                          </Alert>
                        )}

                        <FormControl component="fieldset" fullWidth>
                          {point.type === 'yes_no' && (
                            <RadioGroup
                              value={answers[point.id] || ''}
                              onChange={(e) => handleAnswer(point.id, e.target.value)}
                            >
                              <FormControlLabel 
                                value="Yes" 
                                control={<Radio />} 
                                label="Yes" 
                              />
                              <FormControlLabel 
                                value="No" 
                                control={<Radio />} 
                                label="No" 
                              />
                            </RadioGroup>
                          )}

                          {point.type === 'multiple_choice' && point.options && (
                            <RadioGroup
                              value={answers[point.id] || ''}
                              onChange={(e) => handleAnswer(point.id, e.target.value)}
                            >
                              {point.options.map((option) => (
                                <FormControlLabel
                                  key={option}
                                  value={option}
                                  control={<Radio />}
                                  label={option}
                                />
                              ))}
                            </RadioGroup>
                          )}
                        </FormControl>
                      </CardContent>
                    </Card>

                    <Box display="flex" gap={2}>
                      <Button
                        variant="outlined"
                        onClick={handleBack}
                        disabled={activeStep === 0}
                      >
                        Back
                      </Button>
                      <Button
                        variant="contained"
                        onClick={handleNext}
                        disabled={!answers[point.id]}
                        endIcon={isLastStep() ? <CheckCircle /> : undefined}
                      >
                        {isLastStep() ? 'Complete Analysis' : 'Next'}
                      </Button>
                    </Box>
                  </StepContent>
                </Step>
              ))}
            </Stepper>
          </Box>
        ) : (
          <Box>
            <Alert 
              severity={finalDecision.isCCP ? "warning" : "info"}
              sx={{ mb: 3 }}
            >
              <Typography variant="h6" gutterBottom>
                Decision: {finalDecision.isCCP ? 'Critical Control Point (CCP)' : 'Not a Critical Control Point'}
              </Typography>
              <Typography variant="body2">
                Confidence Level: {finalDecision.confidence}%
              </Typography>
            </Alert>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Box display="flex" alignItems="center" gap={1}>
                    {finalDecision.isCCP ? (
                      <Warning color="warning" />
                    ) : (
                      <CheckCircle color="success" />
                    )}
                    Justification
                  </Box>
                </Typography>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                  {finalDecision.justification}
                </Typography>
              </CardContent>
            </Card>

            {finalDecision.isCCP && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  <strong>Next Steps:</strong> This hazard requires establishment of critical limits, 
                  monitoring procedures, corrective actions, and verification activities as part of 
                  your HACCP plan.
                </Typography>
              </Alert>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        {!finalDecision ? (
          <Button onClick={onClose}>Cancel</Button>
        ) : (
          <>
            <Button onClick={onClose}>Cancel</Button>
            <Button 
              variant="contained" 
              onClick={handleComplete}
              disabled={loading}
              startIcon={finalDecision.isCCP ? <Warning /> : <CheckCircle />}
            >
              {loading ? 'Saving...' : `Confirm ${finalDecision.isCCP ? 'CCP' : 'Non-CCP'} Decision`}
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default DecisionTreeDialog;