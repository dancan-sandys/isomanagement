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

const ManagementReviewActions: React.FC = () => {
  const [actions, setActions] = useState<any[]>([]);
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
  const [currentAction, setCurrentAction] = useState<any>(null);
  const [actionForm, setActionForm] = useState<ReviewActionPayload>({
    title: '',
    description: '',
    priority: 'medium',
    due_date: '',
    verification_required: false
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
        // For now, we'll load actions from all reviews
        // In a real implementation, this would be a dedicated endpoint
        const reviewsResp = await managementReviewAPI.list();
        const reviews = reviewsResp.data?.items || [];
        
        for (const review of reviews) {
          try {
            const actionsResp = await managementReviewAPI.listActions(review.id, statusFilter || undefined);
            const reviewActions = (actionsResp.data || []).map((action: any) => ({
              ...action,
              review_title: review.title,
              review_id: review.id
            }));
            allActions.push(...reviewActions);
          } catch (e) {
            console.error(`Failed to load actions for review ${review.id}:`, e);
          }
        }
      }

      // Apply priority filter
      if (priorityFilter) {
        allActions = allActions.filter(action => action.priority === priorityFilter);
      }

      setActions(allActions);
    } catch (e: any) {
      setError(e?.message || 'Failed to load actions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActions();
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
          <Button variant="outlined" startIcon={<DownloadIcon />}>
            Export
          </Button>
          <Button variant="contained" startIcon={<AddIcon />}>
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
                    <Typography variant="body2">{action.review_title}</Typography>
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
    </Box>
  );
};

export default ManagementReviewActions;