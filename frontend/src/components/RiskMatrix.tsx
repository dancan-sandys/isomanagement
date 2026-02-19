import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Tooltip,
  Card,
  CardContent,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

interface RiskItem {
  id: number;
  area_name: string;
  process_name?: string;
  risk_rating: 'low' | 'medium' | 'high' | 'critical';
  risk_score?: number;
  rationale: string;
  last_audit_date?: string;
  next_audit_due?: string;
  priority_score?: number;
}

interface RiskMatrixProps {
  risks: RiskItem[];
  title?: string;
  onRiskClick?: (risk: RiskItem) => void;
}

const RiskMatrix: React.FC<RiskMatrixProps> = ({ risks, title = "Risk Matrix", onRiskClick }) => {
  // Group risks by rating
  const riskGroups = {
    critical: risks.filter(r => r.risk_rating === 'critical'),
    high: risks.filter(r => r.risk_rating === 'high'),
    medium: risks.filter(r => r.risk_rating === 'medium'),
    low: risks.filter(r => r.risk_rating === 'low'),
  };

  const getRiskColor = (rating: string) => {
    switch (rating) {
      case 'critical': return '#d32f2f';
      case 'high': return '#f57c00';
      case 'medium': return '#fbc02d';
      case 'low': return '#388e3c';
      default: return '#757575';
    }
  };

  const getRiskIcon = (rating: string) => {
    switch (rating) {
      case 'critical': return <ErrorIcon />;
      case 'high': return <WarningIcon />;
      case 'medium': return <InfoIcon />;
      case 'low': return <CheckCircleIcon />;
      default: return <InfoIcon />;
    }
  };

  const getRiskDescription = (rating: string) => {
    switch (rating) {
      case 'critical': return 'Immediate action required';
      case 'high': return 'High priority attention needed';
      case 'medium': return 'Monitor and plan action';
      case 'low': return 'Acceptable risk level';
      default: return 'Unknown risk level';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        
        <Grid container spacing={2}>
          {/* Critical Risks */}
          <Grid item xs={12} md={3}>
            <Paper 
              sx={{ 
                p: 2, 
                bgcolor: '#ffebee', 
                border: '2px solid #d32f2f',
                minHeight: 200,
                cursor: onRiskClick ? 'pointer' : 'default'
              }}
            >
              <Box display="flex" alignItems="center" mb={2}>
                <ErrorIcon sx={{ color: '#d32f2f', mr: 1 }} />
                <Typography variant="h6" color="error">
                  Critical ({riskGroups.critical.length})
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" mb={2}>
                {getRiskDescription('critical')}
              </Typography>
              {riskGroups.critical.map((risk) => (
                <Tooltip key={risk.id} title={risk.rationale}>
                  <Chip
                    label={risk.area_name}
                    size="small"
                    sx={{ 
                      m: 0.5, 
                      bgcolor: '#d32f2f', 
                      color: 'white',
                      cursor: onRiskClick ? 'pointer' : 'default'
                    }}
                    onClick={() => onRiskClick?.(risk)}
                  />
                </Tooltip>
              ))}
            </Paper>
          </Grid>

          {/* High Risks */}
          <Grid item xs={12} md={3}>
            <Paper 
              sx={{ 
                p: 2, 
                bgcolor: '#fff3e0', 
                border: '2px solid #f57c00',
                minHeight: 200,
                cursor: onRiskClick ? 'pointer' : 'default'
              }}
            >
              <Box display="flex" alignItems="center" mb={2}>
                <WarningIcon sx={{ color: '#f57c00', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#f57c00' }}>
                  High ({riskGroups.high.length})
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" mb={2}>
                {getRiskDescription('high')}
              </Typography>
              {riskGroups.high.map((risk) => (
                <Tooltip key={risk.id} title={risk.rationale}>
                  <Chip
                    label={risk.area_name}
                    size="small"
                    sx={{ 
                      m: 0.5, 
                      bgcolor: '#f57c00', 
                      color: 'white',
                      cursor: onRiskClick ? 'pointer' : 'default'
                    }}
                    onClick={() => onRiskClick?.(risk)}
                  />
                </Tooltip>
              ))}
            </Paper>
          </Grid>

          {/* Medium Risks */}
          <Grid item xs={12} md={3}>
            <Paper 
              sx={{ 
                p: 2, 
                bgcolor: '#fffde7', 
                border: '2px solid #fbc02d',
                minHeight: 200,
                cursor: onRiskClick ? 'pointer' : 'default'
              }}
            >
              <Box display="flex" alignItems="center" mb={2}>
                <InfoIcon sx={{ color: '#fbc02d', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#fbc02d' }}>
                  Medium ({riskGroups.medium.length})
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" mb={2}>
                {getRiskDescription('medium')}
              </Typography>
              {riskGroups.medium.map((risk) => (
                <Tooltip key={risk.id} title={risk.rationale}>
                  <Chip
                    label={risk.area_name}
                    size="small"
                    sx={{ 
                      m: 0.5, 
                      bgcolor: '#fbc02d', 
                      color: 'black',
                      cursor: onRiskClick ? 'pointer' : 'default'
                    }}
                    onClick={() => onRiskClick?.(risk)}
                  />
                </Tooltip>
              ))}
            </Paper>
          </Grid>

          {/* Low Risks */}
          <Grid item xs={12} md={3}>
            <Paper 
              sx={{ 
                p: 2, 
                bgcolor: '#e8f5e8', 
                border: '2px solid #388e3c',
                minHeight: 200,
                cursor: onRiskClick ? 'pointer' : 'default'
              }}
            >
              <Box display="flex" alignItems="center" mb={2}>
                <CheckCircleIcon sx={{ color: '#388e3c', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#388e3c' }}>
                  Low ({riskGroups.low.length})
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" mb={2}>
                {getRiskDescription('low')}
              </Typography>
              {riskGroups.low.map((risk) => (
                <Tooltip key={risk.id} title={risk.rationale}>
                  <Chip
                    label={risk.area_name}
                    size="small"
                    sx={{ 
                      m: 0.5, 
                      bgcolor: '#388e3c', 
                      color: 'white',
                      cursor: onRiskClick ? 'pointer' : 'default'
                    }}
                    onClick={() => onRiskClick?.(risk)}
                  />
                </Tooltip>
              ))}
            </Paper>
          </Grid>
        </Grid>

        {/* Risk Summary */}
        <Box mt={2}>
          <Typography variant="body2" color="textSecondary">
            Total Risks: {risks.length} | 
            Critical: {riskGroups.critical.length} | 
            High: {riskGroups.high.length} | 
            Medium: {riskGroups.medium.length} | 
            Low: {riskGroups.low.length}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default RiskMatrix;
