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
  Autocomplete,
  FormControlLabel,
  Switch,
  Stack,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Save,
  Cancel,
  Inventory,
  Science,
  Security,
  LocalShipping,
  Description,
  Add,
  Delete,
  ExpandMore,
  Coronavirus as Allergen,
  Thermostat,
  Assessment,
  Schedule,
  Build,
  CheckCircle,
  Warning,
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  createMaterial,
  updateMaterial,
  fetchMaterial,
  fetchSuppliers,
} from '../../store/slices/supplierSlice';
import { RootState, AppDispatch } from '../../store';
import { 
  Material, 
  MaterialCreate, 
  MaterialUpdate, 
  MaterialSpecificationCreate,
  MaterialMicrobiologicalLimitCreate,
  MaterialPhysicalParameterCreate,
  MaterialChemicalParameterCreate
} from '../../types/supplier';
import { EnhancedCard } from '../UI';
import { NotificationToast } from '../UI';

interface MaterialFormProps {
  materialId?: number;
  onSave?: (material: Material) => void;
  onCancel?: () => void;
  mode?: 'create' | 'edit' | 'view';
}

const validationSchema = Yup.object({
  material_code: Yup.string()
    .required('Material code is required')
    .matches(/^[A-Z0-9-_]+$/, 'Material code must contain only uppercase letters, numbers, hyphens, and underscores'),
  name: Yup.string()
    .required('Material name is required')
    .min(2, 'Name must be at least 2 characters'),
  category: Yup.string()
    .required('Category is required'),
  supplier_id: Yup.number()
    .required('Supplier is required'),
  storage_conditions: Yup.string()
    .required('Storage conditions are required'),
  allergens: Yup.array()
    .of(Yup.string())
    .min(0, 'Please select applicable allergens'),
  shelf_life_days: Yup.number()
    .nullable()
    .min(1, 'Shelf life must be at least 1 day'),
});

const allergenOptions = [
  'milk', 'eggs', 'fish', 'shellfish', 'tree_nuts', 'peanuts', 'wheat', 'soybeans',
  'sesame', 'mustard', 'celery', 'lupin', 'molluscs', 'sulphites'
];

const categoryOptions = [
  { value: 'raw_milk', label: 'Raw Milk' },
  { value: 'additives', label: 'Additives' },
  { value: 'cultures', label: 'Cultures' },
  { value: 'packaging', label: 'Packaging' },
  { value: 'equipment', label: 'Equipment' },
  { value: 'chemicals', label: 'Chemicals' },
  { value: 'services', label: 'Services' },
];

const storageConditionOptions = [
  'Refrigerated (0-4°C)',
  'Frozen (-18°C or below)',
  'Room Temperature (15-25°C)',
  'Controlled Temperature (2-8°C)',
  'Dry Storage',
  'Cool, Dry Place',
  'Ambient',
];

const MaterialForm: React.FC<MaterialFormProps> = ({
  materialId,
  onSave,
  onCancel,
  mode = 'create',
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { suppliers } = useSelector((state: RootState) => state.supplier);
  const [activeStep, setActiveStep] = useState(0);
  const [specifications, setSpecifications] = useState<MaterialSpecificationCreate[]>([]);
  const [microbiologicalLimits, setMicrobiologicalLimits] = useState<MaterialMicrobiologicalLimitCreate[]>([]);
  const [physicalParameters, setPhysicalParameters] = useState<MaterialPhysicalParameterCreate[]>([]);
  const [chemicalParameters, setChemicalParameters] = useState<MaterialChemicalParameterCreate[]>([]);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ open: false, message: '', severity: 'info' });

  const steps = [
    'Basic Information',
    'Specifications',
    'Safety & Compliance',
    'Review & Submit'
  ];

  const formik = useFormik<MaterialCreate>({
    initialValues: {
      material_code: '',
      name: '',
      category: '',
      description: '',
      supplier_id: 0,
      supplier_material_code: '',
      allergens: [],
      storage_conditions: '',
      shelf_life_days: undefined,
      handling_instructions: '',
      specifications: [],
      hygiene_requirements: [],
      microbiological_limits: [],
      physical_parameters: [],
      chemical_parameters: [],
      packaging_requirements: [],
      transportation_conditions: '',
      temperature_requirements: {
        min_temp: undefined,
        max_temp: undefined,
        unit: 'celsius',
      },
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        const materialData = {
          ...values,
          specifications,
          microbiological_limits: microbiologicalLimits,
          physical_parameters: physicalParameters,
          chemical_parameters: chemicalParameters,
        };

        let result;
        if (mode === 'create') {
          result = await dispatch(createMaterial(materialData)).unwrap();
        } else if (mode === 'edit' && materialId) {
          result = await dispatch(updateMaterial({ materialId, materialData: materialData as MaterialUpdate })).unwrap();
        }

        setNotification({
          open: true,
          message: `Material ${mode === 'create' ? 'created' : 'updated'} successfully`,
          severity: 'success',
        });

        if (onSave) {
          onSave(result);
        }
      } catch (error: any) {
        setNotification({
          open: true,
          message: error.message || 'Failed to save material',
          severity: 'error',
        });
      }
    },
  });

  useEffect(() => {
    // Load suppliers for dropdown
    dispatch(fetchSuppliers({}));

    // Load material data if editing
    if (materialId && mode !== 'create') {
      dispatch(fetchMaterial(materialId));
    }
  }, [dispatch, materialId, mode]);

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const addSpecification = () => {
    setSpecifications([
      ...specifications,
      {
        parameter_name: '',
        parameter_value: '',
        unit: '',
        min_value: undefined,
        max_value: undefined,
        target_value: undefined,
        test_method: '',
        frequency: '',
      },
    ]);
  };

  const removeSpecification = (index: number) => {
    setSpecifications(specifications.filter((_, i) => i !== index));
  };

  const updateSpecification = (index: number, field: string, value: any) => {
    const updated = [...specifications];
    updated[index] = { ...updated[index], [field]: value };
    setSpecifications(updated);
  };

  const addMicrobiologicalLimit = () => {
    setMicrobiologicalLimits([
      ...microbiologicalLimits,
      {
        microorganism: '',
        limit_value: '',
        unit: 'CFU/g',
        test_method: '',
        frequency: 'Every batch',
      },
    ]);
  };

  const removeMicrobiologicalLimit = (index: number) => {
    setMicrobiologicalLimits(microbiologicalLimits.filter((_, i) => i !== index));
  };

  const updateMicrobiologicalLimit = (index: number, field: string, value: any) => {
    const updated = [...microbiologicalLimits];
    updated[index] = { ...updated[index], [field]: value };
    setMicrobiologicalLimits(updated);
  };

  const addPhysicalParameter = () => {
    setPhysicalParameters([
      ...physicalParameters,
      {
        parameter: '',
        value: '',
        unit: '',
        acceptable_range: '',
        test_method: '',
      },
    ]);
  };

  const removePhysicalParameter = (index: number) => {
    setPhysicalParameters(physicalParameters.filter((_, i) => i !== index));
  };

  const updatePhysicalParameter = (index: number, field: string, value: any) => {
    const updated = [...physicalParameters];
    updated[index] = { ...updated[index], [field]: value };
    setPhysicalParameters(updated);
  };

  const addChemicalParameter = () => {
    setChemicalParameters([
      ...chemicalParameters,
      {
        parameter: '',
        value: '',
        unit: '',
        acceptable_range: '',
        test_method: '',
      },
    ]);
  };

  const removeChemicalParameter = (index: number) => {
    setChemicalParameters(chemicalParameters.filter((_, i) => i !== index));
  };

  const updateChemicalParameter = (index: number, field: string, value: any) => {
    const updated = [...chemicalParameters];
    updated[index] = { ...updated[index], [field]: value };
    setChemicalParameters(updated);
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                id="material_code"
                name="material_code"
                label="Material Code *"
                value={formik.values.material_code}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.material_code && Boolean(formik.errors.material_code)}
                helperText={formik.touched.material_code && formik.errors.material_code}
                placeholder="e.g., RM-MILK-001"
                disabled={mode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                id="name"
                name="name"
                label="Material Name *"
                value={formik.values.name}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={formik.touched.name && formik.errors.name}
                disabled={mode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={formik.touched.category && Boolean(formik.errors.category)}>
                <InputLabel>Category *</InputLabel>
                <Select
                  id="category"
                  name="category"
                  value={formik.values.category}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  disabled={mode === 'view'}
                >
                  {categoryOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
                {formik.touched.category && formik.errors.category && (
                  <FormHelperText>{formik.errors.category}</FormHelperText>
                )}
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={formik.touched.supplier_id && Boolean(formik.errors.supplier_id)}>
                <InputLabel>Supplier *</InputLabel>
                <Select
                  id="supplier_id"
                  name="supplier_id"
                  value={formik.values.supplier_id}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  disabled={mode === 'view'}
                >
                  {suppliers?.items?.map((supplier) => (
                    <MenuItem key={supplier.id} value={supplier.id}>
                      {supplier.name} ({supplier.supplier_code})
                    </MenuItem>
                  ))}
                </Select>
                {formik.touched.supplier_id && formik.errors.supplier_id && (
                  <FormHelperText>{formik.errors.supplier_id}</FormHelperText>
                )}
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                id="supplier_material_code"
                name="supplier_material_code"
                label="Supplier Material Code"
                value={formik.values.supplier_material_code}
                onChange={formik.handleChange}
                disabled={mode === 'view'}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                id="shelf_life_days"
                name="shelf_life_days"
                label="Shelf Life (Days)"
                type="number"
                value={formik.values.shelf_life_days || ''}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.shelf_life_days && Boolean(formik.errors.shelf_life_days)}
                helperText={formik.touched.shelf_life_days && formik.errors.shelf_life_days}
                disabled={mode === 'view'}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                id="description"
                name="description"
                label="Description"
                multiline
                rows={3}
                value={formik.values.description}
                onChange={formik.handleChange}
                disabled={mode === 'view'}
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Technical Specifications
            </Typography>
            
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle1">General Specifications</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Stack spacing={2}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body1">Specifications</Typography>
                    <Button
                      startIcon={<Add />}
                      onClick={addSpecification}
                      disabled={mode === 'view'}
                    >
                      Add Specification
                    </Button>
                  </Box>
                  {specifications.map((spec, index) => (
                    <Card key={index} variant="outlined">
                      <CardContent>
                        <Grid container spacing={2}>
                          <Grid item xs={12} md={3}>
                            <TextField
                              fullWidth
                              label="Parameter Name"
                              value={spec.parameter_name}
                              onChange={(e) => updateSpecification(index, 'parameter_name', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={2}>
                            <TextField
                              fullWidth
                              label="Value"
                              value={spec.parameter_value}
                              onChange={(e) => updateSpecification(index, 'parameter_value', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={2}>
                            <TextField
                              fullWidth
                              label="Unit"
                              value={spec.unit}
                              onChange={(e) => updateSpecification(index, 'unit', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={3}>
                            <TextField
                              fullWidth
                              label="Test Method"
                              value={spec.test_method}
                              onChange={(e) => updateSpecification(index, 'test_method', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={1}>
                            <IconButton
                              color="error"
                              onClick={() => removeSpecification(index)}
                              disabled={mode === 'view'}
                            >
                              <Delete />
                            </IconButton>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  ))}
                </Stack>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle1">Physical Parameters</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Stack spacing={2}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body1">Physical Parameters</Typography>
                    <Button
                      startIcon={<Add />}
                      onClick={addPhysicalParameter}
                      disabled={mode === 'view'}
                    >
                      Add Parameter
                    </Button>
                  </Box>
                  {physicalParameters.map((param, index) => (
                    <Card key={index} variant="outlined">
                      <CardContent>
                        <Grid container spacing={2}>
                          <Grid item xs={12} md={3}>
                            <TextField
                              fullWidth
                              label="Parameter"
                              value={param.parameter}
                              onChange={(e) => updatePhysicalParameter(index, 'parameter', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={2}>
                            <TextField
                              fullWidth
                              label="Value"
                              value={param.value}
                              onChange={(e) => updatePhysicalParameter(index, 'value', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={2}>
                            <TextField
                              fullWidth
                              label="Unit"
                              value={param.unit}
                              onChange={(e) => updatePhysicalParameter(index, 'unit', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={3}>
                            <TextField
                              fullWidth
                              label="Test Method"
                              value={param.test_method}
                              onChange={(e) => updatePhysicalParameter(index, 'test_method', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={1}>
                            <IconButton
                              color="error"
                              onClick={() => removePhysicalParameter(index)}
                              disabled={mode === 'view'}
                            >
                              <Delete />
                            </IconButton>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  ))}
                </Stack>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle1">Chemical Parameters</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Stack spacing={2}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body1">Chemical Parameters</Typography>
                    <Button
                      startIcon={<Add />}
                      onClick={addChemicalParameter}
                      disabled={mode === 'view'}
                    >
                      Add Parameter
                    </Button>
                  </Box>
                  {chemicalParameters.map((param, index) => (
                    <Card key={index} variant="outlined">
                      <CardContent>
                        <Grid container spacing={2}>
                          <Grid item xs={12} md={3}>
                            <TextField
                              fullWidth
                              label="Parameter"
                              value={param.parameter}
                              onChange={(e) => updateChemicalParameter(index, 'parameter', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={2}>
                            <TextField
                              fullWidth
                              label="Value"
                              value={param.value}
                              onChange={(e) => updateChemicalParameter(index, 'value', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={2}>
                            <TextField
                              fullWidth
                              label="Unit"
                              value={param.unit}
                              onChange={(e) => updateChemicalParameter(index, 'unit', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={3}>
                            <TextField
                              fullWidth
                              label="Test Method"
                              value={param.test_method}
                              onChange={(e) => updateChemicalParameter(index, 'test_method', e.target.value)}
                              disabled={mode === 'view'}
                            />
                          </Grid>
                          <Grid item xs={12} md={1}>
                            <IconButton
                              color="error"
                              onClick={() => removeChemicalParameter(index)}
                              disabled={mode === 'view'}
                            >
                              <Delete />
                            </IconButton>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  ))}
                </Stack>
              </AccordionDetails>
            </Accordion>
          </Box>
        );

      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Safety & Compliance Information
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControl fullWidth error={formik.touched.storage_conditions && Boolean(formik.errors.storage_conditions)}>
                  <Autocomplete
                    options={storageConditionOptions}
                    value={formik.values.storage_conditions}
                    onChange={(_, value) => formik.setFieldValue('storage_conditions', value || '')}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Storage Conditions *"
                        error={formik.touched.storage_conditions && Boolean(formik.errors.storage_conditions)}
                        helperText={formik.touched.storage_conditions && formik.errors.storage_conditions}
                      />
                    )}
                    disabled={mode === 'view'}
                    freeSolo
                  />
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Allergen Information
                </Typography>
                <Autocomplete
                  multiple
                  options={allergenOptions}
                  value={formik.values.allergens}
                  onChange={(_, value) => formik.setFieldValue('allergens', value)}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip
                        variant="outlined"
                        label={option.charAt(0).toUpperCase() + option.slice(1).replace('_', ' ')}
                        {...getTagProps({ index })}
                        icon={<Allergen />}
                        key={option}
                      />
                    ))
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Allergens"
                      placeholder="Select allergens if applicable"
                      helperText="Select all allergens that may be present in this material"
                    />
                  )}
                  disabled={mode === 'view'}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  id="temperature_requirements.min_temp"
                  name="temperature_requirements.min_temp"
                  label="Minimum Temperature"
                  type="number"
                  value={formik.values.temperature_requirements?.min_temp || ''}
                  onChange={(e) => formik.setFieldValue('temperature_requirements.min_temp', e.target.value ? Number(e.target.value) : undefined)}
                  disabled={mode === 'view'}
                  InputProps={{
                    endAdornment: '°C',
                  }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  id="temperature_requirements.max_temp"
                  name="temperature_requirements.max_temp"
                  label="Maximum Temperature"
                  type="number"
                  value={formik.values.temperature_requirements?.max_temp || ''}
                  onChange={(e) => formik.setFieldValue('temperature_requirements.max_temp', e.target.value ? Number(e.target.value) : undefined)}
                  disabled={mode === 'view'}
                  InputProps={{
                    endAdornment: '°C',
                  }}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  id="handling_instructions"
                  name="handling_instructions"
                  label="Handling Instructions"
                  multiline
                  rows={3}
                  value={formik.values.handling_instructions}
                  onChange={formik.handleChange}
                  helperText="Special handling requirements and precautions"
                  disabled={mode === 'view'}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  id="transportation_conditions"
                  name="transportation_conditions"
                  label="Transportation Conditions"
                  value={formik.values.transportation_conditions}
                  onChange={formik.handleChange}
                  helperText="Specific transportation requirements and conditions"
                  disabled={mode === 'view'}
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Microbiological Limits
                </Typography>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="body2" color="text.secondary">
                    Define microbiological safety criteria for this material
                  </Typography>
                  <Button
                    startIcon={<Add />}
                    onClick={addMicrobiologicalLimit}
                    disabled={mode === 'view'}
                  >
                    Add Limit
                  </Button>
                </Box>
                {microbiologicalLimits.map((limit, index) => (
                  <Card key={index} variant="outlined" sx={{ mb: 2 }}>
                    <CardContent>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={3}>
                          <TextField
                            fullWidth
                            label="Microorganism"
                            value={limit.microorganism}
                            onChange={(e) => updateMicrobiologicalLimit(index, 'microorganism', e.target.value)}
                            placeholder="e.g., E. coli"
                            disabled={mode === 'view'}
                          />
                        </Grid>
                        <Grid item xs={12} md={2}>
                          <TextField
                            fullWidth
                            label="Limit Value"
                            value={limit.limit_value}
                            onChange={(e) => updateMicrobiologicalLimit(index, 'limit_value', e.target.value)}
                            placeholder="e.g., <10"
                            disabled={mode === 'view'}
                          />
                        </Grid>
                        <Grid item xs={12} md={2}>
                          <FormControl fullWidth>
                            <InputLabel>Unit</InputLabel>
                            <Select
                              value={limit.unit}
                              onChange={(e) => updateMicrobiologicalLimit(index, 'unit', e.target.value)}
                              disabled={mode === 'view'}
                            >
                              <MenuItem value="CFU/g">CFU/g</MenuItem>
                              <MenuItem value="CFU/ml">CFU/ml</MenuItem>
                              <MenuItem value="MPN/g">MPN/g</MenuItem>
                              <MenuItem value="presence/absence">Presence/Absence</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>
                        <Grid item xs={12} md={3}>
                          <TextField
                            fullWidth
                            label="Test Method"
                            value={limit.test_method}
                            onChange={(e) => updateMicrobiologicalLimit(index, 'test_method', e.target.value)}
                            disabled={mode === 'view'}
                          />
                        </Grid>
                        <Grid item xs={12} md={1}>
                          <IconButton
                            color="error"
                            onClick={() => removeMicrobiologicalLimit(index)}
                            disabled={mode === 'view'}
                          >
                            <Delete />
                          </IconButton>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                ))}
              </Grid>
            </Grid>
          </Box>
        );

      case 3:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Review Material Information
            </Typography>
            
            <Alert severity="info" sx={{ mb: 3 }}>
              Please review all material information before submitting. This material will be pending approval after creation.
            </Alert>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Basic Information
                    </Typography>
                    <Stack spacing={1}>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Material Code:</Typography>
                        <Typography variant="body1" fontWeight="bold">{formik.values.material_code}</Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Name:</Typography>
                        <Typography variant="body1">{formik.values.name}</Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Category:</Typography>
                        <Typography variant="body1">
                          {categoryOptions.find(cat => cat.value === formik.values.category)?.label}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Supplier:</Typography>
                        <Typography variant="body1">
                          {suppliers?.items?.find(s => s.id === formik.values.supplier_id)?.name}
                        </Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Safety Information
                    </Typography>
                    <Stack spacing={1}>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Storage Conditions:</Typography>
                        <Typography variant="body1">{formik.values.storage_conditions}</Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Shelf Life:</Typography>
                        <Typography variant="body1">
                          {formik.values.shelf_life_days ? `${formik.values.shelf_life_days} days` : 'Not specified'}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Allergens:</Typography>
                        <Box display="flex" gap={0.5} flexWrap="wrap" mt={0.5}>
                          {formik.values.allergens.length > 0 ? (
                            formik.values.allergens.map((allergen) => (
                              <Chip 
                                key={allergen} 
                                label={allergen.charAt(0).toUpperCase() + allergen.slice(1).replace('_', ' ')} 
                                size="small" 
                                icon={<Allergen />}
                              />
                            ))
                          ) : (
                            <Typography variant="body2" color="text.secondary">None declared</Typography>
                          )}
                        </Box>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Specifications Summary
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={4}>
                        <Typography variant="subtitle2" gutterBottom>General Specifications</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {specifications.length} specification(s) defined
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Typography variant="subtitle2" gutterBottom>Physical Parameters</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {physicalParameters.length} parameter(s) defined
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Typography variant="subtitle2" gutterBottom>Chemical Parameters</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {chemicalParameters.length} parameter(s) defined
                        </Typography>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" gutterBottom>Microbiological Limits</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {microbiologicalLimits.length} limit(s) defined
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        );

      default:
        return 'Unknown step';
    }
  };

  const canProceedToNext = () => {
    // Ensure Next button is always active during material creation flow
    if (mode === 'create') {
      return true;
    }
    switch (activeStep) {
      case 0:
        return formik.values.material_code && 
               formik.values.name && 
               formik.values.category && 
               formik.values.supplier_id &&
               formik.values.storage_conditions;
      case 1:
      case 2:
        return true;
      default:
        return false;
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Form Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" fontWeight="bold" gutterBottom>
          {mode === 'create' ? 'Create New Material' : mode === 'edit' ? 'Edit Material' : 'View Material'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {mode === 'create' 
            ? 'Add a new material to your supplier inventory with complete specifications and safety information'
            : mode === 'edit'
            ? 'Update material information and specifications'
            : 'View material details and specifications'
          }
        </Typography>
      </Box>

      {/* Progress Stepper */}
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Form Content */}
      <form onSubmit={formik.handleSubmit}>
        <Paper sx={{ p: 3, mb: 3 }}>
          {renderStepContent(activeStep)}
        </Paper>

        {/* Form Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button
            onClick={onCancel}
            startIcon={<Cancel />}
          >
            Cancel
          </Button>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
            >
              Back
            </Button>

            {activeStep === steps.length - 1 ? (
              <Button
                type="submit"
                variant="contained"
                startIcon={formik.isSubmitting ? <Schedule /> : <Save />}
                disabled={formik.isSubmitting || mode === 'view'}
              >
                {formik.isSubmitting 
                  ? 'Saving...' 
                  : mode === 'create' 
                    ? 'Create Material' 
                    : 'Save Changes'
                }
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!canProceedToNext()}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </form>

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

export default MaterialForm;