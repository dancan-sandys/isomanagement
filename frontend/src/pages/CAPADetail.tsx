import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Typography, Paper, Stack, Chip, Divider, TextField, Button, MenuItem, Switch, FormControlLabel } from '@mui/material';
import { AppDispatch, RootState } from '../store';
import { fetchCAPA } from '../store/slices/ncSlice';
import { ncAPI } from '../services/api';

const CAPADetail: React.FC = () => {
  const { id } = useParams();
  const capaId = Number(id);
  const dispatch = useDispatch<AppDispatch>();
  const { capaDetail } = useSelector((s: RootState) => s.nc);
  const [verifications, setVerifications] = useState<any[]>([]);
  const [verifyForm, setVerifyForm] = useState({ verification_date: '', verification_result: 'passed', effectiveness_score: '', comments: '' });
  const [errorMsg, setErrorMsg] = useState<string | undefined>(undefined);
  const [editForm, setEditForm] = useState({ status: '', progress_percentage: '', effectiveness_measured: false as boolean, effectiveness_score: '' });

  useEffect(() => {
    if (!Number.isNaN(capaId)) {
      dispatch(fetchCAPA(capaId));
    }
  }, [dispatch, capaId]);

  useEffect(() => {
    const loadVerifications = async () => {
      if (!capaDetail) return;
      const items = await ncAPI.getCAPAVerifications(capaDetail.non_conformance_id);
      const filtered = (items || []).filter((v: any) => v.capa_action_id === capaId);
      setVerifications(filtered);
    };
    loadVerifications();
  }, [capaDetail, capaId]);

  useEffect(() => {
    if (capaDetail) {
      setEditForm({
        status: String(capaDetail.status || ''),
        progress_percentage: String(capaDetail.progress_percentage ?? ''),
        effectiveness_measured: !!capaDetail.effectiveness_measured,
        effectiveness_score: String(capaDetail.effectiveness_score ?? ''),
      });
    }
  }, [capaDetail]);

  const submitVerification = async () => {
    if (!capaDetail) return;
    try {
      if (!verifyForm.verification_date) {
        throw new Error('Verification date is required');
      }
      await ncAPI.createCAPAVerification(capaDetail.non_conformance_id, capaId, {
        verification_date: new Date(`${verifyForm.verification_date}T00:00:00`).toISOString(),
        verification_result: verifyForm.verification_result,
        effectiveness_score: verifyForm.effectiveness_score ? Number(verifyForm.effectiveness_score) : undefined,
        comments: verifyForm.comments || undefined,
        follow_up_required: false,
      });
      const items = await ncAPI.getCAPAVerifications(capaDetail.non_conformance_id);
      const filtered = (items || []).filter((v: any) => v.capa_action_id === capaId);
      setVerifications(filtered);
      setVerifyForm({ verification_date: '', verification_result: 'passed', effectiveness_score: '', comments: '' });
      setErrorMsg(undefined);
    } catch (e: any) {
      setErrorMsg(e?.message || 'Failed to add verification');
    }
  };

  if (!capaDetail) return null;

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight="bold" gutterBottom>CAPA {capaDetail.capa_number}</Typography>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6">{capaDetail.title}</Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>{capaDetail.description}</Typography>
        <Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: 'wrap' }}>
          <Chip label={`Status: ${String(capaDetail.status).split('_').join(' ')}`} />
          <Chip label={`Progress: ${capaDetail.progress_percentage}%`} />
          <Chip label={`Target: ${capaDetail.target_completion_date}`} />
        </Stack>
        <Divider sx={{ my: 2 }} />
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField select label="Status" value={editForm.status} onChange={e => setEditForm({ ...editForm, status: e.target.value })} sx={{ minWidth: 220 }}>
            {['pending','assigned','in_progress','completed','verified','closed','overdue'].map(s => (
              <MenuItem key={s} value={s}>{s.split('_').join(' ')}</MenuItem>
            ))}
          </TextField>
          <TextField type="number" label="Progress %" value={editForm.progress_percentage} onChange={e => setEditForm({ ...editForm, progress_percentage: e.target.value })} />
          <FormControlLabel control={<Switch checked={editForm.effectiveness_measured} onChange={(_e, c) => setEditForm({ ...editForm, effectiveness_measured: c })} />} label="Effectiveness Measured" />
          <TextField type="number" label="Effectiveness Score" value={editForm.effectiveness_score} onChange={e => setEditForm({ ...editForm, effectiveness_score: e.target.value })} />
          <Button variant="outlined" onClick={async () => {
            try {
              const payload: any = {
                status: editForm.status || undefined,
                progress_percentage: editForm.progress_percentage === '' ? undefined : Number(editForm.progress_percentage),
                effectiveness_measured: editForm.effectiveness_measured,
                effectiveness_score: editForm.effectiveness_score === '' ? undefined : Number(editForm.effectiveness_score),
              };
              const updated = await ncAPI.updateCAPA(capaId, payload);
              // refresh page data
              dispatch(fetchCAPA(capaId));
              setErrorMsg(undefined);
            } catch (e: any) {
              setErrorMsg(e?.message || 'Failed to update CAPA');
            }
          }}>Save</Button>
        </Stack>
      </Paper>

      <Paper sx={{ p: 2, mb: 2 }}>
        {errorMsg && <Typography color="error" variant="body2" sx={{ mb: 1 }}>{errorMsg}</Typography>}
        <Typography variant="subtitle1" gutterBottom>Verifications</Typography>
        {verifications.length === 0 ? (
          <Typography variant="body2" color="text.secondary">No verifications yet.</Typography>
        ) : (
          verifications.map((v) => (
            <Box key={v.id} sx={{ mb: 1 }}>
              <Typography variant="body2">{v.verification_date} - {v.verification_result} - Score: {v.effectiveness_score ?? 'N/A'}</Typography>
              {v.comments && <Typography variant="caption">{v.comments}</Typography>}
            </Box>
          ))
        )}
        <Divider sx={{ my: 2 }} />
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField type="date" label="Verification Date" InputLabelProps={{ shrink: true }} value={verifyForm.verification_date} onChange={e => setVerifyForm({ ...verifyForm, verification_date: e.target.value })} />
          <TextField label="Result (passed/failed/conditional)" value={verifyForm.verification_result} onChange={e => setVerifyForm({ ...verifyForm, verification_result: e.target.value })} />
          <TextField type="number" label="Effectiveness Score" value={verifyForm.effectiveness_score} onChange={e => setVerifyForm({ ...verifyForm, effectiveness_score: e.target.value })} />
          <TextField fullWidth label="Comments" value={verifyForm.comments} onChange={e => setVerifyForm({ ...verifyForm, comments: e.target.value })} />
          <Button variant="contained" onClick={submitVerification}>Add Verification</Button>
        </Stack>
      </Paper>
    </Box>
  );
};

export default CAPADetail;

