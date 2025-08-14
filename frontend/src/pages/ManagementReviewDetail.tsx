import React, { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Button, Card, CardContent, Divider, Grid, Stack, TextField, Typography } from '@mui/material';
import managementReviewAPI from '../services/managementReviewAPI';

const ManagementReviewDetail: React.FC = () => {
  const { id } = useParams();
  const [review, setReview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionTitle, setActionTitle] = useState('');

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true); setError(null);
    try {
      const resp = await managementReviewAPI.get(Number(id));
      const data = resp.data || resp;
      setReview(data);
    } catch (e: any) { setError(e?.message || 'Failed to load'); }
    finally { setLoading(false); }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  if (loading) return <Box sx={{ p: 3 }}>Loading…</Box>;
  if (error) return <Box sx={{ p: 3 }}><Typography color="error">{error}</Typography></Box>;
  if (!review) return null;

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" sx={{ mb: 2 }}>{review.title}</Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1">Overview</Typography>
              <Divider sx={{ my: 1 }} />
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}><Typography><b>Status:</b> {review.status}</Typography></Grid>
                <Grid item xs={12} md={6}><Typography><b>Review Date:</b> {review.review_date || '-'}</Typography></Grid>
                <Grid item xs={12}><Typography><b>Attendees:</b> {review.attendees || '-'}</Typography></Grid>
                <Grid item xs={12}><Typography><b>Inputs:</b> {review.inputs || '-'}</Typography></Grid>
                <Grid item xs={12}><Typography><b>Outputs:</b> {review.outputs || '-'}</Typography></Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1">Actions</Typography>
              <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                <TextField size="small" fullWidth placeholder="New action title" value={actionTitle} onChange={(e) => setActionTitle(e.target.value)} />
                <Button variant="contained" onClick={async () => {
                  if (!actionTitle) return;
                  await managementReviewAPI.addAction(Number(id), { title: actionTitle });
                  setActionTitle('');
                  load();
                }}>Add</Button>
              </Stack>
              <Stack spacing={1} sx={{ mt: 2 }}>
                {(review.actions || []).map((a: any) => (
                  <Stack key={a.id} direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">{a.title}</Typography>
                    {!a.completed && <Button size="small" onClick={async () => { await managementReviewAPI.completeAction(a.id); load(); }}>Complete</Button>}
                  </Stack>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ManagementReviewDetail;


