import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
} from '@mui/material';
import {
  Description,
  Download,
  Person,
  Info,
} from '@mui/icons-material';

interface Document {
  id: number;
  document_number: string;
  title: string;
  description?: string;
  document_type?: string;
  category?: string;
  status?: string;
  version: string;
  file_path?: string;
  file_size?: number;
  file_type?: string;
  original_filename?: string;
  department?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

interface DocumentViewerProps {
  document: Document;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ document }) => {
  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'draft':
        return 'default';
      case 'under_review':
        return 'warning';
      case 'obsolete':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Document Header */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Description sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h5" component="h2">
                  {document.title}
                </Typography>
              </Box>
              
              <Typography variant="body1" color="text.secondary" paragraph>
                {document.description || 'No description available'}
              </Typography>

              <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
                <Chip
                  label={`Document #: ${document.document_number}`}
                  variant="outlined"
                  size="small"
                />
                <Chip
                  label={`Version: ${document.version}`}
                  color="primary"
                  size="small"
                />
                <Chip
                  label={document.status || 'Unknown'}
                  color={getStatusColor(document.status) as any}
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Document Details */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Info sx={{ mr: 1, verticalAlign: 'middle' }} />
                Document Information
              </Typography>
              
              <Box display="flex" flexDirection="column" gap={2}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Document Type
                  </Typography>
                  <Typography variant="body1">
                    {document.document_type || 'Not specified'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Category
                  </Typography>
                  <Typography variant="body1">
                    {document.category || 'Not specified'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Department
                  </Typography>
                  <Typography variant="body1">
                    {document.department || 'Not specified'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* File Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Download sx={{ mr: 1, verticalAlign: 'middle' }} />
                File Information
              </Typography>
              
              {document.file_path ? (
                <Box display="flex" flexDirection="column" gap={2}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      File Name
                    </Typography>
                    <Typography variant="body1" noWrap>
                      {document.original_filename || 'Unknown'}
                    </Typography>
                  </Box>
                  
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      File Size
                    </Typography>
                    <Typography variant="body1">
                      {formatFileSize(document.file_size)}
                    </Typography>
                  </Box>
                  
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      File Type
                    </Typography>
                    <Typography variant="body1">
                      {document.file_type || 'Unknown'}
                    </Typography>
                  </Box>
                  
                  <Button
                    variant="contained"
                    startIcon={<Download />}
                    fullWidth
                  >
                    Download File
                  </Button>
                </Box>
              ) : (
                <Typography variant="body1" color="text.secondary">
                  No file attached to this document
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Metadata */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Person sx={{ mr: 1, verticalAlign: 'middle' }} />
                Document Metadata
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Created By
                    </Typography>
                    <Typography variant="body1">
                      {document.created_by}
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Created Date
                    </Typography>
                    <Typography variant="body1">
                      {formatDate(document.created_at)}
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Last Modified
                    </Typography>
                    <Typography variant="body1">
                      {formatDate(document.updated_at)}
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Document ID
                    </Typography>
                    <Typography variant="body1">
                      {document.id}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DocumentViewer; 