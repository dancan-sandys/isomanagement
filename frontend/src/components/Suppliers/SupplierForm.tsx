import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Alert,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Divider,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  TextareaAutosize,
} from '@mui/material';
import {
  Save,
  Cancel,
  Business,
  Person,
  Email,
  Phone,
  Language,
  LocationOn,
  Security,
  Assessment,
  Description,
  Add,
  Delete,
  Edit,
  Visibility,
  VisibilityOff,
  Verified,
  Warning,
  Error,
  Info,
  CheckCircle,
  Schedule,
  Notifications,
  Settings,
  Upload,
  Download,
  Archive,
  RestoreFromTrash,
  History,
  Timeline,
  Analytics,
  TrendingUp,
  TrendingDown,
  Star,
  StarBorder,
  Block,
  Pending,
  LocalShipping,
  Inventory,
  Science,
  Build,
  Support,
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  createSupplier,
  updateSupplier,
  fetchSupplier,
} from '../../store/slices/supplierSlice';
import { RootState, AppDispatch } from '../../store';
import { Supplier, SupplierCreate, SupplierUpdate } from '../../types/supplier';
import { EnhancedCard } from '../UI';
import { EnhancedStatusChip } from '../UI';
import { NotificationToast } from '../UI';

interface SupplierFormProps {
  supplierId?: number;
  onSave?: (supplier: Supplier) => void;
  onCancel?: () => void;
  mode?: 'create' | 'edit' | 'view';
}

const validationSchema = Yup.object({
  supplier_code: Yup.string()
    .required('Supplier code is required')
    .min(3, 'Supplier code must be at least 3 characters')
    .max(20, 'Supplier code must not exceed 20 characters'),
  name: Yup.string()
    .required('Supplier name is required')
    .min(2, 'Supplier name must be at least 2 characters')
    .max(100, 'Supplier name must not exceed 100 characters'),
  category: Yup.string()
    .required('Category is required'),
  contact_person: Yup.string()
    .required('Contact person is required')
    .min(2, 'Contact person must be at least 2 characters')
    .max(50, 'Contact person must not exceed 50 characters'),
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required'),
  phone: Yup.string()
    .required('Phone number is required')
    // Allow +, digits, spaces, dashes, parentheses; 7-20 chars typical
    .matches(/^[+]?[\d\s\-()]{7,20}$/, 'Invalid phone number'),
  website: Yup.string()
    .transform((value) => (value === '' ? undefined : value))
    .url('Invalid website URL')
    .notRequired(),
  address_line1: Yup.string()
    .required('Address is required')
    .min(5, 'Address must be at least 5 characters')
    .max(100, 'Address must not exceed 100 characters'),
  address_line2: Yup.string()
    .transform((value) => (value === '' ? undefined : value))
    .max(100, 'Address line 2 must not exceed 100 characters')
    .notRequired(),
  city: Yup.string()
    .required('City is required')
    .min(2, 'City must be at least 2 characters')
    .max(50, 'City must not exceed 50 characters'),
  state: Yup.string()
    .transform((value) => (value === '' ? undefined : value))
    .max(50, 'State must not exceed 50 characters')
    .notRequired(),
  postal_code: Yup.string()
    .transform((value) => (value === '' ? undefined : value))
    .max(20, 'Postal code must not exceed 20 characters')
    .notRequired(),
  country: Yup.string()
    .required('Country is required')
    .min(2, 'Country must be at least 2 characters')
    .max(50, 'Country must not exceed 50 characters'),
  business_registration_number: Yup.string()
    .transform((value) => (value === '' ? undefined : value))
    .max(50, 'Business registration number must not exceed 50 characters')
    .notRequired(),
  tax_identification_number: Yup.string()
    .transform((value) => (value === '' ? undefined : value))
    .max(50, 'Tax identification number must not exceed 50 characters')
    .notRequired(),
  company_type: Yup.string()
    .transform((value) => (value === '' ? undefined : value))
    .max(50, 'Company type must not exceed 50 characters')
    .notRequired(),
  year_established: Yup.number()
    .transform((value, originalValue) => {
      if (originalValue === '' || originalValue === null || typeof originalValue === 'undefined') {
        return undefined as any;
      }
      return Number(originalValue);
    })
    .min(1800, 'Year established must be after 1800')
    .max(new Date().getFullYear(), 'Year established cannot be in the future')
    .notRequired(),
  risk_level: Yup.string()
    .required('Risk level is required')
    .oneOf(['low', 'medium', 'high', 'critical'], 'Invalid risk level'),
  notes: Yup.string()
    .max(500, 'Notes must not exceed 500 characters')
    .optional(),
});

const SupplierForm: React.FC<SupplierFormProps> = ({
  supplierId,
  onSave,
  onCancel,
  mode = 'create',
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { selectedSupplier, suppliersLoading, suppliersError } = useSelector(
    (state: RootState) => state.supplier
  );

  const [activeStep, setActiveStep] = useState(0);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ open: false, message: '', severity: 'info' });

  const steps = [
    'Basic Information',
    'Contact Details',
    'Address Information',
    'Business Details',
    'Risk Assessment',
    'Review & Save',
  ];

  // Step-specific validation schemas to avoid blocking Next with future-step fields
  const stepSchemas: Array<Yup.ObjectSchema<any> | null> = [
    Yup.object({
      supplier_code: validationSchema.fields.supplier_code,
      name: validationSchema.fields.name,
      category: validationSchema.fields.category,
      contact_person: validationSchema.fields.contact_person,
    }) as Yup.ObjectSchema<any>,
    Yup.object({
      email: validationSchema.fields.email,
      phone: validationSchema.fields.phone,
      website: validationSchema.fields.website,
    }) as Yup.ObjectSchema<any>,
    Yup.object({
      address_line1: validationSchema.fields.address_line1,
      address_line2: validationSchema.fields.address_line2,
      city: validationSchema.fields.city,
      state: validationSchema.fields.state,
      postal_code: validationSchema.fields.postal_code,
      country: validationSchema.fields.country,
    }) as Yup.ObjectSchema<any>,
    Yup.object({
      business_registration_number: validationSchema.fields.business_registration_number,
      tax_identification_number: validationSchema.fields.tax_identification_number,
      company_type: validationSchema.fields.company_type,
      year_established: validationSchema.fields.year_established,
    }) as Yup.ObjectSchema<any>,
    Yup.object({
      risk_level: validationSchema.fields.risk_level,
      notes: validationSchema.fields.notes,
    }) as Yup.ObjectSchema<any>,
    null,
  ];

  const stepFields: string[][] = [
    ['supplier_code', 'name', 'category', 'contact_person'],
    ['email', 'phone', 'website'],
    ['address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country'],
    ['business_registration_number', 'tax_identification_number', 'company_type', 'year_established'],
    ['risk_level', 'notes'],
    [],
  ];

  // Defer computing step validity until after formik is defined
  let isStepValid = true;

  const touchCurrentStepFields = () => {
    const fields = stepFields[activeStep] || [];
    const touched: Record<string, boolean> = {};
    fields.forEach((f) => { touched[f] = true; });
    formik.setTouched({ ...formik.touched, ...touched }, true);
  };

  const scrollToFirstError = () => {
    const fields = stepFields[activeStep] || [];
    for (const field of fields) {
      if ((formik.touched as any)[field] && (formik.errors as any)[field]) {
        const el = document.querySelector(`[name="${field}"]`);
        if (el && 'scrollIntoView' in el) {
          (el as HTMLElement).scrollIntoView({ behavior: 'smooth', block: 'center' });
          (el as HTMLElement).focus();
        }
        break;
      }
    }
  };

  const formik = useFormik({
    initialValues: {
      supplier_code: '',
      name: '',
      category: '',
      contact_person: '',
      email: '',
      phone: '',
      website: '',
      address_line1: '',
      address_line2: '',
      city: '',
      state: '',
      postal_code: '',
      country: '',
      business_registration_number: '',
      tax_identification_number: '',
      company_type: '',
      year_established: '',
      risk_level: 'low',
      notes: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        if (mode === 'create') {
          const payload = {
            ...values,
            year_established: values.year_established ? Number(values.year_established) : undefined,
          } as any;
          const response = await dispatch(createSupplier(payload)).unwrap();
          setNotification({
            open: true,
            message: 'Supplier created successfully',
            severity: 'success',
          });
          onSave?.(response);
        } else if (mode === 'edit' && supplierId) {
          const payload = {
            ...values,
            year_established: values.year_established === ''
              ? undefined
              : Number(values.year_established),
          } as any;
          const response = await dispatch(updateSupplier({
            supplierId,
            supplierData: {
              ...values,
              year_established: values.year_established ? Number(values.year_established) : undefined,
            } as any,
          })).unwrap();
          setNotification({
            open: true,
            message: 'Supplier updated successfully',
            severity: 'success',
          });
          onSave?.(response);
        }
      } catch (error) {
        setNotification({
          open: true,
          message: 'Failed to save supplier',
          severity: 'error',
        });
      }
    },
  });

  useEffect(() => {
    if (supplierId && mode !== 'create') {
      dispatch(fetchSupplier(supplierId));
    }
  }, [supplierId, mode, dispatch]);

  useEffect(() => {
    if (selectedSupplier && mode !== 'create') {
      formik.setValues({
        supplier_code: selectedSupplier.supplier_code,
        name: selectedSupplier.name,
        category: selectedSupplier.category,
        contact_person: selectedSupplier.contact_person,
        email: selectedSupplier.email,
        phone: selectedSupplier.phone,
        website: selectedSupplier.website || '',
        address_line1: selectedSupplier.address_line1,
        address_line2: selectedSupplier.address_line2 || '',
        city: selectedSupplier.city,
        state: selectedSupplier.state || '',
        postal_code: selectedSupplier.postal_code || '',
        country: selectedSupplier.country,
        business_registration_number: selectedSupplier.business_registration_number || '',
        tax_identification_number: selectedSupplier.tax_identification_number || '',
        company_type: selectedSupplier.company_type || '',
        year_established: selectedSupplier.year_established?.toString() || '',
        risk_level: selectedSupplier.risk_level,
        notes: selectedSupplier.notes || '',
      });
    }
  }, [selectedSupplier, mode]);

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      formik.submitForm();
      return;
    }
    // Validate only current step; prevent advancement if invalid
    const schema = stepSchemas[activeStep];
    if (schema) {
      schema
        .validate(formik.values, { abortEarly: false })
        .then(() => setActiveStep((prev) => prev + 1))
        .catch(() => { touchCurrentStepFields(); scrollToFirstError(); });
    } else {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    formik.resetForm();
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'raw_milk': return <Inventory />;
      case 'additives': return <Add />;
      case 'cultures': return <Science />;
      case 'packaging': return <Inventory />;
      case 'equipment': return <Build />;
      case 'chemicals': return <Science />;
      case 'services': return <Support />;
      default: return <Business />;
    }
  };

  const renderBasicInformation = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          name="supplier_code"
          label="Supplier Code"
          value={formik.values.supplier_code}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.supplier_code && Boolean(formik.errors.supplier_code)}
          helperText={formik.touched.supplier_code && formik.errors.supplier_code}
          disabled={mode === 'view'}
          required
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          name="name"
          label="Supplier Name"
          value={formik.values.name}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.name && Boolean(formik.errors.name)}
          helperText={formik.touched.name && formik.errors.name}
          disabled={mode === 'view'}
          required
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <FormControl fullWidth error={formik.touched.category && Boolean(formik.errors.category)}>
          <InputLabel>Category</InputLabel>
          <Select
            name="category"
            value={formik.values.category}
            label="Category"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            disabled={mode === 'view'}
          >
            <MenuItem value="raw_milk">Raw Milk</MenuItem>
            <MenuItem value="additives">Additives</MenuItem>
            <MenuItem value="cultures">Cultures</MenuItem>
            <MenuItem value="packaging">Packaging</MenuItem>
            <MenuItem value="equipment">Equipment</MenuItem>
            <MenuItem value="chemicals">Chemicals</MenuItem>
            <MenuItem value="services">Services</MenuItem>
          </Select>
          {formik.touched.category && formik.errors.category && (
            <FormHelperText>{formik.errors.category}</FormHelperText>
          )}
        </FormControl>
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          name="contact_person"
          label="Contact Person"
          value={formik.values.contact_person}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.contact_person && Boolean(formik.errors.contact_person)}
          helperText={formik.touched.contact_person && formik.errors.contact_person}
          disabled={mode === 'view'}
          required
        />
      </Grid>
    </Grid>
  );

  const renderContactDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          name="email"
          label="Email"
          type="email"
          value={formik.values.email}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.email && Boolean(formik.errors.email)}
          helperText={formik.touched.email && formik.errors.email}
          disabled={mode === 'view'}
          required
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          name="phone"
          label="Phone"
          value={formik.values.phone}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.phone && Boolean(formik.errors.phone)}
          helperText={formik.touched.phone && formik.errors.phone}
          disabled={mode === 'view'}
          required
        />
      </Grid>
      <Grid item xs={12}>
        <TextField
          fullWidth
          name="website"
          label="Website"
          value={formik.values.website}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.website && Boolean(formik.errors.website)}
          helperText={formik.touched.website && formik.errors.website}
          disabled={mode === 'view'}
        />
      </Grid>
    </Grid>
  );

  const renderAddressInformation = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <TextField
          fullWidth
          name="address_line1"
          label="Address Line 1"
          value={formik.values.address_line1}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.address_line1 && Boolean(formik.errors.address_line1)}
          helperText={formik.touched.address_line1 && formik.errors.address_line1}
          disabled={mode === 'view'}
          required
        />
      </Grid>
      <Grid item xs={12}>
        <TextField
          fullWidth
          name="address_line2"
          label="Address Line 2"
          value={formik.values.address_line2}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.address_line2 && Boolean(formik.errors.address_line2)}
          helperText={formik.touched.address_line2 && formik.errors.address_line2}
          disabled={mode === 'view'}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          name="city"
          label="City"
          value={formik.values.city}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.city && Boolean(formik.errors.city)}
          helperText={formik.touched.city && formik.errors.city}
          disabled={mode === 'view'}
          required
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          name="state"
          label="State/Province"
          value={formik.values.state}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.state && Boolean(formik.errors.state)}
          helperText={formik.touched.state && formik.errors.state}
          disabled={mode === 'view'}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          name="postal_code"
          label="Postal Code"
          value={formik.values.postal_code}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.postal_code && Boolean(formik.errors.postal_code)}
          helperText={formik.touched.postal_code && formik.errors.postal_code}
          disabled={mode === 'view'}
        />
      </Grid>
      <Grid item xs={12}>
        <TextField
          fullWidth
          name="country"
          label="Country"
          value={formik.values.country}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.country && Boolean(formik.errors.country)}
          helperText={formik.touched.country && formik.errors.country}
          disabled={mode === 'view'}
          required
        />
      </Grid>
    </Grid>
  );

  const renderBusinessDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          name="business_registration_number"
          label="Business Registration Number"
          value={formik.values.business_registration_number}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.business_registration_number && Boolean(formik.errors.business_registration_number)}
          helperText={formik.touched.business_registration_number && formik.errors.business_registration_number}
          disabled={mode === 'view'}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          name="tax_identification_number"
          label="Tax Identification Number"
          value={formik.values.tax_identification_number}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.tax_identification_number && Boolean(formik.errors.tax_identification_number)}
          helperText={formik.touched.tax_identification_number && formik.errors.tax_identification_number}
          disabled={mode === 'view'}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          name="company_type"
          label="Company Type"
          value={formik.values.company_type}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.company_type && Boolean(formik.errors.company_type)}
          helperText={formik.touched.company_type && formik.errors.company_type}
          disabled={mode === 'view'}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          name="year_established"
          label="Year Established"
          type="number"
          value={formik.values.year_established}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.year_established && Boolean(formik.errors.year_established)}
          helperText={formik.touched.year_established && formik.errors.year_established}
          disabled={mode === 'view'}
        />
      </Grid>
    </Grid>
  );

  const renderRiskAssessment = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <FormControl fullWidth error={formik.touched.risk_level && Boolean(formik.errors.risk_level)}>
          <InputLabel>Risk Level</InputLabel>
          <Select
            name="risk_level"
            value={formik.values.risk_level}
            label="Risk Level"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            disabled={mode === 'view'}
          >
            <MenuItem value="low">
              <Box display="flex" alignItems="center" gap={1}>
                <Chip label="LOW" color="success" size="small" />
                Low Risk
              </Box>
            </MenuItem>
            <MenuItem value="medium">
              <Box display="flex" alignItems="center" gap={1}>
                <Chip label="MEDIUM" color="warning" size="small" />
                Medium Risk
              </Box>
            </MenuItem>
            <MenuItem value="high">
              <Box display="flex" alignItems="center" gap={1}>
                <Chip label="HIGH" color="error" size="small" />
                High Risk
              </Box>
            </MenuItem>
            <MenuItem value="critical">
              <Box display="flex" alignItems="center" gap={1}>
                <Chip label="CRITICAL" color="error" size="small" />
                Critical Risk
              </Box>
            </MenuItem>
          </Select>
          {formik.touched.risk_level && formik.errors.risk_level && (
            <FormHelperText>{formik.errors.risk_level}</FormHelperText>
          )}
        </FormControl>
      </Grid>
      <Grid item xs={12}>
        <TextField
          fullWidth
          name="notes"
          label="Notes"
          multiline
          rows={4}
          value={formik.values.notes}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.notes && Boolean(formik.errors.notes)}
          helperText={formik.touched.notes && formik.errors.notes}
          disabled={mode === 'view'}
        />
      </Grid>
    </Grid>
  );

  const renderReview = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Review Supplier Information
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <EnhancedCard title="Supplier Details">
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Basic Information
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Code:</Typography>
                  <Typography variant="body2" fontWeight="bold">{formik.values.supplier_code}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Name:</Typography>
                  <Typography variant="body2" fontWeight="bold">{formik.values.name}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Category:</Typography>
                  <Chip
                    label={formik.values.category.replace('_', ' ').toUpperCase()}
                    size="small"
                    icon={getCategoryIcon(formik.values.category)}
                  />
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Contact:</Typography>
                  <Typography variant="body2" fontWeight="bold">{formik.values.contact_person}</Typography>
                </Box>
              </Box>
            </CardContent>
          </EnhancedCard>
        </Grid>
        <Grid item xs={12} md={6}>
          <EnhancedCard title="Additional Information">
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Contact & Risk
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Email:</Typography>
                  <Typography variant="body2" fontWeight="bold">{formik.values.email}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Phone:</Typography>
                  <Typography variant="body2" fontWeight="bold">{formik.values.phone}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Risk Level:</Typography>
                  <Chip
                    label={formik.values.risk_level.toUpperCase()}
                    color={getRiskLevelColor(formik.values.risk_level) as any}
                    size="small"
                  />
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Country:</Typography>
                  <Typography variant="body2" fontWeight="bold">{formik.values.country}</Typography>
                </Box>
              </Box>
            </CardContent>
          </EnhancedCard>
        </Grid>
      </Grid>
    </Box>
  );

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return renderBasicInformation();
      case 1:
        return renderContactDetails();
      case 2:
        return renderAddressInformation();
      case 3:
        return renderBusinessDetails();
      case 4:
        return renderRiskAssessment();
      case 5:
        return renderReview();
      default:
        return null;
    }
  };

  // Compute per-step validity after formik is initialized
  const computeStepValid = () => {
    const schema = stepSchemas[activeStep];
    if (!schema) return true;
    try {
      schema.validateSync(formik.values, { abortEarly: false });
      return true;
    } catch {
      return false;
    }
  };
  isStepValid = computeStepValid();

  if (suppliersLoading) {
    return (
      <Box>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Loading supplier information...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            {mode === 'create' ? 'Create New Supplier' : mode === 'edit' ? 'Edit Supplier' : 'View Supplier'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {mode === 'create' ? 'Add a new supplier to the system' : 
             mode === 'edit' ? 'Update supplier information' : 'View supplier details'}
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            onClick={onCancel}
            startIcon={<Cancel />}
          >
            Cancel
          </Button>
          {mode !== 'view' && (
            <Button
              variant="contained"
              onClick={handleNext}
              startIcon={<Save />}
              disabled={formik.isSubmitting}
            >
              {activeStep === steps.length - 1 ? 'Save Supplier' : 'Next'}
            </Button>
          )}
        </Box>
      </Box>

      {/* Error Alert */}
      {suppliersError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => {}}>
          {suppliersError}
        </Alert>
      )}

      {/* Stepper */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Form Content */}
      <Paper sx={{ p: 3 }}>
        <form onSubmit={formik.handleSubmit} onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); } }}>
          {renderStepContent(activeStep)}
          
          {/* Navigation */}
          <Box display="flex" justifyContent="space-between" mt={4} sx={{ position: 'sticky', bottom: 0, py: 2, backgroundColor: 'background.paper', borderTop: '1px solid', borderColor: 'divider', zIndex: 1 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
            >
              Back
            </Button>
            <Box display="flex" gap={2}>
              <Button
                variant="outlined"
                onClick={handleReset}
              >
                Reset
              </Button>
              {activeStep === steps.length - 1 ? (
                <Button
                  variant="contained"
                  type="submit"
                  disabled={!formik.isValid || formik.isSubmitting}
                  startIcon={<Save />}
                >
                  Save Supplier
                </Button>
              ) : (
                <Button
                  variant="contained"
                  onClick={handleNext}
                  disabled={false}
                >
                  Next
                </Button>
              )}
            </Box>
          </Box>
        </form>
      </Paper>

      {/* Notification Toast */}
      <NotificationToast
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={() => setNotification({ ...notification, open: false })}
      />
    </Box>
  );
};

export default SupplierForm; 