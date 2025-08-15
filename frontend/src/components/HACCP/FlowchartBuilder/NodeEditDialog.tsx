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
  Box,
  Typography,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Chip,
  Divider,
  FormControlLabel,
  Switch,
  InputAdornment,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  ExpandMore,
  Add,
  Delete,
  Warning,
  Security,
  Science,
  ContactSupport,
} from '@mui/icons-material';
import { Node } from 'reactflow';
import { HACCPNodeData, HACCPNodeType } from './types';

interface NodeEditDialogProps {
  open: boolean;
  node: Node;
  onClose: () => void;
  onSave: (nodeId: string, updatedData: Partial<HACCPNodeData>) => void;
  readOnly?: boolean;
}

interface HazardForm {
  id: string;
  type: 'biological' | 'chemical' | 'physical' | 'allergen';
  description: string;
  likelihood: number;
  severity: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  controlMeasures: string;
  isCCP: boolean;
}

interface CCPForm {
  number: string;
  criticalLimits: Array<{
    parameter: string;
    min?: number;
    max?: number;
    unit: string;
  }>;
  monitoringFrequency: string;
  monitoringMethod: string;
  responsiblePerson: string;
  correctiveActions: string;
  verificationMethod: string;
}

const NodeEditDialog: React.FC<NodeEditDialogProps> = ({
  open,
  node,
  onClose,
  onSave,
  readOnly = false,
}) => {
  const [formData, setFormData] = useState<HACCPNodeData>({});
  const [hazards, setHazards] = useState<HazardForm[]>([]);
  const [ccpData, setCcpData] = useState<CCPForm>({
    number: '',
    criticalLimits: [],
    monitoringFrequency: '',
    monitoringMethod: '',
    responsiblePerson: '',
    correctiveActions: '',
    verificationMethod: '',
  });

  useEffect(() => {
    if (node) {
      setFormData(node.data);
      setHazards(node.data.hazards || []);
      setCcpData(node.data.ccp || {
        number: '',
        criticalLimits: [],
        monitoringFrequency: '',
        monitoringMethod: '',
        responsiblePerson: '',
        correctiveActions: '',
        verificationMethod: '',
      });
    }
  }, [node]);

  const calculateRiskLevel = (likelihood: number, severity: number): 'low' | 'medium' | 'high' | 'critical' => {
    const risk = likelihood * severity;
    if (risk >= 20) return 'critical';
    if (risk >= 12) return 'high';
    if (risk >= 6) return 'medium';
    return 'low';
  };

  const handleBasicFieldChange = (field: keyof HACCPNodeData) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const handleParameterChange = (parameter: 'temperature' | 'time' | 'ph' | 'waterActivity', field: string) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.value;
    setFormData(prev => ({
      ...prev,
      [parameter]: {
        ...prev[parameter],
        [field]: field === 'unit' ? value : parseFloat(value) || undefined,
      },
    }));
  };

  const addHazard = () => {
    const newHazard: HazardForm = {
      id: `hazard_${Date.now()}`,
      type: 'biological',
      description: '',
      likelihood: 1,
      severity: 1,
      riskLevel: 'low',
      controlMeasures: '',
      isCCP: false,
    };
    setHazards(prev => [...prev, newHazard]);
  };

  const updateHazard = (index: number, field: keyof HazardForm, value: any) => {
    setHazards(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      
      // Auto-calculate risk level when likelihood or severity changes
      if (field === 'likelihood' || field === 'severity') {
        updated[index].riskLevel = calculateRiskLevel(
          updated[index].likelihood,
          updated[index].severity
        );
      }
      
      return updated;
    });
  };

  const removeHazard = (index: number) => {
    setHazards(prev => prev.filter((_, i) => i !== index));
  };

  const addCriticalLimit = () => {
    setCcpData(prev => ({
      ...prev,
      criticalLimits: [
        ...prev.criticalLimits,
        { parameter: '', min: undefined, max: undefined, unit: '' },
      ],
    }));
  };

  const updateCriticalLimit = (index: number, field: string, value: any) => {
    setCcpData(prev => ({
      ...prev,
      criticalLimits: prev.criticalLimits.map((limit, i) =>
        i === index ? { ...limit, [field]: value } : limit
      ),
    }));
  };

  const removeCriticalLimit = (index: number) => {
    setCcpData(prev => ({
      ...prev,
      criticalLimits: prev.criticalLimits.filter((_, i) => i !== index),
    }));
  };

  const handleSave = () => {
    const hasCCP = hazards.some(h => h.isCCP) || ccpData.number;
    
    const updatedData: Partial<HACCPNodeData> = {
      ...formData,
      hazards: hazards.length > 0 ? hazards : undefined,
      ccp: hasCCP ? ccpData : undefined,
    };

    onSave(node.id, updatedData);
  };

  const getHazardIcon = (type: string) => {
    switch (type) {
      case 'biological': return <Science color="error" />;
      case 'chemical': return <Warning color="warning" />;
      case 'physical': return <Security color="info" />;
      case 'allergen': return <ContactSupport color="secondary" />;
      default: return <Warning />;
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        Edit Node: {node?.data?.label}
        <Typography variant="body2" color="text.secondary">
          Type: {node?.data?.nodeType?.replace(/_/g, ' ')}
        </Typography>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ py: 2 }}>
          {/* Basic Information */}
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6">Basic Information</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Step Number"
                    type="number"
                    value={formData.stepNumber || ''}
                    onChange={handleBasicFieldChange('stepNumber')}
                    disabled={readOnly}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Equipment"
                    value={formData.equipment || ''}
                    onChange={handleBasicFieldChange('equipment')}
                    disabled={readOnly}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    multiline
                    rows={3}
                    value={formData.description || ''}
                    onChange={handleBasicFieldChange('description')}
                    disabled={readOnly}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Process Parameters */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6">Process Parameters</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                {/* Temperature */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" gutterBottom>Temperature</Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={4}>
                      <TextField
                        size="small"
                        label="Min"
                        type="number"
                        value={formData.temperature?.min || ''}
                        onChange={handleParameterChange('temperature', 'min')}
                        disabled={readOnly}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">°</InputAdornment>,
                        }}
                      />
                    </Grid>
                    <Grid item xs={4}>
                      <TextField
                        size="small"
                        label="Max"
                        type="number"
                        value={formData.temperature?.max || ''}
                        onChange={handleParameterChange('temperature', 'max')}
                        disabled={readOnly}
                        InputProps={{
                          endAdornment: <InputAdornment position="end">°</InputAdornment>,
                        }}
                      />
                    </Grid>
                    <Grid item xs={4}>
                      <FormControl size="small" fullWidth>
                        <InputLabel>Unit</InputLabel>
                        <Select
                          value={formData.temperature?.unit || 'C'}
                          onChange={(e) => handleParameterChange('temperature', 'unit')(e as any)}
                          disabled={readOnly}
                        >
                          <MenuItem value="C">°C</MenuItem>
                          <MenuItem value="F">°F</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </Grid>

                {/* Time */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" gutterBottom>Time</Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={8}>
                      <TextField
                        size="small"
                        label="Duration"
                        type="number"
                        value={formData.time?.duration || ''}
                        onChange={handleParameterChange('time', 'duration')}
                        disabled={readOnly}
                      />
                    </Grid>
                    <Grid item xs={4}>
                      <FormControl size="small" fullWidth>
                        <InputLabel>Unit</InputLabel>
                        <Select
                          value={formData.time?.unit || 'minutes'}
                          onChange={(e) => handleParameterChange('time', 'unit')(e as any)}
                          disabled={readOnly}
                        >
                          <MenuItem value="seconds">sec</MenuItem>
                          <MenuItem value="minutes">min</MenuItem>
                          <MenuItem value="hours">hr</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </Grid>

                {/* pH */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" gutterBottom>pH</Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <TextField
                        size="small"
                        label="Min"
                        type="number"
                        inputProps={{ step: 0.1, min: 0, max: 14 }}
                        value={formData.ph?.min || ''}
                        onChange={handleParameterChange('ph', 'min')}
                        disabled={readOnly}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        size="small"
                        label="Max"
                        type="number"
                        inputProps={{ step: 0.1, min: 0, max: 14 }}
                        value={formData.ph?.max || ''}
                        onChange={handleParameterChange('ph', 'max')}
                        disabled={readOnly}
                      />
                    </Grid>
                  </Grid>
                </Grid>

                {/* Water Activity */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" gutterBottom>Water Activity (aw)</Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <TextField
                        size="small"
                        label="Min"
                        type="number"
                        inputProps={{ step: 0.01, min: 0, max: 1 }}
                        value={formData.waterActivity?.min || ''}
                        onChange={handleParameterChange('waterActivity', 'min')}
                        disabled={readOnly}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        size="small"
                        label="Max"
                        type="number"
                        inputProps={{ step: 0.01, min: 0, max: 1 }}
                        value={formData.waterActivity?.max || ''}
                        onChange={handleParameterChange('waterActivity', 'max')}
                        disabled={readOnly}
                      />
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Hazard Analysis */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', pr: 2 }}>
                <Typography variant="h6">Hazard Analysis</Typography>
                {!readOnly && (
                  <Button
                    size="small"
                    startIcon={<Add />}
                    onClick={addHazard}
                    variant="outlined"
                  >
                    Add Hazard
                  </Button>
                )}
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {hazards.length === 0 ? (
                <Typography color="text.secondary" align="center" sx={{ py: 2 }}>
                  No hazards identified for this step
                </Typography>
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Type</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell>Likelihood (1-5)</TableCell>
                        <TableCell>Severity (1-5)</TableCell>
                        <TableCell>Risk Level</TableCell>
                        <TableCell>Control Measures</TableCell>
                        <TableCell>CCP</TableCell>
                        {!readOnly && <TableCell>Actions</TableCell>}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {hazards.map((hazard, index) => (
                        <TableRow key={hazard.id}>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {getHazardIcon(hazard.type)}
                              <FormControl size="small" sx={{ minWidth: 100 }}>
                                <Select
                                  value={hazard.type}
                                  onChange={(e) => updateHazard(index, 'type', e.target.value)}
                                  disabled={readOnly}
                                >
                                  <MenuItem value="biological">Biological</MenuItem>
                                  <MenuItem value="chemical">Chemical</MenuItem>
                                  <MenuItem value="physical">Physical</MenuItem>
                                  <MenuItem value="allergen">Allergen</MenuItem>
                                </Select>
                              </FormControl>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              multiline
                              value={hazard.description}
                              onChange={(e) => updateHazard(index, 'description', e.target.value)}
                              disabled={readOnly}
                              sx={{ minWidth: 200 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              type="number"
                              inputProps={{ min: 1, max: 5 }}
                              value={hazard.likelihood}
                              onChange={(e) => updateHazard(index, 'likelihood', parseInt(e.target.value))}
                              disabled={readOnly}
                              sx={{ width: 80 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              type="number"
                              inputProps={{ min: 1, max: 5 }}
                              value={hazard.severity}
                              onChange={(e) => updateHazard(index, 'severity', parseInt(e.target.value))}
                              disabled={readOnly}
                              sx={{ width: 80 }}
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              size="small"
                              label={hazard.riskLevel.toUpperCase()}
                              color={getRiskColor(hazard.riskLevel) as any}
                              variant={hazard.riskLevel === 'low' ? 'outlined' : 'filled'}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              multiline
                              value={hazard.controlMeasures}
                              onChange={(e) => updateHazard(index, 'controlMeasures', e.target.value)}
                              disabled={readOnly}
                              sx={{ minWidth: 200 }}
                            />
                          </TableCell>
                          <TableCell>
                            <FormControlLabel
                              control={
                                <Switch
                                  size="small"
                                  checked={hazard.isCCP}
                                  onChange={(e) => updateHazard(index, 'isCCP', e.target.checked)}
                                  disabled={readOnly}
                                />
                              }
                              label=""
                            />
                          </TableCell>
                          {!readOnly && (
                            <TableCell>
                              <IconButton
                                size="small"
                                onClick={() => removeHazard(index)}
                                color="error"
                              >
                                <Delete />
                              </IconButton>
                            </TableCell>
                          )}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </AccordionDetails>
          </Accordion>

          {/* CCP Details */}
          {(hazards.some(h => h.isCCP) || ccpData.number) && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6" color="error">Critical Control Point (CCP)</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="CCP Number"
                      value={ccpData.number}
                      onChange={(e) => setCcpData(prev => ({ ...prev, number: e.target.value }))}
                      disabled={readOnly}
                      placeholder="e.g., CCP-1"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>Critical Limits</Typography>
                    {!readOnly && (
                      <Button
                        size="small"
                        startIcon={<Add />}
                        onClick={addCriticalLimit}
                        sx={{ mb: 1 }}
                      >
                        Add Critical Limit
                      </Button>
                    )}
                    {ccpData.criticalLimits.map((limit, index) => (
                      <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
                        <TextField
                          size="small"
                          label="Parameter"
                          value={limit.parameter}
                          onChange={(e) => updateCriticalLimit(index, 'parameter', e.target.value)}
                          disabled={readOnly}
                          sx={{ flex: 1 }}
                        />
                        <TextField
                          size="small"
                          label="Min"
                          type="number"
                          value={limit.min || ''}
                          onChange={(e) => updateCriticalLimit(index, 'min', parseFloat(e.target.value))}
                          disabled={readOnly}
                          sx={{ width: 100 }}
                        />
                        <TextField
                          size="small"
                          label="Max"
                          type="number"
                          value={limit.max || ''}
                          onChange={(e) => updateCriticalLimit(index, 'max', parseFloat(e.target.value))}
                          disabled={readOnly}
                          sx={{ width: 100 }}
                        />
                        <TextField
                          size="small"
                          label="Unit"
                          value={limit.unit}
                          onChange={(e) => updateCriticalLimit(index, 'unit', e.target.value)}
                          disabled={readOnly}
                          sx={{ width: 80 }}
                        />
                        {!readOnly && (
                          <IconButton
                            size="small"
                            onClick={() => removeCriticalLimit(index)}
                            color="error"
                          >
                            <Delete />
                          </IconButton>
                        )}
                      </Box>
                    ))}
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Monitoring Frequency"
                      value={ccpData.monitoringFrequency}
                      onChange={(e) => setCcpData(prev => ({ ...prev, monitoringFrequency: e.target.value }))}
                      disabled={readOnly}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Monitoring Method"
                      value={ccpData.monitoringMethod}
                      onChange={(e) => setCcpData(prev => ({ ...prev, monitoringMethod: e.target.value }))}
                      disabled={readOnly}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Responsible Person"
                      value={ccpData.responsiblePerson}
                      onChange={(e) => setCcpData(prev => ({ ...prev, responsiblePerson: e.target.value }))}
                      disabled={readOnly}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Verification Method"
                      value={ccpData.verificationMethod}
                      onChange={(e) => setCcpData(prev => ({ ...prev, verificationMethod: e.target.value }))}
                      disabled={readOnly}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Corrective Actions"
                      multiline
                      rows={3}
                      value={ccpData.correctiveActions}
                      onChange={(e) => setCcpData(prev => ({ ...prev, correctiveActions: e.target.value }))}
                      disabled={readOnly}
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        {!readOnly && (
          <Button onClick={handleSave} variant="contained">
            Save Changes
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default NodeEditDialog;
