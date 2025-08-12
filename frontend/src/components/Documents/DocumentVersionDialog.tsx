import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/lab';
import {
  Description,
  Close,
  Download,
  History,
  Approval,
  Schedule,
  Person,
  CalendarToday,
  FileCopy,
  Share,
  Visibility,
  Lock,
  LockOpen,
  CheckCircle,
  Pending,
  Edit,
  CloudUpload,
} from '@mui/icons-material';
import { AppDispatch } from '../../store';
import { fetchDocumentVersions } from '../../store/slices/documentSlice';
import CreateNewVersion from '../CreateNewVersion';
import { documentsAPI } from '../../services/api';

interface DocumentVersion {
  id: number;
  version_number: string;
  file_path: string;
  file_size?: number;
  file_type?: string;
  original_filename?: string;
  change_description?: string;
  change_reason?: string;
  created_by: string;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  is_current: boolean;
}

interface Document {
  id: number;
  document_number: string;
  title: string;
  description?: string;
  document_type: string;
  category: string;
  status: string;
  version: string;
  file_path?: string;
  file_size?: number;
  file_type?: string;
  original_filename?: string;
  department?: string;
  product_line?: string;
  applicable_products?: number[];
  keywords?: string;
  created_by: string;
  approved_by?: string;
  approved_at?: string;
  effective_date?: string;
  review_date?: string;
  created_at: string;
  updated_at?: string;
}

interface DocumentVersionDialogProps {
  open: boolean;
  document: Document | null;
  onClose: () => void;
}

const DocumentVersionDialog: React.FC<DocumentVersionDialogProps> = ({
  open,
  document,
  onClose,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [loading, setLoading] = useState(false);
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [showCreateVersion, setShowCreateVersion] = useState(false);
  const [viewingVersion, setViewingVersion] = useState<DocumentVersion | null>(null);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);
  const [exporting, setExporting] = useState<false | 'pdf' | 'xlsx'>(false);

  useEffect(() => {
    if (open && document) {
      loadVersions();
    }
  }, [open, document]);

  const loadVersions = async () => {
    if (!document) return;

    setLoading(true);
    setError(null);

    try {
      const response = await dispatch(fetchDocumentVersions(document.id));
      if (response.payload?.data?.versions) {
        setVersions(response.payload.data.versions);
      }
    } catch (error: any) {
      setError(error.message || 'Failed to load version history');
    } finally {
      setLoading(false);
    }
  };

  const handleVersionCreated = (newVersion: string) => {
    setShowCreateVersion(false);
    loadVersions(); // Reload versions to show the new one
  };

  const handleCreateNewVersion = () => {
    setShowCreateVersion(true);
  };

  if (!document) return null;

  const getDocumentTypeIcon = (type: string) => {
    switch (type) {
      case 'procedure':
        return <Description color="primary" />;
      case 'work_instruction':
        return <Description color="secondary" />;
      case 'form':
        return <Description color="success" />;
      case 'policy':
        return <Description color="warning" />;
      case 'manual':
        return <Description color="error" />;
      case 'plan':
        return <Description color="info" />;
      case 'checklist':
        return <Description />;
      default:
        return <Description />;
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown';
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const link = globalThis.document.createElement('a');
    link.href = url;
    link.download = filename;
    globalThis.document.body.appendChild(link);
    link.click();
    globalThis.document.body.removeChild(link);
    setTimeout(() => window.URL.revokeObjectURL(url), 1000);
  };

  const handleExportVersions = async (format: 'pdf' | 'xlsx') => {
    if (!document) return;
    try {
      setExporting(format);
      const blob = await documentsAPI.exportVersions(document.id, format);
      downloadFile(blob, `version_history_${document.document_number || document.id}.${format}`);
    } catch (e) {
      console.error('Export failed', e);
    } finally {
      setExporting(false);
    }
  };

  const handleDownload = async (version: DocumentVersion) => {
    try {
      // Get the document URL for downloading
      const blob = await documentsAPI.downloadVersion(document.id, version.id);
      const filename = version.original_filename || `document_v${version.version_number}.pdf`;
      downloadFile(blob, filename);
    } catch (error) {
      console.error('Error downloading version:', error);
    }
  };

  const handleViewVersion = async (version: DocumentVersion) => {
    try {
      console.log('=== VIEW VERSION DEBUG ===');
      console.log('Viewing version:', version);
      console.log('Document ID:', document.id);
      console.log('Version ID:', version.id);
      console.log('Version file type:', version.file_type);
      console.log('Version filename:', version.original_filename);
      
      // Get the document URL for viewing
      console.log('Calling API...');
      const blob = await documentsAPI.downloadVersion(document.id, version.id);
      
      console.log('Blob received, size:', blob.size);
      console.log('Blob type:', blob.type);
      const url = window.URL.createObjectURL(blob);
      console.log('Created URL:', url);
      
      // Set the version and URL for iframe viewing
      setViewingVersion(version);
      setViewerUrl(url);
      
    } catch (error: any) {
      console.error('Error viewing version:', error);
      console.error('Error details:', error.message);
      console.error('Error stack:', error.stack);
    }
  };

  const handleCloseViewer = () => {
    if (viewerUrl) {
      window.URL.revokeObjectURL(viewerUrl);
    }
    setViewingVersion(null);
    setViewerUrl(null);
  };

  const getVersionStatusIcon = (version: DocumentVersion) => {
    if (version.approved_by) {
      return <CheckCircle color="success" />;
    }
    return <Pending color="warning" />;
  };

  const getVersionStatusColor = (version: DocumentVersion) => {
    if (version.approved_by) {
      return 'success';
    }
    return 'warning';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <History />
            <Typography variant="h6">Version History</Typography>
          </Box>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {showCreateVersion ? (
          <CreateNewVersion
            documentId={document.id}
            currentVersion={document.version}
            onVersionCreated={handleVersionCreated}
            onCancel={() => setShowCreateVersion(false)}
          />
        ) : viewingVersion ? (
          <Box sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">
                Viewing: {viewingVersion.original_filename || `Version ${viewingVersion.version_number}`}
              </Typography>
              <Button onClick={handleCloseViewer} variant="outlined" size="small">
                Close Viewer
              </Button>
            </Box>
            <Box sx={{ flex: 1, border: '1px solid #ddd', borderRadius: 1, overflow: 'hidden' }}>
              {viewerUrl && (
                <iframe
                  src={viewerUrl}
                  style={{
                    width: '100%',
                    height: '100%',
                    border: 'none',
                  }}
                  title={`Document Version ${viewingVersion.version_number}`}
                />
              )}
            </Box>
          </Box>
        ) : (
          <>
            {/* Document Header */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                {getDocumentTypeIcon(document.document_type)}
                <Box>
                  <Typography variant="h6">
                    {document.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {document.document_number}
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip
                  label={`Current: v${document.version}`}
                  color="primary"
                  variant="filled"
                />
                <Chip
                  label={`${versions.length} versions`}
                  color="secondary"
                  variant="outlined"
                />
              </Box>
            </Box>

            <Divider sx={{ mb: 3 }} />

            {/* Version Timeline */}
            <Typography variant="h6" gutterBottom>
              Version Timeline
            </Typography>

            {versions.length > 0 ? (
              <Timeline position="alternate">
                {versions.map((version, index) => (
                  <TimelineItem key={version.id}>
                    <TimelineOppositeContent sx={{ m: 'auto 0' }} variant="body2" color="text.secondary">
                      {formatDate(version.created_at)}
                    </TimelineOppositeContent>
                    <TimelineSeparator>
                      <TimelineDot color={getVersionStatusColor(version) as any}>
                        {getVersionStatusIcon(version)}
                      </TimelineDot>
                      {index < versions.length - 1 && <TimelineConnector />}
                    </TimelineSeparator>
                    <TimelineContent sx={{ py: '12px', px: 2 }}>
                      <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Chip
                            label={`v${version.version_number}`}
                            color={version.is_current ? 'primary' : 'default'}
                            size="small"
                          />
                          {version.is_current && (
                            <Chip
                              label="Current"
                              color="success"
                              size="small"
                            />
                          )}
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {version.change_description || 'No description'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Created by: {version.created_by}
                        </Typography>
                        {version.approved_by && (
                          <Typography variant="caption" color="text.secondary" display="block">
                            Approved by: {version.approved_by}
                          </Typography>
                        )}
                      </Box>
                    </TimelineContent>
                  </TimelineItem>
                ))}
              </Timeline>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <History sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No Version History
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  This document has no previous versions.
                </Typography>
              </Box>
            )}

            <Divider sx={{ my: 3 }} />

            {/* Version Details */}
            {versions.length > 0 && (
              <>
                <Typography variant="h6" gutterBottom>
                  Version Details
                </Typography>
                <List>
                  {versions.map((version) => (
                    <ListItem key={version.id} divider>
                      <ListItemIcon>
                        {getVersionStatusIcon(version)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Typography variant="body1" fontWeight={600}>
                              Version {version.version_number}
                            </Typography>
                            {version.is_current && (
                              <Chip label="Current" color="success" size="small" />
                            )}
                            <Chip
                              label={version.approved_by ? 'Approved' : 'Pending'}
                              color={version.approved_by ? 'success' : 'warning'}
                              size="small"
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {version.change_description || 'No change description'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Created: {formatDate(version.created_at)} • By: {version.created_by}
                            </Typography>
                            {version.change_reason && (
                              <Typography variant="caption" color="text.secondary" display="block">
                                Reason: {version.change_reason}
                              </Typography>
                            )}
                            {version.file_size && (
                              <Typography variant="caption" color="text.secondary" display="block">
                                File: {version.original_filename} ({formatFileSize(version.file_size)})
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View Version">
                          <IconButton
                            size="small"
                            onClick={() => handleViewVersion(version)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Download Version">
                          <IconButton
                            size="small"
                            onClick={() => handleDownload(version)}
                          >
                            <Download />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </ListItem>
                  ))}
                </List>
              </>
            )}

            {/* Version Statistics */}
            {versions.length > 0 && (
              <>
                <Divider sx={{ my: 3 }} />
                <Typography variant="h6" gutterBottom>
                  Version Statistics
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                      <Typography variant="h4" color="primary">
                        {versions.length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Versions
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                      <Typography variant="h4" color="success.main">
                        {versions.filter(v => v.approved_by).length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Approved Versions
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                      <Typography variant="h4" color="warning.main">
                        {versions.filter(v => !v.approved_by).length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Pending Versions
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                      <Typography variant="h4" color="info.main">
                        {versions[0] ? formatDate(versions[0].created_at) : 'N/A'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        First Version
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </>
            )}
          </>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose}>
          Close
        </Button>
        <Button onClick={() => handleExportVersions('pdf')} disabled={!!exporting}>
          Export Versions PDF
        </Button>
        <Button onClick={() => handleExportVersions('xlsx')} disabled={!!exporting}>
          Export Versions XLSX
        </Button>
        {!showCreateVersion && (
          <Button
            variant="contained"
            startIcon={<CloudUpload />}
            onClick={handleCreateNewVersion}
          >
            Create New Version
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default DocumentVersionDialog; 