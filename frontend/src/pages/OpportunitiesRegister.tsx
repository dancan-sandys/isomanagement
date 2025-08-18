import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Button, Card, CardContent, Chip, Grid, LinearProgress, MenuItem, Select, Stack, TextField, Typography } from '@mui/material';
import { SelectChangeEvent } from '@mui/material/Select';
import { Add } from '@mui/icons-material';
import { AppDispatch, RootState } from '../store';
import { fetchRiskItems, setFilters } from '../store/slices/riskSlice';
import riskAPI, { RiskListParams } from '../services/riskAPI';
import OpportunityCreateDialog from '../components/Risk/OpportunityCreateDialog';
import { Link as RouterLink } from 'react-router-dom';

const OpportunitiesRegister: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { items, loading, error, filters } = useSelector((s: RootState) => s.risk);
  const [search, setSearch] = useState(filters.search || '');
  const [category, setCategory] = useState(filters.category || '');
  const [classification, setClassification] = useState<RiskListParams['classification'] | ''>(filters.classification || '');

  useEffect(() => {
    dispatch(setFilters({ item_type: 'opportunity' }));
    dispatch(fetchRiskItems({ item_type: 'opportunity' }));
  }, [dispatch]);

  const onApply = () => {
    dispatch(setFilters({ search, item_type: 'opportunity', category: category || undefined, classification: classification || undefined }));
    dispatch(fetchRiskItems({ ...filters, search, item_type: 'opportunity', category: category || undefined, classification: classification || undefined }));
  };

  const [open, setOpen] = useState(false);
  const onCreate = async () => setOpen(true);
  const onCreated = () => {
    dispatch(fetchRiskItems({ ...filters, item_type: 'opportunity' }));
  };

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h5">Opportunities Register</Typography>
        <Stack direction="row" spacing={1}>
          <TextField size="small" placeholder="Search" value={search} onChange={(e) => setSearch(e.target.value)} />
          <Select size="small" displayEmpty value={category} onChange={(e) => setCategory(e.target.value as string)}>
            <MenuItem value="">All Categories</MenuItem>
            <MenuItem value="process">Process</MenuItem>
            <MenuItem value="supplier">Supplier</MenuItem>
            <MenuItem value="staff">Staff</MenuItem>
            <MenuItem value="environment">Environment</MenuItem>
            <MenuItem value="customer">Customer</MenuItem>
            <MenuItem value="other">Other</MenuItem>
          </Select>
          <Select size="small" displayEmpty value={classification} onChange={(e: SelectChangeEvent) => setClassification(e.target.value as RiskListParams['classification'] | '')}>
            <MenuItem value="">All Classifications</MenuItem>
            <MenuItem value="food_safety">Food Safety</MenuItem>
            <MenuItem value="business">Business</MenuItem>
            <MenuItem value="customer">Customer</MenuItem>
          </Select>
          <Button variant="outlined" onClick={onApply}>Apply</Button>
          <Button variant="contained" startIcon={<Add />} onClick={onCreate}>New</Button>
        </Stack>
      </Stack>
      {loading && <LinearProgress />}
      {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}
      <OpportunityCreateDialog open={open} onClose={() => setOpen(false)} onCreated={onCreated} />
      <Grid container spacing={2}>
        {items.filter(i => i.item_type === 'opportunity').map((it) => (
          <Grid item xs={12} md={6} lg={4} key={it.id}>
            <Card variant="outlined">
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6">{it.title}</Typography>
                  <Chip label="OPPORTUNITY" color="success" size="small" />
                </Stack>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>{it.risk_number}</Typography>
                <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                  <Chip label={`Category: ${it.category}`} size="small" />
                  {it.classification && <Chip label={`Class: ${it.classification}`} size="small" />}
                </Stack>
                <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                  {typeof it.opportunity_benefit !== 'undefined' && <Chip label={`Benefit: ${it.opportunity_benefit}`} size="small" color="primary" />}
                  {typeof it.opportunity_feasibility !== 'undefined' && <Chip label={`Feasibility: ${it.opportunity_feasibility}`} size="small" color="info" />}
                  {typeof it.opportunity_score !== 'undefined' && <Chip label={`Score: ${it.opportunity_score}`} size="small" color="success" />}
                </Stack>
                <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                  <Button component={RouterLink} to={`/compliance/opportunity/${it.id}`} size="small">View Details</Button>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default OpportunitiesRegister;


