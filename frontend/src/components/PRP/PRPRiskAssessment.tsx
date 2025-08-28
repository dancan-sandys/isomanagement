import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Card,
  CardContent,
  Alert,
  LinearProgress,
  Tooltip,
  Fab,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Add,
  Visibility,
  Edit,
  Delete,
  Warning,
  TrendingUp,
  Assessment,
  Security,
  CheckCircle,
  Error,
  Info,
  Refresh,
  NorthEast as Escalation,
  Assessment as RiskAssessment,
} from '@mui/icons-material';
import { prpAPI, api } from '../../services/api';

interface RiskAssessment {
  id: number;
  assessment_code: string;
  hazard_identified: string;
  hazard_description?: string;
  likelihood_level: string;
  severity_level: string;
  risk_level: string;
  risk_score: number;
  acceptability: boolean;
  existing_controls?: string;
  additional_controls_required?: string;
  control_effectiveness?: string;
  residual_risk_level?: string;
  residual_risk_score?: number;
  assessment_date: string;
  next_review_date?: string;
  escalated_to_risk_register: boolean;
  escalation_date?: string;
  escalated_by?: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

interface RiskControl {
  id: number;
  control_code: string;
  control_name: string;
  control_type: string;
  control_description: string;
  implementation_status: string;
  effectiveness_rating: number;
  responsible_person: string;
  implementation_date?: string;
  review_date?: string;
  cost_estimate?: number;
  priority: string;
}

interface RiskMatrix {
  id: number;
  matrix_name: string;
  matrix_description?: string;
  likelihood_levels: string[];
  severity_levels: string[];
  risk_levels: { [key: string]: string };
  created_by: string;
  created_at: string;
}

const PRPRiskAssessment: React.FC<{ programId?: number }> = ({ programId }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [assessments, setAssessments] = useState<RiskAssessment[]>([]);
  const [controls, setControls] = useState<RiskControl[]>([]);
  const [riskMatrices, setRiskMatrices] = useState<RiskMatrix[]>([]);
  const [programs, setPrograms] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Dialog states
  const [openAssessmentDialog, setOpenAssessmentDialog] = useState(false);
  const [openControlDialog, setOpenControlDialog] = useState(false);
  const [openMatrixDialog, setOpenMatrixDialog] = useState(false);
  const [selectedAssessment, setSelectedAssessment] = useState<RiskAssessment | null>(null);
  const [selectedControl, setSelectedControl] = useState<RiskControl | null>(null);
  const [selectedMatrix, setSelectedMatrix] = useState<RiskMatrix | null>(null);

  // Form states
  const [assessmentForm, setAssessmentForm] = useState({
    assessment_code: '',
    hazard_identified: '',
    hazard_description: '',
    likelihood_level: '',
    severity_level: '',
    existing_controls: '',
    additional_controls_required: '',
    control_effectiveness: '',
    next_review_date: '',
    selected_program_id: programId || '',
  });

  const [controlForm, setControlForm] = useState({
    control_name: '',
    control_type: '',
    control_description: '',
    implementation_status: 'pending',
    effectiveness_rating: 3,
    responsible_person: '',
    implementation_date: '',
    review_date: '',
    cost_estimate: 0,
    priority: 'medium',
  });

  const [matrixForm, setMatrixForm] = useState({
    name: '',
    description: '',
    likelihood_levels: ['Very Low', 'Low', 'Medium', 'High', 'Very High'],
    severity_levels: ['Negligible', 'Minor', 'Moderate', 'Major', 'Catastrophic'],
    risk_levels: {
      'Very Low_Negligible': 'very_low',
      'Low_Minor': 'low',
      'Medium_Moderate': 'medium',
      'High_Major': 'high',
      'Very High_Catastrophic': 'critical'
    }
  });

  useEffect(() => {
    fetchData();
  }, [programId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      console.log('Fetching data for programId:', programId);
      
      if (programId) {
        // Fetch assessments for specific program
        console.log('Fetching assessments for program:', programId);
        const assessmentsResponse = await prpAPI.getProgramRiskAssessments(programId);
        console.log('Assessments response:', assessmentsResponse);
        
        if (assessmentsResponse.success) {
          console.log('Setting assessments:', assessmentsResponse.data.items);
          setAssessments(assessmentsResponse.data.items || []);
        } else {
          console.error('Failed to fetch assessments:', assessmentsResponse);
        }
      } else {
        // Fetch all risk matrices and programs
        console.log('Fetching all risk matrices and programs');
        const matricesResponse = await prpAPI.getRiskMatrices();
        if (matricesResponse.success) {
          setRiskMatrices(matricesResponse.data.items || []);
        }
        
        // Fetch programs for selection
        const programsResponse = await prpAPI.getPrograms();
        if (programsResponse.success) {
          setPrograms(programsResponse.data.items || []);
        }
        
        // Also fetch all assessments if no specific program is selected
        console.log('Fetching all assessments since no specific program selected');
        try {
          // Use the new endpoint to fetch all risk assessments
          const allAssessmentsResponse = await api.get('/prp/risk-assessments');
          console.log('All assessments response:', allAssessmentsResponse);
          
          if (allAssessmentsResponse.data.success) {
            console.log('Setting all assessments:', allAssessmentsResponse.data.data.items);
            setAssessments(allAssessmentsResponse.data.data.items || []);
          } else {
            console.error('Failed to fetch all assessments:', allAssessmentsResponse.data);
          }
        } catch (assessmentError) {
          console.log('Could not fetch all assessments:', assessmentError);
        }
      }
    } catch (err: any) {
      console.error('Error in fetchData:', err);
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAssessment = async () => {
    const targetProgramId = programId || assessmentForm.selected_program_id;
    if (!targetProgramId) {
      setError('Please select a program for the risk assessment');
      return;
    }
    
    // Filter out fields that are not in the backend schema
    const { next_review_date, selected_program_id, ...validAssessmentData } = assessmentForm;
    
    // Validate required fields
    if (!validAssessmentData.assessment_code || validAssessmentData.assessment_code.trim() === '') {
      setError('Please enter an assessment code');
      return;
    }
    
    if (!validAssessmentData.hazard_identified || validAssessmentData.hazard_identified.trim() === '') {
      setError('Please enter the hazard identified');
      return;
    }
    
    if (!validAssessmentData.likelihood_level || validAssessmentData.likelihood_level.trim() === '') {
      setError('Please select a likelihood level');
      return;
    }
    
    if (!validAssessmentData.severity_level || validAssessmentData.severity_level.trim() === '') {
      setError('Please select a severity level');
      return;
    }
    
    try {
      console.log('Creating risk assessment for program:', targetProgramId, 'with data:', validAssessmentData);
      const response = await prpAPI.createRiskAssessment(Number(targetProgramId), validAssessmentData);
      console.log('Risk assessment creation response:', response);
      
      if (response.success) {
        setSuccess('Risk assessment created successfully');
        setOpenAssessmentDialog(false);
        resetAssessmentForm();
        
        // Force refresh the data
        console.log('Refreshing data after creation...');
        await fetchData();
        
        // Also refresh if we're in a specific program view
        if (programId) {
          console.log('Refreshing program-specific assessments...');
          const assessmentsResponse = await prpAPI.getProgramRiskAssessments(programId);
          if (assessmentsResponse.success) {
            console.log('Updated assessments:', assessmentsResponse.data.items);
            setAssessments(assessmentsResponse.data.items || []);
          }
        } else {
          // Refresh all assessments if no specific program
          console.log('Refreshing all assessments...');
          const allAssessmentsResponse = await api.get('/prp/risk-assessments');
          if (allAssessmentsResponse.data.success) {
            console.log('Updated all assessments:', allAssessmentsResponse.data.data.items);
            setAssessments(allAssessmentsResponse.data.data.items || []);
          }
        }
      }
    } catch (err: any) {
      console.error('Error creating risk assessment:', err);
      const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to create assessment';
      setError(errorMessage);
    }
  };

  const handleCreateControl = async () => {
    if (!selectedAssessment) return;
    
    try {
      const response = await prpAPI.addRiskControl(selectedAssessment.id, controlForm);
      if (response.success) {
        setSuccess('Risk control added successfully');
        setOpenControlDialog(false);
        resetControlForm();
        fetchData();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to add control');
    }
  };

  const handleCreateMatrix = async () => {
    try {
      const response = await prpAPI.createRiskMatrix(matrixForm);
      if (response.success) {
        setSuccess('Risk matrix created successfully');
        setOpenMatrixDialog(false);
        resetMatrixForm();
        fetchData();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create matrix');
    }
  };

  const handleEscalateRisk = async (assessmentId: number) => {
    try {
      const response = await prpAPI.escalateRiskAssessment(assessmentId);
      if (response.success) {
        setSuccess('Risk escalated to main risk register successfully');
        fetchData();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to escalate risk');
    }
  };

  const resetAssessmentForm = () => {
    setAssessmentForm({
      assessment_code: '',
      hazard_identified: '',
      hazard_description: '',
      likelihood_level: '',
      severity_level: '',
      existing_controls: '',
      additional_controls_required: '',
      control_effectiveness: '',
      next_review_date: '',
      selected_program_id: programId || '',
    });
  };

  const resetControlForm = () => {
    setControlForm({
      control_name: '',
      control_type: '',
      control_description: '',
      implementation_status: 'pending',
      effectiveness_rating: 3,
      responsible_person: '',
      implementation_date: '',
      review_date: '',
      cost_estimate: 0,
      priority: 'medium',
    });
  };

  const resetMatrixForm = () => {
    setMatrixForm({
      name: '',
      description: '',
      likelihood_levels: ['Very Low', 'Low', 'Medium', 'High', 'Very High'],
      severity_levels: ['Negligible', 'Minor', 'Moderate', 'Major', 'Catastrophic'],
      risk_levels: {
        'Very Low_Negligible': 'very_low',
        'Low_Minor': 'low',
        'Medium_Moderate': 'medium',
        'High_Major': 'high',
        'Very High_Catastrophic': 'critical'
      }
    });
  };

  const getRiskLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'very low': return 'success';
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'very high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getRiskLevelIcon = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'very low':
      case 'low':
        return <CheckCircle color="success" />;
      case 'medium':
        return <Info color="warning" />;
      case 'high':
      case 'very high':
        return <Warning color="error" />;
      case 'critical':
        return <Error color="error" />;
      default:
        return <Info />;
    }
  };

  const renderRiskAssessments = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Risk Assessments</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenAssessmentDialog(true)}
        >
          New Assessment
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Assessment Code</TableCell>
              <TableCell>Hazard</TableCell>
              <TableCell>Risk Level</TableCell>
              <TableCell>Risk Score</TableCell>
              <TableCell>Acceptability</TableCell>
              <TableCell>Escalated</TableCell>
              <TableCell>Assessment Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(() => {
              console.log('Rendering assessments table with', assessments.length, 'items:', assessments);
              return null;
            })()}
            {assessments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <Typography variant="body2" color="textSecondary">
                    No risk assessments found. Create your first assessment using the "New Assessment" button.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              assessments.map((assessment) => (
              <TableRow key={assessment.id}>
                <TableCell>{assessment.assessment_code}</TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold">
                    {assessment.hazard_identified}
                  </Typography>
                  {assessment.hazard_description && (
                    <Typography variant="caption" color="textSecondary">
                      {assessment.hazard_description}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    icon={getRiskLevelIcon(assessment.risk_level)}
                    label={assessment.risk_level}
                    color={getRiskLevelColor(assessment.risk_level) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{assessment.risk_score}</TableCell>
                <TableCell>
                  <Chip
                    label={assessment.acceptability ? 'Acceptable' : 'Unacceptable'}
                    color={assessment.acceptability ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {assessment.escalated_to_risk_register ? (
                    <Chip
                      icon={<TrendingUp />}
                      label="Escalated"
                      color="warning"
                      size="small"
                    />
                  ) : (
                    <Chip label="Not Escalated" size="small" />
                  )}
                </TableCell>
                <TableCell>
                  {new Date(assessment.assessment_date).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    <Tooltip title="View Details">
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Add Control">
                      <IconButton 
                        size="small"
                        onClick={() => {
                          setSelectedAssessment(assessment);
                          setOpenControlDialog(true);
                        }}
                      >
                        <Add />
                      </IconButton>
                    </Tooltip>
                    {!assessment.escalated_to_risk_register && (
                      <Tooltip title="Escalate to Risk Register">
                        <IconButton 
                          size="small"
                          onClick={() => handleEscalateRisk(assessment.id)}
                        >
                          <TrendingUp />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderRiskMatrices = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Risk Matrices</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenMatrixDialog(true)}
        >
          New Matrix
        </Button>
      </Box>

      <Grid container spacing={2}>
        {riskMatrices.map((matrix) => (
          <Grid item xs={12} md={6} lg={4} key={matrix.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {matrix.matrix_name}
                </Typography>
                {matrix.matrix_description && (
                  <Typography variant="body2" color="textSecondary" mb={2}>
                    {matrix.matrix_description}
                  </Typography>
                )}
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="caption">
                    Created by {matrix.created_by}
                  </Typography>
                  <Typography variant="caption">
                    {new Date(matrix.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderAssessmentDialog = () => (
    <Dialog open={openAssessmentDialog} onClose={() => setOpenAssessmentDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>Create Risk Assessment</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {!programId && (
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>Select Program</InputLabel>
                <Select
                  value={assessmentForm.selected_program_id}
                  onChange={(e) => setAssessmentForm({ ...assessmentForm, selected_program_id: e.target.value })}
                  label="Select Program"
                >
                  {programs.map((program) => (
                    <MenuItem key={program.id} value={program.id}>
                      {program.name} ({program.program_code})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          )}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Assessment Code (Optional)"
              value={assessmentForm.assessment_code}
              onChange={(e) => setAssessmentForm({ ...assessmentForm, assessment_code: e.target.value })}
              placeholder="Leave empty for auto-generation (e.g., RA-PROG-20250821-140649)"
              helperText="If left empty, a unique code will be automatically generated based on the program and timestamp"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Hazard Identified"
              value={assessmentForm.hazard_identified}
              onChange={(e) => setAssessmentForm({ ...assessmentForm, hazard_identified: e.target.value })}
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Hazard Description"
              value={assessmentForm.hazard_description}
              onChange={(e) => setAssessmentForm({ ...assessmentForm, hazard_description: e.target.value })}
              multiline
              rows={3}
            />
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Likelihood Level</InputLabel>
              <Select
                value={assessmentForm.likelihood_level}
                onChange={(e) => setAssessmentForm({ ...assessmentForm, likelihood_level: e.target.value })}
                required
              >
                <MenuItem value="Very Low">Very Low</MenuItem>
                <MenuItem value="Low">Low</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="High">High</MenuItem>
                <MenuItem value="Very High">Very High</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Severity Level</InputLabel>
              <Select
                value={assessmentForm.severity_level}
                onChange={(e) => setAssessmentForm({ ...assessmentForm, severity_level: e.target.value })}
                required
              >
                <MenuItem value="Very Low">Very Low</MenuItem>
                <MenuItem value="Low">Low</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="High">High</MenuItem>
                <MenuItem value="Very High">Very High</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Existing Controls"
              value={assessmentForm.existing_controls}
              onChange={(e) => setAssessmentForm({ ...assessmentForm, existing_controls: e.target.value })}
              multiline
              rows={2}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Additional Controls Required"
              value={assessmentForm.additional_controls_required}
              onChange={(e) => setAssessmentForm({ ...assessmentForm, additional_controls_required: e.target.value })}
              multiline
              rows={2}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Control Effectiveness"
              value={assessmentForm.control_effectiveness}
              onChange={(e) => setAssessmentForm({ ...assessmentForm, control_effectiveness: e.target.value })}
              multiline
              rows={2}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Next Review Date"
              type="date"
              value={assessmentForm.next_review_date}
              onChange={(e) => setAssessmentForm({ ...assessmentForm, next_review_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setOpenAssessmentDialog(false)}>Cancel</Button>
        <Button onClick={handleCreateAssessment} variant="contained">
          Create Assessment
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderControlDialog = () => (
    <Dialog open={openControlDialog} onClose={() => setOpenControlDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>Add Risk Control</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Control Name"
              value={controlForm.control_name}
              onChange={(e) => setControlForm({ ...controlForm, control_name: e.target.value })}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Control Type</InputLabel>
              <Select
                value={controlForm.control_type}
                onChange={(e) => setControlForm({ ...controlForm, control_type: e.target.value })}
                required
              >
                <MenuItem value="preventive">Preventive</MenuItem>
                <MenuItem value="detective">Detective</MenuItem>
                <MenuItem value="corrective">Corrective</MenuItem>
                <MenuItem value="administrative">Administrative</MenuItem>
                <MenuItem value="engineering">Engineering</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={controlForm.priority}
                onChange={(e) => setControlForm({ ...controlForm, priority: e.target.value })}
                required
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Control Description"
              value={controlForm.control_description}
              onChange={(e) => setControlForm({ ...controlForm, control_description: e.target.value })}
              multiline
              rows={3}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Implementation Status</InputLabel>
              <Select
                value={controlForm.implementation_status}
                onChange={(e) => setControlForm({ ...controlForm, implementation_status: e.target.value })}
                required
              >
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="implemented">Implemented</MenuItem>
                <MenuItem value="verified">Verified</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Effectiveness Rating (1-5)"
              type="number"
              value={controlForm.effectiveness_rating}
              onChange={(e) => setControlForm({ ...controlForm, effectiveness_rating: parseInt(e.target.value) })}
              inputProps={{ min: 1, max: 5 }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Responsible Person"
              value={controlForm.responsible_person}
              onChange={(e) => setControlForm({ ...controlForm, responsible_person: e.target.value })}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Implementation Date"
              type="date"
              value={controlForm.implementation_date}
              onChange={(e) => setControlForm({ ...controlForm, implementation_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Review Date"
              type="date"
              value={controlForm.review_date}
              onChange={(e) => setControlForm({ ...controlForm, review_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Cost Estimate"
              type="number"
              value={controlForm.cost_estimate}
              onChange={(e) => setControlForm({ ...controlForm, cost_estimate: parseFloat(e.target.value) || 0 })}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setOpenControlDialog(false)}>Cancel</Button>
        <Button onClick={handleCreateControl} variant="contained">
          Add Control
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderMatrixDialog = () => (
    <Dialog open={openMatrixDialog} onClose={() => setOpenMatrixDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>Create Risk Matrix</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Matrix Name"
              value={matrixForm.name}
              onChange={(e) => setMatrixForm({ ...matrixForm, name: e.target.value })}
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Matrix Description"
              value={matrixForm.description}
              onChange={(e) => setMatrixForm({ ...matrixForm, description: e.target.value })}
              multiline
              rows={3}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setOpenMatrixDialog(false)}>Cancel</Button>
        <Button onClick={handleCreateMatrix} variant="contained">
          Create Matrix
        </Button>
      </DialogActions>
    </Dialog>
  );

  if (loading) {
    return (
      <Box>
        <LinearProgress />
        <Typography>Loading risk assessment data...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Risk Assessments" icon={<Assessment />} />
          <Tab label="Risk Matrices" icon={<Security />} />
        </Tabs>
      </Box>

      {activeTab === 0 && renderRiskAssessments()}
      {activeTab === 1 && renderRiskMatrices()}

      {renderAssessmentDialog()}
      {renderControlDialog()}
      {renderMatrixDialog()}
    </Box>
  );
};

export default PRPRiskAssessment;
