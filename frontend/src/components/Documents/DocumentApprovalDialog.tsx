import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  IconButton,
  Chip,
  Grid,
} from '@mui/material';
import {
  Close,
  Approval,
  CheckCircle,
  Error as ErrorIcon,
  Comment,
  Send,
} from '@mui/icons-material';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store';
import { approveVersion } from '../../store/slices/documentSlice';
import { documentsAPI } from '../../services/api';

interface DocumentApprovalDialogProps {
  open: boolean;
  document: any;
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
  const [approvalData, setApprovalData] = useState({
    action: 'approve',
    comments: '',
  });

  const handleSubmit = async () => {
    if (!document) return;

    setLoading(true);
    setError(null);

    try {
      // Get the current version of the document
      const versionResponse = await documentsAPI.getVersionHistory(document.id);
      const currentVersion = versionResponse.data.versions?.find((v: any) => v.is_current);
      
      if (!currentVersion) {
        const error = new Error('No current version found for this document');
        throw error;
      }

      // Call the real approval API
      await dispatch(approveVersion({
        documentId: document.id,
        versionId: currentVersion.id,
        comments: approvalData.comments
      })).unwrap();
      
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
      setApprovalData({
        action: 'approve',
        comments: '',
      });
      setError(null);
      setSuccess(false);
      onClose();
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'approve':
        return 'success';
      case 'reject':
        return 'error';
      case 'request_changes':
        return 'warning';
      default:
        return 'primary';
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'approve':
        return <CheckCircle />;
      case 'reject':
        return <ErrorIcon />;
      case 'request_changes':
        return <Comment />;
      default:
        return <Approval />;
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Approval color="primary" />
            <Typography variant="h6">
              Approve Document
            </Typography>
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

        {document && (
          <Box>
            {/* Document Information */}
            <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom>
                {document.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Document Number: {document.document_number}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Version: {document.version}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Type: {document.document_type?.replace('_', ' ')}
              </Typography>
            </Box>

            {/* Approval Action */}
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Action</InputLabel>
                  <Select
                    value={approvalData.action}
                    onChange={(e) => setApprovalData({ ...approvalData, action: e.target.value })}
                    disabled={loading}
                  >
                    <MenuItem value="approve">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CheckCircle color="success" />
                        Approve Document
                      </Box>
                    </MenuItem>
                    <MenuItem value="reject">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <ErrorIcon color="error" />
                        Reject Document
                      </Box>
                    </MenuItem>
                    <MenuItem value="request_changes">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Comment color="warning" />
                        Request Changes
                      </Box>
                    </MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Comments"
                  value={approvalData.comments}
                  onChange={(e) => setApprovalData({ ...approvalData, comments: e.target.value })}
                  placeholder={`Add your comments for ${approvalData.action}...`}
                  disabled={loading}
                  helperText={`Comments will be recorded with your ${approvalData.action} action`}
                />
              </Grid>
            </Grid>

            {/* Action Summary */}
            <Box sx={{ mt: 3, p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Action Summary:
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {getActionIcon(approvalData.action)}
                <Typography variant="body2">
                  You are about to <strong>{approvalData.action}</strong> this document
                </Typography>
                <Chip
                  label={approvalData.action}
                  color={getActionColor(approvalData.action) as any}
                  size="small"
                />
              </Box>
            </Box>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading}
          color={getActionColor(approvalData.action) as any}
          startIcon={getActionIcon(approvalData.action)}
        >
          {loading ? 'Processing...' : `${approvalData.action.charAt(0).toUpperCase() + approvalData.action.slice(1)} Document`}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentApprovalDialog; 