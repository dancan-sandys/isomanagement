import React, { useState, useEffect } from 'react';
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
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { createProduct, updateProduct } from '../../store/slices/haccpSlice';

interface ProductDialogProps {
  open: boolean;
  onClose: () => void;
  product?: any; // For editing existing product
  onSuccess?: () => void; // Callback for successful save
}

const ProductDialog: React.FC<ProductDialogProps> = ({ open, onClose, product, onSuccess }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { loading, error } = useSelector((state: RootState) => state.haccp);

  const [formData, setFormData] = useState({
    product_code: '',
    name: '',
    description: '',
    composition: '',
    high_risk_ingredients: '',
    physical_chemical_biological_description: '',
    main_processing_steps: '',
    distribution_serving_methods: '',
    product_contact_surfaces: '',
    consumer_groups: '',
    storage_conditions: '',
    shelf_life_days: '',
    packaging_type: '',
    inherent_hazards: '',
    fs_acceptance_criteria: '',
    law_regulation_requirement: '',
    haccp_plan_approved: false,
    haccp_plan_version: '',
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (product) {
      setFormData({
        product_code: product.product_code || '',
        name: product.name || '',
        description: product.description || '',
        composition: product.composition || '',
        high_risk_ingredients: product.high_risk_ingredients || '',
        physical_chemical_biological_description: product.physical_chemical_biological_description || '',
        main_processing_steps: product.main_processing_steps || '',
        distribution_serving_methods: product.distribution_serving_methods || '',
        product_contact_surfaces: product.product_contact_surfaces || '',
        consumer_groups: product.consumer_groups || '',
        storage_conditions: product.storage_conditions || '',
        shelf_life_days: product.shelf_life_days?.toString() || '',
        packaging_type: product.packaging_type || '',
        inherent_hazards: product.inherent_hazards || '',
        fs_acceptance_criteria: product.fs_acceptance_criteria || '',
        law_regulation_requirement: product.law_regulation_requirement || '',
        haccp_plan_approved: product.haccp_plan_approved || false,
        haccp_plan_version: product.haccp_plan_version || '',
      });
    } else {
      setFormData({
        product_code: '',
        name: '',
        description: '',
        composition: '',
        high_risk_ingredients: '',
        physical_chemical_biological_description: '',
        main_processing_steps: '',
        distribution_serving_methods: '',
        product_contact_surfaces: '',
        consumer_groups: '',
        storage_conditions: '',
        shelf_life_days: '',
        packaging_type: '',
        inherent_hazards: '',
        fs_acceptance_criteria: '',
        law_regulation_requirement: '',
        haccp_plan_approved: false,
        haccp_plan_version: '',
      });
    }
    setFormErrors({});
  }, [product, open]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (formErrors[field]) {
      setFormErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};

    if (!formData.product_code.trim()) {
      errors.product_code = 'Product code is required';
    }
    if (!formData.name.trim()) {
      errors.name = 'Product name is required';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      const submitData = {
        ...formData,
        shelf_life_days: formData.shelf_life_days ? parseInt(formData.shelf_life_days) : null,
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

  return (
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
            <TextField
              fullWidth
              label="Composition"
              value={formData.composition}
              onChange={(e) => handleInputChange('composition', e.target.value)}
              multiline
              rows={3}
              placeholder="Detailed composition of the product"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="High-risk Ingredients"
              value={formData.high_risk_ingredients}
              onChange={(e) => handleInputChange('high_risk_ingredients', e.target.value)}
              multiline
              rows={2}
              placeholder="List any high-risk ingredients"
            />
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
            <TextField
              fullWidth
              label="Product Contact Surfaces"
              value={formData.product_contact_surfaces}
              onChange={(e) => handleInputChange('product_contact_surfaces', e.target.value)}
              multiline
              rows={2}
              placeholder="Describe materials and surfaces that come in contact with the product"
            />
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
  );
};

export default ProductDialog;
