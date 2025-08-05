import React, { useState } from 'react';
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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Description,
  Close,
  Approval,
  CheckCircle,
  Warning,
  Info,
  Person,
  CalendarToday,
  FileCopy,
  Visibility,
  Lock,
  LockOpen,
  Edit,
  History,
} from '@mui/icons-material';
import { AppDispatch } from '../../store';
import { approveVersion } from '../../store/slices/documentSlice';

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

interface DocumentApprovalDialogProps {
  open: boolean;
  document: Document | null;
  onClose: () => void;
  onSuccess: () => void;
}

const DocumentApprovalDialog: React.FC<DocumentApprovalDialogProps> = ({
  open,
  document,
  onClose,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    comments: '',
    effective_date: '',
    review_date: '',
  });

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

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleApprove = async () => {
    setLoading(true);
    setError(null);

    try {
      // For now, we'll approve the current version
      // In a real implementation, you might want to select a specific version
      await dispatch(approveVersion({
        documentId: document.id,
        versionId: 1, // This should be the actual version ID
        comments: formData.comments,
      }));
      
      setSuccess(true);
      setTimeout(() => {
        handleClose();
        onSuccess();
      }, 2000);
    } catch (error: any) {
      setError(error.message || 'Failed to approve document');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setFormData({
        comments: '',
        effective_date: '',
        review_date: '',
      });
      setError(null);
      setSuccess(false);
      onClose();
    }
  };

  const isOverdue = document.review_date && new Date(document.review_date) < new Date();

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Approval color="primary" />
            <Typography variant="h6">Approve Document</Typography>
          </Box>
          <IconButton onClick={handleClose} disabled={loading}>
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

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} icon={<CheckCircle />}>
            Document approved successfully!
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Document Information */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  {getDocumentTypeIcon(document.document_type)}
                  <Box>
                    <Typography variant="h6">
                      {document.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {document.document_number} • v{document.version}
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip
                    label={getDocumentTypeLabel(document.document_type)}
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    label={document.category.toUpperCase()}
                    color="secondary"
                    variant="outlined"
                  />
                  <Chip
                    label={document.status.replace('_', ' ')}
                    color="warning"
                    variant="filled"
                  />
                </Box>
                {document.description && (
                  <Typography variant="body2" color="text.secondary">
                    {document.description}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Document Details */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Document Details
            </Typography>
            <List dense>
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
              <ListItem>
                <ListItemIcon>
                  <FileCopy />
                </ListItemIcon>
                <ListItemText
                  primary="Department"
                  secondary={document.department || 'Not specified'}
                />
              </ListItem>
              {document.file_path && (
                <ListItem>
                  <ListItemIcon>
                    <FileCopy />
                  </ListItemIcon>
                  <ListItemText
                    primary="File"
                    secondary={document.original_filename || 'Unknown'}
                  />
                </ListItem>
              )}
            </List>
          </Grid>

          {/* Review Information */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Review Information
            </Typography>
            <List dense>
              {document.review_date && (
                <ListItem>
                  <ListItemIcon>
                    <CalendarToday color={isOverdue ? 'error' : 'primary'} />
                  </ListItemIcon>
                  <ListItemText
                    primary="Review Date"
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2">
                          {formatDate(document.review_date)}
                        </Typography>
                        {isOverdue && (
                          <Chip label="Overdue" color="error" size="small" />
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              )}
              {document.effective_date && (
                <ListItem>
                  <ListItemIcon>
                    <CalendarToday />
                  </ListItemIcon>
                  <ListItemText
                    primary="Effective Date"
                    secondary={formatDate(document.effective_date)}
                  />
                </ListItem>
              )}
              <ListItem>
                <ListItemIcon>
                  <Lock color="warning" />
                </ListItemIcon>
                <ListItemText
                  primary="Current Status"
                  secondary="Pending Approval"
                />
              </ListItem>
            </List>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
          </Grid>

          {/* Approval Form */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Approval Details
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Approval Comments"
              value={formData.comments}
              onChange={(e) => handleInputChange('comments', e.target.value)}
              multiline
              rows={3}
              placeholder="Enter any comments or notes about this approval..."
              disabled={loading}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Effective Date"
              type="date"
              value={formData.effective_date}
              onChange={(e) => handleInputChange('effective_date', e.target.value)}
              disabled={loading}
              InputLabelProps={{
                shrink: true,
              }}
              helperText="Date when this document becomes effective"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Next Review Date"
              type="date"
              value={formData.review_date}
              onChange={(e) => handleInputChange('review_date', e.target.value)}
              disabled={loading}
              InputLabelProps={{
                shrink: true,
              }}
              helperText="Date when this document should be reviewed"
            />
          </Grid>

          {/* Approval Checklist */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Approval Checklist
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                Please confirm the following before approving this document:
              </Typography>
            </Alert>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="Document content has been reviewed"
                  secondary="All information is accurate and complete"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="Document complies with ISO 22000 requirements"
                  secondary="Meets food safety management system standards"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="Document is ready for implementation"
                  secondary="All stakeholders have been consulted"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="Review and effective dates are appropriate"
                  secondary="Timeline is realistic and achievable"
                />
              </ListItem>
            </List>
          </Grid>

          {/* Warnings */}
          {isOverdue && (
            <Grid item xs={12}>
              <Alert severity="warning" icon={<Warning />}>
                <Typography variant="body2">
                  <strong>Warning:</strong> This document's review date has passed. 
                  Please ensure the content is still current and relevant before approval.
                </Typography>
              </Alert>
            </Grid>
          )}

          {!document.file_path && (
            <Grid item xs={12}>
              <Alert severity="warning" icon={<Warning />}>
                <Typography variant="body2">
                  <strong>Note:</strong> This document has no attached file. 
                  Please ensure the document content is available through other means.
                </Typography>
              </Alert>
            </Grid>
          )}
        </Grid>
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="outlined"
          startIcon={<History />}
          onClick={() => {
            // Implement view history functionality
            console.log('View document history');
          }}
          disabled={loading}
        >
          View History
        </Button>
        <Button
          variant="contained"
          color="success"
          startIcon={<Approval />}
          onClick={handleApprove}
          disabled={loading}
        >
          {loading ? 'Approving...' : 'Approve Document'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentApprovalDialog; 