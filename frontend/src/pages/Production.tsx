import React, { useEffect, useState } from 'react';
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
  Badge,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Add,
  PlayArrow,
  Stop,
  Warning,
  CheckCircle,
  Error,
  Info,
  Timeline,
  Science,
  Settings,
  Refresh,
  Visibility,
  Edit,
  Delete,
} from '@mui/icons-material';
import productionAPI, {
  ProcessCreatePayload,
  ProcessParameterPayload,
  ProcessDeviationPayload,
  ProcessAlertPayload,
  ProcessTemplatePayload,
} from '../services/productionAPI';

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
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [processDetails, setProcessDetails] = useState<any | null>(null);
  const [mocOpen, setMocOpen] = useState(false);
  const [mocForm, setMocForm] = useState({ title: '', reason: '', risk_rating: 'medium' });

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

  const handleOpenDetails = async (processId: number) => {
    try {
      setLoading(true);
      const res = await (await fetch(`/api/v1/production/processes/${processId}/details`)).json();
      setProcessDetails(res);
      setDetailsOpen(true);
    } catch (e) {
      setError('Failed to load process details');
    } finally {
      setLoading(false);
    }
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
                      Performance Metrics
                    </Typography>
                    <Stack spacing={2}>
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Average Yield
                        </Typography>
                        <Typography variant="h4">
                          {analytics?.average_yield_percent ? `${analytics.average_yield_percent}%` : '—'}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Critical Deviations
                        </Typography>
                        <Typography variant="h4" color="error.main">
                          {analytics?.critical_deviations ?? '—'}
                        </Typography>
                      </Box>
                    </Stack>
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

      {/* Process Details Dialog */}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Process Details</DialogTitle>
        <DialogContent>
          {!processDetails && (
            <Typography variant="body2" color="text.secondary">No details loaded.</Typography>
          )}
          {processDetails && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Process</Typography>
                <Typography variant="body1">#{processDetails.id} • {processDetails.process_type} • {processDetails.status}</Typography>
                <Typography variant="body2" color="text.secondary">Started: {new Date(processDetails.start_time).toLocaleString()}</Typography>
              </Box>
              <Stack direction="row" spacing={1}>
                <Button size="small" variant="outlined" onClick={async () => {
                  try {
                    await productionAPI.bindSpec(processDetails.id, { document_id: 1, document_version: '1.0' });
                    const res = await productionAPI.checkRelease(processDetails.id);
                    setProcessDetails({ ...processDetails, release_check: res });
                  } catch (e) {
                    setError('Spec bind or release check failed');
                  }
                }}>Bind Spec & Check Release</Button>
                <Button size="small" variant="contained" color="success" onClick={async () => {
                  try {
                    const res = await productionAPI.releaseProcess(processDetails.id, { signature_hash: 'demo-signature' });
                    setProcessDetails({ ...processDetails, release_result: res });
                  } catch (e) {
                    setError('Release failed');
                  }
                }}>Release</Button>
                <Button size="small" variant="outlined" onClick={async () => {
                  try {
                    const blob = await productionAPI.exportProductionSheetPDF(processDetails.id);
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `production_sheet_${processDetails.id}.pdf`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    setTimeout(() => window.URL.revokeObjectURL(url), 1000);
                  } catch (e) {
                    setError('Export PDF failed');
                  }
                }}>Download PDF</Button>
                <Button size="small" variant="outlined" color="warning" onClick={() => setMocOpen(true)}>Request Change</Button>
              </Stack>
              <Divider />
              {processDetails.release_check && (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">Release Check</Typography>
                  <List dense>
                    {(processDetails.release_check.checklist || []).map((c: any, idx: number) => (
                      <ListItem key={idx}>
                        <ListItemText primary={`${c.item}`} secondary={c.passed ? 'OK' : 'FAIL'} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Parameters</Typography>
                <List dense>
                  {(processDetails.parameters || []).slice(0, 10).map((p: any) => (
                    <ListItem key={p.id}>
                      <ListItemText
                        primary={`${p.parameter_name}: ${p.parameter_value} ${p.unit}`}
                        secondary={`Recorded: ${new Date(p.recorded_at).toLocaleString()}${p.is_within_tolerance === false ? ' • OUT OF TOLERANCE' : ''}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Deviations</Typography>
                <List dense>
                  {(processDetails.deviations || []).slice(0, 10).map((d: any) => (
                    <ListItem key={d.id}>
                      <ListItemText
                        primary={`${d.deviation_type}: ${d.actual_value} (target ${d.expected_value}) • ${d.severity}`}
                        secondary={`Resolved: ${d.resolved ? 'Yes' : 'No'}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Alerts</Typography>
                <List dense>
                  {(processDetails.alerts || []).slice(0, 10).map((a: any) => (
                    <ListItem key={a.id}>
                      <ListItemText
                        primary={`${a.alert_type}: ${a.message} • ${a.alert_level}`}
                        secondary={`Ack: ${a.acknowledged ? 'Yes' : 'No'}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Minimal MOC Dialog */}
      <Dialog open={mocOpen} onClose={() => setMocOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Request Change (MOC)</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Title" value={mocForm.title} onChange={(e) => setMocForm({ ...mocForm, title: e.target.value })} fullWidth />
            <TextField label="Reason" value={mocForm.reason} onChange={(e) => setMocForm({ ...mocForm, reason: e.target.value })} fullWidth multiline rows={3} />
            <TextField label="Risk Rating" value={mocForm.risk_rating} onChange={(e) => setMocForm({ ...mocForm, risk_rating: e.target.value })} fullWidth />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMocOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            try {
              const res = await fetch('/api/v1/change-requests/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  title: mocForm.title,
                  reason: mocForm.reason,
                  process_id: processDetails?.id,
                  risk_rating: mocForm.risk_rating,
                })
              });
              if (!res.ok) throw new Error('Failed');
              setMocOpen(false);
            } catch (e) {
              setError('Failed to submit change request');
            }
          }}>Submit</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProductionPage;

