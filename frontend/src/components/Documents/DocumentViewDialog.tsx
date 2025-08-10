import React, { useState } from 'react';
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
  Description,
  Close,
  Download,
  Edit,
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
} from '@mui/icons-material';
import { documentsAPI } from '../../services/api';

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

interface DocumentViewDialogProps {
  open: boolean;
  document: Document | null;
  onClose: () => void;
  onEdit: () => void;
}

const DocumentViewDialog: React.FC<DocumentViewDialogProps> = ({
  open,
  document,
  onClose,
  onEdit,
}) => {
  const [loading, setLoading] = useState(false);
  const [viewingDocument, setViewingDocument] = useState(false);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);

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

  const getDocumentTypeLabel = (type: string) => {
    return type.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'under_review':
        return 'warning';
      case 'draft':
        return 'info';
      case 'obsolete':
        return 'error';
      case 'archived':
        return 'default';
      default:
        return 'default';
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

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
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

  const handleDownload = async () => {
    try {
      // Get the document URL for downloading
      const blob = await documentsAPI.downloadDocument(document.id);
      const filename = document.original_filename || `${document.title}.pdf`;
      downloadFile(blob, filename);
    } catch (error) {
      console.error('Error downloading document:', error);
    }
  };

  const handleViewDocument = async () => {
    try {
      console.log('=== VIEW DOCUMENT DEBUG ===');
      console.log('Document ID:', document.id);
      console.log('Document file type:', document.file_type);
      console.log('Document filename:', document.original_filename);
      
      // Get the document URL for viewing
      console.log('Calling API...');
      const blob = await documentsAPI.downloadDocument(document.id);
      console.log('Blob received, size:', blob.size);
      console.log('Blob type:', blob.type);
      
      const url = window.URL.createObjectURL(blob);
      console.log('Created URL:', url);
      
      // Set the URL for iframe viewing
      setViewerUrl(url);
      setViewingDocument(true);
      
    } catch (error: any) {
      console.error('Error viewing document:', error);
      console.error('Error details:', error.message);
      console.error('Error stack:', error.stack);
    }
  };

  const handleCloseViewer = () => {
    if (viewerUrl) {
      window.URL.revokeObjectURL(viewerUrl);
    }
    setViewingDocument(false);
    setViewerUrl(null);
  };

  const handleViewHistory = () => {
    // Implement view history functionality
    console.log('View history for document:', document.id);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getDocumentTypeIcon(document.document_type)}
            <Typography variant="h6">Document Details</Typography>
          </Box>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}

        {viewingDocument ? (
          <Box sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">
                Viewing: {document.original_filename || document.title}
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
                  title={`Document: ${document.title}`}
                />
              )}
            </Box>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {/* Document Header */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Chip
                  label={getDocumentTypeLabel(document.document_type)}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={`v${document.version}`}
                  color="secondary"
                  variant="outlined"
                />
                <Chip
                  label={document.status.replace('_', ' ')}
                  color={getStatusColor(document.status) as any}
                  variant="filled"
                />
              </Box>
            </Grid>

            {/* Document Information */}
            <Grid item xs={12} md={8}>
              <Typography variant="h5" gutterBottom>
                {document.title}
              </Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                {document.document_number}
              </Typography>
              {document.description && (
                <Typography variant="body2" sx={{ mt: 2 }}>
                  {document.description}
                </Typography>
              )}
            </Grid>

            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Tooltip title="Edit Document">
                  <IconButton color="primary" onClick={onEdit}>
                    <Edit />
                  </IconButton>
                </Tooltip>
                {document.file_path && (
                  <>
                    <Tooltip title="View Document">
                      <IconButton color="primary" onClick={handleViewDocument}>
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Download">
                      <IconButton color="primary" onClick={handleDownload}>
                        <Download />
                      </IconButton>
                    </Tooltip>
                  </>
                )}
                <Tooltip title="View History">
                  <IconButton color="primary" onClick={handleViewHistory}>
                    <History />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Share">
                  <IconButton color="primary">
                    <Share />
                  </IconButton>
                </Tooltip>
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>

            {/* Document Details */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Document Information
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Description />
                  </ListItemIcon>
                  <ListItemText
                    primary="Document Type"
                    secondary={getDocumentTypeLabel(document.document_type)}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <FileCopy />
                  </ListItemIcon>
                  <ListItemText
                    primary="Category"
                    secondary={document.category.toUpperCase()}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Person />
                  </ListItemIcon>
                  <ListItemText
                    primary="Department"
                    secondary={document.department || 'Not specified'}
                  />
                </ListItem>
                {document.product_line && (
                  <ListItem>
                    <ListItemIcon>
                      <FileCopy />
                    </ListItemIcon>
                    <ListItemText
                      primary="Product Line"
                      secondary={document.product_line}
                    />
                  </ListItem>
                )}
              </List>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                File Information
              </Typography>
              <List dense>
                {document.file_path && (
                  <ListItem>
                    <ListItemIcon>
                      <FileCopy />
                    </ListItemIcon>
                    <ListItemText
                      primary="File Name"
                      secondary={document.original_filename || 'Unknown'}
                    />
                  </ListItem>
                )}
                {document.file_size && (
                  <ListItem>
                    <ListItemIcon>
                      <FileCopy />
                    </ListItemIcon>
                    <ListItemText
                      primary="File Size"
                      secondary={formatFileSize(document.file_size)}
                    />
                  </ListItem>
                )}
                <ListItem>
                  <ListItemIcon>
                    <Person />
                  </ListItemIcon>
                  <ListItemText
                    primary="Created By"
                    secondary={document.created_by}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CalendarToday />
                  </ListItemIcon>
                  <ListItemText
                    primary="Created Date"
                    secondary={formatDate(document.created_at)}
                  />
                </ListItem>
                {document.updated_at && (
                  <ListItem>
                    <ListItemIcon>
                      <CalendarToday />
                    </ListItemIcon>
                    <ListItemText
                      primary="Last Updated"
                      secondary={formatDate(document.updated_at)}
                    />
                  </ListItem>
                )}
              </List>
            </Grid>

            {/* Approval Information */}
            {document.approved_by && (
              <>
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Approval Information
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemIcon>
                        <Approval />
                      </ListItemIcon>
                      <ListItemText
                        primary="Approved By"
                        secondary={document.approved_by}
                      />
                    </ListItem>
                    {document.approved_at && (
                      <ListItem>
                        <ListItemIcon>
                          <CalendarToday />
                        </ListItemIcon>
                        <ListItemText
                          primary="Approval Date"
                          secondary={formatDate(document.approved_at)}
                        />
                      </ListItem>
                    )}
                    {document.effective_date && (
                      <ListItem>
                        <ListItemIcon>
                          <Schedule />
                        </ListItemIcon>
                        <ListItemText
                          primary="Effective Date"
                          secondary={formatDate(document.effective_date)}
                        />
                      </ListItem>
                    )}
                    {document.review_date && (
                      <ListItem>
                        <ListItemIcon>
                          <Schedule />
                        </ListItemIcon>
                        <ListItemText
                          primary="Review Date"
                          secondary={formatDate(document.review_date)}
                        />
                      </ListItem>
                    )}
                  </List>
                </Grid>
              </>
            )}

            {/* Keywords */}
            {document.keywords && (
              <>
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Keywords
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {document.keywords.split(',').map((keyword, index) => (
                      <Chip
                        key={index}
                        label={keyword.trim()}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Grid>
              </>
            )}
          </Grid>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose}>
          Close
        </Button>
        <Button
          variant="contained"
          onClick={onEdit}
          startIcon={<Edit />}
        >
          Edit Document
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentViewDialog; 