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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  Chip,
  Divider,
} from '@mui/material';
import {
  Description,
  Close,
  CloudUpload,
  Save,
  Edit,
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

interface DocumentEditDialogProps {
  open: boolean;
  document: Document | null;
  onClose: () => void;
  onSuccess: () => void;
}

const DocumentEditDialog: React.FC<DocumentEditDialogProps> = ({
  open,
  document,
  onClose,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    document_type: '',
    category: '',
    department: '',
    product_line: '',
    keywords: '',
  });
  const [newFile, setNewFile] = useState<File | null>(null);

  useEffect(() => {
    if (document) {
      setFormData({
        title: document.title || '',
        description: document.description || '',
        document_type: document.document_type || '',
        category: document.category || '',
        department: document.department || '',
        product_line: document.product_line || '',
        keywords: document.keywords || '',
      });
    }
  }, [document]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setNewFile(file);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    if (!document) return;

    try {
      setLoading(true);
      setError(null);

      // First, update document metadata
      const metadataFormData = new FormData();
      
      // Add text fields
      Object.entries(formData).forEach(([key, value]) => {
        if (value) {
          metadataFormData.append(key, value);
        }
      });

      // Update document metadata
      await documentsAPI.updateDocument(document.id, metadataFormData);

      // If a new file is selected, upload it separately
      if (newFile) {
        const fileFormData = new FormData();
        fileFormData.append('file', newFile);
        
        // Upload new file (this will create a new version)
        await documentsAPI.uploadDocumentFile(document.id, fileFormData);
      }

      setSuccess('Document updated successfully!');
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1500);

    } catch (error: any) {
      setError(error.message || 'Failed to update document');
    } finally {
      setLoading(false);
    }
  };

  const getDocumentTypeLabel = (type: string) => {
    return type.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (!document) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Edit />
            <Typography variant="h6">Edit Document</Typography>
          </Box>
          <Button onClick={onClose} color="inherit">
            <Close />
          </Button>
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
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Document Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Document Information
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Document Title"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Document Number"
              value={document.document_number}
              disabled
              helperText="Document number cannot be changed"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Document Type</InputLabel>
              <Select
                value={formData.document_type}
                onChange={(e) => handleInputChange('document_type', e.target.value)}
                label="Document Type"
              >
                <MenuItem value="procedure">Procedure</MenuItem>
                <MenuItem value="work_instruction">Work Instruction</MenuItem>
                <MenuItem value="form">Form</MenuItem>
                <MenuItem value="policy">Policy</MenuItem>
                <MenuItem value="manual">Manual</MenuItem>
                <MenuItem value="plan">Plan</MenuItem>
                <MenuItem value="checklist">Checklist</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={formData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                label="Category"
              >
                <MenuItem value="quality">Quality</MenuItem>
                <MenuItem value="safety">Safety</MenuItem>
                <MenuItem value="production">Production</MenuItem>
                <MenuItem value="maintenance">Maintenance</MenuItem>
                <MenuItem value="hr">HR</MenuItem>
                <MenuItem value="finance">Finance</MenuItem>
                <MenuItem value="general">General</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Department"
              value={formData.department}
              onChange={(e) => handleInputChange('department', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Product Line"
              value={formData.product_line}
              onChange={(e) => handleInputChange('product_line', e.target.value)}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Keywords"
              value={formData.keywords}
              onChange={(e) => handleInputChange('keywords', e.target.value)}
              helperText="Separate keywords with commas"
            />
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
          </Grid>

          {/* Current File Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Current File Information
            </Typography>
          </Grid>

          {document.file_path && (
            <Grid item xs={12}>
              <Box sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid #ddd' }}>
                <Typography variant="subtitle2" gutterBottom>
                  Current File: {document.original_filename}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Size: {formatFileSize(document.file_size)} • Type: {document.file_type}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Version: {document.version}
                </Typography>
              </Box>
            </Grid>
          )}

          {/* New File Upload */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Upload New File (Optional)
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Upload a new file to create a new version of this document
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Box
              sx={{
                border: '2px dashed',
                borderColor: newFile ? '#2e7d32' : '#bdbdbd',
                borderRadius: '8px',
                p: 3,
                textAlign: 'center',
                bgcolor: newFile ? '#e8f5e8' : '#fafafa',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
              }}
              onClick={() => globalThis.document.getElementById('file-input')?.click()}
            >
              <input
                id="file-input"
                type="file"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.jpg,.jpeg,.png"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
              
              <CloudUpload sx={{ fontSize: 48, color: newFile ? 'success.main' : 'grey.500', mb: 2 }} />
              
              {newFile ? (
                <Box>
                  <Typography variant="h6" color="success.main" gutterBottom>
                    File Selected
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {newFile.name} ({(newFile.size / 1024 / 1024).toFixed(2)} MB)
                  </Typography>
                </Box>
              ) : (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Click to upload new file
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Supported formats: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG
                  </Typography>
                </Box>
              )}
            </Box>
          </Grid>

          {/* Document Status */}
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Document Status
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip
                label={`Status: ${document.status.replace('_', ' ')}`}
                color={document.status === 'approved' ? 'success' : 
                       document.status === 'under_review' ? 'warning' : 
                       document.status === 'draft' ? 'info' : 'default'}
                variant="filled"
              />
              <Chip
                label={`Version: ${document.version}`}
                variant="outlined"
              />
              <Chip
                label={`Type: ${getDocumentTypeLabel(document.document_type)}`}
                variant="outlined"
              />
            </Box>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading || !formData.title.trim()}
          startIcon={loading ? <LinearProgress /> : <Save />}
        >
          {loading ? 'Updating...' : 'Update Document'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentEditDialog;
