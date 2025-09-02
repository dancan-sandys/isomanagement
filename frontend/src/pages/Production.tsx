import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
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
  Autocomplete,
  FormHelperText,
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
import { traceabilityAPI } from '../services/traceabilityAPI';
import { usersAPI } from '../services/api';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ReTooltip,
  Legend,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const ProductionPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [processes, setProcesses] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState(0);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [parameterDialogOpen, setParameterDialogOpen] = useState(false);
  const [selectedProcess, setSelectedProcess] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Form states
  const [newProcess, setNewProcess] = useState<ProcessCreatePayload>({
    batch_id: 0, // Changed from 1 to 0 to indicate no selection
    process_type: 'fresh_milk',
    operator_id: undefined,
    spec: {},
  });

  // Batch selection state
  const [availableBatches, setAvailableBatches] = useState<Array<{ id: number; batch_number: string; product_name: string; status?: string; batch_type?: string }>>([]);
  const [batchLoading, setBatchLoading] = useState(false);

  const [newParameter, setNewParameter] = useState<ProcessParameterPayload>({
    parameter_name: '',
    parameter_value: 0,
    unit: '°C',
    target_value: undefined,
    tolerance_min: undefined,
    tolerance_max: undefined,
    notes: '',
  });

  // Map user id to display name (full_name preferred, fallback to username)
  const userDisplayNameById = useMemo(() => {
    const map: Record<number, string> = {};
    users.forEach((u: any) => {
      const display = u?.full_name || u?.username || `User #${u?.id}`;
      if (typeof u?.id === 'number') {
        map[u.id] = display;
      }
    });
    return map;
  }, [users]);

  useEffect(() => {
    loadData();
  }, []);

  // Support direct navigation to analytics tab: /production?tab=analytics
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tabParam = params.get('tab') || params.get('view');
    if (tabParam) {
      if (tabParam.toLowerCase() === 'analytics') {
        setActiveTab(2);
      } else if (!Number.isNaN(Number(tabParam))) {
        const idx = Number(tabParam);
        if (idx >= 0 && idx <= 2) setActiveTab(idx);
      }
    }
  }, [location.search]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [analyticsData, processesData, templatesData, usersData] = await Promise.all([
        productionAPI.getEnhancedAnalytics(),
        productionAPI.listProcesses(),
        productionAPI.getTemplates(),
        usersAPI.getUsers({ page: 1, size: 100 }),
      ]);
      console.log('Analytics data received:', analyticsData);
      console.log('Processes data received:', processesData);
      setAnalytics(analyticsData);
      setProcesses(processesData);
      setTemplates(templatesData);
      const usersList = usersData.items || usersData.data?.items || usersData.data || usersData || [];
      console.log('Users loaded:', usersList.length, 'users');
      setUsers(usersList);
    } catch (e) {
      setError('Failed to load production data');
      console.error('Error loading production data:', e);
        // Set empty users list on error
        setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableBatches = async () => {
    setBatchLoading(true);
    try {
      console.log('Loading available batches...');
      // Load batches from the traceability API
      const response = await traceabilityAPI.getBatches({ size: 100 });
      console.log('Batches response:', response);
      
      if (response.success || response.items) {
        const batches = response.data?.items || response.items || [];
        console.log('Available batches:', batches);
        setAvailableBatches(batches);
      } else {
        console.error('Failed to load batches:', response);
        setAvailableBatches([]);
      }
    } catch (e) {
      console.error('Error loading batches:', e);
      setAvailableBatches([]);
      // Show error message to user
      setError('Failed to load batches. Please try refreshing.');
    } finally {
      setBatchLoading(false);
    }
  };

  const handleCreateProcess = async () => {
    // Validate batch selection
    if (!newProcess.batch_id || newProcess.batch_id === 0) {
      setError('Please select a batch');
      return;
    }

    // Validate that the selected batch exists
    const selectedBatch = availableBatches.find(batch => batch.id === newProcess.batch_id);
    if (!selectedBatch) {
      setError('Selected batch not found. Please refresh and try again.');
      return;
    }

    try {
      await productionAPI.createProcessEnhanced(newProcess);
      setCreateDialogOpen(false);
      setNewProcess({ batch_id: 0, process_type: 'fresh_milk', operator_id: undefined, spec: {} });
      loadData();
    } catch (e: any) {
      const errorMessage = e?.response?.data?.detail || e?.message || 'Failed to create process';
      setError(errorMessage);
      console.error('Error creating process:', e);
    }
  };

  const handleRecordParameter = async () => {
    if (!selectedProcess) {
      setError('No process selected');
      return;
    }

    try {
      console.log('Recording parameter for process:', selectedProcess.id);
      console.log('Parameter data:', newParameter);

      // Validate required fields
      if (!newParameter.parameter_name.trim()) {
        setError('Parameter name is required');
        return;
      }

      if (newParameter.parameter_value === undefined || newParameter.parameter_value === null) {
        setError('Parameter value is required');
        return;
      }

      // Validate tolerance values if provided
      if (newParameter.tolerance_min !== undefined && newParameter.tolerance_max !== undefined) {
        if (newParameter.tolerance_min >= newParameter.tolerance_max) {
          setError('Tolerance min must be less than tolerance max');
          return;
        }
      }

      const result = await productionAPI.recordParameter(selectedProcess.id, newParameter);
      console.log('Parameter recorded successfully:', result);
      
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
      setError(null); // Clear any previous errors
      loadData();
    } catch (e: any) {
      const errorMessage = e?.response?.data?.detail || e?.message || 'Failed to record parameter';
      setError(errorMessage);
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
          <Button
            variant="outlined"
            size="small"
            onClick={() => {
              console.log('Current analytics state:', analytics);
              console.log('Current processes state:', processes);
            }}
          >
            Debug Data
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
              <Typography variant="h4">
                {loading ? (
                  <CircularProgress size={24} />
                ) : (
                  analytics?.total_processes ?? processes?.length ?? 0
                )}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Active Processes</Typography>
              <Typography variant="h4" color="primary">
                {loading ? (
                  <CircularProgress size={24} />
                ) : (
                  analytics?.active_processes ?? processes?.filter(p => p.status === 'in_progress')?.length ?? 0
                )}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Deviations</Typography>
              <Typography variant="h4" color="warning.main">
                {loading ? (
                  <CircularProgress size={24} />
                ) : (
                  analytics?.total_deviations ?? 0
                )}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Alerts</Typography>
              <Typography variant="h4" color="error.main">
                {loading ? (
                  <CircularProgress size={24} />
                ) : (
                  analytics?.unacknowledged_alerts ?? 0
                )}
              </Typography>
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
                      <TableCell>{process.operator_id ? (userDisplayNameById[process.operator_id] || process.operator_id) : '—'}</TableCell>
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

        {/* Analytics Tab */
        }
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
            {(() => {
              const processTypeData = Object.entries(analytics?.process_type_breakdown || {})
                .map(([name, value]) => ({ name, value: Number(value) }));
              const deviationPie = [
                { name: 'Deviations', value: Number(analytics?.total_deviations || 0) },
                { name: 'Critical', value: Number(analytics?.critical_deviations || 0) },
              ];
              const alertPie = [
                { name: 'Total', value: Number(analytics?.total_alerts || 0) },
                { name: 'Unacknowledged', value: Number(analytics?.unacknowledged_alerts || 0) },
              ];
              const yieldTrend = (analytics?.yield_trends || []).map((r: any) => ({ date: r.date, count: Number(r.count) }));
              const deviationTrend = (analytics?.deviation_trends || []).map((r: any) => ({ date: r.date, count: Number(r.count) }));
              const colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'];

              return (
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Process Type Breakdown
                        </Typography>
                        <Box sx={{ height: 260 }}>
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={processTypeData} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="name" />
                              <YAxis allowDecimals={false} />
                              <ReTooltip />
                              <Legend />
                              <Bar dataKey="value" name="Processes" fill="#3B82F6" />
                            </BarChart>
                          </ResponsiveContainer>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Alerts Overview
                        </Typography>
                        <Box sx={{ height: 260, display: 'flex', gap: 2 }}>
                          <Box sx={{ flex: 1 }}>
                            <ResponsiveContainer width="100%" height="100%">
                              <PieChart>
                                <Pie data={deviationPie} dataKey="value" nameKey="name" outerRadius={80} label>
                                  {deviationPie.map((_, idx) => (
                                    <Cell key={`c-dev-${idx}`} fill={colors[idx % colors.length]} />
                                  ))}
                                </Pie>
                                <ReTooltip />
                                <Legend />
                              </PieChart>
                            </ResponsiveContainer>
                          </Box>
                          <Box sx={{ flex: 1 }}>
                            <ResponsiveContainer width="100%" height="100%">
                              <PieChart>
                                <Pie data={alertPie} dataKey="value" nameKey="name" outerRadius={80} label>
                                  {alertPie.map((_, idx) => (
                                    <Cell key={`c-al-${idx}`} fill={colors[(idx + 2) % colors.length]} />
                                  ))}
                                </Pie>
                                <ReTooltip />
                                <Legend />
                              </PieChart>
                            </ResponsiveContainer>
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          30-Day Yield Trend
                        </Typography>
                        <Box sx={{ height: 260 }}>
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={yieldTrend} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="date" />
                              <YAxis allowDecimals={false} />
                              <ReTooltip />
                              <Legend />
                              <Line type="monotone" dataKey="count" name="Yield Records" stroke="#10B981" strokeWidth={2} dot={false} />
                            </LineChart>
                          </ResponsiveContainer>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          30-Day Deviations Trend
                        </Typography>
                        <Box sx={{ height: 260 }}>
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={deviationTrend} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="date" />
                              <YAxis allowDecimals={false} />
                              <ReTooltip />
                              <Legend />
                              <Line type="monotone" dataKey="count" name="Deviations" stroke="#EF4444" strokeWidth={2} dot={false} />
                            </LineChart>
                          </ResponsiveContainer>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              );
            })()}
          </Box>
        )}
      </Paper>

      {/* Create Process Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)} 
        TransitionProps={{
          onEnter: () => loadAvailableBatches()
        }}
        maxWidth="sm" 
        fullWidth
      >
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
            
            <FormControl fullWidth>
              <InputLabel>Select Batch</InputLabel>
              <Select
                value={newProcess.batch_id ? String(newProcess.batch_id) : ''}
                onChange={(e) => setNewProcess({ ...newProcess, batch_id: e.target.value ? parseInt(e.target.value) : 0 })}
                label="Select Batch"
                disabled={batchLoading}
              >
                <MenuItem value="">
                  <em>Select a batch...</em>
                </MenuItem>
                {availableBatches.map((batch) => (
                  <MenuItem key={batch.id} value={String(batch.id)}>
                    {batch.batch_number} - {batch.product_name}
                  </MenuItem>
                ))}
              </Select>
              <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                {batchLoading && (
                  <FormHelperText>Loading batches...</FormHelperText>
                )}
                <Button 
                  size="small" 
                  onClick={loadAvailableBatches}
                  disabled={batchLoading}
                  sx={{ ml: 'auto' }}
                >
                  Refresh Batches
                </Button>
              </Box>
              {availableBatches.length === 0 && !batchLoading && (
                <FormHelperText>
                  No batches available. Please create a batch first in the Traceability module.
                  <Button 
                    size="small" 
                    sx={{ ml: 1 }}
                    onClick={() => {
                      setCreateDialogOpen(false);
                      // Navigate to traceability page
                      window.location.href = '/traceability';
                    }}
                  >
                    Go to Traceability
                  </Button>
                </FormHelperText>
              )}
            </FormControl>
            
                                    <Autocomplete
              options={users}
              getOptionLabel={(option) => option ? `${option.full_name || option.username} (${option.email})` : ''}
              value={users.find(user => user.id === newProcess.operator_id) || null}
              onChange={(event, newValue) => {
                setNewProcess({ ...newProcess, operator_id: newValue ? newValue.id : undefined });
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Operator"
                  placeholder={loading ? "Loading operators..." : "Search for an operator..."}
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {loading ? <CircularProgress color="inherit" size={20} /> : null}
                        {params.InputProps.endAdornment}
                      </>
                    ),
                  }}
                />
              )}
              renderOption={(props, option) => (
                <li {...props}>
                  <div>
                    <div style={{ fontWeight: 'bold' }}>
                      {option.full_name || option.username}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#666' }}>
                      {option.email}
                    </div>
                  </div>
                </li>
              )}
              isOptionEqualToValue={(option, value) => option.id === value?.id}
              noOptionsText={loading ? "Loading operators..." : "No operators found"}
              loading={loading}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateProcess} 
            variant="contained"
            disabled={!newProcess.batch_id || newProcess.batch_id === 0 || availableBatches.length === 0}
          >
            Create Process
          </Button>
        </DialogActions>
      </Dialog>

      {/* Record Parameter Dialog */}
      <Dialog open={parameterDialogOpen} onClose={() => setParameterDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Record Process Parameter
          {selectedProcess && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Process #{selectedProcess.id} - {selectedProcess.process_type}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Parameter Name"
              value={newParameter.parameter_name}
              onChange={(e) => setNewParameter({ ...newParameter, parameter_name: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Parameter Value"
              type="number"
              value={newParameter.parameter_value}
              onChange={(e) => setNewParameter({ ...newParameter, parameter_value: parseFloat(e.target.value) })}
              fullWidth
              required
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

