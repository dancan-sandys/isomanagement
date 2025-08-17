import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Pagination,
  Fab,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Schedule as ScheduleIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { auditsAPI } from '../services/api';

interface AuditProgram {
  id: number;
  name: string;
  description?: string;
  objectives: string;
  scope: string;
  year: number;
  period?: string;
  manager_id: number;
  risk_method: string;
  resources?: string;
  schedule?: any;
  kpis?: any;
  status: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

interface AuditProgramListResponse {
  items: AuditProgram[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

const AuditPrograms: React.FC = () => {
  const [programs, setPrograms] = useState<AuditProgram[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProgram, setEditingProgram] = useState<AuditProgram | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    size: 10,
    total: 0,
    pages: 0,
  });
  const [filters, setFilters] = useState({
    status: '',
    year: '',
    manager_id: '',
  });

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    objectives: '',
    scope: '',
    year: new Date().getFullYear(),
    period: '',
    manager_id: 1, // Default to current user
    risk_method: 'qualitative',
    resources: '',
    status: 'draft',
  });

  const loadPrograms = async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.page - 1, // API uses 0-based pagination
        size: pagination.size,
        status: filters.status || undefined,
        year: filters.year ? parseInt(filters.year) : undefined,
        manager_id: filters.manager_id ? parseInt(filters.manager_id) : undefined,
      };
      
      const response: AuditProgramListResponse = await auditsAPI.listPrograms(params);
      setPrograms(response.items);
      setPagination(prev => ({
        ...prev,
        total: response.total,
        pages: response.pages,
      }));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load audit programs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPrograms();
  }, [pagination.page, pagination.size, filters]);

  const handleCreate = () => {
    setEditingProgram(null);
    setFormData({
      name: '',
      description: '',
      objectives: '',
      scope: '',
      year: new Date().getFullYear(),
      period: '',
      manager_id: 1,
      risk_method: 'qualitative',
      resources: '',
      status: 'draft',
    });
    setDialogOpen(true);
  };

  const handleEdit = (program: AuditProgram) => {
    setEditingProgram(program);
    setFormData({
      name: program.name,
      description: program.description || '',
      objectives: program.objectives,
      scope: program.scope,
      year: program.year,
      period: program.period || '',
      manager_id: program.manager_id,
      risk_method: program.risk_method,
      resources: program.resources || '',
      status: program.status,
    });
    setDialogOpen(true);
  };

  const handleDelete = async (programId: number) => {
    if (window.confirm('Are you sure you want to delete this audit program?')) {
      try {
        await auditsAPI.deleteProgram(programId);
        loadPrograms();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to delete audit program');
      }
    }
  };

  const handleSubmit = async () => {
    try {
      if (editingProgram) {
        await auditsAPI.updateProgram(editingProgram.id, formData);
      } else {
        await auditsAPI.createProgram(formData);
      }
      setDialogOpen(false);
      loadPrograms();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save audit program');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'completed': return 'info';
      case 'archived': return 'default';
      default: return 'warning';
    }
  };

  const getRiskMethodColor = (method: string) => {
    switch (method) {
      case 'quantitative': return 'error';
      case 'hybrid': return 'warning';
      default: return 'primary';
    }
  };

  if (loading && programs.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Audit Programs
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          Create Program
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                  label="Status"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="archived">Archived</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                size="small"
                label="Year"
                type="number"
                value={filters.year}
                onChange={(e) => setFilters(prev => ({ ...prev, year: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Button
                variant="outlined"
                onClick={() => setFilters({ status: '', year: '', manager_id: '' })}
              >
                Clear Filters
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Programs Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Year</TableCell>
              <TableCell>Period</TableCell>
              <TableCell>Risk Method</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {programs.map((program) => (
              <TableRow key={program.id}>
                <TableCell>
                  <Typography variant="subtitle2">{program.name}</Typography>
                  {program.description && (
                    <Typography variant="body2" color="textSecondary">
                      {program.description}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>{program.year}</TableCell>
                <TableCell>{program.period || '-'}</TableCell>
                <TableCell>
                  <Chip
                    label={program.risk_method}
                    color={getRiskMethodColor(program.risk_method)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={program.status}
                    color={getStatusColor(program.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(program.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Schedule">
                    <IconButton size="small">
                      <ScheduleIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="KPIs">
                    <IconButton size="small">
                      <AssessmentIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton size="small" onClick={() => handleEdit(program)}>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton size="small" onClick={() => handleDelete(program.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {pagination.pages > 1 && (
        <Box display="flex" justifyContent="center" mt={2}>
          <Pagination
            count={pagination.pages}
            page={pagination.page}
            onChange={(_, page) => setPagination(prev => ({ ...prev, page }))}
          />
        </Box>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingProgram ? 'Edit Audit Program' : 'Create Audit Program'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Program Name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={2}
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Objectives"
                multiline
                rows={3}
                value={formData.objectives}
                onChange={(e) => setFormData(prev => ({ ...prev, objectives: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Scope"
                multiline
                rows={3}
                value={formData.scope}
                onChange={(e) => setFormData(prev => ({ ...prev, scope: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Year"
                type="number"
                value={formData.year}
                onChange={(e) => setFormData(prev => ({ ...prev, year: parseInt(e.target.value) }))}
                required
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Period</InputLabel>
                <Select
                  value={formData.period}
                  onChange={(e) => setFormData(prev => ({ ...prev, period: e.target.value }))}
                  label="Period"
                >
                  <MenuItem value="">None</MenuItem>
                  <MenuItem value="Q1">Q1</MenuItem>
                  <MenuItem value="Q2">Q2</MenuItem>
                  <MenuItem value="Q3">Q3</MenuItem>
                  <MenuItem value="Q4">Q4</MenuItem>
                  <MenuItem value="Annual">Annual</MenuItem>
                  <MenuItem value="H1">H1</MenuItem>
                  <MenuItem value="H2">H2</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Manager ID"
                type="number"
                value={formData.manager_id}
                onChange={(e) => setFormData(prev => ({ ...prev, manager_id: parseInt(e.target.value) }))}
                required
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Risk Method</InputLabel>
                <Select
                  value={formData.risk_method}
                  onChange={(e) => setFormData(prev => ({ ...prev, risk_method: e.target.value }))}
                  label="Risk Method"
                >
                  <MenuItem value="qualitative">Qualitative</MenuItem>
                  <MenuItem value="quantitative">Quantitative</MenuItem>
                  <MenuItem value="hybrid">Hybrid</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Resources"
                multiline
                rows={2}
                value={formData.resources}
                onChange={(e) => setFormData(prev => ({ ...prev, resources: e.target.value }))}
                placeholder="Budget, personnel, equipment..."
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value }))}
                  label="Status"
                >
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="archived">Archived</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingProgram ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AuditPrograms;
