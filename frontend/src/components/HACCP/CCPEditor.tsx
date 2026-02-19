import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Grid,
  Tooltip,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Autocomplete,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Save,
  Cancel,
  Science,
  Security,
  Warning,
  CheckCircle,
  Error,
  Link,
  AttachFile,
  Schedule,
  TrendingUp,
  TrendingDown,
  ExpandMore,
  Visibility,
  Settings,
  Build,
  Assessment,
  VerifiedUser,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

interface CriticalLimitParameter {
  id: string;
  name: string;
  parameterType: 'numeric' | 'qualitative' | 'time' | 'temperature' | 'ph' | 'pressure' | 'flow_rate';
  unit: string;
  minValue?: number;
  maxValue?: number;
  targetValue?: number;
  tolerance?: number;
  description: string;
  validationEvidence: ValidationEvidence[];
}

interface ValidationEvidence {
  id: string;
  type: 'sop' | 'study' | 'certificate' | 'test_result' | 'expert_opinion';
  title: string;
  description: string;
  documentId?: string;
  externalReference?: string;
  date: string;
  approved: boolean;
}

interface CCP {
  id: string;
  ccpNumber: number;
  name: string;
  description: string;
  processStep: string;
  hazard: string;
  criticalLimits: CriticalLimitParameter[];
  monitoringMethod: string;
  monitoringFrequency: string;
  monitoringResponsibility: string;
  correctiveActions: string[];
  verificationMethod: string;
  verificationFrequency: string;
  verificationResponsibility: string;
  sopReferences: string[];
  equipment: string[];
  trainingRequirements: string[];
  isActive: boolean;
  lastReviewDate?: string;
  nextReviewDate?: string;
}

interface CCPEditorProps {
  ccp?: CCP;
  productId: number;
  onSave: (ccp: CCP) => void;
  onCancel: () => void;
  onDelete?: (ccpId: string) => void;
}

const CCPEditor: React.FC<CCPEditorProps> = ({
  ccp,
  productId,
  onSave,
  onCancel,
  onDelete,
}) => {
  const theme = useTheme();
  const [formData, setFormData] = useState<CCP>({
    id: ccp?.id || '',
    ccpNumber: ccp?.ccpNumber || 0,
    name: ccp?.name || '',
    description: ccp?.description || '',
    processStep: ccp?.processStep || '',
    hazard: ccp?.hazard || '',
    criticalLimits: ccp?.criticalLimits || [],
    monitoringMethod: ccp?.monitoringMethod || '',
    monitoringFrequency: ccp?.monitoringFrequency || '',
    monitoringResponsibility: ccp?.monitoringResponsibility || '',
    correctiveActions: ccp?.correctiveActions || [],
    verificationMethod: ccp?.verificationMethod || '',
    verificationFrequency: ccp?.verificationFrequency || '',
    verificationResponsibility: ccp?.verificationResponsibility || '',
    sopReferences: ccp?.sopReferences || [],
    equipment: ccp?.equipment || [],
    trainingRequirements: ccp?.trainingRequirements || [],
    isActive: ccp?.isActive ?? true,
    lastReviewDate: ccp?.lastReviewDate,
    nextReviewDate: ccp?.nextReviewDate,
  });

  const [limitDialogOpen, setLimitDialogOpen] = useState(false);
  const [editingLimit, setEditingLimit] = useState<CriticalLimitParameter | null>(null);
  const [evidenceDialogOpen, setEvidenceDialogOpen] = useState(false);
  const [editingEvidence, setEditingEvidence] = useState<ValidationEvidence | null>(null);
  const [selectedLimit, setSelectedLimit] = useState<CriticalLimitParameter | null>(null);

  const parameterTypes = [
    { value: 'numeric', label: 'Numeric Value' },
    { value: 'qualitative', label: 'Qualitative Assessment' },
    { value: 'time', label: 'Time' },
    { value: 'temperature', label: 'Temperature' },
    { value: 'ph', label: 'pH' },
    { value: 'pressure', label: 'Pressure' },
    { value: 'flow_rate', label: 'Flow Rate' },
  ];

  const units = {
    numeric: ['units', 'count', 'percentage'],
    time: ['seconds', 'minutes', 'hours', 'days'],
    temperature: ['°C', '°F', 'K'],
    ph: ['pH'],
    pressure: ['Pa', 'kPa', 'MPa', 'bar', 'psi'],
    flow_rate: ['L/min', 'L/h', 'm³/h', 'gal/min'],
  };

  const evidenceTypes = [
    { value: 'sop', label: 'Standard Operating Procedure' },
    { value: 'study', label: 'Scientific Study' },
    { value: 'certificate', label: 'Certificate' },
    { value: 'test_result', label: 'Test Result' },
    { value: 'expert_opinion', label: 'Expert Opinion' },
  ];

  const handleInputChange = (field: keyof CCP, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleLimitChange = (field: keyof CriticalLimitParameter, value: any) => {
    if (editingLimit) {
      setEditingLimit(prev => ({ ...prev!, [field]: value }));
    }
  };

  const handleEvidenceChange = (field: keyof ValidationEvidence, value: any) => {
    if (editingEvidence) {
      setEditingEvidence(prev => ({ ...prev!, [field]: value }));
    }
  };

  const handleAddLimit = () => {
    setEditingLimit({
      id: '',
      name: '',
      parameterType: 'numeric',
      unit: '',
      description: '',
      validationEvidence: [],
    });
    setLimitDialogOpen(true);
  };

  const handleEditLimit = (limit: CriticalLimitParameter) => {
    setEditingLimit({ ...limit });
    setLimitDialogOpen(true);
  };

  const handleSaveLimit = () => {
    if (editingLimit) {
      const updatedLimits = [...formData.criticalLimits];
      const existingIndex = updatedLimits.findIndex(l => l.id === editingLimit.id);
      
      if (existingIndex >= 0) {
        updatedLimits[existingIndex] = editingLimit;
      } else {
        updatedLimits.push({ ...editingLimit, id: Date.now().toString() });
      }
      
      setFormData(prev => ({ ...prev, criticalLimits: updatedLimits }));
      setLimitDialogOpen(false);
      setEditingLimit(null);
    }
  };

  const handleDeleteLimit = (limitId: string) => {
    const updatedLimits = formData.criticalLimits.filter(l => l.id !== limitId);
    setFormData(prev => ({ ...prev, criticalLimits: updatedLimits }));
  };

  const handleAddEvidence = () => {
    setEditingEvidence({
      id: '',
      type: 'sop',
      title: '',
      description: '',
      date: new Date().toISOString().split('T')[0],
      approved: false,
    });
    setEvidenceDialogOpen(true);
  };

  const handleEditEvidence = (evidence: ValidationEvidence) => {
    setEditingEvidence({ ...evidence });
    setEvidenceDialogOpen(true);
  };

  const handleSaveEvidence = () => {
    if (editingEvidence && selectedLimit) {
      const updatedEvidence = [...selectedLimit.validationEvidence];
      const existingIndex = updatedEvidence.findIndex(e => e.id === editingEvidence.id);
      
      if (existingIndex >= 0) {
        updatedEvidence[existingIndex] = editingEvidence;
      } else {
        updatedEvidence.push({ ...editingEvidence, id: Date.now().toString() });
      }
      
      const updatedLimits = formData.criticalLimits.map(limit =>
        limit.id === selectedLimit.id
          ? { ...limit, validationEvidence: updatedEvidence }
          : limit
      );
      
      setFormData(prev => ({ ...prev, criticalLimits: updatedLimits }));
      setEvidenceDialogOpen(false);
      setEditingEvidence(null);
      setSelectedLimit(null);
    }
  };

  const handleDeleteEvidence = (evidenceId: string) => {
    if (selectedLimit) {
      const updatedEvidence = selectedLimit.validationEvidence.filter(e => e.id !== evidenceId);
      const updatedLimits = formData.criticalLimits.map(limit =>
        limit.id === selectedLimit.id
          ? { ...limit, validationEvidence: updatedEvidence }
          : limit
      );
      setFormData(prev => ({ ...prev, criticalLimits: updatedLimits }));
    }
  };

  const handleSave = () => {
    onSave(formData);
  };

  const getParameterTypeIcon = (type: string) => {
    switch (type) {
      case 'numeric':
        return <TrendingUp />;
      case 'qualitative':
        return <Assessment />;
      case 'time':
        return <Schedule />;
      case 'temperature':
        return <Science />;
      case 'ph':
        return <Build />;
      case 'pressure':
        return <TrendingDown />;
      case 'flow_rate':
        return <TrendingUp />;
      default:
        return <Settings />;
    }
  };

  const getEvidenceTypeIcon = (type: string) => {
    switch (type) {
      case 'sop':
        return <AttachFile />;
      case 'study':
        return <Science />;
      case 'certificate':
        return <VerifiedUser />;
      case 'test_result':
        return <Assessment />;
      case 'expert_opinion':
        return <Security />;
      default:
        return <AttachFile />;
    }
  };

  return (
    <Card>
      <CardHeader
        title={`${ccp ? 'Edit' : 'Create'} CCP ${formData.ccpNumber}`}
        subheader="Critical Control Point Configuration"
        action={
          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              startIcon={<Cancel />}
              onClick={onCancel}
            >
              Cancel
            </Button>
            {onDelete && ccp && (
              <Button
                variant="outlined"
                color="error"
                startIcon={<Delete />}
                onClick={() => onDelete(ccp.id)}
              >
                Delete
              </Button>
            )}
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
            >
              Save CCP
            </Button>
          </Stack>
        }
      />
      <CardContent>
        <Grid container spacing={3}>
          {/* Basic Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Basic Information
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="CCP Number"
              type="number"
              value={formData.ccpNumber}
              onChange={(e) => handleInputChange('ccpNumber', parseInt(e.target.value))}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="CCP Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Process Step"
              value={formData.processStep}
              onChange={(e) => handleInputChange('processStep', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Hazard"
              value={formData.hazard}
              onChange={(e) => handleInputChange('hazard', e.target.value)}
            />
          </Grid>

          {/* Critical Limits */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Critical Limits
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={handleAddLimit}
              >
                Add Limit
              </Button>
            </Box>
            
            {formData.criticalLimits.length === 0 ? (
              <Alert severity="info">
                No critical limits defined. Add at least one critical limit for this CCP.
              </Alert>
            ) : (
              <List>
                {formData.criticalLimits.map((limit, index) => (
                  <Accordion key={limit.id}>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                        {getParameterTypeIcon(limit.parameterType)}
                        <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                          {limit.name}
                        </Typography>
                        <Chip
                          label={limit.parameterType}
                          size="small"
                          variant="outlined"
                        />
                        <Stack direction="row" spacing={1}>
                          <Tooltip title="Edit Limit">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEditLimit(limit);
                              }}
                            >
                              <Edit />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Limit">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteLimit(limit.id);
                              }}
                            >
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="textSecondary">
                            <strong>Unit:</strong> {limit.unit}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="textSecondary">
                            <strong>Target:</strong> {limit.targetValue || 'N/A'}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="textSecondary">
                            <strong>Range:</strong> {limit.minValue || 'N/A'} - {limit.maxValue || 'N/A'}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="textSecondary">
                            <strong>Tolerance:</strong> ±{limit.tolerance || 'N/A'}
                          </Typography>
                        </Grid>
                        <Grid item xs={12}>
                          <Typography variant="body2" color="textSecondary">
                            <strong>Description:</strong> {limit.description}
                          </Typography>
                        </Grid>
                        
                        {/* Validation Evidence */}
                        <Grid item xs={12}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="subtitle2">
                              Validation Evidence ({limit.validationEvidence.length})
                            </Typography>
                            <Button
                              size="small"
                              startIcon={<Add />}
                              onClick={() => {
                                setSelectedLimit(limit);
                                handleAddEvidence();
                              }}
                            >
                              Add Evidence
                            </Button>
                          </Box>
                          
                          {limit.validationEvidence.length === 0 ? (
                            <Alert severity="warning" sx={{ mt: 1 }}>
                              No validation evidence provided. Add evidence to support this critical limit.
                            </Alert>
                          ) : (
                            <TableContainer component={Paper} variant="outlined">
                              <Table size="small">
                                <TableHead>
                                  <TableRow>
                                    <TableCell>Type</TableCell>
                                    <TableCell>Title</TableCell>
                                    <TableCell>Date</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell>Actions</TableCell>
                                  </TableRow>
                                </TableHead>
                                <TableBody>
                                  {limit.validationEvidence.map((evidence) => (
                                    <TableRow key={evidence.id}>
                                      <TableCell>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                          {getEvidenceTypeIcon(evidence.type)}
                                          <Typography variant="body2">
                                            {evidenceTypes.find(t => t.value === evidence.type)?.label}
                                          </Typography>
                                        </Box>
                                      </TableCell>
                                      <TableCell>{evidence.title}</TableCell>
                                      <TableCell>{new Date(evidence.date).toLocaleDateString()}</TableCell>
                                      <TableCell>
                                        <Chip
                                          label={evidence.approved ? 'Approved' : 'Pending'}
                                          size="small"
                                          color={evidence.approved ? 'success' : 'warning'}
                                        />
                                      </TableCell>
                                      <TableCell>
                                        <Stack direction="row" spacing={1}>
                                          <Tooltip title="Edit Evidence">
                                            <IconButton
                                              size="small"
                                              onClick={() => {
                                                setSelectedLimit(limit);
                                                handleEditEvidence(evidence);
                                              }}
                                            >
                                              <Edit />
                                            </IconButton>
                                          </Tooltip>
                                          <Tooltip title="Delete Evidence">
                                            <IconButton
                                              size="small"
                                              color="error"
                                              onClick={() => handleDeleteEvidence(evidence.id)}
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
                          )}
                        </Grid>
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </List>
            )}
          </Grid>

          {/* Monitoring */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Monitoring
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Monitoring Method"
              value={formData.monitoringMethod}
              onChange={(e) => handleInputChange('monitoringMethod', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Monitoring Frequency"
              value={formData.monitoringFrequency}
              onChange={(e) => handleInputChange('monitoringFrequency', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Monitoring Responsibility"
              value={formData.monitoringResponsibility}
              onChange={(e) => handleInputChange('monitoringResponsibility', e.target.value)}
            />
          </Grid>

          {/* Corrective Actions */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Corrective Actions
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Corrective Actions"
              value={formData.correctiveActions.join('\n')}
              onChange={(e) => handleInputChange('correctiveActions', e.target.value.split('\n').filter(line => line.trim()))}
              helperText="Enter each corrective action on a new line"
            />
          </Grid>

          {/* Verification */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Verification
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Verification Method"
              value={formData.verificationMethod}
              onChange={(e) => handleInputChange('verificationMethod', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Verification Frequency"
              value={formData.verificationFrequency}
              onChange={(e) => handleInputChange('verificationFrequency', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Verification Responsibility"
              value={formData.verificationResponsibility}
              onChange={(e) => handleInputChange('verificationResponsibility', e.target.value)}
            />
          </Grid>

          {/* Additional Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Additional Information
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Autocomplete
              multiple
              freeSolo
              options={[]}
              value={formData.sopReferences}
              onChange={(event, newValue) => handleInputChange('sopReferences', newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="SOP References"
                  placeholder="Add SOP reference..."
                />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    variant="outlined"
                    label={option}
                    {...getTagProps({ index })}
                  />
                ))
              }
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <Autocomplete
              multiple
              freeSolo
              options={[]}
              value={formData.equipment}
              onChange={(event, newValue) => handleInputChange('equipment', newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Equipment"
                  placeholder="Add equipment..."
                />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    variant="outlined"
                    label={option}
                    {...getTagProps({ index })}
                  />
                ))
              }
            />
          </Grid>
          <Grid item xs={12}>
            <Autocomplete
              multiple
              freeSolo
              options={[]}
              value={formData.trainingRequirements}
              onChange={(event, newValue) => handleInputChange('trainingRequirements', newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Training Requirements"
                  placeholder="Add training requirement..."
                />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    variant="outlined"
                    label={option}
                    {...getTagProps({ index })}
                  />
                ))
              }
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.isActive}
                  onChange={(e) => handleInputChange('isActive', e.target.checked)}
                />
              }
              label="CCP is Active"
            />
          </Grid>
        </Grid>
      </CardContent>

      {/* Critical Limit Dialog */}
      <Dialog open={limitDialogOpen} onClose={() => setLimitDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingLimit?.id ? 'Edit' : 'Add'} Critical Limit
        </DialogTitle>
        <DialogContent>
          {editingLimit && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Parameter Name"
                  value={editingLimit.name}
                  onChange={(e) => handleLimitChange('name', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Parameter Type</InputLabel>
                  <Select
                    value={editingLimit.parameterType}
                    label="Parameter Type"
                    onChange={(e) => handleLimitChange('parameterType', e.target.value)}
                  >
                    {parameterTypes.map(type => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Unit</InputLabel>
                  <Select
                    value={editingLimit.unit}
                    label="Unit"
                    onChange={(e) => handleLimitChange('unit', e.target.value)}
                  >
                    {units[editingLimit.parameterType as keyof typeof units]?.map(unit => (
                      <MenuItem key={unit} value={unit}>
                        {unit}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Target Value"
                  type="number"
                  value={editingLimit.targetValue || ''}
                  onChange={(e) => handleLimitChange('targetValue', parseFloat(e.target.value) || undefined)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Minimum Value"
                  type="number"
                  value={editingLimit.minValue || ''}
                  onChange={(e) => handleLimitChange('minValue', parseFloat(e.target.value) || undefined)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Maximum Value"
                  type="number"
                  value={editingLimit.maxValue || ''}
                  onChange={(e) => handleLimitChange('maxValue', parseFloat(e.target.value) || undefined)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Tolerance (±)"
                  type="number"
                  value={editingLimit.tolerance || ''}
                  onChange={(e) => handleLimitChange('tolerance', parseFloat(e.target.value) || undefined)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={editingLimit.description}
                  onChange={(e) => handleLimitChange('description', e.target.value)}
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLimitDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveLimit} variant="contained">
            Save Limit
          </Button>
        </DialogActions>
      </Dialog>

      {/* Validation Evidence Dialog */}
      <Dialog open={evidenceDialogOpen} onClose={() => setEvidenceDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingEvidence?.id ? 'Edit' : 'Add'} Validation Evidence
        </DialogTitle>
        <DialogContent>
          {editingEvidence && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Evidence Type</InputLabel>
                  <Select
                    value={editingEvidence.type}
                    label="Evidence Type"
                    onChange={(e) => handleEvidenceChange('type', e.target.value)}
                  >
                    {evidenceTypes.map(type => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Date"
                  type="date"
                  value={editingEvidence.date}
                  onChange={(e) => handleEvidenceChange('date', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Title"
                  value={editingEvidence.title}
                  onChange={(e) => handleEvidenceChange('title', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={editingEvidence.description}
                  onChange={(e) => handleEvidenceChange('description', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Document ID (optional)"
                  value={editingEvidence.documentId || ''}
                  onChange={(e) => handleEvidenceChange('documentId', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="External Reference (optional)"
                  value={editingEvidence.externalReference || ''}
                  onChange={(e) => handleEvidenceChange('externalReference', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={editingEvidence.approved}
                      onChange={(e) => handleEvidenceChange('approved', e.target.checked)}
                    />
                  }
                  label="Evidence Approved"
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEvidenceDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveEvidence} variant="contained">
            Save Evidence
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default CCPEditor;
