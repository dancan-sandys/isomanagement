import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Alert,
  LinearProgress,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Autocomplete,
  Checkbox,
  FormControlLabel,
  FormGroup,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  Close,
  Info,
  CheckCircle,
  Error,
  Label,
  Category,
} from '@mui/icons-material';
import { AppDispatch } from '../../store';
import { createDocument } from '../../store/slices/documentSlice';
import { usersAPI, documentsAPI } from '../../services/api';
import { haccpAPI } from '../../services/api';
import { departmentsAPI } from '../../services/departmentsAPI';

interface Product {
  id: number;
  name: string;
  product_code: string;
  category: string;
}

interface DocumentUploadDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const DocumentUploadDialog: React.FC<DocumentUploadDialogProps> = ({
  open,
  onClose,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    document_number: '',
    description: '',
    document_type: '',
    category: '',
    department: '',
    product_line: '',
    applicable_products: [] as number[],
    keywords: '',
    file: null as File | null,
  });
  const [reviewerId, setReviewerId] = useState<number | null>(null);
  const [approverId, setApproverId] = useState<number | null>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [departmentId, setDepartmentId] = useState<string>('');

  const documentTypes = [
    { value: 'policy', label: 'Policy' },
    { value: 'procedure', label: 'Procedure' },
    { value: 'work_instruction', label: 'Work Instruction' },
    { value: 'form', label: 'Form' },
    { value: 'record', label: 'Record' },
    { value: 'manual', label: 'Manual' },
    { value: 'specification', label: 'Specification' },
    { value: 'plan', label: 'Plan' },
    { value: 'checklist', label: 'Checklist' },
  ];

  const categories = [
    { value: 'haccp', label: 'HACCP' },
    { value: 'prp', label: 'PRP' },
    { value: 'training', label: 'Training' },
    { value: 'audit', label: 'Audit' },
    { value: 'maintenance', label: 'Maintenance' },
    { value: 'supplier', label: 'Supplier' },
    { value: 'quality', label: 'Quality' },
    { value: 'safety', label: 'Safety' },
    { value: 'general', label: 'General' },
  ];

  // Departments will be loaded dynamically
  const productLines = [
    'Milk Processing',
    'Yogurt Production',
    'Cheese Manufacturing',
    'Butter Production',
    'Ice Cream',
    'Cream Processing',
    'Whey Processing',
    'Packaging',
    'Quality Control',
    'Maintenance',
  ];

  const allowedFileTypes = [
    '.pdf',
    '.doc',
    '.docx',
    '.xls',
    '.xlsx',
    '.txt',
    '.jpg',
    '.jpeg',
    '.png',
  ];

  useEffect(() => {
    if (open) {
      loadProducts();
      loadUsers();
      loadDepartments();
    }
  }, [open]);

  const loadProducts = async () => {
    setLoadingProducts(true);
    try {
      const response = await haccpAPI.getProducts();
      setProducts(response.data.items || []);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoadingProducts(false);
    }
  };

  const loadUsers = async () => {
    try {
      const resp: any = await documentsAPI.getApprovalUsers();
      setUsers(resp?.data || []);
    } catch (e) {
      console.error('Failed to load approval users:', e);
      setUsers([]);
    }
  };

  const loadDepartments = async () => {
    try {
      const res: any = await departmentsAPI.list({ size: 1000 });
      setDepartments(res?.items || res?.data?.items || []);
    } catch (e) {
      console.error('Failed to load departments:', e);
      setDepartments([]);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleProductChange = (event: React.SyntheticEvent, value: Product[]) => {
    const productIds = value.map(product => product.id);
    setFormData(prev => ({
      ...prev,
      applicable_products: productIds,
    }));
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      if (!allowedFileTypes.includes(fileExtension)) {
        setError(`File type ${fileExtension} not allowed. Allowed types: ${allowedFileTypes.join(', ')}`);
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      setError(null);
      setFormData(prev => ({
        ...prev,
        file,
      }));
    }
  };

  const handleSubmit = async () => {
    if (!formData.title || !formData.document_number || !formData.document_type || !formData.category) {
      setError('Please fill in all required fields');
      return;
    }

    if (!formData.file) {
      setError('Please select a file to upload');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const submitFormData = new FormData();
      submitFormData.append('title', formData.title);
      submitFormData.append('document_number', formData.document_number);
      submitFormData.append('description', formData.description);
      submitFormData.append('document_type', formData.document_type);
      submitFormData.append('category', formData.category);
      if (departmentId) {
        const match = departments.find((d) => String(d.id) === String(departmentId));
        submitFormData.append('department', (match && match.name) || '');
      } else {
        submitFormData.append('department', '');
      }
      submitFormData.append('product_line', formData.product_line);
      submitFormData.append('keywords', formData.keywords);
      
      // Add applicable products as JSON string
      if (formData.applicable_products.length > 0) {
        submitFormData.append('applicable_products', JSON.stringify(formData.applicable_products));
      }
      
      submitFormData.append('file', formData.file);

      const created: any = await dispatch(createDocument(submitFormData)).unwrap();
      const newDocId = created?.data?.id || created?.id;

      // If reviewer/approver provided, immediately submit approval chain
      const approvers: Array<{ approver_id: number; approval_order: number }> = [];
      if (reviewerId) approvers.push({ approver_id: reviewerId, approval_order: 1 });
      if (approverId) approvers.push({ approver_id: approverId, approval_order: approverId === reviewerId ? 2 : 2 });
      if (newDocId && approvers.length > 0) {
        await documentsAPI.submitApprovalFlow(newDocId, approvers);
      }
      
      setSuccess(true);
      setTimeout(() => {
        handleClose();
        onSuccess();
      }, 2000);
    } catch (error: any) {
      setError(error.message || 'Failed to create document');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setFormData({
        title: '',
        document_number: '',
        description: '',
        document_type: '',
        category: '',
        department: '',
        product_line: '',
        applicable_products: [],
        keywords: '',
        file: null,
      });
      setError(null);
      setSuccess(false);
      onClose();
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const selectedProducts = products.filter(product => 
    formData.applicable_products.includes(product.id)
  );

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CloudUpload color="primary" />
            <Typography variant="h6">Upload New Document</Typography>
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
            Document created successfully!
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
              label="Document Title *"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              disabled={loading}
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Document Number *"
              value={formData.document_number}
              onChange={(e) => handleInputChange('document_number', e.target.value)}
              disabled={loading}
              required
              helperText="Unique identifier for the document"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              disabled={loading}
              multiline
              rows={3}
              helperText="Brief description of the document"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Document Type *</InputLabel>
              <Select
                value={formData.document_type}
                onChange={(e) => handleInputChange('document_type', e.target.value)}
                disabled={loading}
              >
                {documentTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Category *</InputLabel>
              <Select
                value={formData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                disabled={loading}
              >
                {categories.map((category) => (
                  <MenuItem key={category.value} value={category.value}>
                    {category.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Department</InputLabel>
              <Select
                value={departmentId}
                onChange={(e) => setDepartmentId(String(e.target.value))}
                disabled={loading}
                label="Department"
              >
                <MenuItem value="">Select Department</MenuItem>
                {departments.map((d) => (
                  <MenuItem key={d.id} value={String(d.id)}>
                    {d.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Product Line</InputLabel>
              <Select
                value={formData.product_line}
                onChange={(e) => handleInputChange('product_line', e.target.value)}
                disabled={loading}
              >
                <MenuItem value="">Select Product Line</MenuItem>
                {productLines.map((line) => (
                  <MenuItem key={line} value={line}>
                    {line}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Product Linking */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Product Association
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Autocomplete
              multiple
              options={products}
              getOptionLabel={(option) => `${option.name} (${option.product_code})`}
              value={selectedProducts}
              onChange={handleProductChange}
              loading={loadingProducts}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Applicable Products"
                  placeholder="Select products this document applies to..."
                  helperText="Select products that this document is applicable to"
                />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    {...getTagProps({ index })}
                    key={option.id}
                    label={`${option.name} (${option.product_code})`}
                    size="small"
                  />
                ))
              }
              renderOption={(props, option) => (
                <Box component="li" {...props}>
                  <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                    <Typography variant="body2" fontWeight={500}>
                      {option.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {option.product_code} • {option.category}
                    </Typography>
                  </Box>
                </Box>
              )}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Keywords"
              value={formData.keywords}
              onChange={(e) => handleInputChange('keywords', e.target.value)}
              disabled={loading}
              helperText="Keywords for search (comma-separated)"
            />
          </Grid>

          {/* File Upload */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              File Upload
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Box
              sx={{
                border: '2px dashed',
                borderColor: formData.file ? 'success.main' : 'grey.300',
                borderRadius: 2,
                p: 3,
                textAlign: 'center',
                bgcolor: formData.file ? 'success.50' : 'grey.50',
                transition: 'all 0.3s',
                '&:hover': {
                  borderColor: 'primary.main',
                  bgcolor: 'primary.50',
                },
              }}
            >
              <input
                type="file"
                accept={allowedFileTypes.join(',')}
                onChange={handleFileChange}
                style={{ display: 'none' }}
                id="file-upload"
                disabled={loading}
              />
              <label htmlFor="file-upload">
                <Box sx={{ cursor: 'pointer' }}>
                  <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    {formData.file ? 'File Selected' : 'Click to upload file'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Supported formats: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Maximum file size: 10MB
                  </Typography>
                </Box>
              </label>
            </Box>
          </Grid>

          {formData.file && (
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, bgcolor: 'success.50', borderRadius: 1 }}>
                <Description color="success" />
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="body2" fontWeight={600}>
                    {formData.file.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatFileSize(formData.file.size)}
                  </Typography>
                </Box>
                <Chip label="Ready" color="success" size="small" />
              </Box>
            </Grid>
          )}

          {/* Information */}
          <Grid item xs={12}>
            <Alert severity="info" icon={<Info />}>
              <Typography variant="body2">
                <strong>Note:</strong> The document will be created in draft status. 
                It will need to be reviewed and approved through the workflow process before becoming active.
              </Typography>
            </Alert>
          </Grid>

          {/* Initial Workflow Assignment */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Approval Workflow (Creator → Reviewer → Approver)
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth size="small">
              <InputLabel>Reviewer (Next Step)</InputLabel>
              <Select value={reviewerId || ''} onChange={(e) => setReviewerId(Number(e.target.value) || null)}>
                <MenuItem value="">Select Reviewer</MenuItem>
                {users.map((u) => (
                  <MenuItem key={u.id} value={u.id}>{u.full_name || u.username} ({u.email})</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth size="small">
              <InputLabel>Approver (Final)</InputLabel>
              <Select value={approverId || ''} onChange={(e) => setApproverId(Number(e.target.value) || null)}>
                <MenuItem value="">Select Approver</MenuItem>
                {users.map((u) => (
                  <MenuItem key={u.id} value={u.id}>{u.full_name || u.username} ({u.email})</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading || !formData.title || !formData.document_number || !formData.document_type || !formData.category || !formData.file}
          startIcon={<CloudUpload />}
        >
          {loading ? 'Creating...' : 'Create Document'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentUploadDialog; 