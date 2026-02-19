import React, { useEffect, useState } from 'react';
import { Box, Button, Card, CardContent, Chip, Grid, IconButton, Stack, TextField, Typography } from '@mui/material';
import { CheckCircle, Delete, Save } from '@mui/icons-material';
import riskAPI from '../../services/riskAPI';
import actionsLogAPI from '../../services/actionsLogAPI';

interface Props {
  itemId: number;
}

const RiskActionList: React.FC<Props> = ({ itemId }) => {
  const [actions, setActions] = useState<any[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const load = async () => {
    // Prefer pulling from central actions log filtered by risk_id
    try {
      const list = await actionsLogAPI.getActions({ risk_id: itemId });
      // Map minimal fields expected by this UI
      const mapped = list.map((a: any) => ({
        id: a.id,
        title: a.title,
        description: a.description,
        completed: a.status === 'completed',
        due_date: a.due_date,
      }));
      setActions(mapped);
    } catch (e) {
      const resp = await riskAPI.listActions(itemId);
      setActions(resp.data || resp);
    }
  };
  useEffect(() => { load(); }, [itemId]);

  const add = async () => {
    if (!title) return;
    // Create directly in the central actions log, with risk_id linkage
    await actionsLogAPI.createAction({
      title,
      description: description || '',
      action_source: 'risk_assessment' as any,
      source_id: itemId,
      risk_id: itemId,
      priority: 'medium' as any,
      assigned_by: 1,
    } as any);
    setTitle(''); setDescription('');
    await load();
  };

  const complete = async (id: number) => {
    await actionsLogAPI.updateAction(id, { status: 'completed' as any, progress_percent: 100 });
    await load();
  };

  const remove = async (id: number) => {
    await actionsLogAPI.deleteAction(id);
    await load();
  };

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="subtitle1" sx={{ mb: 1 }}>Mitigation Actions</Typography>
        <Grid container spacing={1} sx={{ mb: 2 }}>
          <Grid item xs={12} md={5}>
            <TextField fullWidth size="small" label="Action title" value={title} onChange={(e) => setTitle(e.target.value)} />
          </Grid>
          <Grid item xs={12} md={5}>
            <TextField fullWidth size="small" label="Description (optional)" value={description} onChange={(e) => setDescription(e.target.value)} />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button variant="contained" onClick={add} disabled={!title}>Add</Button>
          </Grid>
        </Grid>

        <Stack spacing={1}>
          {actions.map(a => (
            <Card key={a.id} variant="outlined">
              <CardContent>
                <Stack direction="row" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="subtitle2">{a.title}</Typography>
                    {a.description && <Typography variant="caption" color="text.secondary">{a.description}</Typography>}
                    <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
                      <Chip label={a.completed ? 'Completed' : 'Open'} size="small" color={a.completed ? 'success' as any : 'default'} />
                      {a.due_date && <Chip label={`Due: ${new Date(a.due_date).toLocaleDateString()}`} size="small" />}
                    </Stack>
                  </Box>
                  <Stack direction="row" spacing={1}>
                    {!a.completed && (
                      <IconButton color="success" onClick={() => complete(a.id)}><CheckCircle /></IconButton>
                    )}
                    <IconButton color="error" onClick={() => remove(a.id)}><Delete /></IconButton>
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          ))}
          {actions.length === 0 && <Typography variant="body2" color="text.secondary">No actions yet</Typography>}
        </Stack>
      </CardContent>
    </Card>
  );
};

export default RiskActionList;


