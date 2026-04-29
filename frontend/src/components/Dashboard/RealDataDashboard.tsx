import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  Stack,
  Chip,
  Button,
  LinearProgress,
  Alert,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Assessment,
  Security,
  CheckCircle,
  School,
  Business,
  TrendingUp,
  Download,
  Schedule,
} from '@mui/icons-material';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
} from 'recharts';
import { RootState } from '../../store';
import { dashboardAPI } from '../../services/api';
import { haccpAPI } from '../../services/haccpAPI';
import objectivesAPI from '../../services/objectivesAPI';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

interface ChartDataPoint {
  period?: string;
  department?: string;
  score?: string;
  name?: string;
  count: number;
  compliance?: number;
}

interface ChartData {
  data: ChartDataPoint[];
}

interface PieSlice {
  name: string;
  value: number;
}

interface KPIData {
  overallCompliance: number;
  documentControl: {
    compliance: number;
    totalDocuments: number;
    approvedDocuments: number;
  };
  haccp: {
    ccpCompliance: number;
    totalHazards: number;
    controlledHazards: number;
  };
  prp: {
    completion: number;
    totalChecklists: number;
    completedChecklists: number;
  };
  suppliers: {
    performance: number;
    totalSuppliers: number;
    avgScore: number;
  };
  training: {
    completion: number;
    totalUsers: number;
    trainedUsers: number;
  };
  nonConformance: {
    last30Days: number;
    openNC: number;
    openCAPA: number;
  };
  audits: {
    completion: number;
    totalAudits: number;
    completedAudits: number;
  };
}

const RealDataDashboard: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [loading, setLoading] = useState(true);
  const [kpiData, setKpiData] = useState<KPIData | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [ccpPieData, setCcpPieData] = useState<PieSlice[]>([]);
  const [oprpPieData, setOprpPieData] = useState<PieSlice[]>([]);
  const [objectivesPieData, setObjectivesPieData] = useState<PieSlice[]>([]);
  const [tasksPieData, setTasksPieData] = useState<PieSlice[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState('6m');
  const [selectedChart, setSelectedChart] = useState('nc_trend');

  useEffect(() => {
    loadDashboardData();
  }, [selectedPeriod, selectedChart]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [kpiResponse, chartResponse, statsResponse, haccpDashboardResponse, monitoringTasksResponse, verificationTasksResponse, objectivesResponse] = await Promise.all([
        dashboardAPI.getKPIs(),
        dashboardAPI.getChartData(selectedChart, selectedPeriod),
        dashboardAPI.getStats(),
        haccpAPI.getDashboard(),
        haccpAPI.getMonitoringTasks(),
        haccpAPI.getVerificationTasks(),
        objectivesAPI.listObjectives(),
      ]);

      if (kpiResponse?.data) {
        setKpiData(kpiResponse.data);
      }
      if (chartResponse?.data) {
        setChartData(chartResponse.data);
      }

      const statsData = statsResponse?.data || statsResponse || {};
      const haccpData = haccpDashboardResponse?.data || haccpDashboardResponse || {};
      const monitoringData = monitoringTasksResponse?.data || monitoringTasksResponse || {};
      const verificationData = verificationTasksResponse?.data || verificationTasksResponse || {};
      const objectivesData = objectivesResponse?.data || objectivesResponse || {};

      const monitoringSummary = monitoringData?.summary || {};
      const verificationSummary = verificationData?.summary || {};
      const objectivesItems = objectivesData?.items || objectivesData?.data?.items || objectivesData || [];
      const objectivesKpi = Array.isArray(statsData?.objectivesKPI) ? statsData.objectivesKPI : [];

      const totalCCPs = Number(haccpData?.total_ccps || 0);
      const activeCCPs = Number(haccpData?.active_ccps || 0);
      const outOfSpec = Number(haccpData?.out_of_spec_count || 0);
      const inactiveCCPs = Math.max(totalCCPs - activeCCPs, 0);

      const targetedObjectives = Array.isArray(objectivesItems)
        ? objectivesItems.filter((o: any) => o?.target_value !== null && o?.target_value !== undefined).length
        : 0;
      const totalObjectives = Array.isArray(objectivesItems) ? objectivesItems.length : 0;
      const nonTargetedObjectives = Math.max(totalObjectives - targetedObjectives, 0);
      const onTrackObjectives = objectivesKpi.filter((o: any) => ['on_track', 'achieved'].includes((o?.status || '').toLowerCase())).length;
      const offTrackObjectives = Math.max(objectivesKpi.length - onTrackObjectives, 0);

      setCcpPieData(
        [
          { name: 'Active CCPs', value: activeCCPs },
          { name: 'Inactive CCPs', value: inactiveCCPs },
          { name: 'Out-of-Spec Logs', value: outOfSpec },
        ].filter((s) => s.value > 0)
      );

      setOprpPieData(
        [
          { name: 'OPRP Tasks', value: Number(verificationSummary?.oprp_count || 0) },
          { name: 'CCP Verification Pending', value: Number(verificationSummary?.ccp_pending || 0) },
        ].filter((s) => s.value > 0)
      );

      setObjectivesPieData(
        [
          { name: 'Targeted Objectives', value: targetedObjectives },
          { name: 'Not Targeted', value: nonTargetedObjectives },
          { name: 'On Track (Latest KPI)', value: onTrackObjectives },
          { name: 'At Risk / Off Track', value: offTrackObjectives },
        ].filter((s) => s.value > 0)
      );

      setTasksPieData(
        [
          { name: 'Monitoring Due', value: Number(monitoringSummary?.due_count || 0) },
          { name: 'Monitoring Overdue', value: Number(monitoringSummary?.overdue_count || 0) },
          { name: 'Monitoring Completed', value: Number(monitoringSummary?.completed_count || 0) },
          { name: 'Verification Pending', value: Number(verificationSummary?.total || 0) },
        ].filter((s) => s.value > 0)
      );
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderPieCard = (title: string, data: PieSlice[]) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" mb={2}>{title}</Typography>
        {data.length === 0 ? (
          <Typography variant="body2" color="text.secondary">No data available</Typography>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                outerRadius={85}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {data.map((entry, index) => (
                  <Cell key={`${title}-${entry.name}-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <RechartsTooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );

  const renderKPICard = (title: string, value: number, subtitle: string, icon: React.ReactNode, color: string) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" color="text.secondary">
            {title}
          </Typography>
          <Box sx={{ color }}>
            {icon}
          </Box>
        </Stack>
        <Typography variant="h4" component="div" sx={{ mb: 1 }}>
          {typeof value === 'number' && title.includes('%') ? `${value}%` : value}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      </CardContent>
    </Card>
  );

  const renderChart = () => {
    if (!chartData?.data) return null;

    switch (selectedChart) {
      case 'nc_trend':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#8884d8" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'compliance_by_department':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="department" />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Bar dataKey="compliance" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'supplier_performance':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="supplier" />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Bar dataKey="score" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'document_status':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData.data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {chartData.data.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <RechartsTooltip />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <LinearProgress sx={{ width: '50%' }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          FSMS Dashboard - Real Data
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button variant="outlined" startIcon={<Download />}>
            Export
          </Button>
          <Button variant="outlined" startIcon={<Schedule />}>
            Schedule Report
          </Button>
        </Stack>
      </Stack>

      {/* KPI Cards */}
      {kpiData && (
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} sm={6} md={3}>
            {renderKPICard(
              'Overall Compliance',
              kpiData.overallCompliance,
              'FSMS Compliance Score',
              <Assessment />,
              '#1976d2'
            )}
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            {renderKPICard(
              'CCP Compliance',
              kpiData.haccp.ccpCompliance,
              `${kpiData.haccp.controlledHazards}/${kpiData.haccp.totalHazards} Hazards Controlled`,
              <Security />,
              '#2e7d32'
            )}
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            {renderKPICard(
              'PRP Completion',
              kpiData.prp.completion,
              `${kpiData.prp.completedChecklists}/${kpiData.prp.totalChecklists} Checklists`,
              <CheckCircle />,
              '#ed6c02'
            )}
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            {renderKPICard(
              'Training Completion',
              kpiData.training.completion,
              `${kpiData.training.trainedUsers}/${kpiData.training.totalUsers} Users Trained`,
              <School />,
              '#9c27b0'
            )}
          </Grid>
        </Grid>
      )}

      {/* Core Operational Pie Charts */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={6}>
          {renderPieCard('CCP Status', ccpPieData)}
        </Grid>
        <Grid item xs={12} md={6}>
          {renderPieCard('OPRP / Verification Workload', oprpPieData)}
        </Grid>
        <Grid item xs={12} md={6}>
          {renderPieCard('Objectives Targeting & Status', objectivesPieData)}
        </Grid>
        <Grid item xs={12} md={6}>
          {renderPieCard('Tasks Overview', tasksPieData)}
        </Grid>
      </Grid>

      {/* Chart Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" spacing={2} alignItems="center">
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Chart Type</InputLabel>
              <Select
                value={selectedChart}
                label="Chart Type"
                onChange={(e) => setSelectedChart(e.target.value)}
              >
                <MenuItem value="nc_trend">NC Trend</MenuItem>
                <MenuItem value="compliance_by_department">Compliance by Department</MenuItem>
                <MenuItem value="supplier_performance">Supplier Performance</MenuItem>
                <MenuItem value="document_status">Document Status</MenuItem>
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Period</InputLabel>
              <Select
                value={selectedPeriod}
                label="Period"
                onChange={(e) => setSelectedPeriod(e.target.value)}
              >
                <MenuItem value="1m">1 Month</MenuItem>
                <MenuItem value="3m">3 Months</MenuItem>
                <MenuItem value="6m">6 Months</MenuItem>
                <MenuItem value="1y">1 Year</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </CardContent>
      </Card>

      {/* Chart */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" mb={2}>
            {selectedChart.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </Typography>
          {renderChart()}
        </CardContent>
      </Card>

      {/* Additional Metrics */}
      {kpiData && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" mb={2}>
                  Non-Conformance Summary
                </Typography>
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Last 30 Days
                    </Typography>
                    <Typography variant="h6">
                      {kpiData.nonConformance.last30Days}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Open NC/CAPA
                    </Typography>
                    <Typography variant="h6">
                      {kpiData.nonConformance.openNC} / {kpiData.nonConformance.openCAPA}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" mb={2}>
                  Supplier Performance
                </Typography>
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Average Score
                    </Typography>
                    <Typography variant="h6">
                      {kpiData.suppliers.performance}%
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Total Suppliers
                    </Typography>
                    <Typography variant="h6">
                      {kpiData.suppliers.totalSuppliers}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default RealDataDashboard;
