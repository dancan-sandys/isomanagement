import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Skeleton,
  Tooltip,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  History,
  Download,
  CheckCircle,
  Pending,
  Schedule,
  Info,
} from '@mui/icons-material';
import { documentsAPI } from '../services/api';

interface Version {
  id: number;
  version_number: string;
  file_path: string;
  file_size: number;
  file_type: string;
  original_filename: string;
  change_description: string;
  change_reason: string;
  created_by: string;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  is_current: boolean;
}

interface ChangeLog {
  id: number;
  change_type: string;
  change_description: string;
  old_version: string | null;
  new_version: string | null;
  changed_by: string;
  created_at: string;
}

interface DocumentVersionHistoryProps {
  documentId: number;
  currentVersion: string;
  onVersionChange?: (version: string) => void;
}

const DocumentVersionHistory: React.FC<DocumentVersionHistoryProps> = ({
  documentId,
  currentVersion,
  onVersionChange,
}) => {
  const [versions, setVersions] = useState<Version[]>([]);
  const [changeLogs, setChangeLogs] = useState<ChangeLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<Version | null>(null);
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [approveComments, setApproveComments] = useState('');
  const [approving, setApproving] = useState(false);
  const [viewChangeLog, setViewChangeLog] = useState(false);

  const fetchVersionHistory = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await documentsAPI.getVersionHistory(documentId);
      if (response.success) {
        setVersions(response.data.versions);
      } else {
        setError('Failed to load version history');
      }
    } catch (err) {
      setError('Error loading version history');
      console.error('Error fetching version history:', err);
    } finally {
      setLoading(false);
    }
  }, [documentId]);

  const fetchChangeLog = useCallback(async () => {
    try {
      const response = await documentsAPI.getChangeLog(documentId);
      if (response.success) {
        setChangeLogs(response.data.changes);
      }
    } catch (err) {
      console.error('Error fetching change log:', err);
    }
  }, [documentId]);

  useEffect(() => {
    fetchVersionHistory();
    fetchChangeLog();
  }, [documentId, fetchVersionHistory, fetchChangeLog]);

  const handleDownloadVersion = async (version: Version) => {
    try {
      const response = await documentsAPI.downloadVersion(documentId, version.id);
      // Handle file download
      const blob = new Blob([response], { type: version.file_type });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = version.original_filename || `document_v${version.version_number}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading version:', err);
    }
  };

  const handleApproveVersion = async () => {
    if (!selectedVersion) return;

    try {
      setApproving(true);
      const response = await documentsAPI.approveVersion(
        documentId,
        selectedVersion.id,
        approveComments
      );
      
      if (response.success) {
        setApproveDialogOpen(false);
        setApproveComments('');
        setSelectedVersion(null);
        fetchVersionHistory(); // Refresh the list
      }
    } catch (err) {
      console.error('Error approving version:', err);
    } finally {
      setApproving(false);
    }
  };

  const getStatusColor = (version: Version) => {
    if (version.approved_by) return 'success';
    if (version.is_current) return 'primary';
    return 'default';
  };

  const getStatusIcon = (version: Version) => {
    if (version.approved_by) return <CheckCircle />;
    if (version.is_current) return <Pending />;
    return <Schedule />;
  };

  const getStatusText = (version: Version) => {
    if (version.approved_by) return 'Approved';
    if (version.is_current) return 'Current';
    return 'Draft';
  };

  const formatFileSize = (bytes: number) => {
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

  if (loading) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          <History sx={{ mr: 1, verticalAlign: 'middle' }} />
          Version History
        </Typography>
        <Skeleton variant="rectangular" height={200} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          <History sx={{ mr: 1, verticalAlign: 'middle' }} />
          Version History
        </Typography>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          <History sx={{ mr: 1, verticalAlign: 'middle' }} />
          Version History
        </Typography>
        <Box>
          <Button
            variant="outlined"
            size="small"
            onClick={() => setViewChangeLog(!viewChangeLog)}
            startIcon={<Info />}
            sx={{ mr: 1 }}
          >
            {viewChangeLog ? 'Hide' : 'Show'} Change Log
          </Button>
        </Box>
      </Box>

      {viewChangeLog && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Change Log
            </Typography>
            <List dense>
              {changeLogs.map((log) => (
                <ListItem key={log.id} divider>
                  <ListItemIcon>
                    <Info color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={log.change_description}
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          {formatDate(log.created_at)} • {log.changed_by}
                        </Typography>
                        {log.old_version && log.new_version && (
                          <Typography variant="caption" color="text.secondary">
                            Version: {log.old_version} → {log.new_version}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Version</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>File</TableCell>
              <TableCell>Changes</TableCell>
              <TableCell>Created By</TableCell>
              <TableCell>Created Date</TableCell>
              <TableCell>Approved By</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {versions.map((version) => (
              <TableRow key={version.id} hover>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <Typography variant="body2" fontWeight="bold">
                      {version.version_number}
                    </Typography>
                    {version.is_current && (
                      <Chip
                        label="Current"
                        size="small"
                        color="primary"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    icon={getStatusIcon(version)}
                    label={getStatusText(version)}
                    color={getStatusColor(version) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="body2" noWrap>
                      {version.original_filename}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {formatFileSize(version.file_size)}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="body2" noWrap>
                      {version.change_description}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Reason: {version.change_reason}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {version.created_by}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {formatDate(version.created_at)}
                  </Typography>
                </TableCell>
                <TableCell>
                  {version.approved_by ? (
                    <Box>
                      <Typography variant="body2">
                        {version.approved_by}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {version.approved_at && formatDate(version.approved_at)}
                      </Typography>
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Not approved
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    <Tooltip title="Download">
                      <IconButton
                        size="small"
                        onClick={() => handleDownloadVersion(version)}
                      >
                        <Download />
                      </IconButton>
                    </Tooltip>
                    {!version.approved_by && (
                      <Tooltip title="Approve Version">
                        <IconButton
                          size="small"
                          color="success"
                          onClick={() => {
                            setSelectedVersion(version);
                            setApproveDialogOpen(true);
                          }}
                        >
                          <CheckCircle />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Approve Version Dialog */}
      <Dialog open={approveDialogOpen} onClose={() => setApproveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Approve Version {selectedVersion?.version_number}</DialogTitle>
        <DialogContent>
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary">
              Are you sure you want to approve this version? This will mark the document as approved.
            </Typography>
          </Box>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Comments (Optional)"
            value={approveComments}
            onChange={(e) => setApproveComments(e.target.value)}
            placeholder="Add any comments about this approval..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApproveDialogOpen(false)} disabled={approving}>
            Cancel
          </Button>
          <Button
            onClick={handleApproveVersion}
            color="success"
            variant="contained"
            disabled={approving}
          >
            {approving ? 'Approving...' : 'Approve Version'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentVersionHistory; 