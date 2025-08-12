import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import { Box, Typography, Chip, Paper, Divider, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Stack, Autocomplete } from '@mui/material';
import FishboneDiagram from '../components/NC/FishboneDiagram';
import { AppDispatch, RootState } from '../store';
import { createFiveWhys, createIshikawa, fetchCAPAList, fetchNonConformance, updateNonConformance, fetchRCAList } from '../store/slices/ncSlice';
import { ncAPI, usersAPI } from '../services/api';
import Alert from '@mui/material/Alert';

const NonConformanceDetail: React.FC = () => {
  const { id } = useParams();
  const ncId = Number(id);
  const dispatch = useDispatch<AppDispatch>();
  const { detail, capaList, rcaList } = useSelector((s: RootState) => s.nc);
  const [errorMsg, setErrorMsg] = useState<string | undefined>(undefined);
  const [openFiveWhys, setOpenFiveWhys] = useState(false);
  const [openIshikawa, setOpenIshikawa] = useState(false);
  const [ishikawa, setIshikawa] = useState<{ problem: string; categories: Record<string, string[]> }>({ problem: '', categories: { People: [], Process: [], Equipment: [], Materials: [], Environment: [], Management: [] } });
  const [fiveWhys, setFiveWhys] = useState({ problem: '', why_1: '', why_2: '', why_3: '', why_4: '', why_5: '', root_cause: '' });
  const [status, setStatus] = useState('');
  const [openCapa, setOpenCapa] = useState(false);
  const [capaForm, setCapaForm] = useState({ title: '', description: '', action_type: 'corrective', responsible_person: '', target_completion_date: '' });
  const [userSearch, setUserSearch] = useState('');
  const [userOptions, setUserOptions] = useState<Array<{ id: number; username: string; full_name?: string }>>([]);
  const [responsibleOpen, setResponsibleOpen] = useState(false);
  const [responsibleInput, setResponsibleInput] = useState('');
  const [responsibleSelected, setResponsibleSelected] = useState<{ id: number; username: string; full_name?: string } | null>(null);

  useEffect(() => {
    let active = true;
    const q = responsibleInput.trim();
    if (!responsibleOpen) return;
    if (q.length < 2) {
      setUserOptions([]);
      return;
    }
    const t = setTimeout(async () => {
      try {
        const resp: any = await usersAPI.getUsers({ page: 1, size: 10, search: q });
        const items = (resp?.data?.items || resp?.items || []) as Array<any>;
        if (active) setUserOptions(items.map((u) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch {
        if (active) setUserOptions([]);
      }
    }, 300);
    return () => { active = false; clearTimeout(t); };
  }, [responsibleInput, responsibleOpen]);

  useEffect(() => {
    if (!Number.isNaN(ncId)) {
      dispatch(fetchNonConformance(ncId));
      dispatch(fetchCAPAList({ non_conformance_id: ncId, page: 1, size: 10 }));
      dispatch(fetchRCAList(ncId));
    }
  }, [dispatch, ncId]);

  useEffect(() => {
    if (detail?.status) setStatus(detail.status);
  }, [detail]);

  const submitFiveWhys = async () => {
    try {
      await dispatch(createFiveWhys({ ncId, payload: fiveWhys })).unwrap();
      setOpenFiveWhys(false);
      dispatch(fetchNonConformance(ncId));
      dispatch(fetchRCAList(ncId));
      setErrorMsg(undefined);
    } catch (e: any) {
      setErrorMsg(e?.message || 'Failed to save 5-Whys');
    }
  };

  const submitIshikawa = async () => {
    try {
      await dispatch(createIshikawa({ ncId, payload: { problem: ishikawa.problem || fiveWhys.problem, categories: ishikawa.categories, diagram_data: {} } })).unwrap();
      setOpenIshikawa(false);
      dispatch(fetchNonConformance(ncId));
      dispatch(fetchRCAList(ncId));
      setErrorMsg(undefined);
    } catch (e: any) {
      setErrorMsg(e?.message || 'Failed to save Ishikawa');
    }
  };

  const saveStatus = async () => {
    await dispatch(updateNonConformance({ ncId, payload: { status } }));
    dispatch(fetchNonConformance(ncId));
  };

  const submitCapa = async () => {
    try {
      // simple client validation
      if (!capaForm.title || !capaForm.description) throw new Error('Title and Description are required');
      if (!responsibleSelected?.id) throw new Error('Responsible person is required');
      if (!capaForm.target_completion_date) throw new Error('Target completion date is required');

      await ncAPI.createCAPA(ncId, {
        title: capaForm.title,
        description: capaForm.description,
        action_type: capaForm.action_type || undefined,
        responsible_person: Number(responsibleSelected.id),
        target_completion_date: new Date(`${capaForm.target_completion_date}T00:00:00`).toISOString(),
        non_conformance_id: ncId,
      });
      setOpenCapa(false);
      setCapaForm({ title: '', description: '', action_type: 'corrective', responsible_person: '', target_completion_date: '' });
      setResponsibleSelected(null);
      setResponsibleInput('');
      dispatch(fetchCAPAList({ non_conformance_id: ncId, page: 1, size: 10 }));
    } catch (e) {
      setErrorMsg((e as any)?.message || 'Failed to create CAPA');
    }
  };

  if (!detail) return null;

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight="bold" gutterBottom>NC {detail.nc_number}</Typography>
      {errorMsg && <Alert severity="error" sx={{ mb: 2 }}>{errorMsg}</Alert>}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6">{detail.title}</Typography>
        <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap' }}>
          <Chip label={`Status: ${String(detail.status).split('_').join(' ')}`} />
          <Chip label={`Severity: ${detail.severity}`} />
          <Chip label={`Source: ${detail.source}`} />
          {detail.batch_reference && <Chip label={`Batch: ${detail.batch_reference}`} />}
        </Stack>
        <Typography variant="body2" sx={{ mt: 2 }}>{detail.description}</Typography>
        <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
          <TextField size="small" label="Update Status" value={status} onChange={e => setStatus(e.target.value)} placeholder={String(detail.status)} />
          <Button variant="outlined" onClick={saveStatus}>Save</Button>
        </Stack>
      </Paper>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" spacing={2}>
          <Button variant="contained" onClick={() => setOpenFiveWhys(true)}>Add 5-Whys</Button>
          <Button variant="outlined" onClick={() => setOpenIshikawa(true)}>Add Ishikawa</Button>
          <Button variant="outlined" onClick={() => setOpenCapa(true)}>Add CAPA</Button>
        </Stack>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Root Cause Analyses</Typography>
        {rcaList.loading ? (
          <Typography variant="body2" color="text.secondary">Loading…</Typography>
        ) : (rcaList.items && rcaList.items.length > 0 ? (
          rcaList.items.map((rca: any) => (
            <Box key={rca.id} sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ mb: 0.5 }}><strong>Method:</strong> {rca.method}</Typography>
              {rca.method === 'five_whys' && (
                <Typography variant="caption">Why1: {rca.why_1} | Why2: {rca.why_2} | Why3: {rca.why_3} | Why4: {rca.why_4} | Why5: {rca.why_5} | Root: {rca.root_cause}</Typography>
              )}
              {rca.method === 'ishikawa' && (
                <Box sx={{ mt: 1, border: '1px solid #eee', borderRadius: 1, p: 1 }}>
                  <FishboneDiagram problem={rca.problem || detail?.title || 'Problem'} categories={rca.fishbone_categories || {}} />
                </Box>
              )}
            </Box>
          ))
        ) : (
          <Typography variant="body2" color="text.secondary">No root cause analyses yet.</Typography>
        ))}
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>CAPA Actions</Typography>
        <Divider sx={{ mb: 2 }} />
        {capaList.items.length === 0 ? (
          <Typography variant="body2" color="text.secondary">No CAPA actions yet.</Typography>
        ) : (
          capaList.items.map((capa: any) => (
            <Box key={capa.id} sx={{ mb: 1 }}>
              <Typography variant="subtitle1">{capa.capa_number} - {capa.title}</Typography>
              <Typography variant="caption">Status: {String(capa.status).split('_').join(' ')} | Progress: {capa.progress_percentage}% | Target: {capa.target_completion_date}</Typography>
            </Box>
          ))
        )}
      </Paper>

      {/* 5-Whys Modal */}
      <Dialog open={openFiveWhys} onClose={() => setOpenFiveWhys(false)} maxWidth="sm" fullWidth>
        <DialogTitle>5-Whys Analysis</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Problem" value={fiveWhys.problem} onChange={e => setFiveWhys({ ...fiveWhys, problem: e.target.value })} />
            <TextField label="Why 1" value={fiveWhys.why_1} onChange={e => setFiveWhys({ ...fiveWhys, why_1: e.target.value })} />
            <TextField label="Why 2" value={fiveWhys.why_2} onChange={e => setFiveWhys({ ...fiveWhys, why_2: e.target.value })} />
            <TextField label="Why 3" value={fiveWhys.why_3} onChange={e => setFiveWhys({ ...fiveWhys, why_3: e.target.value })} />
            <TextField label="Why 4" value={fiveWhys.why_4} onChange={e => setFiveWhys({ ...fiveWhys, why_4: e.target.value })} />
            <TextField label="Why 5" value={fiveWhys.why_5} onChange={e => setFiveWhys({ ...fiveWhys, why_5: e.target.value })} />
            <TextField label="Root Cause" value={fiveWhys.root_cause} onChange={e => setFiveWhys({ ...fiveWhys, root_cause: e.target.value })} />
            <Button variant="contained" onClick={submitFiveWhys}>Save</Button>
          </Stack>
        </DialogContent>
      </Dialog>

      {/* Ishikawa Modal */}
      <Dialog open={openIshikawa} onClose={() => setOpenIshikawa(false)} maxWidth="md" fullWidth>
        <DialogTitle>Ishikawa (Fishbone) Analysis</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField fullWidth label="Problem" value={ishikawa.problem} onChange={e => setIshikawa({ ...ishikawa, problem: e.target.value })} />
            {Object.keys(ishikawa.categories).map((cat) => (
              <TextField
                key={cat}
                fullWidth
                label={`${cat} factors (comma separated)`}
                value={(ishikawa.categories[cat] || []).join(', ')}
                onChange={e => setIshikawa({ ...ishikawa, categories: { ...ishikawa.categories, [cat]: e.target.value.split(',').map(s => s.trim()).filter(Boolean) } })}
              />
            ))}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenIshikawa(false)}>Cancel</Button>
          <Button variant="contained" onClick={submitIshikawa}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* CAPA Modal */}
      <Dialog open={openCapa} onClose={() => setOpenCapa(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New CAPA</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Title" value={capaForm.title} onChange={e => setCapaForm({ ...capaForm, title: e.target.value })} />
            <TextField label="Description" multiline rows={3} value={capaForm.description} onChange={e => setCapaForm({ ...capaForm, description: e.target.value })} />
            <TextField label="Action Type" value={capaForm.action_type} onChange={e => setCapaForm({ ...capaForm, action_type: e.target.value })} />
            <Autocomplete
              options={userOptions}
              open={responsibleOpen}
              onOpen={() => setResponsibleOpen(true)}
              onClose={() => setResponsibleOpen(false)}
              getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
              value={responsibleSelected}
              onChange={(_, val) => {
                setResponsibleSelected(val);
                setCapaForm({ ...capaForm, responsible_person: val ? String(val.id) : '' });
              }}
              inputValue={responsibleInput}
              onInputChange={(_, val) => setResponsibleInput(val)}
              isOptionEqualToValue={(opt, val) => opt.id === val.id}
              renderInput={(params) => <TextField {...params} label="Responsible Person" placeholder="Type at least 2 characters" fullWidth />}
            />
            <TextField type="date" label="Target Completion" InputLabelProps={{ shrink: true }} value={capaForm.target_completion_date} onChange={e => setCapaForm({ ...capaForm, target_completion_date: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCapa(false)}>Cancel</Button>
          <Button variant="contained" onClick={submitCapa}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default NonConformanceDetail;

