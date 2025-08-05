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
  Switch,
  FormControlLabel,
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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Restore as RestoreIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Business as BusinessIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  Assignment as AssignmentIcon,
  LocalShipping as LocalShippingIcon,
  Timeline as TimelineIcon,
  School as SchoolIcon,
  Description as DescriptionIcon,
  IntegrationInstructions as IntegrationIcon,
  Person as PersonIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import { settingsAPI } from '../services/api';

// Interfaces
interface Setting {
  id: number;
  key: string;
  value: string;
  setting_type: string;
  category: string;
  display_name: string;
  description?: string;
  is_editable: boolean;
  is_required: boolean;
  validation_rules?: any;
  default_value?: string;
  group_name?: string;
  created_at: string;
  updated_at?: string;
}

interface SettingsCategory {
  category: string;
  settings: Setting[];
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

const Settings: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [settings, setSettings] = useState<SettingsCategory[]>([]);
  const [userPreferences, setUserPreferences] = useState<UserPreference[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Dialog states
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [selectedSetting, setSelectedSetting] = useState<Setting | null>(null);

  // Form states
  const [editedSettings, setEditedSettings] = useState<{ [key: string]: string }>({});

  // Load data on component mount
  useEffect(() => {
    fetchSettings();
    fetchUserPreferences();
  }, []);

  // API calls
  const fetchSettings = async () => {
    try {
      setLoading(true);
      const data = await settingsAPI.getSettings();
      setSettings(data.categories || []);
    } catch (err) {
      setError('Failed to load settings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserPreferences = async () => {
    try {
      const data = await settingsAPI.getUserPreferences();
      setUserPreferences(data || []);
    } catch (err) {
      console.error('Failed to load user preferences:', err);
    }
  };

  const handleSettingChange = (key: string, value: string) => {
    setEditedSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveSettings = async () => {
    try {
      setLoading(true);
      const settingsToUpdate = Object.entries(editedSettings).map(([key, value]) => ({ [key]: value }));
      
      if (settingsToUpdate.length > 0) {
        const result = await settingsAPI.bulkUpdateSettings(settingsToUpdate);
        
        if (result.valid) {
          setSuccess('Settings saved successfully!');
          setEditedSettings({});
          fetchSettings();
        } else {
          setError(`Failed to save some settings: ${result.errors.map((e: any) => e.error).join(', ')}`);
        }
      }
    } catch (err) {
      setError('Failed to save settings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInitializeSettings = async () => {
    try {
      setLoading(true);
      await settingsAPI.initializeSettings();
      setSuccess('Default settings initialized successfully!');
      fetchSettings();
    } catch (err) {
      setError('Failed to initialize settings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleResetSetting = async (setting: Setting) => {
    try {
      setLoading(true);
      await settingsAPI.resetSetting(setting.key);
      setSuccess(`Setting "${setting.display_name}" reset to default!`);
      fetchSettings();
      setResetDialogOpen(false);
      setSelectedSetting(null);
    } catch (err) {
      setError('Failed to reset setting');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportSettings = async () => {
    try {
      setLoading(true);
      const data = await settingsAPI.exportSettings();
      
      // Create and download file
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `settings_export_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setSuccess('Settings exported successfully!');
      setExportDialogOpen(false);
    } catch (err) {
      setError('Failed to export settings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleImportSettings = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setLoading(true);
      const text = await file.text();
      const data = JSON.parse(text);
      
      const result = await settingsAPI.importSettings(data);
      
      if (result.success) {
        setSuccess('Settings imported successfully!');
        fetchSettings();
      } else {
        setError(`Import completed with errors: ${result.message}`);
      }
      
      setImportDialogOpen(false);
    } catch (err) {
      setError('Failed to import settings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Utility functions
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'GENERAL': return <BusinessIcon />;
      case 'NOTIFICATIONS': return <NotificationsIcon />;
      case 'SECURITY': return <SecurityIcon />;
      case 'HACCP': return <AssessmentIcon />;
      case 'PRP': return <AssignmentIcon />;
      case 'SUPPLIERS': return <LocalShippingIcon />;
      case 'TRACEABILITY': return <TimelineIcon />;
      case 'AUDIT': return <DescriptionIcon />;
      case 'TRAINING': return <SchoolIcon />;
      case 'REPORTING': return <DescriptionIcon />;
      case 'INTEGRATION': return <IntegrationIcon />;
      default: return <SettingsIcon />;
    }
  };

  const getCategoryDisplayName = (category: string) => {
    return category.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  const renderSettingField = (setting: Setting) => {
    const value = editedSettings[setting.key] !== undefined ? editedSettings[setting.key] : setting.value;
    const isEdited = editedSettings[setting.key] !== undefined && editedSettings[setting.key] !== setting.value;

    switch (setting.setting_type) {
      case 'BOOLEAN':
        return (
          <FormControlLabel
            control={
              <Switch
                checked={value === 'true' || value === '1' || value === 'yes'}
                onChange={(e) => handleSettingChange(setting.key, e.target.checked ? 'true' : 'false')}
                disabled={!setting.is_editable}
              />
            }
            label={value === 'true' || value === '1' || value === 'yes' ? 'Enabled' : 'Disabled'}
          />
        );

      case 'INTEGER':
        return (
          <TextField
            fullWidth
            type="number"
            value={value}
            onChange={(e) => handleSettingChange(setting.key, e.target.value)}
            disabled={!setting.is_editable}
            size="small"
            InputProps={{
              endAdornment: isEdited && <Chip label="Modified" color="primary" size="small" />
            }}
          />
        );

      case 'EMAIL':
        return (
          <TextField
            fullWidth
            type="email"
            value={value}
            onChange={(e) => handleSettingChange(setting.key, e.target.value)}
            disabled={!setting.is_editable}
            size="small"
            InputProps={{
              endAdornment: isEdited && <Chip label="Modified" color="primary" size="small" />
            }}
          />
        );

      case 'URL':
        return (
          <TextField
            fullWidth
            type="url"
            value={value}
            onChange={(e) => handleSettingChange(setting.key, e.target.value)}
            disabled={!setting.is_editable}
            size="small"
            InputProps={{
              endAdornment: isEdited && <Chip label="Modified" color="primary" size="small" />
            }}
          />
        );

      default:
        return (
          <TextField
            fullWidth
            value={value}
            onChange={(e) => handleSettingChange(setting.key, e.target.value)}
            disabled={!setting.is_editable}
            size="small"
            InputProps={{
              endAdornment: isEdited && <Chip label="Modified" color="primary" size="small" />
            }}
          />
        );
    }
  };

  const renderSettingsCategory = (category: SettingsCategory) => (
    <Accordion key={category.category} defaultExpanded>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
          {getCategoryIcon(category.category)}
          <Typography variant="h6" sx={{ ml: 2 }}>
            {getCategoryDisplayName(category.category)}
          </Typography>
          <Chip 
            label={`${category.settings.length} settings`} 
            size="small" 
            sx={{ ml: 'auto' }}
          />
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Grid container spacing={2}>
          {category.settings.map((setting) => (
            <Grid item xs={12} md={6} key={setting.key}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {setting.display_name}
                    </Typography>
                    <Box>
                      {setting.is_required && (
                        <Chip label="Required" color="error" size="small" sx={{ mr: 1 }} />
                      )}
                      {!setting.is_editable && (
                        <Chip label="Read-only" size="small" />
                      )}
                    </Box>
                  </Box>
                  
                  {setting.description && (
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                      {setting.description}
                    </Typography>
                  )}
                  
                  {renderSettingField(setting)}
                  
                  {setting.default_value && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                      <Typography variant="caption" color="textSecondary">
                        Default: {setting.default_value}
                      </Typography>
                      <Button
                        size="small"
                        startIcon={<RestoreIcon />}
                        onClick={() => {
                          setSelectedSetting(setting);
                          setResetDialogOpen(true);
                        }}
                        disabled={!setting.is_editable}
                      >
                        Reset
                      </Button>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </AccordionDetails>
    </Accordion>
  );

  const renderUserPreferences = () => (
    <Box>
      <Typography variant="h4" gutterBottom>
        User Preferences
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        Manage your personal preferences and settings.
      </Typography>

      {userPreferences.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <PersonIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="textSecondary">
              No User Preferences
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Your personal preferences will appear here once you customize any settings.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <TableContainer component={Paper}>
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
              {userPreferences.map((pref) => (
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
                      <VisibilityIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );

  const renderSystemInfo = () => (
    <Box>
      <Typography variant="h4" gutterBottom>
        System Information
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        View system status and configuration details.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Application Details
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText 
                    primary="Application Name" 
                    secondary="ISO 22000 FSMS" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Version" 
                    secondary="1.0.0" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Environment" 
                    secondary="Development" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Database" 
                    secondary="SQLite" 
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
                System Status
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText 
                    primary="Backend Status" 
                    secondary={
                      <Chip 
                        icon={<CheckCircleIcon />} 
                        label="Online" 
                        color="success" 
                        size="small" 
                      />
                    } 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Database Status" 
                    secondary={
                      <Chip 
                        icon={<CheckCircleIcon />} 
                        label="Connected" 
                        color="success" 
                        size="small" 
                      />
                    } 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Settings Count" 
                    secondary={settings.reduce((acc, cat) => acc + cat.settings.length, 0)} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Last Backup" 
                    secondary="Never" 
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h3" gutterBottom>
        System Settings
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

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSaveSettings}
          disabled={loading || Object.keys(editedSettings).length === 0}
        >
          Save Changes
        </Button>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={handleInitializeSettings}
          disabled={loading}
        >
          Initialize Defaults
        </Button>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={() => setExportDialogOpen(true)}
          disabled={loading}
        >
          Export Settings
        </Button>
        <Button
          variant="outlined"
          startIcon={<UploadIcon />}
          onClick={() => setImportDialogOpen(true)}
          disabled={loading}
        >
          Import Settings
        </Button>
      </Box>

      {/* Loading Indicator */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Application Settings" icon={<SettingsIcon />} />
          <Tab label="User Preferences" icon={<PersonIcon />} />
          <Tab label="System Information" icon={<InfoIcon />} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Box>
          <Typography variant="h4" gutterBottom>
            Application Settings
          </Typography>
          <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
            Configure system-wide settings for the ISO 22000 FSMS application.
          </Typography>

          {settings.length === 0 ? (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <SettingsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="textSecondary">
                  No Settings Found
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Initialize default settings to get started.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<RefreshIcon />}
                  onClick={handleInitializeSettings}
                >
                  Initialize Default Settings
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Box>
              {settings.map(renderSettingsCategory)}
            </Box>
          )}
        </Box>
      )}

      {activeTab === 1 && renderUserPreferences()}
      {activeTab === 2 && renderSystemInfo()}

      {/* Import Dialog */}
      <Dialog open={importDialogOpen} onClose={() => setImportDialogOpen(false)}>
        <DialogTitle>Import Settings</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Select a JSON file to import settings. This will update existing settings with the values from the file.
          </Typography>
          <input
            accept=".json"
            style={{ display: 'none' }}
            id="import-file"
            type="file"
            onChange={handleImportSettings}
          />
          <label htmlFor="import-file">
            <Button variant="contained" component="span">
              Choose File
            </Button>
          </label>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportDialogOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      {/* Export Dialog */}
      <Dialog open={exportDialogOpen} onClose={() => setExportDialogOpen(false)}>
        <DialogTitle>Export Settings</DialogTitle>
        <DialogContent>
          <Typography variant="body2">
            Export all current settings to a JSON file. This file can be used to backup settings or import them to another system.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleExportSettings} variant="contained">
            Export
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reset Setting Dialog */}
      <Dialog open={resetDialogOpen} onClose={() => setResetDialogOpen(false)}>
        <DialogTitle>Reset Setting</DialogTitle>
        <DialogContent>
          {selectedSetting && (
            <Typography variant="body2">
              Are you sure you want to reset "{selectedSetting.display_name}" to its default value?
              This action cannot be undone.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={() => selectedSetting && handleResetSetting(selectedSetting)} 
            variant="contained" 
            color="warning"
          >
            Reset
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Settings; 