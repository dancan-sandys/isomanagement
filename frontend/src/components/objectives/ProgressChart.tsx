import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { objectivesService } from '../../services/objectivesService';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ProgressChartProps {
  objectiveId: number;
  height?: number;
}

interface ProgressData {
  id: number;
  objective_id: number;
  recorded_value: number;
  recorded_date: string;
  notes?: string;
  recorded_by: string;
  created_at: string;
}

const ProgressChart: React.FC<ProgressChartProps> = ({ objectiveId, height = 300 }) => {
  const [progressData, setProgressData] = useState<ProgressData[]>([]);
  const [objective, setObjective] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [objectiveId]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load objective details
      const objectiveResponse = await objectivesService.getObjective(objectiveId);
      setObjective(objectiveResponse.data);

      // Load progress data
      const progressResponse = await objectivesService.getObjectiveProgress(objectiveId);
      setProgressData(progressResponse.data || []);
    } catch (err) {
      setError('Failed to load progress data');
      console.error('Error loading progress data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height={height}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!objective) {
    return (
      <Alert severity="warning">
        Objective not found
      </Alert>
    );
  }

  // Prepare chart data
  const sortedProgress = [...progressData].sort((a, b) => 
    new Date(a.recorded_date).getTime() - new Date(b.recorded_date).getTime()
  );

  const chartData = {
    labels: sortedProgress.map(p => new Date(p.recorded_date).toLocaleDateString()),
    datasets: [
      {
        label: 'Actual Progress',
        data: sortedProgress.map(p => p.recorded_value),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
        fill: false,
      },
      {
        label: 'Target',
        data: sortedProgress.map(() => objective.target_value),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderDash: [5, 5],
        fill: false,
      },
      {
        label: 'Baseline',
        data: sortedProgress.map(() => objective.baseline_value || 0),
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderDash: [2, 2],
        fill: false,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `Progress: ${objective.title}`,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            return `${label}: ${value} ${objective.unit_of_measure || ''}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: objective.unit_of_measure || 'Value'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Date'
        }
      }
    }
  };

  // Calculate current progress percentage
  const currentValue = progressData.length > 0 
    ? progressData[progressData.length - 1].recorded_value 
    : objective.baseline_value || 0;
  
  const progressPercentage = Math.min((currentValue / objective.target_value) * 100, 100);
  
  // Determine progress status
  const getProgressStatus = () => {
    if (progressPercentage >= 100) return { color: 'success', text: 'Completed' };
    if (progressPercentage >= 75) return { color: 'success', text: 'On Track' };
    if (progressPercentage >= 50) return { color: 'warning', text: 'In Progress' };
    return { color: 'error', text: 'Behind Schedule' };
  };

  const status = getProgressStatus();

  return (
    <Box>
      {/* Progress Summary */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Current Value
              </Typography>
              <Typography variant="h4" component="div">
                {currentValue}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {objective.unit_of_measure}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Target Value
              </Typography>
              <Typography variant="h4" component="div">
                {objective.target_value}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {objective.unit_of_measure}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Progress
              </Typography>
              <Typography variant="h4" component="div">
                {Math.round(progressPercentage)}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={progressPercentage} 
                color={status.color as any}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Status
              </Typography>
              <Typography variant="h6" component="div" color={`${status.color}.main`}>
                {status.text}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {objective.performance_color}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Chart */}
      <Paper sx={{ p: 2, height }}>
        {progressData.length > 0 ? (
          <Line data={chartData} options={chartOptions} height={height - 100} />
        ) : (
          <Box 
            display="flex" 
            justifyContent="center" 
            alignItems="center" 
            height={height - 100}
            flexDirection="column"
          >
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No Progress Data Available
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Start recording progress to see the chart
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Recent Progress Entries */}
      {progressData.length > 0 && (
        <Paper sx={{ p: 2, mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Recent Progress Entries
          </Typography>
          <Box maxHeight={200} overflow="auto">
            {progressData.slice(-5).reverse().map((entry) => (
              <Box key={entry.id} sx={{ py: 1, borderBottom: '1px solid #eee' }}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">
                    {new Date(entry.recorded_date).toLocaleDateString()}
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {entry.recorded_value} {objective.unit_of_measure}
                  </Typography>
                </Box>
                {entry.notes && (
                  <Typography variant="caption" color="textSecondary">
                    {entry.notes}
                  </Typography>
                )}
                <Typography variant="caption" color="textSecondary">
                  Recorded by: {entry.recorded_by}
                </Typography>
              </Box>
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default ProgressChart;
