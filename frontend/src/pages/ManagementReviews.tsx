import React, { useEffect, useState } from 'react';
import {
  Box, Button, Card, CardContent, Dialog, DialogActions, DialogContent, DialogTitle,
  Grid, LinearProgress, Stack, TextField, Typography, Chip, IconButton, Menu, MenuItem,
  FormControl, InputLabel, Select, Tabs, Tab, Badge, Alert, Divider, Paper,
  List, ListItem, ListItemText, ListItemIcon, Avatar, Tooltip, CardActions
} from '@mui/material';
import {
  Add as AddIcon, FilterList as FilterIcon, Analytics as AnalyticsIcon,
  Schedule as ScheduleIcon, Assignment as AssignmentIcon, CheckCircle as CheckCircleIcon,
  Warning as WarningIcon, TrendingUp as TrendingUpIcon, Dashboard as DashboardIcon,
  CalendarToday as CalendarIcon, Assessment as AssessmentIcon, Notifications as NotificationsIcon
} from '@mui/icons-material';
import managementReviewAPI, { MRPayload } from '../services/managementReviewAPI';
import { Link as RouterLink } from 'react-router-dom';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ManagementReviews: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [filterType, setFilterType] = useState<string>('');
  const [overdueActions, setOverdueActions] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [dashboardStats, setDashboardStats] = useState<any>({});
  
  const [form, setForm] = useState<MRPayload>({
    title: '',
    status: 'planned',
    review_type: 'scheduled',
    attendees: [],
    food_safety_policy_reviewed: false,
    food_safety_objectives_reviewed: false,
    fsms_changes_required: false
  });

  const load = async () => {
    setLoading(true); setError(null);
    try {
      const params: any = {};
      if (filterStatus) params.status = filterStatus;
      if (filterType) params.review_type = filterType;
      
      const resp = await managementReviewAPI.list(params);
      const data = resp.data || resp;
      setItems(data.items || []);
    } catch (e: any) {
      setError(e?.message || 'Failed to load management reviews');
    } finally { setLoading(false); }
  };

  const loadOverdueActions = async () => {
    try {
      const resp = await managementReviewAPI.getOverdueActions();
      setOverdueActions(resp.data || []);
    } catch (e) {
      console.error('Failed to load overdue actions:', e);
    }
  };

  const loadTemplates = async () => {
    try {
      const resp = await managementReviewAPI.listTemplates();
      setTemplates(resp.data || []);
    } catch (e) {
      console.error('Failed to load templates:', e);
    }
  };

  const loadDashboardStats = async () => {
    try {
      // Calculate basic stats from current data
      const totalReviews = items.length;
      const completedReviews = items.filter(r => r.status === 'completed').length;
      const inProgressReviews = items.filter(r => r.status === 'in_progress').length;
      const plannedReviews = items.filter(r => r.status === 'planned').length;
      
      setDashboardStats({
        totalReviews,
        completedReviews,
        inProgressReviews,
        plannedReviews,
        completionRate: totalReviews > 0 ? Math.round((completedReviews / totalReviews) * 100) : 0,
        overdueActions: overdueActions.length
      });
    } catch (e) {
      console.error('Failed to calculate dashboard stats:', e);
    }
  };

  useEffect(() => { 
    load(); 
    loadOverdueActions();
    loadTemplates();
  }, [filterStatus, filterType]);

  useEffect(() => {
    loadDashboardStats();
  }, [items, overdueActions]);

  const create = async () => {
    try {
      await managementReviewAPI.create(form);
      setOpen(false);
      setForm({
        title: '',
        status: 'planned',
        review_type: 'scheduled',
        attendees: [],
        food_safety_policy_reviewed: false,
        food_safety_objectives_reviewed: false,
        fsms_changes_required: false
      });
      load();
    } catch (e: any) {
      setError(e?.message || 'Failed to create review');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'warning';
      case 'planned': return 'info';
      default: return 'default';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'emergency': return <WarningIcon color="error" />;
      case 'ad_hoc': return <ScheduleIcon color="warning" />;
      default: return <CalendarIcon color="primary" />;
    }
  };

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>Management Reviews</Typography>
          <Typography variant="subtitle1" color="text.secondary">
            ISO 22000:2018 Compliant Management Review System
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            startIcon={<AssessmentIcon />}
            component={RouterLink}
            to="/management-reviews/analytics"
          >
            Analytics
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpen(true)}
          >
            New Review
          </Button>
        </Stack>
      </Stack>

      {/* Dashboard Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <DashboardIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">{dashboardStats.totalReviews || 0}</Typography>
                  <Typography variant="body2" color="text.secondary">Total Reviews</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <CheckCircleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">{dashboardStats.completionRate || 0}%</Typography>
                  <Typography variant="body2" color="text.secondary">Completion Rate</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <TrendingUpIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">{dashboardStats.inProgressReviews || 0}</Typography>
                  <Typography variant="body2" color="text.secondary">In Progress</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar sx={{ bgcolor: overdueActions.length > 0 ? 'error.main' : 'success.main' }}>
                  <Badge badgeContent={overdueActions.length} color="error">
                    <AssignmentIcon />
                  </Badge>
                </Avatar>
                <Box>
                  <Typography variant="h4">{overdueActions.length}</Typography>
                  <Typography variant="body2" color="text.secondary">Overdue Actions</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Overdue Actions Alert */}
      {overdueActions.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="subtitle2">
            {overdueActions.length} action{overdueActions.length > 1 ? 's' : ''} overdue. 
            <Button size="small" sx={{ ml: 1 }}>View Details</Button>
          </Typography>
        </Alert>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="All Reviews" />
          <Tab label="My Reviews" />
          <Tab label="Templates" />
          <Tab label="Analytics" />
        </Tabs>
      </Paper>

      {/* Tab Panels */}
      <TabPanel value={tabValue} index={0}>
        {/* Filters */}
        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              label="Status"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="planned">Planned</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              label="Type"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="scheduled">Scheduled</MenuItem>
              <MenuItem value="ad_hoc">Ad Hoc</MenuItem>
              <MenuItem value="emergency">Emergency</MenuItem>
            </Select>
          </FormControl>
        </Stack>

        {loading && <LinearProgress sx={{ mb: 2 }} />}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {/* Reviews Grid */}
        <Grid container spacing={3}>
          {items.map((review) => (
            <Grid item xs={12} md={6} lg={4} key={review.id}>
              <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1, mr: 1 }}>
                      {review.title}
                    </Typography>
                    {getTypeIcon(review.review_type || 'scheduled')}
                  </Stack>
                  
                  <Stack spacing={1}>
                    <Chip 
                      label={review.status} 
                      color={getStatusColor(review.status)} 
                      size="small"
                    />
                    
                    {review.review_date && (
                      <Typography variant="body2" color="text.secondary">
                        <CalendarIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
                        {new Date(review.review_date).toLocaleDateString()}
                      </Typography>
                    )}
                    
                    {review.review_effectiveness_score && (
                      <Typography variant="body2" color="text.secondary">
                        <TrendingUpIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
                        Effectiveness: {review.review_effectiveness_score}/10
                      </Typography>
                    )}
                    
                    {review.attendees && Array.isArray(review.attendees) && (
                      <Typography variant="body2" color="text.secondary">
                        {review.attendees.length} participant{review.attendees.length > 1 ? 's' : ''}
                      </Typography>
                    )}
                  </Stack>
                </CardContent>
                
                <CardActions>
                  <Button 
                    component={RouterLink} 
                    to={`/management-reviews/${review.id}`} 
                    size="small"
                    startIcon={<AssessmentIcon />}
                  >
                    Open Review
                  </Button>
                  {review.status === 'planned' && (
                    <Button size="small" color="success">
                      Start Review
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Typography variant="h6">My Reviews</Typography>
        <Typography variant="body2" color="text.secondary">
          Reviews where you are the chairperson or participant
        </Typography>
        {/* Implementation for user's specific reviews */}
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Typography variant="h6">Review Templates</Typography>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {templates.map((template) => (
            <Grid item xs={12} md={6} key={template.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{template.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {template.description}
                  </Typography>
                  <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
                    <Button size="small">Use Template</Button>
                    <Button size="small">Edit</Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Typography variant="h6">Analytics Dashboard</Typography>
        <Typography variant="body2" color="text.secondary">
          Comprehensive analytics and reporting for management reviews
        </Typography>
        {/* Analytics content will be implemented separately */}
      </TabPanel>

      {/* Enhanced Create Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>
          <Stack direction="row" alignItems="center" spacing={1}>
            <AddIcon />
            <Typography variant="h6">Create New Management Review</Typography>
          </Stack>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={8}>
              <TextField 
                label="Review Title" 
                fullWidth 
                value={form.title} 
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Review Type</InputLabel>
                <Select
                  value={form.review_type || 'scheduled'}
                  onChange={(e) => setForm({ ...form, review_type: e.target.value as any })}
                  label="Review Type"
                >
                  <MenuItem value="scheduled">Scheduled</MenuItem>
                  <MenuItem value="ad_hoc">Ad Hoc</MenuItem>
                  <MenuItem value="emergency">Emergency</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField 
                label="Review Date" 
                type="datetime-local"
                fullWidth 
                InputLabelProps={{ shrink: true }}
                value={form.review_date || ''}
                onChange={(e) => setForm({ ...form, review_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField 
                label="Next Review Date" 
                type="date"
                fullWidth 
                InputLabelProps={{ shrink: true }}
                value={form.next_review_date || ''}
                onChange={(e) => setForm({ ...form, next_review_date: e.target.value })}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField 
                label="Review Scope"
                fullWidth 
                multiline
                rows={2}
                value={form.review_scope || ''}
                onChange={(e) => setForm({ ...form, review_scope: e.target.value })}
                placeholder="Define the scope and areas to be covered in this review..."
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>ISO 22000:2018 Compliance Elements</Typography>
              <Stack spacing={1}>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <input 
                    type="checkbox" 
                    checked={form.food_safety_policy_reviewed || false}
                    onChange={(e) => setForm({ ...form, food_safety_policy_reviewed: e.target.checked })}
                  />
                  <Typography variant="body2">Food Safety Policy Review Required</Typography>
                </Stack>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <input 
                    type="checkbox" 
                    checked={form.food_safety_objectives_reviewed || false}
                    onChange={(e) => setForm({ ...form, food_safety_objectives_reviewed: e.target.checked })}
                  />
                  <Typography variant="body2">Food Safety Objectives Review Required</Typography>
                </Stack>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <input 
                    type="checkbox" 
                    checked={form.fsms_changes_required || false}
                    onChange={(e) => setForm({ ...form, fsms_changes_required: e.target.checked })}
                  />
                  <Typography variant="body2">FSMS Changes May Be Required</Typography>
                </Stack>
              </Stack>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={create} disabled={!form.title}>
            Create Review
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ManagementReviews;


