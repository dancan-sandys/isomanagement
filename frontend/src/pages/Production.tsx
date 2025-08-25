import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Stack,
  Button,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
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
  Alert,
  CircularProgress,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Add,
  Warning,
  Error,
  Info,
  Science,
  Refresh,
  Visibility,
  Edit,
} from '@mui/icons-material';
import productionAPI, {
  ProcessCreatePayload,
  ProcessParameterPayload,
} from '../services/productionAPI';
import { suppliersAPI } from '../services/productionAPI';

const ProductionPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [processes, setProcesses] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState(0);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [parameterDialogOpen, setParameterDialogOpen] = useState(false);
  const [selectedProcess, setSelectedProcess] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Form states
  const [newProcess, setNewProcess] = useState<ProcessCreatePayload>({
    batch_id: 1,
    process_type: 'fresh_milk',
    operator_id: undefined,
    spec: {},
  });

  const [newParameter, setNewParameter] = useState<ProcessParameterPayload>({
    parameter_name: '',
    parameter_value: 0,
    unit: '°C',
    target_value: undefined,
    tolerance_min: undefined,
    tolerance_max: undefined,
    notes: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [analyticsData, processesData, templatesData] = await Promise.all([
        productionAPI.getEnhancedAnalytics(),
        productionAPI.listProcesses(),
        productionAPI.getTemplates(),
      ]);
      setAnalytics(analyticsData);
      setProcesses(processesData);
      setTemplates(templatesData);
    } catch (e) {
      setError('Failed to load production data');
      console.error('Error loading production data:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProcess = async () => {
    try {
      await productionAPI.createProcessEnhanced(newProcess);
      setCreateDialogOpen(false);
      setNewProcess({ batch_id: 1, process_type: 'fresh_milk', operator_id: undefined, spec: {} });
      loadData();
    } catch (e) {
      setError('Failed to create process');
      console.error('Error creating process:', e);
    }
  };

  const handleRecordParameter = async () => {
    if (!selectedProcess) return;
    try {
      await productionAPI.recordParameter(selectedProcess.id, newParameter);
      setParameterDialogOpen(false);
      setNewParameter({
        parameter_name: '',
        parameter_value: 0,
        unit: '°C',
        target_value: undefined,
        tolerance_min: undefined,
        tolerance_max: undefined,
        notes: '',
      });
      loadData();
    } catch (e) {
      setError('Failed to record parameter');
      console.error('Error recording parameter:', e);
    }
  };

  const handleOpenDetails = (processId: number) => {
    navigate(`/production/processes/${processId}`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in_progress': return 'primary';
      case 'completed': return 'success';
      case 'diverted': return 'error';
      default: return 'default';
    }
  };

  const getAlertIcon = (level: string) => {
    switch (level) {
      case 'critical': return <Error color="error" />;
      case 'error': return <Error color="error" />;
      case 'warning': return <Warning color="warning" />;
      case 'info': return <Info color="info" />;
      default: return <Info />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Production Management System</Typography>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadData}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Process
          </Button>
        </Stack>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Analytics Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Total Processes</Typography>
              <Typography variant="h4">{analytics?.total_processes ?? '—'}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Active Processes</Typography>
              <Typography variant="h4" color="primary">{analytics?.active_processes ?? '—'}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Deviations</Typography>
              <Typography variant="h4" color="warning.main">{analytics?.total_deviations ?? '—'}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Alerts</Typography>
              <Typography variant="h4" color="error.main">{analytics?.unacknowledged_alerts ?? '—'}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Processes" />
          <Tab label="Templates" />
          <Tab label="Analytics" />
        </Tabs>

        {/* Processes Tab */}
        {activeTab === 0 && (
          <Box p={2}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Start Time</TableCell>
                    <TableCell>Operator</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {processes.map((process) => (
                    <TableRow key={process.id}>
                      <TableCell>{process.id}</TableCell>
                      <TableCell>
                        <Chip label={process.process_type} size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={process.status}
                          color={getStatusColor(process.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(process.start_time).toLocaleString()}
                      </TableCell>
                      <TableCell>{process.operator_id || '—'}</TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          <Tooltip title="View Details">
                            <IconButton size="small" onClick={() => handleOpenDetails(process.id)}>
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Record Parameter">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedProcess(process);
                                setParameterDialogOpen(true);
                              }}
                            >
                              <Science />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton size="small">
                              <Edit />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* Templates Tab */}
        {activeTab === 1 && (
          <Box p={2}>
            <Grid container spacing={2}>
              {templates.map((template) => (
                <Grid item xs={12} md={6} lg={4} key={template.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {template.template_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {template.description}
                      </Typography>
                      <Chip label={template.product_type} size="small" sx={{ mr: 1 }} />
                      <Chip
                        label={template.is_active ? 'Active' : 'Inactive'}
                        color={template.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Analytics Tab */}
        {activeTab === 2 && (
          <Box p={2}>
            <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
              <Button size="small" variant="outlined" onClick={async () => {
                try {
                  const blob = await productionAPI.exportAnalyticsCSV();
                  const url = window.URL.createObjectURL(blob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = 'production_analytics.csv';
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                  setTimeout(() => window.URL.revokeObjectURL(url), 1000);
                } catch (e) {
                  setError('Export CSV failed');
                }
              }}>Export CSV</Button>
              <Button size="small" variant="outlined" onClick={async () => {
                try {
                  const blob = await productionAPI.exportAnalyticsPDF();
                  const url = window.URL.createObjectURL(blob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = 'production_analytics.pdf';
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                  setTimeout(() => window.URL.revokeObjectURL(url), 1000);
                } catch (e) {
                  setError('Export PDF failed');
                }
              }}>Export PDF</Button>
            </Stack>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Process Type Breakdown
                    </Typography>
                    <List>
                      {analytics?.process_type_breakdown && 
                        Object.entries(analytics.process_type_breakdown).map(([type, count]) => (
                          <ListItem key={type}>
                            <ListItemText
                              primary={type}
                              secondary={`${count} processes`}
                            />
                          </ListItem>
                        ))
                      }
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      30-Day Trends
                    </Typography>
                    <Typography variant="subtitle2">Yield Records</Typography>
                    <List dense>
                      {analytics?.yield_trends?.map((row: any) => (
                        <ListItem key={`y-${row.date}`}>
                          <ListItemText primary={`${row.date}`} secondary={`${row.count} records`} />
                        </ListItem>
                      ))}
                    </List>
                    <Divider sx={{ my: 1 }} />
                    <Typography variant="subtitle2">Deviations</Typography>
                    <List dense>
                      {analytics?.deviation_trends?.map((row: any) => (
                        <ListItem key={`d-${row.date}`}>
                          <ListItemText primary={`${row.date}`} secondary={`${row.count} deviations`} />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>

      {/* Create Process Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Process</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Process Type</InputLabel>
              <Select
                value={newProcess.process_type}
                onChange={(e) => setNewProcess({ ...newProcess, process_type: e.target.value as any })}
                label="Process Type"
              >
                <MenuItem value="fresh_milk">Fresh Milk</MenuItem>
                <MenuItem value="yoghurt">Yoghurt</MenuItem>
                <MenuItem value="mala">Mala</MenuItem>
                <MenuItem value="cheese">Cheese</MenuItem>
                <MenuItem value="pasteurized_milk">Pasteurized Milk</MenuItem>
                <MenuItem value="fermented_products">Fermented Products</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Batch ID"
              type="number"
              value={newProcess.batch_id}
              onChange={(e) => setNewProcess({ ...newProcess, batch_id: parseInt(e.target.value) })}
              fullWidth
            />
            <TextField
              label="Operator ID"
              type="number"
              value={newProcess.operator_id || ''}
              onChange={(e) => setNewProcess({ ...newProcess, operator_id: e.target.value ? parseInt(e.target.value) : undefined })}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateProcess} variant="contained">
            Create Process
          </Button>
        </DialogActions>
      </Dialog>

      {/* Record Parameter Dialog */}
      <Dialog open={parameterDialogOpen} onClose={() => setParameterDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Record Process Parameter</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Parameter Name"
              value={newParameter.parameter_name}
              onChange={(e) => setNewParameter({ ...newParameter, parameter_name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Parameter Value"
              type="number"
              value={newParameter.parameter_value}
              onChange={(e) => setNewParameter({ ...newParameter, parameter_value: parseFloat(e.target.value) })}
              fullWidth
            />
            <TextField
              label="Unit"
              value={newParameter.unit}
              onChange={(e) => setNewParameter({ ...newParameter, unit: e.target.value })}
              fullWidth
            />
            <TextField
              label="Target Value"
              type="number"
              value={newParameter.target_value || ''}
              onChange={(e) => setNewParameter({ ...newParameter, target_value: e.target.value ? parseFloat(e.target.value) : undefined })}
              fullWidth
            />
            <TextField
              label="Tolerance Min"
              type="number"
              value={newParameter.tolerance_min || ''}
              onChange={(e) => setNewParameter({ ...newParameter, tolerance_min: e.target.value ? parseFloat(e.target.value) : undefined })}
              fullWidth
            />
            <TextField
              label="Tolerance Max"
              type="number"
              value={newParameter.tolerance_max || ''}
              onChange={(e) => setNewParameter({ ...newParameter, tolerance_max: e.target.value ? parseFloat(e.target.value) : undefined })}
              fullWidth
            />
            <TextField
              label="Notes"
              multiline
              rows={3}
              value={newParameter.notes}
              onChange={(e) => setNewParameter({ ...newParameter, notes: e.target.value })}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setParameterDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleRecordParameter} variant="contained">
            Record Parameter
          </Button>
        </DialogActions>
      </Dialog>

      {/* Details moved to full page at /production/processes/:id */}
    </Box>
  );
};

export default ProductionPage;

