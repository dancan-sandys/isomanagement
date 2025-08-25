import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Fab,
  Divider,
  LinearProgress,
  Avatar,
  Badge
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Timeline as TimelineIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { analyticsAPI, KPI, KPIValue } from '../../services/analyticsAPI';

interface KPIManagementProps {
  onRefresh?: () => void;
}

const KPIManagement: React.FC<KPIManagementProps> = ({ onRefresh }) => {
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingKPI, setEditingKPI] = useState<KPI | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    display_name: '',
    description: '',
    category: '',
    module: '',
    calculation_method: '',
    unit: '',
    decimal_places: 2,
    target_value: '',
    warning_threshold: '',
    critical_threshold: '',
    alert_enabled: false,
    is_active: true,
    refresh_interval: 60
  });

  useEffect(() => {
    loadKPIs();
  }, []);

  const loadKPIs = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsAPI.getKPIs();
      setKpis(data);
    } catch (err) {
      setError('Failed to load KPIs. Please try again.');
      console.error('Error loading KPIs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKPI = () => {
    setEditingKPI(null);
    setFormData({
      name: '',
      display_name: '',
      description: '',
      category: '',
      module: '',
      calculation_method: '',
      unit: '',
      decimal_places: 2,
      target_value: '',
      warning_threshold: '',
      critical_threshold: '',
      alert_enabled: false,
      is_active: true,
      refresh_interval: 60
    });
    setDialogOpen(true);
  };

  const handleEditKPI = (kpi: KPI) => {
    setEditingKPI(kpi);
    setFormData({
      name: kpi.name,
      display_name: kpi.display_name,
      description: kpi.description || '',
      category: kpi.category,
      module: kpi.module,
      calculation_method: kpi.calculation_method,
      unit: kpi.unit || '',
      decimal_places: kpi.decimal_places,
      target_value: kpi.target_value?.toString() || '',
      warning_threshold: kpi.warning_threshold?.toString() || '',
      critical_threshold: kpi.critical_threshold?.toString() || '',
      alert_enabled: kpi.alert_enabled,
      is_active: kpi.is_active,
      refresh_interval: kpi.refresh_interval
    });
    setDialogOpen(true);
  };

  const handleSaveKPI = async () => {
    try {
      const kpiData = {
        ...formData,
        target_value: formData.target_value ? parseFloat(formData.target_value) : undefined,
        warning_threshold: formData.warning_threshold ? parseFloat(formData.warning_threshold) : undefined,
        critical_threshold: formData.critical_threshold ? parseFloat(formData.critical_threshold) : undefined,
      };

      if (editingKPI) {
        await analyticsAPI.updateKPI(editingKPI.id, kpiData);
      } else {
        await analyticsAPI.createKPI(kpiData);
      }

      setDialogOpen(false);
      loadKPIs();
      if (onRefresh) onRefresh();
    } catch (err) {
      setError('Failed to save KPI. Please try again.');
      console.error('Error saving KPI:', err);
    }
  };

  const handleCalculateKPI = async (kpiId: number) => {
    try {
      await analyticsAPI.calculateKPI(kpiId);
      loadKPIs();
      if (onRefresh) onRefresh();
    } catch (err) {
      setError('Failed to calculate KPI. Please try again.');
      console.error('Error calculating KPI:', err);
    }
  };

  const getStatusColor = (kpi: KPI) => {
    if (!kpi.current_value || !kpi.target_value) return 'default';
    
    const value = kpi.current_value;
    const target = kpi.target_value;
    const warning = kpi.warning_threshold;
    const critical = kpi.critical_threshold;

    if (critical && value >= critical) return 'error';
    if (warning && value >= warning) return 'warning';
    return 'success';
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUpIcon color="success" />;
      case 'decreasing':
        return <TrendingDownIcon color="error" />;
      default:
        return <TimelineIcon color="action" />;
    }
  };

  const getPerformanceStatus = (kpi: KPI) => {
    if (!kpi.current_value || !kpi.target_value) return 'No Data';
    
    const value = kpi.current_value;
    const target = kpi.target_value;
    const percentage = (value / target) * 100;

    if (percentage >= 100) return 'Above Target';
    if (percentage >= 90) return 'On Target';
    return 'Below Target';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5" component="h2">
          KPI Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateKPI}
        >
          Create KPI
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* KPI Grid */}
      <Grid container spacing={3}>
        {kpis.map((kpi) => (
          <Grid item xs={12} sm={6} md={4} key={kpi.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6" noWrap sx={{ maxWidth: '70%' }}>
                    {kpi.display_name}
                  </Typography>
                  <Chip
                    label={kpi.is_active ? 'Active' : 'Inactive'}
                    color={kpi.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </Box>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {kpi.description}
                </Typography>

                <Box display="flex" alignItems="center" mb={2}>
                  {getTrendIcon(kpi.trend)}
                  <Typography variant="h4" sx={{ ml: 1 }}>
                    {kpi.current_value || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    {kpi.unit}
                  </Typography>
                </Box>

                <Box mb={2}>
                  <Typography variant="body2" color="text.secondary">
                    Target: {kpi.target_value || 'N/A'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Status: {getPerformanceStatus(kpi)}
                  </Typography>
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Chip label={kpi.category} size="small" />
                  <Chip label={kpi.module} size="small" variant="outlined" />
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => handleEditKPI(kpi)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleCalculateKPI(kpi.id)}
                      color="secondary"
                    >
                      <RefreshIcon />
                    </IconButton>
                    <IconButton size="small" color="info">
                      <VisibilityIcon />
                    </IconButton>
                  </Box>
                  <Chip
                    label={getPerformanceStatus(kpi)}
                    color={getStatusColor(kpi) as any}
                    size="small"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingKPI ? 'Edit KPI' : 'Create New KPI'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="KPI Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Display Name"
                value={formData.display_name}
                onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                margin="normal"
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Module"
                value={formData.module}
                onChange={(e) => setFormData({ ...formData, module: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Calculation Method"
                value={formData.calculation_method}
                onChange={(e) => setFormData({ ...formData, calculation_method: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Unit"
                value={formData.unit}
                onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Target Value"
                type="number"
                value={formData.target_value}
                onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Decimal Places"
                type="number"
                value={formData.decimal_places}
                onChange={(e) => setFormData({ ...formData, decimal_places: parseInt(e.target.value) })}
                margin="normal"
                inputProps={{ min: 0, max: 4 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Warning Threshold"
                type="number"
                value={formData.warning_threshold}
                onChange={(e) => setFormData({ ...formData, warning_threshold: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Critical Threshold"
                type="number"
                value={formData.critical_threshold}
                onChange={(e) => setFormData({ ...formData, critical_threshold: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Refresh Interval (minutes)"
                type="number"
                value={formData.refresh_interval}
                onChange={(e) => setFormData({ ...formData, refresh_interval: parseInt(e.target.value) })}
                margin="normal"
                inputProps={{ min: 1 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.alert_enabled}
                    onChange={(e) => setFormData({ ...formData, alert_enabled: e.target.checked })}
                  />
                }
                label="Enable Alerts"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                }
                label="Active"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveKPI}>
            {editingKPI ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add kpi"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleCreateKPI}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

export default KPIManagement;

