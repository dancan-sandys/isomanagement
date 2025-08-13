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
}

const ProductDialog: React.FC<ProductDialogProps> = ({ open, onClose, product }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { loading, error } = useSelector((state: RootState) => state.haccp);

  const [formData, setFormData] = useState({
    product_code: '',
    name: '',
    description: '',
    category: '',
    formulation: '',
    allergens: '',
    shelf_life_days: '',
    storage_conditions: '',
    packaging_type: '',
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
        category: product.category || '',
        formulation: product.formulation || '',
        allergens: product.allergens || '',
        shelf_life_days: product.shelf_life_days?.toString() || '',
        storage_conditions: product.storage_conditions || '',
        packaging_type: product.packaging_type || '',
        haccp_plan_approved: product.haccp_plan_approved || false,
        haccp_plan_version: product.haccp_plan_version || '',
      });
    } else {
      setFormData({
        product_code: '',
        name: '',
        description: '',
        category: '',
        formulation: '',
        allergens: '',
        shelf_life_days: '',
        storage_conditions: '',
        packaging_type: '',
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
    if (!formData.category.trim()) {
      errors.category = 'Category is required';
    }

    // Validate JSON fields if they have content
    if (formData.formulation.trim()) {
      try {
        JSON.parse(formData.formulation);
      } catch (e) {
        errors.formulation = 'Formulation must be valid JSON';
      }
    }

    if (formData.allergens.trim()) {
      try {
        JSON.parse(formData.allergens);
      } catch (e) {
        errors.allergens = 'Allergens must be valid JSON';
      }
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
        formulation: formData.formulation || null,
        allergens: formData.allergens || null,
      };

      if (product) {
        await dispatch(updateProduct({ productId: product.id, productData: submitData })).unwrap();
      } else {
        await dispatch(createProduct(submitData)).unwrap();
      }
      
      onClose();
    } catch (error: any) {
      console.error('Failed to save product:', error);
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
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required error={!!formErrors.category}>
              <InputLabel>Category</InputLabel>
              <Select
                value={formData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                label="Category"
              >
                <MenuItem value="milk">Milk</MenuItem>
                <MenuItem value="yogurt">Yogurt</MenuItem>
                <MenuItem value="cheese">Cheese</MenuItem>
                <MenuItem value="butter">Butter</MenuItem>
                <MenuItem value="cream">Cream</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>
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
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Storage Conditions"
              value={formData.storage_conditions}
              onChange={(e) => handleInputChange('storage_conditions', e.target.value)}
              placeholder="e.g., Refrigerated at 2-4°C"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Packaging Type"
              value={formData.packaging_type}
              onChange={(e) => handleInputChange('packaging_type', e.target.value)}
              placeholder="e.g., Plastic bottle, Carton"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Formulation (JSON)"
              value={formData.formulation}
              onChange={(e) => handleInputChange('formulation', e.target.value)}
              placeholder='{"ingredients": ["milk"], "proportions": [100]}'
              multiline
              rows={2}
              error={!!formErrors.formulation}
              helperText={formErrors.formulation}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Allergens (JSON)"
              value={formData.allergens}
              onChange={(e) => handleInputChange('allergens', e.target.value)}
              placeholder='["milk", "lactose"]'
              multiline
              rows={2}
              error={!!formErrors.allergens}
              helperText={formErrors.allergens}
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
