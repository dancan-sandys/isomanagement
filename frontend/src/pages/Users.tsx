import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
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
  Divider,
  Pagination,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Password as PasswordIcon,
  Person as PersonIcon,
  Group as GroupIcon,
  School as SchoolIcon,
  Assessment as AssessmentIcon,
  Lock as LockIcon,
  LockOpen as LockOpenIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Business as BusinessIcon,
  Work as WorkIcon,
  CalendarToday as CalendarIcon,
} from '@mui/icons-material';
import { usersAPI } from '../services/api';
import { RootState } from '../store';
import { canManageUsers } from '../store/slices/authSlice';
import PageHeader from '../components/UI/PageHeader';

// Interfaces
interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role_id: number;
  role_name?: string;
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
  const { user: currentUser } = useSelector((state: RootState) => state.auth);
  
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [users, setUsers] = useState<User[]>([]);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Dialog states
  const [userDialogOpen, setUserDialogOpen] = useState(false);
  const [viewUserDialogOpen, setViewUserDialogOpen] = useState(false);
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [resetPassword, setResetPassword] = useState('');
  const [resetPasswordConfirm, setResetPasswordConfirm] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  // Form states
  const [userForm, setUserForm] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role_id: '',
    department: '',
    position: '',
    phone: '',
    employee_id: '',
    bio: ''
  });
  const [createConfirmPassword, setCreateConfirmPassword] = useState('');
  const [formErrors, setFormErrors] = useState<{
    username?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
    role_id?: string;
  }>({});

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

  // Check if user has permission to manage users
  const hasUserManagementPermission = canManageUsers(currentUser);

  // Helper function to format error messages
  const formatErrorMessage = (error: any): string => {
    if (typeof error === 'string') return error;
    if (error?.response?.data?.detail) {
      const detail = error.response.data.detail;
      if (Array.isArray(detail)) return detail.map((err: any) => (typeof err === 'string' ? err : err.msg || 'Validation error')).join(', ');
      if (typeof detail === 'object' && detail.msg) return detail.msg;
      if (typeof detail === 'string') return detail;
    }
    return 'An unexpected error occurred';
  };

  // Load data on component mount
  useEffect(() => {
    if (hasUserManagementPermission) {
      fetchDashboardData();
      fetchUsers();
    }
  }, [hasUserManagementPermission]); // eslint-disable-line react-hooks/exhaustive-deps

  // API calls
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await usersAPI.getDashboard();
      setDashboardData(response);
    } catch (err: any) {
      setError(formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params: any = { page: pagination.page, size: pagination.size };
      if (userFilters.search?.trim()) params.search = userFilters.search;
      if (userFilters.role?.trim()) params.role_id = parseInt(userFilters.role);
      if (userFilters.status?.trim()) params.status = userFilters.status;
      if (userFilters.department?.trim()) params.department = userFilters.department;
      const response = await usersAPI.getUsers(params);
      // Backend returns PaginatedResponse directly (no data wrapper)
      setUsers(response.items || []);
      setPagination({
        page: response.page || 1,
        size: response.size || 10,
        total: response.total || 0,
        pages: response.pages || 0,
      });
    } catch (err: any) {
      setError(formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Form handlers
  const handleCreateUser = async () => {
    if (!validateUserForm(false)) return;
    try {
      setLoading(true);
      await usersAPI.createUser({ ...userForm, role_id: parseInt(userForm.role_id) });
      setUserDialogOpen(false);
      resetUserForm();
      fetchUsers();
    } catch (err: any) {
      setError(formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (userId: number) => {
    if (!validateUserForm(true)) return;
    try {
      setLoading(true);
      const updateData: any = { ...userForm };
      if (userForm.role_id) updateData.role_id = parseInt(userForm.role_id);
      if (!userForm.password) delete updateData.password;
      await usersAPI.updateUser(userId, updateData);
      setUserDialogOpen(false);
      resetUserForm();
      fetchUsers();
    } catch (err: any) {
      setError(formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    try {
      setLoading(true);
      await usersAPI.deleteUser(userId);
      fetchUsers();
    } catch (err: any) {
      setError(formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleActivateUser = async (userId: number) => {
    try {
      setLoading(true);
      await usersAPI.activateUser(userId);
      fetchUsers();
    } catch (err: any) {
      setError(formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivateUser = async (userId: number) => {
    try {
      setLoading(true);
      await usersAPI.deactivateUser(userId);
      fetchUsers();
    } catch (err: any) {
      setError(formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const resetUserForm = () => {
    setUserForm({
      username: '',
      email: '',
      full_name: '',
      password: '',
      role_id: '',
      department: '',
      position: '',
      phone: '',
      employee_id: '',
      bio: '',
    });
    setSelectedUser(null);
    setCreateConfirmPassword('');
    setFormErrors({});
  };

  // Utility functions
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'System Administrator': return 'error';
      case 'QA Manager': return 'warning';
      case 'QA Specialist': return 'info';
      case 'Production Manager': return 'primary';
      case 'Production Operator': return 'success';
      case 'Maintenance': return 'secondary';
      case 'Lab Technician': return 'default';
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

  const getRoleDisplayName = (role: string) => role.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  const getStatusDisplayName = (status: string) => status.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  const evaluatePasswordStrength = (password: string): { score: number; label: 'Very Weak'|'Weak'|'Medium'|'Strong'|'Very Strong' } => {
    let score = 0;
    if (!password) return { score: 0, label: 'Very Weak' };
    const lengthOK = password.length >= 8;
    const hasLower = /[a-z]/.test(password);
    const hasUpper = /[A-Z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[^A-Za-z0-9]/.test(password);
    const checksPassed = [lengthOK, hasLower, hasUpper, hasNumber, hasSpecial].filter(Boolean).length;
    score = Math.min(100, Math.round((checksPassed / 5) * 100));
    const label = score >= 80 ? 'Very Strong' : score >= 60 ? 'Strong' : score >= 40 ? 'Medium' : score >= 20 ? 'Weak' : 'Very Weak';
    return { score, label };
  };
  const passwordMeetsPolicy = (password: string): boolean => {
    return password.length >= 8 && /[a-z]/.test(password) && /[A-Z]/.test(password) && /[0-9]/.test(password) && /[^A-Za-z0-9]/.test(password);
  };

  const isEmailValid = (email: string): boolean => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const validateUserForm = (isEdit: boolean): boolean => {
    const errors: typeof formErrors = {};
    if (!userForm.username.trim()) errors.username = 'Username is required';
    if (!userForm.email.trim()) errors.email = 'Email is required';
    else if (!isEmailValid(userForm.email.trim())) errors.email = 'Invalid email';
    if (!userForm.role_id) errors.role_id = 'Role is required';
    if (!isEdit) {
      if (!passwordMeetsPolicy(userForm.password)) errors.password = 'Password must meet policy';
      if (userForm.password !== createConfirmPassword) errors.confirmPassword = 'Passwords do not match';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, page: number) => setPagination(prev => ({ ...prev, page }));
  const handleFilterApply = () => { setPagination(prev => ({ ...prev, page: 1 })); fetchUsers(); };

  // If user doesn't have permission, show access denied
  if (!hasUserManagementPermission) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          <Typography variant="h6">Access Denied</Typography>
          <Typography variant="body2">You don't have permission to access user management. Please contact your system administrator.</Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <PageHeader
        title="User Management & Security"
        subtitle="Manage system users, roles, and permissions"
        breadcrumbs={[
          { label: 'Dashboard', path: '/' },
          { label: 'Users', path: '/users' },
        ]}
      />

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
          <Tab label="Dashboard" icon={<AssessmentIcon />} />
          <Tab label="User Management" icon={<GroupIcon />} />
          <Tab label="Training & Competency" icon={<SchoolIcon />} />
        </Tabs>
      </Box>

      {activeTab === 0 && (
        <Box>
          <Typography variant="h4" gutterBottom>User Management Dashboard</Typography>
          {loading && <LinearProgress />}
          {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}
          {dashboardData && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Card><CardContent>
                  <Typography color="textSecondary" gutterBottom>Total Users</Typography>
                  <Typography variant="h4">{dashboardData.total_users}</Typography>
                  <Typography variant="body2" color="textSecondary">{dashboardData.active_users} active, {dashboardData.inactive_users} inactive</Typography>
                </CardContent></Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card><CardContent>
                  <Typography color="textSecondary" gutterBottom>Active Users</Typography>
                  <Typography variant="h4" color="success.main">{dashboardData.active_users}</Typography>
                  <Typography variant="body2" color="textSecondary">{dashboardData.recent_logins} logged in today</Typography>
                </CardContent></Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card><CardContent>
                  <Typography color="textSecondary" gutterBottom>Pending Approval</Typography>
                  <Typography variant="h4" color="warning.main">{dashboardData.pending_approval}</Typography>
                  <Typography variant="body2" color="textSecondary">Awaiting activation</Typography>
                </CardContent></Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card><CardContent>
                  <Typography color="textSecondary" gutterBottom>Training Alerts</Typography>
                  <Typography variant="h4" color="error.main">{dashboardData.training_overdue}</Typography>
                  <Typography variant="body2" color="textSecondary">{dashboardData.competencies_expiring} competencies expiring</Typography>
                </CardContent></Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card><CardContent>
                  <Typography variant="h6" gutterBottom>Users by Role</Typography>
                  <Box>
                    {Object.entries(dashboardData.users_by_role).map(([role, count]) => (
                      <Box key={role} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography>{getRoleDisplayName(role)}</Typography>
                        <Chip label={count} color={getRoleColor(role)} size="small" />
                      </Box>
                    ))}
                  </Box>
                </CardContent></Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card><CardContent>
                  <Typography variant="h6" gutterBottom>Users by Department</Typography>
                  <Box>
                    {Object.entries(dashboardData.users_by_department).map(([dept, count]) => (
                      <Box key={dept} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography>{dept}</Typography>
                        <Chip label={count} color="primary" size="small" />
                      </Box>
                    ))}
                  </Box>
                </CardContent></Card>
              </Grid>
            </Grid>
          )}
        </Box>
      )}

      {activeTab === 1 && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">User Management</Typography>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => setUserDialogOpen(true)}>Add New User</Button>
          </Box>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Role</InputLabel>
                    <Select value={userFilters.role} onChange={(e) => setUserFilters({ ...userFilters, role: e.target.value })}>
                      <MenuItem value="">All Roles</MenuItem>
                      <MenuItem value="1">System Administrator</MenuItem>
                      <MenuItem value="2">QA Manager</MenuItem>
                      <MenuItem value="3">QA Specialist</MenuItem>
                      <MenuItem value="4">Production Manager</MenuItem>
                      <MenuItem value="5">Production Operator</MenuItem>
                      <MenuItem value="6">Maintenance</MenuItem>
                      <MenuItem value="7">Lab Technician</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Status</InputLabel>
                    <Select value={userFilters.status} onChange={(e) => setUserFilters({ ...userFilters, status: e.target.value })}>
                      <MenuItem value="">All Statuses</MenuItem>
                      <MenuItem value="ACTIVE">Active</MenuItem>
                      <MenuItem value="INACTIVE">Inactive</MenuItem>
                      <MenuItem value="SUSPENDED">Suspended</MenuItem>
                      <MenuItem value="PENDING_APPROVAL">Pending Approval</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField fullWidth size="small" placeholder="Search users..." value={userFilters.search} onChange={(e) => setUserFilters({ ...userFilters, search: e.target.value })} InputProps={{ startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} /> }} />
                </Grid>
                <Grid item xs={12} md={2}>
                  <Button variant="outlined" startIcon={<FilterIcon />} onClick={handleFilterApply} fullWidth>Apply Filters</Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

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
                          {user.profile_picture ? <img src={user.profile_picture} alt={user.full_name} /> : <PersonIcon />}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">{user.full_name}</Typography>
                          <Typography variant="caption" color="textSecondary">{user.username} • {user.email}</Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={getRoleDisplayName(user.role_name || 'Unknown')} color={getRoleColor(user.role_name || '')} size="small" />
                    </TableCell>
                    <TableCell>{user.department || '-'}</TableCell>
                    <TableCell>
                      <Chip label={getStatusDisplayName(user.status)} color={getStatusColor(user.status)} size="small" />
                    </TableCell>
                    <TableCell>{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => { setSelectedUser(user); setViewUserDialogOpen(true); }}><VisibilityIcon /></IconButton>
                      <IconButton size="small" onClick={() => { setSelectedUser(user); setUserForm({ username: user.username, email: user.email, full_name: user.full_name, password: '', role_id: user.role_id.toString(), department: user.department || '', position: user.position || '', phone: user.phone || '', employee_id: user.employee_id || '', bio: user.bio || '' }); setUserDialogOpen(true); }}><EditIcon /></IconButton>
                      <IconButton size="small" onClick={() => { setSelectedUser(user); setResetPassword(''); setResetDialogOpen(true); }} title="Reset Password"><PasswordIcon /></IconButton>
                      {user.is_active ? (
                        <IconButton size="small" onClick={() => handleDeactivateUser(user.id)}><LockIcon /></IconButton>
                      ) : (
                        <IconButton size="small" onClick={() => handleActivateUser(user.id)}><LockOpenIcon /></IconButton>
                      )}
                      <IconButton size="small" onClick={() => handleDeleteUser(user.id)}><DeleteIcon /></IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {pagination.pages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <Pagination count={pagination.pages} page={pagination.page} onChange={handlePageChange} color="primary" />
            </Box>
          )}
        </Box>
      )}

      {activeTab === 2 && (
        <Box>
          <Typography variant="h4" gutterBottom>Training & Competency Management</Typography>
          <Typography variant="body1" color="textSecondary">This section will include training records, competency matrices, and skill assessments.</Typography>
        </Box>
      )}

      {/* Create/Edit User Dialog */}
      <Dialog open={userDialogOpen} onClose={() => setUserDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedUser ? 'Edit User' : 'Create New User'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}><TextField fullWidth label="Username" value={userForm.username} onChange={(e) => { setUserForm({ ...userForm, username: e.target.value }); setFormErrors({ ...formErrors, username: undefined }); }} disabled={!!selectedUser} error={!!formErrors.username} helperText={formErrors.username} /></Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Email" type="email" value={userForm.email} onChange={(e) => { setUserForm({ ...userForm, email: e.target.value }); setFormErrors({ ...formErrors, email: undefined }); }} error={!!formErrors.email} helperText={formErrors.email} /></Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Full Name" value={userForm.full_name} onChange={(e) => setUserForm({ ...userForm, full_name: e.target.value })} /></Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Password" type="password" value={userForm.password} onChange={(e) => { setUserForm({ ...userForm, password: e.target.value }); setFormErrors({ ...formErrors, password: undefined }); }} disabled={!!selectedUser} helperText={selectedUser ? 'Leave blank to keep current password' : (formErrors.password || '')} error={!!formErrors.password} /></Grid>
            {!selectedUser && (
              <Grid item xs={12} md={6}><TextField fullWidth label="Confirm Password" type="password" value={createConfirmPassword} onChange={(e) => { setCreateConfirmPassword(e.target.value); setFormErrors({ ...formErrors, confirmPassword: undefined }); }} error={!!formErrors.confirmPassword} helperText={formErrors.confirmPassword} /></Grid>
            )}
            {!selectedUser && (
              <Grid item xs={12} md={6}>
                <Box>
                  <Typography variant="caption" color="text.secondary">Strength: {evaluatePasswordStrength(userForm.password).label}</Typography>
                  <LinearProgress variant="determinate" value={evaluatePasswordStrength(userForm.password).score} sx={{ mt: 0.5 }} />
                </Box>
              </Grid>
            )}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select value={userForm.role_id} onChange={(e) => { setUserForm({ ...userForm, role_id: e.target.value }); setFormErrors({ ...formErrors, role_id: undefined }); }} error={!!formErrors.role_id}>
                  <MenuItem value="1">System Administrator</MenuItem>
                  <MenuItem value="2">QA Manager</MenuItem>
                  <MenuItem value="3">QA Specialist</MenuItem>
                  <MenuItem value="4">Production Manager</MenuItem>
                  <MenuItem value="5">Production Operator</MenuItem>
                  <MenuItem value="6">Maintenance</MenuItem>
                  <MenuItem value="7">Lab Technician</MenuItem>
                  <MenuItem value="8">Viewer</MenuItem>
                </Select>
                {formErrors.role_id && <Typography variant="caption" color="error">{formErrors.role_id}</Typography>}
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Department" value={userForm.department} onChange={(e) => setUserForm({ ...userForm, department: e.target.value })} /></Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Position" value={userForm.position} onChange={(e) => setUserForm({ ...userForm, position: e.target.value })} /></Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Phone" value={userForm.phone} onChange={(e) => setUserForm({ ...userForm, phone: e.target.value })} /></Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Employee ID" value={userForm.employee_id} onChange={(e) => setUserForm({ ...userForm, employee_id: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField fullWidth label="Bio" multiline rows={3} value={userForm.bio} onChange={(e) => setUserForm({ ...userForm, bio: e.target.value })} /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setUserDialogOpen(false); resetUserForm(); }}>Cancel</Button>
          <Button onClick={() => (selectedUser ? handleUpdateUser(selectedUser.id) : handleCreateUser())} variant="contained" disabled={loading}>
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
                  {selectedUser.profile_picture ? <img src={selectedUser.profile_picture} alt={selectedUser.full_name} /> : <PersonIcon sx={{ fontSize: 40 }} />}
                </Avatar>
                <Typography variant="h5">{selectedUser.full_name}</Typography>
                <Typography variant="body2" color="textSecondary">{selectedUser.username}</Typography>
              </Grid>
              <Grid item xs={12} md={6}><Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}><EmailIcon sx={{ mr: 1, color: 'text.secondary' }} /><Typography variant="body2">{selectedUser.email}</Typography></Box></Grid>
              <Grid item xs={12} md={6}><Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}><PhoneIcon sx={{ mr: 1, color: 'text.secondary' }} /><Typography variant="body2">{selectedUser.phone || 'Not provided'}</Typography></Box></Grid>
              <Grid item xs={12} md={6}><Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}><BusinessIcon sx={{ mr: 1, color: 'text.secondary' }} /><Typography variant="body2">{selectedUser.department || 'Not assigned'}</Typography></Box></Grid>
              <Grid item xs={12} md={6}><Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}><WorkIcon sx={{ mr: 1, color: 'text.secondary' }} /><Typography variant="body2">{selectedUser.position || 'Not assigned'}</Typography></Box></Grid>
              <Grid item xs={12} md={6}><Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}><CalendarIcon sx={{ mr: 1, color: 'text.secondary' }} /><Typography variant="body2">Last login: {selectedUser.last_login ? new Date(selectedUser.last_login).toLocaleString() : 'Never'}</Typography></Box></Grid>
              <Grid item xs={12} md={6}><Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}><CalendarIcon sx={{ mr: 1, color: 'text.secondary' }} /><Typography variant="body2">Created: {new Date(selectedUser.created_at).toLocaleDateString()}</Typography></Box></Grid>
              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>Account Status</Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label={getRoleDisplayName(selectedUser.role_name || 'Unknown')} color={getRoleColor(selectedUser.role_name || '')} />
                  <Chip label={getStatusDisplayName(selectedUser.status)} color={getStatusColor(selectedUser.status)} />
                  <Chip label={selectedUser.is_active ? 'Active' : 'Inactive'} color={selectedUser.is_active ? 'success' : 'error'} />
                  <Chip label={selectedUser.is_verified ? 'Verified' : 'Unverified'} color={selectedUser.is_verified ? 'success' : 'warning'} />
                </Box>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewUserDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Admin Reset Password Dialog */}
      <Dialog open={resetDialogOpen} onClose={() => setResetDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Admin Reset Password {selectedUser ? `— ${selectedUser.username}` : ''}</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will immediately set a new password for the user. The user should change it after first login.
          </Alert>
          <TextField
            fullWidth
            type="password"
            label="New Password"
            value={resetPassword}
            onChange={(e) => setResetPassword(e.target.value)}
            helperText="Must be at least 8 characters and include upper, lower, number, and special character"
          />
          <Box sx={{ mt: 1 }}>
            <Typography variant="caption" color="text.secondary">Strength: {evaluatePasswordStrength(resetPassword).label}</Typography>
            <LinearProgress variant="determinate" value={evaluatePasswordStrength(resetPassword).score} sx={{ mt: 0.5 }} />
          </Box>
          <TextField
            fullWidth
            sx={{ mt: 2 }}
            type="password"
            label="Confirm New Password"
            value={resetPasswordConfirm}
            onChange={(e) => setResetPasswordConfirm(e.target.value)}
            error={!!resetPassword && resetPasswordConfirm.length > 0 && resetPassword !== resetPasswordConfirm}
            helperText={resetPasswordConfirm && resetPassword !== resetPasswordConfirm ? 'Passwords do not match' : ' '}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={
              loading ||
              !selectedUser ||
              !passwordMeetsPolicy(resetPassword) ||
              resetPassword !== resetPasswordConfirm
            }
            onClick={async () => {
              if (!selectedUser) return;
              try {
                setLoading(true);
                await usersAPI.resetPassword(selectedUser.id, resetPassword);
                setResetDialogOpen(false);
                setResetPassword('');
                setResetPasswordConfirm('');
              } catch (err: any) {
                setError(formatErrorMessage(err));
              } finally {
                setLoading(false);
              }
            }}
          >
            Reset Password
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Users; 