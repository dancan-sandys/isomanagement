import React, { useEffect, useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import { Box, Button, Card, CardContent, Chip, Divider, Grid, Stack, TextField, Typography } from '@mui/material';
import riskAPI from '../services/riskAPI';

const OpportunityDetail: React.FC = () => {
  const { id } = useParams();
  const [item, setItem] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    if (!id) return;
    setLoading(true); setError(null);
    try {
      const resp = await riskAPI.get(Number(id));
      const data = resp.data || resp;
      setItem(data);
    } catch (e: any) {
      setError(e?.message || 'Failed to load opportunity');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

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
                <Grid item xs={12} md={4}><Typography><b>Benefit:</b> {item.opportunity_benefit ?? '-'}</Typography></Grid>
                <Grid item xs={12} md={4}><Typography><b>Feasibility:</b> {item.opportunity_feasibility ?? '-'}</Typography></Grid>
                <Grid item xs={12} md={4}><Typography><b>Score:</b> {item.opportunity_score ?? '-'}</Typography></Grid>
                <Grid item xs={12}><Typography><b>Description:</b> {item.description || '-'}</Typography></Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" sx={{ mb: 1 }}>Opportunity Evaluation</Typography>
              <Stack spacing={1}>
                <TextField size="small" type="number" label="Benefit (1-5)" value={item.opportunity_benefit ?? ''}
                  onChange={async (e) => {
                    const v = Number(e.target.value) || undefined;
                    await riskAPI.update(item.id, { opportunity_benefit: v });
                    load();
                  }} />
                <TextField size="small" type="number" label="Feasibility (1-5)" value={item.opportunity_feasibility ?? ''}
                  onChange={async (e) => {
                    const v = Number(e.target.value) || undefined;
                    await riskAPI.update(item.id, { opportunity_feasibility: v });
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


