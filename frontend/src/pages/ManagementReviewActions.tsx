import React, { useEffect, useState } from 'react';
import {
  Box, Card, CardContent, Grid, Typography, Stack, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, IconButton, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, FormControl, InputLabel, Select, MenuItem, Switch,
  FormControlLabel, Alert, LinearProgress, Avatar, Tooltip,
  TablePagination, Checkbox, Menu, ListItemIcon, ListItemText
} from '@mui/material';
import {
  Assignment as AssignmentIcon, Edit as EditIcon, Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon, Warning as WarningIcon, Schedule as ScheduleIcon,
  Person as PersonIcon, MoreVert as MoreVertIcon, PlayArrow as StartIcon,
  Pause as PauseIcon, Stop as StopIcon, Visibility as ViewIcon,
  FilterList as FilterIcon, Download as DownloadIcon, Add as AddIcon
} from '@mui/icons-material';
import managementReviewAPI, { ReviewActionPayload } from '../services/managementReviewAPI';
import { actionsLogAPI } from '../services/actionsLogAPI';
import { ActionLog, ActionSource, ActionPriority } from '../types/actionsLog';

const ManagementReviewActions: React.FC = (): JSX.Element => {
  const [actions, setActions] = useState<any[]>([]);
  const [actionsLogEntries, setActionsLogEntries] = useState<ActionLog[]>([]);
  const [showActionsLog, setShowActionsLog] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedActions, setSelectedActions] = useState<number[]>([]);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [overdueOnly, setOverdueOnly] = useState(false);
  
  // Dialog states
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [currentAction, setCurrentAction] = useState<any>(null);
  const [actionForm, setActionForm] = useState<ReviewActionPayload>({
    title: '',
    description: '',
    priority: 'medium',
    due_date: '',
    verification_required: false,
    resource_requirements: ''
  });

  // Menu state
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuActionId, setMenuActionId] = useState<number | null>(null);

  const loadActions = async () => {
    setLoading(true);
    setError(null);
    try {
      let allActions: any[] = [];
      
      if (overdueOnly) {
        const resp = await managementReviewAPI.getOverdueActions();
        allActions = resp.data || [];
      } else {
        // Load actions from management reviews
        try {
          const reviewsResp = await managementReviewAPI.list();
          const reviews = reviewsResp.data?.items || [];
          
          for (const review of reviews) {
            try {
              const actionsResp = await managementReviewAPI.listActions(review.id, statusFilter || undefined);
              const reviewActions = (actionsResp.data || []).map((action: any) => ({
                ...action,
                review_title: review.title,
                review_id: review.id,
                source: 'management_review'
              }));
              allActions.push(...reviewActions);
            } catch (e) {
              console.error(`Failed to load actions for review ${review.id}:`, e);
            }
          }
        } catch (e) {
          console.error('Failed to load management review actions:', e);
        }
        
        // Also load actions from actions log (management review source)
        try {
          const actionsLogActions = await actionsLogAPI.getActionsBySource('management_review');
          const logActions = actionsLogActions.map((action: any) => ({
            ...action,
            review_title: 'Actions Log',
            review_id: null,
            source: 'actions_log'
          }));
          allActions.push(...logActions);
        } catch (e) {
          console.error('Failed to load actions log actions:', e);
        }
      }

      // Apply priority filter
      if (priorityFilter) {
        allActions = allActions.filter(action => action.priority === priorityFilter);
      }

      // Sort by creation date (newest first)
      allActions.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

      setActions(allActions);
    } catch (e: any) {
      setError(e?.message || 'Failed to load actions');
    } finally {
      setLoading(false);
    }
  };

  const loadActionsLogEntries = async () => {
    try {
      const allActionsLogEntries = await actionsLogAPI.getActionsBySource('management_review');
      setActionsLogEntries(allActionsLogEntries);
    } catch (e: any) {
      console.error('Failed to load actions log entries:', e);
    }
  };

  useEffect(() => {
    loadActions();
    loadActionsLogEntries();
  }, [statusFilter, priorityFilter, overdueOnly]);

  const handleSelectAction = (actionId: number) => {
    setSelectedActions(prev => 
      prev.includes(actionId) 
        ? prev.filter(id => id !== actionId)
        : [...prev, actionId]
    );
  };

  const handleSelectAll = () => {
    setSelectedActions(
      selectedActions.length === actions.length ? [] : actions.map(a => a.id)
    );
  };

  const openCreateDialog = () => {
    setActionForm({
      title: '',
      description: '',
      priority: 'medium',
      due_date: '',
      verification_required: false,
      resource_requirements: ''
    });
    setCreateDialogOpen(true);
  };

  const createAction = async () => {
    try {
      // Create action in the actions log first
      const actionLogEntry = await actionsLogAPI.createAction({
        title: actionForm.title,
        description: actionForm.description,
        action_source: ActionSource.MANAGEMENT_REVIEW,
        priority: getActionPriority(actionForm.priority),
        due_date: actionForm.due_date,
        assigned_by: 2 // Default to admin user for now
      });

      // Then create the review action
      // Note: This would need to be associated with a specific review
      // For now, we'll create it in the actions log
      setCreateDialogOpen(false);
      setActionForm({
        title: '',
        description: '',
        priority: 'medium',
        due_date: '',
        verification_required: false,
        resource_requirements: ''
      });
      await loadActions();
      await loadActionsLogEntries();
    } catch (e: any) {
      setError(e?.message || 'Failed to create action');
    }
  };

  const openEditDialog = (action: any) => {
    setCurrentAction(action);
    setActionForm({
      title: action.title,
      description: action.description || '',
      priority: action.priority,
      due_date: action.due_date ? action.due_date.split('T')[0] : '',
      verification_required: action.verification_required || false
    });
    setEditDialogOpen(true);
    setAnchorEl(null);
  };

  const updateAction = async () => {
    if (!currentAction) return;
    
    try {
      await managementReviewAPI.updateAction(currentAction.id, actionForm);
      setEditDialogOpen(false);
      setCurrentAction(null);
      await loadActions();
    } catch (e: any) {
      setError(e?.message || 'Failed to update action');
    }
  };

  const completeAction = async (actionId: number) => {
    try {
      await managementReviewAPI.completeAction(actionId);
      await loadActions();
    } catch (e: any) {
      setError(e?.message || 'Failed to complete action');
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'warning';
      case 'overdue': return 'error';
      case 'assigned': return 'info';
      default: return 'default';
    }
  };

  const isOverdue = (action: any) => {
    return action.due_date && new Date(action.due_date) < new Date() && !action.completed;
  };

  const getDaysUntilDue = (dueDate: string) => {
    const due = new Date(dueDate);
    const now = new Date();
    const diffTime = due.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getActionPriority = (priority: string): ActionPriority => {
    switch (priority) {
      case 'low': return ActionPriority.LOW;
      case 'medium': return ActionPriority.MEDIUM;
      case 'high': return ActionPriority.HIGH;
      case 'critical': return ActionPriority.CRITICAL;
      default: return ActionPriority.MEDIUM;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>Action Item Tracking</Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Comprehensive tracking of management review action items
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
          <FormControlLabel
            control={
              <Switch
                checked={showActionsLog}
                onChange={(e) => setShowActionsLog(e.target.checked)}
              />
            }
            label="Show Actions Log View"
          />
          <Button variant="outlined" startIcon={<DownloadIcon />}>
            Export
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={openCreateDialog}>
            New Action
          </Button>
        </Stack>
      </Stack>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <AssignmentIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">{actions.length}</Typography>
                  <Typography variant="body2" color="text.secondary">Total Actions</Typography>
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
                  <Typography variant="h4">
                    {actions.filter(a => a.completed).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">Completed</Typography>
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
                  <ScheduleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">
                    {actions.filter(a => a.status === 'in_progress').length}
                  </Typography>
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
                <Avatar sx={{ bgcolor: 'error.main' }}>
                  <WarningIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">
                    {actions.filter(a => isOverdue(a)).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">Overdue</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <FilterIcon color="action" />
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              label="Status"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="assigned">Assigned</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="overdue">Overdue</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Priority</InputLabel>
            <Select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              label="Priority"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </Select>
          </FormControl>
          
          <FormControlLabel
            control={
              <Switch
                checked={overdueOnly}
                onChange={(e) => setOverdueOnly(e.target.checked)}
              />
            }
            label="Overdue Only"
          />
        </Stack>
      </Paper>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Actions Log Section */}
      {showActionsLog && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Actions Log Entries from Management Reviews
          </Typography>
          <Grid container spacing={2}>
            {actionsLogEntries.map((logEntry) => (
              <Grid item xs={12} md={6} lg={4} key={logEntry.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Typography variant="h6" sx={{ maxWidth: '70%' }}>
                        {logEntry.title}
                      </Typography>
                      <Chip
                        label={logEntry.status.replace(/_/g, ' ')}
                        color={logEntry.status === 'completed' ? 'success' : 
                               logEntry.status === 'in_progress' ? 'primary' : 
                               logEntry.status === 'overdue' ? 'error' : 'warning'}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {logEntry.description}
                    </Typography>
                    <Box display="flex" alignItems="center" mb={2}>
                      <PersonIcon color="action" sx={{ mr: 1 }} />
                      <Typography variant="body2">
                        {logEntry.assigned_user_name || 'Unassigned'}
                      </Typography>
                    </Box>
                    <Box mb={2}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="body2" color="text.secondary">
                          Progress
                        </Typography>
                        <Typography variant="body2">
                          {logEntry.progress_percent}%
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={logEntry.progress_percent}
                        color={logEntry.progress_percent === 100 ? 'success' : 'primary'}
                      />
                    </Box>
                    {logEntry.tags?.review_title && (
                      <Typography variant="caption" color="text.secondary">
                        From: {logEntry.tags.review_title}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Actions Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedActions.length === actions.length && actions.length > 0}
                    indeterminate={selectedActions.length > 0 && selectedActions.length < actions.length}
                    onChange={handleSelectAll}
                  />
                </TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Review</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Due Date</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {actions
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((action) => (
                <TableRow key={action.id} hover>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedActions.includes(action.id)}
                      onChange={() => handleSelectAction(action.id)}
                    />
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="subtitle2">{action.title}</Typography>
                      {action.description && (
                        <Typography variant="body2" color="text.secondary" noWrap>
                          {action.description}
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">{action.review_title}</Typography>
                      {action.source && (
                        <Chip 
                          label={action.source === 'actions_log' ? 'Actions Log' : 'Review'} 
                          size="small" 
                          variant="outlined"
                          color={action.source === 'actions_log' ? 'primary' : 'secondary'}
                          sx={{ mt: 0.5 }}
                        />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={action.priority} 
                      color={getPriorityColor(action.priority)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={action.status} 
                      color={getStatusColor(action.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {action.due_date ? (
                      <Box>
                        <Typography variant="body2">
                          {new Date(action.due_date).toLocaleDateString()}
                        </Typography>
                        {isOverdue(action) ? (
                          <Chip label="Overdue" color="error" size="small" />
                        ) : (
                          <Typography variant="caption" color="text.secondary">
                            {getDaysUntilDue(action.due_date)} days
                          </Typography>
                        )}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">No due date</Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Box sx={{ width: 100 }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={action.progress_percentage || 0}
                        sx={{ mb: 0.5 }}
                      />
                      <Typography variant="caption">
                        {action.progress_percentage || 0}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1}>
                      {!action.completed && (
                        <Tooltip title="Complete Action">
                          <IconButton 
                            size="small" 
                            color="success"
                            onClick={() => completeAction(action.id)}
                          >
                            <CheckCircleIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      <Tooltip title="More Options">
                        <IconButton 
                          size="small"
                          onClick={(e) => {
                            setAnchorEl(e.currentTarget);
                            setMenuActionId(action.id);
                          }}
                        >
                          <MoreVertIcon />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={actions.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Paper>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem onClick={() => {
          const action = actions.find(a => a.id === menuActionId);
          if (action) openEditDialog(action);
        }}>
          <ListItemIcon><EditIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Edit Action</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => {
          // View action details
          setAnchorEl(null);
        }}>
          <ListItemIcon><ViewIcon fontSize="small" /></ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => {
          if (menuActionId) completeAction(menuActionId);
        }}>
          <ListItemIcon><CheckCircleIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Mark Complete</ListItemText>
        </MenuItem>
      </Menu>

      {/* Edit Action Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Edit Action Item</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Action Title"
              fullWidth
              value={actionForm.title}
              onChange={(e) => setActionForm({ ...actionForm, title: e.target.value })}
              required
            />
            
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={actionForm.description}
              onChange={(e) => setActionForm({ ...actionForm, description: e.target.value })}
            />
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={actionForm.priority}
                    onChange={(e) => setActionForm({ ...actionForm, priority: e.target.value as any })}
                    label="Priority"
                  >
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="critical">Critical</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  label="Due Date"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                  value={actionForm.due_date}
                  onChange={(e) => setActionForm({ ...actionForm, due_date: e.target.value })}
                />
              </Grid>
            </Grid>
            
            <TextField
              label="Resource Requirements"
              fullWidth
              multiline
              rows={2}
              value={actionForm.resource_requirements || ''}
              onChange={(e) => setActionForm({ ...actionForm, resource_requirements: e.target.value })}
              placeholder="Describe any resource requirements for this action..."
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={actionForm.verification_required}
                  onChange={(e) => setActionForm({ ...actionForm, verification_required: e.target.checked })}
                />
              }
              label="Verification Required Upon Completion"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={updateAction} disabled={!actionForm.title}>
            Update Action
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Action Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Create New Action Item</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Action Title"
              fullWidth
              value={actionForm.title}
              onChange={(e) => setActionForm({ ...actionForm, title: e.target.value })}
              required
            />
            
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={actionForm.description}
              onChange={(e) => setActionForm({ ...actionForm, description: e.target.value })}
            />
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={actionForm.priority}
                    onChange={(e) => setActionForm({ ...actionForm, priority: e.target.value as any })}
                    label="Priority"
                  >
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="critical">Critical</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  label="Due Date"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                  value={actionForm.due_date}
                  onChange={(e) => setActionForm({ ...actionForm, due_date: e.target.value })}
                />
              </Grid>
            </Grid>
            
            <TextField
              label="Resource Requirements"
              fullWidth
              multiline
              rows={2}
              value={actionForm.resource_requirements || ''}
              onChange={(e) => setActionForm({ ...actionForm, resource_requirements: e.target.value })}
              placeholder="Describe any resource requirements for this action..."
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={actionForm.verification_required}
                  onChange={(e) => setActionForm({ ...actionForm, verification_required: e.target.checked })}
                />
              }
              label="Verification Required Upon Completion"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={createAction} disabled={!actionForm.title}>
            Create Action
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ManagementReviewActions;