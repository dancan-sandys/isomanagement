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
  Grow,
} from '@mui/material';
import {
  Close,
  CheckCircle,
  Pending,
  Error as ErrorIcon,
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
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { isSystemAdministrator } from '../../store/slices/authSlice';
// Legacy approveVersion removed; use approvals API chain instead

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
  const dispatch = useDispatch<AppDispatch>();
  const { user: currentUser } = useSelector((state: RootState) => state.auth);

  // Icons per status for dynamic steps coming from backend
  const stepIconByName: Record<string, JSX.Element> = {
    creation: <Edit />, review: <Assignment />, technical: <Person />, approval: <Approval />,
  };

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
      const resp = await documentsAPI.getApprovalWorkflow(document.id);
      const data = (resp && (resp.data || resp)) as any; // ResponseModel -> data
      setWorkflow(data);
      setActiveStep(Math.max(0, (data?.current_step || 1) - 1));
    } catch (error: any) {
      setError(error.message || 'Failed to load workflow');
    } finally {
      setLoading(false);
    }
  };

  const handleStepAction = async (stepIndex?: number) => {
    if (!workflow || !document) return;

    setLoading(true);
    setError(null);

    try {
      let approvalId: number;
      
      // System Administrator can act on any step directly
      if (isSystemAdministrator(currentUser) && stepIndex !== undefined) {
        const step = workflow.steps[stepIndex];
        if (!step || (step.status !== 'pending' && step.status !== 'in_progress')) {
          throw new Error('Selected step is not available for action');
        }
        approvalId = step.id;
      } else {
        // Find user's pending approval step for this document and act on it
        const pending = await documentsAPI.getPendingApprovals();
        const record = (pending?.data?.items || pending?.data || []).find((i: any) => i.document_id === document.id);
        if (!record || !record.approval_id) {
          throw new Error('No pending approval step found for this document');
        }
        approvalId = record.approval_id;
      }

      if (action === 'approve') {
        await documentsAPI.approveApprovalStep(document.id, approvalId, { comments });
      } else {
        // For 'reject' and 'request_changes', use reject; backend treats comments as reason
        await documentsAPI.rejectApprovalStep(document.id, approvalId, { comments });
      }

      // Reload the workflow to get updated status
      await loadWorkflow();
      
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
        return <ErrorIcon color="error" />;
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
    if (!workflow || !Array.isArray(workflow.steps)) return false;
    const step = workflow.steps[stepIndex];
    if (!step) return false;
    
    // System Administrator can take action on any pending step
    if (isSystemAdministrator(currentUser)) {
      return step.status === 'pending' || step.status === 'in_progress';
    }
    
    // Regular users can only act on current in-progress step assigned to them
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
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth scroll="paper">
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

      <DialogContent dividers sx={{ maxHeight: '72vh', overflowY: 'auto' }}>
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {workflow && (
          <Box>
            {/* Three-stage primary flow: Draft → Reviewed → Approved */}
            {(() => {
              const createdBy = (document?.created_by_name || document?.owner_name || document?.created_by || '').toString();
              const createdAt = document?.created_at ? new Date(document.created_at).toLocaleString() : '';
              // Exclude the synthetic Creation step (order 0) from approval computations
              const approvalSteps = (workflow.steps || []).filter((s) => (s.order ?? 0) > 0);
              const firstApproval = approvalSteps.length > 0 ? approvalSteps[0] : undefined;
              const lastApproval = approvalSteps.length > 0 ? approvalSteps[approvalSteps.length - 1] : undefined;

              // Stage statuses
              const reviewCompleted = !!firstApproval && (firstApproval.status === 'completed' || !!firstApproval.completed_at);
              const approvedCompleted = (workflow.status === 'approved') || (!!lastApproval && (lastApproval.status === 'completed' || !!lastApproval.completed_at));
              const primaryActive = approvedCompleted ? 2 : reviewCompleted ? 1 : 0;

              const stages = [
                {
                  key: 'draft',
                  name: 'Draft',
                  status: 'completed' as const,
                  by: createdBy,
                  at: createdAt,
                  icon: <CheckCircle color="success" />,
                },
                {
                  key: 'reviewed',
                  name: 'Reviewed',
                  status: reviewCompleted ? ('completed' as const) : (workflow.current_step === 1 ? ('in_progress' as const) : ('pending' as const)),
                  by: firstApproval?.assigned_to || '-',
                  at: firstApproval?.completed_at ? new Date(firstApproval.completed_at).toLocaleString() : firstApproval?.assigned_at ? new Date(firstApproval.assigned_at).toLocaleString() : '',
                },
                {
                  key: 'approved',
                  name: 'Approved',
                  status: approvedCompleted ? ('completed' as const) : (approvalSteps.some((s) => s.status === 'in_progress' || s.status === 'pending') ? ('in_progress' as const) : ('pending' as const)),
                  by: lastApproval?.assigned_to || '-',
                  at: lastApproval?.completed_at ? new Date(lastApproval.completed_at).toLocaleString() : '',
                },
              ];

              const renderPrimaryIcon = (status: string) => {
                if (status === 'completed') return (
                  <Grow in timeout={400}>
                    <span><CheckCircle color="success" /></span>
                  </Grow>
                );
                if (status === 'in_progress') return <Pending color="warning" />;
                return <Timeline color="disabled" />;
              };

              return (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                    <Stepper alternativeLabel activeStep={primaryActive}>
                      {stages.map((s) => (
                        <Step key={s.key} completed={s.status === 'completed'}>
                          <StepLabel icon={renderPrimaryIcon(s.status)}>
                            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                              <Typography variant="subtitle2" fontWeight={600}>{s.name}</Typography>
                              {(s.by || s.at) && (
                                <Typography variant="caption" color="text.secondary" align="center">
                                  {s.by ? `${s.by}` : ''}
                                  {s.by && s.at ? ' • ' : ''}
                                  {s.at || ''}
                  </Typography>
                              )}
                </Box>
                          </StepLabel>
                        </Step>
                      ))}
                    </Stepper>
              </CardContent>
            </Card>
              );
            })()}

            {/* Status card removed per request; three-stage flow above serves as summary */}

            {/* Workflow Steps */}
            <Stepper activeStep={activeStep} orientation="vertical">
              {(workflow.steps || []).map((workflowStep, index) => {
                const step = {
                  name: workflowStep.name || `Step ${workflowStep.order}`,
                  description: workflowStep.comments || '',
                };
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
                        {step.description && (
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            {step.description}
                          </Typography>
                        )}
                        
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
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                              <Typography variant="subtitle2">
                                Take Action:
                              </Typography>
                              {isSystemAdministrator(currentUser) && workflowStep?.status === 'pending' && (
                                <Chip 
                                  label="Admin Override" 
                                  size="small" 
                                  color="secondary" 
                                  variant="outlined"
                                />
                              )}
                            </Box>
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
                                    onClick={() => handleStepAction(index)}
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