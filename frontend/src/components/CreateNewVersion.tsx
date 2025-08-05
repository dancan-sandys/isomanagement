import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
} from '@mui/material';
import {
  Add,
  CloudUpload,
  Info,
} from '@mui/icons-material';
import { documentsAPI } from '../services/api';

interface CreateNewVersionProps {
  documentId: number;
  currentVersion: string;
  onVersionCreated?: (newVersion: string) => void;
  onCancel?: () => void;
}

const CreateNewVersion: React.FC<CreateNewVersionProps> = ({
  documentId,
  currentVersion,
  onVersionCreated,
  onCancel,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [changeDescription, setChangeDescription] = useState('');
  const [changeReason, setChangeReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Helper function to format error messages
  const formatErrorMessage = (error: any): string => {
    if (typeof error === 'string') {
      return error;
    }
    
    if (error?.response?.data?.detail) {
      const detail = error.response.data.detail;
      
      // Handle array of validation errors
      if (Array.isArray(detail)) {
        return detail.map((err: any) => 
          typeof err === 'string' ? err : err.msg || 'Validation error'
        ).join(', ');
      }
      
      // Handle single validation error object
      if (typeof detail === 'object' && detail.msg) {
        return detail.msg;
      }
      
      // Handle string detail
      if (typeof detail === 'string') {
        return detail;
      }
    }
    
    return 'An unexpected error occurred';
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const calculateNextVersion = (currentVersion: string): string => {
    if (!currentVersion) return '1.0';
    
    const match = currentVersion.match(/^(\d+)\.(\d+)$/);
    if (match) {
      const major = parseInt(match[1]);
      const minor = parseInt(match[2]);
      return `${major}.${minor + 1}`;
    }
    
    return '1.0';
  };

  const handleSubmit = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    if (!changeDescription.trim()) {
      setError('Please provide a change description');
      return;
    }

    if (!changeReason.trim()) {
      setError('Please provide a change reason');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('change_description', changeDescription);
      formData.append('change_reason', changeReason);

      const response = await documentsAPI.createNewVersion(documentId, formData);

      if (response.success) {
        setSuccess(`New version ${response.data.new_version} created successfully!`);
        setFile(null);
        setChangeDescription('');
        setChangeReason('');
        
        if (onVersionCreated) {
          onVersionCreated(response.data.new_version);
        }
      } else {
        setError('Failed to create new version');
      }
    } catch (err: any) {
      setError(formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const nextVersion = calculateNextVersion(currentVersion);

  return (
    <Paper sx={{ p: 3 }}>
      <Box display="flex" alignItems="center" mb={3}>
        <Add sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">Create New Version</Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle2" color="primary" gutterBottom>
                Version Information
              </Typography>
              <Box display="flex" gap={2} alignItems="center">
                <Chip label={`Current: ${currentVersion}`} />
                <Typography variant="body2">→</Typography>
                <Chip label={`New: ${nextVersion}`} color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <div
            style={{
              border: '2px dashed',
              borderColor: file ? '#2e7d32' : '#bdbdbd',
              borderRadius: '8px',
              padding: '24px',
              textAlign: 'center',
              backgroundColor: file ? '#e8f5e8' : '#fafafa',
              transition: 'all 0.3s ease',
              cursor: 'pointer',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#1976d2';
              e.currentTarget.style.backgroundColor = '#e3f2fd';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = file ? '#2e7d32' : '#bdbdbd';
              e.currentTarget.style.backgroundColor = file ? '#e8f5e8' : '#fafafa';
            }}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.jpg,.jpeg,.png"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            
            <CloudUpload sx={{ fontSize: 48, color: file ? 'success.main' : 'grey.500', mb: 2 }} />
            
            {file ? (
              <Box>
                <Typography variant="h6" color="success.main" gutterBottom>
                  File Selected
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                </Typography>
              </Box>
            ) : (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Click to upload file
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Supported formats: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG
                </Typography>
              </Box>
            )}
          </div>
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Change Description"
            multiline
            rows={3}
            value={changeDescription}
            onChange={(e) => setChangeDescription(e.target.value)}
            placeholder="Describe what changes were made in this version..."
            helperText="Provide a clear description of the changes made"
            required
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Change Reason"
            multiline
            rows={2}
            value={changeReason}
            onChange={(e) => setChangeReason(e.target.value)}
            placeholder="Explain why these changes were necessary..."
            helperText="Provide the business reason for these changes"
            required
          />
        </Grid>

        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
          <Box display="flex" gap={2} justifyContent="flex-end">
            {onCancel && (
              <Button
                variant="outlined"
                onClick={onCancel}
                disabled={loading}
              >
                Cancel
              </Button>
            )}
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={loading || !file || !changeDescription.trim() || !changeReason.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : <Add />}
            >
              {loading ? 'Creating Version...' : 'Create New Version'}
            </Button>
          </Box>
        </Grid>
      </Grid>

      <Box mt={3}>
        <Alert severity="info" icon={<Info />}>
          <Typography variant="body2">
            <strong>Version Control Guidelines:</strong>
          </Typography>
          <Typography variant="body2" component="div" sx={{ mt: 1 }}>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              <li>Each new version should have a clear purpose and justification</li>
              <li>Document all significant changes for audit trail</li>
              <li>Ensure the new version addresses the identified need</li>
              <li>Version numbers follow the format: major.minor (e.g., 1.0, 1.1, 2.0)</li>
            </ul>
          </Typography>
        </Alert>
      </Box>
    </Paper>
  );
};

export default CreateNewVersion; 