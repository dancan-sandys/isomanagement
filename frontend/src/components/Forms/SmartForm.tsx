import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  Chip,
  LinearProgress,
  Stack,
  Card,
  CardContent,
  Collapse,
  IconButton,
  Tooltip,
  Autocomplete,
  Stepper,
  Step,
  StepLabel,
  Fade,
  Avatar,
  Divider,
} from '@mui/material';
import {
  Save,
  AutoAwesome,
  CheckCircle,
  Warning,
  Info,
  Error,
  Lightbulb,
  ExpandMore,
  ExpandLess,
  CloudUpload,
  Schedule,
  Psychology,
  Speed,
} from '@mui/icons-material';

interface FormField {
  id: string;
  label: string;
  type: 'text' | 'email' | 'number' | 'date' | 'select' | 'multiselect' | 'textarea' | 'file';
  required?: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: RegExp;
    custom?: (value: any) => string | null;
  };
  options?: Array<{ label: string; value: any }>;
  placeholder?: string;
  helperText?: string;
  smartSuggestions?: boolean;
  autoComplete?: boolean;
  dependencies?: string[];
  section?: string;
}

interface SmartSuggestion {
  type: 'improvement' | 'warning' | 'info' | 'success';
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface FormSection {
  id: string;
  title: string;
  description?: string;
  fields: string[];
  optional?: boolean;
}

interface SmartFormProps {
  title: string;
  description?: string;
  fields: FormField[];
  sections?: FormSection[];
  onSubmit: (data: Record<string, any>) => Promise<void>;
  initialData?: Record<string, any>;
  enableAutoSave?: boolean;
  enableSmartSuggestions?: boolean;
  enableProgressiveDisclosure?: boolean;
}

const SmartForm: React.FC<SmartFormProps> = ({
  title,
  description,
  fields,
  sections,
  onSubmit,
  initialData = {},
  enableAutoSave = true,
  enableSmartSuggestions = true,
  enableProgressiveDisclosure = true,
}) => {
  const [formData, setFormData] = useState<Record<string, any>>(initialData);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [suggestions, setSuggestions] = useState<SmartSuggestion[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [autoSaveStatus, setAutoSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [completionPercentage, setCompletionPercentage] = useState(0);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [currentStep, setCurrentStep] = useState(0);

  // Auto-save functionality
  useEffect(() => {
    if (!enableAutoSave) return;

    const timer = setTimeout(() => {
      if (Object.keys(formData).length > 0) {
        setAutoSaveStatus('saving');
        // Simulate auto-save
        setTimeout(() => {
          localStorage.setItem(`smart-form-${title}`, JSON.stringify(formData));
          setAutoSaveStatus('saved');
          setTimeout(() => setAutoSaveStatus('idle'), 2000);
        }, 500);
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [formData, enableAutoSave, title]);

  // Smart suggestions based on form data
  useEffect(() => {
    if (!enableSmartSuggestions) return;

    const newSuggestions: SmartSuggestion[] = [];

    // Example smart suggestions based on form content
    if (formData.riskLevel === 'high' && !formData.mitigationPlan) {
      newSuggestions.push({
        type: 'warning',
        title: 'High Risk Detected',
        description: 'Consider adding a detailed mitigation plan for high-risk items.',
        action: {
          label: 'Add Mitigation Plan',
          onClick: () => {
            const mitigationField = fields.find(f => f.id === 'mitigationPlan');
            if (mitigationField) {
              document.getElementById('mitigationPlan')?.focus();
            }
          },
        },
      });
    }

    if (formData.category === 'food_contact' && !formData.allergenInfo) {
      newSuggestions.push({
        type: 'info',
        title: 'Allergen Information Recommended',
        description: 'Food contact materials should include allergen compatibility information.',
        action: {
          label: 'Add Allergen Info',
          onClick: () => {
            const allergenField = fields.find(f => f.id === 'allergenInfo');
            if (allergenField) {
              document.getElementById('allergenInfo')?.focus();
            }
          },
        },
      });
    }

    setSuggestions(newSuggestions);
  }, [formData, fields, enableSmartSuggestions]);

  // Calculate completion percentage
  useEffect(() => {
    const requiredFields = fields.filter(f => f.required);
    const completedRequired = requiredFields.filter(f => formData[f.id] && formData[f.id] !== '').length;
    const allFields = fields.length;
    const completedAll = fields.filter(f => formData[f.id] && formData[f.id] !== '').length;
    
    const percentage = Math.round((completedAll / allFields) * 100);
    setCompletionPercentage(percentage);
  }, [formData, fields]);

  const validateField = useCallback((field: FormField, value: any): string | null => {
    if (field.required && (!value || value === '')) {
      return `${field.label} is required`;
    }

    if (field.validation) {
      if (field.validation.min && value && value.length < field.validation.min) {
        return `${field.label} must be at least ${field.validation.min} characters`;
      }
      
      if (field.validation.max && value && value.length > field.validation.max) {
        return `${field.label} must be no more than ${field.validation.max} characters`;
      }
      
      if (field.validation.pattern && value && !field.validation.pattern.test(value)) {
        return `${field.label} format is invalid`;
      }
      
      if (field.validation.custom && value) {
        return field.validation.custom(value);
      }
    }

    return null;
  }, []);

  const handleFieldChange = (fieldId: string, value: any) => {
    setFormData(prev => ({ ...prev, [fieldId]: value }));
    
    // Validate field
    const field = fields.find(f => f.id === fieldId);
    if (field) {
      const error = validateField(field, value);
      setErrors(prev => ({ ...prev, [fieldId]: error || '' }));
    }
  };

  const handleFieldBlur = (fieldId: string) => {
    setTouched(prev => ({ ...prev, [fieldId]: true }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Validate all fields
    const newErrors: Record<string, string> = {};
    fields.forEach(field => {
      const error = validateField(field, formData[field.id]);
      if (error) {
        newErrors[field.id] = error;
      }
    });

    setErrors(newErrors);
    
    if (Object.keys(newErrors).length === 0) {
      try {
        await onSubmit(formData);
        // Clear auto-saved data on successful submit
        localStorage.removeItem(`smart-form-${title}`);
      } catch (error) {
        console.error('Form submission error:', error);
      }
    }

    setIsSubmitting(false);
  };

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId],
    }));
  };

  const renderField = (field: FormField) => {
    const value = formData[field.id] || '';
    const error = touched[field.id] && errors[field.id];
    const hasError = Boolean(error);

    const commonProps = {
      fullWidth: true,
      id: field.id,
      label: field.label,
      value,
      error: hasError,
      helperText: error || field.helperText,
      required: field.required,
      onChange: (e: any) => handleFieldChange(field.id, e.target.value),
      onBlur: () => handleFieldBlur(field.id),
      sx: { mb: 2 },
    };

    switch (field.type) {
      case 'textarea':
        return (
          <TextField
            {...commonProps}
            multiline
            rows={4}
            placeholder={field.placeholder}
          />
        );
      
      case 'select':
        return (
          <Autocomplete
            options={field.options || []}
            getOptionLabel={(option) => option.label}
            value={field.options?.find(opt => opt.value === value) || null}
            onChange={(_, newValue) => handleFieldChange(field.id, newValue?.value || '')}
            renderInput={(params) => (
              <TextField
                {...params}
                label={field.label}
                error={hasError}
                helperText={error || field.helperText}
                required={field.required}
                onBlur={() => handleFieldBlur(field.id)}
              />
            )}
            sx={{ mb: 2 }}
          />
        );
      
      default:
        return (
          <TextField
            {...commonProps}
            type={field.type}
            placeholder={field.placeholder}
          />
        );
    }
  };

  const renderSection = (section: FormSection) => {
    const sectionFields = fields.filter(f => section.fields.includes(f.id));
    const isExpanded = expandedSections[section.id] ?? true;
    const sectionProgress = Math.round(
      (sectionFields.filter(f => formData[f.id] && formData[f.id] !== '').length / sectionFields.length) * 100
    );

    return (
      <Card key={section.id} sx={{ mb: 3 }}>
        <CardContent>
          <Stack
            direction="row"
            alignItems="center"
            justifyContent="space-between"
            onClick={() => enableProgressiveDisclosure && toggleSection(section.id)}
            sx={{ 
              cursor: enableProgressiveDisclosure ? 'pointer' : 'default',
              '&:hover': enableProgressiveDisclosure ? { backgroundColor: 'action.hover' } : {},
              borderRadius: 1,
              p: 1,
              mx: -1,
            }}
          >
            <Box sx={{ flex: 1 }}>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Typography variant="h6" fontWeight={600}>
                  {section.title}
                </Typography>
                {!section.optional && (
                  <Chip label="Required" color="primary" size="small" />
                )}
                <Chip 
                  label={`${sectionProgress}% complete`} 
                  color={sectionProgress === 100 ? 'success' : 'default'}
                  size="small" 
                />
              </Stack>
              {section.description && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {section.description}
                </Typography>
              )}
              <LinearProgress 
                variant="determinate" 
                value={sectionProgress} 
                sx={{ 
                  mt: 1, 
                  height: 4, 
                  borderRadius: 2,
                  backgroundColor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 2,
                  },
                }}
              />
            </Box>
            {enableProgressiveDisclosure && (
              <IconButton>
                {isExpanded ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            )}
          </Stack>

          <Collapse in={isExpanded}>
            <Box sx={{ pt: 2 }}>
              {sectionFields.map(field => (
                <Fade in key={field.id} timeout={300}>
                  <Box>{renderField(field)}</Box>
                </Fade>
              ))}
            </Box>
          </Collapse>
        </CardContent>
      </Card>
    );
  };

  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'improvement': return <Lightbulb />;
      case 'warning': return <Warning />;
      case 'info': return <Info />;
      case 'success': return <CheckCircle />;
      default: return <Info />;
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      {/* Form Header */}
      <Box sx={{ mb: 4 }}>
        <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
          <Avatar sx={{ 
            bgcolor: 'primary.main', 
            width: 56, 
            height: 56,
            background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
          }}>
            <AutoAwesome fontSize="large" />
          </Avatar>
          <Box>
            <Typography variant="h4" fontWeight={700}>
              {title}
            </Typography>
            {description && (
              <Typography variant="body1" color="text.secondary">
                {description}
              </Typography>
            )}
          </Box>
        </Stack>

        {/* Progress Indicator */}
        <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)' }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={2}>
              <Avatar sx={{ bgcolor: 'success.main', width: 40, height: 40 }}>
                <Speed />
              </Avatar>
              <Box sx={{ flex: 1 }}>
                <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1 }}>
                  <Typography variant="subtitle1" fontWeight={600}>
                    Form Completion
                  </Typography>
                  <Typography variant="h6" fontWeight={700} color="primary.main">
                    {completionPercentage}%
                  </Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={completionPercentage} 
                  sx={{ 
                    height: 8, 
                    borderRadius: 4,
                    backgroundColor: 'grey.200',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 4,
                    },
                  }}
                />
              </Box>
              {enableAutoSave && (
                <Stack alignItems="center" spacing={0.5}>
                  <Chip
                    label={
                      autoSaveStatus === 'saving' ? 'Saving...' :
                      autoSaveStatus === 'saved' ? 'Saved' :
                      autoSaveStatus === 'error' ? 'Error' : 'Auto-save'
                    }
                    color={
                      autoSaveStatus === 'saved' ? 'success' :
                      autoSaveStatus === 'error' ? 'error' : 'default'
                    }
    size="small"
                    icon={autoSaveStatus === 'saving' ? <Schedule /> : <CloudUpload />}
                  />
                </Stack>
              )}
            </Stack>
          </CardContent>
        </Card>
      </Box>

      {/* Smart Suggestions */}
      {enableSmartSuggestions && suggestions.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Psychology color="primary" />
            Smart Suggestions
          </Typography>
          <Stack spacing={2}>
            {suggestions.map((suggestion, index) => (
              <Fade in key={index} timeout={300 + index * 100}>
                <Alert
                  severity={suggestion.type === 'improvement' ? 'info' : suggestion.type}
                  icon={getSuggestionIcon(suggestion.type)}
                  action={
                    suggestion.action && (
                      <Button size="small" onClick={suggestion.action.onClick}>
                        {suggestion.action.label}
                      </Button>
                    )
                  }
                  sx={{ borderRadius: 3 }}
                >
                  <Typography variant="subtitle2" fontWeight={600}>
                    {suggestion.title}
                  </Typography>
                  <Typography variant="body2">
                    {suggestion.description}
                  </Typography>
                </Alert>
              </Fade>
            ))}
          </Stack>
        </Box>
      )}

      {/* Form Content */}
      <form onSubmit={handleSubmit}>
        {sections ? (
          // Sectioned form
          <>
            {sections.map(section => renderSection(section))}
          </>
        ) : (
          // Simple form
          <Card>
            <CardContent>
              {fields.map(field => (
                <Fade in key={field.id} timeout={300}>
                  <Box>{renderField(field)}</Box>
                </Fade>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Submit Section */}
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={isSubmitting || completionPercentage < 100}
            startIcon={isSubmitting ? <Schedule /> : <Save />}
            sx={{
              borderRadius: 3,
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 600,
              background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%)',
                transform: 'translateY(-2px)',
                boxShadow: '0 10px 20px rgba(30, 64, 175, 0.3)',
              },
            }}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Form'}
          </Button>
          
          {completionPercentage < 100 && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
              Complete all required fields to submit
            </Typography>
          )}
        </Box>
      </form>
    </Box>
  );
};

export default SmartForm;
