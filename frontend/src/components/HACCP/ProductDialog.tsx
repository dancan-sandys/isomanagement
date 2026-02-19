import React, { useState, useEffect, useMemo } from 'react';
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
  Grid,
  Alert,
  CircularProgress,
  Autocomplete,
  Box,
  Chip,
  FormHelperText,
  Typography,
  Stack,
} from '@mui/material';
import GlobalStyles from '@mui/material/GlobalStyles';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { createProduct, updateProduct, fetchContactSurfaces } from '../../store/slices/haccpSlice';
import { supplierAPI } from '../../services/supplierAPI';
import { Material } from '../../types/supplier';
import MaterialForm from '../Materials/MaterialForm';
import ContactSurfaceDialog from './ContactSurfaceDialog';
import { ContactSurface } from '../../types/haccp';
import { Add as AddIcon } from '@mui/icons-material';

interface MaterialOption {
  id: number;
  material_id: number;
  material_code?: string;
  name: string;
  supplier_id?: number;
  supplier_name?: string;
  category?: string;
}

interface CompositionItem {
  material_id: number;
  material_code?: string;
  material_name?: string;
  supplier_id?: number;
  supplier_name?: string;
  category?: string;
  percentage?: number;
  unit?: string;
  notes?: string;
  is_high_risk?: boolean;
}

interface ProductFormData {
  product_code: string;
  name: string;
  description: string;
  composition: CompositionItem[];
  high_risk_ingredients: CompositionItem | null;
  physical_chemical_biological_description: string;
  main_processing_steps: string;
  distribution_serving_methods: string;
  consumer_groups: string;
  storage_conditions: string;
  shelf_life_days: string;
  packaging_type: string;
  inherent_hazards: string;
  fs_acceptance_criteria: string;
  law_regulation_requirement: string;
  haccp_plan_approved: boolean;
  haccp_plan_version: string;
  contact_surface_ids: number[];
}

interface ProductDialogProps {
  open: boolean;
  onClose: () => void;
  product?: any; // For editing existing product
  onSuccess?: () => void; // Callback for successful save
}

interface MaterialQuickCreateDialogProps {
  open: boolean;
  onClose: () => void;
  onCreated: (material: Material) => void;
}

const MaterialQuickCreateDialog: React.FC<MaterialQuickCreateDialogProps> = ({
  open,
  onClose,
  onCreated,
}) => {
  useEffect(() => {
    if (open) {
      document.body.classList.add('material-dialog-active');
    } else {
      document.body.classList.remove('material-dialog-active');
    }
    return () => {
      document.body.classList.remove('material-dialog-active');
    };
  }, [open]);

  const handleMaterialSaved = (material: Material) => {
    onCreated(material);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      keepMounted
      disableEnforceFocus
      sx={{ zIndex: (theme) => theme.zIndex.modal + 30 }}
      BackdropProps={{ sx: { zIndex: (theme) => theme.zIndex.modal + 29 } }}
      PaperProps={{
        id: 'material-create-dialog',
        sx: {
          position: 'relative',
          zIndex: (theme) => theme.zIndex.modal + 30,
          '& .MuiAutocomplete-popper, & .MuiPopper-root': {
            zIndex: (theme) => theme.zIndex.modal + 40,
          },
          '& .MuiPopover-root, & .MuiMenu-paper': {
            zIndex: (theme) => theme.zIndex.modal + 40,
          },
        },
      }}
    >
      <DialogTitle>Add Raw Material</DialogTitle>
      <DialogContent dividers sx={{ p: 0 }}>
        <MaterialForm mode="create" onSave={handleMaterialSaved} onCancel={onClose} />
      </DialogContent>
    </Dialog>
  );
};

const ProductDialog: React.FC<ProductDialogProps> = ({ open, onClose, product, onSuccess }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { loading, error, contactSurfaces, contactSurfacesLoading } = useSelector((state: RootState) => state.haccp);

  const [formData, setFormData] = useState<ProductFormData>({
    product_code: '',
    name: '',
    description: '',
    composition: [],
    high_risk_ingredients: null,
    physical_chemical_biological_description: '',
    main_processing_steps: '',
    distribution_serving_methods: '',
    consumer_groups: '',
    storage_conditions: '',
    shelf_life_days: '',
    packaging_type: '',
    inherent_hazards: '',
    fs_acceptance_criteria: '',
    law_regulation_requirement: '',
    haccp_plan_approved: false,
    haccp_plan_version: '',
    contact_surface_ids: [],
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [materialOptions, setMaterialOptions] = useState<MaterialOption[]>([]);
  const [materialsLoading, setMaterialsLoading] = useState(false);
  const [materialsError, setMaterialsError] = useState<string | null>(null);
  const [materialDialogOpen, setMaterialDialogOpen] = useState(false);
  const [contactSurfaceDialogOpen, setContactSurfaceDialogOpen] = useState(false);
  const selectedContactSurfaces = useMemo(
    () => contactSurfaces.filter((surface) => formData.contact_surface_ids.includes(surface.id)),
    [contactSurfaces, formData.contact_surface_ids]
  );

  useEffect(() => {
    if (open) {
      dispatch(fetchContactSurfaces(undefined));
    }
  }, [dispatch, open]);

  useEffect(() => {
    if (product) {
      const rawComposition = Array.isArray(product.composition) ? product.composition : [];
      const compositionItems: CompositionItem[] = rawComposition.map((item: any) => ({
        material_id: item.material_id,
        material_code: item.material_code,
        material_name: item.material_name,
        supplier_id: item.supplier_id,
        supplier_name: item.supplier_name,
        category: item.category,
        percentage: item.percentage,
        unit: item.unit,
        notes: item.notes,
        is_high_risk: item.is_high_risk,
      }));
      const highRiskId = product.high_risk_ingredients?.material_id ?? null;
      const compositionWithFlags = markHighRisk(compositionItems, highRiskId);
      const highRiskItem = product.high_risk_ingredients
        ? {
            material_id: product.high_risk_ingredients.material_id,
            material_code: product.high_risk_ingredients.material_code,
            material_name: product.high_risk_ingredients.material_name,
            supplier_id: product.high_risk_ingredients.supplier_id,
            supplier_name: product.high_risk_ingredients.supplier_name,
            category: product.high_risk_ingredients.category,
            percentage: product.high_risk_ingredients.percentage,
            unit: product.high_risk_ingredients.unit,
            notes: product.high_risk_ingredients.notes,
            is_high_risk: true,
          }
        : null;

      setFormData({
        product_code: product.product_code || '',
        name: product.name || '',
        description: product.description || '',
        composition: compositionWithFlags,
        high_risk_ingredients: highRiskItem,
        physical_chemical_biological_description: product.physical_chemical_biological_description || '',
        main_processing_steps: product.main_processing_steps || '',
        distribution_serving_methods: product.distribution_serving_methods || '',
        consumer_groups: product.consumer_groups || '',
        storage_conditions: product.storage_conditions || '',
        shelf_life_days: product.shelf_life_days?.toString() || '',
        packaging_type: product.packaging_type || '',
        inherent_hazards: product.inherent_hazards || '',
        fs_acceptance_criteria: product.fs_acceptance_criteria || '',
        law_regulation_requirement: product.law_regulation_requirement || '',
        haccp_plan_approved: product.haccp_plan_approved || false,
        haccp_plan_version: product.haccp_plan_version || '',
        contact_surface_ids: (product.contact_surfaces || []).map((surface: any) => surface.id),
      });
    } else {
      setFormData({
        product_code: '',
        name: '',
        description: '',
        composition: [],
        high_risk_ingredients: null,
        physical_chemical_biological_description: '',
        main_processing_steps: '',
        distribution_serving_methods: '',
        consumer_groups: '',
        storage_conditions: '',
        shelf_life_days: '',
        packaging_type: '',
        inherent_hazards: '',
        fs_acceptance_criteria: '',
        law_regulation_requirement: '',
        haccp_plan_approved: false,
        haccp_plan_version: '',
        contact_surface_ids: [],
      });
    }
    setFormErrors({});
  }, [product, open]);

  useEffect(() => {
    let active = true;
    const loadMaterials = async () => {
      setMaterialsLoading(true);
      setMaterialsError(null);
      try {
        const res: any = await supplierAPI.getMaterials({ size: 200, approval_status: 'approved' });
        if (!active) return;
        const items = res?.data?.items || res?.items || res?.data || [];
        const mapped: MaterialOption[] = items.map((item: any) => ({
          id: item.id,
          material_id: item.id,
          material_code: item.material_code,
          name: item.name,
          supplier_id: item.supplier_id,
          supplier_name: item.supplier_name,
          category: item.category,
        }));
        setMaterialOptions(mapped);
      } catch (error) {
        if (!active) return;
        setMaterialOptions([]);
        setMaterialsError('Failed to load raw materials.');
      } finally {
        if (active) {
          setMaterialsLoading(false);
        }
      }
    };

    loadMaterials();
    return () => {
      active = false;
    };
  }, []);

  const handleInputChange = (field: keyof ProductFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    clearFieldError(field as string);
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};

    if (!formData.product_code.trim()) {
      errors.product_code = 'Product code is required';
    }
    if (!formData.name.trim()) {
      errors.name = 'Product name is required';
    }
    if (!formData.composition.length) {
      errors.composition = 'Select at least one raw material';
    }
    if (!formData.high_risk_ingredients) {
      errors.high_risk_ingredients = 'Select a high-risk ingredient';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      const compositionPayload = serializeComposition(formData.composition);
      const highRiskPayload = serializeHighRisk(formData.high_risk_ingredients);

      const submitData = {
        ...formData,
        composition: compositionPayload,
        high_risk_ingredients: highRiskPayload,
        shelf_life_days: formData.shelf_life_days ? parseInt(formData.shelf_life_days, 10) : null,
        contact_surface_ids: formData.contact_surface_ids,
      };

      if (product) {
        await dispatch(updateProduct({ productId: product.id, productData: submitData })).unwrap();
      } else {
        // For creation, exclude haccp_plan_approved and haccp_plan_version
        const { haccp_plan_approved, haccp_plan_version, ...createData } = submitData;
        console.log('Sending product data:', createData);
        await dispatch(createProduct(createData)).unwrap();
      }
      
      onClose();
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      console.error('Failed to save product - Full error:', error);
      console.error('Error response:', error?.response?.data);
      // Error is already handled by the Redux slice
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  const markHighRisk = (items: CompositionItem[], highRiskId?: number | null) =>
    items.map(item => ({ ...item, is_high_risk: !!highRiskId && item.material_id === highRiskId }));

  const clearFieldError = (field: string) => {
    if (formErrors[field]) {
      setFormErrors(prev => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const handleMaterialCreated = (material: Material) => {
    const newOption: MaterialOption = {
      id: material.id,
      material_id: material.id,
      material_code: material.material_code,
      name: material.name,
      supplier_id: material.supplier_id,
      supplier_name: material.supplier_name,
      category: material.category,
    };

    setMaterialOptions((prev) => {
      const exists = prev.some((option) => option.material_id === material.id);
      if (exists) {
        return prev.map((option) =>
          option.material_id === material.id ? newOption : option
        );
      }
      return [...prev, newOption];
    });

    setMaterialsError(null);

    setFormData((prev) => {
      const compositionExists = prev.composition.some(
        (item) => item.material_id === material.id
      );

      const newCompositionItem: CompositionItem = {
        material_id: material.id,
        material_code: material.material_code,
        material_name: material.name,
        supplier_id: material.supplier_id,
        supplier_name: material.supplier_name,
        category: material.category,
      };

      const baseComposition = compositionExists
        ? prev.composition
        : [...prev.composition, newCompositionItem];

      const shouldSetHighRisk = !prev.high_risk_ingredients;
      const targetHighRiskId = shouldSetHighRisk
        ? material.id
        : prev.high_risk_ingredients?.material_id ?? null;

      const compositionWithFlags = markHighRisk(baseComposition, targetHighRiskId);
      const updatedHighRisk = targetHighRiskId
        ? compositionWithFlags.find((item) => item.material_id === targetHighRiskId) || null
        : null;

      return {
        ...prev,
        composition: compositionWithFlags,
        high_risk_ingredients: updatedHighRisk
          ? { ...updatedHighRisk }
          : prev.high_risk_ingredients,
      };
    });

    clearFieldError('composition');
    clearFieldError('high_risk_ingredients');
  };

  const handleContactSurfaceSelection = (value: ContactSurface[]) => {
    setFormData((prev) => ({ ...prev, contact_surface_ids: value.map((surface) => surface.id) }));
  };

  const handleContactSurfaceCreated = (surface: ContactSurface) => {
    setFormData((prev) => {
      const nextIds = new Set(prev.contact_surface_ids);
      nextIds.add(surface.id);
      return { ...prev, contact_surface_ids: Array.from(nextIds) };
    });
  };

  const handleCompositionChange = (_: any, selected: MaterialOption[]) => {
    const updatedCompositionRaw: CompositionItem[] = selected.map(option => {
      const existing = formData.composition.find(item => item.material_id === option.material_id);
      return {
        material_id: option.material_id,
        material_code: option.material_code,
        material_name: option.name,
        supplier_id: option.supplier_id,
        supplier_name: option.supplier_name,
        category: option.category,
        percentage: existing?.percentage,
        unit: existing?.unit,
        notes: existing?.notes,
      };
    });

    setFormData(prev => {
      const currentHighRiskId = prev.high_risk_ingredients?.material_id ?? null;
      const compositionWithFlags = markHighRisk(updatedCompositionRaw, currentHighRiskId);
      const updatedHighRisk = currentHighRiskId
        ? compositionWithFlags.find(item => item.material_id === currentHighRiskId)
        : null;
      return {
        ...prev,
        composition: compositionWithFlags,
        high_risk_ingredients: updatedHighRisk ? { ...updatedHighRisk } : null,
      };
    });

    if (selected.length === 0) {
      setFormErrors(prev => ({ ...prev, composition: 'Select at least one raw material' }));
    } else {
      clearFieldError('composition');
    }
    if (formData.high_risk_ingredients && selected.some(option => option.material_id === formData.high_risk_ingredients!.material_id)) {
      clearFieldError('high_risk_ingredients');
    } else if (formData.high_risk_ingredients) {
      setFormErrors(prev => ({ ...prev, high_risk_ingredients: 'Select a high-risk ingredient from the composition' }));
    }
  };

  const handleHighRiskSelect = (materialId: number | null) => {
    setFormData(prev => {
      const compositionWithFlags = markHighRisk(prev.composition, materialId);
      const selectedItem = materialId
        ? compositionWithFlags.find(item => item.material_id === materialId) || null
        : null;
      return {
        ...prev,
        composition: compositionWithFlags,
        high_risk_ingredients: selectedItem ? { ...selectedItem } : null,
      };
    });

    if (materialId) {
      clearFieldError('high_risk_ingredients');
    } else {
      setFormErrors(prev => ({ ...prev, high_risk_ingredients: 'Select a high-risk ingredient' }));
    }
  };

  const serializeComposition = (items: CompositionItem[]) =>
    items.map(item => {
      const payload: any = {
        material_id: item.material_id,
        material_code: item.material_code,
        material_name: item.material_name,
        supplier_id: item.supplier_id,
        supplier_name: item.supplier_name,
        category: item.category,
      };
      if (item.percentage !== undefined && item.percentage !== null) {
        payload.percentage = item.percentage;
      }
      if (item.unit) {
        payload.unit = item.unit;
      }
      if (item.notes) {
        payload.notes = item.notes;
      }
      if (item.is_high_risk) {
        payload.is_high_risk = true;
      }
      return payload;
    });

  const serializeHighRisk = (item: CompositionItem | null) => {
    if (!item) return null;
    const payload: any = {
      material_id: item.material_id,
      material_code: item.material_code,
      material_name: item.material_name,
      supplier_id: item.supplier_id,
      supplier_name: item.supplier_name,
      category: item.category,
      is_high_risk: true,
    };
    if (item.percentage !== undefined && item.percentage !== null) {
      payload.percentage = item.percentage;
    }
    if (item.unit) {
      payload.unit = item.unit;
    }
    if (item.notes) {
      payload.notes = item.notes;
    }
    return payload;
  };

  const selectedCompositionOptions = useMemo(
    () =>
      materialOptions.filter(option =>
        formData.composition.some(item => item.material_id === option.material_id)
      ),
    [materialOptions, formData.composition]
  );

  return (
    <>
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {product ? 'Edit Product' : 'Add New Product'}
        </DialogTitle>
        <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Product Code"
              value={formData.product_code}
              onChange={(e) => handleInputChange('product_code', e.target.value)}
              error={!!formErrors.product_code}
              helperText={formErrors.product_code}
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Product Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              error={!!formErrors.name}
              helperText={formErrors.name}
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              multiline
              rows={3}
              placeholder="General product description"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <Stack
                direction={{ xs: 'column', sm: 'row' }}
                spacing={1}
                alignItems={{ xs: 'stretch', sm: 'flex-start' }}
              >
                <Box flex={1}>
                  <Autocomplete
                    multiple
                    options={materialOptions}
                    value={selectedCompositionOptions}
                    onChange={handleCompositionChange}
                    loading={materialsLoading}
                    disableCloseOnSelect
                    isOptionEqualToValue={(option, value) => option.material_id === value.material_id}
                    getOptionLabel={(option) => {
                      if (!option) return '';
                      const code = option.material_code ? `${option.material_code} — ` : '';
                      return `${code}${option.name}`;
                    }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Composition (Raw Materials)"
                        placeholder="Select raw materials"
                        error={!!formErrors.composition}
                        helperText={formErrors.composition}
                      />
                    )}
                  />
                </Box>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={() => setMaterialDialogOpen(true)}
                  sx={{ whiteSpace: 'nowrap' }}
                >
                  Add Material
                </Button>
              </Stack>
            </FormControl>
            {materialsError && (
              <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                {materialsError}
              </Typography>
            )}
            {formData.composition.length > 0 && (
              <Box sx={{ mt: 1 }}>
                {formData.composition.map(item => (
                  <Chip
                    key={item.material_id}
                    label={`${item.material_code ? `${item.material_code} — ` : ''}${item.material_name || 'Unnamed material'}${item.is_high_risk ? ' • High Risk' : ''}`}
                    color={item.is_high_risk ? 'warning' : 'default'}
                    size="small"
                    sx={{ mr: 0.75, mb: 0.75 }}
                  />
                ))}
              </Box>
            )}
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth error={!!formErrors.high_risk_ingredients} disabled={!formData.composition.length}>
              <InputLabel id="high-risk-ingredient-label">High-risk Ingredient</InputLabel>
              <Select
                labelId="high-risk-ingredient-label"
                label="High-risk Ingredient"
                value={formData.high_risk_ingredients?.material_id ?? ''}
                onChange={(e) => {
                  const value = e.target.value === '' ? null : Number(e.target.value);
                  handleHighRiskSelect(value);
                }}
              >
                {formData.composition.map(item => (
                  <MenuItem key={item.material_id} value={item.material_id}>
                    {item.material_code ? `${item.material_code} — ` : ''}{item.material_name || 'Unnamed material'}
                  </MenuItem>
                ))}
              </Select>
              {formErrors.high_risk_ingredients && (
                <FormHelperText>{formErrors.high_risk_ingredients}</FormHelperText>
              )}
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Physical, Chemical and Biological Characteristics"
              value={formData.physical_chemical_biological_description}
              onChange={(e) => handleInputChange('physical_chemical_biological_description', e.target.value)}
              multiline
              rows={3}
              placeholder="Describe physical, chemical and biological characteristics"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Main Processing Steps"
              value={formData.main_processing_steps}
              onChange={(e) => handleInputChange('main_processing_steps', e.target.value)}
              multiline
              rows={3}
              placeholder="Describe the main processing steps"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Packaging Material / Container"
              value={formData.packaging_type}
              onChange={(e) => handleInputChange('packaging_type', e.target.value)}
              placeholder="e.g., Plastic bottle, Carton, Vacuum pack"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Distribution / Serving Methods"
              value={formData.distribution_serving_methods}
              onChange={(e) => handleInputChange('distribution_serving_methods', e.target.value)}
              placeholder="e.g., Refrigerated transport, Room temperature serving"
            />
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              Contact Surfaces
            </Typography>
            <Autocomplete
              multiple
              options={contactSurfaces}
              loading={contactSurfacesLoading}
              value={selectedContactSurfaces}
              onChange={(_, value) => handleContactSurfaceSelection(value)}
              getOptionLabel={(option) => option.name}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip key={option.id} label={option.name} {...getTagProps({ index })} />
                ))
              }
              renderOption={(props, option) => (
                <li {...props} key={option.id}>
                  <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                    <Typography variant="body2">{option.name}</Typography>
                    {option.point_of_contact && (
                      <Typography variant="caption" color="text.secondary">
                        {option.point_of_contact}
                      </Typography>
                    )}
                  </Box>
                </li>
              )}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Select contact surfaces"
                  placeholder="Begin typing to search"
                  helperText="Reuse existing surfaces or add a new one below."
                />
              )}
            />
            <Button
              variant="text"
              startIcon={<AddIcon />}
              sx={{ mt: 1 }}
              onClick={() => setContactSurfaceDialogOpen(true)}
            >
              Add Contact Surface
            </Button>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Consumer Groups"
              value={formData.consumer_groups}
              onChange={(e) => handleInputChange('consumer_groups', e.target.value)}
              multiline
              rows={2}
              placeholder="e.g., General population, Children, Elderly, Immunocompromised"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Storage Conditions"
              value={formData.storage_conditions}
              onChange={(e) => handleInputChange('storage_conditions', e.target.value)}
              placeholder="e.g., Refrigerated at 2-4°C, Frozen at -18°C"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Shelf Life (days)"
              type="number"
              value={formData.shelf_life_days}
              onChange={(e) => handleInputChange('shelf_life_days', e.target.value)}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Inherent Hazards"
              value={formData.inherent_hazards}
              onChange={(e) => handleInputChange('inherent_hazards', e.target.value)}
              multiline
              rows={3}
              placeholder="Describe inherent hazards associated with the product"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Food Safety Acceptance Criteria"
              value={formData.fs_acceptance_criteria}
              onChange={(e) => handleInputChange('fs_acceptance_criteria', e.target.value)}
              multiline
              rows={3}
              placeholder="Define food safety acceptance criteria"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Law / Regulation Requirement"
              value={formData.law_regulation_requirement}
              onChange={(e) => handleInputChange('law_regulation_requirement', e.target.value)}
              multiline
              rows={2}
              placeholder="Specify relevant laws and regulations"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="HACCP Plan Version"
              value={formData.haccp_plan_version}
              onChange={(e) => handleInputChange('haccp_plan_version', e.target.value)}
              placeholder="e.g., 1.0"
            />
          </Grid>
        </Grid>
      </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {product ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
      <MaterialQuickCreateDialog
        open={materialDialogOpen}
        onClose={() => setMaterialDialogOpen(false)}
        onCreated={handleMaterialCreated}
      />
      <ContactSurfaceDialog
        open={contactSurfaceDialogOpen}
        onClose={() => setContactSurfaceDialogOpen(false)}
        onCreated={handleContactSurfaceCreated}
      />
      {materialDialogOpen && (
        <GlobalStyles
          styles={(theme) => ({
            '.material-dialog-active .MuiPopover-root': {
              zIndex: theme.zIndex.modal + 40,
            },
            '.material-dialog-active .MuiAutocomplete-popper': {
              zIndex: theme.zIndex.modal + 40,
            },
            '.material-dialog-active .MuiMenu-root, .material-dialog-active .MuiMenu-paper': {
              zIndex: theme.zIndex.modal + 40,
            },
            '.material-dialog-active .MuiPickersPopper-root, .material-dialog-active .MuiPopover-paper': {
              zIndex: theme.zIndex.modal + 40,
            },
          })}
        />
      )}
    </>
  );
};

export default ProductDialog;
