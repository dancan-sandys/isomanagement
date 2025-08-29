import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Stack,
  Typography,
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
  Button,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  TextField,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Warning, Error, Info, ArrowBack, Science, Edit, Refresh } from '@mui/icons-material';
import productionAPI, { suppliersAPI, ProcessParameterPayload } from '../services/productionAPI';
import Autocomplete from '@mui/material/Autocomplete';

const ProductionProcessDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [processDetails, setProcessDetails] = useState<any | null>(null);
  const [processAudit, setProcessAudit] = useState<any[]>([]);
  const [detailsTab, setDetailsTab] = useState(0);
  const [auditFilter, setAuditFilter] = useState({ action: '', from: '', to: '' });

  const [materialOptions, setMaterialOptions] = useState<any[]>([]);
  const [matForm, setMatForm] = useState({ material_id: '', quantity: '', unit: 'kg', lot_number: '' });

  const [mocOpen, setMocOpen] = useState(false);
  const [mocForm, setMocForm] = useState({ title: '', reason: '', risk_rating: 'medium' });

  // Record Parameter state
  const [parameterDialogOpen, setParameterDialogOpen] = useState(false);
  const [newParameter, setNewParameter] = useState<ProcessParameterPayload>({
    parameter_name: '',
    parameter_value: 0,
    unit: '°C',
    target_value: undefined,
    tolerance_min: undefined,
    tolerance_max: undefined,
    notes: '',
  });

  // Edit Process state
  const [editOpen, setEditOpen] = useState(false);
  const [editForm, setEditForm] = useState<{ operator_id?: number; status?: string; notes?: string }>({});

  const loadDetails = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      setError(null);
      const processId = parseInt(id, 10);
      
      // Use the productionAPI service instead of direct fetch
      const res = await productionAPI.getProcessDetails(processId);
      setProcessDetails(res);
      
      try {
        const audit = await productionAPI.getProcessAudit(processId, { limit: 100, offset: 0 });
        setProcessAudit(audit);
      } catch (e) {
        console.warn('Failed to load audit data:', e);
        setProcessAudit([]);
      }
    } catch (e: any) {
      const errorMessage = e?.response?.data?.detail || e?.message || 'Failed to load process details';
      setError(errorMessage);
      console.error('Error loading process details:', e);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadDetails();
  }, [loadDetails]);

  const handleRecordParameter = async () => {
    try {
      if (!processDetails?.id) {
        setError('Process not found');
        return;
      }

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

      await productionAPI.recordParameter(processDetails.id, newParameter);
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
      await loadDetails();
    } catch (e: any) {
      const errorMessage = e?.response?.data?.detail || e?.message || 'Failed to record parameter';
      setError(errorMessage);
      console.error('Error recording parameter:', e);
    }
  };

  const handleOpenEdit = () => {
    if (!processDetails) return;
    setEditForm({
      operator_id: processDetails.operator_id,
      status: processDetails.status,
      notes: processDetails.notes || '',
    });
    setEditOpen(true);
  };

  const handleSaveEdit = async () => {
    try {
      if (!processDetails?.id) {
        setError('Process not found');
        return;
      }

      // Validate status if provided
      if (editForm.status && !['in_progress', 'completed', 'diverted'].includes(editForm.status)) {
        setError('Invalid status value');
        return;
      }

      await productionAPI.updateProcess(processDetails.id, editForm);
      setEditOpen(false);
      await loadDetails();
    } catch (e: any) {
      const errorMessage = e?.response?.data?.detail || e?.message || 'Failed to update process';
      setError(errorMessage);
      console.error('Error updating process:', e);
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
        <Stack direction="row" spacing={1} alignItems="center">
          <Button startIcon={<ArrowBack />} onClick={() => navigate('/production')}>Back</Button>
          <Typography variant="h5">Process Details</Typography>
        </Stack>
        <Stack direction="row" spacing={1} alignItems="center">
          <Button
            variant="outlined"
            size="small"
            startIcon={<Refresh />}
            onClick={loadDetails}
            disabled={loading}
          >
            Refresh
          </Button>

          <Tooltip title="Record Parameter">
            <IconButton size="small" onClick={() => setParameterDialogOpen(true)}>
              <Science />
            </IconButton>
          </Tooltip>
          <Tooltip title="Edit Process">
            <IconButton size="small" onClick={handleOpenEdit}>
              <Edit />
            </IconButton>
          </Tooltip>
        </Stack>
      </Stack>
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs value={detailsTab} onChange={(_, v) => setDetailsTab(v)} sx={{ px: 2 }}>
          <Tab label="Overview" />
          <Tab label="Parameters" />
          <Tab label="Deviations & Alerts" />
          <Tab label="Audit" />
        </Tabs>

        <Box p={2}>
          {detailsTab === 0 && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Core Info
              </Typography>
              <List>
                <ListItem>
                  <ListItemText 
                    primary={`ID: ${processDetails?.id}`} 
                    secondary={`Type: ${processDetails?.process_type}`} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary={
                      <Stack direction="row" spacing={1} alignItems="center">
                        <span>Status:</span>
                        <Chip 
                          label={processDetails?.status || 'Unknown'} 
                          color={
                            processDetails?.status === 'completed' ? 'success' :
                            processDetails?.status === 'in_progress' ? 'primary' :
                            processDetails?.status === 'diverted' ? 'error' : 'default'
                          }
                          size="small"
                        />
                      </Stack>
                    } 
                    secondary={`Batch: ${processDetails?.batch_id}`} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary={`Operator: ${processDetails?.operator_id || '—'}`} 
                    secondary={`Start: ${processDetails?.start_time ? new Date(processDetails.start_time).toLocaleString() : '—'}`} 
                  />
                </ListItem>
                {processDetails?.end_time && (
                  <ListItem>
                    <ListItemText 
                      primary={`End Time: ${new Date(processDetails.end_time).toLocaleString()}`} 
                      secondary={`Duration: ${processDetails.start_time ? 
                        Math.round((new Date(processDetails.end_time).getTime() - new Date(processDetails.start_time).getTime()) / (1000 * 60)) + ' minutes' : 
                        '—'}`} 
                    />
                  </ListItem>
                )}
              </List>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle1" gutterBottom>Materials</Typography>
              <Stack direction="row" spacing={1} sx={{ mt: 1, mb: 1 }}>
                <Autocomplete
                  size="small"
                  options={materialOptions}
                  getOptionLabel={(o: any) => o.name || o.code || String(o.id)}
                  onInputChange={async (_, value) => {
                    if (value && value.length >= 2) {
                      try {
                        const results = await suppliersAPI.searchMaterials(value, 10);
                        setMaterialOptions(results);
                      } catch (e) {
                        setMaterialOptions([]);
                      }
                    } else {
                      setMaterialOptions([]);
                    }
                  }}
                  onChange={(_, value: any) => {
                    setMatForm({ ...matForm, material_id: value?.id ? String(value.id) : '' });
                  }}
                  renderInput={(params) => (
                    <TextField {...params} label="Search Material" />
                  )}
                  sx={{ minWidth: 260 }}
                />
                <TextField label="Qty" size="small" value={matForm.quantity} onChange={(e) => setMatForm({ ...matForm, quantity: e.target.value })} />
                <TextField label="Unit" size="small" value={matForm.unit} onChange={(e) => setMatForm({ ...matForm, unit: e.target.value })} />
                <TextField label="Lot" size="small" value={matForm.lot_number} onChange={(e) => setMatForm({ ...matForm, lot_number: e.target.value })} />
                <Button size="small" variant="outlined" onClick={async () => {
                  try {
                    if (!processDetails?.id) {
                      setError('Process not found');
                      return;
                    }
                    
                    if (!matForm.material_id) {
                      setError('Please select a material');
                      return;
                    }
                    
                    if (!matForm.quantity || parseFloat(matForm.quantity) <= 0) {
                      setError('Please enter a valid quantity');
                      return;
                    }

                    await productionAPI.recordMaterialConsumption(processDetails.id, {
                      material_id: parseInt(matForm.material_id, 10),
                      quantity: parseFloat(matForm.quantity),
                      unit: matForm.unit,
                      lot_number: matForm.lot_number || undefined,
                    });
                    
                    setMatForm({ material_id: '', quantity: '', unit: 'kg', lot_number: '' });
                    await loadDetails(); // Refresh the data
                  } catch (e: any) {
                    const errorMessage = e?.response?.data?.detail || e?.message || 'Failed to record material consumption';
                    setError(errorMessage);
                    console.error('Error recording material consumption:', e);
                  }
                }}>Record</Button>
              </Stack>
              <Typography variant="subtitle2" color="text.secondary">Consumptions</Typography>
              <Table size="small" sx={{ mb: 1 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Material</TableCell>
                    <TableCell>Qty</TableCell>
                    <TableCell>Unit</TableCell>
                    <TableCell>Lot</TableCell>
                    <TableCell>When</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(processDetails?.materials || []).map((m: any) => (
                    <TableRow key={m.id}>
                      <TableCell>{m.id}</TableCell>
                      <TableCell>{m.material_id}</TableCell>
                      <TableCell>{m.quantity}</TableCell>
                      <TableCell>{m.unit}</TableCell>
                      <TableCell>{m.lot_number}</TableCell>
                      <TableCell>{m.consumed_at ? new Date(m.consumed_at).toLocaleString() : '—'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          )}

          {detailsTab === 1 && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>Parameters</Typography>
              {processDetails?.parameters && processDetails.parameters.length > 0 ? (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Value</TableCell>
                      <TableCell>Unit</TableCell>
                      <TableCell>Target</TableCell>
                      <TableCell>Tolerance</TableCell>
                      <TableCell>Within</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {processDetails.parameters.map((p: any) => (
                      <TableRow key={p.id}>
                        <TableCell>{p.parameter_name}</TableCell>
                        <TableCell>{p.parameter_value}</TableCell>
                        <TableCell>{p.unit}</TableCell>
                        <TableCell>{p.target_value ?? '—'}</TableCell>
                        <TableCell>{p.tolerance_min ?? '—'} - {p.tolerance_max ?? '—'}</TableCell>
                        <TableCell>{p.is_within_tolerance === false ? <Chip label="OOT" color="error" size="small"/> : 'OK'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <Box textAlign="center" py={3}>
                  <Typography color="text.secondary">No parameters recorded yet</Typography>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    onClick={() => setParameterDialogOpen(true)}
                    sx={{ mt: 1 }}
                  >
                    Record First Parameter
                  </Button>
                </Box>
              )}
            </Box>
          )}

          {detailsTab === 2 && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>Deviations</Typography>
                {processDetails?.deviations && processDetails.deviations.length > 0 ? (
                  <List>
                    {processDetails.deviations.map((d: any) => (
                      <ListItem key={d.id}>
                        <ListItemIcon><Warning color={d.severity === 'critical' ? 'error' : 'warning'} /></ListItemIcon>
                        <ListItemText 
                          primary={`${d.deviation_type}: ${d.actual_value} vs ${d.expected_value}`} 
                          secondary={`Severity: ${d.severity} • ${new Date(d.created_at).toLocaleString()}`} 
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Box textAlign="center" py={3}>
                    <Typography color="text.secondary">No deviations recorded</Typography>
                  </Box>
                )}
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>Alerts</Typography>
                {processDetails?.alerts && processDetails.alerts.length > 0 ? (
                  <List>
                    {processDetails.alerts.map((a: any) => (
                      <ListItem key={a.id}>
                        <ListItemIcon>{getAlertIcon(a.alert_level)}</ListItemIcon>
                        <ListItemText 
                          primary={a.message} 
                          secondary={`${a.alert_type} • ${new Date(a.created_at).toLocaleString()}`} 
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Box textAlign="center" py={3}>
                    <Typography color="text.secondary">No alerts recorded</Typography>
                  </Box>
                )}
              </Grid>
            </Grid>
          )}

          {detailsTab === 3 && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>Audit Trail</Typography>
              <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
                <TextField size="small" label="Action contains" value={auditFilter.action} onChange={(e) => setAuditFilter({ ...auditFilter, action: e.target.value })} />
                <TextField size="small" label="From" type="date" InputLabelProps={{ shrink: true }} value={auditFilter.from} onChange={(e) => setAuditFilter({ ...auditFilter, from: e.target.value })} />
                <TextField size="small" label="To" type="date" InputLabelProps={{ shrink: true }} value={auditFilter.to} onChange={(e) => setAuditFilter({ ...auditFilter, to: e.target.value })} />
              </Stack>
              {(() => {
                const filtered = processAudit.filter((r) => {
                  const okAction = auditFilter.action ? (r.action || '').toLowerCase().includes(auditFilter.action.toLowerCase()) : true;
                  const ts = r.created_at ? new Date(r.created_at).getTime() : 0;
                  const fromOk = auditFilter.from ? ts >= new Date(auditFilter.from).getTime() : true;
                  const toOk = auditFilter.to ? ts <= new Date(auditFilter.to).getTime() + 24*3600*1000 - 1 : true;
                  return okAction && fromOk && toOk;
                });
                return (
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>Action</TableCell>
                        <TableCell>User</TableCell>
                        <TableCell>Details</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {filtered.map((r) => (
                        <TableRow key={r.id}>
                          <TableCell>{new Date(r.created_at).toLocaleString()}</TableCell>
                          <TableCell><Chip label={r.action} size="small" /></TableCell>
                          <TableCell>{r.user_id ?? '—'}</TableCell>
                          <TableCell><pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(r.details || {}, null, 2)}</pre></TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                );
              })()}
            </Box>
          )}
        </Box>
      </Paper>

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
          <Button onClick={handleRecordParameter} variant="contained">Record Parameter</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Process Dialog */}
      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Process</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Operator ID"
              type="number"
              value={editForm.operator_id ?? ''}
              onChange={(e) => setEditForm({ ...editForm, operator_id: e.target.value ? parseInt(e.target.value) : undefined })}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                label="Status"
                value={editForm.status || ''}
                onChange={(e) => setEditForm({ ...editForm, status: e.target.value as string })}
              >
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="diverted">Diverted</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Notes"
              multiline
              rows={3}
              value={editForm.notes || ''}
              onChange={(e) => setEditForm({ ...editForm, notes: e.target.value })}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveEdit}>Save</Button>
        </DialogActions>
      </Dialog>

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
              if (!res.ok) {
                throw 'Failed to submit change request';
              }
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

export default ProductionProcessDetail;

