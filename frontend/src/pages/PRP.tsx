import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Fab,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress,
  CircularProgress,
  Avatar,
} from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';
import { usersAPI } from '../services/api';
import {
  Add,
  Visibility,
  Assignment,
  Warning,
  CheckCircle,
  Refresh,
  Schedule,
  CalendarToday,
  Person,
  Search,
  Notifications,
  CheckBox,
  Edit,
  Delete,
  TrendingUp,
  Assessment,
  Dashboard,
  List as ListIcon,
  ViewList,
  CalendarMonth,
  Work,
  CleaningServices,
  BugReport,
  People,
  DeleteSweep,
  Build,
  School,
  LocalShipping,
  WaterDrop,
  Air,
} from '@mui/icons-material';
import { prpAPI } from '../services/api';
import { useLocation } from 'react-router-dom';

interface PRPProgram {
  id: number;
  program_code: string;
  name: string;
  description?: string;
  category?: string;
  status?: string;
  frequency?: string;
  checklist_count: number;
  overdue_count: number;
  created_by: string;
  next_due_date?: string;
  responsible_person?: string;
  compliance_percentage?: number;
}

interface PRPChecklist {
  id: number;
  checklist_code: string;
  name: string;
  status: string;
  scheduled_date: string;
  due_date: string;
  assigned_to: string;
  compliance_percentage: number;
  total_items: number;
  passed_items: number;
  failed_items: number;
}

const PRP: React.FC = () => {
  const [userSearch, setUserSearch] = useState('');
  type UserOption = { id: number; username: string; full_name?: string };
  const [userOptions, setUserOptions] = useState<Array<UserOption>>([]);
  // Keep selected objects stable to avoid Autocomplete flicker when options refresh
  const [selectedResponsible, setSelectedResponsible] = useState<UserOption | null>(null);
  const [selectedAssignee, setSelectedAssignee] = useState<UserOption | null>(null);
  useEffect(() => {
    let active = true;
    const t = setTimeout(async () => {
      try {
        const resp: any = await usersAPI.getUsers({ page: 1, size: 10, search: userSearch });
        const items = (resp?.data?.items || resp?.items || []) as Array<any>;
        if (active) setUserOptions(items.map((u: any) => ({ id: u.id, username: u.username, full_name: u.full_name })));
        // re-hydrate selected objects from refreshed options to keep Autocomplete stable
        if (active && selectedResponsible) {
          const match = items.find((u: any) => u.id === selectedResponsible.id);
          if (match) setSelectedResponsible({ id: match.id, username: match.username, full_name: match.full_name });
        }
        if (active && selectedAssignee) {
          const match = items.find((u: any) => u.id === selectedAssignee.id);
          if (match) setSelectedAssignee({ id: match.id, username: match.username, full_name: match.full_name });
        }
      } catch {
        if (active) setUserOptions([]);
      }
    }, 300);
    return () => { active = false; clearTimeout(t); };
  }, [userSearch, selectedResponsible, selectedAssignee]);
  const [activeTab, setActiveTab] = useState(0);
  const location = useLocation();
  const [programs, setPrograms] = useState<PRPProgram[]>([]);
  const [checklists, setChecklists] = useState<PRPChecklist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [openProgramDialog, setOpenProgramDialog] = useState(false);
  const [openChecklistDialog, setOpenChecklistDialog] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState<PRPProgram | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  
  const [programForm, setProgramForm] = useState({
    program_code: '',
    name: '',
    description: '',
    category: '',
    frequency: '',
    responsible_person: '',
    objective: '',
    scope: '',
    responsible_department: '',
    sop_reference: '',
  });

  const [checklistForm, setChecklistForm] = useState({
    checklist_code: '',
    name: '',
    description: '',
    scheduled_date: '',
    due_date: '',
    assigned_to: '',
  });

  const [dashboardData, setDashboardData] = useState({
    total_programs: 0,
    active_programs: 0,
    total_checklists: 0,
    pending_checklists: 0,
    overdue_checklists: 0,
    completed_this_month: 0,
    recent_checklists: [],
  });

  const categoryIcons: { [key: string]: React.ReactElement } = {
    cleaning_sanitation: <CleaningServices />,
    pest_control: <BugReport />,
    staff_hygiene: <People />,
    waste_management: <DeleteSweep />,
    equipment_calibration: <Build />,
    maintenance: <Build />,
    personnel_training: <School />,
    supplier_control: <LocalShipping />,
    water_quality: <WaterDrop />,
    air_quality: <Air />,
    transportation: <LocalShipping />,
  };

  const fetchChecklists = useCallback(async () => {
    try {
      // Get all checklists by fetching from each program
      const allChecklists: PRPChecklist[] = [];
      for (const program of programs) {
        try {
          const response = await prpAPI.getChecklists(program.id, { page: 1, size: 50 });
          if (response.success && response.data.items) {
            allChecklists.push(...response.data.items);
          }
        } catch (err) {
          console.error(`Failed to load checklists for program ${program.id}:`, err);
        }
      }
      setChecklists(allChecklists);
    } catch (err: any) {
      console.error('Failed to load checklists:', err);
    }
  }, [programs]);

  const fetchPrograms = async () => {
    try {
      setLoading(true);
      console.log('Fetching PRP programs...');
      const response = await prpAPI.getPrograms();
      console.log('PRP programs response:', response);
      if (response.success) {
        setPrograms(response.data.items || []);
        console.log('Programs loaded:', response.data.items?.length || 0);
      } else {
        console.error('Failed to load programs:', response.message);
        setError(response.message || 'Failed to load programs');
      }
    } catch (err: any) {
      console.error('Error fetching programs:', err);
      setError(err.message || 'Failed to load programs');
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboard = async () => {
    try {
      const response = await prpAPI.getDashboard();
      if (response.success) {
        setDashboardData(response.data);
      }
    } catch (err: any) {
      console.error('Dashboard error:', err);
    }
  };

  useEffect(() => {
    fetchPrograms();
    fetchDashboard();
  }, []);

  // Read ?category= and ?tab= to prime filters and tab
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const category = params.get('category');
    const tab = params.get('tab');
    if (category) {
      setFilterCategory(category);
    }
    if (tab === 'programs') {
      setActiveTab(1);
    } else if (tab === 'checklists') {
      setActiveTab(2);
    } else if (tab === 'overview') {
      setActiveTab(0);
    }
  }, [location.search]);

  // Fetch checklists after programs are loaded
  useEffect(() => {
    if (programs.length > 0) {
      fetchChecklists();
    }
  }, [programs, fetchChecklists]);

  const handleCreateProgram = async () => {
    try {
      const response = await prpAPI.createProgram(programForm);
      if (response.success) {
        setSuccess('PRP program created successfully');
        setOpenProgramDialog(false);
        setProgramForm({
          program_code: '',
          name: '',
          description: '',
          category: '',
          frequency: '',
          responsible_person: '',
          objective: '',
          scope: '',
          responsible_department: '',
          sop_reference: '',
        });
        setSelectedResponsible(null);
        fetchPrograms();
        fetchDashboard();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create program');
    }
  };

  const handleCreateChecklist = async () => {
    if (!selectedProgram) return;
    
    try {
      const response = await prpAPI.createChecklist(selectedProgram.id, checklistForm);
      if (response.success) {
        setSuccess('Checklist created successfully');
        setOpenChecklistDialog(false);
        setChecklistForm({
          checklist_code: '',
          name: '',
          description: '',
          scheduled_date: '',
          due_date: '',
          assigned_to: '',
        });
        setSelectedAssignee(null);
        fetchChecklists();
        fetchDashboard();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create checklist');
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'suspended': return 'warning';
      case 'completed': return 'success';
      case 'pending': return 'warning';
      case 'in_progress': return 'info';
      case 'overdue': return 'error';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getCategoryColor = (category?: string) => {
    switch (category?.toLowerCase()) {
      case 'cleaning_sanitation': return 'primary';
      case 'pest_control': return 'secondary';
      case 'staff_hygiene': return 'success';
      case 'waste_management': return 'warning';
      case 'equipment_calibration': return 'info';
      case 'maintenance': return 'info';
      case 'personnel_training': return 'success';
      case 'supplier_control': return 'primary';
      case 'water_quality': return 'info';
      case 'air_quality': return 'info';
      case 'transportation': return 'primary';
      default: return 'default';
    }
  };

  const getCategoryDisplayName = (category?: string) => {
    return category?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
  };

  const filteredPrograms = programs.filter(program => {
    const matchesSearch = !searchTerm || 
      program.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      program.program_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      program.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = !filterCategory || program.category === filterCategory;
    const matchesStatus = !filterStatus || program.status === filterStatus;
    
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const filteredChecklists = checklists.filter(checklist => {
    const matchesSearch = !searchTerm || 
      checklist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      checklist.checklist_code.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = !filterStatus || checklist.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  const renderDashboard = () => (
    <Grid container spacing={3} mb={3}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Programs
                </Typography>
                <Typography variant="h4">
                  {dashboardData.total_programs}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {dashboardData.active_programs} active
                </Typography>
              </Box>
              <Assignment color="primary" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Checklists
                </Typography>
                <Typography variant="h4">
                  {dashboardData.total_checklists}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {dashboardData.completed_this_month} completed this month
                </Typography>
              </Box>
              <CheckBox color="success" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Pending
                </Typography>
                <Typography variant="h4">
                  {dashboardData.pending_checklists}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Awaiting completion
                </Typography>
              </Box>
              <Schedule color="warning" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Overdue
                </Typography>
                <Typography variant="h4">
                  {dashboardData.overdue_checklists}
                </Typography>
                <Typography variant="body2" color="error">
                  Requires attention
                </Typography>
              </Box>
              <Warning color="error" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderProgramsList = () => (
    <Paper>
      <Box p={2}>
        <Grid container spacing={2} alignItems="center" mb={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search programs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={filterCategory}
                label="Category"
                onChange={(e) => setFilterCategory(e.target.value)}
              >
                <MenuItem value="">All Categories</MenuItem>
                <MenuItem value="cleaning_sanitation">Cleaning & Sanitation</MenuItem>
                <MenuItem value="pest_control">Pest Control</MenuItem>
                <MenuItem value="staff_hygiene">Staff Hygiene</MenuItem>
                <MenuItem value="waste_management">Waste Management</MenuItem>
                <MenuItem value="equipment_calibration">Equipment Calibration</MenuItem>
                <MenuItem value="maintenance">Maintenance</MenuItem>
                <MenuItem value="personnel_training">Personnel Training</MenuItem>
                <MenuItem value="supplier_control">Supplier Control</MenuItem>
                <MenuItem value="water_quality">Water Quality</MenuItem>
                <MenuItem value="air_quality">Air Quality</MenuItem>
                <MenuItem value="transportation">Transportation</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                label="Status"
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
                <MenuItem value="suspended">Suspended</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Refresh />}
              onClick={() => {
                setSearchTerm('');
                setFilterCategory('');
                setFilterStatus('');
                fetchPrograms();
              }}
            >
              Reset
            </Button>
          </Grid>
        </Grid>
      </Box>
      
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Program</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Frequency</TableCell>
              <TableCell>Next Due</TableCell>
              <TableCell>Checklists</TableCell>
              <TableCell>Responsible</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <LinearProgress />
                  <Typography sx={{ mt: 1 }}>Loading programs...</Typography>
                </TableCell>
              </TableRow>
            ) : filteredPrograms.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No PRP programs found
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={() => setOpenProgramDialog(true)}
                    sx={{ mt: 2 }}
                  >
                    Create First Program
                  </Button>
                </TableCell>
              </TableRow>
            ) : (
              filteredPrograms.map((program) => (
                <TableRow key={program.id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {program.program_code}
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {program.name}
                      </Typography>
                      {program.description && (
                        <Typography variant="caption" color="text.secondary">
                          {program.description.substring(0, 60)}...
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      icon={categoryIcons[program.category || '']}
                      label={getCategoryDisplayName(program.category || '')}
                      color={getCategoryColor(program.category) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={program.status?.toUpperCase() || 'UNKNOWN'}
                      color={getStatusColor(program.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={program.frequency?.toUpperCase() || 'UNKNOWN'}
                      color="primary"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {program.next_due_date ? (
                      <Typography variant="body2">
                        {new Date(program.next_due_date).toLocaleDateString()}
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        Not scheduled
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2">
                        {program.checklist_count} total
                      </Typography>
                      {program.overdue_count > 0 && (
                        <Chip
                          label={`${program.overdue_count} overdue`}
                          color="error"
                          size="small"
                        />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                        {program.responsible_person?.charAt(0) || 'U'}
                      </Avatar> 
                      <Typography variant="body2">
                        {program.responsible_person || 'Unassigned'}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Box display="flex" gap={1}>
                      <Tooltip title="View Details">
                        <IconButton size="small">
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Create Checklist">
                        <IconButton 
                          size="small"
                          onClick={() => {
                            setSelectedProgram(program);
                            setOpenChecklistDialog(true);
                          }}
                        >
                          <Add />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );

  const renderChecklistsList = () => (
    <Paper>
      <Box p={2}>
        <Grid container spacing={2} alignItems="center" mb={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search checklists..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                label="Status"
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="overdue">Overdue</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Refresh />}
              onClick={() => {
                setSearchTerm('');
                setFilterStatus('');
                fetchChecklists();
              }}
            >
              Reset
            </Button>
          </Grid>
        </Grid>
      </Box>
      
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Checklist</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Scheduled</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell>Assigned To</TableCell>
              <TableCell>Progress</TableCell>
              <TableCell>Compliance</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredChecklists.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No checklists found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredChecklists.map((checklist) => (
                <TableRow key={checklist.id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {checklist.checklist_code}
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {checklist.name}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={checklist.status?.toUpperCase()}
                      color={getStatusColor(checklist.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {new Date(checklist.scheduled_date).toLocaleDateString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography 
                      variant="body2" 
                      color={new Date(checklist.due_date) < new Date() ? 'error' : 'inherit'}
                    >
                      {new Date(checklist.due_date).toLocaleDateString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                        {checklist.assigned_to?.charAt(0) || 'U'}
                      </Avatar>
                      <Typography variant="body2">
                        {checklist.assigned_to || 'Unassigned'}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2">
                        {checklist.passed_items}/{checklist.total_items}
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={(checklist.passed_items / checklist.total_items) * 100}
                        sx={{ width: 60 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="bold">
                      {checklist.compliance_percentage}%
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Box display="flex" gap={1}>
                      <Tooltip title="View Details">
                        <IconButton size="small">
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Prerequisite Programs (PRP)
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage and monitor prerequisite programs for food safety compliance
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenProgramDialog(true)}
          size="large"
        >
          New Program
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {renderDashboard()}

      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={(e, newValue) => setActiveTab(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab 
            icon={<Dashboard />} 
            label="Overview" 
            iconPosition="start"
          />
          <Tab 
            icon={<ListIcon />} 
            label="Programs" 
            iconPosition="start"
          />
          <Tab 
            icon={<CheckBox />} 
            label="Checklists" 
            iconPosition="start"
          />
          <Tab 
            icon={<CalendarMonth />} 
            label="Schedule" 
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      {/* Show loading state or content */}
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <Box textAlign="center">
            <CircularProgress size={60} />
            <Typography variant="h6" sx={{ mt: 2 }}>
              Loading PRP Programs...
            </Typography>
          </Box>
        </Box>
      ) : (
        <>
          {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                <List>
                  {dashboardData.recent_checklists?.map((checklist: any, index: number) => (
                    <ListItem key={index} divider>
                      <ListItemIcon>
                        <CheckBox color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={checklist.name}
                        secondary={`Due: ${new Date(checklist.due_date).toLocaleDateString()} • Compliance: ${checklist.compliance_percentage}%`}
                      />
                      <Chip
                        label={checklist.status?.toUpperCase()}
                        color={getStatusColor(checklist.status) as any}
                        size="small"
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Box display="flex" flexDirection="column" gap={2}>
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={() => setOpenProgramDialog(true)}
                    fullWidth
                  >
                    Create New Program
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<CheckBox />}
                    onClick={() => setActiveTab(2)}
                    fullWidth
                  >
                    View All Checklists
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<CalendarToday />}
                    onClick={() => setActiveTab(3)}
                    fullWidth
                  >
                    View Schedule
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Assessment />}
                    fullWidth
                  >
                    Generate Reports
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
        </>
      )}

      {activeTab === 1 && renderProgramsList()}
      {activeTab === 2 && renderChecklistsList()}
      {activeTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              PRP Schedule
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Calendar view and scheduling features coming soon...
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Create Program Dialog */}
      <Dialog open={openProgramDialog} onClose={() => setOpenProgramDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New PRP Program</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} pt={1}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Program Code"
                  fullWidth
                  value={programForm.program_code}
                  onChange={(e) => setProgramForm({ ...programForm, program_code: e.target.value })}
                  required
                  helperText="Unique identifier for the program"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Program Name"
                  fullWidth
                  value={programForm.name}
                  onChange={(e) => setProgramForm({ ...programForm, name: e.target.value })}
                  required
                />
              </Grid>
            </Grid>
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={programForm.description}
              onChange={(e) => setProgramForm({ ...programForm, description: e.target.value })}
              helperText="Brief description of the program's purpose and scope"
            />
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={programForm.category}
                    label="Category"
                    onChange={(e) => setProgramForm({ ...programForm, category: e.target.value })}
                  >
                    <MenuItem value="cleaning_sanitation">Cleaning & Sanitation</MenuItem>
                    <MenuItem value="pest_control">Pest Control</MenuItem>
                    <MenuItem value="staff_hygiene">Staff Hygiene</MenuItem>
                    <MenuItem value="waste_management">Waste Management</MenuItem>
                    <MenuItem value="equipment_calibration">Equipment Calibration</MenuItem>
                    <MenuItem value="maintenance">Maintenance</MenuItem>
                    <MenuItem value="personnel_training">Personnel Training</MenuItem>
                    <MenuItem value="supplier_control">Supplier Control</MenuItem>
                    <MenuItem value="water_quality">Water Quality</MenuItem>
                    <MenuItem value="air_quality">Air Quality</MenuItem>
                    <MenuItem value="transportation">Transportation</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Frequency</InputLabel>
                  <Select
                    value={programForm.frequency}
                    label="Frequency"
                    onChange={(e) => setProgramForm({ ...programForm, frequency: e.target.value })}
                  >
                    <MenuItem value="daily">Daily</MenuItem>
                    <MenuItem value="weekly">Weekly</MenuItem>
                    <MenuItem value="monthly">Monthly</MenuItem>
                    <MenuItem value="quarterly">Quarterly</MenuItem>
                    <MenuItem value="semi_annually">Semi-Annually</MenuItem>
                    <MenuItem value="annually">Annually</MenuItem>
                    <MenuItem value="as_needed">As Needed</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Responsible Department"
                  fullWidth
                  value={programForm.responsible_department}
                  onChange={(e) => setProgramForm({ ...programForm, responsible_department: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Autocomplete
                  options={userOptions}
                  getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                  value={selectedResponsible}
                  onChange={(_, val) => {
                    setSelectedResponsible(val);
                    setProgramForm({ ...programForm, responsible_person: val ? (val.full_name || val.username) : '' });
                  }}
                  onInputChange={(_, val, reason) => {
                    if (reason === 'input') setUserSearch(val);
                  }}
                  isOptionEqualToValue={(opt, val) => opt.id === val.id}
                  renderInput={(params) => <TextField {...params} label="Responsible Person" placeholder="Search user..." fullWidth />}
                />
              </Grid>
            </Grid>
            <TextField
              label="Objective"
              fullWidth
              multiline
              rows={2}
              value={programForm.objective}
              onChange={(e) => setProgramForm({ ...programForm, objective: e.target.value })}
              helperText="What this program aims to achieve"
            />
            <TextField
              label="Scope"
              fullWidth
              multiline
              rows={2}
              value={programForm.scope}
              onChange={(e) => setProgramForm({ ...programForm, scope: e.target.value })}
              helperText="Areas and processes covered by this program"
            />
            <TextField
              label="SOP Reference"
              fullWidth
              value={programForm.sop_reference}
              onChange={(e) => setProgramForm({ ...programForm, sop_reference: e.target.value })}
              helperText="Reference to related Standard Operating Procedure"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenProgramDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateProgram} variant="contained">
            Create Program
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Checklist Dialog */}
      <Dialog open={openChecklistDialog} onClose={() => setOpenChecklistDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Create New Checklist
          {selectedProgram && (
            <Typography variant="body2" color="text.secondary">
              for {selectedProgram.name}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} pt={1}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Checklist Code"
                  fullWidth
                  value={checklistForm.checklist_code}
                  onChange={(e) => setChecklistForm({ ...checklistForm, checklist_code: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Checklist Name"
                  fullWidth
                  value={checklistForm.name}
                  onChange={(e) => setChecklistForm({ ...checklistForm, name: e.target.value })}
                  required
                />
              </Grid>
            </Grid>
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={checklistForm.description}
              onChange={(e) => setChecklistForm({ ...checklistForm, description: e.target.value })}
            />
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Scheduled Date"
                  type="date"
                  fullWidth
                  value={checklistForm.scheduled_date}
                  onChange={(e) => setChecklistForm({ ...checklistForm, scheduled_date: e.target.value })}
                  required
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Due Date"
                  type="date"
                  fullWidth
                  value={checklistForm.due_date}
                  onChange={(e) => setChecklistForm({ ...checklistForm, due_date: e.target.value })}
                  required
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
            <Autocomplete
              options={userOptions}
              getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
              value={selectedAssignee}
              onChange={(_, val) => {
                setSelectedAssignee(val);
                setChecklistForm({ ...checklistForm, assigned_to: val ? (val.full_name || val.username) : '' });
              }}
              onInputChange={(_, val, reason) => {
                if (reason === 'input') setUserSearch(val);
              }}
              isOptionEqualToValue={(opt, val) => opt.id === val.id}
              renderInput={(params) => <TextField {...params} label="Assigned To" placeholder="Search user..." fullWidth helperText="Person responsible for completing this checklist" />}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenChecklistDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateChecklist} variant="contained">
            Create Checklist
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button for Mobile */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setOpenProgramDialog(true)}
      >
        <Add />
      </Fab>
    </Box>
  );
};

export default PRP; 