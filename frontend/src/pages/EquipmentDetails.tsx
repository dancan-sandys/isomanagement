import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
  Breadcrumbs,
  Link,
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
  Verified as VerifiedIcon,
  ArrowBack as ArrowBackIcon,
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

const EquipmentDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [equipment, setEquipment] = useState<any>(null);
  const [maintenancePlans, setMaintenancePlans] = useState<any[]>([]);
  const [workOrders, setWorkOrders] = useState<any[]>([]);
  const [calibrationPlans, setCalibrationPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Maintenance Plan Dialog
  const [maintenanceDialog, setMaintenanceDialog] = useState(false);
  const [maintenanceForm, setMaintenanceForm] = useState({
    frequency_days: 30,
    maintenance_type: 'preventive' as 'preventive' | 'corrective',
    notes: '',
  });

  // Work Order Dialog
  const [workOrderDialog, setWorkOrderDialog] = useState(false);
  const [workOrderForm, setWorkOrderForm] = useState({
    plan_id: '',
    title: '',
    description: '',
  });

  // Calibration Dialog
  const [calibrationDialog, setCalibrationDialog] = useState(false);
  const [calibrationForm, setCalibrationForm] = useState({
    schedule_date: new Date(),
    frequency_days: 365,
    notes: '',
  });

  const loadData = async () => {
    if (!id) return;
    
    setLoading(true);
    try {
      // Load equipment details
      const equipmentData = await equipmentAPI.get(parseInt(id));
      setEquipment(equipmentData);

      // Load maintenance plans for this equipment
      const maintenanceData = await equipmentAPI.listMaintenancePlans(parseInt(id));
      setMaintenancePlans(maintenanceData || []);

      // Load work orders for this equipment
      const workOrdersData = await equipmentAPI.listWorkOrders(parseInt(id));
      setWorkOrders(workOrdersData || []);

      // Load calibration plans for this equipment
      const calibrationData = await equipmentAPI.listCalibrationPlans(parseInt(id));
      setCalibrationPlans(calibrationData || []);

    } catch (error) {
      console.error('Error loading equipment details:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleMaintenanceSubmit = async () => {
    try {
      await equipmentAPI.createMaintenancePlan(parseInt(id!), maintenanceForm);
      setMaintenanceDialog(false);
      setMaintenanceForm({ frequency_days: 30, maintenance_type: 'preventive', notes: '' });
      loadData();
    } catch (error) {
      console.error('Error creating maintenance plan:', error);
    }
  };

  const handleWorkOrderSubmit = async () => {
    try {
      await equipmentAPI.createWorkOrder({
        equipment_id: parseInt(id!),
        plan_id: workOrderForm.plan_id ? parseInt(workOrderForm.plan_id) : undefined,
        title: workOrderForm.title,
        description: workOrderForm.description,
      });
      setWorkOrderDialog(false);
      setWorkOrderForm({ plan_id: '', title: '', description: '' });
      loadData();
    } catch (error) {
      console.error('Error creating work order:', error);
    }
  };

  const handleCalibrationSubmit = async () => {
    try {
      await equipmentAPI.createCalibrationPlan(parseInt(id!), {
        schedule_date: calibrationForm.schedule_date.toISOString().split('T')[0],
        frequency_days: calibrationForm.frequency_days,
        notes: calibrationForm.notes,
      });
      setCalibrationDialog(false);
      setCalibrationForm({ schedule_date: new Date(), frequency_days: 365, notes: '' });
      loadData();
    } catch (error) {
      console.error('Error creating calibration plan:', error);
    }
  };

  if (!equipment) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography>Loading equipment details...</Typography>
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 3 }}>
        {/* Breadcrumbs */}
        <Breadcrumbs sx={{ mb: 3 }}>
          <Link
            component="button"
            variant="body1"
            onClick={() => navigate('/maintenance/equipment')}
            sx={{ display: 'flex', alignItems: 'center' }}
          >
            <ArrowBackIcon sx={{ mr: 1 }} />
            Equipment
          </Link>
          <Typography color="text.primary">{equipment.name}</Typography>
        </Breadcrumbs>

        {/* Equipment Header */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
            <Box>
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                {equipment.name}
              </Typography>
              <Stack direction="row" spacing={2} alignItems="center">
                <Chip
                  label={equipment.equipment_type}
                  color="primary"
                  size="small"
                />
                <Typography variant="body2" color="text.secondary">
                  Serial: {equipment.serial_number || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Location: {equipment.location || 'N/A'}
                </Typography>
              </Stack>
            </Box>
          </Stack>
          {equipment.notes && (
            <Typography variant="body2" color="text.secondary">
              <strong>Notes:</strong> {equipment.notes}
            </Typography>
          )}
        </Paper>

        {loading && <LinearProgress sx={{ mb: 2 }} />}

        {/* Tabs */}
        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="equipment details tabs">
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
            </Tabs>
          </Box>

          {/* Maintenance Plans Tab */}
          <TabPanel value={tabValue} index={0}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6">Maintenance Plans</Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setMaintenanceDialog(true)}
              >
                Add Maintenance Plan
              </Button>
            </Stack>
            
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Type</TableCell>
                  <TableCell>Frequency (days)</TableCell>
                  <TableCell>Next Due</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {maintenancePlans.map((plan) => (
                  <TableRow key={plan.id}>
                    <TableCell>{plan.maintenance_type}</TableCell>
                    <TableCell>{plan.frequency_days}</TableCell>
                    <TableCell>
                      {plan.next_due_at ? new Date(plan.next_due_at).toLocaleDateString() : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={plan.status || 'Active'}
                        color={plan.status === 'overdue' ? 'error' : 'success'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <EditIcon />
                      </IconButton>
                      <IconButton size="small">
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
                {maintenancePlans.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      No maintenance plans found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TabPanel>

          {/* Work Orders Tab */}
          <TabPanel value={tabValue} index={1}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6">Work Orders</Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setWorkOrderDialog(true)}
              >
                Add Work Order
              </Button>
            </Stack>
            
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Due Date</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {workOrders.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell>{order.title}</TableCell>
                    <TableCell>
                      <Chip
                        label={order.status || 'Pending'}
                        color={order.completed_at ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {order.due_date ? new Date(order.due_date).toLocaleDateString() : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <EditIcon />
                      </IconButton>
                      <IconButton size="small">
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
                {workOrders.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      No work orders found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TabPanel>

          {/* Calibration Tab */}
          <TabPanel value={tabValue} index={2}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6">Calibration Plans</Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setCalibrationDialog(true)}
              >
                Add Calibration Plan
              </Button>
            </Stack>
            
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Schedule Date</TableCell>
                  <TableCell>Frequency (days)</TableCell>
                  <TableCell>Next Due</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {calibrationPlans.map((plan) => (
                  <TableRow key={plan.id}>
                    <TableCell>
                      {plan.schedule_date ? new Date(plan.schedule_date).toLocaleDateString() : 'N/A'}
                    </TableCell>
                    <TableCell>{plan.frequency_days}</TableCell>
                    <TableCell>
                      {plan.next_due_at ? new Date(plan.next_due_at).toLocaleDateString() : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <EditIcon />
                      </IconButton>
                      <IconButton size="small">
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
                {calibrationPlans.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      No calibration plans found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TabPanel>
        </Paper>

        {/* Maintenance Plan Dialog */}
        <Dialog open={maintenanceDialog} onClose={() => setMaintenanceDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add Maintenance Plan</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ mt: 1 }}>
              <FormControl fullWidth>
                <InputLabel>Maintenance Type</InputLabel>
                <Select
                  value={maintenanceForm.maintenance_type}
                  onChange={(e) => setMaintenanceForm({ ...maintenanceForm, maintenance_type: e.target.value as 'preventive' | 'corrective' })}
                  label="Maintenance Type"
                >
                  <MenuItem value="preventive">Preventive</MenuItem>
                  <MenuItem value="corrective">Corrective</MenuItem>
                </Select>
              </FormControl>
              <TextField
                label="Frequency (days)"
                type="number"
                value={maintenanceForm.frequency_days}
                onChange={(e) => setMaintenanceForm({ ...maintenanceForm, frequency_days: parseInt(e.target.value) })}
                fullWidth
              />
              <TextField
                label="Notes"
                multiline
                rows={3}
                value={maintenanceForm.notes}
                onChange={(e) => setMaintenanceForm({ ...maintenanceForm, notes: e.target.value })}
                fullWidth
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
          <DialogTitle>Add Work Order</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                label="Title"
                value={workOrderForm.title}
                onChange={(e) => setWorkOrderForm({ ...workOrderForm, title: e.target.value })}
                fullWidth
              />
              <TextField
                label="Description"
                multiline
                rows={3}
                value={workOrderForm.description}
                onChange={(e) => setWorkOrderForm({ ...workOrderForm, description: e.target.value })}
                fullWidth
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setWorkOrderDialog(false)}>Cancel</Button>
            <Button onClick={handleWorkOrderSubmit} variant="contained">Add Work Order</Button>
          </DialogActions>
        </Dialog>

        {/* Calibration Dialog */}
        <Dialog open={calibrationDialog} onClose={() => setCalibrationDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add Calibration Plan</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ mt: 1 }}>
              <DatePicker
                label="Schedule Date"
                value={calibrationForm.schedule_date}
                onChange={(newValue) => setCalibrationForm({ ...calibrationForm, schedule_date: newValue || new Date() })}
              />
              <TextField
                label="Frequency (days)"
                type="number"
                value={calibrationForm.frequency_days}
                onChange={(e) => setCalibrationForm({ ...calibrationForm, frequency_days: parseInt(e.target.value) })}
                fullWidth
              />
              <TextField
                label="Notes"
                multiline
                rows={3}
                value={calibrationForm.notes}
                onChange={(e) => setCalibrationForm({ ...calibrationForm, notes: e.target.value })}
                fullWidth
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCalibrationDialog(false)}>Cancel</Button>
            <Button onClick={handleCalibrationSubmit} variant="contained">Add Calibration Plan</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};

export default EquipmentDetailsPage;
