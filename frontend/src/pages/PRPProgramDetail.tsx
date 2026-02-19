import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Stack,
} from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';
import { prpAPI, usersAPI } from '../services/api';

const PRPProgramDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const programId = Number(id);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [program, setProgram] = useState<any>(null);
  const [checklists, setChecklists] = useState<any[]>([]);

  // Add Checklist dialog state
  const [openChecklistDialog, setOpenChecklistDialog] = useState(false);
  const [creating, setCreating] = useState(false);
  const [checklistForm, setChecklistForm] = useState({
    checklist_code: '',
    name: '',
    description: '',
    scheduled_date: '',
    due_date: '',
    assigned_to: 0,
  });
  const [userSearch, setUserSearch] = useState('');
  type UserOption = { id: number; username: string; full_name?: string };
  const [userOptions, setUserOptions] = useState<Array<UserOption>>([]);
  const [selectedAssignee, setSelectedAssignee] = useState<UserOption | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [programResp, checklistsResp] = await Promise.all([
          prpAPI.getProgram(programId),
          prpAPI.getChecklists(programId, { page: 1, size: 50 }),
        ]);
        setProgram(programResp?.data || programResp);
        setChecklists(checklistsResp?.data?.items || []);
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load program');
      } finally {
        setLoading(false);
      }
    };
    if (!Number.isNaN(programId)) load();
  }, [programId]);

  // Fetch users for assignee Autocomplete
  useEffect(() => {
    let active = true;
    const t = setTimeout(async () => {
      try {
        const resp: any = await usersAPI.getUsers({ page: 1, size: 10, search: userSearch });
        const items = (resp?.data?.items || resp?.items || []) as Array<any>;
        if (active) setUserOptions(items.map((u: any) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch {
        if (active) setUserOptions([]);
      }
    }, 300);
    return () => { active = false; clearTimeout(t); };
  }, [userSearch]);

  const reloadChecklists = async () => {
    try {
      const resp = await prpAPI.getChecklists(programId, { page: 1, size: 50 });
      setChecklists(resp?.data?.items || []);
    } catch {}
  };

  const handleCreateChecklist = async () => {
    if (!selectedAssignee?.id) {
      setError('Please select an assignee');
      return;
    }
    if (!checklistForm.checklist_code || !checklistForm.name || !checklistForm.scheduled_date || !checklistForm.due_date) {
      setError('Please fill in required fields');
      return;
    }
    try {
      setCreating(true);
      const payload = { ...checklistForm, assigned_to: selectedAssignee.id };
      const resp = await prpAPI.createChecklist(programId, payload);
      if (resp?.success) {
        setOpenChecklistDialog(false);
        setChecklistForm({ checklist_code: '', name: '', description: '', scheduled_date: '', due_date: '', assigned_to: 0 });
        setSelectedAssignee(null);
        await reloadChecklists();
      } else {
        setError(resp?.message || 'Failed to create checklist');
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to create checklist');
    } finally {
      setCreating(false);
    }
  };

  const getStatusColor = (status?: string) => {
    switch (String(status || '').toLowerCase()) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'suspended': return 'warning';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={360}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!program) return null;

  const safeDate = (d?: string) => {
    try { return d ? new Date(d).toLocaleDateString() : '—'; } catch { return '—'; }
  };

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            {program.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Program Code: {program.program_code}
          </Typography>
        </Box>
        <Button variant="outlined" onClick={() => navigate('/prp?tab=programs')}>Back to Programs</Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>ISO Program Overview</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Category</Typography>
                  <Chip label={String(program.category || '').replace(/_/g,' ').toUpperCase()} size="small" />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Chip label={String(program.status || '').toUpperCase()} color={getStatusColor(program.status) as any} size="small" />
                </Grid>
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Objective</Typography>
                  <Typography variant="body1">{program.objective || '—'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Scope</Typography>
                  <Typography variant="body1">{program.scope || '—'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Responsible Department</Typography>
                  <Typography variant="body1">{program.responsible_department || '—'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Responsible Person</Typography>
                  <Typography variant="body1">{program.responsible_person || '—'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">SOP Reference</Typography>
                  <Typography variant="body1">{program.sop_reference || '—'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Monitoring / Verification</Typography>
                  <Typography variant="body1">
                    {(program.monitoring_frequency || '—') + ' / ' + (program.verification_frequency || '—')}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Acceptance Criteria</Typography>
                  <Typography variant="body1">{program.acceptance_criteria || '—'}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          <Box mt={3}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="h6">Program Checklists</Typography>
                  <Button variant="contained" onClick={() => setOpenChecklistDialog(true)}>Add Checklist</Button>
                </Box>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Checklist</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Scheduled</TableCell>
                        <TableCell>Due</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {checklists.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={4} align="center">No checklists</TableCell>
                        </TableRow>
                      ) : (
                        checklists.map((c) => (
                          <TableRow key={c.id} hover>
                            <TableCell>
                              <Typography variant="body2" fontWeight="medium">{c.checklist_code}</Typography>
                              <Typography variant="body1" fontWeight="bold">{c.name}</Typography>
                            </TableCell>
                            <TableCell>
                              <Chip label={String(c.status || '').toUpperCase()} size="small" />
                            </TableCell>
                            <TableCell>{safeDate(c.scheduled_date)}</TableCell>
                            <TableCell>{safeDate(c.due_date)}</TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Box>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Summary</Typography>
              <Grid container spacing={1}>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Total Checklists</Typography>
                  <Typography variant="h5">{program.checklist_count}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Overdue</Typography>
                  <Typography variant="h5" color={program.overdue_count > 0 ? 'error' : 'inherit'}>
                    {program.overdue_count}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Next Due Date</Typography>
                  <Typography variant="body1">{program.next_due_date ? new Date(program.next_due_date).toLocaleDateString() : '—'}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Dialog open={openChecklistDialog} onClose={() => setOpenChecklistDialog(false)} fullWidth maxWidth="sm">
        <DialogTitle>Add Checklist</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField label="Checklist Code" fullWidth value={checklistForm.checklist_code} onChange={(e) => setChecklistForm({ ...checklistForm, checklist_code: e.target.value })} />
            <TextField label="Name" fullWidth value={checklistForm.name} onChange={(e) => setChecklistForm({ ...checklistForm, name: e.target.value })} />
            <TextField label="Description" fullWidth multiline minRows={3} value={checklistForm.description} onChange={(e) => setChecklistForm({ ...checklistForm, description: e.target.value })} />
            <TextField label="Scheduled Date" type="date" fullWidth InputLabelProps={{ shrink: true }} value={checklistForm.scheduled_date} onChange={(e) => setChecklistForm({ ...checklistForm, scheduled_date: e.target.value })} />
            <TextField label="Due Date" type="date" fullWidth InputLabelProps={{ shrink: true }} value={checklistForm.due_date} onChange={(e) => setChecklistForm({ ...checklistForm, due_date: e.target.value })} />
            <Autocomplete
              options={userOptions}
              getOptionLabel={(o) => o.full_name || o.username || ''}
              value={selectedAssignee}
              onChange={(_, v) => setSelectedAssignee(v)}
              onInputChange={(_, v) => setUserSearch(v)}
              renderInput={(params) => <TextField {...params} label="Assign To" />}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenChecklistDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateChecklist} disabled={creating}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PRPProgramDetail;