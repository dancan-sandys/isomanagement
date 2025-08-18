import React, { useEffect, useState } from 'react';
import {
  Box, Card, CardContent, Grid, Typography, Stack, Button, Chip,
  Paper, Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  FormControl, InputLabel, Select, MenuItem, Alert, IconButton,
  List, ListItem, ListItemText, ListItemIcon, Divider, Switch,
  FormControlLabel, Accordion, AccordionSummary, AccordionDetails,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import {
  Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon, ContentCopy as CopyIcon,
  Star as StarIcon, StarBorder as StarBorderIcon, Visibility as ViewIcon,
  ExpandMore as ExpandMoreIcon, PlayArrow as UseIcon, Settings as SettingsIcon,
  Description as DescriptionIcon, CheckCircle as CheckCircleIcon,
  Assignment as AssignmentIcon, Input as InputIcon, Output as OutputIcon
} from '@mui/icons-material';
import managementReviewAPI, { TemplatePayload } from '../services/managementReviewAPI';

const ManagementReviewTemplates: React.FC = () => {
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  
  const [templateForm, setTemplateForm] = useState<TemplatePayload>({
    name: '',
    description: '',
    is_default: false,
    review_frequency: 'quarterly',
    applicable_departments: [],
    compliance_standards: ['ISO 22000:2018'],
    agenda_template: [],
    input_checklist: [],
    output_categories: []
  });

  const loadTemplates = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await managementReviewAPI.listTemplates();
      setTemplates(resp.data || []);
    } catch (e: any) {
      setError(e?.message || 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const createTemplate = async () => {
    try {
      await managementReviewAPI.createTemplate(templateForm);
      setCreateDialogOpen(false);
      resetForm();
      await loadTemplates();
    } catch (e: any) {
      setError(e?.message || 'Failed to create template');
    }
  };

  const resetForm = () => {
    setTemplateForm({
      name: '',
      description: '',
      is_default: false,
      review_frequency: 'quarterly',
      applicable_departments: [],
      compliance_standards: ['ISO 22000:2018'],
      agenda_template: [],
      input_checklist: [],
      output_categories: []
    });
  };

  const addAgendaItem = () => {
    const newItem = {
      topic: '',
      description: '',
      order_index: (templateForm.agenda_template?.length || 0) + 1,
      required: true
    };
    setTemplateForm({
      ...templateForm,
      agenda_template: [...(templateForm.agenda_template || []), newItem]
    });
  };

  const updateAgendaItem = (index: number, field: string, value: any) => {
    const updatedAgenda = [...(templateForm.agenda_template || [])];
    updatedAgenda[index] = { ...updatedAgenda[index], [field]: value };
    setTemplateForm({ ...templateForm, agenda_template: updatedAgenda });
  };

  const removeAgendaItem = (index: number) => {
    const updatedAgenda = (templateForm.agenda_template || []).filter((_, i) => i !== index);
    setTemplateForm({ ...templateForm, agenda_template: updatedAgenda });
  };

  const addInputChecklistItem = () => {
    const newItem = {
      input_type: '',
      description: '',
      required: true,
      automated: false
    };
    setTemplateForm({
      ...templateForm,
      input_checklist: [...(templateForm.input_checklist || []), newItem]
    });
  };

  const updateInputChecklistItem = (index: number, field: string, value: any) => {
    const updatedChecklist = [...(templateForm.input_checklist || [])];
    updatedChecklist[index] = { ...updatedChecklist[index], [field]: value };
    setTemplateForm({ ...templateForm, input_checklist: updatedChecklist });
  };

  const removeInputChecklistItem = (index: number) => {
    const updatedChecklist = (templateForm.input_checklist || []).filter((_, i) => i !== index);
    setTemplateForm({ ...templateForm, input_checklist: updatedChecklist });
  };

  const getFrequencyColor = (frequency: string) => {
    switch (frequency) {
      case 'monthly': return 'success';
      case 'quarterly': return 'primary';
      case 'semi_annually': return 'warning';
      case 'annually': return 'info';
      default: return 'default';
    }
  };

  const defaultTemplates = [
    {
      name: 'ISO 22000:2018 Standard Review',
      description: 'Comprehensive management review template following ISO 22000:2018 requirements',
      frequency: 'quarterly',
      compliance_standards: ['ISO 22000:2018'],
      agenda_items: 8,
      input_types: 12,
      is_default: true
    },
    {
      name: 'Annual Strategic Review',
      description: 'Annual comprehensive review including strategic planning and resource allocation',
      frequency: 'annually',
      compliance_standards: ['ISO 22000:2018', 'ISO 9001:2015'],
      agenda_items: 12,
      input_types: 15,
      is_default: false
    },
    {
      name: 'Emergency Response Review',
      description: 'Template for emergency management reviews following incidents or crises',
      frequency: 'ad_hoc',
      compliance_standards: ['ISO 22000:2018'],
      agenda_items: 6,
      input_types: 8,
      is_default: false
    }
  ];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>Review Templates</Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Standardized templates for consistent and compliant management reviews
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
          <Button variant="outlined" startIcon={<SettingsIcon />}>
            Settings
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateDialogOpen(true)}>
            Create Template
          </Button>
        </Stack>
      </Stack>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Template Categories */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <StarIcon color="primary" />
                <Box>
                  <Typography variant="h6">Default Templates</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {templates.filter(t => t.is_default).length} template(s)
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <DescriptionIcon color="info" />
                <Box>
                  <Typography variant="h6">Custom Templates</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {templates.filter(t => !t.is_default).length} template(s)
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <CheckCircleIcon color="success" />
                <Box>
                  <Typography variant="h6">ISO Compliant</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {templates.filter(t => t.compliance_standards?.includes('ISO 22000:2018')).length} template(s)
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Templates Grid */}
      <Grid container spacing={3}>
        {/* Show default templates first */}
        {defaultTemplates.map((template, index) => (
          <Grid item xs={12} md={6} lg={4} key={`default-${index}`}>
            <Card elevation={template.is_default ? 3 : 1}>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                  <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    {template.name}
                  </Typography>
                  {template.is_default && <StarIcon color="primary" />}
                </Stack>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {template.description}
                </Typography>
                
                <Stack spacing={1} sx={{ mb: 2 }}>
                  <Chip 
                    label={template.frequency} 
                    color={getFrequencyColor(template.frequency)}
                    size="small"
                  />
                  <Stack direction="row" spacing={1}>
                    {template.compliance_standards.map((standard: string) => (
                      <Chip key={standard} label={standard} variant="outlined" size="small" />
                    ))}
                  </Stack>
                </Stack>
                
                <Grid container spacing={1} sx={{ mb: 2 }}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      <AssignmentIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
                      {template.agenda_items} agenda items
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      <InputIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
                      {template.input_types} input types
                    </Typography>
                  </Grid>
                </Grid>
                
                <Stack direction="row" spacing={1}>
                  <Button size="small" startIcon={<UseIcon />} variant="contained">
                    Use Template
                  </Button>
                  <Button size="small" startIcon={<ViewIcon />} onClick={() => {
                    setSelectedTemplate(template);
                    setViewDialogOpen(true);
                  }}>
                    Preview
                  </Button>
                  <IconButton size="small">
                    <CopyIcon />
                  </IconButton>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}

        {/* Show custom templates */}
        {templates.map((template) => (
          <Grid item xs={12} md={6} lg={4} key={template.id}>
            <Card>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                  <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    {template.name}
                  </Typography>
                  {template.is_default && <StarIcon color="primary" />}
                </Stack>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {template.description}
                </Typography>
                
                <Stack spacing={1} sx={{ mb: 2 }}>
                  <Chip 
                    label={template.review_frequency || 'quarterly'} 
                    color={getFrequencyColor(template.review_frequency)}
                    size="small"
                  />
                  {template.compliance_standards && (
                    <Stack direction="row" spacing={1}>
                      {template.compliance_standards.map((standard: string) => (
                        <Chip key={standard} label={standard} variant="outlined" size="small" />
                      ))}
                    </Stack>
                  )}
                </Stack>
                
                <Stack direction="row" spacing={1}>
                  <Button size="small" startIcon={<UseIcon />} variant="contained">
                    Use Template
                  </Button>
                  <Button size="small" startIcon={<EditIcon />}>
                    Edit
                  </Button>
                  <IconButton size="small">
                    <DeleteIcon />
                  </IconButton>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create Template Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} fullWidth maxWidth="lg">
        <DialogTitle>
          <Stack direction="row" alignItems="center" spacing={1}>
            <AddIcon />
            <Typography variant="h6">Create Review Template</Typography>
          </Stack>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>Basic Information</Typography>
            </Grid>
            
            <Grid item xs={12} md={8}>
              <TextField
                label="Template Name"
                fullWidth
                value={templateForm.name}
                onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
                required
                placeholder="e.g., Quarterly ISO Review Template"
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Frequency</InputLabel>
                <Select
                  value={templateForm.review_frequency || 'quarterly'}
                  onChange={(e) => setTemplateForm({ ...templateForm, review_frequency: e.target.value })}
                  label="Frequency"
                >
                  <MenuItem value="monthly">Monthly</MenuItem>
                  <MenuItem value="quarterly">Quarterly</MenuItem>
                  <MenuItem value="semi_annually">Semi-Annually</MenuItem>
                  <MenuItem value="annually">Annually</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Description"
                fullWidth
                multiline
                rows={3}
                value={templateForm.description}
                onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })}
                placeholder="Describe the purpose and scope of this template..."
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={templateForm.is_default}
                    onChange={(e) => setTemplateForm({ ...templateForm, is_default: e.target.checked })}
                  />
                }
                label="Set as Default Template"
              />
            </Grid>

            {/* Agenda Template */}
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">Agenda Template</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Stack spacing={2}>
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={addAgendaItem}
                    >
                      Add Agenda Item
                    </Button>
                    
                    {(templateForm.agenda_template || []).map((item, index) => (
                      <Paper key={index} sx={{ p: 2 }}>
                        <Grid container spacing={2} alignItems="center">
                          <Grid item xs={12} md={6}>
                            <TextField
                              label="Topic"
                              fullWidth
                              size="small"
                              value={item.topic || ''}
                              onChange={(e) => updateAgendaItem(index, 'topic', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={4}>
                            <TextField
                              label="Description"
                              fullWidth
                              size="small"
                              value={item.description || ''}
                              onChange={(e) => updateAgendaItem(index, 'description', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={2}>
                            <IconButton onClick={() => removeAgendaItem(index)} color="error">
                              <DeleteIcon />
                            </IconButton>
                          </Grid>
                        </Grid>
                      </Paper>
                    ))}
                  </Stack>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Input Checklist */}
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">Input Checklist</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Stack spacing={2}>
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={addInputChecklistItem}
                    >
                      Add Input Type
                    </Button>
                    
                    {(templateForm.input_checklist || []).map((item, index) => (
                      <Paper key={index} sx={{ p: 2 }}>
                        <Grid container spacing={2} alignItems="center">
                          <Grid item xs={12} md={4}>
                            <FormControl fullWidth size="small">
                              <InputLabel>Input Type</InputLabel>
                              <Select
                                value={item.input_type || ''}
                                onChange={(e) => updateInputChecklistItem(index, 'input_type', e.target.value)}
                                label="Input Type"
                              >
                                <MenuItem value="audit_results">Audit Results</MenuItem>
                                <MenuItem value="nc_capa_status">NC/CAPA Status</MenuItem>
                                <MenuItem value="supplier_performance">Supplier Performance</MenuItem>
                                <MenuItem value="haccp_performance">HACCP Performance</MenuItem>
                                <MenuItem value="prp_performance">PRP Performance</MenuItem>
                                <MenuItem value="risk_assessment">Risk Assessment</MenuItem>
                                <MenuItem value="kpi_metrics">KPI Metrics</MenuItem>
                                <MenuItem value="customer_feedback">Customer Feedback</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              label="Description"
                              fullWidth
                              size="small"
                              value={item.description || ''}
                              onChange={(e) => updateInputChecklistItem(index, 'description', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={2}>
                            <IconButton onClick={() => removeInputChecklistItem(index)} color="error">
                              <DeleteIcon />
                            </IconButton>
                          </Grid>
                        </Grid>
                      </Paper>
                    ))}
                  </Stack>
                </AccordionDetails>
              </Accordion>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={createTemplate} 
            disabled={!templateForm.name}
          >
            Create Template
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Template Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>
          <Stack direction="row" alignItems="center" spacing={1}>
            <ViewIcon />
            <Typography variant="h6">Template Preview: {selectedTemplate?.name}</Typography>
          </Stack>
        </DialogTitle>
        <DialogContent>
          {selectedTemplate && (
            <Stack spacing={3}>
              <Box>
                <Typography variant="subtitle2" gutterBottom>Description</Typography>
                <Typography variant="body2">{selectedTemplate.description}</Typography>
              </Box>
              
              <Box>
                <Typography variant="subtitle2" gutterBottom>Template Details</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Frequency:</strong> {selectedTemplate.frequency}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Agenda Items:</strong> {selectedTemplate.agenda_items}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Input Types:</strong> {selectedTemplate.input_types}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Default:</strong> {selectedTemplate.is_default ? 'Yes' : 'No'}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
              
              <Box>
                <Typography variant="subtitle2" gutterBottom>Compliance Standards</Typography>
                <Stack direction="row" spacing={1}>
                  {selectedTemplate.compliance_standards?.map((standard: string) => (
                    <Chip key={standard} label={standard} variant="outlined" size="small" />
                  ))}
                </Stack>
              </Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
          <Button variant="contained" startIcon={<UseIcon />}>
            Use This Template
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ManagementReviewTemplates;