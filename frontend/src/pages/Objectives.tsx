import React, { useEffect, useState } from 'react';
import { Box, Card, CardContent, Typography, Grid, Chip, Stack, Button } from '@mui/material';
import objectivesAPI, { Objective } from '../services/objectivesAPI';

const StatusChip: React.FC<{ status?: string }> = ({ status }) => {
  const color = status === 'on_track' ? 'success' : status === 'at_risk' ? 'warning' : status === 'off_track' ? 'error' : 'default';
  return <Chip label={status || 'unknown'} color={color as any} size="small" />;
};

const ObjectivesPage: React.FC = () => {
  const [objectives, setObjectives] = useState<Objective[]>([]);
  const [kpis, setKpis] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        const [objs, k] = await Promise.all([
          objectivesAPI.listObjectives(),
          objectivesAPI.getKPIs(),
        ]);
        if (mounted) {
          setObjectives(objs);
          setKpis(k);
        }
      } catch (e) {
      } finally {
        setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const kpiByObjective: Record<number, any> = {};
  for (const k of kpis) {
    if (k.objective_id && !kpiByObjective[k.objective_id]) kpiByObjective[k.objective_id] = k;
  }

  return (
    <Box p={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Food Safety Objectives</Typography>
        <Button variant="contained" disabled>New Objective</Button>
      </Stack>

      <Grid container spacing={2}>
        {objectives.map((o) => {
          const k = kpiByObjective[o.id];
          return (
            <Grid item xs={12} md={6} lg={4} key={o.id}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">{o.objective_code}</Typography>
                  <Typography variant="h6" gutterBottom>{o.title}</Typography>
                  <Typography variant="body2" color="text.secondary">{o.description}</Typography>
                  <Box mt={2}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography variant="body2">Attainment:</Typography>
                      <Typography variant="body1" fontWeight={600}>{k?.attainment_percent ? `${k.attainment_percent.toFixed(1)}%` : '—'}</Typography>
                      <StatusChip status={k?.status} />
                    </Stack>
                    <Typography variant="caption" color="text.secondary">Period: {k?.period_start?.slice(0,10)} → {k?.period_end?.slice(0,10)}</Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
      {(!loading && objectives.length === 0) && (
        <Typography variant="body2" color="text.secondary" mt={2}>No objectives found.</Typography>
      )}
    </Box>
  );
};

export default ObjectivesPage;

