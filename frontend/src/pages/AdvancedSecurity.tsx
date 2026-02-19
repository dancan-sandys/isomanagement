import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Stack,
  Button,
  Card,
  CardContent,
  Grid,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Checkbox,
  FormControlLabel,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Switch,
  Slider,
  InputAdornment,
  FormHelperText,
  Badge,
  CircularProgress,
  CardActions,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Avatar,
  ListItemAvatar,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Security as SecurityIcon,
  TwoWheeler as TwoFactorIcon,
  History as HistoryIcon,
  // MUI has no Session icon; reuse History
  History as SessionIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Lock as LockIcon,
  LockOpen as LockOpenIcon,
  Person as PersonIcon,
  Computer as ComputerIcon,
  LocationOn as LocationIcon,
  AccessTime as TimeIcon,
  Refresh as RefreshIcon,
  Block as BlockIcon,
  // MUI has no Unblock icon; reuse LockOpen
  LockOpen as UnblockIcon,
  QrCode as QrCodeIcon,
  Key as KeyIcon,
  Shield as ShieldIcon,
  VisibilityOff as VisibilityOffIcon,
  Visibility as VisibilityOnIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon2,
} from '@mui/icons-material';

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
      id={`security-tabpanel-${index}`}
      aria-labelledby={`security-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AdvancedSecurity: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [securityAlerts, setSecurityAlerts] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [activeSessions, setActiveSessions] = useState<any[]>([]);
  const [twoFactorUsers, setTwoFactorUsers] = useState<any[]>([]);
  const [securitySettings, setSecuritySettings] = useState<any>({});

  // 2FA Setup Dialog
  const [twoFactorDialog, setTwoFactorDialog] = useState(false);
  const [twoFactorForm, setTwoFactorForm] = useState({
    user_id: '',
    method: 'app',
    phone: '',
    email: '',
  });

  // Security Policy Dialog
  const [policyDialog, setPolicyDialog] = useState(false);
  const [policyForm, setPolicyForm] = useState({
    password_min_length: 8,
    password_require_uppercase: true,
    password_require_lowercase: true,
    password_require_numbers: true,
    password_require_special: true,
    password_max_age_days: 90,
    session_timeout_minutes: 30,
    max_login_attempts: 5,
    lockout_duration_minutes: 15,
    require_2fa_for_admin: true,
    require_2fa_for_sensitive_roles: true,
    ip_whitelist: [] as string[],
    ip_blacklist: [] as string[],
  });

  // Audit Trail Filter Dialog
  const [auditFilterDialog, setAuditFilterDialog] = useState(false);
  const [auditFilterForm, setAuditFilterForm] = useState({
    start_date: '',
    end_date: '',
    user_id: '',
    action_type: '',
    resource_type: '',
    severity: '',
  });

  // Security Alerts Data
  const [securityData, setSecurityData] = useState({
    alerts: [
      { id: 1, type: 'failed_login', user: 'john.doe', ip: '192.168.1.100', timestamp: '2024-12-01T10:30:00Z', severity: 'medium' },
      { id: 2, type: 'suspicious_activity', user: 'admin', ip: '10.0.0.50', timestamp: '2024-12-01T09:15:00Z', severity: 'high' },
      { id: 3, type: 'multiple_sessions', user: 'jane.smith', ip: '172.16.0.25', timestamp: '2024-12-01T08:45:00Z', severity: 'low' },
    ],
    auditLogs: [
      { id: 1, user: 'admin', action: 'login', resource: 'system', ip: '192.168.1.1', timestamp: '2024-12-01T10:00:00Z', details: 'Successful login' },
      { id: 2, user: 'john.doe', action: 'create', resource: 'document', ip: '192.168.1.100', timestamp: '2024-12-01T09:30:00Z', details: 'Created new document' },
      { id: 3, user: 'jane.smith', action: 'update', resource: 'user', ip: '172.16.0.25', timestamp: '2024-12-01T09:00:00Z', details: 'Updated user profile' },
    ],
    activeSessions: [
      { id: 1, user: 'admin', ip: '192.168.1.1', location: 'Office', device: 'Desktop', browser: 'Chrome', login_time: '2024-12-01T08:00:00Z', last_activity: '2024-12-01T10:30:00Z' },
      { id: 2, user: 'john.doe', ip: '192.168.1.100', location: 'Home', device: 'Laptop', browser: 'Firefox', login_time: '2024-12-01T09:00:00Z', last_activity: '2024-12-01T10:25:00Z' },
      { id: 3, user: 'jane.smith', ip: '172.16.0.25', location: 'Mobile', device: 'iPhone', browser: 'Safari', login_time: '2024-12-01T09:30:00Z', last_activity: '2024-12-01T10:20:00Z' },
    ],
    twoFactorUsers: [
      { id: 1, user: 'admin', method: 'app', status: 'enabled', last_used: '2024-12-01T10:00:00Z' },
      { id: 2, user: 'john.doe', method: 'sms', status: 'enabled', last_used: '2024-12-01T09:30:00Z' },
      { id: 3, user: 'jane.smith', method: 'email', status: 'pending', last_used: null },
    ],
  });

  const loadData = async () => {
    setLoading(true);
    try {
      // Simulate API calls for now
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSecurityAlerts(securityData.alerts);
      setAuditLogs(securityData.auditLogs);
      setActiveSessions(securityData.activeSessions);
      setTwoFactorUsers(securityData.twoFactorUsers);

      // Mock security settings
      setSecuritySettings({
        password_policy: {
          min_length: 8,
          require_uppercase: true,
          require_lowercase: true,
          require_numbers: true,
          require_special: true,
          max_age_days: 90,
        },
        session_policy: {
          timeout_minutes: 30,
          max_concurrent_sessions: 3,
          require_reauthentication: true,
        },
        lockout_policy: {
          max_attempts: 5,
          lockout_duration_minutes: 15,
          reset_after_hours: 24,
        },
        two_factor_policy: {
          require_for_admin: true,
          require_for_sensitive_roles: true,
          allowed_methods: ['app', 'sms', 'email'],
        },
      });

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

  const handleTwoFactorSubmit = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setTwoFactorDialog(false);
      setTwoFactorForm({
        user_id: '',
        method: 'app',
        phone: '',
        email: '',
      });
      loadData();
    } catch (error) {
      console.error('Error setting up 2FA:', error);
    }
  };

  const handlePolicySubmit = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setPolicyDialog(false);
      loadData();
    } catch (error) {
      console.error('Error updating security policy:', error);
    }
  };

  const handleTerminateSession = async (sessionId: number) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setActiveSessions(prev => prev.filter(session => session.id !== sessionId));
    } catch (error) {
      console.error('Error terminating session:', error);
    }
  };

  const handleBlockUser = async (userId: number) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      // Update user status
    } catch (error) {
      console.error('Error blocking user:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'login': return 'success';
      case 'logout': return 'info';
      case 'create': return 'primary';
      case 'update': return 'warning';
      case 'delete': return 'error';
      default: return 'default';
    }
  };

  const getTwoFactorStatusColor = (status: string) => {
    switch (status) {
      case 'enabled': return 'success';
      case 'pending': return 'warning';
      case 'disabled': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box p={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight="bold" color="primary">
          Advanced Security Management
        </Typography>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<SettingsIcon />}
            onClick={() => setPolicyDialog(true)}
          >
            Security Policy
          </Button>
          <Button
            variant="contained"
            startIcon={<TwoFactorIcon />}
            onClick={() => setTwoFactorDialog(true)}
          >
            Setup 2FA
          </Button>
        </Stack>
      </Stack>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Security Alerts */}
      {securityAlerts.filter(alert => alert.severity === 'high').length > 0 && (
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            🚨 {securityAlerts.filter(alert => alert.severity === 'high').length} High Priority Security Alert(s)
          </Typography>
          <Stack spacing={1}>
            {securityAlerts.filter(alert => alert.severity === 'high').slice(0, 3).map((alert) => (
              <Typography key={alert.id} variant="body2">
                • {alert.type.replace('_', ' ').toUpperCase()}: {alert.user} from {alert.ip}
              </Typography>
            ))}
          </Stack>
        </Alert>
      )}

      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="security tabs">
            <Tab
              icon={<SecurityIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Security Overview</span>
                  <Badge badgeContent={securityAlerts.length} color="error" />
                </Stack>
              }
            />
            <Tab
              icon={<TwoFactorIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Two-Factor Auth</span>
                  <Badge badgeContent={twoFactorUsers.filter(u => u.status === 'enabled').length} color="success" />
                </Stack>
              }
            />
            <Tab
              icon={<HistoryIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Audit Trail</span>
                  <Badge badgeContent={auditLogs.length} color="info" />
                </Stack>
              }
            />
            <Tab
              icon={<SessionIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Active Sessions</span>
                  <Badge badgeContent={activeSessions.length} color="warning" />
                </Stack>
              }
            />
            <Tab
              icon={<SettingsIcon />}
              label="Security Policy"
            />
          </Tabs>
        </Box>

        {/* Security Overview Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            {/* Security Score Card */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                    <Typography variant="h6" color="text.secondary">
                      Security Score
                    </Typography>
                    <Chip
                      label="92%"
                      color="success"
                      size="small"
                    />
                  </Stack>
                  <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                    <CircularProgress
                      variant="determinate"
                      value={92}
                      size={80}
                      color="success"
                    />
                    <Box
                      sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Typography variant="h6" component="div" color="text.secondary">
                        92%
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Security Alerts Card */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                    Security Alerts
                  </Typography>
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">High Priority</Typography>
                      <Chip label={securityAlerts.filter(a => a.severity === 'high').length} color="error" size="small" />
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Medium Priority</Typography>
                      <Chip label={securityAlerts.filter(a => a.severity === 'medium').length} color="warning" size="small" />
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Low Priority</Typography>
                      <Chip label={securityAlerts.filter(a => a.severity === 'low').length} color="info" size="small" />
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            {/* 2FA Status Card */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                    2FA Status
                  </Typography>
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Enabled</Typography>
                      <Chip label={twoFactorUsers.filter(u => u.status === 'enabled').length} color="success" size="small" />
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Pending</Typography>
                      <Chip label={twoFactorUsers.filter(u => u.status === 'pending').length} color="warning" size="small" />
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Disabled</Typography>
                      <Chip label={twoFactorUsers.filter(u => u.status === 'disabled').length} color="error" size="small" />
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            {/* Active Sessions Card */}
            <Grid item xs={12} md={6} lg={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                    Active Sessions
                  </Typography>
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Total Active</Typography>
                      <Typography variant="h6">{activeSessions.length}</Typography>
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Suspicious</Typography>
                      <Typography variant="h6" color="warning.main">2</Typography>
                    </Stack>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">Blocked</Typography>
                      <Typography variant="h6" color="error.main">1</Typography>
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            {/* Recent Security Alerts */}
            <Grid item xs={12} lg={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Recent Security Alerts</Typography>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Type</TableCell>
                        <TableCell>User</TableCell>
                        <TableCell>IP Address</TableCell>
                        <TableCell>Time</TableCell>
                        <TableCell>Severity</TableCell>
                        <TableCell align="right">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {securityAlerts.slice(0, 5).map((alert) => (
                        <TableRow key={alert.id}>
                          <TableCell>
                            <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                              {alert.type.replace('_', ' ')}
                            </Typography>
                          </TableCell>
                          <TableCell>{alert.user}</TableCell>
                          <TableCell>{alert.ip}</TableCell>
                          <TableCell>{new Date(alert.timestamp).toLocaleString()}</TableCell>
                          <TableCell>
                            <Chip
                              label={alert.severity}
                              color={getSeverityColor(alert.severity)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="right">
                            <Stack direction="row" spacing={1}>
                              <Tooltip title="View Details">
                                <IconButton size="small">
                                  <ViewIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Block IP">
                                <IconButton size="small" color="error">
                                  <BlockIcon />
                                </IconButton>
                              </Tooltip>
                            </Stack>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </Grid>

            {/* Security Metrics */}
            <Grid item xs={12} lg={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Security Metrics</Typography>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Failed Login Attempts</Typography>
                      <Typography variant="h4" color="error.main">12</Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Suspicious Activities</Typography>
                      <Typography variant="h4" color="warning.main">3</Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Blocked IPs</Typography>
                      <Typography variant="h4" color="info.main">5</Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">2FA Enrollments</Typography>
                      <Typography variant="h4" color="success.main">24</Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Two-Factor Authentication Tab */}
        <TabPanel value={tabValue} index={1}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">Two-Factor Authentication</Typography>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => setTwoFactorDialog(true)}
            >
              Setup 2FA
            </Button>
          </Stack>
          <Grid container spacing={3}>
            {twoFactorUsers.map((user) => (
              <Grid item xs={12} md={6} lg={4} key={user.id}>
                <Card>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                      <Typography variant="h6" fontWeight="bold">
                        {user.user}
                      </Typography>
                      <Chip
                        label={user.status}
                        color={getTwoFactorStatusColor(user.status)}
                        size="small"
                      />
                    </Stack>
                    <Stack spacing={1}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Method:</strong> {user.method.toUpperCase()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Last Used:</strong> {user.last_used ? new Date(user.last_used).toLocaleString() : 'Never'}
                      </Typography>
                    </Stack>
                  </CardContent>
                  <CardActions>
                    <Button size="small" startIcon={<ViewIcon />}>
                      View Details
                    </Button>
                    <Button size="small" startIcon={<EditIcon />}>
                      Edit
                    </Button>
                    <Button size="small" startIcon={<DeleteIcon />} color="error">
                      Disable
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Audit Trail Tab */}
        <TabPanel value={tabValue} index={2}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">Audit Trail</Typography>
            <Button
              variant="outlined"
              // Filter icon not imported; use Settings icon
              startIcon={<SettingsIcon />}
              onClick={() => setAuditFilterDialog(true)}
            >
              Filter Logs
            </Button>
          </Stack>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>IP Address</TableCell>
                <TableCell>Timestamp</TableCell>
                <TableCell>Details</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {auditLogs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell>{log.user}</TableCell>
                  <TableCell>
                    <Chip
                      label={log.action}
                      color={getActionColor(log.action)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{log.resource}</TableCell>
                  <TableCell>{log.ip}</TableCell>
                  <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                  <TableCell>{log.details}</TableCell>
                  <TableCell align="right">
                    <Tooltip title="View Details">
                      <IconButton size="small">
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TabPanel>

        {/* Active Sessions Tab */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" sx={{ mb: 2 }}>Active Sessions</Typography>
          <Grid container spacing={3}>
            {activeSessions.map((session) => (
              <Grid item xs={12} md={6} lg={4} key={session.id}>
                <Card>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                      <Typography variant="h6" fontWeight="bold">
                        {session.user}
                      </Typography>
                      <Chip
                        label="Active"
                        color="success"
                        size="small"
                      />
                    </Stack>
                    <Stack spacing={1}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>IP:</strong> {session.ip}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Location:</strong> {session.location}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Device:</strong> {session.device} ({session.browser})
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Login:</strong> {new Date(session.login_time).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Last Activity:</strong> {new Date(session.last_activity).toLocaleString()}
                      </Typography>
                    </Stack>
                  </CardContent>
                  <CardActions>
                    <Button size="small" startIcon={<ViewIcon />}>
                      View Details
                    </Button>
                    <Button
                      size="small"
                      startIcon={<BlockIcon />}
                      color="error"
                      onClick={() => handleTerminateSession(session.id)}
                    >
                      Terminate
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Security Policy Tab */}
        <TabPanel value={tabValue} index={4}>
          <Typography variant="h6" sx={{ mb: 2 }}>Security Policy Configuration</Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Password Policy</Typography>
                  <Stack spacing={2}>
                    <FormControlLabel
                      control={<Switch checked={securitySettings.password_policy?.require_uppercase} />}
                      label="Require Uppercase Letters"
                    />
                    <FormControlLabel
                      control={<Switch checked={securitySettings.password_policy?.require_lowercase} />}
                      label="Require Lowercase Letters"
                    />
                    <FormControlLabel
                      control={<Switch checked={securitySettings.password_policy?.require_numbers} />}
                      label="Require Numbers"
                    />
                    <FormControlLabel
                      control={<Switch checked={securitySettings.password_policy?.require_special} />}
                      label="Require Special Characters"
                    />
                    <Box>
                      <Typography variant="body2" color="text.secondary">Minimum Password Length</Typography>
                      <Slider
                        value={securitySettings.password_policy?.min_length || 8}
                        min={6}
                        max={20}
                        marks
                        valueLabelDisplay="auto"
                      />
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Session Policy</Typography>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Session Timeout (minutes)</Typography>
                      <Slider
                        value={securitySettings.session_policy?.timeout_minutes || 30}
                        min={5}
                        max={120}
                        marks
                        valueLabelDisplay="auto"
                      />
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Max Concurrent Sessions</Typography>
                      <Slider
                        value={securitySettings.session_policy?.max_concurrent_sessions || 3}
                        min={1}
                        max={10}
                        marks
                        valueLabelDisplay="auto"
                      />
                    </Box>
                    <FormControlLabel
                      control={<Switch checked={securitySettings.session_policy?.require_reauthentication} />}
                      label="Require Re-authentication for Sensitive Actions"
                    />
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Lockout Policy</Typography>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Max Login Attempts</Typography>
                      <Slider
                        value={securitySettings.lockout_policy?.max_attempts || 5}
                        min={3}
                        max={10}
                        marks
                        valueLabelDisplay="auto"
                      />
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Lockout Duration (minutes)</Typography>
                      <Slider
                        value={securitySettings.lockout_policy?.lockout_duration_minutes || 15}
                        min={5}
                        max={60}
                        marks
                        valueLabelDisplay="auto"
                      />
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Two-Factor Authentication</Typography>
                  <Stack spacing={2}>
                    <FormControlLabel
                      control={<Switch checked={securitySettings.two_factor_policy?.require_for_admin} />}
                      label="Require 2FA for Administrators"
                    />
                    <FormControlLabel
                      control={<Switch checked={securitySettings.two_factor_policy?.require_for_sensitive_roles} />}
                      label="Require 2FA for Sensitive Roles"
                    />
                    <Typography variant="body2" color="text.secondary">Allowed Methods:</Typography>
                    <Stack direction="row" spacing={1}>
                      <Chip label="App" color="primary" size="small" />
                      <Chip label="SMS" color="primary" size="small" />
                      <Chip label="Email" color="primary" size="small" />
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>

      {/* Two-Factor Setup Dialog */}
      <Dialog open={twoFactorDialog} onClose={() => setTwoFactorDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Setup Two-Factor Authentication</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>User</InputLabel>
                <Select
                  label="User"
                  value={twoFactorForm.user_id}
                  onChange={(e) => setTwoFactorForm({ ...twoFactorForm, user_id: e.target.value })}
                >
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="john.doe">John Doe</MenuItem>
                  <MenuItem value="jane.smith">Jane Smith</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>2FA Method</InputLabel>
                <Select
                  label="2FA Method"
                  value={twoFactorForm.method}
                  onChange={(e) => setTwoFactorForm({ ...twoFactorForm, method: e.target.value })}
                >
                  <MenuItem value="app">Authenticator App</MenuItem>
                  <MenuItem value="sms">SMS</MenuItem>
                  <MenuItem value="email">Email</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            {twoFactorForm.method === 'sms' && (
              <Grid item xs={12}>
                <TextField
                  label="Phone Number"
                  value={twoFactorForm.phone}
                  onChange={(e) => setTwoFactorForm({ ...twoFactorForm, phone: e.target.value })}
                  fullWidth
                  required
                />
              </Grid>
            )}
            {twoFactorForm.method === 'email' && (
              <Grid item xs={12}>
                <TextField
                  label="Email Address"
                  type="email"
                  value={twoFactorForm.email}
                  onChange={(e) => setTwoFactorForm({ ...twoFactorForm, email: e.target.value })}
                  fullWidth
                  required
                />
              </Grid>
            )}
            {twoFactorForm.method === 'app' && (
              <Grid item xs={12}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <QrCodeIcon sx={{ fontSize: 100, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Scan QR code with your authenticator app
                  </Typography>
                </Box>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTwoFactorDialog(false)}>Cancel</Button>
          <Button onClick={handleTwoFactorSubmit} variant="contained">Setup 2FA</Button>
        </DialogActions>
      </Dialog>

      {/* Security Policy Dialog */}
      <Dialog open={policyDialog} onClose={() => setPolicyDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Security Policy Configuration</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" sx={{ mb: 2 }}>Password Policy</Typography>
              <Stack spacing={2}>
                <TextField
                  label="Minimum Password Length"
                  type="number"
                  value={policyForm.password_min_length}
                  onChange={(e) => setPolicyForm({ ...policyForm, password_min_length: parseInt(e.target.value) })}
                  fullWidth
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={policyForm.password_require_uppercase}
                      onChange={(e) => setPolicyForm({ ...policyForm, password_require_uppercase: e.target.checked })}
                    />
                  }
                  label="Require Uppercase Letters"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={policyForm.password_require_lowercase}
                      onChange={(e) => setPolicyForm({ ...policyForm, password_require_lowercase: e.target.checked })}
                    />
                  }
                  label="Require Lowercase Letters"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={policyForm.password_require_numbers}
                      onChange={(e) => setPolicyForm({ ...policyForm, password_require_numbers: e.target.checked })}
                    />
                  }
                  label="Require Numbers"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={policyForm.password_require_special}
                      onChange={(e) => setPolicyForm({ ...policyForm, password_require_special: e.target.checked })}
                    />
                  }
                  label="Require Special Characters"
                />
                <TextField
                  label="Password Max Age (days)"
                  type="number"
                  value={policyForm.password_max_age_days}
                  onChange={(e) => setPolicyForm({ ...policyForm, password_max_age_days: parseInt(e.target.value) })}
                  fullWidth
                />
              </Stack>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" sx={{ mb: 2 }}>Session & Lockout Policy</Typography>
              <Stack spacing={2}>
                <TextField
                  label="Session Timeout (minutes)"
                  type="number"
                  value={policyForm.session_timeout_minutes}
                  onChange={(e) => setPolicyForm({ ...policyForm, session_timeout_minutes: parseInt(e.target.value) })}
                  fullWidth
                />
                <TextField
                  label="Max Login Attempts"
                  type="number"
                  value={policyForm.max_login_attempts}
                  onChange={(e) => setPolicyForm({ ...policyForm, max_login_attempts: parseInt(e.target.value) })}
                  fullWidth
                />
                <TextField
                  label="Lockout Duration (minutes)"
                  type="number"
                  value={policyForm.lockout_duration_minutes}
                  onChange={(e) => setPolicyForm({ ...policyForm, lockout_duration_minutes: parseInt(e.target.value) })}
                  fullWidth
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={policyForm.require_2fa_for_admin}
                      onChange={(e) => setPolicyForm({ ...policyForm, require_2fa_for_admin: e.target.checked })}
                    />
                  }
                  label="Require 2FA for Administrators"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={policyForm.require_2fa_for_sensitive_roles}
                      onChange={(e) => setPolicyForm({ ...policyForm, require_2fa_for_sensitive_roles: e.target.checked })}
                    />
                  }
                  label="Require 2FA for Sensitive Roles"
                />
              </Stack>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPolicyDialog(false)}>Cancel</Button>
          <Button onClick={handlePolicySubmit} variant="contained">Update Policy</Button>
        </DialogActions>
      </Dialog>

      {/* Audit Filter Dialog */}
      <Dialog open={auditFilterDialog} onClose={() => setAuditFilterDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Filter Audit Logs</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                label="Start Date"
                type="date"
                value={auditFilterForm.start_date}
                onChange={(e) => setAuditFilterForm({ ...auditFilterForm, start_date: e.target.value })}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="End Date"
                type="date"
                value={auditFilterForm.end_date}
                onChange={(e) => setAuditFilterForm({ ...auditFilterForm, end_date: e.target.value })}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Action Type</InputLabel>
                <Select
                  label="Action Type"
                  value={auditFilterForm.action_type}
                  onChange={(e) => setAuditFilterForm({ ...auditFilterForm, action_type: e.target.value })}
                >
                  <MenuItem value="">All Actions</MenuItem>
                  <MenuItem value="login">Login</MenuItem>
                  <MenuItem value="logout">Logout</MenuItem>
                  <MenuItem value="create">Create</MenuItem>
                  <MenuItem value="update">Update</MenuItem>
                  <MenuItem value="delete">Delete</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Resource Type</InputLabel>
                <Select
                  label="Resource Type"
                  value={auditFilterForm.resource_type}
                  onChange={(e) => setAuditFilterForm({ ...auditFilterForm, resource_type: e.target.value })}
                >
                  <MenuItem value="">All Resources</MenuItem>
                  <MenuItem value="user">User</MenuItem>
                  <MenuItem value="document">Document</MenuItem>
                  <MenuItem value="system">System</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAuditFilterDialog(false)}>Cancel</Button>
          <Button variant="contained">Apply Filter</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdvancedSecurity;
