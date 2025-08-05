import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '@mui/material';
import {
  Close,
  Compare,
  Description,
  History,
  CheckCircle,
  Error,
  Add,
  Remove,
  Edit,
  Timeline,
  Person,
  AccessTime,
} from '@mui/icons-material';
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

interface DocumentComparisonDialogProps {
  open: boolean;
  document: any;
  onClose: () => void;
}

const DocumentComparisonDialog: React.FC<DocumentComparisonDialogProps> = ({
  open,
  document,
  onClose,
}) => {
  const [loading, setLoading] = useState(false);
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedVersion1, setSelectedVersion1] = useState<string>('');
  const [selectedVersion2, setSelectedVersion2] = useState<string>('');
  const [comparisonData, setComparisonData] = useState<any>(null);

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
      const response = await documentsAPI.getVersionHistory(document.id);
      const versionList = response.data.versions || [];
      setVersions(versionList);
      
      if (versionList.length >= 2) {
        setSelectedVersion1(versionList[0].version_number);
        setSelectedVersion2(versionList[1].version_number);
      }
    } catch (error: any) {
      setError(error.message || 'Failed to load versions');
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = async () => {
    if (!selectedVersion1 || !selectedVersion2) {
      setError('Please select two versions to compare');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Mock comparison data - in real implementation, this would come from API
      const mockComparison = {
        version1: {
          version: selectedVersion1,
          changes: [
            { type: 'added', content: 'New section on quality control procedures' },
            { type: 'modified', content: 'Updated temperature requirements' },
            { type: 'removed', content: 'Old manual process steps' },
          ],
          metadata: {
            created_by: 'John Smith',
            created_at: '2024-08-01T10:30:00Z',
            file_size: '2.3 MB',
          },
        },
        version2: {
          version: selectedVersion2,
          changes: [
            { type: 'added', content: 'Additional safety protocols' },
            { type: 'modified', content: 'Revised cleaning procedures' },
            { type: 'removed', content: 'Outdated equipment references' },
          ],
          metadata: {
            created_by: 'Sarah Johnson',
            created_at: '2024-08-05T14:20:00Z',
            file_size: '2.8 MB',
          },
        },
        summary: {
          total_changes: 6,
          additions: 2,
          modifications: 2,
          deletions: 2,
        },
      };

      setComparisonData(mockComparison);
    } catch (error: any) {
      setError(error.message || 'Failed to compare versions');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setVersions([]);
    setError(null);
    setSelectedVersion1('');
    setSelectedVersion2('');
    setComparisonData(null);
    onClose();
  };

  const getChangeIcon = (type: string) => {
    switch (type) {
      case 'added':
        return <Add color="success" />;
      case 'modified':
        return <Edit color="warning" />;
      case 'removed':
        return <Remove color="error" />;
      default:
        return <Description />;
    }
  };

  const getChangeColor = (type: string) => {
    switch (type) {
      case 'added':
        return 'success';
      case 'modified':
        return 'warning';
      case 'removed':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Compare color="primary" />
            <Typography variant="h6">
              Document Version Comparison - {document?.title}
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

        {versions.length > 0 && (
          <Box>
            {/* Version Selection */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Select Versions to Compare
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={5}>
                    <FormControl fullWidth>
                      <InputLabel>Version 1</InputLabel>
                      <Select
                        value={selectedVersion1}
                        onChange={(e) => setSelectedVersion1(e.target.value)}
                      >
                        {versions.map((version) => (
                          <MenuItem key={version.version_number} value={version.version_number}>
                            v{version.version_number} - {version.change_description}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={2} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Compare color="action" />
                  </Grid>
                  <Grid item xs={12} md={5}>
                    <FormControl fullWidth>
                      <InputLabel>Version 2</InputLabel>
                      <Select
                        value={selectedVersion2}
                        onChange={(e) => setSelectedVersion2(e.target.value)}
                      >
                        {versions.map((version) => (
                          <MenuItem key={version.version_number} value={version.version_number}>
                            v{version.version_number} - {version.change_description}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleCompare}
                    disabled={!selectedVersion1 || !selectedVersion2 || selectedVersion1 === selectedVersion2}
                    startIcon={<Compare />}
                  >
                    Compare Versions
                  </Button>
                </Box>
              </CardContent>
            </Card>

            {/* Comparison Results */}
            {comparisonData && (
              <Grid container spacing={3}>
                {/* Summary */}
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Comparison Summary
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={3}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="primary" fontWeight={700}>
                              {comparisonData.summary.total_changes}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Total Changes
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={3}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="success.main" fontWeight={700}>
                              {comparisonData.summary.additions}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Additions
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={3}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="warning.main" fontWeight={700}>
                              {comparisonData.summary.modifications}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Modifications
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={3}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="error.main" fontWeight={700}>
                              {comparisonData.summary.deletions}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Deletions
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Version Details */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title={`Version ${comparisonData.version1.version}`} />
                    <CardContent>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Created by: {comparisonData.version1.metadata.created_by}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Created: {formatDate(comparisonData.version1.metadata.created_at)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          File size: {comparisonData.version1.metadata.file_size}
                        </Typography>
                      </Box>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="subtitle2" gutterBottom>
                        Changes in this version:
                      </Typography>
                      <List dense>
                        {comparisonData.version1.changes.map((change: any, index: number) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              {getChangeIcon(change.type)}
                            </ListItemIcon>
                            <ListItemText
                              primary={change.content}
                              secondary={
                                <Chip
                                  label={change.type}
                                  size="small"
                                  color={getChangeColor(change.type) as any}
                                  variant="outlined"
                                />
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title={`Version ${comparisonData.version2.version}`} />
                    <CardContent>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Created by: {comparisonData.version2.metadata.created_by}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Created: {formatDate(comparisonData.version2.metadata.created_at)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          File size: {comparisonData.version2.metadata.file_size}
                        </Typography>
                      </Box>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="subtitle2" gutterBottom>
                        Changes in this version:
                      </Typography>
                      <List dense>
                        {comparisonData.version2.changes.map((change: any, index: number) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              {getChangeIcon(change.type)}
                            </ListItemIcon>
                            <ListItemText
                              primary={change.content}
                              secondary={
                                <Chip
                                  label={change.type}
                                  size="small"
                                  color={getChangeColor(change.type) as any}
                                  variant="outlined"
                                />
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}

            {versions.length === 0 && !loading && (
              <Alert severity="info">
                No versions available for comparison. Create multiple versions to compare documents.
              </Alert>
            )}
          </Box>
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

export default DocumentComparisonDialog; 