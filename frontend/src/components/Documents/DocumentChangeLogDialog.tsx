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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Close,
  Timeline,
  History,
  Edit,
  CheckCircle,
  Warning,
  Info,
  Person,
  AccessTime,
  Label,
} from '@mui/icons-material';
import { AppDispatch } from '../../store';
import { fetchChangeLog } from '../../store/slices/documentSlice';

interface DocumentChangeLogDialogProps {
  open: boolean;
  document: any;
  onClose: () => void;
}

const DocumentChangeLogDialog: React.FC<DocumentChangeLogDialogProps> = ({
  open,
  document,
  onClose,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [loading, setLoading] = useState(false);
  const [changeLog, setChangeLog] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && document) {
      loadChangeLog();
    }
  }, [open, document]);

  const loadChangeLog = async () => {
    if (!document) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await dispatch(fetchChangeLog(document.id)).unwrap();
      setChangeLog(response.data.changes || []);
    } catch (error: any) {
      setError(error.message || 'Failed to load change log');
    } finally {
      setLoading(false);
    }
  };

  const getChangeIcon = (changeType: string) => {
    switch (changeType) {
      case 'created':
        return <Info color="primary" />;
      case 'updated':
        return <Edit color="warning" />;
      case 'version_created':
        return <History color="info" />;
      case 'approved':
        return <CheckCircle color="success" />;
      case 'file_uploaded':
        return <Timeline color="secondary" />;
      default:
        return <Info />;
    }
  };

  const getChangeColor = (changeType: string) => {
    switch (changeType) {
      case 'created':
        return 'primary';
      case 'updated':
        return 'warning';
      case 'version_created':
        return 'info';
      case 'approved':
        return 'success';
      case 'file_uploaded':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const handleClose = () => {
    setChangeLog([]);
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Timeline color="primary" />
            <Typography variant="h6">
              Change Log - {document?.title}
            </Typography>
          </Box>
          <IconButton onClick={handleClose}>
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

        {!loading && changeLog.length === 0 && (
          <Alert severity="info" sx={{ mb: 2 }}>
            No change history available for this document.
          </Alert>
        )}

        {!loading && changeLog.length > 0 && (
          <List>
            {changeLog.map((change, index) => (
              <React.Fragment key={change.id}>
                <ListItem alignItems="flex-start">
                  <ListItemIcon>
                    {getChangeIcon(change.change_type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="body1" fontWeight={500}>
                          {change.change_description}
                        </Typography>
                        <Chip
                          label={change.change_type.replace('_', ' ')}
                          size="small"
                          color={getChangeColor(change.change_type) as any}
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Person fontSize="small" color="action" />
                            <Typography variant="body2" color="text.secondary">
                              {change.changed_by}
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <AccessTime fontSize="small" color="action" />
                            <Typography variant="body2" color="text.secondary">
                              {formatDate(change.created_at)}
                            </Typography>
                          </Box>
                        </Box>
                        
                        {(change.old_version || change.new_version) && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                            <Label fontSize="small" color="action" />
                            <Typography variant="body2" color="text.secondary">
                              Version: {change.old_version || 'N/A'} → {change.new_version || 'N/A'}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
                {index < changeLog.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={handleClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentChangeLogDialog; 