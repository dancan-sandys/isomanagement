import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Stack,
  Box,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  Close as CloseIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  Flag as TargetIcon,
  ShowChart as ShowChartIcon
} from '@mui/icons-material';
import objectivesAPI from '../../services/objectivesAPI';
import { safeFormatDate } from '../../utils/nullSafeUtils';

interface ObjectiveDetailViewProps {
  open: boolean;
  objectiveId: number | null;
  onClose: () => void;
}

interface ObjectiveDetail {
  objective: any;
  targets: any[];
  progress: any[];
  trend_analysis: any;
  child_objectives: any[];
}

const ObjectiveDetailView: React.FC<ObjectiveDetailViewProps> = ({
  open,
  objectiveId,
  onClose
}) => {
  const [detail, setDetail] = useState<ObjectiveDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (open && objectiveId) {
      loadObjectiveDetail();
    }
  }, [open, objectiveId]);

  const loadObjectiveDetail = async () => {
    if (!objectiveId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await objectivesAPI.getEnhancedObjective(objectiveId);
      setDetail(response || {
        objective: {},
        targets: [],
        progress: [],
        trend_analysis: null,
        child_objectives: []
      });
    } catch (e) {
      setError('Failed to load objective details');
      console.error('Error loading objective detail:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on_track': return 'success';
      case 'at_risk': return 'warning';
      case 'off_track': return 'error';
      default: return 'default';
    }
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'improving': return <TrendingUpIcon color="success" />;
      case 'declining': return <TrendingDownIcon color="error" />;
      case 'stable': return <TrendingFlatIcon color="action" />;
      default: return <AssessmentIcon color="action" />;
    }
  };

  const formatDate = (dateString: string) => safeFormatDate(dateString, 'N/A');

  const calculateProgress = (actual: number, target: number) => {
    if (target === 0) return 0;
    return Math.min((actual / target) * 100, 100);
  };

  if (!open) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            {detail?.objective?.title || 'Objective Details'}
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {loading && (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {detail && !loading && (
          <>
            {/* Objective Header */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={8}>
                    <Typography variant="h6" gutterBottom>
                      {detail.objective?.title || 'Untitled Objective'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {detail.objective?.description || 'No description available'}
                    </Typography>
                    
                    <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                      <Chip 
                        label={detail.objective?.objective_type || 'N/A'} 
                        color="primary" 
                        size="small" 
                      />
                      <Chip 
                        label={detail.objective?.hierarchy_level || 'N/A'} 
                        variant="outlined" 
                        size="small" 
                      />
                      <Chip 
                        label={detail.objective?.status || 'N/A'} 
                        color={getStatusColor(detail.objective?.status || '') as 'success' | 'warning' | 'error' | 'default'}
                        size="small" 
                      />
                      {detail.objective?.performance_color && (
                        <Chip 
                          label={detail.objective.performance_color} 
                          color={(detail.objective.performance_color === 'green' ? 'success' : 
                                 detail.objective.performance_color === 'yellow' ? 'warning' : 'error') as 'success' | 'warning' | 'error'}
                          size="small" 
                        />
                      )}
                    </Stack>
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2" gutterBottom>
                      Objective Code
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                      {detail.objective?.objective_code || 'N/A'}
                    </Typography>
                    
                    <Typography variant="subtitle2" gutterBottom>
                      Measurement Unit
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                      {detail.objective?.measurement_unit || 'N/A'}
                    </Typography>
                    
                    <Typography variant="subtitle2" gutterBottom>
                      Frequency
                    </Typography>
                    <Typography variant="body1">
                      {detail.objective?.frequency || 'N/A'}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Tabs */}
            <Paper sx={{ width: '100%' }}>
              <Tabs value={activeTab} onChange={handleTabChange} aria-label="objective detail tabs">
                <Tab label="Overview" />
                <Tab label="Targets" />
                <Tab label="Progress" />
                <Tab label="Trend Analysis" />
              </Tabs>

              {/* Overview Tab */}
              {activeTab === 0 && (
                <Box p={3}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            <TargetIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                            Targets Summary
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {detail.targets?.length || 0} target(s) defined
                          </Typography>
                          {detail.targets && detail.targets.length > 0 && (
                            <Box sx={{ mt: 2 }}>
                              {detail.targets.slice(0, 3).map((target, index) => (
                                <Box key={index} sx={{ mb: 1 }}>
                                  <Typography variant="body2">
                                    Target: {target.target_value} {detail.objective?.measurement_unit || ''}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {formatDate(target.period_start)} - {formatDate(target.period_end)}
                                  </Typography>
                                </Box>
                              ))}
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            <ShowChartIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                            Progress Summary
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {detail.progress?.length || 0} progress entry(ies)
                          </Typography>
                          {detail.progress && detail.progress.length > 0 && (
                            <Box sx={{ mt: 2 }}>
                              {detail.progress.slice(0, 3).map((prog, index) => (
                                <Box key={index} sx={{ mb: 1 }}>
                                  <Typography variant="body2">
                                    {prog.actual_value} {detail.objective?.measurement_unit || ''}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {formatDate(prog.period_start)} - {formatDate(prog.period_end)}
                                  </Typography>
                                </Box>
                              ))}
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>

                    <Grid item xs={12}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                            Trend Analysis
                          </Typography>
                          {detail.trend_analysis ? (
                            <Box>
                              <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                                <Typography variant="body1">
                                  Trend: {detail.trend_analysis.trend}
                                </Typography>
                                {getTrendIcon(detail.trend_analysis.direction)}
                                <Typography variant="body2" color="text.secondary">
                                  Slope: {detail.trend_analysis.slope?.toFixed(2)}
                                </Typography>
                              </Stack>
                              {detail.trend_analysis.values && detail.trend_analysis.values.length > 0 && (
                                <Typography variant="body2" color="text.secondary">
                                  Data points: {detail.trend_analysis.values.length}
                                </Typography>
                              )}
                            </Box>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              No trend data available
                            </Typography>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {/* Targets Tab */}
              {activeTab === 1 && (
                <Box p={3}>
                  {detail.targets && detail.targets.length > 0 ? (
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Period</TableCell>
                            <TableCell>Target Value</TableCell>
                            <TableCell>Lower Threshold</TableCell>
                            <TableCell>Upper Threshold</TableCell>
                            <TableCell>Weight</TableCell>
                            <TableCell>Created</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {detail.targets.map((target) => (
                            <TableRow key={target.id}>
                              <TableCell>
                                {formatDate(target.period_start)} - {formatDate(target.period_end)}
                              </TableCell>
                              <TableCell>
                                {target.target_value} {detail.objective.measurement_unit}
                              </TableCell>
                              <TableCell>
                                {target.lower_threshold || 'N/A'}
                              </TableCell>
                              <TableCell>
                                {target.upper_threshold || 'N/A'}
                              </TableCell>
                              <TableCell>
                                {target.weight}
                              </TableCell>
                              <TableCell>
                                {formatDate(target.created_at)}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ) : (
                    <Alert severity="info">
                      No targets defined for this objective.
                    </Alert>
                  )}
                </Box>
              )}

              {/* Progress Tab */}
              {activeTab === 2 && (
                <Box p={3}>
                  {detail.progress && detail.progress.length > 0 ? (
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Period</TableCell>
                            <TableCell>Actual Value</TableCell>
                            <TableCell>Attainment %</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Evidence</TableCell>
                            <TableCell>Created</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {detail.progress.map((prog) => (
                            <TableRow key={prog.id}>
                              <TableCell>
                                {formatDate(prog.period_start)} - {formatDate(prog.period_end)}
                              </TableCell>
                              <TableCell>
                                {prog.actual_value} {detail.objective.measurement_unit}
                              </TableCell>
                              <TableCell>
                                {prog.attainment_percent ? `${prog.attainment_percent.toFixed(1)}%` : 'N/A'}
                              </TableCell>
                              <TableCell>
                                <Chip 
                                  label={prog.status || 'N/A'} 
                                  color={getStatusColor(prog.status || '') as 'success' | 'warning' | 'error' | 'default'}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>
                                {prog.evidence || 'N/A'}
                              </TableCell>
                              <TableCell>
                                {formatDate(prog.created_at)}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ) : (
                    <Alert severity="info">
                      No progress entries for this objective.
                    </Alert>
                  )}
                </Box>
              )}

              {/* Trend Analysis Tab */}
              {activeTab === 3 && (
                <Box p={3}>
                  {detail.trend_analysis ? (
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Trend Analysis
                        </Typography>
                        
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <Typography variant="subtitle2" gutterBottom>
                              Trend Direction
                            </Typography>
                            <Stack direction="row" spacing={1} alignItems="center">
                              {getTrendIcon(detail.trend_analysis.direction)}
                              <Typography variant="body1">
                                {detail.trend_analysis.trend}
                              </Typography>
                            </Stack>
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <Typography variant="subtitle2" gutterBottom>
                              Trend Strength
                            </Typography>
                            <Typography variant="body1">
                              Slope: {detail.trend_analysis.slope?.toFixed(4)}
                            </Typography>
                          </Grid>
                          
                          {detail.trend_analysis.values && detail.trend_analysis.values.length > 0 && (
                            <Grid item xs={12}>
                              <Typography variant="subtitle2" gutterBottom>
                                Recent Values
                              </Typography>
                              <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                                {detail.trend_analysis.values.map((value: number, index: number) => (
                                  <Typography key={index} variant="body2">
                                    Point {index + 1}: {value}
                                  </Typography>
                                ))}
                              </Box>
                            </Grid>
                          )}
                        </Grid>
                      </CardContent>
                    </Card>
                  ) : (
                    <Alert severity="info">
                      No trend analysis data available.
                    </Alert>
                  )}
                </Box>
              )}

              {/* Child Objectives temporarily removed per request */}
            </Paper>
          </>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ObjectiveDetailView;
