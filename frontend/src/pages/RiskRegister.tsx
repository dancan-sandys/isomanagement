import React, { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Button, Card, CardContent, Chip, Grid, LinearProgress, MenuItem, Select, Stack, TextField, Typography } from '@mui/material';
import { Add, Assessment } from '@mui/icons-material';
import { AppDispatch, RootState } from '../store';
import { clearError, fetchRiskItems, fetchRiskStats, setFilters } from '../store/slices/riskSlice';
import riskAPI from '../services/riskAPI';
import RiskCreateDialog from '../components/Risk/RiskCreateDialog';
import { Link as RouterLink } from 'react-router-dom';

const RiskRegister: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { items, stats, loading, error, filters } = useSelector((s: RootState) => s.risk);
  const [search, setSearch] = useState(filters.search || '');
  const [type, setType] = useState<'risk' | 'opportunity' | ''>(filters.item_type ?? '');
  const [category, setCategory] = useState(filters.category || '');
  const [classification, setClassification] = useState<
    'food_safety' | 'business' | 'customer' | ''
  >(filters.classification || '');
  const [status, setStatus] = useState(filters.status || '');
  const [severity, setSeverity] = useState(filters.severity || '');
  const [likelihood, setLikelihood] = useState(filters.likelihood || '');
  const [detectability, setDetectability] = useState<
    'easily_detectable' | 'moderately_detectable' | 'difficult' | 'very_difficult' | 'almost_undetectable' | ''
  >(filters.detectability || '');

  useEffect(() => {
    dispatch(fetchRiskItems({ ...filters }));
    dispatch(fetchRiskStats());
  }, []);

  const onApply = () => {
    const itemTypeValue = type ? (type as 'risk' | 'opportunity') : undefined;
    const classificationValue = classification ? (classification as 'food_safety' | 'business' | 'customer') : undefined;
    const detectabilityValue = detectability ? (detectability as 'easily_detectable' | 'moderately_detectable' | 'difficult' | 'very_difficult' | 'almost_undetectable') : undefined;
    dispatch(setFilters({
      search,
      item_type: itemTypeValue,
      category: category || undefined,
      classification: classificationValue,
      status: status || undefined,
      severity: severity || undefined,
      likelihood: likelihood || undefined,
      detectability: detectabilityValue,
    }));
    dispatch(fetchRiskItems({
      ...filters,
      search,
      item_type: itemTypeValue,
      category: category || undefined,
      classification: classificationValue,
      status: status || undefined,
      severity: severity || undefined,
      likelihood: likelihood || undefined,
      detectability: detectabilityValue,
    }));
    dispatch(fetchRiskStats());
  };

  const [openCreate, setOpenCreate] = useState(false);
  const onCreated = () => {
    dispatch(fetchRiskItems(filters));
    dispatch(fetchRiskStats());
  };

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h4">Risk & Opportunity Register</Typography>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<Assessment />} onClick={() => dispatch(fetchRiskStats())}>Refresh Stats</Button>
          <Button variant="contained" startIcon={<Add />} onClick={() => setOpenCreate(true)}>New</Button>
        </Stack>
      </Stack>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField fullWidth size="small" label="Search" value={search} onChange={(e) => setSearch(e.target.value)} />
            </Grid>
            <Grid item xs={12} md={2}>
              <Select fullWidth size="small" displayEmpty value={type} onChange={(e) => setType(e.target.value as 'risk' | 'opportunity' | '')}>
                <MenuItem value="">All Types</MenuItem>
                <MenuItem value="risk">Risk</MenuItem>
                <MenuItem value="opportunity">Opportunity</MenuItem>
              </Select>
            </Grid>
            <Grid item xs={12} md={3}>
              <Select fullWidth size="small" displayEmpty value={category} onChange={(e) => setCategory(e.target.value as string)}>
                <MenuItem value="">All Categories</MenuItem>
                <MenuItem value="process">Process</MenuItem>
                <MenuItem value="supplier">Supplier</MenuItem>
                <MenuItem value="staff">Staff</MenuItem>
                <MenuItem value="environment">Environment</MenuItem>
                <MenuItem value="haccp">HACCP</MenuItem>
                <MenuItem value="prp">PRP</MenuItem>
                <MenuItem value="document">Document</MenuItem>
                <MenuItem value="training">Training</MenuItem>
                <MenuItem value="equipment">Equipment</MenuItem>
                <MenuItem value="compliance">Compliance</MenuItem>
                <MenuItem value="customer">Customer</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </Grid>
            <Grid item xs={12} md={3}>
              <Select fullWidth size="small" displayEmpty value={classification} onChange={(e) => setClassification(e.target.value as 'food_safety' | 'business' | 'customer' | '')}>
                <MenuItem value="">All Classifications</MenuItem>
                <MenuItem value="food_safety">Food Safety</MenuItem>
                <MenuItem value="business">Business</MenuItem>
                <MenuItem value="customer">Customer</MenuItem>
              </Select>
            </Grid>
            <Grid item xs={12} md={2}>
              <Select fullWidth size="small" displayEmpty value={status} onChange={(e) => setStatus(e.target.value as string)}>
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="open">Open</MenuItem>
                <MenuItem value="monitoring">Monitoring</MenuItem>
                <MenuItem value="mitigated">Mitigated</MenuItem>
                <MenuItem value="closed">Closed</MenuItem>
              </Select>
            </Grid>
            <Grid item xs={12} md={2}>
              <Select fullWidth size="small" displayEmpty value={severity} onChange={(e) => setSeverity(e.target.value as string)}>
                <MenuItem value="">Any Severity</MenuItem>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </Grid>
            <Grid item xs={12} md={2}>
              <Select fullWidth size="small" displayEmpty value={likelihood} onChange={(e) => setLikelihood(e.target.value as string)}>
                <MenuItem value="">Any Likelihood</MenuItem>
                <MenuItem value="rare">Rare</MenuItem>
                <MenuItem value="unlikely">Unlikely</MenuItem>
                <MenuItem value="possible">Possible</MenuItem>
                <MenuItem value="likely">Likely</MenuItem>
                <MenuItem value="almost_certain">Almost Certain</MenuItem>
              </Select>
            </Grid>
            <Grid item xs={12} md={3}>
              <Select fullWidth size="small" displayEmpty value={detectability} onChange={(e) => setDetectability(e.target.value as 'easily_detectable' | 'moderately_detectable' | 'difficult' | 'very_difficult' | 'almost_undetectable' | '')}>
                <MenuItem value="">Any Detectability</MenuItem>
                <MenuItem value="easily_detectable">Easily detectable</MenuItem>
                <MenuItem value="moderately_detectable">Moderately detectable</MenuItem>
                <MenuItem value="difficult">Difficult</MenuItem>
                <MenuItem value="very_difficult">Very difficult</MenuItem>
                <MenuItem value="almost_undetectable">Almost undetectable</MenuItem>
              </Select>
            </Grid>
            <Grid item xs={12} md={1}>
              <Button variant="contained" onClick={onApply}>Apply</Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}

      {/* Stats */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} md={3}>
            <Card><CardContent><Typography variant="h6">Total</Typography><Typography variant="h4">{stats.total}</Typography></CardContent></Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card><CardContent><Typography variant="subtitle2">By Type</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {Object.entries(stats.by_item_type || {}).map(([k,v]) => (<Chip key={k} label={`${k}: ${v}`} />))}
              </Stack>
            </CardContent></Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card><CardContent><Typography variant="subtitle2">By Status</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {Object.entries(stats.by_status || {}).map(([k,v]) => (<Chip key={k} label={`${k}: ${v}`} />))}
              </Stack>
            </CardContent></Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card><CardContent><Typography variant="subtitle2">By Severity</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {Object.entries(stats.by_severity || {}).map(([k,v]) => (<Chip key={k} label={`${k}: ${v}`} />))}
              </Stack>
            </CardContent></Card>
          </Grid>
        </Grid>
      )}

      {/* List */}
      <Card>
        <CardContent>
          <Grid container spacing={2}>
            {items.map((it) => (
              <Grid item xs={12} md={6} key={it.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="h6">{it.title}</Typography>
                      <Chip label={it.item_type.toUpperCase()} color={it.item_type === 'risk' ? 'error' : 'success'} size="small" />
                    </Stack>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>{it.risk_number}</Typography>
                    <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                      <Chip label={`Severity: ${it.severity}`} size="small" />
                      <Chip label={`Likelihood: ${it.likelihood}`} size="small" />
                      <Chip label={`Score: ${it.risk_score}`} size="small" />
                      <Chip label={it.status} size="small" />
                    </Stack>
                    {it.description && (<Typography variant="body2" sx={{ mt: 1 }}>{it.description}</Typography>)}
                    <Box sx={{ mt: 2 }}>
                      <Button component={RouterLink} to={`/compliance/risk/${it.id}`} size="small" variant="outlined">View Details</Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
            {items.length === 0 && (
              <Grid item xs={12}><Typography variant="body2" color="text.secondary">No items</Typography></Grid>
            )}
          </Grid>
        </CardContent>
      </Card>

      <RiskCreateDialog open={openCreate} onClose={() => setOpenCreate(false)} onCreated={onCreated} />
    </Box>
  );
};

export default RiskRegister;


