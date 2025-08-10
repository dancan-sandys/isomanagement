import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  Box,
  Slider,
  FormHelperText,
  Tabs,
  Tab
} from '@mui/material';
import {
  Warning as WarningIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  Warning as RiskIcon,
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { RecallSimulation, SimulationResults, RiskAssessment, Recommendation } from '../../types/traceability';
import { traceabilityAPI } from '../../services/traceabilityAPI';

interface RecallSimulationFormProps {
  open: boolean;
  onClose: () => void;
  onSimulationComplete?: (simulation: RecallSimulation) => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simulation-tabpanel-${index}`}
      aria-labelledby={`simulation-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const RecallSimulationForm: React.FC<RecallSimulationFormProps> = ({
  open,
  onClose,
  onSimulationComplete
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [simulation, setSimulation] = useState<RecallSimulation | null>(null);

  // Form state
  const [simulationForm, setSimulationForm] = useState({
    batch_id: '',
    recall_type: '',
    reason: '',
    risk_level: 'medium'
  });

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!simulationForm.batch_id) {
      errors.batch_id = 'Batch ID is required';
    }

    if (!simulationForm.recall_type) {
      errors.recall_type = 'Recall type is required';
    }

    if (!simulationForm.reason.trim()) {
      errors.reason = 'Reason is required';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSimulate = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const simulationData = {
        batch_id: parseInt(simulationForm.batch_id),
        recall_type: simulationForm.recall_type,
        reason: simulationForm.reason,
        risk_level: simulationForm.risk_level
      };

      const result = await traceabilityAPI.simulateRecall(simulationData);
      setSimulation(result);
      setActiveTab(1); // Switch to results tab
      onSimulationComplete?.(result);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to run simulation');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSimulationForm({
      batch_id: '',
      recall_type: '',
      reason: '',
      risk_level: 'medium'
    });
    setSimulation(null);
    setError(null);
    setValidationErrors({});
    setActiveTab(0);
    onClose();
  };

  const handleInputChange = (field: string, value: string) => {
    setSimulationForm(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear validation error when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getRecallTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'class_i': return 'error';
      case 'class_ii': return 'warning';
      case 'class_iii': return 'info';
      default: return 'default';
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <WarningIcon color="error" />
          <Typography variant="h6">
            Recall Simulation
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Simulation Setup" icon={<AssessmentIcon />} />
            <Tab label="Simulation Results" icon={<TimelineIcon />} disabled={!simulation} />
          </Tabs>
        </Box>

        {/* Simulation Setup Tab */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Batch ID *"
                type="number"
                value={simulationForm.batch_id}
                onChange={(e) => handleInputChange('batch_id', e.target.value)}
                error={!!validationErrors.batch_id}
                helperText={validationErrors.batch_id}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={!!validationErrors.recall_type}>
                <InputLabel>Recall Type *</InputLabel>
                <Select
                  value={simulationForm.recall_type}
                  onChange={(e) => handleInputChange('recall_type', e.target.value)}
                  label="Recall Type *"
                >
                  <MenuItem value="class_i">Class I - Life-threatening</MenuItem>
                  <MenuItem value="class_ii">Class II - Temporary health effects</MenuItem>
                  <MenuItem value="class_iii">Class III - No health effects</MenuItem>
                </Select>
                {validationErrors.recall_type && (
                  <FormHelperText>{validationErrors.recall_type}</FormHelperText>
                )}
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Reason for Recall *"
                multiline
                rows={3}
                value={simulationForm.reason}
                onChange={(e) => handleInputChange('reason', e.target.value)}
                error={!!validationErrors.reason}
                helperText={validationErrors.reason}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography gutterBottom>
                Risk Level Assessment
              </Typography>
              <Slider
                value={['low', 'medium', 'high', 'critical'].indexOf(simulationForm.risk_level)}
                onChange={(e, value) => {
                  const levels = ['low', 'medium', 'high', 'critical'];
                  handleInputChange('risk_level', levels[value as number]);
                }}
                min={0}
                max={3}
                step={1}
                marks={[
                  { value: 0, label: 'Low' },
                  { value: 1, label: 'Medium' },
                  { value: 2, label: 'High' },
                  { value: 3, label: 'Critical' }
                ]}
                valueLabelDisplay="auto"
              />
              <Box display="flex" justifyContent="center" mt={1}>
                <Chip 
                  label={simulationForm.risk_level.toUpperCase()} 
                  color={getRiskLevelColor(simulationForm.risk_level)}
                  icon={<RiskIcon />}
                />
              </Box>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Simulation Results Tab */}
        <TabPanel value={activeTab} index={1}>
          {simulation && (
            <Grid container spacing={3}>
              {/* Simulation Summary */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Simulation Summary
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={3}>
                        <Typography variant="body2" color="text.secondary">
                          Simulation Number
                        </Typography>
                        <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                          {simulation.simulation_number}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Typography variant="body2" color="text.secondary">
                          Affected Batches
                        </Typography>
                        <Typography variant="body1">
                          {simulation.affected_batches}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Typography variant="body2" color="text.secondary">
                          Affected Quantity
                        </Typography>
                        <Typography variant="body1">
                          {simulation.affected_quantity}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Typography variant="body2" color="text.secondary">
                          Estimated Cost
                        </Typography>
                        <Typography variant="body1">
                          ${simulation.estimated_cost.toLocaleString()}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Risk Assessment */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Risk Assessment
                    </Typography>
                    <Box mb={2}>
                      <Chip 
                        label={simulation.results.risk_assessment.risk_level.toUpperCase()} 
                        color={getRiskLevelColor(simulation.results.risk_assessment.risk_level)}
                        size="medium"
                      />
                    </Box>
                    <Typography variant="body2" gutterBottom>
                      Risk Score: {simulation.results.risk_assessment.risk_score}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Risk Factors:
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                      {simulation.results.risk_assessment.risk_factors.map((factor, index) => (
                        <Chip key={index} label={factor} size="small" />
                      ))}
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Mitigation Measures:
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1}>
                      {simulation.results.risk_assessment.mitigation_measures.map((measure, index) => (
                        <Chip key={index} label={measure} size="small" color="success" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Recommendations */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Recommendations
                    </Typography>
                    {simulation.results.recommendations.map((rec, index) => (
                      <Box key={index} mb={2}>
                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                          <Chip 
                            label={rec.type.replace('_', ' ').toUpperCase()} 
                            color={rec.priority === 'high' ? 'error' : rec.priority === 'medium' ? 'warning' : 'success'}
                            size="small"
                          />
                          <Chip 
                            label={rec.priority.toUpperCase()} 
                            color={rec.priority === 'high' ? 'error' : rec.priority === 'medium' ? 'warning' : 'success'}
                            size="small"
                          />
                        </Box>
                        <Typography variant="body2" gutterBottom>
                          {rec.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Action: {rec.action_required}
                        </Typography>
                        {rec.estimated_cost && (
                          <Typography variant="caption" color="text.secondary" display="block">
                            Estimated Cost: ${rec.estimated_cost.toLocaleString()}
                          </Typography>
                        )}
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>

              {/* Affected Batches */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Affected Batches
                    </Typography>
                    <Grid container spacing={2}>
                      {simulation.results.affected_batches.map((batch) => (
                        <Grid item xs={12} md={4} key={batch.id}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography variant="subtitle2" sx={{ fontFamily: 'monospace' }}>
                                {batch.batch_number}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {batch.product_name}
                              </Typography>
                              <Chip 
                                label={batch.batch_type.replace('_', ' ').toUpperCase()} 
                                color="primary"
                                size="small"
                                sx={{ mt: 1 }}
                              />
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </TabPanel>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>
          Cancel
        </Button>
        {activeTab === 0 && (
          <Button
            onClick={handleSimulate}
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <AssessmentIcon />}
            disabled={loading}
          >
            {loading ? 'Running Simulation...' : 'Run Simulation'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default RecallSimulationForm; 