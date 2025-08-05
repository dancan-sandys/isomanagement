import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Divider,
  Avatar,
  AvatarGroup,
} from '@mui/material';
import {
  Close,
  CheckCircle,
  Pending,
  Error,
  Person,
  AccessTime,
  Comment,
  Send,
  ArrowForward,
  ArrowBack,
  Assignment,
  Approval,
  Edit,
  History,
  Timeline,
} from '@mui/icons-material';
import { documentsAPI } from '../../services/api';

interface WorkflowStep {
  id: number;
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'rejected';
  assigned_to: string;
  assigned_at?: string;
  completed_at?: string;
  comments?: string;
  order: number;
}

interface DocumentWorkflow {
  id: number;
  document_id: number;
  current_step: number;
  status: 'draft' | 'under_review' | 'approved' | 'rejected';
  steps: WorkflowStep[];
  created_at: string;
  updated_at: string;
}

interface DocumentWorkflowDialogProps {
  open: boolean;
  document: any;
  onClose: () => void;
  onWorkflowUpdate?: (workflow: DocumentWorkflow) => void;
}

const DocumentWorkflowDialog: React.FC<DocumentWorkflowDialogProps> = ({
  open,
  document,
  onClose,
  onWorkflowUpdate,
}) => {
  const [loading, setLoading] = useState(false);
  const [workflow, setWorkflow] = useState<DocumentWorkflow | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [comments, setComments] = useState('');
  const [action, setAction] = useState<'approve' | 'reject' | 'request_changes'>('approve');

  const workflowSteps = [
    {
      name: 'Document Creation',
      description: 'Document created and ready for review',
      icon: <Edit />,
    },
    {
      name: 'Initial Review',
      description: 'QA Specialist reviews document content',
      icon: <Assignment />,
    },
    {
      name: 'Technical Review',
      description: 'Technical expert reviews technical accuracy',
      icon: <Person />,
    },
    {
      name: 'Final Approval',
      description: 'QA Manager gives final approval',
      icon: <Approval />,
    },
  ];

  useEffect(() => {
    if (open && document) {
      loadWorkflow();
    }
  }, [open, document]);

  const loadWorkflow = async () => {
    if (!document) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Mock workflow data - in real implementation, this would come from API
      const mockWorkflow: DocumentWorkflow = {
        id: 1,
        document_id: document.id,
        current_step: 1,
        status: 'under_review',
        steps: [
          {
            id: 1,
            name: 'Document Creation',
            status: 'completed',
            assigned_to: document.created_by,
            assigned_at: document.created_at,
            completed_at: document.created_at,
            order: 1,
          },
          {
            id: 2,
            name: 'Initial Review',
            status: 'in_progress',
            assigned_to: 'QA Specialist',
            assigned_at: document.created_at,
            order: 2,
          },
          {
            id: 3,
            name: 'Technical Review',
            status: 'pending',
            assigned_to: 'Technical Expert',
            order: 3,
          },
          {
            id: 4,
            name: 'Final Approval',
            status: 'pending',
            assigned_to: 'QA Manager',
            order: 4,
          },
        ],
        created_at: document.created_at,
        updated_at: document.updated_at,
      };
      
      setWorkflow(mockWorkflow);
      setActiveStep(mockWorkflow.current_step - 1);
    } catch (error: any) {
      setError(error.message || 'Failed to load workflow');
    } finally {
      setLoading(false);
    }
  };

  const handleStepAction = async () => {
    if (!workflow) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Mock API call - in real implementation, this would update the workflow
      const updatedWorkflow = { ...workflow };
      const currentStep = updatedWorkflow.steps[activeStep];
      
      if (action === 'approve') {
        currentStep.status = 'completed';
        currentStep.completed_at = new Date().toISOString();
        currentStep.comments = comments;
        
        if (activeStep < workflowSteps.length - 1) {
          updatedWorkflow.current_step = activeStep + 2;
          updatedWorkflow.steps[activeStep + 1].status = 'in_progress';
        } else {
          updatedWorkflow.status = 'approved';
        }
      } else if (action === 'reject') {
        currentStep.status = 'rejected';
        currentStep.comments = comments;
        updatedWorkflow.status = 'rejected';
      } else if (action === 'request_changes') {
        currentStep.status = 'rejected';
        currentStep.comments = comments;
        updatedWorkflow.steps[0].status = 'in_progress';
        updatedWorkflow.current_step = 1;
      }
      
      setWorkflow(updatedWorkflow);
      if (onWorkflowUpdate) {
        onWorkflowUpdate(updatedWorkflow);
      }
      
      setComments('');
    } catch (error: any) {
      setError(error.message || 'Failed to update workflow');
    } finally {
      setLoading(false);
    }
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'in_progress':
        return <Pending color="warning" />;
      case 'rejected':
        return <Error color="error" />;
      default:
        return <Timeline color="disabled" />;
    }
  };

  const getStepColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'warning';
      case 'rejected':
        return 'error';
      default:
        return 'disabled';
    }
  };

  const canTakeAction = (stepIndex: number) => {
    if (!workflow) return false;
    const step = workflow.steps[stepIndex];
    return step.status === 'in_progress' && stepIndex === activeStep;
  };

  const handleClose = () => {
    setWorkflow(null);
    setError(null);
    setComments('');
    setAction('approve');
    setActiveStep(0);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Timeline color="primary" />
            <Typography variant="h6">
              Document Workflow - {document?.title}
            </Typography>
          </Box>
          <IconButton onClick={handleClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {workflow && (
          <Box>
            {/* Workflow Status */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Chip
                    label={workflow.status.replace('_', ' ').toUpperCase()}
                    color={workflow.status === 'approved' ? 'success' : 
                           workflow.status === 'rejected' ? 'error' : 'warning'}
                    variant="filled"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Current Step: {workflowSteps[workflow.current_step - 1]?.name}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <AvatarGroup max={3}>
                    {workflow.steps.map((step, index) => (
                      <Tooltip key={step.id} title={`${step.name}: ${step.assigned_to}`}>
                        <Avatar sx={{ width: 32, height: 32 }}>
                          {step.assigned_to.charAt(0)}
                        </Avatar>
                      </Tooltip>
                    ))}
                  </AvatarGroup>
                  <Typography variant="body2" color="text.secondary">
                    {workflow.steps.length} steps • Created {new Date(workflow.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>

            {/* Workflow Steps */}
            <Stepper activeStep={activeStep} orientation="vertical">
              {workflowSteps.map((step, index) => {
                const workflowStep = workflow.steps[index];
                const isActive = index === activeStep;
                const isCompleted = workflowStep?.status === 'completed';
                const isRejected = workflowStep?.status === 'rejected';
                
                return (
                  <Step key={index} completed={isCompleted}>
                    <StepLabel
                      icon={getStepIcon(workflowStep?.status || 'pending')}
                      error={isRejected}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" fontWeight={500}>
                          {step.name}
                        </Typography>
                        {isActive && (
                          <Chip label="Current" size="small" color="primary" />
                        )}
                      </Box>
                    </StepLabel>
                    <StepContent>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {step.description}
                        </Typography>
                        
                        {workflowStep && (
                          <Box sx={{ mt: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                              <Person fontSize="small" color="action" />
                              <Typography variant="body2">
                                Assigned to: {workflowStep.assigned_to}
                              </Typography>
                            </Box>
                            
                            {workflowStep.assigned_at && (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                                <AccessTime fontSize="small" color="action" />
                                <Typography variant="body2">
                                  Assigned: {new Date(workflowStep.assigned_at).toLocaleDateString()}
                                </Typography>
                              </Box>
                            )}
                            
                            {workflowStep.completed_at && (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                                <CheckCircle fontSize="small" color="success" />
                                <Typography variant="body2">
                                  Completed: {new Date(workflowStep.completed_at).toLocaleDateString()}
                                </Typography>
                              </Box>
                            )}
                            
                            {workflowStep.comments && (
                              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                                <Typography variant="body2" fontWeight={500} gutterBottom>
                                  Comments:
                                </Typography>
                                <Typography variant="body2">
                                  {workflowStep.comments}
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        )}
                        
                        {/* Action Buttons for Current Step */}
                        {canTakeAction(index) && (
                          <Box sx={{ mt: 3 }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Take Action:
                            </Typography>
                            <Grid container spacing={2}>
                              <Grid item xs={12}>
                                <FormControl fullWidth size="small">
                                  <InputLabel>Action</InputLabel>
                                  <Select
                                    value={action}
                                    onChange={(e) => setAction(e.target.value as any)}
                                  >
                                    <MenuItem value="approve">Approve</MenuItem>
                                    <MenuItem value="reject">Reject</MenuItem>
                                    <MenuItem value="request_changes">Request Changes</MenuItem>
                                  </Select>
                                </FormControl>
                              </Grid>
                              <Grid item xs={12}>
                                <TextField
                                  fullWidth
                                  multiline
                                  rows={3}
                                  label="Comments"
                                  value={comments}
                                  onChange={(e) => setComments(e.target.value)}
                                  placeholder="Add your comments..."
                                />
                              </Grid>
                              <Grid item xs={12}>
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                  <Button
                                    variant="contained"
                                    onClick={handleStepAction}
                                    disabled={loading}
                                    startIcon={<Send />}
                                  >
                                    Submit Action
                                  </Button>
                                  <Button
                                    variant="outlined"
                                    onClick={() => setComments('')}
                                  >
                                    Clear
                                  </Button>
                                </Box>
                              </Grid>
                            </Grid>
                          </Box>
                        )}
                      </Box>
                    </StepContent>
                  </Step>
                );
              })}
            </Stepper>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={handleClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentWorkflowDialog; 