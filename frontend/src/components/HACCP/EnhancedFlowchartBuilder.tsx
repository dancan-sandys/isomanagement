import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
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
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Tooltip,
  Alert,
  Stack,
  Grid,
  Paper,
  Zoom,
  Fade,
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
  ArrowForward,
  ArrowDownward,
  DragIndicator,
  Save,
  Undo,
  Redo,
  Fullscreen,
  ZoomIn,
  ZoomOut,
  FitScreen,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

interface ProcessStep {
  id: string;
  stepNumber: number;
  name: string;
  description: string;
  hazards: Hazard[];
  hasCCPs: boolean;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}

interface Hazard {
  id: string;
  name: string;
  type: 'biological' | 'chemical' | 'physical';
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  isCCP: boolean;
  controlMeasures: string[];
}

interface FlowchartBuilderProps {
  productId: number;
  processSteps: ProcessStep[];
  onSave: (steps: ProcessStep[]) => void;
  onStepClick: (stepId: string) => void;
  onHazardClick: (hazardId: string) => void;
}

const EnhancedFlowchartBuilder: React.FC<FlowchartBuilderProps> = ({
  productId,
  processSteps,
  onSave,
  onStepClick,
  onHazardClick,
}) => {
  const theme = useTheme();
  const [selectedStep, setSelectedStep] = useState<string | null>(null);
  const [showHazards, setShowHazards] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [editMode, setEditMode] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingStep, setEditingStep] = useState<ProcessStep | null>(null);
  const [fullscreen, setFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

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

  const handleStepClick = (stepId: string) => {
    setSelectedStep(stepId);
    onStepClick(stepId);
  };

  const handleHazardClick = (hazardId: string) => {
    onHazardClick(hazardId);
  };

  const handleEditStep = (step: ProcessStep) => {
    setEditingStep(step);
    setEditDialogOpen(true);
  };

  const handleSaveStep = () => {
    if (editingStep) {
      // Update the step in the processSteps array
      const updatedSteps = processSteps.map(step =>
        step.id === editingStep.id ? editingStep : step
      );
      onSave(updatedSteps);
    }
    setEditDialogOpen(false);
    setEditingStep(null);
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.1, 2));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.1, 0.5));
  };

  const handleFitScreen = () => {
    setZoom(1);
  };

  const handleFullscreen = () => {
    setFullscreen(!fullscreen);
  };

  const renderStep = (step: ProcessStep, index: number) => {
    const isSelected = selectedStep === step.id;
    const hasHazards = step.hazards.length > 0;
    const hasCCPs = step.hazards.some(h => h.isCCP);

    return (
      <Box
        key={step.id}
        sx={{
          position: 'relative',
          mb: 2,
          transform: `scale(${zoom})`,
          transition: 'transform 0.2s ease-in-out',
        }}
      >
        <Card
          sx={{
            cursor: 'pointer',
            border: isSelected ? `2px solid ${theme.palette.primary.main}` : '1px solid',
            borderColor: isSelected ? theme.palette.primary.main : theme.palette.divider,
            backgroundColor: isSelected ? theme.palette.action.selected : 'background.paper',
            '&:hover': {
              boxShadow: theme.shadows[4],
              borderColor: theme.palette.primary.main,
            },
            position: 'relative',
            overflow: 'visible',
          }}
          onClick={() => handleStepClick(step.id)}
        >
          <CardHeader
            title={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="h6">
                  Step {step.stepNumber}: {step.name}
                </Typography>
                {hasCCPs && (
                  <Chip
                    icon={<Security />}
                    label="CCP"
                    color="error"
                    size="small"
                    variant="outlined"
                  />
                )}
                <Chip
                  label={step.riskLevel.toUpperCase()}
                  size="small"
                  sx={{
                    backgroundColor: getRiskColor(step.riskLevel),
                    color: 'white',
                    fontWeight: 'bold',
                  }}
                />
              </Box>
            }
            action={
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Tooltip title="Edit Step">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditStep(step);
                    }}
                  >
                    <Edit />
                  </IconButton>
                </Tooltip>
                <Tooltip title="View Details">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleStepClick(step.id);
                    }}
                  >
                    <Visibility />
                  </IconButton>
                </Tooltip>
              </Box>
            }
          />
          <CardContent>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              {step.description}
            </Typography>

            {/* Hazards Overlay */}
            {showHazards && hasHazards && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Hazards ({step.hazards.length})
                </Typography>
                <List dense>
                  {step.hazards.map((hazard, hazardIndex) => (
                    <ListItem
                      key={hazard.id}
                      sx={{
                        py: 0.5,
                        cursor: 'pointer',
                        '&:hover': {
                          backgroundColor: theme.palette.action.hover,
                        },
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleHazardClick(hazard.id);
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        {getHazardIcon(hazard.type)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2">
                              {hazard.name}
                            </Typography>
                            {hazard.isCCP && (
                              <Chip
                                label="CCP"
                                color="error"
                                size="small"
                                variant="outlined"
                              />
                            )}
                            <Chip
                              label={hazard.riskLevel.toUpperCase()}
                              size="small"
                              sx={{
                                backgroundColor: getRiskColor(hazard.riskLevel),
                                color: 'white',
                                fontSize: '0.7rem',
                              }}
                            />
                          </Box>
                        }
                        secondary={
                          <Typography variant="caption" color="textSecondary">
                            {hazard.controlMeasures.join(', ')}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {/* Control Measures Summary */}
            {hasHazards && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="textSecondary">
                  Control Measures: {step.hazards.reduce((acc, h) => acc + h.controlMeasures.length, 0)} total
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Arrow to next step */}
        {index < processSteps.length - 1 && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              my: 1,
              transform: `scale(${zoom})`,
            }}
          >
            <ArrowDownward color="action" />
          </Box>
        )}
      </Box>
    );
  };

  return (
    <Box
      ref={containerRef}
      sx={{
        height: fullscreen ? '100vh' : 'auto',
        width: fullscreen ? '100vw' : 'auto',
        position: fullscreen ? 'fixed' : 'relative',
        top: fullscreen ? 0 : 'auto',
        left: fullscreen ? 0 : 'auto',
        zIndex: fullscreen ? 9999 : 'auto',
        backgroundColor: fullscreen ? 'background.paper' : 'transparent',
        overflow: fullscreen ? 'auto' : 'visible',
      }}
    >
      <Card>
        <CardHeader
          title="Process Flowchart"
          subheader={`Product ID: ${productId} • ${processSteps.length} Steps`}
          action={
            <Stack direction="row" spacing={1}>
              <Tooltip title="Toggle Hazards">
                <IconButton
                  size="small"
                  onClick={() => setShowHazards(!showHazards)}
                  color={showHazards ? 'primary' : 'default'}
                >
                  <Warning />
                </IconButton>
              </Tooltip>
              <Tooltip title="Edit Mode">
                <IconButton
                  size="small"
                  onClick={() => setEditMode(!editMode)}
                  color={editMode ? 'primary' : 'default'}
                >
                  <Edit />
                </IconButton>
              </Tooltip>
              <Tooltip title="Zoom In">
                <IconButton size="small" onClick={handleZoomIn}>
                  <ZoomIn />
                </IconButton>
              </Tooltip>
              <Tooltip title="Zoom Out">
                <IconButton size="small" onClick={handleZoomOut}>
                  <ZoomOut />
                </IconButton>
              </Tooltip>
              <Tooltip title="Fit Screen">
                <IconButton size="small" onClick={handleFitScreen}>
                  <FitScreen />
                </IconButton>
              </Tooltip>
              <Tooltip title="Fullscreen">
                <IconButton size="small" onClick={handleFullscreen}>
                  <Fullscreen />
                </IconButton>
              </Tooltip>
            </Stack>
          }
        />
        <CardContent>
          {/* Flowchart Container */}
          <Box
            sx={{
              minHeight: 400,
              p: 2,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: 1,
              backgroundColor: theme.palette.grey[50],
              overflow: 'auto',
              maxHeight: fullscreen ? 'calc(100vh - 200px)' : 600,
            }}
          >
            {processSteps.length === 0 ? (
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: 300,
                  color: theme.palette.text.secondary,
                }}
              >
                <Science sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" gutterBottom>
                  No Process Steps Defined
                </Typography>
                <Typography variant="body2" textAlign="center">
                  Add process steps to create your HACCP flowchart
                </Typography>
              </Box>
            ) : (
              <Box>
                {processSteps.map((step, index) => renderStep(step, index))}
              </Box>
            )}
          </Box>

          {/* Legend */}
          <Box sx={{ mt: 2, p: 2, backgroundColor: theme.palette.grey[100], borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Legend
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Chip label="LOW" size="small" sx={{ backgroundColor: theme.palette.success.main, color: 'white' }} />
                  <Chip label="MEDIUM" size="small" sx={{ backgroundColor: theme.palette.info.main, color: 'white' }} />
                  <Chip label="HIGH" size="small" sx={{ backgroundColor: theme.palette.warning.main, color: 'white' }} />
                  <Chip label="CRITICAL" size="small" sx={{ backgroundColor: theme.palette.error.main, color: 'white' }} />
                </Stack>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Chip icon={<Security />} label="CCP" size="small" color="error" variant="outlined" />
                  <Chip icon={<Science />} label="Biological" size="small" />
                  <Chip icon={<Warning />} label="Chemical" size="small" />
                  <Chip icon={<Error />} label="Physical" size="small" />
                </Stack>
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>

      {/* Edit Step Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Process Step</DialogTitle>
        <DialogContent>
          {editingStep && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Step Name"
                  value={editingStep.name}
                  onChange={(e) => setEditingStep({ ...editingStep, name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={editingStep.description}
                  onChange={(e) => setEditingStep({ ...editingStep, description: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Risk Level</InputLabel>
                  <Select
                    value={editingStep.riskLevel}
                    label="Risk Level"
                    onChange={(e) => setEditingStep({ ...editingStep, riskLevel: e.target.value as any })}
                  >
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="critical">Critical</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveStep} variant="contained">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EnhancedFlowchartBuilder;
