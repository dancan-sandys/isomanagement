import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Button, Card, CardContent, Divider, Grid, Stack, TextField, Typography,
  Stepper, Step, StepLabel, StepContent, Chip, Alert, Dialog, DialogTitle,
  DialogContent, DialogActions, Tab, Tabs, Paper, List, ListItem, ListItemText,
  ListItemIcon, LinearProgress, IconButton, Tooltip, Accordion, AccordionSummary,
  AccordionDetails, FormControl, InputLabel, Select, MenuItem, Switch, FormControlLabel
} from '@mui/material';
import {
  PlayArrow as StartIcon, Check as CheckIcon, Warning as WarningIcon,
  Assessment as AssessmentIcon, Assignment as AssignmentIcon, Timeline as TimelineIcon,
  ExpandMore as ExpandMoreIcon, GetApp as CollectIcon, Save as SaveIcon,
  Send as SendIcon, Analytics as AnalyticsIcon, Checklist as ChecklistIcon,
  Schedule as ScheduleIcon, Group as GroupIcon
} from '@mui/icons-material';
import managementReviewAPI, { ReviewParticipant } from '../services/managementReviewAPI';

const ManagementReviewDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [review, setReview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [tabValue, setTabValue] = useState(0);
  const [inputs, setInputs] = useState<any[]>([]);
  const [outputs, setOutputs] = useState<any[]>([]);
  const [actions, setActions] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>({});
  const [compliance, setCompliance] = useState<any>({});
  const [attendance, setAttendance] = useState<ReviewParticipant[]>([]);
  const [newAttendee, setNewAttendee] = useState<ReviewParticipant>({ name: '', role: '', attendance_status: 'present' });
  const [collectingInputs, setCollectingInputs] = useState(false);
  const [actionForm, setActionForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    due_date: '',
    verification_required: false
  });

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true); setError(null);
    try {
      const [reviewResp, inputsResp, outputsResp, actionsResp] = await Promise.all([
        managementReviewAPI.get(Number(id)),
        managementReviewAPI.getInputs(Number(id)),
        managementReviewAPI.getOutputs(Number(id)),
        managementReviewAPI.listActions(Number(id))
      ]);
      
      setReview(reviewResp.data || reviewResp);
      setInputs(inputsResp.data || []);
      setOutputs(outputsResp.data || []);
      setActions(actionsResp.data || []);
      try {
        const attResp = await managementReviewAPI.listAttendance(Number(id));
        setAttendance(attResp.data || []);
      } catch {}
      
      // Load analytics and compliance if review is completed
      if ((reviewResp.data || reviewResp).status === 'completed') {
        try {
          const [analyticsResp, complianceResp] = await Promise.all([
            managementReviewAPI.getAnalytics(Number(id)),
            managementReviewAPI.checkCompliance(Number(id))
          ]);
          setAnalytics(analyticsResp.data || {});
          setCompliance(complianceResp.data || {});
        } catch (e) {
          console.error('Failed to load analytics/compliance:', e);
        }
      }
    } catch (e: any) { 
      setError(e?.message || 'Failed to load review'); 
    }
    finally { setLoading(false); }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  const collectInputs = async () => {
    setCollectingInputs(true);
    try {
      const request = {
        input_types: [
          'audit_results', 'nc_capa_status', 'supplier_performance',
          'haccp_performance', 'prp_performance', 'risk_assessment',
          'kpi_metrics', 'previous_actions'
        ],
        include_summaries: true
      };
      
      await managementReviewAPI.collectInputs(Number(id), request);
      await load(); // Reload to get updated inputs
    } catch (e: any) {
      setError(e?.message || 'Failed to collect inputs');
    } finally {
      setCollectingInputs(false);
    }
  };

  const addAttendee = async () => {
    if (!newAttendee.name || !newAttendee.role) return;
    await managementReviewAPI.addAttendee(Number(id), newAttendee);
    setNewAttendee({ name: '', role: '', attendance_status: 'present' });
    await load();
  };

  const updateAttendeeStatus = async (index: number, status: 'present' | 'absent' | 'partial') => {
    await managementReviewAPI.updateAttendee(Number(id), index, { attendance_status: status });
    await load();
  };

  const removeAttendee = async (index: number) => {
    await managementReviewAPI.deleteAttendee(Number(id), index);
    await load();
  };

  const startReview = async () => {
    try {
      await managementReviewAPI.update(Number(id), { status: 'in_progress' });
      await load();
    } catch (e: any) {
      setError(e?.message || 'Failed to start review');
    }
  };

  const completeReview = async () => {
    try {
      await managementReviewAPI.complete(Number(id));
      await load();
    } catch (e: any) {
      setError(e?.message || 'Failed to complete review');
    }
  };

  const addAction = async () => {
    try {
      await managementReviewAPI.addAction(Number(id), {
        ...actionForm,
        priority: actionForm.priority as 'low' | 'medium' | 'high' | 'critical'
      });
      setActionForm({
        title: '',
        description: '',
        priority: 'medium',
        due_date: '',
        verification_required: false
      });
      await load();
    } catch (e: any) {
      setError(e?.message || 'Failed to add action');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'warning';
      case 'planned': return 'info';
      default: return 'default';
    }
  };

  const getStepStatus = (stepIndex: number) => {
    if (review?.status === 'completed') return 'completed';
    if (review?.status === 'in_progress' && stepIndex <= activeStep) return 'active';
    if (review?.status === 'planned' && stepIndex === 0) return 'active';
    return 'pending';
  };

  const reviewSteps = [
    {
      label: 'Preparation & Input Collection',
      description: 'Collect all required inputs for ISO 22000:2018 compliance',
      component: 'inputs'
    },
    {
      label: 'Review Meeting',
      description: 'Conduct the management review meeting',
      component: 'meeting'
    },
    {
      label: 'Outputs & Decisions',
      description: 'Document decisions and action items',
      component: 'outputs'
    },
    {
      label: 'Action Planning',
      description: 'Plan and assign follow-up actions',
      component: 'actions'
    },
    {
      label: 'Completion & Analytics',
      description: 'Complete review and analyze effectiveness',
      component: 'completion'
    }
  ];

  if (loading) return <Box sx={{ p: 3 }}><LinearProgress /></Box>;
  if (error) return <Box sx={{ p: 3 }}><Alert severity="error">{error}</Alert></Box>;
  if (!review) return null;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4">{review.title}</Typography>
          <Stack direction="row" alignItems="center" spacing={2} sx={{ mt: 1 }}>
            <Chip label={review.status} color={getStatusColor(review.status)} />
            {review.review_type && <Chip label={review.review_type} variant="outlined" />}
            {review.review_effectiveness_score && (
              <Chip 
                label={`Effectiveness: ${review.review_effectiveness_score}/10`} 
                color="primary" 
                variant="outlined"
              />
            )}
          </Stack>
        </Box>
        <Stack direction="row" spacing={2}>
          {review.status === 'planned' && (
            <Button
              variant="contained"
              startIcon={<StartIcon />}
              onClick={startReview}
            >
              Start Review
            </Button>
          )}
          {review.status === 'in_progress' && (
            <Button
              variant="contained"
              color="success"
              startIcon={<CheckIcon />}
              onClick={completeReview}
            >
              Complete Review
            </Button>
          )}
          <Button
            variant="outlined"
            startIcon={<AnalyticsIcon />}
            onClick={() => setTabValue(4)}
          >
            Analytics
          </Button>
        </Stack>
      </Stack>

      {/* Progress Stepper */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stepper activeStep={activeStep} orientation="horizontal">
          {reviewSteps.map((step, index) => (
            <Step key={step.label} completed={getStepStatus(index) === 'completed'}>
              <StepLabel>
                <Typography variant="subtitle2">{step.label}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {step.description}
                </Typography>
              </StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Main Content Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Overview" />
          <Tab label="Inputs" />
          <Tab label="Outputs" />
          <Tab label="Actions" />
          <Tab label="Analytics" />
          <Tab label="Attendance" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Review Information</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Review Date</Typography>
                    <Typography variant="body1">
                      {review.review_date ? new Date(review.review_date).toLocaleString() : 'Not scheduled'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Review Type</Typography>
                    <Typography variant="body1">{review.review_type || 'Scheduled'}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Review Scope</Typography>
                    <Typography variant="body1">{review.review_scope || 'Not specified'}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Participants</Typography>
                    <Typography variant="body1">
                      {review.attendees && Array.isArray(review.attendees) 
                        ? `${review.attendees.length} participants`
                        : 'Not specified'}
                    </Typography>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                <Typography variant="h6" gutterBottom>ISO 22000:2018 Compliance</Typography>
                <Stack spacing={1}>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    {review.food_safety_policy_reviewed ? <CheckIcon color="success" /> : <WarningIcon color="warning" />}
                    <Typography variant="body2">Food Safety Policy Reviewed</Typography>
                  </Stack>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    {review.food_safety_objectives_reviewed ? <CheckIcon color="success" /> : <WarningIcon color="warning" />}
                    <Typography variant="body2">Food Safety Objectives Reviewed</Typography>
                  </Stack>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    {review.fsms_changes_required ? <WarningIcon color="warning" /> : <CheckIcon color="success" />}
                    <Typography variant="body2">FSMS Changes {review.fsms_changes_required ? 'Required' : 'Not Required'}</Typography>
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Stack spacing={2}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Quick Stats</Typography>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Inputs Collected</Typography>
                      <Typography variant="h4">{inputs.length}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Outputs Generated</Typography>
                      <Typography variant="h4">{outputs.length}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Actions Created</Typography>
                      <Typography variant="h4">{actions.length}</Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>

              {review.status === 'planned' && (
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Next Steps</Typography>
                    <Stack spacing={1}>
                      <Button
                        fullWidth
                        variant="outlined"
                        startIcon={<CollectIcon />}
                        onClick={collectInputs}
                        disabled={collectingInputs}
                      >
                        {collectingInputs ? 'Collecting...' : 'Collect Inputs'}
                      </Button>
                      <Button
                        fullWidth
                        variant="contained"
                        startIcon={<StartIcon />}
                        onClick={startReview}
                      >
                        Start Review
                      </Button>
                    </Stack>
                  </CardContent>
                </Card>
              )}
            </Stack>
          </Grid>
        </Grid>
      )}

      {tabValue === 1 && (
        <Box>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">Review Inputs</Typography>
            <Button
              variant="contained"
              startIcon={<CollectIcon />}
              onClick={collectInputs}
              disabled={collectingInputs}
            >
              {collectingInputs ? 'Collecting...' : 'Collect All Inputs'}
            </Button>
          </Stack>
          
          {inputs.length === 0 ? (
            <Alert severity="info">
              No inputs collected yet. Click "Collect All Inputs" to automatically gather data from all integrated modules.
            </Alert>
          ) : (
            <Grid container spacing={2}>
              {inputs.map((input, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">{input.input_type?.replace('_', ' ').toUpperCase()}</Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Source: {input.input_source || 'Automated'}
                      </Typography>
                      <Typography variant="body2">{input.input_summary}</Typography>
                      {input.data_completeness_score && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption">
                            Completeness: {Math.round(input.data_completeness_score * 100)}%
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={input.data_completeness_score * 100}
                            sx={{ mt: 0.5 }}
                          />
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      )}

      {tabValue === 2 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>Review Outputs & Decisions</Typography>
          {outputs.length === 0 ? (
            <Alert severity="info">
              No outputs recorded yet. Outputs will be generated during the review meeting.
            </Alert>
          ) : (
            <Stack spacing={2}>
              {outputs.map((output, index) => (
                <Card key={index}>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6">{output.title}</Typography>
                        <Chip label={output.output_type} size="small" sx={{ mt: 1 }} />
                        <Typography variant="body2" sx={{ mt: 1 }}>{output.description}</Typography>
                        {output.progress_percentage > 0 && (
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="caption">Progress: {output.progress_percentage}%</Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={output.progress_percentage}
                              sx={{ mt: 0.5 }}
                            />
                          </Box>
                        )}
                      </Box>
                      <Chip 
                        label={output.status} 
                        color={output.completed ? 'success' : 'default'}
                      />
                    </Stack>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          )}
        </Box>
      )}

      {tabValue === 3 && (
        <Box>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">Action Items</Typography>
            <Button variant="contained" startIcon={<AssignmentIcon />} onClick={addAction}>
              Add Action
            </Button>
          </Stack>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              {actions.length === 0 ? (
                <Alert severity="info">No action items yet. Add actions to track follow-up tasks.</Alert>
              ) : (
                <Stack spacing={2}>
                  {actions.map((action, index) => (
                    <Card key={index}>
                      <CardContent>
                        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                          <Box sx={{ flexGrow: 1 }}>
                            <Typography variant="h6">{action.title}</Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                              {action.description}
                            </Typography>
                            <Stack direction="row" spacing={1}>
                              <Chip label={action.priority} size="small" />
                              <Chip label={action.status} size="small" />
                              {action.due_date && (
                                <Chip 
                                  label={`Due: ${new Date(action.due_date).toLocaleDateString()}`} 
                                  size="small" 
                                  variant="outlined"
                                />
                              )}
                            </Stack>
                            {action.progress_percentage > 0 && (
                              <Box sx={{ mt: 2 }}>
                                <Typography variant="caption">Progress: {action.progress_percentage}%</Typography>
                                <LinearProgress 
                                  variant="determinate" 
                                  value={action.progress_percentage}
                                  sx={{ mt: 0.5 }}
                                />
                              </Box>
                            )}
                          </Box>
                          {!action.completed && (
                            <Button 
                              size="small" 
                              onClick={async () => {
                                await managementReviewAPI.completeAction(action.id);
                                load();
                              }}
                            >
                              Complete
                            </Button>
                          )}
                        </Stack>
                      </CardContent>
                    </Card>
                  ))}
                </Stack>
              )}
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Add New Action</Typography>
                  <Stack spacing={2}>
                    <TextField
                      label="Action Title"
                      fullWidth
                      value={actionForm.title}
                      onChange={(e) => setActionForm({ ...actionForm, title: e.target.value })}
                    />
                    <TextField
                      label="Description"
                      fullWidth
                      multiline
                      rows={3}
                      value={actionForm.description}
                      onChange={(e) => setActionForm({ ...actionForm, description: e.target.value })}
                    />
                    <FormControl fullWidth>
                      <InputLabel>Priority</InputLabel>
                      <Select
                        value={actionForm.priority}
                        onChange={(e) => setActionForm({ ...actionForm, priority: e.target.value })}
                        label="Priority"
                      >
                        <MenuItem value="low">Low</MenuItem>
                        <MenuItem value="medium">Medium</MenuItem>
                        <MenuItem value="high">High</MenuItem>
                        <MenuItem value="critical">Critical</MenuItem>
                      </Select>
                    </FormControl>
                    <TextField
                      label="Due Date"
                      type="date"
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      value={actionForm.due_date}
                      onChange={(e) => setActionForm({ ...actionForm, due_date: e.target.value })}
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          checked={actionForm.verification_required}
                          onChange={(e) => setActionForm({ ...actionForm, verification_required: e.target.checked })}
                        />
                      }
                      label="Verification Required"
                    />
                    <Button
                      variant="contained"
                      onClick={addAction}
                      disabled={!actionForm.title}
                      fullWidth
                    >
                      Add Action
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {tabValue === 4 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>Analytics & Compliance</Typography>
          {review.status !== 'completed' ? (
            <Alert severity="info">
              Analytics and compliance data will be available after the review is completed.
            </Alert>
          ) : (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Review Analytics</Typography>
                    {analytics.review_summary && (
                      <Stack spacing={2}>
                        <Box>
                          <Typography variant="body2" color="text.secondary">Effectiveness Score</Typography>
                          <Typography variant="h4">
                            {analytics.review_summary.effectiveness_score || 'N/A'}/10
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">Total Inputs</Typography>
                          <Typography variant="h4">
                            {analytics.input_analytics?.total_inputs || 0}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">Total Outputs</Typography>
                          <Typography variant="h4">
                            {analytics.output_analytics?.total_outputs || 0}
                          </Typography>
                        </Box>
                      </Stack>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>ISO Compliance</Typography>
                    {compliance.compliance_score && (
                      <Stack spacing={2}>
                        <Box>
                          <Typography variant="body2" color="text.secondary">Compliance Score</Typography>
                          <Typography variant="h4" color={compliance.compliance_score >= 80 ? 'success.main' : 'error.main'}>
                            {Math.round(compliance.compliance_score)}%
                          </Typography>
                        </Box>
                        {compliance.missing_inputs?.length > 0 && (
                          <Box>
                            <Typography variant="body2" color="text.secondary">Missing Inputs</Typography>
                            <Stack spacing={0.5}>
                              {compliance.missing_inputs.map((input: string, index: number) => (
                                <Chip key={index} label={input} size="small" color="warning" />
                              ))}
                            </Stack>
                          </Box>
                        )}
                        {compliance.recommendations?.length > 0 && (
                          <Box>
                            <Typography variant="body2" color="text.secondary">Recommendations</Typography>
                            <List dense>
                              {compliance.recommendations.map((rec: string, index: number) => (
                                <ListItem key={index}>
                                  <ListItemText primary={rec} />
                                </ListItem>
                              ))}
                            </List>
                          </Box>
                        )}
                      </Stack>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </Box>
      )}

      {tabValue === 5 && (
        <Box>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">Attendance Register</Typography>
          </Stack>
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              {(!attendance || attendance.length === 0) ? (
                <Alert severity="info">No attendees recorded. Add participants below.</Alert>
              ) : (
                <Stack spacing={2}>
                  {attendance.map((a, idx) => (
                    <Card key={idx}>
                      <CardContent>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Box>
                            <Typography variant="subtitle1">{a.name}</Typography>
                            <Typography variant="body2" color="text.secondary">{a.role}{a.department ? ` • ${a.department}` : ''}</Typography>
                            {a.email && <Typography variant="body2" color="text.secondary">{a.email}</Typography>}
                          </Box>
                          <Stack direction="row" spacing={1} alignItems="center">
                            <Chip label={a.attendance_status || 'present'} color={
                              (a.attendance_status === 'present' ? 'success' : a.attendance_status === 'partial' ? 'warning' : 'default') as any
                            } />
                            {review.status !== 'completed' && (
                              <Stack direction="row" spacing={1}>
                                <Button size="small" onClick={() => updateAttendeeStatus(idx, 'present')}>Present</Button>
                                <Button size="small" onClick={() => updateAttendeeStatus(idx, 'partial')}>Partial</Button>
                                <Button size="small" onClick={() => updateAttendeeStatus(idx, 'absent')}>Absent</Button>
                                <Button size="small" color="error" onClick={() => removeAttendee(idx)}>Remove</Button>
                              </Stack>
                            )}
                          </Stack>
                        </Stack>
                      </CardContent>
                    </Card>
                  ))}
                </Stack>
              )}
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Add Participant</Typography>
                  <Stack spacing={2}>
                    <TextField label="Name" value={newAttendee.name} onChange={(e) => setNewAttendee({ ...newAttendee, name: e.target.value })} fullWidth />
                    <TextField label="Role" value={newAttendee.role} onChange={(e) => setNewAttendee({ ...newAttendee, role: e.target.value })} fullWidth />
                    <TextField label="Department" value={newAttendee.department || ''} onChange={(e) => setNewAttendee({ ...newAttendee, department: e.target.value })} fullWidth />
                    <TextField label="Email" value={newAttendee.email || ''} onChange={(e) => setNewAttendee({ ...newAttendee, email: e.target.value })} fullWidth />
                    <FormControl fullWidth>
                      <InputLabel>Attendance Status</InputLabel>
                      <Select value={newAttendee.attendance_status || 'present'} label="Attendance Status" onChange={(e) => setNewAttendee({ ...newAttendee, attendance_status: e.target.value as any })}>
                        <MenuItem value="present">Present</MenuItem>
                        <MenuItem value="partial">Partial</MenuItem>
                        <MenuItem value="absent">Absent</MenuItem>
                      </Select>
                    </FormControl>
                    <Button variant="contained" onClick={addAttendee} disabled={!newAttendee.name || !newAttendee.role}>Add Participant</Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default ManagementReviewDetail;


