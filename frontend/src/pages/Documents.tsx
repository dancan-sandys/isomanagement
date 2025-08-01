import React, { useState, useEffect } from 'react';
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
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Download,
  Search,
  FilterList,
} from '@mui/icons-material';
import { documentsAPI } from '../services/api';

interface Document {
  id: number;
  title: string;
  document_number: string;
  category: string;
  status: string;
  version: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  
  // Dialog states
  const [openDialog, setOpenDialog] = useState(false);
  const [editingDocument, setEditingDocument] = useState<Document | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    document_number: '',
    category: '',
    description: '',
  });

  useEffect(() => {
    fetchDocuments();
  }, [page, rowsPerPage, searchTerm, filterCategory, filterStatus]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Mock data for now since backend endpoints aren't implemented
      const mockDocuments: Document[] = [
        {
          id: 1,
          title: 'Food Safety Policy',
          document_number: 'FSP-001',
          category: 'Policy',
          status: 'Active',
          version: '1.0',
          created_by: 'John Doe',
          created_at: '2024-01-15T10:30:00Z',
          updated_at: '2024-01-15T10:30:00Z',
        },
        {
          id: 2,
          title: 'HACCP Plan - Milk Processing',
          document_number: 'HACCP-001',
          category: 'HACCP',
          status: 'Draft',
          version: '2.1',
          created_by: 'Jane Smith',
          created_at: '2024-01-10T14:20:00Z',
          updated_at: '2024-01-12T09:15:00Z',
        },
        {
          id: 3,
          title: 'PRP Program - Cleaning and Sanitation',
          document_number: 'PRP-001',
          category: 'PRP',
          status: 'Active',
          version: '1.2',
          created_by: 'Mike Johnson',
          created_at: '2024-01-08T11:45:00Z',
          updated_at: '2024-01-14T16:30:00Z',
        },
        {
          id: 4,
          title: 'Supplier Evaluation Procedure',
          document_number: 'SUP-001',
          category: 'Procedure',
          status: 'Under Review',
          version: '1.0',
          created_by: 'Sarah Wilson',
          created_at: '2024-01-05T08:15:00Z',
          updated_at: '2024-01-13T13:45:00Z',
        },
      ];
      
      setDocuments(mockDocuments);
    } catch (err) {
      setError('Failed to load documents');
      console.error('Documents error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (document?: Document) => {
    if (document) {
      setEditingDocument(document);
      setFormData({
        title: document.title,
        document_number: document.document_number,
        category: document.category,
        description: '',
      });
    } else {
      setEditingDocument(null);
      setFormData({
        title: '',
        document_number: '',
        category: '',
        description: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingDocument(null);
    setFormData({
      title: '',
      document_number: '',
      category: '',
      description: '',
    });
  };

  const handleSubmit = async () => {
    try {
      if (editingDocument) {
        // Update document
        console.log('Updating document:', editingDocument.id, formData);
      } else {
        // Create document
        console.log('Creating document:', formData);
      }
      handleCloseDialog();
      fetchDocuments();
    } catch (err) {
      console.error('Document operation error:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        console.log('Deleting document:', id);
        fetchDocuments();
      } catch (err) {
        console.error('Delete error:', err);
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active':
        return 'success';
      case 'Draft':
        return 'warning';
      case 'Under Review':
        return 'info';
      case 'Archived':
        return 'default';
      default:
        return 'default';
    }
  };

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.document_number.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !filterCategory || doc.category === filterCategory;
    const matchesStatus = !filterStatus || doc.status === filterStatus;
    
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const paginatedDocuments = filteredDocuments.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

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

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

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
              <MenuItem value="Policy">Policy</MenuItem>
              <MenuItem value="Procedure">Procedure</MenuItem>
              <MenuItem value="HACCP">HACCP</MenuItem>
              <MenuItem value="PRP">PRP</MenuItem>
              <MenuItem value="Form">Form</MenuItem>
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
              <MenuItem value="Active">Active</MenuItem>
              <MenuItem value="Draft">Draft</MenuItem>
              <MenuItem value="Under Review">Under Review</MenuItem>
              <MenuItem value="Archived">Archived</MenuItem>
            </Select>
          </FormControl>
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
                <TableCell>Created By</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedDocuments.map((document) => (
                <TableRow key={document.id} hover>
                  <TableCell>{document.document_number}</TableCell>
                  <TableCell>{document.title}</TableCell>
                  <TableCell>{document.category}</TableCell>
                  <TableCell>
                    <Chip
                      label={document.status}
                      color={getStatusColor(document.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{document.version}</TableCell>
                  <TableCell>{document.created_by}</TableCell>
                  <TableCell>
                    {new Date(document.updated_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="View">
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton size="small" onClick={() => handleOpenDialog(document)}>
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Download">
                      <IconButton size="small">
                        <Download />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton size="small" onClick={() => handleDelete(document.id)}>
                        <Delete />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredDocuments.length}
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
          <Box display="flex" flexDirection="column" gap={2} pt={1}>
            <TextField
              label="Document Title"
              fullWidth
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            />
            <TextField
              label="Document Number"
              fullWidth
              value={formData.document_number}
              onChange={(e) => setFormData({ ...formData, document_number: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={formData.category}
                label="Category"
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              >
                <MenuItem value="Policy">Policy</MenuItem>
                <MenuItem value="Procedure">Procedure</MenuItem>
                <MenuItem value="HACCP">HACCP</MenuItem>
                <MenuItem value="PRP">PRP</MenuItem>
                <MenuItem value="Form">Form</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingDocument ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Documents; 