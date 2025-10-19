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
  Alert,
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
  risk_strategy?: 'ccp' | 'opprp' | 'use_existing_prps';
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
      console.log('[NodeEditDialog] ========== NODE EDIT DIALOG OPENED ==========');
      console.log('[NodeEditDialog] Full node:', node);
      console.log('[NodeEditDialog] Node ID:', node.id);
      console.log('[NodeEditDialog] Node type:', node.type);
      console.log('[NodeEditDialog] Node data:', node.data);
      console.log('[NodeEditDialog] Hazards count:', node.data.hazards?.length || 0);
      console.log('[NodeEditDialog] Hazards detail:', node.data.hazards);
      console.log('[NodeEditDialog] Has CCP?', !!node.data.ccp);
      console.log('[NodeEditDialog] CCP data received:', node.data.ccp);
      
      if (node.data.hazards) {
        const ccpHazards = node.data.hazards.filter((h: any) => h.isCCP);
        console.log('[NodeEditDialog] Hazards marked as CCP:', ccpHazards);
      }
      
      setFormData(node.data);
      setHazards(node.data.hazards || []);
      
      const ccpDataToSet = node.data.ccp || {
        number: '',
        criticalLimits: [],
        monitoringFrequency: '',
        monitoringMethod: '',
        responsiblePerson: '',
        correctiveActions: '',
        verificationMethod: '',
      };
      
      console.log('[NodeEditDialog] Setting ccpData to:', ccpDataToSet);
      setCcpData(ccpDataToSet);
      console.log('[NodeEditDialog] ================================================');
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


  const handleSave = () => {
    // Only save editable fields (Basic Information and Process Parameters)
    // Hazards and CCP data are read-only and managed elsewhere
    const updatedData: Partial<HACCPNodeData> = {
      stepNumber: formData.stepNumber,
      description: formData.description,
      equipment: formData.equipment,
      temperature: formData.temperature,
      time: formData.time,
      ph: formData.ph,
      waterActivity: formData.waterActivity,
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
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {hazards.length === 0 ? (
                <Typography color="text.secondary" align="center" sx={{ py: 2 }}>
                  No hazards attached to this step
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
                        <TableCell>Strategy</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {hazards.map((hazard, index) => (
                        <TableRow key={hazard.id}>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {getHazardIcon(hazard.type)}
                              <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                                {hazard.type}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {hazard.description}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {hazard.likelihood}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {hazard.severity}
                            </Typography>
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
                            <Typography variant="body2">
                              {hazard.controlMeasures}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              size="small"
                              label={
                                hazard.risk_strategy === 'ccp' ? 'CCP' :
                                hazard.risk_strategy === 'opprp' ? 'OPRP' :
                                hazard.risk_strategy === 'use_existing_prps' ? 'PRP' :
                                'N/A'
                              }
                              color={
                                hazard.risk_strategy === 'ccp' ? 'error' :
                                hazard.risk_strategy === 'opprp' ? 'warning' :
                                hazard.risk_strategy === 'use_existing_prps' ? 'info' :
                                'default'
                              }
                              variant="filled"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </AccordionDetails>
          </Accordion>

          {/* PRP Details */}
          {hazards.some(h => h.risk_strategy === 'use_existing_prps') && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6" color="info.main">Prerequisite Programs (PRPs)</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      The following hazards at this step are managed by existing Prerequisite Programs:
                    </Typography>
                  </Grid>
                  
                  {hazards
                    .filter(h => h.risk_strategy === 'use_existing_prps')
                    .map((hazard, index) => (
                      <Grid item xs={12} key={hazard.id}>
                        <Paper variant="outlined" sx={{ p: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            {getHazardIcon(hazard.type)}
                            <Typography variant="subtitle2" fontWeight="bold">
                              {hazard.description}
                            </Typography>
                            <Chip 
                              label="PRP" 
                              color="info" 
                              size="small"
                              variant="filled"
                            />
                          </Box>
                          
                          <Grid container spacing={2} sx={{ mt: 1 }}>
                            <Grid item xs={6} sm={3}>
                              <Typography variant="caption" color="text.secondary">
                                Hazard Type
                              </Typography>
                              <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                                {hazard.type}
                              </Typography>
                            </Grid>
                            
                            <Grid item xs={6} sm={3}>
                              <Typography variant="caption" color="text.secondary">
                                Likelihood
                              </Typography>
                              <Typography variant="body2">
                                {hazard.likelihood}/5
                              </Typography>
                            </Grid>
                            
                            <Grid item xs={6} sm={3}>
                              <Typography variant="caption" color="text.secondary">
                                Severity
                              </Typography>
                              <Typography variant="body2">
                                {hazard.severity}/5
                              </Typography>
                            </Grid>
                            
                            <Grid item xs={6} sm={3}>
                              <Typography variant="caption" color="text.secondary">
                                Risk Level
                              </Typography>
                              <Chip
                                size="small"
                                label={hazard.riskLevel.toUpperCase()}
                                color={getRiskColor(hazard.riskLevel) as any}
                                variant={hazard.riskLevel === 'low' ? 'outlined' : 'filled'}
                              />
                            </Grid>
                            
                            {hazard.controlMeasures && (
                              <Grid item xs={12}>
                                <Typography variant="caption" color="text.secondary">
                                  Control Measures
                                </Typography>
                                <Typography variant="body2">
                                  {hazard.controlMeasures}
                                </Typography>
                              </Grid>
                            )}
                          </Grid>
                        </Paper>
                      </Grid>
                    ))}
                  
                  <Grid item xs={12}>
                    <Alert severity="info" sx={{ mt: 1 }}>
                      <Typography variant="body2">
                        These hazards are controlled by general Prerequisite Programs (Good Manufacturing Practices, 
                        Good Hygiene Practices, etc.) and do not require specific CCPs or OPRPs.
                      </Typography>
                    </Alert>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* OPRP Details */}
          {hazards.some(h => h.risk_strategy === 'opprp') && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6" color="warning.main">Operational Prerequisite Programs (OPRPs)</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      The following hazards at this step require Operational Prerequisite Programs:
                    </Typography>
                  </Grid>
                  
                  {hazards
                    .filter(h => h.risk_strategy === 'opprp')
                    .map((hazard, index) => (
                      <Grid item xs={12} key={hazard.id}>
                        <Paper variant="outlined" sx={{ p: 2, borderColor: 'warning.main' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            {getHazardIcon(hazard.type)}
                            <Typography variant="subtitle2" fontWeight="bold">
                              {hazard.description}
                            </Typography>
                            <Chip 
                              label="OPRP" 
                              color="warning" 
                              size="small"
                              variant="filled"
                            />
                          </Box>
                          
                          <Grid container spacing={2} sx={{ mt: 1 }}>
                            <Grid item xs={6} sm={3}>
                              <Typography variant="caption" color="text.secondary">
                                Hazard Type
                              </Typography>
                              <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                                {hazard.type}
                              </Typography>
                            </Grid>
                            
                            <Grid item xs={6} sm={3}>
                              <Typography variant="caption" color="text.secondary">
                                Likelihood
                              </Typography>
                              <Typography variant="body2">
                                {hazard.likelihood}/5
                              </Typography>
                            </Grid>
                            
                            <Grid item xs={6} sm={3}>
                              <Typography variant="caption" color="text.secondary">
                                Severity
                              </Typography>
                              <Typography variant="body2">
                                {hazard.severity}/5
                              </Typography>
                            </Grid>
                            
                            <Grid item xs={6} sm={3}>
                              <Typography variant="caption" color="text.secondary">
                                Risk Level
                              </Typography>
                              <Chip
                                size="small"
                                label={hazard.riskLevel.toUpperCase()}
                                color={getRiskColor(hazard.riskLevel) as any}
                                variant={hazard.riskLevel === 'low' ? 'outlined' : 'filled'}
                              />
                            </Grid>
                            
                            {hazard.controlMeasures && (
                              <Grid item xs={12}>
                                <Typography variant="caption" color="text.secondary">
                                  Control Measures
                                </Typography>
                                <Typography variant="body2">
                                  {hazard.controlMeasures}
                                </Typography>
                              </Grid>
                            )}
                          </Grid>
                        </Paper>
                      </Grid>
                    ))}
                  
                  <Grid item xs={12}>
                    <Alert severity="warning" sx={{ mt: 1 }}>
                      <Typography variant="body2">
                        OPRPs are control measures applied to prevent or reduce significant food safety hazards 
                        to acceptable levels. Unlike CCPs, critical limits cannot be established for these controls, 
                        but operational limits are defined.
                      </Typography>
                    </Alert>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* CCP Details */}
          {(hazards.some(h => h.isCCP) || ccpData.number) && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6" color="error">Critical Control Point (CCP)</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={3}>
                  {ccpData.number && (
                    <Grid item xs={12}>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          CCP Number
                        </Typography>
                        <Chip 
                          label={ccpData.number} 
                          color="error" 
                          variant="filled"
                          sx={{ fontWeight: 'bold' }}
                        />
                      </Box>
                    </Grid>
                  )}

                  {ccpData.criticalLimits && ccpData.criticalLimits.length > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Critical Limits
                      </Typography>
                      <TableContainer component={Paper} variant="outlined">
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Parameter</TableCell>
                              <TableCell>Minimum</TableCell>
                              <TableCell>Maximum</TableCell>
                              <TableCell>Unit</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {ccpData.criticalLimits.map((limit, index) => (
                              <TableRow key={index}>
                                <TableCell>
                                  <Typography variant="body2" fontWeight="medium">
                                    {limit.parameter}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2">
                                    {limit.min !== undefined ? limit.min : '-'}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2">
                                    {limit.max !== undefined ? limit.max : '-'}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2">
                                    {limit.unit || '-'}
                                  </Typography>
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Grid>
                  )}

                  {ccpData.monitoringFrequency && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Monitoring Frequency
                      </Typography>
                      <Typography variant="body2">
                        {ccpData.monitoringFrequency}
                      </Typography>
                    </Grid>
                  )}

                  {ccpData.monitoringMethod && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Monitoring Method
                      </Typography>
                      <Typography variant="body2">
                        {ccpData.monitoringMethod}
                      </Typography>
                    </Grid>
                  )}

                  {ccpData.responsiblePerson && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Responsible Person
                      </Typography>
                      <Typography variant="body2">
                        {ccpData.responsiblePerson}
                      </Typography>
                    </Grid>
                  )}

                  {ccpData.verificationMethod && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Verification Method
                      </Typography>
                      <Typography variant="body2">
                        {ccpData.verificationMethod}
                      </Typography>
                    </Grid>
                  )}

                  {ccpData.correctiveActions && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Corrective Actions
                      </Typography>
                      <Typography variant="body2">
                        {ccpData.correctiveActions}
                      </Typography>
                    </Grid>
                  )}

                  {!ccpData.number && (!ccpData.criticalLimits || ccpData.criticalLimits.length === 0) && (
                    <Grid item xs={12}>
                      <Alert severity="info" sx={{ my: 2 }}>
                        <Typography variant="body2">
                          No CCP details available for this step
                        </Typography>
                        <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                          Debug info: {JSON.stringify({
                            hasCcpData: !!node.data.ccp,
                            ccpNumber: ccpData.number || 'none',
                            criticalLimitsCount: ccpData.criticalLimits?.length || 0,
                            hasMonitoring: !!ccpData.monitoringMethod,
                          })}
                        </Typography>
                      </Alert>
                    </Grid>
                  )}
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
