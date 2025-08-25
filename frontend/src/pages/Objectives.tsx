import React, { useEffect, useState } from 'react';
import { Box, Card, CardContent, Typography, Grid, Chip, Stack, Button, CircularProgress, Alert } from '@mui/material';
import objectivesService from '../services/objectivesService';
import { Objective } from '../types/objectives';

const StatusChip: React.FC<{ status?: string }> = ({ status }) => {
  const color = status === 'on_track' ? 'success' : status === 'at_risk' ? 'warning' : status === 'off_track' ? 'error' : 'default';
  return <Chip label={status || 'unknown'} color={color as any} size="small" />;
};

const ObjectivesPage: React.FC = () => {
  const [objectives, setObjectives] = useState<Objective[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await objectivesService.getObjectives();
        if (mounted) {
          setObjectives(response.data || []);
        }
      } catch (e) {
        if (mounted) {
          setError('Failed to load objectives. Please try again.');
          console.error('Error loading objectives:', e);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Food Safety Objectives Management</Typography>
        <Button variant="contained" color="primary">
          New Objective
        </Button>
      </Stack>

      <Grid container spacing={2}>
        {objectives.map((objective) => (
          <Grid item xs={12} md={6} lg={4} key={objective.id}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary">
                  {objective.objective_code}
                </Typography>
                <Typography variant="h6" gutterBottom>
                  {objective.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {objective.description}
                </Typography>
                
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                  <Typography variant="body2">Type:</Typography>
                  <Chip 
                    label={objective.objective_type} 
                    size="small" 
                    color={objective.objective_type === 'corporate' ? 'primary' : 'secondary'}
                  />
                </Stack>
                
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                  <Typography variant="body2">Level:</Typography>
                  <Chip 
                    label={objective.hierarchy_level} 
                    size="small" 
                    variant="outlined"
                  />
                </Stack>
                
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                  <Typography variant="body2">Status:</Typography>
                  <StatusChip status={objective.status} />
                </Stack>
                
                {objective.target_value && (
                  <Typography variant="caption" color="text.secondary">
                    Target: {objective.target_value} {objective.measurement_unit}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {(!loading && objectives.length === 0) && (
        <Box textAlign="center" py={4}>
          <Typography variant="body2" color="text.secondary">
            No objectives found. Create your first objective to get started.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ObjectivesPage;

