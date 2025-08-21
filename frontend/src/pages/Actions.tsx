import React, { useEffect, useState } from 'react';
import { Box, Card, CardContent, Typography, Stack, Chip, Grid, Select, MenuItem } from '@mui/material';
import actionsAPI, { ActionStatus, ActionPriority, ActionSource } from '../services/actionsAPI';

const StatusChip: React.FC<{ status?: ActionStatus }> = ({ status }) => {
  const color = status === 'completed' || status === 'verified' ? 'success' : status === 'in_progress' ? 'warning' : status === 'cancelled' ? 'default' : 'error';
  return <Chip size="small" label={status || 'open'} color={color as any} />;
};

const ActionsPage: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<ActionStatus | ''>('');
  const [source, setSource] = useState<ActionSource | ''>('');

  const load = async () => {
    setLoading(true);
    try {
      const data = await actionsAPI.list({ status: status || undefined, source: source || undefined });
      setItems(data || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, source]);

  return (
    <Box p={2}>
      <Stack direction="row" spacing={2} mb={2} alignItems="center">
        <Typography variant="h6">Actions Log</Typography>
        <Select size="small" value={status} onChange={(e) => setStatus((e.target.value as ActionStatus) || '')} displayEmpty>
          <MenuItem value="">All Status</MenuItem>
          <MenuItem value="open">Open</MenuItem>
          <MenuItem value="in_progress">In Progress</MenuItem>
          <MenuItem value="completed">Completed</MenuItem>
          <MenuItem value="verified">Verified</MenuItem>
          <MenuItem value="cancelled">Cancelled</MenuItem>
        </Select>
        <Select size="small" value={source} onChange={(e) => setSource((e.target.value as ActionSource) || '')} displayEmpty>
          <MenuItem value="">All Sources</MenuItem>
          <MenuItem value="interested_party">Interested Parties</MenuItem>
          <MenuItem value="swot">SWOT</MenuItem>
          <MenuItem value="pestel">PESTEL</MenuItem>
          <MenuItem value="risk_opportunity">Risks & Opportunities</MenuItem>
          <MenuItem value="management_review">Management Review</MenuItem>
          <MenuItem value="capa">CAPA</MenuItem>
        </Select>
      </Stack>

      <Grid container spacing={1}>
        {items.map((it) => (
          <Grid item xs={12} md={6} lg={4} key={it.id}>
            <Card>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography fontWeight={600}>{it.title}</Typography>
                  <StatusChip status={(it.status || '').toLowerCase() as ActionStatus} />
                </Stack>
                <Typography variant="body2" color="text.secondary" mt={1}>{it.description}</Typography>
                <Stack direction="row" spacing={1} mt={1}>
                  <Chip size="small" label={`Source: ${String(it.source).toLowerCase()}`} />
                  {it.owner_id ? <Chip size="small" label={`Owner: ${it.owner_id}`} /> : null}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
        {!loading && items.length === 0 && (
          <Grid item xs={12}><Typography>No actions found.</Typography></Grid>
        )}
      </Grid>
    </Box>
  );
};

export default ActionsPage;

