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
  Autocomplete,
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
  History,
  Approval,
} from '@mui/icons-material';
import { documentsAPI, usersAPI } from '../../services/api';
import { List as MUIList, ListItem as MUIListItem } from '@mui/material';

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
  const [showVersions, setShowVersions] = useState<{ open: boolean; template: DocumentTemplate | null; versions: any[]; loading: boolean }>({ open: false, template: null, versions: [], loading: false });
  const [showApprovals, setShowApprovals] = useState<{ open: boolean; template: DocumentTemplate | null; steps: Array<{ approver_id: number; approval_order: number }> }>({ open: false, template: null, steps: [{ approver_id: 0, approval_order: 1 }] });
  const [userSearch, setUserSearch] = useState('');
  const [userOptions, setUserOptions] = useState<Array<{ id: number; username: string; full_name?: string }>>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
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

  const handleViewTemplateVersions = async (template: DocumentTemplate) => {
    setShowVersions({ open: true, template, versions: [], loading: true });
    try {
      const resp = await documentsAPI.getTemplateVersions(template.id);
      setShowVersions(prev => ({ ...prev, versions: resp.data?.versions || resp.versions || [], loading: false }));
    } catch (e) {
      setShowVersions(prev => ({ ...prev, loading: false }));
    }
  };

  const handleCreateTemplateVersion = async (template: DocumentTemplate) => {
    const change_description = window.prompt('Enter change description') || '';
    if (!change_description) return;
    const change_reason = window.prompt('Enter change reason') || '';
    try {
      await documentsAPI.createTemplateVersion(template.id, { change_description, change_reason });
      handleViewTemplateVersions(template);
    } catch (e) {
      console.error('Create template version failed', e);
    }
  };

  const handleOpenTemplateApproval = (template: DocumentTemplate) => {
    setShowApprovals({ open: true, template, steps: [{ approver_id: 0, approval_order: 1 }] });
  };

  const handleSubmitTemplateApproval = async () => {
    if (!showApprovals.template) return;
    const steps = showApprovals.steps.filter(s => s.approver_id);
    if (steps.length === 0) return;
    try {
      await documentsAPI.submitTemplateApprovalFlow(showApprovals.template.id, steps);
      setShowApprovals({ open: false, template: null, steps: [{ approver_id: 0, approval_order: 1 }] });
    } catch (e) {
      console.error('Submit template approval failed', e);
    }
  };

  useEffect(() => {
    let active = true;
    const t = setTimeout(async () => {
      try {
        setLoadingUsers(true);
        const resp: any = await usersAPI.getUsers({ page: 1, size: 10, search: userSearch });
        const items = resp?.data?.items || resp?.items || [];
        if (active) setUserOptions(items.map((u: any) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch (e) {
        if (active) setUserOptions([]);
      } finally {
        if (active) setLoadingUsers(false);
      }
    }, 300);
    return () => { active = false; clearTimeout(t); };
  }, [userSearch]);

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
                  <Tooltip title="Versions">
                    <IconButton size="small" onClick={() => handleViewTemplateVersions(template)}>
                      <History />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="New Template Version">
                    <IconButton size="small" onClick={() => handleCreateTemplateVersion(template)}>
                      <Add />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Submit for Approval">
                    <IconButton size="small" onClick={() => handleOpenTemplateApproval(template)}>
                      <Approval />
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

      {/* Template Versions Modal (inline simple view) */}
      <Dialog open={showVersions.open} onClose={() => setShowVersions({ open: false, template: null, versions: [], loading: false })} maxWidth="sm" fullWidth>
        <DialogTitle>Template Versions - {showVersions.template?.name}</DialogTitle>
        <DialogContent>
          {showVersions.loading && <LinearProgress sx={{ mb: 2 }} />}
          {!showVersions.loading && showVersions.versions.length === 0 && (
            <Alert severity="info">No versions found for this template.</Alert>
          )}
          <List>
            {showVersions.versions.map((v: any) => (
              <ListItem key={v.id} divider>
                <ListItemText
                  primary={`v${v.version_number} ${v.approved_by ? '(Approved)' : ''}`}
                  secondary={<>
                    <Typography variant="caption">{v.change_description}</Typography><br/>
                    <Typography variant="caption">{v.created_at && new Date(v.created_at).toLocaleString()}</Typography>
                  </>}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowVersions({ open: false, template: null, versions: [], loading: false })}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Template Approval Steps Modal */}
      <Dialog open={showApprovals.open} onClose={() => setShowApprovals({ open: false, template: null, steps: [{ approver_id: 0, approval_order: 1 }] })} maxWidth="sm" fullWidth>
        <DialogTitle>Submit Template For Approval - {showApprovals.template?.name}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 1 }}>Define approvers in order:</Typography>
          {showApprovals.steps.map((s, idx) => (
            <Box key={idx} sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <Autocomplete
                options={userOptions}
                loading={loadingUsers}
                getOptionLabel={(opt) => opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username}
                value={userOptions.find(o => o.id === s.approver_id) || null}
                onChange={(_, val) => {
                  setShowApprovals(prev => {
                    const steps = [...prev.steps];
                    steps[idx] = { ...steps[idx], approver_id: val ? val.id : 0, approval_order: idx + 1 };
                    return { ...prev, steps };
                  });
                }}
                onInputChange={(_, val) => setUserSearch(val)}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
                renderInput={(params) => (
                  <TextField {...params} label={`Approver (Step ${idx + 1})`} placeholder="Search user..." fullWidth />
                )}
              />
            </Box>
          ))}
          <Button size="small" onClick={() => setShowApprovals(prev => ({ ...prev, steps: [...prev.steps, { approver_id: 0, approval_order: prev.steps.length + 1 }] }))}>Add Step</Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowApprovals({ open: false, template: null, steps: [{ approver_id: 0, approval_order: 1 }] })}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmitTemplateApproval}>Submit</Button>
        </DialogActions>
      </Dialog>
    </Dialog>
  );
};

export default DocumentTemplatesDialog; 