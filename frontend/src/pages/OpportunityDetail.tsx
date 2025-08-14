import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import { Box, Button, Card, CardContent, Chip, Divider, Grid, MenuItem, Select, Stack, TextField, Typography } from '@mui/material';
import riskAPI from '../services/riskAPI';
import { usersAPI } from '../services/api';

const OpportunityDetail: React.FC = () => {
  const { id } = useParams();
  const [item, setItem] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [users, setUsers] = useState<any[]>([]);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true); setError(null);
    try {
      const resp = await riskAPI.get(Number(id));
      const data = resp.data || resp;
      setItem(data);
      try {
        const u = await usersAPI.getUsers({ page: 1, size: 50 });
        const list = u?.items || u?.data?.items || [];
        setUsers(list);
      } catch {}
    } catch (e: any) {
      setError(e?.message || 'Failed to load opportunity');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  if (loading) return <Typography>Loading...</Typography>;
  if (error) return <Typography color="error">{error}</Typography>;
  if (!item) return null;

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h5">Opportunity Details</Typography>
        <Button component={RouterLink} to="/compliance/opportunities" variant="outlined">Back to register</Button>
      </Stack>
      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <Card variant="outlined">
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="h6">{item.title}</Typography>
                <Chip label="OPPORTUNITY" color="success" size="small" />
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>{item.risk_number}</Typography>
              <Divider sx={{ my: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}><Typography><b>Category:</b> {item.category}</Typography></Grid>
                <Grid item xs={12} md={6}><Typography><b>Classification:</b> {item.classification || '-'}</Typography></Grid>
                <Grid item xs={12} md={4}><Typography><b>Feasibility:</b> {item.opportunity_feasibility ?? '-'}</Typography></Grid>
                <Grid item xs={12} md={4}><Typography><b>Score:</b> {item.opportunity_score ?? '-'}</Typography></Grid>
                <Grid item xs={12}><Typography><b>Description:</b> {item.description || '-'}</Typography></Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" sx={{ mb: 1 }}>Tracking</Typography>
              <Stack spacing={1}>
                <Select size="small" value={item.status || 'open'} onChange={async (e) => {
                  const v = e.target.value as string;
                  await riskAPI.update(item.id, { status: v });
                  load();
                }}>
                  <MenuItem value="open">Open</MenuItem>
                  <MenuItem value="monitoring">Monitoring</MenuItem>
                  <MenuItem value="mitigated">Mitigated</MenuItem>
                  <MenuItem value="closed">Closed</MenuItem>
                </Select>
                <Select
                  size="small"
                  displayEmpty
                  value={item.assigned_to || ''}
                  onChange={async (e) => {
                    const v = e.target.value as number | '';
                    await riskAPI.update(item.id, { assigned_to: v === '' ? undefined : Number(v) });
                    load();
                  }}
                >
                  <MenuItem value="">Unassigned</MenuItem>
                  {users.map((u: any) => (
                    <MenuItem key={u.id} value={u.id}>{u.full_name || u.username}</MenuItem>
                  ))}
                </Select>
                <TextField
                  size="small"
                  type="date"
                  label="Due Date"
                  InputLabelProps={{ shrink: true }}
                  value={item.due_date ? (new Date(item.due_date).toISOString().slice(0,10)) : ''}
                  onChange={async (e) => {
                    const v = e.target.value;
                    const iso = v ? new Date(v + 'T00:00:00Z').toISOString() : undefined;
                    await riskAPI.update(item.id, { due_date: iso });
                    load();
                  }}
                />
              </Stack>
            </CardContent>
          </Card>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" sx={{ mb: 1 }}>Opportunity Evaluation</Typography>
              <Stack spacing={1}>
                <TextField size="small" type="number" label="Feasibility (1-5)" value={item.opportunity_feasibility ?? ''}
                  onChange={async (e) => {
                    const v = Number(e.target.value) || undefined;
                    await riskAPI.update(item.id, { opportunity_feasibility: v });
                    load();
                  }} />
                <TextField size="small" type="number" label="Score" value={item.opportunity_score ?? ''}
                  onChange={async (e) => {
                    const v = Number(e.target.value) || undefined;
                    await riskAPI.update(item.id, { opportunity_score: v });
                    load();
                  }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default OpportunityDetail;


