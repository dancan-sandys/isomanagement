import React, { useState } from 'react';
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
  alpha
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
  Inventory as InventoryIcon
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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<TraceabilityResults | null>(null);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const handleOneClickTrace = async () => {
    setLoading(true);
    setError(null);
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
    <Card sx={{ width: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={2} mb={3}>
          <TimelineIcon color="primary" sx={{ fontSize: 32 }} />
          <Box flex={1}>
            <Typography variant="h5" fontWeight={600}>
              One-Click Traceability Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {batchNumber && productName ? `${batchNumber} - ${productName}` : `Batch ID: ${batchId}`}
            </Typography>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {!results && !loading && (
          <Box textAlign="center" py={4}>
            <TimelineIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" mb={2}>
              Ready for Traceability Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3}>
              Click the button below to perform comprehensive traceability analysis including
              one-up-one-back tracing, completeness scoring, verification status, and CCP alerts.
            </Typography>
            <Button
              variant="contained"
              size="large"
              startIcon={<TimelineIcon />}
              onClick={handleOneClickTrace}
              sx={{ px: 4, py: 1.5 }}
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
            <Box display="flex" alignItems="center" gap={2} mb={3}>
              <CheckCircleIcon color="success" sx={{ fontSize: 24 }} />
              <Typography variant="h6" fontWeight={600}>
                Analysis Complete
              </Typography>
              <Button
                variant="outlined"
                size="small"
                startIcon={<RefreshIcon />}
                onClick={handleOneClickTrace}
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
      </CardContent>
    </Card>
  );
};

export default OneClickTraceability;
