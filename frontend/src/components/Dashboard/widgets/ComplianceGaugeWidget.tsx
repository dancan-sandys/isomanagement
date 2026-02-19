import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Skeleton,
  LinearProgress,
  Grid,
  Tooltip
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Speed as SpeedIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip as ChartTooltip,
  Legend
} from 'chart.js';

// Register Chart.js components
ChartJS.register(ArcElement, ChartTooltip, Legend);

import { dashboardService } from '../../../services/dashboardService';
import { ComplianceScoreBreakdown, DashboardStats } from '../../../types/dashboard';

interface ComplianceGaugeWidgetProps {
  config: {
    compliance_type: 'overall' | 'haccp' | 'prp';
    department_filter?: boolean;
    title?: string;
    show_breakdown?: boolean;
    refresh_interval?: number;
  };
  dashboardStats?: DashboardStats | null;
  complianceScore?: ComplianceScoreBreakdown | null;
  selectedDepartment?: number | null;
  isEditMode?: boolean;
}

interface ComplianceData {
  score: number;
  level: string;
  breakdown: { [key: string]: number };
  lastUpdated: string;
}

const ComplianceGaugeWidget: React.FC<ComplianceGaugeWidgetProps> = ({
  config,
  dashboardStats,
  complianceScore,
  selectedDepartment,
  isEditMode = false
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [complianceData, setComplianceData] = useState<ComplianceData | null>(null);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    loadComplianceData();
  }, [config.compliance_type, selectedDepartment, complianceScore]);

  useEffect(() => {
    // Auto-refresh if configured
    const refreshInterval = config.refresh_interval || 300000; // 5 minutes default
    
    if (refreshInterval > 0) {
      const interval = setInterval(loadComplianceData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [config.refresh_interval]);

  const loadComplianceData = async () => {
    try {
      setError(null);

      let score = 0;
      let breakdown: { [key: string]: number } = {};
      let lastUpdated = new Date().toISOString();

      if (config.compliance_type === 'overall' && complianceScore) {
        score = Number(complianceScore.overall_score);
        breakdown = Object.fromEntries(
          Object.entries(complianceScore.component_scores).map(([key, value]) => [
            key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
            Number(value)
          ])
        );
        lastUpdated = complianceScore.last_calculated;
      } else if (config.compliance_type === 'haccp') {
        // Calculate HACCP-specific compliance
        if (complianceScore?.component_scores?.haccp_compliance) {
          score = Number(complianceScore.component_scores.haccp_compliance);
          breakdown = {
            'CCP Monitoring': score * 0.4,
            'Hazard Analysis': score * 0.3,
            'Verification': score * 0.2,
            'Documentation': score * 0.1
          };
        }
      } else if (config.compliance_type === 'prp') {
        // Calculate PRP-specific compliance
        if (complianceScore?.component_scores?.prp_performance) {
          score = Number(complianceScore.component_scores.prp_performance);
          breakdown = {
            'Cleaning & Sanitation': score * 0.3,
            'Pest Control': score * 0.2,
            'Water Quality': score * 0.2,
            'Equipment Maintenance': score * 0.15,
            'Personnel Hygiene': score * 0.15
          };
        }
      }

      const level = getComplianceLevel(score);

      setComplianceData({
        score,
        level,
        breakdown,
        lastUpdated
      });

    } catch (err) {
      console.error('Error loading compliance data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load compliance data');
    }
  };

  const getComplianceLevel = (score: number): string => {
    if (score >= 95) return 'Excellent';
    if (score >= 85) return 'Good';
    if (score >= 75) return 'Acceptable';
    if (score >= 65) return 'Needs Improvement';
    return 'Critical';
  };

  const getComplianceColor = (score: number): string => {
    if (score >= 95) return '#4caf50'; // Green
    if (score >= 85) return '#8bc34a'; // Light Green
    if (score >= 75) return '#ffeb3b'; // Yellow
    if (score >= 65) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const getComplianceIcon = (level: string) => {
    switch (level) {
      case 'Excellent':
      case 'Good':
        return <CheckCircleIcon color="success" />;
      case 'Acceptable':
        return <WarningIcon color="warning" />;
      default:
        return <ErrorIcon color="error" />;
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const handleRefresh = () => {
    loadComplianceData();
    handleMenuClose();
  };

  const handleExport = () => {
    // Export compliance data as JSON
    if (complianceData) {
      const dataStr = JSON.stringify(complianceData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `compliance_${config.compliance_type}_${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      
      URL.revokeObjectURL(url);
    }
    handleMenuClose();
  };

  // Gauge chart data
  const gaugeData = complianceData ? {
    datasets: [{
      data: [complianceData.score, 100 - complianceData.score],
      backgroundColor: [
        getComplianceColor(complianceData.score),
        '#e0e0e0'
      ],
      borderWidth: 0,
      cutout: '75%',
      rotation: -90,
      circumference: 180
    }]
  } : null;

  const gaugeOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: false
      }
    }
  };

  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader
          title={<Skeleton variant="text" width="60%" />}
          action={<Skeleton variant="circular" width={40} height={40} />}
        />
        <CardContent>
          <Skeleton variant="circular" width={200} height={200} sx={{ mx: 'auto' }} />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader
          title={
            <Typography variant="h6" color="error">
              Compliance Error
            </Typography>
          }
        />
        <CardContent>
          <Typography color="error" variant="body2">
            {error}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card 
      sx={{ 
        height: '100%',
        border: isEditMode ? '2px dashed #ccc' : 'none',
        position: 'relative'
      }}
    >
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <SpeedIcon color="primary" />
            <Typography variant="h6">
              {config.title || `${config.compliance_type.toUpperCase()} Compliance`}
            </Typography>
          </Box>
        }
        action={
          <IconButton onClick={handleMenuOpen}>
            <MoreVertIcon />
          </IconButton>
        }
        sx={{ pb: 1 }}
      />
      
      <CardContent sx={{ pt: 0 }}>
        {complianceData && (
          <>
            {/* Gauge Chart */}
            <Box 
              display="flex" 
              justifyContent="center" 
              alignItems="center" 
              position="relative"
              height={200}
              mb={2}
            >
              {gaugeData && (
                <>
                  <Doughnut data={gaugeData} options={gaugeOptions} />
                  
                  {/* Center Score Display */}
                  <Box
                    position="absolute"
                    display="flex"
                    flexDirection="column"
                    alignItems="center"
                    justifyContent="center"
                    sx={{ top: '60%', transform: 'translateY(-50%)' }}
                  >
                    <Typography 
                      variant="h3" 
                      component="div"
                      sx={{ 
                        fontWeight: 700,
                        color: getComplianceColor(complianceData.score)
                      }}
                    >
                      {complianceData.score.toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Compliance Score
                    </Typography>
                  </Box>
                </>
              )}
            </Box>

            {/* Status Indicator */}
            <Box display="flex" justifyContent="center" alignItems="center" gap={1} mb={2}>
              {getComplianceIcon(complianceData.level)}
              <Chip
                label={complianceData.level}
                color={
                  complianceData.level === 'Excellent' || complianceData.level === 'Good' ? 'success' :
                  complianceData.level === 'Acceptable' ? 'warning' : 'error'
                }
                variant="outlined"
              />
            </Box>

            {/* Breakdown */}
            {config.show_breakdown && Object.keys(complianceData.breakdown).length > 0 && (
              <Box>
                <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
                  Component Breakdown
                </Typography>
                <Grid container spacing={1}>
                  {Object.entries(complianceData.breakdown).map(([component, score]) => (
                    <Grid item xs={12} key={component}>
                      <Box display="flex" alignItems="center" justifyContent="space-between" mb={0.5}>
                        <Typography variant="caption" color="textSecondary">
                          {component}
                        </Typography>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>
                          {score.toFixed(1)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={score}
                        sx={{
                          height: 4,
                          borderRadius: 2,
                          backgroundColor: 'grey.200',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: getComplianceColor(score),
                            borderRadius: 2
                          }
                        }}
                      />
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}

            {/* Last Updated */}
            <Box mt={2} textAlign="center">
              <Typography variant="caption" color="textSecondary">
                Last updated: {new Date(complianceData.lastUpdated).toLocaleString()}
              </Typography>
            </Box>
          </>
        )}
      </CardContent>

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleRefresh}>
          <RefreshIcon sx={{ mr: 1 }} />
          Refresh Data
        </MenuItem>
        <MenuItem onClick={handleExport}>
          <DownloadIcon sx={{ mr: 1 }} />
          Export Data
        </MenuItem>
      </Menu>

      {/* Edit Mode Overlay */}
      {isEditMode && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'move'
          }}
        >
          <Typography variant="caption" sx={{ 
            backgroundColor: 'white',
            padding: '4px 8px',
            borderRadius: 1,
            fontWeight: 600
          }}>
            Compliance Gauge Widget
          </Typography>
        </Box>
      )}
    </Card>
  );
};

export default ComplianceGaugeWidget;