import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Tooltip,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Autocomplete,
  FormHelperText,
  InputAdornment,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  alpha
} from '@mui/material';
import {
  Add as AddIcon,
  Save as SaveIcon,
  Clear as ClearIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ArrowBack as ArrowBackIcon,
  ArrowForward as ArrowForwardIcon,
  QrCode as QrCodeIcon,
  Business as BusinessIcon,
  LocalShipping as LocalShippingIcon,
  Inventory as InventoryIcon,
  Timeline as TimelineIcon,
  Security as SecurityIcon,
  VerifiedUser as VerifiedUserIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Help as HelpIcon
} from '@mui/icons-material';
import { traceabilityAPI } from '../../services/traceabilityAPI';

interface GuidedDataEntryProps {
  entryType: 'batch' | 'traceability_link' | 'recall';
  onComplete?: (data: any) => void;
  onCancel?: () => void;
  initialData?: any;
}

interface ValidationRule {
  field: string;
  type: 'required' | 'minLength' | 'maxLength' | 'pattern' | 'custom';
  value?: any;
  message: string;
  validator?: (value: any) => boolean;
}

interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'select' | 'multiselect' | 'textarea' | 'checkbox';
  required: boolean;
  options?: string[];
  placeholder?: string;
  helperText?: string;
  validation?: ValidationRule[];
  dependencies?: string[];
  conditional?: (formData: any) => boolean;
}

interface FormData {
  [key: string]: any;
}

const GuidedDataEntry: React.FC<GuidedDataEntryProps> = ({
  entryType,
  onComplete,
  onCancel,
  initialData
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<FormData>({});
  const [validationErrors, setValidationErrors] = useState<{ [key: string]: string }>({});
  const [showPreview, setShowPreview] = useState(false);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [batches, setBatches] = useState<any[]>([]);

  // Define form structure based on entry type
  const getFormStructure = (): { steps: { title: string; fields: FormField[] }[] } => {
    switch (entryType) {
      case 'batch':
        return {
          steps: [
            {
              title: 'Basic Information',
              fields: [
                {
                  name: 'batch_number',
                  label: 'Batch Number',
                  type: 'text',
                  required: true,
                  placeholder: 'e.g., BATCH-2024-001',
                  helperText: 'Unique identifier for the batch',
                  validation: [
                    { field: 'batch_number', type: 'required', message: 'Batch number is required' },
                    { field: 'batch_number', type: 'pattern', value: /^[A-Z0-9-]+$/, message: 'Only uppercase letters, numbers, and hyphens allowed' }
                  ]
                },
                {
                  name: 'batch_type',
                  label: 'Batch Type',
                  type: 'select',
                  required: true,
                  options: ['raw_milk', 'additive', 'culture', 'packaging', 'final_product', 'intermediate'],
                  helperText: 'Type of batch being created'
                },
                {
                  name: 'product_name',
                  label: 'Product Name',
                  type: 'text',
                  required: true,
                  placeholder: 'e.g., Organic Whole Milk',
                  helperText: 'Name of the product'
                },
                {
                  name: 'quantity',
                  label: 'Quantity',
                  type: 'number',
                  required: true,
                  placeholder: '100',
                  helperText: 'Quantity of the batch'
                },
                {
                  name: 'unit',
                  label: 'Unit',
                  type: 'select',
                  required: true,
                  options: ['kg', 'liters', 'units', 'cases', 'pallets'],
                  helperText: 'Unit of measurement'
                }
              ]
            },
            {
              title: 'Production Details',
              fields: [
                {
                  name: 'production_date',
                  label: 'Production Date',
                  type: 'date',
                  required: true,
                  helperText: 'Date when production started'
                },
                {
                  name: 'expiry_date',
                  label: 'Expiry Date',
                  type: 'date',
                  required: false,
                  helperText: 'Expected expiry date (optional)'
                },
                {
                  name: 'lot_number',
                  label: 'Lot Number',
                  type: 'text',
                  required: false,
                  placeholder: 'e.g., LOT2024-001',
                  helperText: 'Manufacturer lot number (optional)'
                },
                {
                  name: 'storage_location',
                  label: 'Storage Location',
                  type: 'text',
                  required: false,
                  placeholder: 'e.g., Warehouse A, Section 1',
                  helperText: 'Where the batch is stored'
                },
                {
                  name: 'storage_conditions',
                  label: 'Storage Conditions',
                  type: 'textarea',
                  required: false,
                  placeholder: 'e.g., Temperature: 2-4°C, Humidity: 85-90%',
                  helperText: 'Special storage requirements'
                }
              ]
            },
            {
              title: 'GS1 Compliance',
              fields: [
                {
                  name: 'gtin',
                  label: 'GTIN (Global Trade Item Number)',
                  type: 'text',
                  required: false,
                  placeholder: '12345678901234',
                  helperText: '14-digit Global Trade Item Number (optional)',
                  validation: [
                    { field: 'gtin', type: 'pattern', value: /^\d{14}$/, message: 'GTIN must be exactly 14 digits' }
                  ]
                },
                {
                  name: 'sscc',
                  label: 'SSCC (Serial Shipping Container Code)',
                  type: 'text',
                  required: false,
                  placeholder: '123456789012345678',
                  helperText: '18-digit Serial Shipping Container Code (optional)',
                  validation: [
                    { field: 'sscc', type: 'pattern', value: /^\d{18}$/, message: 'SSCC must be exactly 18 digits' }
                  ]
                },
                {
                  name: 'hierarchical_lot_number',
                  label: 'Hierarchical Lot Number',
                  type: 'text',
                  required: false,
                  placeholder: 'LOT2024-001-001',
                  helperText: 'Hierarchical lot numbering system (optional)'
                }
              ]
            },
            {
              title: 'Supplier Information',
              fields: [
                {
                  name: 'supplier_id',
                  label: 'Supplier',
                  type: 'select',
                  required: false,
                  options: suppliers.map(s => s.id.toString()),
                  helperText: 'Select the supplier (optional)'
                },
                {
                  name: 'supplier_information',
                  label: 'Supplier Information',
                  type: 'textarea',
                  required: false,
                  placeholder: 'Additional supplier details in JSON format',
                  helperText: 'Additional supplier information (optional)',
                  conditional: (data) => !data.supplier_id
                }
              ]
            }
          ]
        };

      case 'traceability_link':
        return {
          steps: [
            {
              title: 'Link Information',
              fields: [
                {
                  name: 'source_batch_id',
                  label: 'Source Batch',
                  type: 'select',
                  required: true,
                  options: batches.map(b => b.id.toString()),
                  helperText: 'Select the source batch'
                },
                {
                  name: 'target_batch_id',
                  label: 'Target Batch',
                  type: 'select',
                  required: true,
                  options: batches.map(b => b.id.toString()),
                  helperText: 'Select the target batch'
                },
                {
                  name: 'link_type',
                  label: 'Link Type',
                  type: 'select',
                  required: true,
                  options: ['ingredient', 'product', 'process'],
                  helperText: 'Type of relationship between batches'
                },
                {
                  name: 'quantity_used',
                  label: 'Quantity Used',
                  type: 'number',
                  required: true,
                  placeholder: '50',
                  helperText: 'Quantity of source batch used in target batch'
                },
                {
                  name: 'process_step',
                  label: 'Process Step',
                  type: 'text',
                  required: true,
                  placeholder: 'e.g., Pasteurization, Packaging',
                  helperText: 'Processing step that created this link'
                }
              ]
            }
          ]
        };

      case 'recall':
        return {
          steps: [
            {
              title: 'Issue Identification',
              fields: [
                {
                  name: 'issue_type',
                  label: 'Issue Type',
                  type: 'select',
                  required: true,
                  options: ['Contamination', 'Allergen Mislabeling', 'Quality Defect', 'Packaging Issue', 'Other'],
                  helperText: 'Type of safety issue'
                },
                {
                  name: 'issue_description',
                  label: 'Issue Description',
                  type: 'textarea',
                  required: true,
                  placeholder: 'Detailed description of the issue...',
                  helperText: 'Provide a detailed description of the issue'
                },
                {
                  name: 'issue_severity',
                  label: 'Severity Level',
                  type: 'select',
                  required: true,
                  options: ['low', 'medium', 'high', 'critical'],
                  helperText: 'Severity level of the issue'
                }
              ]
            },
            {
              title: 'Affected Products',
              fields: [
                {
                  name: 'affected_batches',
                  label: 'Affected Batches',
                  type: 'multiselect',
                  required: true,
                  options: batches.map(b => b.id.toString()),
                  helperText: 'Select all affected batches'
                },
                {
                  name: 'quantity_affected',
                  label: 'Quantity Affected',
                  type: 'number',
                  required: true,
                  placeholder: '100',
                  helperText: 'Total quantity affected by the recall'
                }
              ]
            }
          ]
        };

      default:
        return { steps: [] };
    }
  };

  const formStructure = getFormStructure();

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
    loadReferenceData();
  }, [initialData]);

  const loadReferenceData = async () => {
    try {
      // Load suppliers and batches for dropdowns
      const [suppliersResponse, batchesResponse] = await Promise.all([
        traceabilityAPI.getSuppliers?.() || Promise.resolve({ items: [] }),
        traceabilityAPI.getBatches({ size: 100 })
      ]);
      
      setSuppliers(suppliersResponse.items || []);
      setBatches(batchesResponse.items || []);
    } catch (err) {
      console.error('Failed to load reference data:', err);
    }
  };

  const validateField = (field: FormField, value: any): string | null => {
    if (field.required && (!value || value === '')) {
      return field.validation?.find(v => v.type === 'required')?.message || `${field.label} is required`;
    }

    if (field.validation) {
      for (const rule of field.validation) {
        switch (rule.type) {
          case 'minLength':
            if (value && value.length < rule.value) {
              return rule.message;
            }
            break;
          case 'maxLength':
            if (value && value.length > rule.value) {
              return rule.message;
            }
            break;
          case 'pattern':
            if (value && rule.value && !rule.value.test(value)) {
              return rule.message;
            }
            break;
          case 'custom':
            if (value && rule.validator && !rule.validator(value)) {
              return rule.message;
            }
            break;
        }
      }
    }

    return null;
  };

  const validateStep = (stepIndex: number): boolean => {
    const step = formStructure.steps[stepIndex];
    const errors: { [key: string]: string } = {};

    step.fields.forEach(field => {
      // Check if field should be shown based on conditional logic
      if (field.conditional && !field.conditional(formData)) {
        return;
      }

      const error = validateField(field, formData[field.name]);
      if (error) {
        errors[field.name] = error;
      }
    });

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const updateFormData = (fieldName: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));

    // Clear validation error for this field
    if (validationErrors[fieldName]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[fieldName];
        return newErrors;
      });
    }
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      if (activeStep === formStructure.steps.length - 1) {
        setShowPreview(true);
      } else {
        setActiveStep(prev => prev + 1);
      }
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      let response;
      
      switch (entryType) {
        case 'batch':
          response = await traceabilityAPI.createBatch(formData);
          break;
        case 'traceability_link':
          response = await traceabilityAPI.createTraceabilityLink(formData as any);
          break;
        case 'recall':
          response = await traceabilityAPI.createRecall(formData);
          break;
        default:
          throw new Error('Invalid entry type');
      }

      onComplete?.(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to save data');
    } finally {
      setLoading(false);
    }
  };

  const renderField = (field: FormField) => {
    const value = formData[field.name] || '';
    const error = validationErrors[field.name];
    const showField = !field.conditional || field.conditional(formData);

    if (!showField) return null;

    const commonProps = {
      fullWidth: true,
      label: field.label,
      value: value,
      onChange: (e: any) => updateFormData(field.name, e.target.value),
      error: !!error,
      helperText: error || field.helperText,
      placeholder: field.placeholder,
      required: field.required
    };

    switch (field.type) {
      case 'text':
        return <TextField {...commonProps} />;

      case 'number':
        return <TextField {...commonProps} type="number" />;

      case 'date':
        return (
          <TextField
            {...commonProps}
            type="date"
            InputLabelProps={{ shrink: true }}
          />
        );

      case 'select':
        return (
          <FormControl fullWidth error={!!error} required={field.required}>
            <InputLabel>{field.label}</InputLabel>
            <Select
              value={value}
              onChange={(e) => updateFormData(field.name, e.target.value)}
              label={field.label}
            >
              {field.options?.map(option => (
                <MenuItem key={option} value={option}>
                  {option.replace('_', ' ').toUpperCase()}
                </MenuItem>
              ))}
            </Select>
            {error && <FormHelperText>{error}</FormHelperText>}
            {field.helperText && <FormHelperText>{field.helperText}</FormHelperText>}
          </FormControl>
        );

      case 'multiselect':
        return (
          <Autocomplete
            multiple
            options={field.options || []}
            value={Array.isArray(value) ? value : []}
            onChange={(_, newValue) => updateFormData(field.name, newValue)}
            renderInput={(params) => (
              <TextField
                {...params}
                label={field.label}
                error={!!error}
                helperText={error || field.helperText}
                required={field.required}
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option}
                  {...getTagProps({ index })}
                  key={option}
                />
              ))
            }
          />
        );

      case 'textarea':
        return (
          <TextField
            {...commonProps}
            multiline
            rows={4}
          />
        );

      case 'checkbox':
        return (
          <FormControlLabel
            control={
              <Checkbox
                checked={!!value}
                onChange={(e) => updateFormData(field.name, e.target.checked)}
              />
            }
            label={field.label}
          />
        );

      default:
        return <TextField {...commonProps} />;
    }
  };

  const renderPreview = () => (
    <Dialog open={showPreview} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={2}>
          <CheckCircleIcon color="primary" />
          <Typography variant="h6">Review Data</Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2}>
          {Object.entries(formData).map(([key, value]) => (
            <Grid item xs={12} md={6} key={key}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  {key.replace('_', ' ').toUpperCase()}
                </Typography>
                <Typography variant="body1">
                  {Array.isArray(value) ? value.join(', ') : String(value || 'N/A')}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowPreview(false)}>Back to Edit</Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
        >
          {loading ? 'Saving...' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={2} mb={3}>
          <AddIcon color="primary" sx={{ fontSize: 32 }} />
          <Box flex={1}>
            <Typography variant="h5" fontWeight={600}>
              Guided Data Entry
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {entryType === 'batch' && 'Create new batch with guided validation'}
              {entryType === 'traceability_link' && 'Create traceability link between batches'}
              {entryType === 'recall' && 'Create new recall with step-by-step guidance'}
            </Typography>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Stepper activeStep={activeStep} orientation="vertical">
          {formStructure.steps.map((step, stepIndex) => (
            <Step key={stepIndex}>
              <StepLabel>
                <Typography variant="h6">{step.title}</Typography>
              </StepLabel>
              <StepContent>
                <Grid container spacing={3}>
                  {step.fields.map((field, fieldIndex) => (
                    <Grid item xs={12} md={6} key={fieldIndex}>
                      {renderField(field)}
                    </Grid>
                  ))}
                </Grid>

                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                  <Button
                    disabled={stepIndex === 0}
                    onClick={handleBack}
                    startIcon={<ArrowBackIcon />}
                  >
                    Back
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    endIcon={stepIndex === formStructure.steps.length - 1 ? <SaveIcon /> : <ArrowForwardIcon />}
                  >
                    {stepIndex === formStructure.steps.length - 1 ? 'Review & Save' : 'Next'}
                  </Button>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>

        {renderPreview()}
      </CardContent>
    </Card>
  );
};

export default GuidedDataEntry;
