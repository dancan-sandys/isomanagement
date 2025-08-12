import React, { useEffect, useState } from 'react';
import { Box, Button, Card, CardContent, Dialog, DialogActions, DialogContent, DialogTitle, Grid, LinearProgress, Stack, TextField, Typography } from '@mui/material';
import managementReviewAPI, { MRPayload } from '../services/managementReviewAPI';
import { Link as RouterLink } from 'react-router-dom';

const ManagementReviews: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<MRPayload>({ title: '', status: 'planned' });

  const load = async () => {
    setLoading(true); setError(null);
    try {
      const resp = await managementReviewAPI.list();
      const data = resp.data || resp;
      setItems(data.items || []);
    } catch (e: any) {
      setError(e?.message || 'Failed to load management reviews');
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const create = async () => {
    await managementReviewAPI.create(form);
    setOpen(false);
    setForm({ title: '', status: 'planned' });
    load();
  };

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h5">Management Reviews</Typography>
        <Button variant="contained" onClick={() => setOpen(true)}>New Review</Button>
      </Stack>
      {loading && <LinearProgress />}
      {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}
      <Grid container spacing={2}>
        {items.map((it) => (
          <Grid item xs={12} md={6} lg={4} key={it.id}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6">{it.title}</Typography>
                <Typography variant="body2" color="text.secondary">{it.status}</Typography>
                <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                  <Button component={RouterLink} to={`/management-reviews/${it.id}`} size="small">Open</Button>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>New Management Review</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Title" fullWidth value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            <TextField label="Review Date" type="date" fullWidth InputLabelProps={{ shrink: true }}
              value={form.review_date || ''}
              onChange={(e) => setForm({ ...form, review_date: e.target.value })} />
            <TextField label="Attendees" fullWidth value={form.attendees || ''} onChange={(e) => setForm({ ...form, attendees: e.target.value })} />
            <TextField label="Inputs" fullWidth multiline minRows={3} value={form.inputs || ''} onChange={(e) => setForm({ ...form, inputs: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={create} disabled={!form.title}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ManagementReviews;


