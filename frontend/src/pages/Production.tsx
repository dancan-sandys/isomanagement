import React, { useEffect, useState } from 'react';
import { Box, Grid, Card, CardContent, Typography, Stack, Button } from '@mui/material';
import productionAPI from '../services/productionAPI';

const ProductionPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    let mounted = true;
    (async () => {
      setLoading(true);
      try {
        const a = await productionAPI.analytics();
        if (mounted) setAnalytics(a);
      } catch (e) {
      } finally {
        setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  return (
    <Box p={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Production Sheet</Typography>
        <Button variant="contained" disabled>Create Process</Button>
      </Stack>
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Records</Typography>
              <Typography variant="h4">{analytics?.total_records ?? '—'}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Average Overrun</Typography>
              <Typography variant="h4">{analytics?.avg_overrun_percent != null ? `${analytics.avg_overrun_percent}%` : '—'}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Overruns / Underruns</Typography>
              <Typography variant="h4">{analytics ? `${analytics.overruns} / ${analytics.underruns}` : '—'}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProductionPage;

