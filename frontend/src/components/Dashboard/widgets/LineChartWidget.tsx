import React, { useState, useEffect, useRef } from 'react';
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
  Chip,
  FormControl,
  InputLabel,
  Select,
  SelectChangeEvent
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  TrendingUp as TrendingUpIcon,
  Download as DownloadIcon,
  Fullscreen as FullscreenIcon,
  ZoomIn as ZoomInIcon
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  ChartOptions
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

import { dashboardService } from '../../../services/dashboardService';
import { KPIDefinition, KPIValue, DashboardStats } from '../../../types/dashboard';

interface LineChartWidgetProps {
  config: {
    kpi_ids: number[];
    period_days?: number;
    show_target_line?: boolean;
    title?: string;
    chart_type?: 'line' | 'area';
    refresh_interval?: number;
    colors?: string[];
  };
  dashboardStats?: DashboardStats | null;
  kpiDefinitions: KPIDefinition[];
  selectedDepartment?: number | null;
  isEditMode?: boolean;
}

interface ChartDataPoint {
  x: string;
  y: number;
}

interface ChartDataset {
  label: string;
  data: ChartDataPoint[];
  borderColor: string;
  backgroundColor: string;
  borderWidth: number;
  fill: boolean;
  tension: number;
  pointRadius: number;
  pointHoverRadius: number;
}

const LineChartWidget: React.FC<LineChartWidgetProps> = ({
  config,
  dashboardStats,
  kpiDefinitions,
  selectedDepartment,
  isEditMode = false
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartData, setChartData] = useState<any>(null);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<number>(config.period_days || 30);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const chartRef = useRef<ChartJS<"line", ChartDataPoint[], string>>(null);

  // Default colors for multiple KPIs
  const defaultColors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
  ];

  useEffect(() => {
    loadChartData();
  }, [config.kpi_ids, selectedDepartment, selectedPeriod]);

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

      // Calculate date range
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - selectedPeriod);

      // Fetch KPI values for all selected KPIs
      const kpiValuesPromises = selectedKPIs.map(kpi =>
        dashboardService.getKPITrendData(kpi.id, selectedPeriod, selectedDepartment)
      );

      const allKpiValues = await Promise.all(kpiValuesPromises);

      // Prepare chart datasets
      const datasets: ChartDataset[] = selectedKPIs.map((kpi, index) => {
        const values = allKpiValues[index];
        const color = (config.colors && config.colors[index]) || defaultColors[index % defaultColors.length];
        
        // Sort values by date
        const sortedValues = values.sort((a, b) => 
          new Date(a.period_end).getTime() - new Date(b.period_end).getTime()
        );

        const data: ChartDataPoint[] = sortedValues.map(value => ({
          x: value.period_end,
          y: Number(value.value)
        }));

        const dataset: ChartDataset = {
          label: kpi.display_name,
          data,
          borderColor: color,
          backgroundColor: config.chart_type === 'area' ? `${color}20` : 'transparent',
          borderWidth: 2,
          fill: config.chart_type === 'area',
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 6
        };

        return dataset;
      });

      // Add target lines if configured
      if (config.show_target_line) {
        selectedKPIs.forEach((kpi, index) => {
          if (kpi.target_value) {
            const targetColor = `${defaultColors[index % defaultColors.length]}80`;
            const firstValue = datasets[index].data[0];
            const lastValue = datasets[index].data[datasets[index].data.length - 1];
            
            if (firstValue && lastValue) {
              datasets.push({
                label: `${kpi.display_name} Target`,
                data: [
                  { x: firstValue.x, y: Number(kpi.target_value) },
                  { x: lastValue.x, y: Number(kpi.target_value) }
                ],
                borderColor: targetColor,
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [5, 5],
                fill: false,
                tension: 0,
                pointRadius: 0,
                pointHoverRadius: 0
              });
            }
          }
        });
      }

      setChartData({
        datasets
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

  const handlePeriodChange = (event: SelectChangeEvent<number>) => {
    setSelectedPeriod(Number(event.target.value));
  };

  const handleExportChart = async () => {
    if (chartRef.current) {
      const canvas = chartRef.current.canvas;
      const url = canvas.toDataURL('image/png');
      
      const link = document.createElement('a');
      link.download = `${config.title || 'chart'}_${new Date().toISOString().split('T')[0]}.png`;
      link.href = url;
      link.click();
    }
    handleMenuClose();
  };

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    handleMenuClose();
  };

  const handleZoomReset = () => {
    if (chartRef.current) {
      chartRef.current.resetZoom();
    }
    handleMenuClose();
  };

  // Chart.js options
  const chartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      title: {
        display: false
      },
      legend: {
        position: 'bottom' as const,
        labels: {
          usePointStyle: true,
          padding: 20
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        callbacks: {
          title: (context) => {
            return new Date(context[0].parsed.x).toLocaleDateString();
          },
          label: (context) => {
            const kpi = kpiDefinitions.find(k => k.display_name === context.dataset.label);
            const unit = kpi?.unit || '';
            return `${context.dataset.label}: ${dashboardService.formatKPIValue(context.parsed.y, unit)}`;
          }
        }
      }
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          displayFormats: {
            day: 'MMM dd',
            week: 'MMM dd',
            month: 'MMM yyyy'
          }
        },
        title: {
          display: true,
          text: 'Date'
        },
        grid: {
          display: true,
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'Value'
        },
        grid: {
          display: true,
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          callback: function(value) {
            // Format tick labels based on the first KPI's unit
            const firstKPI = kpiDefinitions.find(k => config.kpi_ids.includes(k.id));
            const unit = firstKPI?.unit || '';
            return dashboardService.formatKPIValue(Number(value), unit);
          }
        }
      }
    },
    elements: {
      point: {
        hoverRadius: 8
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
        position: isFullscreen ? 'fixed' : 'relative',
        top: isFullscreen ? 0 : 'auto',
        left: isFullscreen ? 0 : 'auto',
        right: isFullscreen ? 0 : 'auto',
        bottom: isFullscreen ? 0 : 'auto',
        zIndex: isFullscreen ? 9999 : 'auto',
        backgroundColor: 'white'
      }}
    >
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <TrendingUpIcon color="primary" />
            <Typography variant="h6">
              {config.title || 'KPI Trends'}
            </Typography>
            <Chip 
              label={`${selectedPeriod} days`}
              size="small" 
              color="primary" 
              variant="outlined" 
            />
          </Box>
        }
        action={
          <Box display="flex" alignItems="center" gap={1}>
            <FormControl size="small" sx={{ minWidth: 100 }}>
              <InputLabel>Period</InputLabel>
              <Select
                value={selectedPeriod}
                onChange={handlePeriodChange}
                label="Period"
                disabled={isEditMode}
              >
                <MenuItem value={7}>7 days</MenuItem>
                <MenuItem value={14}>14 days</MenuItem>
                <MenuItem value={30}>30 days</MenuItem>
                <MenuItem value={60}>60 days</MenuItem>
                <MenuItem value={90}>90 days</MenuItem>
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
            <Line 
              ref={chartRef}
              data={chartData} 
              options={chartOptions}
            />
          </Box>
        )}
      </CardContent>

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleExportChart}>
          <DownloadIcon sx={{ mr: 1 }} />
          Export Chart
        </MenuItem>
        <MenuItem onClick={handleZoomReset}>
          <ZoomInIcon sx={{ mr: 1 }} />
          Reset Zoom
        </MenuItem>
        <MenuItem onClick={handleFullscreen}>
          <FullscreenIcon sx={{ mr: 1 }} />
          {isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
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
            Line Chart Widget
          </Typography>
        </Box>
      )}

      {/* Fullscreen Close Button */}
      {isFullscreen && (
        <IconButton
          onClick={() => setIsFullscreen(false)}
          sx={{
            position: 'absolute',
            top: 16,
            right: 16,
            backgroundColor: 'white',
            '&:hover': {
              backgroundColor: 'grey.100'
            }
          }}
        >
          <FullscreenIcon />
        </IconButton>
      )}
    </Card>
  );
};

export default LineChartWidget;