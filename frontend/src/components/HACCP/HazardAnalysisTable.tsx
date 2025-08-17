import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Paper,
  Chip,
  IconButton,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Grid,
  Tooltip,
  Alert,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Badge,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Warning,
  CheckCircle,
  Error,
  Science,
  Security,
  FilterList,
  Sort,
  Assessment,
  VerifiedUser,
  Person,
  Schedule,
  TrendingUp,
  TrendingDown,
  FilterAlt,
  Clear,
  Save,
  Send,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

interface Hazard {
  id: string;
  name: string;
  type: 'biological' | 'chemical' | 'physical';
  description: string;
  likelihood: number;
  severity: number;
  riskScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  controlMeasures: string[];
  isCCP: boolean;
  reviewedBy?: string;
  reviewDate?: string;
  reviewStatus: 'pending' | 'approved' | 'rejected';
  rationale: string;
  prpReferences: string[];
  references: string[];
}

interface HazardAnalysisTableProps {
  productId: number;
  hazards: Hazard[];
  onHazardClick: (hazardId: string) => void;
  onEditHazard: (hazard: Hazard) => void;
  onDeleteHazard: (hazardId: string) => void;
  onReviewHazard: (hazardId: string, reviewData: any) => void;
  onRiskCalculation: (hazardId: string, likelihood: number, severity: number) => void;
}

type Order = 'asc' | 'desc';

interface HeadCell {
  id: keyof Hazard;
  label: string;
  numeric: boolean;
  sortable: boolean;
}

const headCells: HeadCell[] = [
  { id: 'name', label: 'Hazard Name', numeric: false, sortable: true },
  { id: 'type', label: 'Type', numeric: false, sortable: true },
  { id: 'likelihood', label: 'Likelihood', numeric: true, sortable: true },
  { id: 'severity', label: 'Severity', numeric: true, sortable: true },
  { id: 'riskScore', label: 'Risk Score', numeric: true, sortable: true },
  { id: 'riskLevel', label: 'Risk Level', numeric: false, sortable: true },
  { id: 'isCCP', label: 'CCP', numeric: false, sortable: true },
  { id: 'reviewStatus', label: 'Review Status', numeric: false, sortable: true },
  { id: 'reviewedBy', label: 'Reviewed By', numeric: false, sortable: true },
  { id: 'reviewDate', label: 'Review Date', numeric: false, sortable: true },
];

const HazardAnalysisTable: React.FC<HazardAnalysisTableProps> = ({
  productId,
  hazards,
  onHazardClick,
  onEditHazard,
  onDeleteHazard,
  onReviewHazard,
  onRiskCalculation,
}) => {
  const theme = useTheme();
  const [order, setOrder] = useState<Order>('desc');
  const [orderBy, setOrderBy] = useState<keyof Hazard>('riskScore');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [filters, setFilters] = useState({
    type: '',
    riskLevel: '',
    reviewStatus: '',
    isCCP: '',
    search: '',
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedHazard, setSelectedHazard] = useState<Hazard | null>(null);
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false);
  const [reviewData, setReviewData] = useState({
    status: 'approved',
    comments: '',
    reviewer: '',
  });

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical':
        return theme.palette.error.main;
      case 'high':
        return theme.palette.warning.main;
      case 'medium':
        return theme.palette.info.main;
      case 'low':
        return theme.palette.success.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const getHazardIcon = (type: string) => {
    switch (type) {
      case 'biological':
        return <Science color="error" />;
      case 'chemical':
        return <Warning color="warning" />;
      case 'physical':
        return <Error color="info" />;
      default:
        return <Warning />;
    }
  };

  const getReviewStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'rejected':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const filteredHazards = useMemo(() => {
    return hazards.filter((hazard) => {
      const matchesType = !filters.type || hazard.type === filters.type;
      const matchesRiskLevel = !filters.riskLevel || hazard.riskLevel === filters.riskLevel;
      const matchesReviewStatus = !filters.reviewStatus || hazard.reviewStatus === filters.reviewStatus;
      const matchesCCP = filters.isCCP === '' || 
        (filters.isCCP === 'true' && hazard.isCCP) || 
        (filters.isCCP === 'false' && !hazard.isCCP);
      const matchesSearch = !filters.search || 
        hazard.name.toLowerCase().includes(filters.search.toLowerCase()) ||
        hazard.description.toLowerCase().includes(filters.search.toLowerCase());

      return matchesType && matchesRiskLevel && matchesReviewStatus && matchesCCP && matchesSearch;
    });
  }, [hazards, filters]);

  const sortedHazards = useMemo(() => {
    const sorted = [...filteredHazards].sort((a, b) => {
      const aValue = a[orderBy];
      const bValue = b[orderBy];

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return order === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return order === 'asc' ? aValue - bValue : bValue - aValue;
      }

      if (typeof aValue === 'boolean' && typeof bValue === 'boolean') {
        return order === 'asc' ? (aValue === bValue ? 0 : aValue ? 1 : -1) : (aValue === bValue ? 0 : aValue ? -1 : 1);
      }

      return 0;
    });

    return sorted;
  }, [filteredHazards, order, orderBy]);

  const handleRequestSort = (property: keyof Hazard) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleFilterChange = (field: string, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPage(0);
  };

  const handleClearFilters = () => {
    setFilters({
      type: '',
      riskLevel: '',
      reviewStatus: '',
      isCCP: '',
      search: '',
    });
    setPage(0);
  };

  const handleReviewHazard = (hazard: Hazard) => {
    setSelectedHazard(hazard);
    setReviewData({
      status: hazard.reviewStatus === 'pending' ? 'approved' : hazard.reviewStatus,
      comments: '',
      reviewer: '',
    });
    setReviewDialogOpen(true);
  };

  const handleSubmitReview = () => {
    if (selectedHazard) {
      onReviewHazard(selectedHazard.id, {
        ...reviewData,
        reviewDate: new Date().toISOString(),
      });
      setReviewDialogOpen(false);
      setSelectedHazard(null);
    }
  };

  const handleRiskCalculation = (hazard: Hazard, likelihood: number, severity: number) => {
    onRiskCalculation(hazard.id, likelihood, severity);
  };

  const paginatedHazards = sortedHazards.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const riskDistribution = useMemo(() => {
    const distribution = { low: 0, medium: 0, high: 0, critical: 0 };
    filteredHazards.forEach(hazard => {
      distribution[hazard.riskLevel]++;
    });
    return distribution;
  }, [filteredHazards]);

  return (
    <Card>
      <CardHeader
        title="Hazard Analysis"
        subheader={`${filteredHazards.length} hazards found • ${hazards.filter(h => h.isCCP).length} CCPs identified`}
        action={
          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              startIcon={<FilterAlt />}
              onClick={() => setShowFilters(!showFilters)}
              color={showFilters ? 'primary' : 'default'}
            >
              Filters
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => onEditHazard({} as Hazard)}
            >
              Add Hazard
            </Button>
          </Stack>
        }
      />
      <CardContent>
        {/* Risk Distribution Summary */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Risk Distribution
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(riskDistribution).map(([level, count]) => (
              <Grid item xs={3} key={level}>
                <Box
                  sx={{
                    p: 2,
                    textAlign: 'center',
                    backgroundColor: getRiskColor(level) + '20',
                    borderRadius: 1,
                    border: `1px solid ${getRiskColor(level)}`,
                  }}
                >
                  <Typography variant="h6" color={getRiskColor(level)}>
                    {count}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {level.toUpperCase()}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Filters */}
        {showFilters && (
          <Paper sx={{ p: 2, mb: 3 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Search"
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  placeholder="Search hazards..."
                />
              </Grid>
              <Grid item xs={12} sm={6} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={filters.type}
                    label="Type"
                    onChange={(e) => handleFilterChange('type', e.target.value)}
                  >
                    <MenuItem value="">All Types</MenuItem>
                    <MenuItem value="biological">Biological</MenuItem>
                    <MenuItem value="chemical">Chemical</MenuItem>
                    <MenuItem value="physical">Physical</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Risk Level</InputLabel>
                  <Select
                    value={filters.riskLevel}
                    label="Risk Level"
                    onChange={(e) => handleFilterChange('riskLevel', e.target.value)}
                  >
                    <MenuItem value="">All Levels</MenuItem>
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="critical">Critical</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Review Status</InputLabel>
                  <Select
                    value={filters.reviewStatus}
                    label="Review Status"
                    onChange={(e) => handleFilterChange('reviewStatus', e.target.value)}
                  >
                    <MenuItem value="">All Status</MenuItem>
                    <MenuItem value="pending">Pending</MenuItem>
                    <MenuItem value="approved">Approved</MenuItem>
                    <MenuItem value="rejected">Rejected</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={2}>
                <FormControl fullWidth>
                  <InputLabel>CCP</InputLabel>
                  <Select
                    value={filters.isCCP}
                    label="CCP"
                    onChange={(e) => handleFilterChange('isCCP', e.target.value)}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="true">CCP Only</MenuItem>
                    <MenuItem value="false">Non-CCP Only</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={1}>
                <Button
                  variant="outlined"
                  startIcon={<Clear />}
                  onClick={handleClearFilters}
                  fullWidth
                >
                  Clear
                </Button>
              </Grid>
            </Grid>
          </Paper>
        )}

        {/* Table */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                {headCells.map((headCell) => (
                  <TableCell
                    key={headCell.id}
                    align={headCell.numeric ? 'right' : 'left'}
                    sortDirection={orderBy === headCell.id ? order : false}
                  >
                    {headCell.sortable ? (
                      <TableSortLabel
                        active={orderBy === headCell.id}
                        direction={orderBy === headCell.id ? order : 'asc'}
                        onClick={() => handleRequestSort(headCell.id)}
                      >
                        {headCell.label}
                      </TableSortLabel>
                    ) : (
                      headCell.label
                    )}
                  </TableCell>
                ))}
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedHazards.map((hazard) => (
                <TableRow
                  key={hazard.id}
                  hover
                  sx={{ cursor: 'pointer' }}
                  onClick={() => onHazardClick(hazard.id)}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getHazardIcon(hazard.type)}
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {hazard.name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {hazard.description.substring(0, 50)}...
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={hazard.type}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2">{hazard.likelihood}</Typography>
                      <Tooltip title="Edit likelihood">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            // Open likelihood editor
                          }}
                        >
                          <Edit fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2">{hazard.severity}</Typography>
                      <Tooltip title="Edit severity">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            // Open severity editor
                          }}
                        >
                          <Edit fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={hazard.riskScore}
                      size="small"
                      sx={{
                        backgroundColor: getRiskColor(hazard.riskLevel),
                        color: 'white',
                        fontWeight: 'bold',
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={hazard.riskLevel.toUpperCase()}
                      size="small"
                      sx={{
                        backgroundColor: getRiskColor(hazard.riskLevel),
                        color: 'white',
                        fontWeight: 'bold',
                      }}
                    />
                  </TableCell>
                  <TableCell align="center">
                    {hazard.isCCP ? (
                      <Chip
                        icon={<Security />}
                        label="CCP"
                        color="error"
                        size="small"
                        variant="outlined"
                      />
                    ) : (
                      <Typography variant="body2" color="textSecondary">
                        -
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={hazard.reviewStatus}
                      size="small"
                      color={getReviewStatusColor(hazard.reviewStatus) as any}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    {hazard.reviewedBy ? (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Avatar sx={{ width: 24, height: 24 }}>
                          <Person fontSize="small" />
                        </Avatar>
                        <Typography variant="body2">{hazard.reviewedBy}</Typography>
                      </Box>
                    ) : (
                      <Typography variant="body2" color="textSecondary">
                        -
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {hazard.reviewDate ? (
                      <Typography variant="body2">
                        {new Date(hazard.reviewDate).toLocaleDateString()}
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="textSecondary">
                        -
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={1}>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            onHazardClick(hazard.id);
                          }}
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Hazard">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            onEditHazard(hazard);
                          }}
                        >
                          <Edit />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Review Hazard">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleReviewHazard(hazard);
                          }}
                        >
                          <VerifiedUser />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Hazard">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteHazard(hazard.id);
                          }}
                        >
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredHazards.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </CardContent>

      {/* Review Dialog */}
      <Dialog open={reviewDialogOpen} onClose={() => setReviewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Review Hazard</DialogTitle>
        <DialogContent>
          {selectedHazard && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  {selectedHazard.name}
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {selectedHazard.description}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Review Status</InputLabel>
                  <Select
                    value={reviewData.status}
                    label="Review Status"
                    onChange={(e) => setReviewData({ ...reviewData, status: e.target.value })}
                  >
                    <MenuItem value="approved">Approved</MenuItem>
                    <MenuItem value="rejected">Rejected</MenuItem>
                    <MenuItem value="pending">Pending</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Reviewer Name"
                  value={reviewData.reviewer}
                  onChange={(e) => setReviewData({ ...reviewData, reviewer: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Review Comments"
                  value={reviewData.comments}
                  onChange={(e) => setReviewData({ ...reviewData, comments: e.target.value })}
                  placeholder="Provide detailed review comments..."
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReviewDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmitReview} variant="contained">
            Submit Review
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default HazardAnalysisTable;
