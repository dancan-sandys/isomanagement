import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Skeleton,
  Tooltip,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Download,
  Search,
  Refresh,
  Description,
  CloudUpload,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { documentsAPI } from '../services/api';
import DocumentViewer from '../components/DocumentViewer';

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

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  
  // Dialog states
  const [openDialog, setOpenDialog] = useState(false);
  const [editingDocument, setEditingDocument] = useState<Document | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    document_number: '',
    description: '',
    document_type: '',
    category: '',
    department: '',
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await documentsAPI.getDocuments({
        page: page + 1,
        size: rowsPerPage,
        search: searchTerm || undefined,
        category: filterCategory || undefined,
        status: filterStatus || undefined,
      });
      
      if (response.success) {
        setDocuments(response.data.items);
        setTotal(response.data.total);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load documents');
      console.error('Documents error:', err);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, searchTerm, filterCategory, filterStatus]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleOpenDialog = (document?: Document) => {
    if (document) {
      setEditingDocument(document);
      setFormData({
        title: document.title,
        document_number: document.document_number,
        description: document.description || '',
        document_type: document.document_type || '',
        category: document.category || '',
        department: document.department || '',
      });
    } else {
      setEditingDocument(null);
      setFormData({
        title: '',
        document_number: '',
        description: '',
        document_type: '',
        category: '',
        department: '',
      });
    }
    setSelectedFile(null);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingDocument(null);
    setFormData({
      title: '',
      document_number: '',
      description: '',
      document_type: '',
      category: '',
      department: '',
    });
    setSelectedFile(null);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleSubmit = async () => {
    try {
      setUploading(true);
      
      const formDataToSend = new FormData();
      formDataToSend.append('title', formData.title);
      formDataToSend.append('document_number', formData.document_number);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('document_type', formData.document_type);
      formDataToSend.append('category', formData.category);
      formDataToSend.append('department', formData.department);
      
      if (selectedFile) {
        formDataToSend.append('file', selectedFile);
      }
      
      if (editingDocument) {
        await documentsAPI.updateDocument(editingDocument.id, formDataToSend);
        setSuccess('Document updated successfully');
      } else {
        await documentsAPI.createDocument(formDataToSend);
        setSuccess('Document created successfully');
      }
      
      handleCloseDialog();
      fetchDocuments();
    } catch (err: any) {
      setError(err.message || 'Failed to save document');
      console.error('Document operation error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await documentsAPI.deleteDocument(id);
        setSuccess('Document deleted successfully');
        fetchDocuments();
      } catch (err: any) {
        setError(err.message || 'Failed to delete document');
        console.error('Delete error:', err);
      }
    }
  };

  const handleView = (document: Document) => {
    setSelectedDocument(document);
    setViewerOpen(true);
  };

  const handleDownload = async (id: number) => {
    try {
      const response = await documentsAPI.downloadDocument(id);
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document_${id}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message || 'Failed to download document');
      console.error('Download error:', err);
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return 'success';
      case 'draft':
        return 'warning';
      case 'under_review':
        return 'info';
      case 'archived':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleCloseSnackbar = () => {
    setError(null);
    setSuccess(null);
  };

  return (
    <Box p={3}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Document Management</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
        >
          New Document
        </Button>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={handleCloseSnackbar}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={handleCloseSnackbar}>
          {success}
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Documents
                  </Typography>
                  <Typography variant="h4">
                    {total}
                  </Typography>
                </Box>
                <Description color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Approved
                  </Typography>
                  <Typography variant="h4">
                    {documents.filter(d => d.status === 'approved').length}
                  </Typography>
                </Box>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Draft
                  </Typography>
                  <Typography variant="h4">
                    {documents.filter(d => d.status === 'draft').length}
                  </Typography>
                </Box>
                <Error color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Under Review
                  </Typography>
                  <Typography variant="h4">
                    {documents.filter(d => d.status === 'under_review').length}
                  </Typography>
                </Box>
                <Error color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
          <TextField
            label="Search documents"
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ minWidth: 200 }}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
            }}
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={filterCategory}
              label="Category"
              onChange={(e) => setFilterCategory(e.target.value)}
            >
              <MenuItem value="">All Categories</MenuItem>
              <MenuItem value="general">General</MenuItem>
              <MenuItem value="haccp">HACCP</MenuItem>
              <MenuItem value="prp">PRP</MenuItem>
              <MenuItem value="supplier">Supplier</MenuItem>
              <MenuItem value="quality">Quality</MenuItem>
              <MenuItem value="safety">Safety</MenuItem>
              <MenuItem value="training">Training</MenuItem>
              <MenuItem value="audit">Audit</MenuItem>
              <MenuItem value="maintenance">Maintenance</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filterStatus}
              label="Status"
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <MenuItem value="">All Statuses</MenuItem>
              <MenuItem value="approved">Approved</MenuItem>
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="under_review">Under Review</MenuItem>
              <MenuItem value="archived">Archived</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchDocuments}
            size="small"
          >
            Refresh
          </Button>
        </Box>
      </Paper>

      {/* Documents Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Document Number</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>File</TableCell>
                <TableCell>Created By</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                Array.from({ length: rowsPerPage }).map((_, index) => (
                  <TableRow key={index}>
                    <TableCell><Skeleton variant="text" width="80%" /></TableCell>
                    <TableCell><Skeleton variant="text" width="90%" /></TableCell>
                    <TableCell><Skeleton variant="text" width="60%" /></TableCell>
                    <TableCell><Skeleton variant="rectangular" width={60} height={24} sx={{ borderRadius: 1 }} /></TableCell>
                    <TableCell><Skeleton variant="text" width="40%" /></TableCell>
                    <TableCell><Skeleton variant="text" width="70%" /></TableCell>
                    <TableCell><Skeleton variant="text" width="60%" /></TableCell>
                    <TableCell><Skeleton variant="circular" width={32} height={32} /></TableCell>
                  </TableRow>
                ))
              ) : documents.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                      No documents found
                    </Typography>
                    <Button
                      variant="outlined"
                      startIcon={<Add />}
                      onClick={() => handleOpenDialog()}
                      sx={{ mt: 2 }}
                    >
                      Create First Document
                    </Button>
                  </TableCell>
                </TableRow>
              ) : (
                documents.map((document) => (
                  <TableRow key={document.id} hover>
                    <TableCell>{document.document_number}</TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {document.title}
                        </Typography>
                        {document.description && (
                          <Typography variant="caption" color="text.secondary">
                            {document.description.substring(0, 50)}...
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>{document.category}</TableCell>
                    <TableCell>
                      <Chip
                        label={document.status || 'Unknown'}
                        color={getStatusColor(document.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{document.version}</TableCell>
                    <TableCell>
                      {document.file_path ? (
                        <Box display="flex" alignItems="center" gap={1}>
                          <Description color="primary" fontSize="small" />
                          <Typography variant="caption">
                            {document.original_filename}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            ({formatFileSize(document.file_size)})
                          </Typography>
                        </Box>
                      ) : (
                        <Typography variant="caption" color="text.secondary">
                          No file
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{document.created_by}</TableCell>
                    <TableCell>
                      {new Date(document.updated_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell align="center">
                      {document.file_path && (
                        <Tooltip title="View">
                          <IconButton size="small" onClick={() => handleView(document)}>
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      )}
                      <Tooltip title="Edit">
                        <IconButton size="small" onClick={() => handleOpenDialog(document)}>
                          <Edit />
                        </IconButton>
                      </Tooltip>
                      {document.file_path && (
                        <Tooltip title="Download">
                          <IconButton size="small" onClick={() => handleDownload(document.id)}>
                            <Download />
                          </IconButton>
                        </Tooltip>
                      )}
                      <Tooltip title="Delete">
                        <IconButton size="small" onClick={() => handleDelete(document.id)}>
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={total}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Paper>

      {/* Document Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingDocument ? 'Edit Document' : 'New Document'}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={3} pt={1}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Document Title"
                  fullWidth
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Document Number"
                  fullWidth
                  value={formData.document_number}
                  onChange={(e) => setFormData({ ...formData, document_number: e.target.value })}
                  required
                />
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Document Type</InputLabel>
                  <Select
                    value={formData.document_type}
                    label="Document Type"
                    onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
                  >
                    <MenuItem value="policy">Policy</MenuItem>
                    <MenuItem value="procedure">Procedure</MenuItem>
                    <MenuItem value="work_instruction">Work Instruction</MenuItem>
                    <MenuItem value="form">Form</MenuItem>
                    <MenuItem value="record">Record</MenuItem>
                    <MenuItem value="manual">Manual</MenuItem>
                    <MenuItem value="specification">Specification</MenuItem>
                    <MenuItem value="plan">Plan</MenuItem>
                    <MenuItem value="checklist">Checklist</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={formData.category}
                    label="Category"
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  >
                    <MenuItem value="general">General</MenuItem>
                    <MenuItem value="haccp">HACCP</MenuItem>
                    <MenuItem value="prp">PRP</MenuItem>
                    <MenuItem value="supplier">Supplier</MenuItem>
                    <MenuItem value="quality">Quality</MenuItem>
                    <MenuItem value="safety">Safety</MenuItem>
                    <MenuItem value="training">Training</MenuItem>
                    <MenuItem value="audit">Audit</MenuItem>
                    <MenuItem value="maintenance">Maintenance</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <TextField
              label="Department"
              fullWidth
              value={formData.department}
              onChange={(e) => setFormData({ ...formData, department: e.target.value })}
            />

            <TextField
              label="Description"
              fullWidth
              multiline
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />

            {/* File Upload Section */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Document File
              </Typography>
              
              {selectedFile ? (
                <Box display="flex" alignItems="center" gap={2} p={2} border={1} borderColor="primary.main" borderRadius={1}>
                  <Description color="primary" />
                  <Box flex={1}>
                    <Typography variant="body2" fontWeight="medium">
                      {selectedFile.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {formatFileSize(selectedFile.size)}
                    </Typography>
                  </Box>
                  <Button
                    size="small"
                    onClick={() => setSelectedFile(null)}
                    color="error"
                  >
                    Remove
                  </Button>
                </Box>
              ) : (
                <Paper
                  variant="outlined"
                  sx={{
                    border: '2px dashed',
                    borderColor: 'grey.300',
                    borderRadius: 2,
                    p: 3,
                    textAlign: 'center',
                    cursor: 'pointer',
                    '&:hover': { borderColor: 'primary.main' }
                  }}
                  onClick={() => document.getElementById('file-input')?.click()}
                >
                  <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Upload Document File
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Click to select a file or drag and drop
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                    Supported formats: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG
                  </Typography>
                </Paper>
              )}
              
              <input
                id="file-input"
                type="file"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.jpg,.jpeg,.png"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={uploading}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            disabled={uploading || !formData.title || !formData.document_number || !formData.document_type || !formData.category}
          >
            {uploading ? 'Saving...' : (editingDocument ? 'Update' : 'Create')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Document Viewer */}
      {selectedDocument && (
        <DocumentViewer
          open={viewerOpen}
          onClose={() => {
            setViewerOpen(false);
            setSelectedDocument(null);
          }}
          documentId={selectedDocument.id}
          documentTitle={selectedDocument.title}
        />
      )}
    </Box>
  );
};

export default Documents; 