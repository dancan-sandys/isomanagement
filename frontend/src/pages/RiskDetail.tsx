import React, { useEffect, useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import { Box, Button, Card, CardContent, Chip, Divider, Grid, Stack, Typography } from '@mui/material';
import riskAPI from '../services/riskAPI';
import RiskActionList from '../components/Risk/RiskActionList';

const RiskDetail: React.FC = () => {
  const { id } = useParams();
  const [risk, setRisk] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    if (!id) return;
    setLoading(true); setError(null);
    try {
      const resp = await riskAPI.get(Number(id));
      const data = resp.data || resp;
      setRisk(data);
    } catch (e: any) {
      setError(e?.message || 'Failed to load risk');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  if (loading) return <Box sx={{ p: 3 }}>Loading…</Box>;
  if (error) return <Box sx={{ p: 3 }}><Typography color="error">{error}</Typography></Box>;
  if (!risk) return null;

  return (
    <Box sx={{ p: 2 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h4">{risk.title}</Typography>
        <Stack direction="row" spacing={1}>
          <Button component={RouterLink} to="/compliance/risk" variant="outlined">Back to Register</Button>
        </Stack>
      </Stack>

      <Grid container spacing={2}>
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="h6">Overview</Typography>
                <Chip label={risk.item_type?.toUpperCase()} color={risk.item_type === 'risk' ? 'error' : 'success'} size="small" />
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>{risk.risk_number}</Typography>
              <Divider sx={{ my: 2 }} />
              <Stack direction="row" spacing={1} flexWrap="wrap">
                <Chip label={`Category: ${risk.category}`} size="small" />
                {risk.classification && <Chip label={`Class: ${risk.classification}`} size="small" />}
                <Chip label={`Status: ${risk.status}`} size="small" />
                <Chip label={`Severity: ${risk.severity}`} size="small" />
                <Chip label={`Likelihood: ${risk.likelihood}`} size="small" />
                {risk.detectability && <Chip label={`Detectability: ${risk.detectability}`} size="small" />}
                <Chip label={`Score: ${risk.risk_score}`} size="small" />
              </Stack>
              {risk.description && <Typography variant="body2" sx={{ mt: 2 }}>{risk.description}</Typography>}
              {risk.mitigation_plan && (
                <>
                  <Typography variant="subtitle2" sx={{ mt: 2 }}>Mitigation Plan</Typography>
                  <Typography variant="body2">{risk.mitigation_plan}</Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={5}>
          <RiskActionList itemId={Number(id)} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default RiskDetail;


