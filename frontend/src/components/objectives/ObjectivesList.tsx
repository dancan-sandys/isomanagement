import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Tooltip,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Collapse,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import { objectivesService } from '../../services/objectivesService';
import { Objective, ObjectiveType, HierarchyLevel } from '../../types/objectives';
import ObjectiveForm from './ObjectiveForm';
import ObjectiveDetail from './ObjectiveDetail';
import ProgressChart from './ProgressChart';

interface ObjectivesListProps {
  onObjectiveSelect?: (objective: Objective) => void;
  refreshTrigger?: number;
}

const ObjectivesList: React.FC<ObjectivesListProps> = ({ onObjectiveSelect, refreshTrigger }) => {
  const [objectives, setObjectives] = useState<Objective[]>([]);
  const [filteredObjectives, setFilteredObjectives] = useState<Objective[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<ObjectiveType | 'all'>('all');
  const [levelFilter, setLevelFilter] = useState<HierarchyLevel | 'all'>('all');
  const [departmentFilter, setDepartmentFilter] = useState<string>('all');

  // Modal states
  const [showForm, setShowForm] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const [selectedObjective, setSelectedObjective] = useState<Objective | null>(null);
  const [editingObjective, setEditingObjective] = useState<Objective | null>(null);

  useEffect(() => {
    loadObjectives();
  }, [refreshTrigger]);

  useEffect(() => {
    applyFilters();
  }, [objectives, searchTerm, typeFilter, levelFilter, departmentFilter]);

  const loadObjectives = async () => {
    try {
      setLoading(true);
      const response = await objectivesService.getObjectives();
      setObjectives(response.data || []);
      setError(null);
    } catch (err) {
      setError('Failed to load objectives');
      console.error('Error loading objectives:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = objectives;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(obj =>
        obj.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        obj.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(obj => obj.objective_type === typeFilter);
    }

    // Level filter
    if (levelFilter !== 'all') {
      filtered = filtered.filter(obj => obj.hierarchy_level === levelFilter);
    }

    // Department filter
    if (departmentFilter !== 'all') {
      filtered = filtered.filter(obj => obj.department_id?.toString() === departmentFilter);
    }

    setFilteredObjectives(filtered);
  };

  const handleRowExpand = (objectiveId: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(objectiveId)) {
      newExpanded.delete(objectiveId);
    } else {
      newExpanded.add(objectiveId);
    }
    setExpandedRows(newExpanded);
  };

  const handleEdit = (objective: Objective) => {
    setEditingObjective(objective);
    setShowForm(true);
  };

  const handleView = (objective: Objective) => {
    setSelectedObjective(objective);
    setShowDetail(true);
    if (onObjectiveSelect) {
      onObjectiveSelect(objective);
    }
  };

  const handleDelete = async (objectiveId: number) => {
    if (window.confirm('Are you sure you want to delete this objective?')) {
      try {
        await objectivesService.deleteObjective(objectiveId);
        await loadObjectives();
      } catch (err) {
        setError('Failed to delete objective');
        console.error('Error deleting objective:', err);
      }
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingObjective(null);
  };

  const handleFormSubmit = async () => {
    await loadObjectives();
    handleFormClose();
  };

  const getPerformanceColor = (color: string) => {
    switch (color) {
      case 'green': return 'success';
      case 'yellow': return 'warning';
      case 'red': return 'error';
      default: return 'default';
    }
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'improving': return <TrendingUpIcon color="success" />;
      case 'declining': return <TrendingDownIcon color="error" />;
      case 'stable': return <TrendingFlatIcon color="action" />;
      default: return null;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <Typography>Loading objectives...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Objectives Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setShowForm(true)}
        >
          Add Objective
        </Button>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Search objectives"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              size="small"
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Type</InputLabel>
              <Select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value as ObjectiveType | 'all')}
                label="Type"
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="corporate">Corporate</MenuItem>
                <MenuItem value="departmental">Departmental</MenuItem>
                <MenuItem value="operational">Operational</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Level</InputLabel>
              <Select
                value={levelFilter}
                onChange={(e) => setLevelFilter(e.target.value as HierarchyLevel | 'all')}
                label="Level"
              >
                <MenuItem value="all">All Levels</MenuItem>
                <MenuItem value="strategic">Strategic</MenuItem>
                <MenuItem value="tactical">Tactical</MenuItem>
                <MenuItem value="operational">Operational</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Department</InputLabel>
              <Select
                value={departmentFilter}
                onChange={(e) => setDepartmentFilter(e.target.value)}
                label="Department"
              >
                <MenuItem value="all">All Departments</MenuItem>
                {/* Add department options dynamically */}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box display="flex" gap={1}>
              <Typography variant="body2" color="text.secondary">
                {filteredObjectives.length} objectives
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Objectives Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Level</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Progress</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Trend</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredObjectives
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((objective) => (
                <React.Fragment key={objective.id}>
                  <TableRow hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <IconButton
                          size="small"
                          onClick={() => handleRowExpand(objective.id)}
                        >
                          {expandedRows.has(objective.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                        <Typography variant="body2" fontWeight="medium">
                          {objective.title}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={objective.objective_type}
                        size="small"
                        color={objective.objective_type === 'corporate' ? 'primary' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={objective.hierarchy_level}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      {objective.department_name || 'N/A'}
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body2">
                          {objective.current_value || 0} / {objective.target_value}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          ({Math.round(((objective.current_value || 0) / objective.target_value) * 100)}%)
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={objective.performance_color}
                        size="small"
                        color={getPerformanceColor(objective.performance_color) as any}
                      />
                    </TableCell>
                    <TableCell>
                      {getTrendIcon(objective.trend_direction)}
                    </TableCell>
                    <TableCell align="right">
                      <Box display="flex" gap={1}>
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => handleView(objective)}>
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit">
                          <IconButton size="small" onClick={() => handleEdit(objective)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton size="small" onClick={() => handleDelete(objective.id)}>
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={8}>
                      <Collapse in={expandedRows.has(objective.id)} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1 }}>
                          <Typography variant="h6" gutterBottom component="div">
                            Progress Details
                          </Typography>
                          <ProgressChart objectiveId={objective.id} />
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredObjectives.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>

      {/* Modals */}
      {showForm && (
        <ObjectiveForm
          open={showForm}
          objective={editingObjective}
          onClose={handleFormClose}
          onSubmit={handleFormSubmit}
        />
      )}

      {showDetail && selectedObjective && (
        <ObjectiveDetail
          open={showDetail}
          objective={selectedObjective}
          onClose={() => {
            setShowDetail(false);
            setSelectedObjective(null);
          }}
        />
      )}
    </Box>
  );
};

export default ObjectivesList;
