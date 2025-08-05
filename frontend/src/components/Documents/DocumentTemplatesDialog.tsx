import React, { useState, useEffect } from 'react';
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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
} from '@mui/material';
import {
  Close,
  Description,
  Add,
  Edit,
  Delete,
  FileCopy,
  Category,
  Label,
  Person,
  AccessTime,
} from '@mui/icons-material';
import { documentsAPI } from '../../services/api';

interface DocumentTemplate {
  id: number;
  name: string;
  description: string;
  document_type: string;
  category: string;
  template_content?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

interface DocumentTemplatesDialogProps {
  open: boolean;
  onClose: () => void;
  onTemplateSelect?: (template: DocumentTemplate) => void;
}

const DocumentTemplatesDialog: React.FC<DocumentTemplatesDialogProps> = ({
  open,
  onClose,
  onTemplateSelect,
}) => {
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<DocumentTemplate[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<DocumentTemplate | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    document_type: '',
    category: '',
    template_content: '',
  });

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

  useEffect(() => {
    if (open) {
      loadTemplates();
    }
  }, [open]);

  const loadTemplates = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await documentsAPI.getDocumentTemplates();
      setTemplates(response.data.items || []);
    } catch (error: any) {
      setError(error.message || 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async () => {
    if (!formData.name || !formData.document_type || !formData.category) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await documentsAPI.createDocumentTemplate(formData);
      setFormData({
        name: '',
        description: '',
        document_type: '',
        category: '',
        template_content: '',
      });
      setShowCreateForm(false);
      loadTemplates();
    } catch (error: any) {
      setError(error.message || 'Failed to create template');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTemplate = async (templateId: number) => {
    if (!window.confirm('Are you sure you want to delete this template?')) {
      return;
    }

    try {
      await documentsAPI.deleteDocumentTemplate(templateId);
      loadTemplates();
    } catch (error: any) {
      setError(error.message || 'Failed to delete template');
    }
  };

  const handleTemplateSelect = (template: DocumentTemplate) => {
    if (onTemplateSelect) {
      onTemplateSelect(template);
      onClose();
    } else {
      setSelectedTemplate(template);
    }
  };

  const handleClose = () => {
    setTemplates([]);
    setError(null);
    setSelectedTemplate(null);
    setShowCreateForm(false);
    setFormData({
      name: '',
      description: '',
      document_type: '',
      category: '',
      template_content: '',
    });
    onClose();
  };

  const getDocumentTypeLabel = (type: string) => {
    return type.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  const getCategoryLabel = (category: string) => {
    return category.charAt(0).toUpperCase() + category.slice(1);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Description color="primary" />
            <Typography variant="h6">
              Document Templates
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<Add />}
              onClick={() => setShowCreateForm(true)}
            >
              New Template
            </Button>
            <IconButton onClick={handleClose}>
              <Close />
            </IconButton>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {showCreateForm ? (
          <Box>
            <Typography variant="h6" gutterBottom>
              Create New Template
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Template Name *"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  multiline
                  rows={3}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Document Type *</InputLabel>
                  <Select
                    value={formData.document_type}
                    onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
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
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  >
                    {categories.map((category) => (
                      <MenuItem key={category.value} value={category.value}>
                        {category.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Template Content"
                  value={formData.template_content}
                  onChange={(e) => setFormData({ ...formData, template_content: e.target.value })}
                  multiline
                  rows={6}
                  helperText="Optional template content or structure"
                />
              </Grid>
            </Grid>
          </Box>
        ) : (
          <List>
            {templates.map((template) => (
              <ListItem
                key={template.id}
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,
                  mb: 1,
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon>
                  <Description color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Typography variant="body1" fontWeight={500}>
                        {template.name}
                      </Typography>
                      <Chip
                        label={getDocumentTypeLabel(template.document_type)}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      <Chip
                        label={getCategoryLabel(template.category)}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {template.description}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Person fontSize="small" color="action" />
                          <Typography variant="caption" color="text.secondary">
                            {template.created_by}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <AccessTime fontSize="small" color="action" />
                          <Typography variant="caption" color="text.secondary">
                            {new Date(template.created_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  }
                />
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Tooltip title="Use Template">
                    <IconButton
                      size="small"
                      onClick={() => handleTemplateSelect(template)}
                    >
                      <FileCopy />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete Template">
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDeleteTemplate(template.id)}
                    >
                      <Delete />
                    </IconButton>
                  </Tooltip>
                </Box>
              </ListItem>
            ))}
            {templates.length === 0 && !loading && (
              <Alert severity="info">
                No document templates available. Create your first template to get started.
              </Alert>
            )}
          </List>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        {showCreateForm ? (
          <>
            <Button onClick={() => setShowCreateForm(false)}>
              Cancel
            </Button>
            <Button
              variant="contained"
              onClick={handleCreateTemplate}
              disabled={loading || !formData.name || !formData.document_type || !formData.category}
            >
              Create Template
            </Button>
          </>
        ) : (
          <Button onClick={handleClose}>
            Close
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default DocumentTemplatesDialog; 