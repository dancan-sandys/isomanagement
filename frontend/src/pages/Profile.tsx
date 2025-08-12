import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Tabs,
  Tab,
  TextField,
  Avatar,
  Grid,
  Alert,
  LinearProgress,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Person as PersonIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Camera as CameraIcon,
  Delete as DeleteIcon,
  Lock as LockIcon,
  Security as SecurityIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  CalendarToday as CalendarIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon
} from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import api, { settingsAPI, authAPI } from '../services/api';

// Interfaces
interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  department?: string;
  position?: string;
  phone?: string;
  employee_id?: string;
  profile_picture?: string;
  bio?: string;
  last_login?: string;
}

interface UserPreference {
  id: number;
  user_id: number;
  key: string;
  value: string;
  setting_type: string;
  created_at: string;
  updated_at?: string;
}

interface ActivityData {
  last_login?: string;
  created_at: string;
  updated_at: string;
  failed_login_attempts: number;
  is_locked: boolean;
  locked_until?: string;
}

interface SecurityData {
  is_active: boolean;
  is_verified: boolean;
  failed_login_attempts: number;
  locked_until?: string;
  last_login?: string;
  account_created: string;
  last_updated: string;
}

const Profile: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Profile data
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedProfile, setEditedProfile] = useState<Partial<UserProfile>>({});

  // Password change
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });

  // Avatar upload
  const [avatarDialogOpen, setAvatarDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // User preferences
  const [preferences, setPreferences] = useState<UserPreference[]>([]);
  const [activityData, setActivityData] = useState<ActivityData | null>(null);
  const [securityData, setSecurityData] = useState<SecurityData | null>(null);

  // Get current user from Redux store
  const currentUser = useSelector((state: RootState) => state.auth.user);

  // Load data on component mount
  useEffect(() => {
    if (currentUser) {
      fetchProfile();
      fetchPreferences();
      fetchActivityData();
      fetchSecurityData();
    }
  }, [currentUser]); // eslint-disable-line react-hooks/exhaustive-deps

  // API calls
  const fetchProfile = async () => {
    try {
      setLoading(true);
      const resp = await api.get('/profile/me');
      const data = resp?.data?.data || resp?.data || resp;
      // Backend returns UserProfile shape; adapt role field for local UI type if needed
      const adapted: UserProfile = {
        id: data.id,
        username: data.username,
        email: data.email,
        full_name: data.full_name,
        role: data.role_name || '',
        department: data.department,
        position: data.position,
        phone: data.phone,
        employee_id: data.employee_id,
        profile_picture: data.profile_picture,
        bio: data.bio,
        last_login: data.last_login,
      };
      setProfile(adapted);
    } catch (err) {
      setError('Failed to load profile');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPreferences = async () => {
    try {
      const resp = await api.get('/settings/preferences/me');
      const prefs = resp?.data || [];
      setPreferences(prefs);
    } catch (err) {
      console.error('Failed to load preferences:', err);
    }
  };

  const fetchActivityData = async () => {
    try {
      const resp = await api.get('/profile/me/activity');
      const data = resp?.data?.data || resp?.data || null;
      setActivityData(data);
    } catch (err) {
      console.error('Failed to load activity data:', err);
    }
  };

  const fetchSecurityData = async () => {
    try {
      const resp = await api.get('/profile/me/security');
      const data = resp?.data?.data || resp?.data || null;
      setSecurityData(data);
    } catch (err) {
      console.error('Failed to load security data:', err);
    }
  };

  const handleProfileUpdate = async () => {
    try {
      setLoading(true);
      const form = new FormData();
      if (editedProfile.full_name !== undefined) form.append('full_name', editedProfile.full_name);
      if (editedProfile.department !== undefined) form.append('department', editedProfile.department);
      if (editedProfile.position !== undefined) form.append('position', editedProfile.position);
      if (editedProfile.phone !== undefined) form.append('phone', editedProfile.phone);
      if (editedProfile.bio !== undefined) form.append('bio', editedProfile.bio);
      await api.put('/profile/me', form);
      
      if (profile) {
        setProfile({ ...profile, ...editedProfile });
        setSuccess('Profile updated successfully!');
        setIsEditing(false);
        setEditedProfile({});
      }
    } catch (err) {
      setError('Failed to update profile');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    try {
      setLoading(true);
      await api.post('/profile/me/change-password', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      });
      
      setSuccess('Password changed successfully!');
      setPasswordDialogOpen(false);
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (err) {
      setError('Failed to change password');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUpload = async () => {
    if (!selectedFile) return;

    try {
      setLoading(true);
      const form = new FormData();
      form.append('file', selectedFile);
      await api.post('/profile/me/upload-avatar', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      setSuccess('Avatar uploaded successfully!');
      setAvatarDialogOpen(false);
      setSelectedFile(null);
      // Refresh profile to show new avatar
      fetchProfile();
    } catch (err) {
      setError('Failed to upload avatar');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const renderProfileTab = () => (
    <Box>
      <Typography variant="h4" gutterBottom>
        Profile Information
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        Manage your personal information and profile settings.
      </Typography>

      {profile && (
        <Grid container spacing={3}>
          {/* Profile Picture */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Avatar
                  src={profile.profile_picture}
                  sx={{ width: 120, height: 120, mx: 'auto', mb: 2 }}
                >
                  {profile.full_name.split(' ').map(n => n[0]).join('')}
                </Avatar>
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                  <Button
                    variant="outlined"
                    startIcon={<CameraIcon />}
                    onClick={() => setAvatarDialogOpen(true)}
                    size="small"
                  >
                    Upload
                  </Button>
                  {profile.profile_picture && (
                    <Button
                      variant="outlined"
                      startIcon={<DeleteIcon />}
                      color="error"
                      size="small"
                    >
                      Remove
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Profile Details */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">Personal Information</Typography>
                  <Button
                    variant={isEditing ? "contained" : "outlined"}
                    startIcon={isEditing ? <SaveIcon /> : <EditIcon />}
                    onClick={isEditing ? handleProfileUpdate : () => setIsEditing(true)}
                    disabled={loading}
                  >
                    {isEditing ? 'Save' : 'Edit'}
                  </Button>
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Full Name"
                      value={isEditing ? (editedProfile.full_name ?? profile.full_name) : profile.full_name}
                      onChange={(e) => setEditedProfile({ ...editedProfile, full_name: e.target.value })}
                      disabled={!isEditing}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      value={profile.email}
                      disabled
                      margin="normal"
                      helperText="Email cannot be changed"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Department"
                      value={isEditing ? (editedProfile.department ?? profile.department) : profile.department}
                      onChange={(e) => setEditedProfile({ ...editedProfile, department: e.target.value })}
                      disabled={!isEditing}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Position"
                      value={isEditing ? (editedProfile.position ?? profile.position) : profile.position}
                      onChange={(e) => setEditedProfile({ ...editedProfile, position: e.target.value })}
                      disabled={!isEditing}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Phone"
                      value={isEditing ? (editedProfile.phone ?? profile.phone) : profile.phone}
                      onChange={(e) => setEditedProfile({ ...editedProfile, phone: e.target.value })}
                      disabled={!isEditing}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Employee ID"
                      value={profile.employee_id}
                      disabled
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Bio"
                      value={isEditing ? (editedProfile.bio ?? profile.bio) : profile.bio}
                      onChange={(e) => setEditedProfile({ ...editedProfile, bio: e.target.value })}
                      disabled={!isEditing}
                      margin="normal"
                      multiline
                      rows={3}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );

  const renderSecurityTab = () => (
    <Box>
      <Typography variant="h4" gutterBottom>
        Security Settings
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        Manage your account security and password settings.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Change Password
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Update your password to keep your account secure.
              </Typography>
              <Button
                variant="contained"
                startIcon={<LockIcon />}
                onClick={() => setPasswordDialogOpen(true)}
              >
                Change Password
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Account Status
              </Typography>
              {securityData && (
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      {securityData.is_active ? <CheckCircleIcon color="success" /> : <ErrorIcon color="error" />}
                    </ListItemIcon>
                    <ListItemText 
                      primary="Account Status" 
                      secondary={securityData.is_active ? 'Active' : 'Inactive'} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      {securityData.is_verified ? <CheckCircleIcon color="success" /> : <WarningIcon color="warning" />}
                    </ListItemIcon>
                    <ListItemText 
                      primary="Email Verification" 
                      secondary={securityData.is_verified ? 'Verified' : 'Not Verified'} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <SecurityIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Failed Login Attempts" 
                      secondary={securityData.failed_login_attempts} 
                    />
                  </ListItem>
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderPreferencesTab = () => (
    <Box>
      <Typography variant="h4" gutterBottom>
        User Preferences
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        Customize your application preferences and settings.
      </Typography>

      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Preference</TableCell>
                  <TableCell>Value</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Last Updated</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {preferences.map((pref) => (
                  <TableRow key={pref.id}>
                    <TableCell>{pref.key}</TableCell>
                    <TableCell>{pref.value}</TableCell>
                    <TableCell>
                      <Chip label={pref.setting_type} size="small" />
                    </TableCell>
                    <TableCell>
                      {new Date(pref.updated_at || pref.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <EditIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );

  const renderActivityTab = () => (
    <Box>
      <Typography variant="h4" gutterBottom>
        Activity History
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        View your account activity and login history.
      </Typography>

      {activityData && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <CalendarIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Last Login" 
                      secondary={activityData.last_login ? new Date(activityData.last_login).toLocaleString() : 'Never'} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <HistoryIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Account Created" 
                      secondary={new Date(activityData.created_at).toLocaleDateString()} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <EditIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Last Updated" 
                      secondary={new Date(activityData.updated_at).toLocaleDateString()} 
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Security Events
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <WarningIcon color="warning" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Failed Login Attempts" 
                      secondary={activityData.failed_login_attempts} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      {activityData.is_locked ? <ErrorIcon color="error" /> : <CheckCircleIcon color="success" />}
                    </ListItemIcon>
                    <ListItemText 
                      primary="Account Locked" 
                      secondary={activityData.is_locked ? 'Yes' : 'No'} 
                    />
                  </ListItem>
                  {activityData.locked_until && (
                    <ListItem>
                      <ListItemIcon>
                        <LockIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Locked Until" 
                        secondary={new Date(activityData.locked_until).toLocaleString()} 
                      />
                    </ListItem>
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h3" gutterBottom>
        My Profile
      </Typography>

      {/* Success/Error Alerts */}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Loading Indicator */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Profile" icon={<PersonIcon />} />
          <Tab label="Security" icon={<SecurityIcon />} />
          <Tab label="Preferences" icon={<SettingsIcon />} />
          <Tab label="Activity" icon={<HistoryIcon />} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && renderProfileTab()}
      {activeTab === 1 && renderSecurityTab()}
      {activeTab === 2 && renderPreferencesTab()}
      {activeTab === 3 && renderActivityTab()}

      {/* Password Change Dialog */}
      <Dialog open={passwordDialogOpen} onClose={() => setPasswordDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            type={showPasswords.current ? 'text' : 'password'}
            label="Current Password"
            value={passwordData.current_password}
            onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
            margin="normal"
            InputProps={{
              endAdornment: (
                <IconButton
                  onClick={() => setShowPasswords({ ...showPasswords, current: !showPasswords.current })}
                >
                  {showPasswords.current ? <VisibilityOffIcon /> : <VisibilityIcon />}
                </IconButton>
              )
            }}
          />
          <TextField
            fullWidth
            type={showPasswords.new ? 'text' : 'password'}
            label="New Password"
            value={passwordData.new_password}
            onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
            margin="normal"
            InputProps={{
              endAdornment: (
                <IconButton
                  onClick={() => setShowPasswords({ ...showPasswords, new: !showPasswords.new })}
                >
                  {showPasswords.new ? <VisibilityOffIcon /> : <VisibilityIcon />}
                </IconButton>
              )
            }}
          />
          <TextField
            fullWidth
            type={showPasswords.confirm ? 'text' : 'password'}
            label="Confirm New Password"
            value={passwordData.confirm_password}
            onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
            margin="normal"
            InputProps={{
              endAdornment: (
                <IconButton
                  onClick={() => setShowPasswords({ ...showPasswords, confirm: !showPasswords.confirm })}
                >
                  {showPasswords.confirm ? <VisibilityOffIcon /> : <VisibilityIcon />}
                </IconButton>
              )
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPasswordDialogOpen(false)}>Cancel</Button>
          <Button onClick={handlePasswordChange} variant="contained" disabled={loading}>
            Change Password
          </Button>
        </DialogActions>
      </Dialog>

      {/* Avatar Upload Dialog */}
      <Dialog open={avatarDialogOpen} onClose={() => setAvatarDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Profile Picture</DialogTitle>
        <DialogContent>
          <input
            accept="image/*"
            style={{ display: 'none' }}
            id="avatar-file"
            type="file"
            onChange={handleFileSelect}
          />
          <label htmlFor="avatar-file">
            <Button variant="contained" component="span" sx={{ mb: 2 }}>
              Choose File
            </Button>
          </label>
          {selectedFile && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected: {selectedFile.name}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAvatarDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAvatarUpload} variant="contained" disabled={!selectedFile || loading}>
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Profile;
 