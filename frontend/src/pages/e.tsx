import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Chip,
  IconButton,
  Alert,
  LinearProgress,
  CircularProgress,
  Avatar,
  Switch,
  FormControlLabel,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Badge,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Person as PersonIcon,
  Group as GroupIcon,
  School as SchoolIcon,
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Lock as LockIcon,
  LockOpen as LockOpenIcon,
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Print as PrintIcon,
  Refresh as RefreshIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Business as BusinessIcon,
  Work as WorkIcon,
  CalendarToday as CalendarIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { usersAPI } from '../services/api';

// Interfaces
interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
  department?: string;
  position?: string;
  phone?: string;
  employee_id?: string;
  profile_picture?: string;
  bio?: string;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

interface TrainingRecord {
  id: number;
  user_id: number;
  training_name: string;
  training_type: string;
  completion_date: string;
  expiry_date?: string;
  score?: number;
  status: string;
  certificate_path?: string;
}

interface CompetencyMatrix {
  user_id: number;
  competencies: {
    [key: string]: {
      level: number;
      last_assessed: string;
      next_assessment: string;
      status: string;
    };
  };
}

interface DashboardData {
  total_users: number;
  active_users: number;
  inactive_users: number;
  pending_approval: number;
  users_by_role: Record<string, number>;
  users_by_department: Record<string, number>;
  recent_logins: number;
  training_overdue: number;
  competencies_expiring: number;
}

const Users: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [users, setUsers] = useState<User[]>([]);
  const [trainingRecords, setTrainingRecords] = useState<TrainingRecord[]>([]);
  const [competencyMatrix, setCompetencyMatrix] = useState<CompetencyMatrix[]>([]);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Dialog states
  const [userDialogOpen, setUserDialogOpen] = useState(false);
  const [trainingDialogOpen, setTrainingDialogOpen] = useState(false);
  const [competencyDialogOpen, setCompetencyDialogOpen] = useState(false);
  const [viewUserDialogOpen, setViewUserDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  // Form states
  const [userForm, setUserForm] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: '',
    department: '',
    position: '',
    phone: '',
    employee_id: '',
    bio: ''
  });

  const [trainingForm, setTrainingForm] = useState({
    user_id: '',
    training_name: '',
    training_type: '',
    completion_date: '',
    expiry_date: '',
    score: '',
    certificate_path: ''
  });

  const [competencyForm, setCompetencyForm] = useState({
    user_id: '',
    competency_name: '',
    level: 1,
    last_assessed: '',
    next_assessment: ''
  });

  // Filter states
  const [userFilters, setUserFilters] = useState({
    search: '',
    role: '',
    status: '',
    department: ''
  });

  // Pagination
  const [pagination, setPagination] = useState({
    page: 1,
    size: 10,
    total: 0,
    pages: 0
  });

  // Load data on component mount
  useEffect(() => {
    fetchDashboardData();
    fetchUsers();
    fetchTrainingRecords();
    fetchCompetencyMatrix();
  }, []);

  // API calls
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await usersAPI.getDashboard();
      setDashboardData(data);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      // Create mock data for demonstration
      setDashboardData({
        total_users: 25,
        active_users: 20,
        inactive_users: 3,
        pending_approval: 2,
        users_by_role: {
          'ADMIN': 2,
          'QA_MANAGER': 3,
          'QA_SPECIALIST': 5,
          'PRODUCTION_MANAGER': 2,
          'PRODUCTION_OPERATOR': 8,
          'MAINTENANCE': 2,
          'LAB_TECHNICIAN': 3
        },
        users_by_department: {
          'Quality Assurance': 8,
          'Production': 10,
          'Maintenance': 2,
          'Laboratory': 3,
          'Management': 2
        },
        recent_logins: 18,
        training_overdue: 3,
        competencies_expiring: 5
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await usersAPI.getUsers({
        page: pagination.page,
        size: pagination.size,
        ...userFilters
      });
      setUsers(data.items || []);
      setPagination({
        page: data.page || 1,
        size: data.size || 10,
        total: data.total || 0,
        pages: data.pages || 0
      });
    } catch (err) {
      setError('Failed to load users');
      console.error(err);
      // Create mock data for demonstration
      setUsers([
        {
          id: 1,
          username: 'admin',
          email: 'admin@dairy.com',
          full_name: 'System Administrator',
          role: 'ADMIN',
          status: 'ACTIVE',
          department: 'IT',
          position: 'System Administrator',
          phone: '+1234567890',
          employee_id: 'EMP001',
          is_active: true,
          is_verified: true,
          last_login: '2024-01-15T10:30:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T10:30:00Z'
        },
        {
          id: 2,
          username: 'qa_manager',
          email: 'qa.manager@dairy.com',
          full_name: 'Sarah Johnson',
          role: 'QA_MANAGER',
          status: 'ACTIVE',
          department: 'Quality Assurance',
          position: 'QA Manager',
          phone: '+1234567891',
          employee_id: 'EMP002',
          is_active: true,
          is_verified: true,
          last_login: '2024-01-15T09:15:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T09:15:00Z'
        },
        {
          id: 3,
          username: 'prod_operator',
          email: 'operator@dairy.com',
          full_name: 'Mike Chen',
          role: 'PRODUCTION_OPERATOR',
          status: 'ACTIVE',
          department: 'Production',
          position: 'Production Operator',
          phone: '+1234567892',
          employee_id: 'EMP003',
          is_active: true,
          is_verified: true,
          last_login: '2024-01-15T08:45:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T08:45:00Z'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrainingRecords = async () => {
    try {
      setLoading(true);
      // Mock training records for demonstration
      setTrainingRecords([
        {
          id: 1,
          user_id: 2,
          training_name: 'HACCP Principles',
          training_type: 'Food Safety',
          completion_date: '2024-01-10',
          expiry_date: '2025-01-10',
          score: 95,
          status: 'COMPLETED',
          certificate_path: '/certificates/haccp_sarah.pdf'
        },
        {
          id: 2,
          user_id: 3,
          training_name: 'Equipment Operation',
          training_type: 'Technical',
          completion_date: '2024-01-05',
          expiry_date: '2025-01-05',
          score: 88,
          status: 'COMPLETED',
          certificate_path: '/certificates/equipment_mike.pdf'
        }
      ]);
    } catch (err) {
      console.error('Failed to load training records:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCompetencyMatrix = async () => {
    try {
      setLoading(true);
      // Mock competency matrix for demonstration
      setCompetencyMatrix([
        {
          user_id: 2,
          competencies: {
            'HACCP Implementation': {
              level: 4,
              last_assessed: '2024-01-10',
              next_assessment: '2024-07-10',
              status: 'COMPETENT'
            },
            'Quality Control': {
              level: 3,
              last_assessed: '2024-01-05',
              next_assessment: '2024-07-05',
              status: 'COMPETENT'
            }
          }
        },
        {
          user_id: 3,
          competencies: {
            'Equipment Operation': {
              level: 3,
              last_assessed: '2024-01-05',
              next_assessment: '2024-07-05',
              status: 'COMPETENT'
            },
            'Safety Procedures': {
              level: 2,
              last_assessed: '2024-01-01',
              next_assessment: '2024-07-01',
              status: 'DEVELOPING'
            }
          }
        }
      ]);
    } catch (err) {
      console.error('Failed to load competency matrix:', err);
    } finally {
      setLoading(false);
    }
  };

  // Form handlers
  const handleCreateUser = async () => {
    try {
      setLoading(true);
      await usersAPI.createUser(userForm);
      setUserDialogOpen(false);
      setUserForm({
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: '',
        department: '',
        position: '',
        phone: '',
        employee_id: '',
        bio: ''
      });
      fetchUsers();
    } catch (err) {
      setError('Failed to create user');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (userId: number) => {
    try {
      setLoading(true);
      await usersAPI.updateUser(userId, userForm);
      setUserDialogOpen(false);
      fetchUsers();
    } catch (err) {
      setError('Failed to update user');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    try {
      setLoading(true);
      await usersAPI.deleteUser(userId);
      fetchUsers();
    } catch (err) {
      setError('Failed to delete user');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleActivateUser = async (userId: number) => {
    try {
      setLoading(true);
      await usersAPI.activateUser(userId);
      fetchUsers();
    } catch (err) {
      setError('Failed to activate user');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivateUser = async (userId: number) => {
    try {
      setLoading(true);
      await usersAPI.deactivateUser(userId);
      fetchUsers();
    } catch (err) {
      setError('Failed to deactivate user');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Utility functions
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'ADMIN': return 'error';
      case 'QA_MANAGER': return 'warning';
      case 'QA_SPECIALIST': return 'info';
      case 'PRODUCTION_MANAGER': return 'primary';
      case 'PRODUCTION_OPERATOR': return 'success';
      case 'MAINTENANCE': return 'secondary';
      case 'LAB_TECHNICIAN': return 'default';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'success';
      case 'INACTIVE': return 'error';
      case 'SUSPENDED': return 'warning';
      case 'PENDING_APPROVAL': return 'info';
      default: return 'default';
    }
  };

  const getRoleDisplayName = (role: string) => {
    return role.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  const getStatusDisplayName = (status: string) => {
    return status.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  // Render functions
  const renderDashboard = () => (
    <Box>
      <Typography variant="h4" gutterBottom>
        User Management Dashboard
      </Typography>
      
      {loading && <LinearProgress />}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {dashboardData && (
        <Grid container spacing={3}>
          {/* Summary Cards */}
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Users
                </Typography>
                <Typography variant="h4">
                  {dashboardData.total_users}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {dashboardData.active_users} active, {dashboardData.inactive_users} inactive
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Active Users
                </Typography>
                <Typography variant="h4" color="success.main">
                  {dashboardData.active_users}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {dashboardData.recent_logins} logged in today
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Pending Approval
                </Typography>
                <Typography variant="h4" color="warning.main">
                  {dashboardData.pending_approval}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Awaiting activation
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Training Alerts
                </Typography>
                <Typography variant="h4" color="error.main">
                  {dashboardData.training_overdue}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {dashboardData.competencies_expiring} competencies expiring
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Users by Role */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Users by Role
                </Typography>
                <Box>
                  {Object.entries(dashboardData.users_by_role).map(([role, count]) => (
                    <Box key={role} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography>{getRoleDisplayName(role)}</Typography>
                      <Chip label={count} color={getRoleColor(role)} size="small" />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Users by Department */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Users by Department
                </Typography>
                <Box>
                  {Object.entries(dashboardData.users_by_department).map(([dept, count]) => (
                    <Box key={dept} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography>{dept}</Typography>
                      <Chip label={count} color="primary" size="small" />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );

  const renderUsersList = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          User Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setUserDialogOpen(true)}
        >
          Add New User
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Role</InputLabel>
                <Select
                  value={userFilters.role}
                  onChange={(e) => setUserFilters({ ...userFilters, role: e.target.value })}
                >
                  <MenuItem value="">All Roles</MenuItem>
                  <MenuItem value="ADMIN">Admin</MenuItem>
                  <MenuItem value="QA_MANAGER">QA Manager</MenuItem>
                  <MenuItem value="QA_SPECIALIST">QA Specialist</MenuItem>
                  <MenuItem value="PRODUCTION_MANAGER">Production Manager</MenuItem>
                  <MenuItem value="PRODUCTION_OPERATOR">Production Operator</MenuItem>
                  <MenuItem value="MAINTENANCE">Maintenance</MenuItem>
                  <MenuItem value="LAB_TECHNICIAN">Lab Technician</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={userFilters.status}
                  onChange={(e) => setUserFilters({ ...userFilters, status: e.target.value })}
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="ACTIVE">Active</MenuItem>
                  <MenuItem value="INACTIVE">Inactive</MenuItem>
                  <MenuItem value="SUSPENDED">Suspended</MenuItem>
                  <MenuItem value="PENDING_APPROVAL">Pending Approval</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search users..."
                value={userFilters.search}
                onChange={(e) => setUserFilters({ ...userFilters, search: e.target.value })}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                variant="outlined"
                startIcon={<FilterIcon />}
                onClick={fetchUsers}
                fullWidth
              >
                Apply Filters
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Users Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>User</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Last Login</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar sx={{ mr: 2 }}>
                      {user.profile_picture ? (
                        <img src={user.profile_picture} alt={user.full_name} />
                      ) : (
                        <PersonIcon />
                      )}
                    </Avatar>
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {user.full_name}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {user.username} • {user.email}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={getRoleDisplayName(user.role)} 
                    color={getRoleColor(user.role)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{user.department || '-'}</TableCell>
                <TableCell>
                  <Chip 
                    label={getStatusDisplayName(user.status)} 
                    color={getStatusColor(user.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {user.last_login ? (
                    new Date(user.last_login).toLocaleDateString()
                  ) : (
                    'Never'
                  )}
                </TableCell>
                <TableCell>
                  <IconButton size="small" onClick={() => {
                    setSelectedUser(user);
                    setViewUserDialogOpen(true);
                  }}>
                    <VisibilityIcon />
                  </IconButton>
                  <IconButton size="small" onClick={() => {
                    setSelectedUser(user);
                    setUserForm({
                      username: user.username,
                      email: user.email,
                      full_name: user.full_name,
                      password: '',
                      role: user.role,
                      department: user.department || '',
                      position: user.position || '',
                      phone: user.phone || '',
                      employee_id: user.employee_id || '',
                      bio: user.bio || ''
                    });
                    setUserDialogOpen(true);
                  }}>
                    <EditIcon />
                  </IconButton>
                  {user.is_active ? (
                    <IconButton size="small" onClick={() => handleDeactivateUser(user.id)}>
                      <LockIcon />
                    </IconButton>
                  ) : (
                    <IconButton size="small" onClick={() => handleActivateUser(user.id)}>
                      <LockOpenIcon />
                    </IconButton>
                  )}
                  <IconButton size="small" onClick={() => handleDeleteUser(user.id)}>
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderTrainingManagement = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Training & Competency Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setTrainingDialogOpen(true)}
        >
          Add Training Record
        </Button>
      </Box>

      {/* Training Records */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Training Records
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Employee</TableCell>
                  <TableCell>Training</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Completion Date</TableCell>
                  <TableCell>Expiry Date</TableCell>
                  <TableCell>Score</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {trainingRecords.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell>
                      {users.find(u => u.id === record.user_id)?.full_name || 'Unknown'}
                    </TableCell>
                    <TableCell>{record.training_name}</TableCell>
                    <TableCell>{record.training_type}</TableCell>
                    <TableCell>{new Date(record.completion_date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      {record.expiry_date ? new Date(record.expiry_date).toLocaleDateString() : '-'}
                    </TableCell>
                    <TableCell>{record.score || '-'}</TableCell>
                    <TableCell>
                      <Chip 
                        label={record.status} 
                        color={record.status === 'COMPLETED' ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <DownloadIcon />
                      </IconButton>
                      <IconButton size="small">
                        <PrintIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Competency Matrix */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Competency Matrix
          </Typography>
          {competencyMatrix.map((matrix) => {
            const user = users.find(u => u.id === matrix.user_id);
            return (
              <Accordion key={matrix.user_id} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <Avatar sx={{ mr: 2 }}>
                      <PersonIcon />
                    </Avatar>
                    <Typography variant="subtitle1">
                      {user?.full_name || 'Unknown User'}
                    </Typography>
                    <Box sx={{ ml: 'auto' }}>
                      <Chip 
                        label={`${Object.keys(matrix.competencies).length} competencies`} 
                        size="small"
                      />
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {Object.entries(matrix.competencies).map(([competency, details]) => (
                      <Grid item xs={12} md={6} key={competency}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography variant="subtitle2" gutterBottom>
                              {competency}
                            </Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="body2">Level:</Typography>
                              <Chip label={details.level} size="small" />
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="body2">Status:</Typography>
                              <Chip 
                                label={details.status} 
                                color={details.status === 'COMPETENT' ? 'success' : 'warning'}
                                size="small"
                              />
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="body2">Next Assessment:</Typography>
                              <Typography variant="body2">
                                {new Date(details.next_assessment).toLocaleDateString()}
                              </Typography>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            );
          })}
        </CardContent>
      </Card>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h3" gutterBottom>
        User Management & Security
      </Typography>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Dashboard" icon={<AssessmentIcon />} />
          <Tab label="User Management" icon={<GroupIcon />} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && renderDashboard()}
      {activeTab === 1 && renderUsersList()}
      {false && activeTab === 2 && renderTrainingManagement()}

      {/* Create/Edit User Dialog */}
      <Dialog open={userDialogOpen} onClose={() => setUserDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedUser ? 'Edit User' : 'Create New User'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Username"
                value={userForm.username}
                onChange={(e) => setUserForm({ ...userForm, username: e.target.value })}
                disabled={!!selectedUser}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={userForm.email}
                onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Full Name"
                value={userForm.full_name}
                onChange={(e) => setUserForm({ ...userForm, full_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={userForm.password}
                onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}
                disabled={!!selectedUser}
                helperText={selectedUser ? 'Leave blank to keep current password' : ''}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  value={userForm.role}
                  onChange={(e) => setUserForm({ ...userForm, role: e.target.value })}
                >
                  <MenuItem value="ADMIN">Admin</MenuItem>
                  <MenuItem value="QA_MANAGER">QA Manager</MenuItem>
                  <MenuItem value="QA_SPECIALIST">QA Specialist</MenuItem>
                  <MenuItem value="PRODUCTION_MANAGER">Production Manager</MenuItem>
                  <MenuItem value="PRODUCTION_OPERATOR">Production Operator</MenuItem>
                  <MenuItem value="MAINTENANCE">Maintenance</MenuItem>
                  <MenuItem value="LAB_TECHNICIAN">Lab Technician</MenuItem>
                  <MenuItem value="VIEWER">Viewer</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Department"
                value={userForm.department}
                onChange={(e) => setUserForm({ ...userForm, department: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Position"
                value={userForm.position}
                onChange={(e) => setUserForm({ ...userForm, position: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Phone"
                value={userForm.phone}
                onChange={(e) => setUserForm({ ...userForm, phone: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Employee ID"
                value={userForm.employee_id}
                onChange={(e) => setUserForm({ ...userForm, employee_id: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Bio"
                multiline
                rows={3}
                value={userForm.bio}
                onChange={(e) => setUserForm({ ...userForm, bio: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUserDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={() => selectedUser ? handleUpdateUser(selectedUser.id) : handleCreateUser()} 
            variant="contained" 
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : (selectedUser ? 'Update User' : 'Create User')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* View User Dialog */}
      <Dialog open={viewUserDialogOpen} onClose={() => setViewUserDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>User Details</DialogTitle>
        <DialogContent>
          {selectedUser && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sx={{ textAlign: 'center', mb: 2 }}>
                <Avatar sx={{ width: 80, height: 80, mx: 'auto', mb: 2 }}>
                  {selectedUser.profile_picture ? (
                    <img src={selectedUser.profile_picture} alt={selectedUser.full_name} />
                  ) : (
                    <PersonIcon sx={{ fontSize: 40 }} />
                  )}
                </Avatar>
                <Typography variant="h5">{selectedUser.full_name}</Typography>
                <Typography variant="body2" color="textSecondary">{selectedUser.username}</Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2">{selectedUser.email}</Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <PhoneIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2">{selectedUser.phone || 'Not provided'}</Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <BusinessIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2">{selectedUser.department || 'Not assigned'}</Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <WorkIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2">{selectedUser.position || 'Not assigned'}</Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <CalendarIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2">
                    Last login: {selectedUser.last_login ? new Date(selectedUser.last_login).toLocaleString() : 'Never'}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <CalendarIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2">
                    Created: {new Date(selectedUser.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>Account Status</Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip 
                    label={getRoleDisplayName(selectedUser.role)} 
                    color={getRoleColor(selectedUser.role)}
                  />
                  <Chip 
                    label={getStatusDisplayName(selectedUser.status)} 
                    color={getStatusColor(selectedUser.status)}
                  />
                  <Chip 
                    label={selectedUser.is_active ? 'Active' : 'Inactive'} 
                    color={selectedUser.is_active ? 'success' : 'error'}
                  />
                  <Chip 
                    label={selectedUser.is_verified ? 'Verified' : 'Unverified'} 
                    color={selectedUser.is_verified ? 'success' : 'warning'}
                  />
                </Box>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewUserDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Add Training Record Dialog */}
      <Dialog open={trainingDialogOpen} onClose={() => setTrainingDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Training Record</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Employee</InputLabel>
                <Select
                  value={trainingForm.user_id}
                  onChange={(e) => setTrainingForm({ ...trainingForm, user_id: e.target.value })}
                >
                  {users.map((user) => (
                    <MenuItem key={user.id} value={user.id}>
                      {user.full_name} ({user.username})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Training Name"
                value={trainingForm.training_name}
                onChange={(e) => setTrainingForm({ ...trainingForm, training_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Training Type</InputLabel>
                <Select
                  value={trainingForm.training_type}
                  onChange={(e) => setTrainingForm({ ...trainingForm, training_type: e.target.value })}
                >
                  <MenuItem value="Food Safety">Food Safety</MenuItem>
                  <MenuItem value="Technical">Technical</MenuItem>
                  <MenuItem value="Safety">Safety</MenuItem>
                  <MenuItem value="Quality">Quality</MenuItem>
                  <MenuItem value="Compliance">Compliance</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Completion Date"
                type="date"
                value={trainingForm.completion_date}
                onChange={(e) => setTrainingForm({ ...trainingForm, completion_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Expiry Date"
                type="date"
                value={trainingForm.expiry_date}
                onChange={(e) => setTrainingForm({ ...trainingForm, expiry_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Score"
                type="number"
                value={trainingForm.score}
                onChange={(e) => setTrainingForm({ ...trainingForm, score: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Certificate Path"
                value={trainingForm.certificate_path}
                onChange={(e) => setTrainingForm({ ...trainingForm, certificate_path: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTrainingDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Add Training Record'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Users; 