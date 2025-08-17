import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Grid,
  Chip,
  Divider,
  LinearProgress,
  Tooltip,
  IconButton,
  Collapse,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  alpha,
  useMediaQuery,
  useTheme,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Snackbar,
  Slide
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  VerifiedUser as VerifiedUserIcon,
  QrCode as QrCodeIcon,
  Business as BusinessIcon,
  LocalShipping as LocalShippingIcon,
  Inventory as InventoryIcon,
  Save as SaveIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
  Keyboard as KeyboardIcon
} from '@mui/icons-material';
import { traceabilityAPI } from '../../services/traceabilityAPI';

interface OneClickTraceabilityProps {
  batchId: number;
  batchNumber?: string;
  productName?: string;
  onComplete?: (results: any) => void;
}

interface TraceabilityResults {
  oneUpOneBack: any;
  completeness: any;
  verificationStatus: any;
  ccpAlerts: any[];
  haccpCompliance: any;
}

interface TraceNode {
  id: number;
  batch_number: string;
  product_name: string;
  batch_type: string;
  status: string;
  quantity: number;
  unit: string;
  production_date: string;
  link_type?: string;
  process_step?: string;
}

const OneClickTraceability: React.FC<OneClickTraceabilityProps> = ({
  batchId,
  batchNumber,
  productName,
  onComplete
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'lg'));
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<TraceabilityResults | null>(null);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [autoSaveStatus, setAutoSaveStatus] = useState<string>('');
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false);
  const [undoStack, setUndoStack] = useState<any[]>([]);
  const [redoStack, setRedoStack] = useState<any[]>([]);

  // Auto-save functionality
  useEffect(() => {
    if (results) {
      const autoSave = setTimeout(() => {
        setAutoSaveStatus('Auto-saving...');
        // Simulate auto-save
        setTimeout(() => {
          setAutoSaveStatus('Auto-saved');
          setTimeout(() => setAutoSaveStatus(''), 2000);
        }, 1000);
      }, 2000);
      
      return () => clearTimeout(autoSave);
    }
  }, [results]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 's':
            event.preventDefault();
            handleSave();
            break;
          case 'z':
            event.preventDefault();
            if (event.shiftKey) {
              handleRedo();
            } else {
              handleUndo();
            }
            break;
          case 'r':
            event.preventDefault();
            handleOneClickTrace();
            break;
          case 'h':
            event.preventDefault();
            setShowKeyboardShortcuts(!showKeyboardShortcuts);
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [results, undoStack, redoStack]);

  const handleSave = () => {
    if (results) {
      setAutoSaveStatus('Saving...');
      // Simulate save operation
      setTimeout(() => {
        setAutoSaveStatus('Saved');
        setTimeout(() => setAutoSaveStatus(''), 2000);
      }, 1000);
    }
  };

  const handleUndo = () => {
    if (undoStack.length > 0) {
      const lastState = undoStack[undoStack.length - 1];
      setRedoStack([...redoStack, results]);
      setResults(lastState);
      setUndoStack(undoStack.slice(0, -1));
    }
  };

  const handleRedo = () => {
    if (redoStack.length > 0) {
      const lastState = redoStack[redoStack.length - 1];
      setUndoStack([...undoStack, results]);
      setResults(lastState);
      setRedoStack(redoStack.slice(0, -1));
    }
  };

  const handleOneClickTrace = async () => {
    setLoading(true);
    setError(null);
    
    // Save current state for undo
    if (results) {
      setUndoStack([...undoStack, results]);
      setRedoStack([]);
    }
    
    setResults(null);

    try {
      // Execute all traceability analyses in parallel
      const [
        oneUpOneBackResponse,
        completenessResponse,
        verificationResponse,
        ccpAlertsResponse
      ] = await Promise.all([
        traceabilityAPI.getOneUpOneBackTrace(batchId),
        traceabilityAPI.getTraceCompleteness(batchId),
        traceabilityAPI.getTraceVerificationStatus(batchId),
        traceabilityAPI.getCCPTraceabilityAlerts()
      ]);

      const traceResults: TraceabilityResults = {
        oneUpOneBack: oneUpOneBackResponse.data,
        completeness: completenessResponse.data,
        verificationStatus: verificationResponse.data,
        ccpAlerts: ccpAlertsResponse.data?.items || [],
        haccpCompliance: null // Will be generated on demand
      };

      setResults(traceResults);
      onComplete?.(traceResults);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to perform traceability analysis');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'verified':
      case 'passed':
        return 'success';
      case 'pending':
      case 'in_progress':
        return 'warning';
      case 'failed':
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getCompletenessColor = (score: number) => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const renderTraceNode = (node: TraceNode, direction: 'upstream' | 'downstream') => {
    return (
      <Card key={node.id} sx={{ mb: 1, border: '1px solid', borderColor: 'divider' }}>
        <CardContent sx={{ py: 1.5, px: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" fontWeight={600}>
                {node.batch_number}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {node.product_name}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Chip
                label={node.batch_type?.replace('_', ' ')}
                size="small"
                variant="outlined"
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="body2">
                  {node.quantity} {node.unit}
                </Typography>
                <Chip
                  label={node.status?.replace('_', ' ')}
                  size="small"
                  color={getStatusColor(node.status) as any}
                />
              </Box>
            </Grid>
          </Grid>
          {node.link_type && (
            <Box mt={1}>
              <Typography variant="caption" color="text.secondary">
                Link: {node.link_type} • Process: {node.process_step}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  const renderCompletenessScore = (completeness: any) => {
    const score = completeness?.completeness_score || 0;
    const color = getCompletenessColor(score);
    
    return (
      <Box>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Typography variant="h4" fontWeight={700} color={`${color}.main`}>
            {score}%
          </Typography>
          <Box flex={1}>
            <LinearProgress
              variant="determinate"
              value={score}
              color={color as any}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        </Box>
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">
              Upstream Completeness
            </Typography>
            <Typography variant="h6" fontWeight={600}>
              {completeness?.upstream_completeness || 0}%
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">
              Downstream Completeness
            </Typography>
            <Typography variant="h6" fontWeight={600}>
              {completeness?.downstream_completeness || 0}%
            </Typography>
          </Grid>
        </Grid>
        
        {completeness?.missing_links && completeness.missing_links.length > 0 && (
          <Box mt={2}>
            <Typography variant="subtitle2" color="warning.main" mb={1}>
              Missing Links:
            </Typography>
            <List dense>
              {completeness.missing_links.map((link: string, index: number) => (
                <ListItem key={index} sx={{ py: 0.5 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <WarningIcon color="warning" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText primary={link} />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </Box>
    );
  };

  const renderVerificationStatus = (verification: any) => {
    const status = verification?.verification_status || 'pending';
    const color = getStatusColor(status);
    
    return (
      <Box>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Chip
            icon={status === 'verified' ? <VerifiedUserIcon /> : <SecurityIcon />}
            label={status?.replace('_', ' ').toUpperCase()}
            color={color as any}
            size="medium"
          />
          <Typography variant="body2" color="text.secondary">
            Last verified: {verification?.last_verified_date || 'Never'}
          </Typography>
        </Box>
        
        {verification?.verification_details && (
          <List dense>
            {verification.verification_details.map((detail: any, index: number) => (
              <ListItem key={index} sx={{ py: 0.5 }}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  {detail.verified ? (
                    <CheckCircleIcon color="success" fontSize="small" />
                  ) : (
                    <ErrorIcon color="error" fontSize="small" />
                  )}
                </ListItemIcon>
                <ListItemText 
                  primary={detail.check_name}
                  secondary={detail.description}
                />
              </ListItem>
            ))}
          </List>
        )}
      </Box>
    );
  };

  const renderCCPAlerts = (alerts: any[]) => {
    if (!alerts || alerts.length === 0) {
      return (
        <Box textAlign="center" py={3}>
          <CheckCircleIcon color="success" sx={{ fontSize: 48, mb: 2 }} />
          <Typography variant="h6" color="success.main">
            No CCP Alerts
          </Typography>
          <Typography variant="body2" color="text.secondary">
            All critical control points are properly monitored
          </Typography>
        </Box>
      );
    }

    return (
      <List>
        {alerts.map((alert, index) => (
          <ListItem key={index} sx={{ border: '1px solid', borderColor: 'divider', mb: 1, borderRadius: 1 }}>
            <ListItemIcon>
              <WarningIcon color="warning" />
            </ListItemIcon>
            <ListItemText
              primary={alert.alert_type}
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    {alert.description}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Detected: {alert.detected_at}
                  </Typography>
                </Box>
              }
            />
            <Chip
              label={alert.severity}
              color={alert.severity === 'high' ? 'error' : 'warning'}
              size="small"
            />
          </ListItem>
        ))}
      </List>
    );
  };

  return (
    <Card sx={{ 
      width: '100%',
      borderRadius: { xs: 1, sm: 2 },
      boxShadow: { xs: 1, sm: 2 }
    }}>
      <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
        {/* Auto-save status */}
        {autoSaveStatus && (
          <Snackbar
            open={!!autoSaveStatus}
            message={autoSaveStatus}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            TransitionComponent={Slide}
            sx={{ mt: { xs: 7, sm: 0 } }}
          />
        )}

        {/* Keyboard shortcuts help */}
        {showKeyboardShortcuts && (
          <Alert 
            severity="info" 
            onClose={() => setShowKeyboardShortcuts(false)}
            sx={{ mb: 2 }}
          >
            <Typography variant="subtitle2" gutterBottom>Keyboard Shortcuts:</Typography>
            <Typography variant="body2" component="div">
              • Ctrl+S: Save • Ctrl+Z: Undo • Ctrl+Shift+Z: Redo • Ctrl+R: Refresh • Ctrl+H: Help
            </Typography>
          </Alert>
        )}

        <Box 
          display="flex" 
          flexDirection={{ xs: 'column', sm: 'row' }}
          alignItems={{ xs: 'flex-start', sm: 'center' }} 
          gap={2} 
          mb={3}
        >
          <TimelineIcon 
            color="primary" 
            sx={{ 
              fontSize: { xs: 24, sm: 32 },
              flexShrink: 0
            }} 
            aria-hidden="true"
          />
          <Box flex={1}>
            <Typography 
              variant="h5" 
              fontWeight={600}
              sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem' } }}
            >
              One-Click Traceability Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {batchNumber && productName ? `${batchNumber} - ${productName}` : `Batch ID: ${batchId}`}
            </Typography>
          </Box>
          
          {/* Quick action buttons */}
          <Box 
            display="flex" 
            gap={1}
            sx={{ 
              flexDirection: { xs: 'row', sm: 'row' },
              width: { xs: '100%', sm: 'auto' },
              justifyContent: { xs: 'space-between', sm: 'flex-end' }
            }}
          >
            <Tooltip title="Save (Ctrl+S)" arrow>
              <IconButton
                onClick={handleSave}
                disabled={!results}
                aria-label="Save traceability results"
                size={isMobile ? "medium" : "small"}
              >
                <SaveIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Undo (Ctrl+Z)" arrow>
              <IconButton
                onClick={handleUndo}
                disabled={undoStack.length === 0}
                aria-label="Undo last action"
                size={isMobile ? "medium" : "small"}
              >
                <UndoIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Redo (Ctrl+Shift+Z)" arrow>
              <IconButton
                onClick={handleRedo}
                disabled={redoStack.length === 0}
                aria-label="Redo last action"
                size={isMobile ? "medium" : "small"}
              >
                <RedoIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Keyboard shortcuts (Ctrl+H)" arrow>
              <IconButton
                onClick={() => setShowKeyboardShortcuts(!showKeyboardShortcuts)}
                aria-label="Show keyboard shortcuts"
                size={isMobile ? "medium" : "small"}
              >
                <KeyboardIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {!results && !loading && (
          <Box 
            textAlign="center" 
            py={{ xs: 3, sm: 4 }}
            px={{ xs: 1, sm: 2 }}
          >
            <TimelineIcon 
              sx={{ 
                fontSize: { xs: 48, sm: 64 }, 
                color: 'primary.main', 
                mb: 2 
              }} 
              aria-hidden="true"
            />
            <Typography 
              variant="h6" 
              mb={2}
              sx={{ fontSize: { xs: '1.1rem', sm: '1.25rem' } }}
            >
              Ready for Traceability Analysis
            </Typography>
            <Typography 
              variant="body2" 
              color="text.secondary" 
              mb={3}
              sx={{ 
                fontSize: { xs: '0.875rem', sm: '1rem' },
                lineHeight: 1.5
              }}
            >
              Click the button below to perform comprehensive traceability analysis including
              one-up-one-back tracing, completeness scoring, verification status, and CCP alerts.
            </Typography>
            <Button
              variant="contained"
              size={isMobile ? "large" : "large"}
              startIcon={<TimelineIcon />}
              onClick={handleOneClickTrace}
              sx={{ 
                px: { xs: 3, sm: 4 }, 
                py: { xs: 1.5, sm: 1.5 },
                minHeight: { xs: 48, sm: 56 },
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }}
              aria-label="Start traceability analysis"
            >
              Start Traceability Analysis
            </Button>
          </Box>
        )}

        {loading && (
          <Box textAlign="center" py={4}>
            <CircularProgress size={48} sx={{ mb: 2 }} />
            <Typography variant="h6" mb={1}>
              Analyzing Traceability...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Gathering comprehensive traceability data
            </Typography>
          </Box>
        )}

        {results && (
          <Box>
            <Box 
              display="flex" 
              flexDirection={{ xs: 'column', sm: 'row' }}
              alignItems={{ xs: 'flex-start', sm: 'center' }} 
              gap={2} 
              mb={3}
            >
              <Box display="flex" alignItems="center" gap={2} flex={1}>
                <CheckCircleIcon 
                  color="success" 
                  sx={{ 
                    fontSize: { xs: 20, sm: 24 } 
                  }} 
                  aria-hidden="true"
                />
                <Typography 
                  variant="h6" 
                  fontWeight={600}
                  sx={{ fontSize: { xs: '1.1rem', sm: '1.25rem' } }}
                >
                  Analysis Complete
                </Typography>
              </Box>
              <Button
                variant="outlined"
                size={isMobile ? "medium" : "small"}
                startIcon={<RefreshIcon />}
                onClick={handleOneClickTrace}
                aria-label="Refresh traceability analysis"
                sx={{ 
                  minWidth: { xs: '100%', sm: 'auto' },
                  height: { xs: 48, sm: 40 }
                }}
              >
                Refresh
              </Button>
            </Box>

            {/* Trace Completeness */}
            <Accordion
              expanded={expandedSection === 'completeness'}
              onChange={() => setExpandedSection(expandedSection === 'completeness' ? null : 'completeness')}
              sx={{ mb: 2 }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box display="flex" alignItems="center" gap={2}>
                  <TrendingUpIcon color="primary" />
                  <Typography variant="h6">Trace Completeness</Typography>
                  <Chip
                    label={`${results.completeness?.completeness_score || 0}%`}
                    color={getCompletenessColor(results.completeness?.completeness_score || 0) as any}
                    size="small"
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                {renderCompletenessScore(results.completeness)}
              </AccordionDetails>
            </Accordion>

            {/* Verification Status */}
            <Accordion
              expanded={expandedSection === 'verification'}
              onChange={() => setExpandedSection(expandedSection === 'verification' ? null : 'verification')}
              sx={{ mb: 2 }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box display="flex" alignItems="center" gap={2}>
                  <VerifiedUserIcon color="primary" />
                  <Typography variant="h6">Verification Status</Typography>
                  <Chip
                    label={results.verificationStatus?.verification_status || 'pending'}
                    color={getStatusColor(results.verificationStatus?.verification_status) as any}
                    size="small"
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                {renderVerificationStatus(results.verificationStatus)}
              </AccordionDetails>
            </Accordion>

            {/* One-Up, One-Back Trace */}
            <Accordion
              expanded={expandedSection === 'trace'}
              onChange={() => setExpandedSection(expandedSection === 'trace' ? null : 'trace')}
              sx={{ mb: 2 }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box display="flex" alignItems="center" gap={2}>
                  <TimelineIcon color="primary" />
                  <Typography variant="h6">One-Up, One-Back Trace</Typography>
                  <Chip
                    label={`${(results.oneUpOneBack?.upstream_trace?.length || 0) + (results.oneUpOneBack?.downstream_trace?.length || 0)} nodes`}
                    variant="outlined"
                    size="small"
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" fontWeight={600} mb={2} display="flex" alignItems="center" gap={1}>
                      <BusinessIcon color="primary" />
                      Upstream Trace
                    </Typography>
                    {results.oneUpOneBack?.upstream_trace?.map((node: TraceNode) => 
                      renderTraceNode(node, 'upstream')
                    )}
                    {(!results.oneUpOneBack?.upstream_trace || results.oneUpOneBack.upstream_trace.length === 0) && (
                      <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
                        No upstream trace data available
                      </Typography>
                    )}
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" fontWeight={600} mb={2} display="flex" alignItems="center" gap={1}>
                      <LocalShippingIcon color="primary" />
                      Downstream Trace
                    </Typography>
                    {results.oneUpOneBack?.downstream_trace?.map((node: TraceNode) => 
                      renderTraceNode(node, 'downstream')
                    )}
                    {(!results.oneUpOneBack?.downstream_trace || results.oneUpOneBack.downstream_trace.length === 0) && (
                      <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
                        No downstream trace data available
                      </Typography>
                    )}
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            {/* CCP Alerts */}
            <Accordion
              expanded={expandedSection === 'alerts'}
              onChange={() => setExpandedSection(expandedSection === 'alerts' ? null : 'alerts')}
              sx={{ mb: 2 }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box display="flex" alignItems="center" gap={2}>
                  <SecurityIcon color="primary" />
                  <Typography variant="h6">CCP Alerts</Typography>
                  <Chip
                    label={results.ccpAlerts.length}
                    color={results.ccpAlerts.length > 0 ? 'warning' : 'success'}
                    size="small"
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                {renderCCPAlerts(results.ccpAlerts)}
              </AccordionDetails>
            </Accordion>
          </Box>
        )}

        {/* Mobile Speed Dial for Quick Actions */}
        {isMobile && results && (
          <SpeedDial
            ariaLabel="Quick actions"
            sx={{ 
              position: 'fixed', 
              bottom: 16, 
              right: 16,
              zIndex: theme.zIndex.speedDial
            }}
            icon={<SpeedDialIcon />}
          >
            <SpeedDialAction
              icon={<SaveIcon />}
              tooltipTitle="Save"
              onClick={handleSave}
              aria-label="Save traceability results"
            />
            <SpeedDialAction
              icon={<UndoIcon />}
              tooltipTitle="Undo"
              onClick={undoStack.length === 0 ? undefined : handleUndo}
              aria-label="Undo last action"
            />
            <SpeedDialAction
              icon={<RedoIcon />}
              tooltipTitle="Redo"
              onClick={redoStack.length === 0 ? undefined : handleRedo}
              aria-label="Redo last action"
            />
            <SpeedDialAction
              icon={<RefreshIcon />}
              tooltipTitle="Refresh"
              onClick={handleOneClickTrace}
              aria-label="Refresh traceability analysis"
            />
          </SpeedDial>
        )}
      </CardContent>
    </Card>
  );
};

export default OneClickTraceability;
