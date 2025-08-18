import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Skeleton,
  FormControl,
  InputLabel,
  Select,
  SelectChangeEvent,
  Chip
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  BarChart as BarChartIcon,
  Download as DownloadIcon,
  SwapHoriz as SwapHorizIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

import { dashboardService } from '../../../services/dashboardService';
import { KPIDefinition, KPIValue } from '../../../types/dashboard';

interface BarChartWidgetProps {
  config: {
    kpi_ids: number[];
    chart_orientation?: 'horizontal' | 'vertical';
    show_values?: boolean;
    title?: string;
    refresh_interval?: number;
    colors?: string[];
  };
  kpiDefinitions: KPIDefinition[];
  selectedDepartment?: number | null;
  isEditMode?: boolean;
}

const BarChartWidget: React.FC<BarChartWidgetProps> = ({
  config,
  kpiDefinitions,
  selectedDepartment,
  isEditMode = false
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartData, setChartData] = useState<any>(null);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [orientation, setOrientation] = useState<'horizontal' | 'vertical'>(
    config.chart_orientation || 'vertical'
  );

  // Default colors for bars
  const defaultColors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
  ];

  useEffect(() => {
    loadChartData();
  }, [config.kpi_ids, selectedDepartment, orientation]);

  useEffect(() => {
    // Auto-refresh if configured
    const refreshInterval = config.refresh_interval || 300000; // 5 minutes default
    
    if (refreshInterval > 0) {
      const interval = setInterval(loadChartData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [config.refresh_interval]);

  const loadChartData = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!config.kpi_ids || config.kpi_ids.length === 0) {
        throw new Error('No KPIs configured for this chart');
      }

      // Get KPI definitions for the configured KPIs
      const selectedKPIs = kpiDefinitions.filter(kpi => 
        config.kpi_ids.includes(kpi.id)
      );

      if (selectedKPIs.length === 0) {
        throw new Error('No valid KPIs found');
      }

      // Fetch latest KPI values
      const kpiValuesPromises = selectedKPIs.map(async kpi => {
        const values = await dashboardService.getKPITrendData(kpi.id, 1, selectedDepartment);
        return {
          kpi,
          value: values.length > 0 ? Number(values[0].value) : 0
        };
      });

      const kpiData = await Promise.all(kpiValuesPromises);

      // Prepare chart data
      const labels = kpiData.map(item => item.kpi.display_name);
      const values = kpiData.map(item => item.value);
      
      // Generate colors
      const backgroundColors = kpiData.map((item, index) => {
        if (config.colors && config.colors[index]) {
          return config.colors[index];
        }
        
        // Color based on target achievement
        if (item.kpi.target_value) {
          const achievement = item.value / Number(item.kpi.target_value);
          if (achievement >= 1) return '#4caf50'; // Green - target met
          if (achievement >= 0.8) return '#ff9800'; // Orange - close to target
          return '#f44336'; // Red - below target
        }
        
        return defaultColors[index % defaultColors.length];
      });

      const borderColors = backgroundColors.map(color => color.replace('0.8', '1'));

      setChartData({
        labels,
        datasets: [{
          label: 'Current Values',
          data: values,
          backgroundColor: backgroundColors,
          borderColor: borderColors,
          borderWidth: 1
        }]
      });

    } catch (err) {
      console.error('Error loading chart data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load chart data');
    } finally {
      setLoading(false);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const handleOrientationChange = (event: SelectChangeEvent<string>) => {
    setOrientation(event.target.value as 'horizontal' | 'vertical');
  };

  const handleToggleOrientation = () => {
    setOrientation(prev => prev === 'vertical' ? 'horizontal' : 'vertical');
    handleMenuClose();
  };

  const handleRefresh = () => {
    loadChartData();
    handleMenuClose();
  };

  const handleExportChart = () => {
    // Export chart as image
    const canvas = document.querySelector('canvas');
    if (canvas) {
      const url = canvas.toDataURL('image/png');
      const link = document.createElement('a');
      link.download = `${config.title || 'bar-chart'}_${new Date().toISOString().split('T')[0]}.png`;
      link.href = url;
      link.click();
    }
    handleMenuClose();
  };

  // Chart.js options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: orientation === 'horizontal' ? 'y' as const : 'x' as const,
    plugins: {
      title: {
        display: false
      },
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        callbacks: {
          label: (context: any) => {
            const kpi = kpiDefinitions.find(k => 
              config.kpi_ids.includes(k.id) && k.display_name === context.label
            );
            const unit = kpi?.unit || '';
            const value = context.parsed[orientation === 'horizontal' ? 'x' : 'y'];
            return `${context.label}: ${dashboardService.formatKPIValue(value, unit)}`;
          }
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        title: {
          display: true,
          text: orientation === 'vertical' ? 'KPIs' : 'Value'
        },
        grid: {
          display: true,
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: orientation === 'vertical' ? 'Value' : 'KPIs'
        },
        grid: {
          display: true,
          color: 'rgba(0, 0, 0, 0.1)'
        }
      }
    },
    elements: {
      bar: {
        borderRadius: 4
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
          <Skeleton variant="rectangular" width="100%" height={200} />
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
              Chart Error
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
            <BarChartIcon color="primary" />
            <Typography variant="h6">
              {config.title || 'KPI Comparison'}
            </Typography>
            <Chip 
              label={orientation}
              size="small" 
              color="primary" 
              variant="outlined" 
            />
          </Box>
        }
        action={
          <Box display="flex" alignItems="center" gap={1}>
            <FormControl size="small" sx={{ minWidth: 100 }}>
              <InputLabel>Layout</InputLabel>
              <Select
                value={orientation}
                onChange={handleOrientationChange}
                label="Layout"
                disabled={isEditMode}
              >
                <MenuItem value="vertical">Vertical</MenuItem>
                <MenuItem value="horizontal">Horizontal</MenuItem>
              </Select>
            </FormControl>
            
            <IconButton onClick={handleMenuOpen}>
              <MoreVertIcon />
            </IconButton>
          </Box>
        }
        sx={{ pb: 1 }}
      />
      
      <CardContent sx={{ pt: 0, height: 'calc(100% - 80px)' }}>
        {chartData && (
          <Box height="100%">
            <Bar data={chartData} options={chartOptions} />
          </Box>
        )}
      </CardContent>

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleToggleOrientation}>
          <SwapHorizIcon sx={{ mr: 1 }} />
          Toggle Orientation
        </MenuItem>
        <MenuItem onClick={handleRefresh}>
          <RefreshIcon sx={{ mr: 1 }} />
          Refresh Data
        </MenuItem>
        <MenuItem onClick={handleExportChart}>
          <DownloadIcon sx={{ mr: 1 }} />
          Export Chart
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
            Bar Chart Widget
          </Typography>
        </Box>
      )}
    </Card>
  );
};

export default BarChartWidget;