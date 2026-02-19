import React, { useEffect, useMemo, useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tabs,
  Tab,
  Box,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormControlLabel,
  Checkbox,
  Typography,
  Card,
  CardContent,
  Autocomplete,
} from '@mui/material';
import { traceabilityAPI } from '../../services/traceabilityAPI';
import { usersAPI } from '../../services/api';
import NotificationToast from '../UI/NotificationToast';

interface RecallDetailProps {
  open: boolean;
  onClose: () => void;
  recallId: number;
  recallTitle?: string;
}

const RecallDetail: React.FC<RecallDetailProps> = ({ open, onClose, recallId, recallTitle }) => {
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [actions, setActions] = useState<any[]>([]);
  const [rca, setRca] = useState<any | null>(null);
  const [measures, setMeasures] = useState<any[]>([]);
  const [plans, setPlans] = useState<any[]>([]);
  const [reviews, setReviews] = useState<any[]>([]);

  const [actionForm, setActionForm] = useState({
    action_type: 'investigation',
    description: '',
    assigned_to: '',
    due_date: '',
  });
  const [assigneeInput, setAssigneeInput] = useState('');
  const [assigneeOptions, setAssigneeOptions] = useState<Array<{ id: number; username: string; full_name?: string }>>([]);
  const [selectedAssignee, setSelectedAssignee] = useState<{ id: number; username: string; full_name?: string } | null>(null);
  const [toast, setToast] = useState<{ open: boolean; message: string; severity: 'success'|'error'|'warning'|'info' }>(
    { open: false, message: '', severity: 'info' }
  );
  const [dirty, setDirty] = useState(false);
  const [rcaForm, setRcaForm] = useState({
    immediate_cause: '',
    underlying_cause: '',
    systemic_cause: '',
    analysis_date: '',
    analyzed_by: '',
  });
  const [measureForm, setMeasureForm] = useState({
    measure_type: 'process_improvement',
    description: '',
    implementation_date: '',
    responsible_person: '',
  });
  const [planForm, setPlanForm] = useState({
    verification_methods: '',
    verification_schedule: '',
    responsible_person: '',
    success_criteria: '',
  });
  const [reviewForm, setReviewForm] = useState({
    review_date: '',
    reviewed_by: '',
    effectiveness_score: '',
    additional_actions_required: false,
    review_notes: '',
  });

  useEffect(() => {
    if (!open) return;
    // initial users load
    (async () => {
      try {
        const res: any = await usersAPI.getUsers({ size: 10 });
        const items = res?.data?.items || res?.data?.users || res?.items || res?.users || [];
        setAssigneeOptions(items.map((u: any) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch (e) {
        // eslint-disable-next-line no-console
        console.warn('Failed to load initial users');
      }
    })();
    const loadAll = async () => {
      setLoading(true);
      try {
        const [actionsResp, rcaResp, measuresResp, plansResp, reviewsResp] = await Promise.all([
          traceabilityAPI.getCorrectiveActions(recallId),
          traceabilityAPI.getRootCauseAnalysis(recallId),
          traceabilityAPI.getPreventiveMeasures(recallId),
          traceabilityAPI.getVerificationPlans(recallId),
          traceabilityAPI.getEffectivenessReviews(recallId),
        ]);
        setActions(actionsResp?.items || actionsResp?.data?.items || []);
        setRca(rcaResp?.data || rcaResp || null);
        setMeasures(measuresResp?.items || measuresResp?.data?.items || []);
        setPlans(plansResp?.items || plansResp?.data?.items || []);
        setReviews(reviewsResp?.items || reviewsResp?.data?.items || []);
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    loadAll();
  }, [open, recallId]);

  // Debounced user search for Autocomplete fields to avoid empty options
  useEffect(() => {
    if (!open) return;
    const handle = setTimeout(async () => {
      try {
        const res: any = await usersAPI.getUsers({ search: assigneeInput, size: 10 });
        const items = res?.data?.items || res?.data?.users || res?.items || res?.users || [];
        setAssigneeOptions(items.map((u: any) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch (e) {
        // eslint-disable-next-line no-console
        console.warn('User search failed');
      }
    }, 300);
    return () => clearTimeout(handle);
  }, [assigneeInput, open]);

  const handleCreateAction = async () => {
    if (!actionForm.description.trim()) {
      setToast({ open: true, message: 'Description is required', severity: 'warning' });
      return;
    }
    await traceabilityAPI.createCorrectiveAction(recallId, {
      action_type: actionForm.action_type,
      description: actionForm.description,
      assigned_to: selectedAssignee?.id,
      due_date: actionForm.due_date || undefined,
    });
    const resp = await traceabilityAPI.getCorrectiveActions(recallId);
    setActions(resp?.items || resp?.data?.items || []);
    setActionForm({ action_type: 'investigation', description: '', assigned_to: '', due_date: '' });
    setSelectedAssignee(null);
    setAssigneeInput('');
    setDirty(true);
    setToast({ open: true, message: 'Action added', severity: 'success' });
  };

  const handleSaveRca = async () => {
    if (!rcaForm.immediate_cause.trim() || !rcaForm.underlying_cause.trim() || !rcaForm.systemic_cause.trim()) {
      setToast({ open: true, message: 'Complete all RCA cause fields', severity: 'warning' });
      return;
    }
    await traceabilityAPI.createRootCauseAnalysis(recallId, {
      immediate_cause: rcaForm.immediate_cause,
      underlying_cause: rcaForm.underlying_cause,
      systemic_cause: rcaForm.systemic_cause,
      analysis_date: rcaForm.analysis_date,
      analyzed_by: Number(rcaForm.analyzed_by),
    });
    const resp = await traceabilityAPI.getRootCauseAnalysis(recallId);
    setRca(resp?.data || resp || null);
    setRcaForm({ immediate_cause: '', underlying_cause: '', systemic_cause: '', analysis_date: '', analyzed_by: '' });
    setDirty(true);
    setToast({ open: true, message: 'Root cause analysis saved', severity: 'success' });
  };

  const handleCreateMeasure = async () => {
    if (!measureForm.description.trim()) {
      setToast({ open: true, message: 'Description is required', severity: 'warning' });
      return;
    }
    await traceabilityAPI.createPreventiveMeasure(recallId, {
      measure_type: measureForm.measure_type,
      description: measureForm.description,
      implementation_date: measureForm.implementation_date || undefined,
      responsible_person: Number(measureForm.responsible_person),
    });
    const resp = await traceabilityAPI.getPreventiveMeasures(recallId);
    setMeasures(resp?.items || resp?.data?.items || []);
    setMeasureForm({ measure_type: 'process_improvement', description: '', implementation_date: '', responsible_person: '' });
    setDirty(true);
    setToast({ open: true, message: 'Preventive measure added', severity: 'success' });
  };

  const handleCreatePlan = async () => {
    if (!planForm.verification_methods.trim() || !planForm.verification_schedule.trim()) {
      setToast({ open: true, message: 'Methods and schedule are required', severity: 'warning' });
      return;
    }
    await traceabilityAPI.createVerificationPlan(recallId, {
      verification_methods: planForm.verification_methods.split(',').map(s => s.trim()).filter(Boolean),
      verification_schedule: planForm.verification_schedule,
      responsible_person: Number(planForm.responsible_person),
      success_criteria: planForm.success_criteria.split(',').map(s => s.trim()).filter(Boolean),
    });
    const resp = await traceabilityAPI.getVerificationPlans(recallId);
    setPlans(resp?.items || resp?.data?.items || []);
    setPlanForm({ verification_methods: '', verification_schedule: '', responsible_person: '', success_criteria: '' });
    setDirty(true);
    setToast({ open: true, message: 'Verification plan added', severity: 'success' });
  };

  const handleCreateReview = async () => {
    if (!reviewForm.review_date || !reviewForm.reviewed_by || reviewForm.effectiveness_score === '') {
      setToast({ open: true, message: 'Review date, reviewer, and score are required', severity: 'warning' });
      return;
    }
    await traceabilityAPI.createEffectivenessReview(recallId, {
      review_date: reviewForm.review_date,
      reviewed_by: Number(reviewForm.reviewed_by),
      effectiveness_score: Number(reviewForm.effectiveness_score),
      additional_actions_required: reviewForm.additional_actions_required,
      review_notes: reviewForm.review_notes || undefined,
    });
    const resp = await traceabilityAPI.getEffectivenessReviews(recallId);
    setReviews(resp?.items || resp?.data?.items || []);
    setReviewForm({ review_date: '', reviewed_by: '', effectiveness_score: '', additional_actions_required: false, review_notes: '' });
    setDirty(true);
    setToast({ open: true, message: 'Effectiveness review added', severity: 'success' });
  };

  return (
    <Dialog open={open} onClose={() => { onClose(); }} maxWidth="lg" fullWidth>
      <DialogTitle>Recall Details{recallTitle ? ` — ${recallTitle}` : ''}</DialogTitle>
      <DialogContent dividers>
        <Tabs value={tab} onChange={(_e, v) => setTab(v)} sx={{ mb: 2 }}>
          <Tab label="Corrective Actions" />
          <Tab label="Root Cause Analysis" />
          <Tab label="Preventive Measures" />
          <Tab label="Verification Plans" />
          <Tab label="Effectiveness Reviews" />
        </Tabs>

        {tab === 0 && (
          <Box>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Action Type</InputLabel>
                  <Select value={actionForm.action_type} label="Action Type" onChange={(e) => setActionForm({ ...actionForm, action_type: e.target.value })}>
                    <MenuItem value="notification">Notification</MenuItem>
                    <MenuItem value="retrieval">Retrieval</MenuItem>
                    <MenuItem value="disposal">Disposal</MenuItem>
                    <MenuItem value="investigation">Investigation</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={5}>
                <TextField fullWidth label="Description" value={actionForm.description} onChange={(e) => setActionForm({ ...actionForm, description: e.target.value })} />
              </Grid>
              <Grid item xs={12} md={4}>
                <Autocomplete
                  options={assigneeOptions}
                  getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                  value={selectedAssignee}
                  onChange={(_, val) => setSelectedAssignee(val)}
                  onInputChange={(_, val) => setAssigneeInput(val)}
                  isOptionEqualToValue={(opt, val) => opt.id === val.id}
                  renderInput={(params) => <TextField {...params} label="Assign to" placeholder="Search user..." fullWidth />}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField fullWidth type="date" label="Due Date" InputLabelProps={{ shrink: true }} value={actionForm.due_date} onChange={(e) => setActionForm({ ...actionForm, due_date: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <Button variant="contained" onClick={handleCreateAction} disabled={loading}>Add Action</Button>
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              {actions.map((a) => (
                <Grid item xs={12} md={6} key={a.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2">{a.action_type.toUpperCase()}</Typography>
                      <Typography variant="body2" color="text.secondary">{a.description}</Typography>
                      <Typography variant="caption" display="block">Assigned: {a.assigned_to || '—'} | Due: {a.due_date || '—'} | Status: {a.status}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {tab === 1 && (
          <Box>
            {rca ? (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1">Existing Root Cause Analysis</Typography>
                <Typography variant="body2">Immediate: {rca.immediate_cause}</Typography>
                <Typography variant="body2">Underlying: {rca.underlying_cause}</Typography>
                <Typography variant="body2">Systemic: {rca.systemic_cause}</Typography>
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>No root cause analysis saved yet.</Typography>
            )}

            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField fullWidth label="Immediate Cause" value={rcaForm.immediate_cause} onChange={(e) => setRcaForm({ ...rcaForm, immediate_cause: e.target.value })} />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField fullWidth label="Underlying Cause" value={rcaForm.underlying_cause} onChange={(e) => setRcaForm({ ...rcaForm, underlying_cause: e.target.value })} />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField fullWidth label="Systemic Cause" value={rcaForm.systemic_cause} onChange={(e) => setRcaForm({ ...rcaForm, systemic_cause: e.target.value })} />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField fullWidth type="date" label="Analysis Date" InputLabelProps={{ shrink: true }} value={rcaForm.analysis_date} onChange={(e) => setRcaForm({ ...rcaForm, analysis_date: e.target.value })} />
              </Grid>
              <Grid item xs={12} md={4}>
                <Autocomplete
                  options={assigneeOptions}
                  getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                  value={assigneeOptions.find(o => String(o.id) === rcaForm.analyzed_by) || null}
                  onChange={(_, val) => setRcaForm({ ...rcaForm, analyzed_by: val ? String(val.id) : '' })}
                  onInputChange={(_, val) => setAssigneeInput(val)}
                  isOptionEqualToValue={(opt, val) => opt.id === val.id}
                  renderInput={(params) => <TextField {...params} label="Analyzed By" placeholder="Search user..." fullWidth />}
                />
              </Grid>
              <Grid item xs={12}>
                <Button variant="contained" onClick={handleSaveRca} disabled={loading}>Save RCA</Button>
              </Grid>
            </Grid>
          </Box>
        )}

        {tab === 2 && (
          <Box>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Measure Type</InputLabel>
                  <Select value={measureForm.measure_type} label="Measure Type" onChange={(e) => setMeasureForm({ ...measureForm, measure_type: e.target.value })}>
                    <MenuItem value="process_improvement">Process Improvement</MenuItem>
                    <MenuItem value="training">Training</MenuItem>
                    <MenuItem value="system_update">System Update</MenuItem>
                    <MenuItem value="monitoring">Monitoring</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth label="Description" value={measureForm.description} onChange={(e) => setMeasureForm({ ...measureForm, description: e.target.value })} />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField fullWidth type="date" label="Implementation Date" InputLabelProps={{ shrink: true }} value={measureForm.implementation_date} onChange={(e) => setMeasureForm({ ...measureForm, implementation_date: e.target.value })} />
              </Grid>
              <Grid item xs={12} md={4}>
                <Autocomplete
                  options={assigneeOptions}
                  getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                  value={assigneeOptions.find(o => String(o.id) === measureForm.responsible_person) || null}
                  onChange={(_, val) => setMeasureForm({ ...measureForm, responsible_person: val ? String(val.id) : '' })}
                  onInputChange={(_, val) => setAssigneeInput(val)}
                  isOptionEqualToValue={(opt, val) => opt.id === val.id}
                  renderInput={(params) => <TextField {...params} label="Responsible" placeholder="Search user..." fullWidth />}
                />
              </Grid>
              <Grid item xs={12}>
                <Button variant="contained" onClick={handleCreateMeasure} disabled={loading}>Add Measure</Button>
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              {measures.map((m) => (
                <Grid item xs={12} md={6} key={m.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2">{m.measure_type.replace('_', ' ').toUpperCase()}</Typography>
                      <Typography variant="body2" color="text.secondary">{m.description}</Typography>
                      <Typography variant="caption" display="block">Implementation: {m.implementation_date || '—'}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {tab === 3 && (
          <Box>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} md={6}>
                <TextField fullWidth label="Verification Methods (comma-separated)" value={planForm.verification_methods} onChange={(e) => setPlanForm({ ...planForm, verification_methods: e.target.value })} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth label="Verification Schedule" value={planForm.verification_schedule} onChange={(e) => setPlanForm({ ...planForm, verification_schedule: e.target.value })} />
              </Grid>
              <Grid item xs={12} md={6}>
                <Autocomplete
                  options={assigneeOptions}
                  getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                  value={assigneeOptions.find(o => String(o.id) === planForm.responsible_person) || null}
                  onChange={(_, val) => setPlanForm({ ...planForm, responsible_person: val ? String(val.id) : '' })}
                  onInputChange={(_, val) => setAssigneeInput(val)}
                  isOptionEqualToValue={(opt, val) => opt.id === val.id}
                  renderInput={(params) => <TextField {...params} label="Responsible" placeholder="Search user..." fullWidth />}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth label="Success Criteria (comma-separated)" value={planForm.success_criteria} onChange={(e) => setPlanForm({ ...planForm, success_criteria: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <Button variant="contained" onClick={handleCreatePlan} disabled={loading}>Add Plan</Button>
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              {plans.map((p) => (
                <Grid item xs={12} md={6} key={p.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2">Plan #{p.id}</Typography>
                      <Typography variant="body2">Methods: {(p.verification_methods || []).join(', ')}</Typography>
                      <Typography variant="body2">Schedule: {p.verification_schedule}</Typography>
                      <Typography variant="body2">Criteria: {(p.success_criteria || []).join(', ')}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {tab === 4 && (
          <Box>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} md={3}>
                <TextField fullWidth type="date" label="Review Date" InputLabelProps={{ shrink: true }} value={reviewForm.review_date} onChange={(e) => setReviewForm({ ...reviewForm, review_date: e.target.value })} />
              </Grid>
              <Grid item xs={12} md={3}>
                <Autocomplete
                  options={assigneeOptions}
                  getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                  value={assigneeOptions.find(o => String(o.id) === reviewForm.reviewed_by) || null}
                  onChange={(_, val) => setReviewForm({ ...reviewForm, reviewed_by: val ? String(val.id) : '' })}
                  onInputChange={(_, val) => setAssigneeInput(val)}
                  isOptionEqualToValue={(opt, val) => opt.id === val.id}
                  renderInput={(params) => <TextField {...params} label="Reviewed By" placeholder="Search user..." fullWidth />}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField fullWidth type="number" label="Effectiveness Score (0-100)" value={reviewForm.effectiveness_score} onChange={(e) => setReviewForm({ ...reviewForm, effectiveness_score: e.target.value })} />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControlLabel control={<Checkbox checked={reviewForm.additional_actions_required} onChange={(_e, c) => setReviewForm({ ...reviewForm, additional_actions_required: c })} />} label="Additional Actions Required" />
              </Grid>
              <Grid item xs={12}>
                <TextField fullWidth multiline rows={2} label="Review Notes" value={reviewForm.review_notes} onChange={(e) => setReviewForm({ ...reviewForm, review_notes: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <Button variant="contained" onClick={handleCreateReview} disabled={loading}>Add Review</Button>
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              {reviews.map((r) => (
                <Grid item xs={12} md={6} key={r.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2">Review #{r.id} — Score: {r.effectiveness_score}</Typography>
                      <Typography variant="body2">Date: {r.review_date}</Typography>
                      <Typography variant="body2">Additional actions required: {r.additional_actions_required ? 'Yes' : 'No'}</Typography>
                      {r.review_notes && <Typography variant="body2">Notes: {r.review_notes}</Typography>}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => { onClose(); }}>Close</Button>
      </DialogActions>
      <NotificationToast open={toast.open} message={toast.message} severity={toast.severity} onClose={() => setToast({ ...toast, open: false })} />
    </Dialog>
  );
};

export default RecallDetail;


