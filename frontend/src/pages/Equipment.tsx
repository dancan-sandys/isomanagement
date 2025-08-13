import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Stack,
  Button,
  TextField,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  Grid,
  Card,
  CardContent,
  CardActions,
  Divider,
  Badge,
  LinearProgress,
  InputAdornment,
  FormHelperText,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Schedule as ScheduleIcon,
  Build as BuildIcon,
  Science as ScienceIcon,
  History as HistoryIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  CalendarToday as CalendarIcon,
  LocationOn as LocationIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { equipmentAPI } from '../services/equipmentAPI';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`equipment-tabpanel-${index}`}
      aria-labelledby={`equipment-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const EquipmentPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [equipment, setEquipment] = useState<any[]>([]);
  const [maintenancePlans, setMaintenancePlans] = useState<any[]>([]);
  const [workOrders, setWorkOrders] = useState<any[]>([]);
  const [calibrationPlans, setCalibrationPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Equipment Dialog
  const [equipmentDialog, setEquipmentDialog] = useState(false);
  const [equipmentForm, setEquipmentForm] = useState({
    name: '',
    equipment_type: '',
    serial_number: '',
    location: '',
    notes: '',
  });

  // Maintenance Plan Dialog
  const [maintenanceDialog, setMaintenanceDialog] = useState(false);
  const [maintenanceForm, setMaintenanceForm] = useState({
    equipment_id: 0,
    frequency_days: 30,
    maintenance_type: 'preventive',
    notes: '',
  });

  // Work Order Dialog
  const [workOrderDialog, setWorkOrderDialog] = useState(false);
  const [workOrderForm, setWorkOrderForm] = useState({
    equipment_id: 0,
    plan_id: '',
    title: '',
    description: '',
  });

  // Calibration Dialog
  const [calibrationDialog, setCalibrationDialog] = useState(false);
  const [calibrationForm, setCalibrationForm] = useState({
    equipment_id: 0,
    schedule_date: new Date(),
    notes: '',
  });

  // Calibration Certificate Upload
  const [certificateDialog, setCertificateDialog] = useState(false);
  const [certificateForm, setCertificateForm] = useState({
    plan_id: 0,
    file: null as File | null,
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [equipmentData, workOrdersData] = await Promise.all([
        equipmentAPI.list(),
        equipmentAPI.listWorkOrders(),
      ]);
      setEquipment(equipmentData || []);
      setWorkOrders(workOrdersData || []);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleEquipmentSubmit = async () => {
    try {
      await equipmentAPI.create(equipmentForm);
      setEquipmentDialog(false);
      setEquipmentForm({ name: '', equipment_type: '', serial_number: '', location: '', notes: '' });
      loadData();
    } catch (error) {
      console.error('Error creating equipment:', error);
    }
  };

  const handleMaintenanceSubmit = async () => {
    try {
      await equipmentAPI.createMaintenancePlan(maintenanceForm.equipment_id, {
        frequency_days: maintenanceForm.frequency_days,
        maintenance_type: maintenanceForm.maintenance_type as 'preventive' | 'corrective',
        notes: maintenanceForm.notes,
      });
      setMaintenanceDialog(false);
      setMaintenanceForm({ equipment_id: 0, frequency_days: 30, maintenance_type: 'preventive', notes: '' });
      loadData();
    } catch (error) {
      console.error('Error creating maintenance plan:', error);
    }
  };

  const handleWorkOrderSubmit = async () => {
    try {
      await equipmentAPI.createWorkOrder({
        equipment_id: workOrderForm.equipment_id,
        plan_id: workOrderForm.plan_id ? parseInt(workOrderForm.plan_id) : undefined,
        title: workOrderForm.title,
        description: workOrderForm.description,
      });
      setWorkOrderDialog(false);
      setWorkOrderForm({ equipment_id: 0, plan_id: '', title: '', description: '' });
      loadData();
    } catch (error) {
      console.error('Error creating work order:', error);
    }
  };

  const handleCalibrationSubmit = async () => {
    try {
      await equipmentAPI.createCalibrationPlan(calibrationForm.equipment_id, {
        schedule_date: calibrationForm.schedule_date.toISOString().split('T')[0],
        notes: calibrationForm.notes,
      });
      setCalibrationDialog(false);
      setCalibrationForm({ equipment_id: 0, schedule_date: new Date(), notes: '' });
      loadData();
    } catch (error) {
      console.error('Error creating calibration plan:', error);
    }
  };

  const handleCertificateUpload = async () => {
    if (!certificateForm.file) return;
    try {
      await equipmentAPI.uploadCalibrationCertificate(certificateForm.plan_id, certificateForm.file);
      setCertificateDialog(false);
      setCertificateForm({ plan_id: 0, file: null });
      loadData();
    } catch (error) {
      console.error('Error uploading certificate:', error);
    }
  };

  const handleCompleteWorkOrder = async (workOrderId: number) => {
    try {
      await equipmentAPI.completeWorkOrder(workOrderId);
      loadData();
    } catch (error) {
      console.error('Error completing work order:', error);
    }
  };

  const getEquipmentTypeColor = (type: string) => {
    const colors: { [key: string]: 'primary' | 'secondary' | 'success' | 'warning' | 'error' } = {
      'processing': 'primary',
      'packaging': 'secondary',
      'testing': 'success',
      'cleaning': 'warning',
      'storage': 'error',
    };
    return colors[type] || 'default';
  };

  const getMaintenanceTypeColor = (type: string) => {
    return type === 'preventive' ? 'success' : 'warning';
  };

  const getWorkOrderStatusColor = (completed: boolean) => {
    return completed ? 'success' : 'warning';
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
    <Box p={3}>
        <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Typography variant="h4" fontWeight="bold" color="primary">
            Equipment Management
          </Typography>
        <Stack direction="row" spacing={1}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setEquipmentDialog(true)}
            >
              Add Equipment
            </Button>
          </Stack>
        </Stack>

        {loading && <LinearProgress sx={{ mb: 2 }} />}

        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="equipment tabs">
              <Tab
                icon={<SettingsIcon />}
                label={
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <span>Equipment</span>
                    <Badge badgeContent={equipment.length} color="primary" />
                  </Stack>
                }
              />
              <Tab
                icon={<ScheduleIcon />}
                label={
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <span>Maintenance Plans</span>
                    <Badge badgeContent={maintenancePlans.length} color="secondary" />
                  </Stack>
                }
              />
              <Tab
                icon={<BuildIcon />}
                label={
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <span>Work Orders</span>
                    <Badge badgeContent={workOrders.filter(wo => !wo.completed_at).length} color="warning" />
                  </Stack>
                }
              />
              <Tab
                icon={<ScienceIcon />}
                label={
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <span>Calibration</span>
                    <Badge badgeContent={calibrationPlans.length} color="info" />
                  </Stack>
                }
              />
              <Tab
                icon={<HistoryIcon />}
                label="History"
              />
            </Tabs>
          </Box>

          {/* Equipment Tab */}
          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              {equipment.map((item) => (
                <Grid item xs={12} md={6} lg={4} key={item.id}>
                  <Card>
                    <CardContent>
                      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                        <Typography variant="h6" fontWeight="bold">
                          {item.name}
                        </Typography>
                        <Chip
                          label={item.equipment_type}
                          color={getEquipmentTypeColor(item.equipment_type)}
                          size="small"
                        />
                      </Stack>
                      <Stack spacing={1}>
                        <Typography variant="body2" color="text.secondary">
                          <strong>Serial:</strong> {item.serial_number || 'N/A'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          <strong>Location:</strong> {item.location || 'N/A'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          <strong>Created:</strong> {new Date(item.created_at).toLocaleDateString()}
                        </Typography>
                        {item.notes && (
                          <Typography variant="body2" color="text.secondary">
                            <strong>Notes:</strong> {item.notes}
                          </Typography>
                        )}
                      </Stack>
                    </CardContent>
                    <CardActions>
                      <Button size="small" startIcon={<ScheduleIcon />} onClick={() => {
                        setMaintenanceForm({ ...maintenanceForm, equipment_id: item.id });
                        setMaintenanceDialog(true);
                      }}>
                        Add Maintenance Plan
                      </Button>
                      <Button size="small" startIcon={<ScienceIcon />} onClick={() => {
                        setCalibrationForm({ ...calibrationForm, equipment_id: item.id });
                        setCalibrationDialog(true);
                      }}>
                        Add Calibration
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </TabPanel>

          {/* Maintenance Plans Tab */}
          <TabPanel value={tabValue} index={1}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6">Maintenance Plans</Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setMaintenanceDialog(true)}
              >
                Add Maintenance Plan
              </Button>
      </Stack>
            <Table>
          <TableHead>
            <TableRow>
                  <TableCell>Equipment</TableCell>
              <TableCell>Type</TableCell>
                  <TableCell>Frequency (Days)</TableCell>
                  <TableCell>Last Maintenance</TableCell>
                  <TableCell>Next Due</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
                {maintenancePlans.map((plan) => (
                  <TableRow key={plan.id}>
                    <TableCell>{plan.equipment_name}</TableCell>
                    <TableCell>
                      <Chip
                        label={plan.maintenance_type}
                        color={getMaintenanceTypeColor(plan.maintenance_type)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{plan.frequency_days}</TableCell>
                    <TableCell>{plan.last_maintenance_date || 'Never'}</TableCell>
                    <TableCell>{plan.next_due_date || 'Not scheduled'}</TableCell>
                    <TableCell>
                      <Chip
                        label={plan.status || 'Active'}
                        color={plan.status === 'overdue' ? 'error' : 'success'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Create Work Order">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setWorkOrderForm({ ...workOrderForm, equipment_id: plan.equipment_id, plan_id: plan.id.toString() });
                            setWorkOrderDialog(true);
                          }}
                        >
                          <BuildIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
          </TabPanel>

          {/* Work Orders Tab */}
          <TabPanel value={tabValue} index={2}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6">Work Orders</Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setWorkOrderDialog(true)}
              >
                Create Work Order
              </Button>
            </Stack>
            <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Equipment</TableCell>
                  <TableCell>Title</TableCell>
              <TableCell>Plan</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Completed</TableCell>
                  <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
                {workOrders.map((wo) => (
                  <TableRow key={wo.id}>
                    <TableCell>{wo.id}</TableCell>
                    <TableCell>{wo.equipment_name}</TableCell>
                    <TableCell>{wo.title}</TableCell>
                    <TableCell>{wo.plan_id || 'Manual'}</TableCell>
                    <TableCell>{new Date(wo.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>{wo.completed_at ? new Date(wo.completed_at).toLocaleDateString() : '-'}</TableCell>
                    <TableCell>
                      <Chip
                        icon={wo.completed_at ? <CheckIcon /> : <WarningIcon />}
                        label={wo.completed_at ? 'Completed' : 'Pending'}
                        color={getWorkOrderStatusColor(!!wo.completed_at)}
                        size="small"
                      />
                    </TableCell>
                <TableCell align="right">
                      {!wo.completed_at && (
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<CheckIcon />}
                          onClick={() => handleCompleteWorkOrder(wo.id)}
                        >
                          Complete
                        </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
          </TabPanel>

          {/* Calibration Tab */}
          <TabPanel value={tabValue} index={3}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6">Calibration Plans</Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setCalibrationDialog(true)}
              >
                Add Calibration Plan
              </Button>
            </Stack>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Equipment</TableCell>
                  <TableCell>Schedule Date</TableCell>
                  <TableCell>Last Calibration</TableCell>
                  <TableCell>Certificate</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {calibrationPlans.map((plan) => (
                  <TableRow key={plan.id}>
                    <TableCell>{plan.equipment_name}</TableCell>
                    <TableCell>{new Date(plan.schedule_date).toLocaleDateString()}</TableCell>
                    <TableCell>{plan.last_calibration_date || 'Never'}</TableCell>
                    <TableCell>
                      {plan.certificate_file ? (
                        <Button size="small" startIcon={<DownloadIcon />}>
                          Download
                        </Button>
                      ) : (
                        <Button
                          size="small"
                          startIcon={<UploadIcon />}
                          onClick={() => {
                            setCertificateForm({ ...certificateForm, plan_id: plan.id });
                            setCertificateDialog(true);
                          }}
                        >
                          Upload
                        </Button>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={plan.status || 'Scheduled'}
                        color={plan.status === 'overdue' ? 'error' : 'success'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Upload Certificate">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setCertificateForm({ ...certificateForm, plan_id: plan.id });
                            setCertificateDialog(true);
                          }}
                        >
                          <UploadIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TabPanel>

          {/* History Tab */}
          <TabPanel value={tabValue} index={4}>
            <Typography variant="h6" sx={{ mb: 2 }}>Maintenance History</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2 }}>Recent Work Orders</Typography>
                    <Stack spacing={2}>
                      {workOrders.slice(0, 5).map((wo) => (
                        <Box key={wo.id} sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                          <Typography variant="subtitle2">{wo.title}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            Equipment: {wo.equipment_name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {wo.completed_at ? `Completed: ${new Date(wo.completed_at).toLocaleDateString()}` : 'Pending'}
                          </Typography>
                        </Box>
                      ))}
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2 }}>Equipment Statistics</Typography>
                    <Stack spacing={2}>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Total Equipment</Typography>
                        <Typography variant="h4">{equipment.length}</Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Pending Work Orders</Typography>
                        <Typography variant="h4" color="warning.main">
                          {workOrders.filter(wo => !wo.completed_at).length}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Completed This Month</Typography>
                        <Typography variant="h4" color="success.main">
                          {workOrders.filter(wo => wo.completed_at && new Date(wo.completed_at).getMonth() === new Date().getMonth()).length}
                        </Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>
      </Paper>

        {/* Equipment Dialog */}
        <Dialog open={equipmentDialog} onClose={() => setEquipmentDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add New Equipment</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                label="Equipment Name"
                value={equipmentForm.name}
                onChange={(e) => setEquipmentForm({ ...equipmentForm, name: e.target.value })}
                fullWidth
                required
              />
              <FormControl fullWidth required>
                <InputLabel>Equipment Type</InputLabel>
                <Select
                  value={equipmentForm.equipment_type}
                  onChange={(e) => setEquipmentForm({ ...equipmentForm, equipment_type: e.target.value })}
                  label="Equipment Type"
                >
                  <MenuItem value="processing">Processing</MenuItem>
                  <MenuItem value="packaging">Packaging</MenuItem>
                  <MenuItem value="testing">Testing</MenuItem>
                  <MenuItem value="cleaning">Cleaning</MenuItem>
                  <MenuItem value="storage">Storage</MenuItem>
                </Select>
              </FormControl>
              <TextField
                label="Serial Number"
                value={equipmentForm.serial_number}
                onChange={(e) => setEquipmentForm({ ...equipmentForm, serial_number: e.target.value })}
                fullWidth
              />
              <TextField
                label="Location"
                value={equipmentForm.location}
                onChange={(e) => setEquipmentForm({ ...equipmentForm, location: e.target.value })}
                fullWidth
              />
              <TextField
                label="Notes"
                value={equipmentForm.notes}
                onChange={(e) => setEquipmentForm({ ...equipmentForm, notes: e.target.value })}
                fullWidth
                multiline
                rows={3}
              />
          </Stack>
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setEquipmentDialog(false)}>Cancel</Button>
            <Button onClick={handleEquipmentSubmit} variant="contained">Add Equipment</Button>
        </DialogActions>
      </Dialog>

        {/* Maintenance Plan Dialog */}
        <Dialog open={maintenanceDialog} onClose={() => setMaintenanceDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add Maintenance Plan</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
              <FormControl fullWidth required>
                <InputLabel>Equipment</InputLabel>
                <Select
                  value={maintenanceForm.equipment_id}
                  onChange={(e) => setMaintenanceForm({ ...maintenanceForm, equipment_id: e.target.value as number })}
                  label="Equipment"
                >
                  {equipment.map((item) => (
                    <MenuItem key={item.id} value={item.id}>{item.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth required>
                <InputLabel>Maintenance Type</InputLabel>
                <Select
                  value={maintenanceForm.maintenance_type}
                  onChange={(e) => setMaintenanceForm({ ...maintenanceForm, maintenance_type: e.target.value })}
                  label="Maintenance Type"
                >
                  <MenuItem value="preventive">Preventive</MenuItem>
                  <MenuItem value="corrective">Corrective</MenuItem>
                </Select>
              </FormControl>
              <TextField
                label="Frequency (Days)"
                type="number"
                value={maintenanceForm.frequency_days}
                onChange={(e) => setMaintenanceForm({ ...maintenanceForm, frequency_days: parseInt(e.target.value) })}
                fullWidth
                required
                InputProps={{
                  endAdornment: <InputAdornment position="end">days</InputAdornment>,
                }}
              />
              <TextField
                label="Notes"
                value={maintenanceForm.notes}
                onChange={(e) => setMaintenanceForm({ ...maintenanceForm, notes: e.target.value })}
                fullWidth
                multiline
                rows={3}
              />
          </Stack>
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setMaintenanceDialog(false)}>Cancel</Button>
            <Button onClick={handleMaintenanceSubmit} variant="contained">Add Plan</Button>
        </DialogActions>
      </Dialog>

        {/* Work Order Dialog */}
        <Dialog open={workOrderDialog} onClose={() => setWorkOrderDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Create Work Order</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
              <FormControl fullWidth required>
                <InputLabel>Equipment</InputLabel>
                <Select
                  value={workOrderForm.equipment_id}
                  onChange={(e) => setWorkOrderForm({ ...workOrderForm, equipment_id: e.target.value as number })}
                  label="Equipment"
                >
                  {equipment.map((item) => (
                    <MenuItem key={item.id} value={item.id}>{item.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                label="Title"
                value={workOrderForm.title}
                onChange={(e) => setWorkOrderForm({ ...workOrderForm, title: e.target.value })}
                fullWidth
                required
              />
              <TextField
                label="Description"
                value={workOrderForm.description}
                onChange={(e) => setWorkOrderForm({ ...workOrderForm, description: e.target.value })}
                fullWidth
                multiline
                rows={3}
              />
          </Stack>
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setWorkOrderDialog(false)}>Cancel</Button>
            <Button onClick={handleWorkOrderSubmit} variant="contained">Create Work Order</Button>
        </DialogActions>
      </Dialog>

        {/* Calibration Dialog */}
        <Dialog open={calibrationDialog} onClose={() => setCalibrationDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add Calibration Plan</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
              <FormControl fullWidth required>
                <InputLabel>Equipment</InputLabel>
                <Select
                  value={calibrationForm.equipment_id}
                  onChange={(e) => setCalibrationForm({ ...calibrationForm, equipment_id: e.target.value as number })}
                  label="Equipment"
                >
                  {equipment.map((item) => (
                    <MenuItem key={item.id} value={item.id}>{item.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <DatePicker
                label="Schedule Date"
                value={calibrationForm.schedule_date}
                onChange={(newValue) => setCalibrationForm({ ...calibrationForm, schedule_date: newValue || new Date() })}
                slotProps={{ textField: { fullWidth: true } }}
              />
              <TextField
                label="Notes"
                value={calibrationForm.notes}
                onChange={(e) => setCalibrationForm({ ...calibrationForm, notes: e.target.value })}
                fullWidth
                multiline
                rows={3}
              />
          </Stack>
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setCalibrationDialog(false)}>Cancel</Button>
            <Button onClick={handleCalibrationSubmit} variant="contained">Add Calibration</Button>
        </DialogActions>
      </Dialog>

        {/* Certificate Upload Dialog */}
        <Dialog open={certificateDialog} onClose={() => setCertificateDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Upload Calibration Certificate</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
              <input
                type="file"
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                onChange={(e) => setCertificateForm({ ...certificateForm, file: e.target.files?.[0] || null })}
                style={{ marginTop: '8px' }}
              />
              <FormHelperText>
                Supported formats: PDF, DOC, DOCX, JPG, JPEG, PNG
              </FormHelperText>
          </Stack>
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setCertificateDialog(false)}>Cancel</Button>
            <Button onClick={handleCertificateUpload} variant="contained" disabled={!certificateForm.file}>
              Upload Certificate
            </Button>
        </DialogActions>
      </Dialog>
    </Box>
    </LocalizationProvider>
  );
};

export default EquipmentPage;


