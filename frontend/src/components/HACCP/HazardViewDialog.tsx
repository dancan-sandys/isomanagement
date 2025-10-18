import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Typography,
  Paper,
  Chip,
  Divider,
  Box,
  Card,
  CardContent,
} from '@mui/material';
import { Security, Warning, Info } from '@mui/icons-material';

interface HazardViewData {
  id: number;
  process_step_id: number;
  hazard_type: string;
  hazard_name: string;
  description?: string;
  consequences?: string;
  likelihood: number;
  severity: number;
  risk_score: number;
  risk_level: string;
  control_measures?: string;
  risk_strategy?: string;
  risk_strategy_justification?: string;
  subsequent_step?: string;
  is_ccp: boolean;
  ccp_justification?: string;
  references?: any[];
  prp_reference_ids?: number[];
}

interface HazardViewDialogProps {
  open: boolean;
  onClose: () => void;
  hazardData: HazardViewData | null;
  processFlows: Array<{ id: number; step_number: number; step_name: string }>;
}

const HazardViewDialog: React.FC<HazardViewDialogProps> = ({
  open,
  onClose,
  hazardData,
  processFlows,
}) => {
  if (!hazardData) return null;

  const getProcessStepName = () => {
    const flow = processFlows.find(f => f.id === hazardData.process_step_id);
    return flow ? `${flow.step_number}. ${flow.step_name}` : 'Unknown';
  };

  const getRiskLevelColor = () => {
    switch (hazardData.risk_level?.toLowerCase()) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getRiskStrategyIcon = () => {
    switch (hazardData.risk_strategy) {
      case 'ccp': return <Security />;
      case 'opprp': return <Warning />;
      case 'use_existing_prps': return <Info />;
      default: return null;
    }
  };

  const getRiskStrategyLabel = () => {
    switch (hazardData.risk_strategy) {
      case 'ccp': return 'CCP (Critical Control Point)';
      case 'opprp': return 'OPRP (Operational Prerequisite Program)';
      case 'use_existing_prps': return 'Use Existing PRPs';
      case 'further_analysis': return 'Further Analysis Required';
      default: return 'Not Determined';
    }
  };

  const getRiskStrategyColor = () => {
    switch (hazardData.risk_strategy) {
      case 'ccp': return 'error';
      case 'opprp': return 'warning';
      case 'use_existing_prps': return 'info';
      default: return 'default';
    }
  };

  const getHazardTypeLabel = () => {
    switch (hazardData.hazard_type?.toLowerCase()) {
      case 'biological': return 'Biological';
      case 'chemical': return 'Chemical';
      case 'physical': return 'Physical';
      case 'allergen': return 'Allergen';
      default: return hazardData.hazard_type || 'Unknown';
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">View Hazard</Typography>
          <Chip 
            label={getHazardTypeLabel()} 
            color="primary" 
            size="small" 
          />
        </Box>
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={3} sx={{ mt: 0.5 }}>
          {/* Basic Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom color="primary">
              Basic Information
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
              <Typography variant="caption" color="textSecondary">
                Process Step
              </Typography>
              <Typography variant="body1" fontWeight={500}>
                {getProcessStepName()}
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
              <Typography variant="caption" color="textSecondary">
                Hazard Name
              </Typography>
              <Typography variant="body1" fontWeight={500}>
                {hazardData.hazard_name}
              </Typography>
            </Paper>
          </Grid>

          {hazardData.description && (
            <Grid item xs={12}>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="caption" color="textSecondary">
                  Description
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  {hazardData.description}
                </Typography>
              </Paper>
            </Grid>
          )}

          {hazardData.consequences && (
            <Grid item xs={12}>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="caption" color="textSecondary">
                  Potential Consequences
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  {hazardData.consequences}
                </Typography>
              </Paper>
            </Grid>
          )}

          {/* Risk Assessment */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom color="primary">
              Risk Assessment
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="caption" color="textSecondary">
                Likelihood
              </Typography>
              <Typography variant="h4" fontWeight={600} sx={{ my: 1 }}>
                {hazardData.likelihood}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                (1-5 scale)
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="caption" color="textSecondary">
                Severity
              </Typography>
              <Typography variant="h4" fontWeight={600} sx={{ my: 1 }}>
                {hazardData.severity}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                (1-5 scale)
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="caption" color="textSecondary">
                Risk Score
              </Typography>
              <Typography variant="h4" fontWeight={600} sx={{ my: 1 }}>
                {hazardData.risk_score}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                L × S
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: getRiskLevelColor() === 'error' ? '#ffebee' : getRiskLevelColor() === 'warning' ? '#fff3e0' : getRiskLevelColor() === 'info' ? '#e3f2fd' : '#e8f5e9' }}>
              <Typography variant="caption" color="textSecondary">
                Risk Level
              </Typography>
              <Chip
                label={hazardData.risk_level?.toUpperCase() || 'N/A'}
                color={getRiskLevelColor() as any}
                sx={{ my: 1, fontWeight: 'bold' }}
              />
            </Paper>
          </Grid>

          {hazardData.control_measures && (
            <Grid item xs={12}>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="caption" color="textSecondary">
                  Existing Control Measures
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  {hazardData.control_measures}
                </Typography>
              </Paper>
            </Grid>
          )}

          {/* Risk Strategy */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom color="primary">
              Risk Control Strategy
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12}>
            <Card sx={{ 
              bgcolor: hazardData.risk_strategy === 'ccp' ? '#ffebee' : 
                       hazardData.risk_strategy === 'opprp' ? '#fff3e0' : 
                       '#e3f2fd',
              border: 2,
              borderColor: hazardData.risk_strategy === 'ccp' ? 'error.main' : 
                          hazardData.risk_strategy === 'opprp' ? 'warning.main' : 
                          'info.main'
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {getRiskStrategyIcon()}
                  <Chip 
                    label={getRiskStrategyLabel()} 
                    color={getRiskStrategyColor() as any}
                    sx={{ ml: 1, fontWeight: 'bold' }}
                  />
                </Box>

                {hazardData.risk_strategy_justification && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                      Justification
                    </Typography>
                    <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
                      <Typography variant="body2">
                        {hazardData.risk_strategy_justification}
                      </Typography>
                    </Paper>
                  </Box>
                )}

                {hazardData.subsequent_step && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                      Subsequent Control Step
                    </Typography>
                    <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
                      <Typography variant="body2">
                        {hazardData.subsequent_step}
                      </Typography>
                    </Paper>
                  </Box>
                )}

                {hazardData.risk_strategy === 'ccp' && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="textSecondary">
                      ℹ️ This hazard is managed as a Critical Control Point (CCP) in the HACCP Plan
                    </Typography>
                  </Box>
                )}

                {hazardData.risk_strategy === 'opprp' && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="textSecondary">
                      ℹ️ This hazard is managed as an Operational Prerequisite Program (OPRP)
                    </Typography>
                  </Box>
                )}

                {hazardData.risk_strategy === 'use_existing_prps' && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="textSecondary">
                      ℹ️ This hazard is controlled by existing Prerequisite Programs (PRPs)
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* References */}
          {hazardData.references && hazardData.references.length > 0 && (
            <>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom color="primary">
                  References
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12}>
                {hazardData.references.map((ref: any, index: number) => (
                  <Card key={index} sx={{ mb: 1 }}>
                    <CardContent>
                      <Typography variant="body1" fontWeight={600}>
                        {ref.title}
                      </Typography>
                      <Typography variant="caption" color="textSecondary" display="block">
                        Type: {ref.type || 'Document'} {ref.description && `• ${ref.description}`}
                      </Typography>
                      {ref.url && (
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          <a href={ref.url} target="_blank" rel="noopener noreferrer" style={{ color: '#1976d2' }}>
                            {ref.url}
                          </a>
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Grid>
            </>
          )}

          {/* Additional Information */}
          {(hazardData.is_ccp || hazardData.ccp_justification) && (
            <>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom color="primary">
                  CCP Information
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                  <Typography variant="caption" color="textSecondary">
                    Is CCP
                  </Typography>
                  <Typography variant="body1" fontWeight={500}>
                    {hazardData.is_ccp ? 'Yes' : 'No'}
                  </Typography>
                  
                  {hazardData.ccp_justification && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="textSecondary">
                        CCP Justification
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 0.5 }}>
                        {hazardData.ccp_justification}
                      </Typography>
                    </Box>
                  )}
                </Paper>
              </Grid>
            </>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="contained">Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default HazardViewDialog;

