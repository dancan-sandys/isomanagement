import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Close as CloseIcon,
  Edit as EditIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  CalendarToday as CalendarIcon,
  Business as BusinessIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { objectivesService } from '../../services/objectivesService';
import { Objective } from '../../types/objectives';
import ProgressChart from './ProgressChart';
import ProgressEntryForm from './ProgressEntryForm';
import RefreshIcon from '@mui/icons-material/Refresh';
import EvidenceSection from './EvidenceSection';

interface ObjectiveDetailProps {
  open: boolean;
  objective: Objective;
  onClose: () => void;
}

const ObjectiveDetail: React.FC<ObjectiveDetailProps> = ({
  open,
  objective,
  onClose
}) => {
  const [detailedObjective, setDetailedObjective] = useState<Objective | null>(null);
  const [progressHistory, setProgressHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showProgressForm, setShowProgressForm] = useState(false);
  const [links, setLinks] = useState<{ linked_risk_ids: number[]; linked_control_ids: number[]; linked_document_ids: number[]; management_review_refs: number[] } | null>(null);

  useEffect(() => {
    if (open && objective) {
      loadDetailedData();
    }
  }, [open, objective]);

  const loadDetailedData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load detailed objective data
      const objectiveResponse = await objectivesService.getObjective(objective.id);
      setDetailedObjective(objectiveResponse.data);

      // Load progress history
      const progressResponse = await objectivesService.getObjectiveProgress(objective.id);
      setProgressHistory(progressResponse.data || []);

      // Load linkages
      try {
        const linkRes = await objectivesService.getObjectiveLinks(objective.id);
        setLinks(linkRes);
      } catch (e) {
        // non-blocking
        setLinks({ linked_risk_ids: [], linked_control_ids: [], linked_document_ids: [], management_review_refs: [] });
      }
    } catch (err) {
      setError('Failed to load objective details');
      console.error('Error loading objective details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleProgressSubmit = async () => {
    await loadDetailedData();
    setShowProgressForm(false);
  };

  const getObjectiveTypeColor = (type: string) => {
    switch (type) {
      case 'corporate': return 'primary';
      case 'departmental': return 'secondary';
      case 'operational': return 'default';
      default: return 'default';
    }
  };

  const getHierarchyLevelColor = (level: string) => {
    switch (level) {
      case 'strategic': return 'error';
      case 'tactical': return 'warning';
      case 'operational': return 'info';
      default: return 'default';
    }
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

  const getStatusIcon = (color: string) => {
    switch (color) {
      case 'green': return <CheckCircleIcon color="success" />;
      case 'yellow': return <WarningIcon color="warning" />;
      case 'red': return <ErrorIcon color="error" />;
      default: return <AssessmentIcon color="action" />;
    }
  };

  const calculateProgress = () => {
    if (!detailedObjective) return 0;
    const currentValue = detailedObjective.current_value || detailedObjective.baseline_value || 0;
    return Math.min((currentValue / detailedObjective.target_value) * 100, 100);
  };

  const getDaysRemaining = () => {
    if (!detailedObjective?.target_date) return null;
    const targetDate = new Date(detailedObjective.target_date);
    const today = new Date();
    const diffTime = targetDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <DialogContent>
          <Box display="flex" justifyContent="center" alignItems="center" height={400}>
            <CircularProgress />
          </Box>
        </DialogContent>
      </Dialog>
    );
  }

  if (error || !detailedObjective) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <DialogContent>
          <Alert severity="error">
            {error || 'Failed to load objective details'}
          </Alert>
        </DialogContent>
      </Dialog>
    );
  }

  const progressPercentage = calculateProgress();
  const daysRemaining = getDaysRemaining();

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h5" component="div">
            {detailedObjective.title}
          </Typography>
          <Box>
            <Tooltip title="Add Progress">
              <IconButton onClick={() => setShowProgressForm(true)} color="primary">
                <AssessmentIcon />
              </IconButton>
            </Tooltip>
            <IconButton onClick={onClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Grid container spacing={3}>
          {/* Basic Information */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Description
                </Typography>
                <Typography variant="body1" paragraph>
                  {detailedObjective.description}
                </Typography>
                
                <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
                  <Chip
                    label={detailedObjective.objective_type}
                    color={getObjectiveTypeColor(detailedObjective.objective_type) as any}
                    size="small"
                  />
                  <Chip
                    label={detailedObjective.hierarchy_level}
                    color={getHierarchyLevelColor(detailedObjective.hierarchy_level) as any}
                    variant="outlined"
                    size="small"
                  />
                  {detailedObjective.department_name && (
                    <Chip
                      label={detailedObjective.department_name}
                      color="info"
                      variant="outlined"
                      size="small"
                    />
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Status Summary */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Status Summary
                </Typography>
                
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  {getStatusIcon(detailedObjective.performance_color)}
                  <Typography variant="body1" fontWeight="bold">
                    {detailedObjective.performance_color.toUpperCase()}
                  </Typography>
                </Box>

                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  {getTrendIcon(detailedObjective.trend_direction)}
                  <Typography variant="body2">
                    {detailedObjective.trend_direction}
                  </Typography>
                </Box>

                <Typography variant="h4" color="primary" gutterBottom>
                  {Math.round(progressPercentage)}%
                </Typography>
                
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Progress
                </Typography>

                {daysRemaining !== null && (
                  <Box mt={2}>
                    <Typography variant="body2" color={daysRemaining < 0 ? 'error' : 'textSecondary'}>
                      {daysRemaining < 0 ? `${Math.abs(daysRemaining)} days overdue` : `${daysRemaining} days remaining`}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Targets and Measurements */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Targets & Measurements
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Baseline Value
                    </Typography>
                    <Typography variant="h6">
                      {detailedObjective.baseline_value || 0} {detailedObjective.unit_of_measure}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Target Value
                    </Typography>
                    <Typography variant="h6">
                      {detailedObjective.target_value} {detailedObjective.unit_of_measure}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Current Value
                    </Typography>
                    <Typography variant="h6">
                      {detailedObjective.current_value || detailedObjective.baseline_value || 0} {detailedObjective.unit_of_measure}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Weight
                    </Typography>
                    <Typography variant="h6">
                      {detailedObjective.weight}%
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">
                      Measurement Frequency
                    </Typography>
                    <Typography variant="body1">
                      {detailedObjective.measurement_frequency}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Timeline */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Timeline
                </Typography>
                
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <CalendarIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Start Date"
                      secondary={new Date(detailedObjective.start_date).toLocaleDateString()}
                    />
                  </ListItem>
                  
                  <ListItem>
                    <ListItemIcon>
                      <TimelineIcon color="secondary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Target Date"
                      secondary={new Date(detailedObjective.target_date).toLocaleDateString()}
                    />
                  </ListItem>
                  
                  {detailedObjective.last_updated_at && (
                    <ListItem>
                      <ListItemIcon>
                        <AssessmentIcon color="action" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Last Updated"
                        secondary={new Date(detailedObjective.last_updated_at).toLocaleDateString()}
                      />
                    </ListItem>
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Linkages */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="h6">Linked Risks / Controls / Documents / MR</Typography>
                  <Tooltip title="Refresh Links">
                    <IconButton size="small" onClick={loadDetailedData}>
                      <RefreshIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={3}>
                    <Typography variant="caption" color="textSecondary">Risks</Typography>
                    <Box mt={1} display="flex" gap={1} flexWrap="wrap">
                      {(links?.linked_risk_ids || []).length === 0 ? (
                        <Typography variant="body2">None</Typography>
                      ) : (
                        links!.linked_risk_ids.map((id) => <Chip key={`risk-${id}`} label={`Risk #${id}`} size="small" />)
                      )}
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Typography variant="caption" color="textSecondary">Controls</Typography>
                    <Box mt={1} display="flex" gap={1} flexWrap="wrap">
                      {(links?.linked_control_ids || []).length === 0 ? (
                        <Typography variant="body2">None</Typography>
                      ) : (
                        links!.linked_control_ids.map((id) => <Chip key={`ctrl-${id}`} label={`Control #${id}`} size="small" />)
                      )}
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Typography variant="caption" color="textSecondary">Documents</Typography>
                    <Box mt={1} display="flex" gap={1} flexWrap="wrap">
                      {(links?.linked_document_ids || []).length === 0 ? (
                        <Typography variant="body2">None</Typography>
                      ) : (
                        links!.linked_document_ids.map((id) => <Chip key={`doc-${id}`} label={`Doc #${id}`} size="small" />)
                      )}
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Typography variant="caption" color="textSecondary">Management Reviews</Typography>
                    <Box mt={1} display="flex" gap={1} flexWrap="wrap">
                      {(links?.management_review_refs || []).length === 0 ? (
                        <Typography variant="body2">None</Typography>
                      ) : (
                        links!.management_review_refs.map((id) => <Chip key={`mr-${id}`} label={`MR #${id}`} size="small" />)
                      )}
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Evidence */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <EvidenceSection objectiveId={detailedObjective.id} />
              </CardContent>
            </Card>
          </Grid>

          {/* Progress Chart */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Progress Visualization
                </Typography>
                <ProgressChart objectiveId={detailedObjective.id} height={400} />
              </CardContent>
            </Card>
          </Grid>

          {/* Progress History */}
          {progressHistory.length > 0 && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Progress History
                  </Typography>
                  
                  <Box maxHeight={300} overflow="auto">
                    <List dense>
                      {progressHistory.slice(-10).reverse().map((entry) => (
                        <ListItem key={entry.id} divider>
                          <ListItemText
                            primary={`${entry.recorded_value} ${detailedObjective.unit_of_measure}`}
                            secondary={
                              <Box>
                                <Typography variant="caption" display="block">
                                  {new Date(entry.recorded_date).toLocaleDateString()} - {entry.recorded_by}
                                </Typography>
                                {entry.notes && (
                                  <Typography variant="caption" color="textSecondary">
                                    {entry.notes}
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>
          Close
        </Button>
        <Button
          variant="contained"
          onClick={() => setShowProgressForm(true)}
          startIcon={<AssessmentIcon />}
        >
          Add Progress
        </Button>
      </DialogActions>

      {/* Progress Entry Form Modal */}
      {showProgressForm && (
        <ProgressEntryForm
          open={showProgressForm}
          objectiveId={detailedObjective.id}
          onClose={() => setShowProgressForm(false)}
          onSubmit={handleProgressSubmit}
        />
      )}
    </Dialog>
  );
};

export default ObjectiveDetail;
