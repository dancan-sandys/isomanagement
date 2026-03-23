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
  Autocomplete,
  Radio,
  RadioGroup,
  CircularProgress,
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
  Close,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { hasPermission } from '../store/slices/authSlice';
import { fetchProducts } from '../store/slices/haccpSlice';
import { haccpAPI, traceabilityAPI } from '../services/api';
import { haccpAPI as haccpRecordsAPI } from '../services/haccpAPI';
import PageHeader from '../components/UI/PageHeader';
import HACCPBreadcrumbs from '../components/UI/HACCPBreadcrumbs';

interface CCPSVerificationTaskItem {
  task_type: 'ccp';
  id: string;
  log_id: number;
  ccp_id: number;
  ccp_number: string | null;
  ccp_name: string | null;
  product_id: number | null;
  product_name: string | null;
  batch_number: string | null;
  monitoring_time: string | null;
  measured_value: number | null;
  unit: string | null;
  is_within_limits: boolean | null;
  observations: string | null;
  created_at: string | null;
}

interface OPRPVerificationTaskItem {
  task_type: 'oprp';
  id: string;
  oprp_id: number;
  oprp_number: string;
  oprp_name: string;
  product_id: number;
  product_name: string | null;
  verification_frequency: string | null;
  description: string | null;
}

type VerificationTaskItem = CCPSVerificationTaskItem | OPRPVerificationTaskItem;

interface VerificationRecordItem {
  id: number;
  record_type: string;
  ccp_id: number | null;
  oprp_id: number | null;
  ccp_name: string | null;
  oprp_name: string | null;
  verified_at: string;
  verified_by: number;
  verifier_name: string | null;
  result?: string | null;
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
  const { user: currentUser } = useSelector((state: RootState) => state.auth);
  const canVerify = !!currentUser && (hasPermission(currentUser, 'haccp', 'verify') || hasPermission(currentUser, 'haccp', 'update') || hasPermission(currentUser, 'haccp', 'create'));
  const canViewRecords = !!currentUser && hasPermission(currentUser, 'haccp', 'view');

  const [selectedTab, setSelectedTab] = useState(0);
  const [verificationTasks, setVerificationTasks] = useState<VerificationTaskItem[]>([]);
  const [verificationRecords, setVerificationRecords] = useState<VerificationRecordItem[]>([]);
  const [recordsLoading, setRecordsLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [viewerRecordId, setViewerRecordId] = useState<number | null>(null);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);
  const [loadingViewer, setLoadingViewer] = useState(false);

  // CCP verify dialog: pending monitoring log to verify/reject
  const [ccpVerifyDialogOpen, setCcpVerifyDialogOpen] = useState(false);
  const [selectedCcpTask, setSelectedCcpTask] = useState<CCPSVerificationTaskItem | null>(null);
  const [ccpVerifyForm, setCcpVerifyForm] = useState({ verification_notes: '', allowOverride: false });

  // OPRP verify dialog: record OPRP verification (batch, conducted as expected, notes)
  const [oprpVerifyDialogOpen, setOprpVerifyDialogOpen] = useState(false);
  const [selectedOprpTask, setSelectedOprpTask] = useState<OPRPVerificationTaskItem | null>(null);
  const [oprpVerifyForm, setOprpVerifyForm] = useState({
    conductedAsExpected: true,
    notes: '',
  });
  const [oprpBatchValue, setOprpBatchValue] = useState<{ id: number; batch_number?: string } | null>(null);
  const [batchOptions, setBatchOptions] = useState<any[]>([]);
  const [batchSearch, setBatchSearch] = useState('');
  const [batchOpen, setBatchOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchProducts());
    loadVerificationTasks();
  }, [dispatch]);

  useEffect(() => {
    if (selectedTab === 1 && canViewRecords) loadVerificationRecords();
  }, [selectedTab, canViewRecords]);

  useEffect(() => {
    let active = true;
    if (!batchOpen) return () => { active = false; };
    const t = setTimeout(async () => {
      try {
        const params: any = { search: batchSearch, size: 10 };
        if (selectedOprpTask?.product_id) params.product_id = selectedOprpTask.product_id;
        const resp: any = await traceabilityAPI.getBatches(params);
        const items = resp?.data?.items || resp?.items || [];
        if (active) setBatchOptions(items);
      } catch (e) {
        if (active) setBatchOptions([]);
      }
    }, 250);
    return () => { active = false; clearTimeout(t); };
  }, [batchOpen, batchSearch, selectedOprpTask?.product_id]);

  const loadVerificationTasks = async () => {
    setLoading(true);
    try {
      const res: any = await haccpAPI.getVerificationTasks();
      const data = res?.data ?? res;
      const ccpTasks: CCPSVerificationTaskItem[] = (data.ccp_tasks ?? []).map((t: any) => ({
        task_type: 'ccp' as const,
        id: t.id,
        log_id: t.log_id,
        ccp_id: t.ccp_id,
        ccp_number: t.ccp_number ?? null,
        ccp_name: t.ccp_name ?? null,
        product_id: t.product_id ?? null,
        product_name: t.product_name ?? null,
        batch_number: t.batch_number ?? null,
        monitoring_time: t.monitoring_time ?? null,
        measured_value: t.measured_value ?? null,
        unit: t.unit ?? null,
        is_within_limits: t.is_within_limits ?? null,
        observations: t.observations ?? null,
        created_at: t.created_at ?? null,
      }));
      const oprpTasks: OPRPVerificationTaskItem[] = (data.oprp_tasks ?? []).map((t: any) => ({
        task_type: 'oprp' as const,
        id: t.id,
        oprp_id: t.oprp_id,
        oprp_number: t.oprp_number ?? '',
        oprp_name: t.oprp_name ?? '',
        product_id: t.product_id ?? 0,
        product_name: t.product_name ?? null,
        verification_frequency: t.verification_frequency ?? null,
        description: t.description ?? null,
      }));
      setVerificationTasks([...ccpTasks, ...oprpTasks]);
    } catch (error) {
      console.error('Error loading verification tasks:', error);
      setVerificationTasks([]);
    } finally {
      setLoading(false);
    }
  };

  const loadVerificationRecords = async () => {
    if (!canViewRecords) return;
    setRecordsLoading(true);
    try {
      const res: any = await haccpRecordsAPI.getVerificationRecords({ skip: 0, limit: 100 });
      const payload = res?.data ?? res;
      const items: VerificationRecordItem[] = payload?.items ?? [];
      setVerificationRecords(items);
    } catch (error) {
      console.error('Error loading verification records:', error);
      setVerificationRecords([]);
    } finally {
      setRecordsLoading(false);
    }
  };

  const handleOpenTask = (task: VerificationTaskItem) => {
    if (task.task_type === 'ccp') {
      setSelectedCcpTask(task);
      setCcpVerifyForm({ verification_notes: '', allowOverride: false });
      setCcpVerifyDialogOpen(true);
    } else {
      setSelectedOprpTask(task);
      setOprpVerifyForm({ conductedAsExpected: true, notes: '' });
      setOprpBatchValue(null);
      setBatchSearch('');
      setOprpVerifyDialogOpen(true);
    }
  };

  const handleSubmitCcpVerify = async (compliant: boolean) => {
    if (!selectedCcpTask) return;
    try {
      await haccpAPI.verifyMonitoringLog(
        selectedCcpTask.ccp_id,
        selectedCcpTask.log_id,
        {
          verification_is_compliant: compliant,
          verification_notes: ccpVerifyForm.verification_notes.trim() || undefined,
        },
        { allowOverride: ccpVerifyForm.allowOverride }
      );
      setCcpVerifyDialogOpen(false);
      setSelectedCcpTask(null);
      loadVerificationTasks();
      alert(compliant ? 'Log verified successfully.' : 'Log rejected.');
    } catch (e: any) {
      console.error('CCP verify failed', e);
      alert(e?.response?.data?.detail || 'Failed to submit verification');
    }
  };

  const handleSubmitOprpVerify = async () => {
    if (!selectedOprpTask) return;
    try {
      await haccpAPI.createOPRPVerificationLog(selectedOprpTask.oprp_id, {
        batch_id: oprpBatchValue?.id,
        verification_type: 'batch_check',
        conducted_as_expected: oprpVerifyForm.conductedAsExpected,
        findings: oprpVerifyForm.notes.trim() || undefined,
      });
      setOprpVerifyDialogOpen(false);
      setSelectedOprpTask(null);
      setOprpBatchValue(null);
      loadVerificationTasks();
      alert('OPRP verification recorded.');
    } catch (e: any) {
      console.error('OPRP verify failed', e);
      alert(e?.response?.data?.detail || 'Failed to record OPRP verification');
    }
  };

  const formatDateTime = (iso: string | null | undefined) =>
    iso ? new Date(iso).toLocaleString() : '—';

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

  const handleViewPdf = async (record: VerificationRecordItem) => {
    setLoadingViewer(true);
    setViewerRecordId(null);
    setViewerUrl(null);
    try {
      const blob = await haccpRecordsAPI.downloadVerificationRecordPdf(record.id);
      const url = window.URL.createObjectURL(blob);
      setViewerUrl(url);
      setViewerRecordId(record.id);
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Failed to load PDF');
    } finally {
      setLoadingViewer(false);
    }
  };

  const handleClosePdfViewer = () => {
    if (viewerUrl) window.URL.revokeObjectURL(viewerUrl);
    setViewerUrl(null);
    setViewerRecordId(null);
  };

  const ccpTasks = verificationTasks.filter((t): t is CCPSVerificationTaskItem => t.task_type === 'ccp');
  const oprpTasks = verificationTasks.filter((t): t is OPRPVerificationTaskItem => t.task_type === 'oprp');
  const totalPending = verificationTasks.length;

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
                    Total Pending
                  </Typography>
                  <Typography variant="h4">
                    {totalPending}
                  </Typography>
                </Box>
                <Badge badgeContent={totalPending} color="primary">
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
                    CCP (logs to verify)
                  </Typography>
                  <Typography variant="h4">
                    {ccpTasks.length}
                  </Typography>
                </Box>
                <Security color="info" />
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
                    OPRP verification
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {oprpTasks.length}
                  </Typography>
                </Box>
                <VerifiedUser color="success" />
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
                    Compliance
                  </Typography>
                  <Typography variant="h4" color="info.main">
                    {totalPending === 0 ? '100' : '0'}%
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
          label={`Tasks (${totalPending})`} 
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
            {verificationTasks.length === 0 ? (
              <Alert severity="success">
                No verification tasks. CCP monitoring logs that are not yet verified and OPRPs you are responsible for will appear here.
              </Alert>
            ) : (
              <List>
                {verificationTasks.map((task) => (
                  <ListItem
                    key={task.id}
                    divider
                    onClick={() => handleOpenTask(task)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <ListItemIcon>
                      {task.task_type === 'ccp' ? (
                        <Security color="primary" />
                      ) : (
                        <VerifiedUser color="secondary" />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primaryTypographyProps={{ component: 'div' }}
                      secondaryTypographyProps={{ component: 'div' }}
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                          <Chip
                            label={task.task_type === 'ccp' ? 'CCP' : 'OPRP'}
                            color={task.task_type === 'ccp' ? 'primary' : 'secondary'}
                            size="small"
                            variant="outlined"
                          />
                          <Typography variant="h6">
                            {task.task_type === 'ccp'
                              ? `${task.ccp_number || ''}: ${task.ccp_name || ''}`
                              : `${task.oprp_number}: ${task.oprp_name}`}
                          </Typography>
                          {task.task_type === 'ccp' && (
                            <Typography variant="body2" color="textSecondary">
                              Batch: {task.batch_number || '—'} • {task.measured_value ?? '—'} {task.unit ?? ''}
                            </Typography>
                          )}
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="body2" color="textSecondary">
                            Product: {task.task_type === 'ccp' ? task.product_name : task.product_name} •{' '}
                            {task.task_type === 'ccp'
                              ? `Recorded: ${formatDateTime(task.monitoring_time)}`
                              : task.verification_frequency ? `Frequency: ${task.verification_frequency}` : ''}
                          </Typography>
                        </Box>
                      }
                    />
                    {canVerify && (
                      <Button
                        variant="contained"
                        startIcon={<VerifiedUser />}
                        color="primary"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenTask(task);
                        }}
                        sx={{ ml: 2 }}
                      >
                        {task.task_type === 'ccp' ? 'Verify / Reject' : 'Record verification'}
                      </Button>
                    )}
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
              canViewRecords && (
                <Stack direction="row" spacing={1}>
                  <Button
                    variant="outlined"
                    startIcon={recordsLoading ? <CircularProgress size={18} /> : <Refresh />}
                    size="small"
                    onClick={loadVerificationRecords}
                    disabled={recordsLoading}
                  >
                    Refresh
                  </Button>
                </Stack>
              )
            }
          />
          <CardContent>
            {!canViewRecords ? (
              <Alert severity="info">You need HACCP view permission to see verification records.</Alert>
            ) : recordsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>CCP/OPRP</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Result</TableCell>
                      <TableCell>Verified By</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {verificationRecords.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
                          <Typography variant="body2" color="text.secondary">
                            No verification records. Records are created when a monitoring log or OPRP is verified.
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      verificationRecords.map((record) => (
                        <TableRow key={record.id}>
                          <TableCell>{record.verified_at ? new Date(record.verified_at).toLocaleDateString() : '—'}</TableCell>
                          <TableCell>{record.ccp_name ?? record.oprp_name ?? '—'}</TableCell>
                          <TableCell>{record.record_type ? record.record_type.toUpperCase() : '—'}</TableCell>
                          <TableCell>
                            {record.result ? (
                              <Chip 
                                size="small" 
                                color={getResultColor(record.result) as any}
                                label={record.result.toUpperCase()} 
                              />
                            ) : '—'}
                          </TableCell>
                          <TableCell>{record.verifier_name ?? `User ${record.verified_by}`}</TableCell>
                          <TableCell>
                            <IconButton
                              size="small"
                              onClick={() => handleViewPdf(record)}
                              disabled={loadingViewer}
                              title="View PDF"
                            >
                              {loadingViewer && viewerRecordId === record.id ? (
                                <CircularProgress size={20} />
                              ) : (
                                <Visibility />
                              )}
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
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

      {/* PDF Viewer for verification record */}
      <Dialog open={!!viewerUrl} onClose={handleClosePdfViewer} maxWidth="md" fullWidth PaperProps={{ sx: { height: '85vh' } }}>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6">
              {viewerRecordId != null
                ? (() => {
                    const rec = verificationRecords.find((r) => r.id === viewerRecordId);
                    return rec
                      ? `Verification record: ${rec.ccp_name ?? rec.oprp_name ?? rec.record_type}${rec.verified_at ? ` (${new Date(rec.verified_at).toLocaleString()})` : ''}`
                      : `Verification record #${viewerRecordId}`;
                  })()
                : 'Verification record'}
            </Typography>
            <IconButton onClick={handleClosePdfViewer} size="small">
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers sx={{ p: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {viewerUrl && (
            <iframe
              src={viewerUrl}
              style={{ width: '100%', height: '100%', minHeight: 480, border: 'none' }}
              title="Verification record PDF"
            />
          )}
        </DialogContent>
      </Dialog>

      {/* CCP Verify Dialog – verify or reject a monitoring log */}
      <Dialog open={ccpVerifyDialogOpen} onClose={() => { setCcpVerifyDialogOpen(false); setSelectedCcpTask(null); }} maxWidth="sm" fullWidth>
        <DialogTitle>Verify or Reject Monitoring Log</DialogTitle>
        <DialogContent dividers>
          {selectedCcpTask && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Monitoring snapshot</Typography>
                <Typography variant="body2">
                  {selectedCcpTask.batch_number || 'Batch N/A'} • {selectedCcpTask.measured_value ?? '—'} {selectedCcpTask.unit ?? ''}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Recorded: {formatDateTime(selectedCcpTask.monitoring_time)}
                </Typography>
                <Chip
                  size="small"
                  color={selectedCcpTask.is_within_limits ? 'success' : 'error'}
                  label={selectedCcpTask.is_within_limits ? 'In Spec' : 'Out of Spec'}
                  sx={{ mt: 1 }}
                />
              </Box>
              <TextField
                label="Note (optional)"
                value={ccpVerifyForm.verification_notes}
                onChange={(e) => setCcpVerifyForm(prev => ({ ...prev, verification_notes: e.target.value }))}
                fullWidth
                multiline
                rows={2}
                placeholder="e.g. reason for rejection or brief comment"
              />
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setCcpVerifyDialogOpen(false); setSelectedCcpTask(null); }}>Cancel</Button>
          <Button color="error" variant="outlined" onClick={() => handleSubmitCcpVerify(false)}>Reject</Button>
          <Button variant="contained" color="success" onClick={() => handleSubmitCcpVerify(true)}>Verify</Button>
        </DialogActions>
      </Dialog>

      {/* OPRP Verify Dialog – record OPRP verification */}
      <Dialog open={oprpVerifyDialogOpen} onClose={() => { setOprpVerifyDialogOpen(false); setSelectedOprpTask(null); }} maxWidth="sm" fullWidth>
        <DialogTitle>Record OPRP verification</DialogTitle>
        <DialogContent dividers>
          {selectedOprpTask && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {selectedOprpTask.oprp_number}: {selectedOprpTask.oprp_name} • Product: {selectedOprpTask.product_name ?? '—'}
              </Typography>
              <FormControl component="fieldset">
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                  OPRP conducted as expected?
                </Typography>
                <RadioGroup
                  row
                  value={oprpVerifyForm.conductedAsExpected ? 'yes' : 'no'}
                  onChange={(_, v) => setOprpVerifyForm(prev => ({ ...prev, conductedAsExpected: v === 'yes' }))}
                >
                  <FormControlLabel value="yes" control={<Radio size="small" />} label="Yes" />
                  <FormControlLabel value="no" control={<Radio size="small" />} label="No" />
                </RadioGroup>
              </FormControl>
              <Autocomplete
                options={batchOptions}
                open={batchOpen}
                onOpen={() => setBatchOpen(true)}
                onClose={() => setBatchOpen(false)}
                getOptionLabel={(b: any) => b?.batch_number ?? String(b?.id ?? '')}
                value={oprpBatchValue}
                onChange={(_, val: any) => setOprpBatchValue(val)}
                inputValue={batchSearch}
                onInputChange={(_, val) => setBatchSearch(val)}
                isOptionEqualToValue={(a: any, b: any) => a?.id === b?.id}
                renderInput={(params) => <TextField {...params} label="Batch (optional)" size="small" />}
              />
              <TextField
                size="small"
                label="Notes"
                value={oprpVerifyForm.notes}
                onChange={(e) => setOprpVerifyForm(prev => ({ ...prev, notes: e.target.value }))}
                placeholder="e.g. OPRP checked / findings"
                fullWidth
                multiline
                rows={2}
              />
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setOprpVerifyDialogOpen(false); setSelectedOprpTask(null); }}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmitOprpVerify}>Confirm verification</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HACCPVerification;