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
  Alert,
  CircularProgress,
  Paper,
  Tooltip,
  Fab,
  Divider,
  Avatar,
  Badge,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Dashboard as DashboardIcon,
  Widgets as WidgetsIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Public as PublicIcon,
  Lock as LockIcon,
  Palette as PaletteIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { analyticsAPI, AnalyticsDashboard, DashboardWidget } from '../../services/analyticsAPI';

interface DashboardManagementProps {
  onRefresh?: () => void;
}

const DashboardManagement: React.FC<DashboardManagementProps> = ({ onRefresh }) => {
  const [dashboards, setDashboards] = useState<AnalyticsDashboard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingDashboard, setEditingDashboard] = useState<AnalyticsDashboard | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    theme: 'light',
    refresh_interval: 300,
    is_public: false,
    is_active: true,
    is_default: false
  });

  useEffect(() => {
    loadDashboards();
  }, []);

  const loadDashboards = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsAPI.getDashboards();
      setDashboards(data);
    } catch (err) {
      setError('Failed to load dashboards. Please try again.');
      console.error('Error loading dashboards:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDashboard = () => {
    setEditingDashboard(null);
    setFormData({
      name: '',
      description: '',
      theme: 'light',
      refresh_interval: 300,
      is_public: false,
      is_active: true,
      is_default: false
    });
    setDialogOpen(true);
  };

  const handleEditDashboard = (dashboard: AnalyticsDashboard) => {
    setEditingDashboard(dashboard);
    setFormData({
      name: dashboard.name,
      description: dashboard.description || '',
      theme: dashboard.theme,
      refresh_interval: dashboard.refresh_interval,
      is_public: dashboard.is_public,
      is_active: dashboard.is_active,
      is_default: dashboard.is_default
    });
    setDialogOpen(true);
  };

  const handleSaveDashboard = async () => {
    try {
      const dashboardData = {
        ...formData,
        layout_config: editingDashboard?.layout_config || {}
      };

      if (editingDashboard) {
        await analyticsAPI.updateDashboard(editingDashboard.id, dashboardData);
      } else {
        await analyticsAPI.createDashboard(dashboardData);
      }

      setDialogOpen(false);
      loadDashboards();
      if (onRefresh) onRefresh();
    } catch (err) {
      setError('Failed to save dashboard. Please try again.');
      console.error('Error saving dashboard:', err);
    }
  };

  const getThemeColor = (theme: string) => {
    switch (theme) {
      case 'light':
        return 'default';
      case 'dark':
        return 'primary';
      case 'blue':
        return 'info';
      case 'green':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (dashboard: AnalyticsDashboard) => {
    if (dashboard.is_default) {
      return <CheckCircleIcon color="primary" />;
    }
    if (dashboard.is_active) {
      return <CheckCircleIcon color="success" />;
    }
    return <WarningIcon color="warning" />;
  };

  const formatRefreshInterval = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    return `${Math.floor(seconds / 3600)}h`;
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
          Dashboard Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateDashboard}
        >
          Create Dashboard
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Dashboard Grid */}
      <Grid container spacing={3}>
        {dashboards.map((dashboard) => (
          <Grid item xs={12} sm={6} md={4} key={dashboard.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Box display="flex" alignItems="center">
                    {getStatusIcon(dashboard)}
                    <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                      {dashboard.name}
                    </Typography>
                  </Box>
                  <Box>
                    {dashboard.is_public ? (
                      <PublicIcon color="action" fontSize="small" />
                    ) : (
                      <LockIcon color="action" fontSize="small" />
                    )}
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {dashboard.description}
                </Typography>

                <Box display="flex" alignItems="center" mb={2}>
                  <DashboardIcon color="action" sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    {dashboard.widgets_count || 0} widgets
                  </Typography>
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Chip
                    label={dashboard.theme}
                    color={getThemeColor(dashboard.theme) as any}
                    size="small"
                  />
                  <Chip
                    label={`Refresh: ${formatRefreshInterval(dashboard.refresh_interval)}`}
                    size="small"
                    variant="outlined"
                  />
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => handleEditDashboard(dashboard)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton size="small" color="info">
                      <VisibilityIcon />
                    </IconButton>
                    <IconButton size="small" color="secondary">
                      <SettingsIcon />
                    </IconButton>
                  </Box>
                  <Box>
                    {dashboard.is_default && (
                      <Chip label="Default" color="primary" size="small" />
                    )}
                    {dashboard.is_active && !dashboard.is_default && (
                      <Chip label="Active" color="success" size="small" />
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingDashboard ? 'Edit Dashboard' : 'Create New Dashboard'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Dashboard Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
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
              <FormControl fullWidth margin="normal">
                <InputLabel>Theme</InputLabel>
                <Select
                  value={formData.theme}
                  onChange={(e) => setFormData({ ...formData, theme: e.target.value })}
                  label="Theme"
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                  <MenuItem value="blue">Blue</MenuItem>
                  <MenuItem value="green">Green</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Refresh Interval (seconds)"
                type="number"
                value={formData.refresh_interval}
                onChange={(e) => setFormData({ ...formData, refresh_interval: parseInt(e.target.value) })}
                margin="normal"
                inputProps={{ min: 30 }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_public}
                    onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                  />
                }
                label="Public Dashboard"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
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
            <Grid item xs={12} sm={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_default}
                    onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                  />
                }
                label="Default Dashboard"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveDashboard}>
            {editingDashboard ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add dashboard"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleCreateDashboard}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

export default DashboardManagement;

