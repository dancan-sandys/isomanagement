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
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  Alert,
  Chip,
  Paper,
  Divider
} from '@mui/material';
import { CheckCircle, Cancel, Help } from '@mui/icons-material';
import { decisionTreeAPI } from '../services/api';

interface DecisionTreeDialogProps {
  open: boolean;
  onClose: () => void;
  hazardId: number;
  hazardName: string;
  onDecisionComplete?: (isCCP: boolean, reasoning: string) => void;
}

interface DecisionTreeData {
  id: number;
  hazard_id: number;
  q1_answer: boolean | null;
  q1_justification: string | null;
  q2_answer: boolean | null;
  q2_justification: string | null;
  q3_answer: boolean | null;
  q3_justification: string | null;
  q4_answer: boolean | null;
  q4_justification: string | null;
  is_ccp: boolean | null;
  decision_reasoning: string | null;
  status: string;
  current_question: number;
  can_proceed: boolean;
}

const questions = [
  {
    number: 1,
    text: "Is control at this step necessary for safety?",
    description: "Consider whether this step is essential for ensuring the safety of the final product."
  },
  {
    number: 2,
    text: "Is control at this step necessary to eliminate or reduce the likelihood of occurrence of a hazard to an acceptable level?",
    description: "Evaluate if this step can effectively control the identified hazard."
  },
  {
    number: 3,
    text: "Could contamination with identified hazard(s) occur or could this increase to unacceptable level(s)?",
    description: "Assess the potential for hazard introduction or amplification at this step."
  },
  {
    number: 4,
    text: "Will a subsequent step eliminate or reduce the likelihood of occurrence of a hazard to an acceptable level?",
    description: "Determine if later steps in the process will control this hazard."
  }
];

const DecisionTreeDialog: React.FC<DecisionTreeDialogProps> = ({
  open,
  onClose,
  hazardId,
  hazardName,
  onDecisionComplete
}) => {
  const [decisionTree, setDecisionTree] = useState<DecisionTreeData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<{ [key: number]: boolean | null }>({});
  const [justifications, setJustifications] = useState<{ [key: number]: string }>({});

  useEffect(() => {
    if (open && hazardId) {
      loadDecisionTree();
    }
  }, [open, hazardId]);

  const loadDecisionTree = async () => {
    try {
      setLoading(true);
      setError(null);
      
      try {
        const data = await decisionTreeAPI.getDecisionTree(hazardId);
        setDecisionTree(data);
        setCurrentStep(data.current_question - 1);
        
        const existingAnswers: { [key: number]: boolean | null } = {};
        const existingJustifications: { [key: number]: string } = {};
        
        if (data.q1_answer !== null) {
          existingAnswers[1] = data.q1_answer;
          existingJustifications[1] = data.q1_justification || '';
        }
        if (data.q2_answer !== null) {
          existingAnswers[2] = data.q2_answer;
          existingJustifications[2] = data.q2_justification || '';
        }
        if (data.q3_answer !== null) {
          existingAnswers[3] = data.q3_answer;
          existingJustifications[3] = data.q3_justification || '';
        }
        if (data.q4_answer !== null) {
          existingAnswers[4] = data.q4_answer;
          existingJustifications[4] = data.q4_justification || '';
        }
        
        setAnswers(existingAnswers);
        setJustifications(existingJustifications);
      } catch (err: any) {
        if (err.response?.status === 404) {
          setDecisionTree(null);
          setCurrentStep(0);
          setAnswers({});
          setJustifications({});
        } else {
          throw err;
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load decision tree');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionNumber: number, answer: boolean) => {
    setAnswers(prev => ({ ...prev, [questionNumber]: answer }));
  };

  const handleJustificationChange = (questionNumber: number, justification: string) => {
    setJustifications(prev => ({ ...prev, [questionNumber]: justification }));
  };

  const handleNext = async () => {
    const questionNumber = currentStep + 1;
    const answer = answers[questionNumber];
    const justification = justifications[questionNumber] || '';

    if (answer === null) {
      setError('Please select an answer before proceeding');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      let data;
      if (!decisionTree) {
        data = await decisionTreeAPI.createDecisionTree(hazardId, {
          q1_answer: answer,
          q1_justification: justification
        });
      } else {
        data = await decisionTreeAPI.answerQuestion(hazardId, {
          question_number: questionNumber,
          answer,
          justification
        });
      }

      setDecisionTree(data);
      
      if (data.is_ccp !== null) {
        if (onDecisionComplete) {
          onDecisionComplete(data.is_ccp, data.decision_reasoning || '');
        }
      } else {
        setCurrentStep(questionNumber);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save answer');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setCurrentStep(prev => Math.max(0, prev - 1));
  };

  const getDecisionResult = () => {
    if (!decisionTree || decisionTree.is_ccp === null) return null;

    return {
      isCCP: decisionTree.is_ccp,
      reasoning: decisionTree.decision_reasoning || '',
      status: decisionTree.status
    };
  };

  const canProceedToNext = (questionNumber: number) => {
    if (questionNumber === 1) return true;
    
    for (let i = 1; i < questionNumber; i++) {
      if (answers[i] === false) return false;
    }
    return true;
  };

  const result = getDecisionResult();

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <Help color="primary" />
          <Typography variant="h6">
            Codex Alimentarius Decision Tree
          </Typography>
        </Box>
        <Typography variant="subtitle2" color="text.secondary">
          Hazard: {hazardName}
        </Typography>
      </DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {result ? (
          <Box>
            <Paper elevation={2} sx={{ p: 3, mb: 2 }}>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                {result.isCCP ? (
                  <CheckCircle color="success" sx={{ fontSize: 40 }} />
                ) : (
                  <Cancel color="error" sx={{ fontSize: 40 }} />
                )}
                <Box>
                  <Typography variant="h6" color={result.isCCP ? 'success.main' : 'error.main'}>
                    {result.isCCP ? 'This is a Critical Control Point (CCP)' : 'This is NOT a Critical Control Point'}
                  </Typography>
                  <Chip 
                    label={result.status} 
                    color={result.status === 'completed' ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
              </Box>
              
              <Typography variant="body1" sx={{ mb: 2 }}>
                <strong>Decision Reasoning:</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {result.reasoning}
              </Typography>
            </Paper>

            <Typography variant="h6" sx={{ mb: 2 }}>Decision Tree Answers</Typography>
            {questions.map((question, index) => (
              <Box key={question.number} sx={{ mb: 2 }}>
                <Typography variant="subtitle1" sx={{ mb: 1 }}>
                  Question {question.number}: {question.text}
                </Typography>
                <Box display="flex" alignItems="center" gap={1} sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    Answer: 
                  </Typography>
                  {decisionTree && decisionTree[`q${question.number}_answer` as keyof DecisionTreeData] !== null ? (
                    <Chip 
                      label={decisionTree[`q${question.number}_answer` as keyof DecisionTreeData] ? 'Yes' : 'No'}
                      color={decisionTree[`q${question.number}_answer` as keyof DecisionTreeData] ? 'success' : 'error'}
                      size="small"
                    />
                  ) : (
                    <Chip label="Not answered" color="default" size="small" />
                  )}
                </Box>
                {decisionTree && decisionTree[`q${question.number}_justification` as keyof DecisionTreeData] && (
                  <Typography variant="body2" color="text.secondary">
                    Justification: {decisionTree[`q${question.number}_justification` as keyof DecisionTreeData]}
                  </Typography>
                )}
                {index < questions.length - 1 && <Divider sx={{ mt: 2 }} />}
              </Box>
            ))}
          </Box>
        ) : (
          <Stepper activeStep={currentStep} orientation="vertical">
            {questions.map((question, index) => (
              <Step key={question.number}>
                <StepLabel>
                  <Typography variant="subtitle1">
                    Question {question.number}
                  </Typography>
                </StepLabel>
                <StepContent>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body1" sx={{ mb: 1 }}>
                      {question.text}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {question.description}
                    </Typography>

                    {!canProceedToNext(question.number) ? (
                      <Alert severity="warning">
                        Cannot proceed to this question based on previous answers.
                      </Alert>
                    ) : (
                      <>
                        <RadioGroup
                          value={answers[question.number] === null ? '' : answers[question.number]}
                          onChange={(e) => handleAnswerChange(question.number, e.target.value === 'true')}
                        >
                          <FormControlLabel value={true} control={<Radio />} label="Yes" />
                          <FormControlLabel value={false} control={<Radio />} label="No" />
                        </RadioGroup>

                        <TextField
                          fullWidth
                          multiline
                          rows={3}
                          label="Justification (optional)"
                          value={justifications[question.number] || ''}
                          onChange={(e) => handleJustificationChange(question.number, e.target.value)}
                          sx={{ mt: 2 }}
                          placeholder="Provide reasoning for your answer..."
                        />

                        <Box sx={{ mt: 2 }}>
                          <Button
                            variant="contained"
                            onClick={handleNext}
                            disabled={loading || answers[question.number] === null}
                          >
                            {loading ? 'Saving...' : index === questions.length - 1 ? 'Complete Decision' : 'Next Question'}
                          </Button>
                          {index > 0 && (
                            <Button onClick={handleBack} sx={{ ml: 1 }}>
                              Back
                            </Button>
                          )}
                        </Box>
                      </>
                    )}
                  </Box>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>
          {result ? 'Close' : 'Cancel'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DecisionTreeDialog;
