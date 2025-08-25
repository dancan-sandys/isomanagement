import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Badge,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControlLabel,
  Checkbox,
  Divider,
} from '@mui/material';
import {
  Security,
  VerifiedUser,
  Assignment,
  CheckCircle,
  Error,
  Warning,
  Schedule,
  Refresh,
  Add,
  Visibility,
  ExpandMore,
  Download,
  Upload,
  Assessment,
  TrendingUp,
  NotificationImportant,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchProducts } from '../store/slices/haccpSlice';
import { haccpAPI } from '../services/api';
import PageHeader from '../components/UI/PageHeader';
import HACCPBreadcrumbs from '../components/UI/HACCPBreadcrumbs';

interface VerificationTask {
  id: string;
  ccpId: number;
  ccpName: string;
  ccpNumber: string;
  productName: string;
  productId: number;
  verificationType: 'calibration' | 'review' | 'testing' | 'audit' | 'validation';
  status: 'pending' | 'in_progress' | 'completed' | 'overdue' | 'failed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  dueDate: string;
  frequency: string;
  lastVerified?: string;
  responsible: string;
  description: string;
  requirements: string[];
  evidence?: string[];
}

interface VerificationRecord {
  id: string;
  taskId: string;
  verifiedBy: string;
  verificationDate: string;
  result: 'pass' | 'fail' | 'conditional';
  findings: string;
  correctiveActions?: string;
  evidence: string[];
  nextDueDate: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`verification-tabpanel-${index}`}
      aria-labelledby={`verification-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const HACCPVerification: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { products } = useSelector((state: RootState) => state.haccp);
  const { user } = useSelector((state: RootState) => state.auth);

  const [selectedTab, setSelectedTab] = useState(0);
  const [verificationTasks, setVerificationTasks] = useState<VerificationTask[]>([]);
  const [verificationRecords, setVerificationRecords] = useState<VerificationRecord[]>([]);
  const [selectedTask, setSelectedTask] = useState<VerificationTask | null>(null);
  const [verificationDialogOpen, setVerificationDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const [verificationForm, setVerificationForm] = useState({
    result: 'pass' as 'pass' | 'fail' | 'conditional',
    findings: '',
    correctiveActions: '',
    evidence: [] as string[],
    requirements: [] as { id: string; description: string; met: boolean }[],
  });

  useEffect(() => {
    dispatch(fetchProducts());
    loadVerificationTasks();
    loadVerificationRecords();
  }, [dispatch]);

  const loadVerificationTasks = async () => {
    setLoading(true);
    try {
      // Mock data - replace with actual API call
      const mockTasks: VerificationTask[] = [
        {
          id: '1',
          ccpId: 1,
          ccpName: 'Temperature Control',
          ccpNumber: 'CCP-1',
          productName: 'Chicken Breast',
          productId: 1,
          verificationType: 'calibration',
          status: 'pending',
          priority: 'high',
          dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days from now
          frequency: 'Monthly',
          responsible: user?.username || 'QA Manager',
          description: 'Calibration of temperature monitoring equipment',
          requirements: [
            'Equipment calibration against certified standard',
            'Documentation of calibration results',
            'Verification of accuracy within ±1°C',
            'Update calibration records'
          ],
        },
        {
          id: '2',
          ccpId: 2,
          ccpName: 'pH Control',
          ccpNumber: 'CCP-2',
          productName: 'Pickled Vegetables',
          productId: 2,
          verificationType: 'review',
          status: 'overdue',
          priority: 'critical',
          dueDate: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
          frequency: 'Weekly',
          responsible: user?.username || 'QA Specialist',
          description: 'Review of monitoring records and control measures',
          requirements: [
            'Review monitoring logs for completeness',
            'Verify corrective actions were appropriate',
            'Check trend analysis',
            'Confirm training records are current'
          ],
        },
        {
          id: '3',
          ccpId: 3,
          ccpName: 'Water Activity',
          ccpNumber: 'CCP-3',
          productName: 'Dried Fruits',
          productId: 3,
          verificationType: 'testing',
          status: 'in_progress',
          priority: 'medium',
          dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days from now
          frequency: 'Bi-weekly',
          responsible: user?.username || 'QA Manager',
          description: 'Independent testing of water activity measurements',
          requirements: [
            'Collect representative samples',
            'Test using calibrated aw meter',
            'Compare results with production data',
            'Document any deviations'
          ],
        },
      ];
      setVerificationTasks(mockTasks);
    } catch (error) {
      console.error('Error loading verification tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadVerificationRecords = async () => {
    try {
      // Mock data - replace with actual API call
      const mockRecords: VerificationRecord[] = [
        {
          id: '1',
          taskId: '1',
          verifiedBy: user?.username || 'QA Manager',
          verificationDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
          result: 'pass',
          findings: 'Temperature monitoring equipment calibrated successfully. All readings within acceptable range.',
          evidence: ['calibration_cert_001.pdf', 'verification_log_temp.xlsx'],
          nextDueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        },
        {
          id: '2',
          taskId: '2',
          verifiedBy: user?.username || 'QA Specialist',
          verificationDate: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
          result: 'conditional',
          findings: 'Monitoring records complete but noted 2 instances of delayed corrective actions.',
          correctiveActions: 'Training reminder sent to production staff on timely corrective action implementation.',
          evidence: ['monitoring_review_ph.pdf', 'training_record.pdf'],
          nextDueDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
        },
      ];
      setVerificationRecords(mockRecords);
    } catch (error) {
      console.error('Error loading verification records:', error);
    }
  };

  const handleStartVerification = (task: VerificationTask) => {
    setSelectedTask(task);
    setVerificationForm({
      result: 'pass',
      findings: '',
      correctiveActions: '',
      evidence: [],
      requirements: task.requirements.map((req, index) => ({
        id: `req_${index}`,
        description: req,
        met: false,
      })),
    });
    setVerificationDialogOpen(true);
  };

  const handleSubmitVerification = async () => {
    if (!selectedTask || !verificationForm.findings.trim()) {
      alert('Please enter verification findings');
      return;
    }

    try {
      const payload = {
        task_id: selectedTask.id,
        result: verificationForm.result,
        findings: verificationForm.findings,
        corrective_actions: verificationForm.correctiveActions,
        evidence: verificationForm.evidence,
        requirements_met: verificationForm.requirements.map(req => ({
          description: req.description,
          met: req.met,
        })),
      };

      // Submit verification record
      await haccpAPI.createVerificationRecord(selectedTask.ccpId, payload);

      // Update task status
      setVerificationTasks(prev => 
        prev.map(task => 
          task.id === selectedTask.id 
            ? { 
                ...task, 
                status: 'completed',
                lastVerified: new Date().toISOString()
              }
            : task
        )
      );

      // Add to records
      const newRecord: VerificationRecord = {
        id: Date.now().toString(),
        taskId: selectedTask.id,
        verifiedBy: user?.username || 'Current User',
        verificationDate: new Date().toISOString(),
        result: verificationForm.result,
        findings: verificationForm.findings,
        correctiveActions: verificationForm.correctiveActions,
        evidence: verificationForm.evidence,
        nextDueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days from now
      };
      setVerificationRecords(prev => [newRecord, ...prev]);

      setVerificationDialogOpen(false);
      setSelectedTask(null);
    } catch (error) {
      console.error('Error submitting verification:', error);
      alert('Failed to submit verification record');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Schedule color="info" />;
      case 'overdue':
        return <Warning color="error" />;
      case 'completed':
        return <CheckCircle color="success" />;
      case 'in_progress':
        return <VerifiedUser color="primary" />;
      case 'failed':
        return <Error color="error" />;
      default:
        return <Schedule />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'info';
      case 'overdue':
        return 'error';
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getResultColor = (result: string) => {
    switch (result) {
      case 'pass':
        return 'success';
      case 'fail':
        return 'error';
      case 'conditional':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getVerificationTypeIcon = (type: string) => {
    switch (type) {
      case 'calibration':
        return <Assessment />;
      case 'review':
        return <Visibility />;
      case 'testing':
        return <Security />;
      case 'audit':
        return <Assignment />;
      case 'validation':
        return <VerifiedUser />;
      default:
        return <Assignment />;
    }
  };

  const formatTimeRemaining = (dueDate: string) => {
    const now = new Date();
    const due = new Date(dueDate);
    const diffMs = due.getTime() - now.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      return `${Math.abs(diffDays)} days overdue`;
    } else if (diffDays === 0) {
      return 'Due today';
    } else {
      return `${diffDays} days remaining`;
    }
  };

  const pendingTasks = verificationTasks.filter(task => task.status === 'pending' || task.status === 'overdue' || task.status === 'in_progress');
  const completedTasks = verificationTasks.filter(task => task.status === 'completed');
  const overdueTasks = verificationTasks.filter(task => task.status === 'overdue');

  return (
    <Box sx={{ p: 3 }}>
      <HACCPBreadcrumbs />
      <PageHeader
        title="HACCP Verification Console"
        subtitle="Verification and validation of HACCP system effectiveness"
        showAdd={false}
      />

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Pending Tasks
                  </Typography>
                  <Typography variant="h4">
                    {pendingTasks.length}
                  </Typography>
                </Box>
                <Badge badgeContent={pendingTasks.length} color="primary">
                  <Assignment color="primary" />
                </Badge>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Overdue
                  </Typography>
                  <Typography variant="h4" color="error">
                    {overdueTasks.length}
                  </Typography>
                </Box>
                <Badge badgeContent={overdueTasks.length} color="error">
                  <NotificationImportant color="error" />
                </Badge>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Completed
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {completedTasks.length}
                  </Typography>
                </Box>
                <CheckCircle color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Compliance Rate
                  </Typography>
                  <Typography variant="h4" color="info.main">
                    {pendingTasks.length > 0 ? Math.round((completedTasks.length / (completedTasks.length + pendingTasks.length)) * 100) : 100}%
                  </Typography>
                </Box>
                <TrendingUp color="info" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Tabs value={selectedTab} onChange={(_, newValue) => setSelectedTab(newValue)} sx={{ mb: 3 }}>
        <Tab 
          icon={<Assignment />} 
          label={`Tasks (${pendingTasks.length})`} 
          iconPosition="start"
        />
        <Tab 
          icon={<Assessment />} 
          label="Records" 
          iconPosition="start"
        />
        <Tab 
          icon={<TrendingUp />} 
          label="Analytics" 
          iconPosition="start"
        />
      </Tabs>

      <TabPanel value={selectedTab} index={0}>
        {/* Verification Tasks */}
        <Card>
          <CardHeader
            title="Verification Tasks"
            action={
              <Stack direction="row" spacing={1}>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={loadVerificationTasks}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Stack>
            }
          />
          <CardContent>
            {pendingTasks.length === 0 ? (
              <Alert severity="success">
                No verification tasks pending. All systems are verified and up to date.
              </Alert>
            ) : (
              <List>
                {pendingTasks.map((task) => (
                  <ListItem key={task.id} divider>
                    <ListItemIcon>
                      {getVerificationTypeIcon(task.verificationType)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                          <Typography variant="h6">
                            {task.ccpNumber}: {task.ccpName}
                          </Typography>
                          <Chip
                            label={task.verificationType.toUpperCase()}
                            color="primary"
                            size="small"
                            variant="outlined"
                          />
                          <Chip
                            label={task.status.toUpperCase()}
                            color={getStatusColor(task.status) as any}
                            size="small"
                          />
                          <Chip
                            label={task.priority.toUpperCase()}
                            color={getPriorityColor(task.priority) as any}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="body2" color="textSecondary">
                            Product: {task.productName} • Frequency: {task.frequency}
                          </Typography>
                          <Typography variant="body2" color={task.status === 'overdue' ? 'error' : 'textSecondary'}>
                            {formatTimeRemaining(task.dueDate)} • Responsible: {task.responsible}
                          </Typography>
                          <Typography variant="body2" color="textSecondary" sx={{ mt: 0.5 }}>
                            {task.description}
                          </Typography>
                        </Box>
                      }
                    />
                    <Button
                      variant="contained"
                      startIcon={<VerifiedUser />}
                      color={task.status === 'overdue' ? 'error' : 'primary'}
                      onClick={() => handleStartVerification(task)}
                      sx={{ ml: 2 }}
                    >
                      Start Verification
                    </Button>
                  </ListItem>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={selectedTab} index={1}>
        {/* Verification Records */}
        <Card>
          <CardHeader 
            title="Verification Records"
            action={
              <Stack direction="row" spacing={1}>
                <Button
                  variant="outlined"
                  startIcon={<Download />}
                  size="small"
                >
                  Export
                </Button>
              </Stack>
            }
          />
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>CCP</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Result</TableCell>
                    <TableCell>Verified By</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {verificationRecords.map((record) => (
                    <TableRow key={record.id}>
                      <TableCell>{new Date(record.verificationDate).toLocaleDateString()}</TableCell>
                      <TableCell>
                        {verificationTasks.find(t => t.id === record.taskId)?.ccpNumber || 'N/A'}
                      </TableCell>
                      <TableCell>
                        {verificationTasks.find(t => t.id === record.taskId)?.verificationType || 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Chip 
                          size="small" 
                          color={getResultColor(record.result) as any}
                          label={record.result.toUpperCase()} 
                        />
                      </TableCell>
                      <TableCell>{record.verifiedBy}</TableCell>
                      <TableCell>
                        <IconButton size="small">
                          <Visibility />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={selectedTab} index={2}>
        {/* Verification Analytics */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Verification Compliance Trends" />
              <CardContent>
                <Alert severity="info">
                  Verification compliance analytics and trend charts would be displayed here.
                  This could include:
                  <ul>
                    <li>Monthly compliance rates</li>
                    <li>Time to completion trends</li>
                    <li>Failure rate analysis</li>
                    <li>Resource utilization</li>
                  </ul>
                </Alert>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Verification Effectiveness" />
              <CardContent>
                <Alert severity="info">
                  Verification effectiveness metrics would be displayed here, including:
                  <ul>
                    <li>System effectiveness scores</li>
                    <li>Issue detection rates</li>
                    <li>Corrective action effectiveness</li>
                    <li>Continuous improvement opportunities</li>
                  </ul>
                </Alert>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Verification Dialog */}
      <Dialog 
        open={verificationDialogOpen} 
        onClose={() => setVerificationDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Verify {selectedTask?.ccpNumber}: {selectedTask?.ccpName}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <strong>Verification Type:</strong> {selectedTask?.verificationType} • 
                  <strong> Frequency:</strong> {selectedTask?.frequency} • 
                  <strong> Responsible:</strong> {selectedTask?.responsible}
                </Typography>
              </Alert>
            </Grid>
            
            {/* Requirements Checklist */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>Requirements Checklist</Typography>
              {verificationForm.requirements.map((req, index) => (
                <FormControlLabel
                  key={req.id}
                  control={
                    <Checkbox
                      checked={req.met}
                      onChange={(e) => {
                        const updatedReqs = [...verificationForm.requirements];
                        updatedReqs[index].met = e.target.checked;
                        setVerificationForm(prev => ({ ...prev, requirements: updatedReqs }));
                      }}
                    />
                  }
                  label={req.description}
                  sx={{ display: 'block', mb: 1 }}
                />
              ))}
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>

            {/* Verification Result */}
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Verification Result</InputLabel>
                <Select
                  value={verificationForm.result}
                  onChange={(e) => setVerificationForm(prev => ({ ...prev, result: e.target.value as any }))}
                  label="Verification Result"
                >
                  <MenuItem value="pass">Pass</MenuItem>
                  <MenuItem value="conditional">Conditional Pass</MenuItem>
                  <MenuItem value="fail">Fail</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Findings */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Verification Findings"
                value={verificationForm.findings}
                onChange={(e) => setVerificationForm(prev => ({ ...prev, findings: e.target.value }))}
                placeholder="Document your verification findings, observations, and any issues identified..."
                required
              />
            </Grid>

            {/* Corrective Actions (if needed) */}
            {(verificationForm.result === 'fail' || verificationForm.result === 'conditional') && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Corrective Actions Required"
                  value={verificationForm.correctiveActions}
                  onChange={(e) => setVerificationForm(prev => ({ ...prev, correctiveActions: e.target.value }))}
                  placeholder="Detail the corrective actions required to address identified issues..."
                />
              </Grid>
            )}

            {/* Evidence Upload */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>Evidence and Documentation</Typography>
              <Stack direction="row" spacing={2} alignItems="center">
                <Button
                  variant="outlined"
                  startIcon={<Upload />}
                  onClick={() => {
                    // Simulate file upload
                    const fileName = `verification_evidence_${Date.now()}.pdf`;
                    setVerificationForm(prev => ({
                      ...prev,
                      evidence: [...prev.evidence, fileName]
                    }));
                  }}
                >
                  Upload Evidence
                </Button>
                <Typography variant="body2" color="textSecondary">
                  Upload calibration certificates, test results, photos, etc.
                </Typography>
              </Stack>
              {verificationForm.evidence.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  {verificationForm.evidence.map((file, index) => (
                    <Chip
                      key={index}
                      label={file}
                      onDelete={() => {
                        setVerificationForm(prev => ({
                          ...prev,
                          evidence: prev.evidence.filter((_, i) => i !== index)
                        }));
                      }}
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>
              )}
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVerificationDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleSubmitVerification}
            disabled={!verificationForm.findings.trim()}
            color={verificationForm.result === 'fail' ? 'error' : 'primary'}
          >
            Submit Verification
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HACCPVerification;