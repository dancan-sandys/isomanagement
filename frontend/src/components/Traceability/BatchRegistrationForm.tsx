import React, { useEffect, useMemo, useState } from 'react';
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
  Typography,
  Alert,
  CircularProgress,
  Chip,
  Box,
  FormHelperText,
  Autocomplete
} from '@mui/material';
import {
  Add as AddIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Inventory as InventoryIcon
} from '@mui/icons-material';
import { BatchFormData } from '../../types/traceability';
import { traceabilityAPI } from '../../services/traceabilityAPI';
import { haccpAPI } from '../../services/haccpAPI';
import { supplierAPI } from '../../services/supplierAPI';

interface BatchRegistrationFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  initialData?: Partial<BatchFormData>;
  isEdit?: boolean;
}

const BATCH_TYPES = [
  { value: 'raw_milk', label: 'Raw Milk', color: 'primary' },
  { value: 'additive', label: 'Additive', color: 'secondary' },
  { value: 'culture', label: 'Culture', color: 'success' },
  { value: 'packaging', label: 'Packaging', color: 'warning' },
  { value: 'final_product', label: 'Final Product', color: 'info' },
  { value: 'intermediate', label: 'Intermediate', color: 'default' }
];

const UNITS = [
  'kg', 'liters', 'pieces', 'boxes', 'pallets', 'tons', 'grams', 'milliliters'
];

const STORAGE_CONDITIONS = [
  'refrigerated', 'frozen', 'ambient', 'controlled_atmosphere', 'vacuum_packed'
];

const BatchRegistrationForm: React.FC<BatchRegistrationFormProps> = ({
  open,
  onClose,
  onSuccess,
  initialData,
  isEdit = false
}) => {
  const [formData, setFormData] = useState<BatchFormData>({
    batch_type: '',
    product_name: '',
    quantity: '',
    unit: '',
    production_date: '',
    expiry_date: '',
    lot_number: '',
    storage_location: '',
    storage_conditions: '',
    supplier_id: undefined,
    ...initialData
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Searchable options
  const [productOptions, setProductOptions] = useState<Array<{ id: number; name: string }>>([]);
  const [productInput, setProductInput] = useState('');
  const filteredProductOptions = useMemo(() => {
    if (!productInput) return productOptions;
    const q = productInput.toLowerCase();
    return productOptions.filter(p => p.name.toLowerCase().includes(q));
  }, [productInput, productOptions]);

  const [supplierOptions, setSupplierOptions] = useState<Array<{ id: number; name: string; supplier_code?: string }>>([]);
  const [supplierLoading, setSupplierLoading] = useState(false);
  const [supplierSearch, setSupplierSearch] = useState('');
  const [selectedSupplier, setSelectedSupplier] = useState<{ id: number; name: string; supplier_code?: string } | null>(null);

  // Load products once when dialog opens
  useEffect(() => {
    if (!open) return;
    (async () => {
      try {
        const res: any = await haccpAPI.getProducts();
        const products = (res?.data?.products || res?.products || res || []).map((p: any) => ({ id: p.id, name: p.name || p.product_name || p.title || '' }));
        setProductOptions(products.filter((p: any) => p.name));
      } catch (e) {
        // Silent: fallback is free text if products fail
      }
    })();
  }, [open]);

  // Debounced supplier search
  useEffect(() => {
    let active = true;
    if (!open) return;
    setSupplierLoading(true);
    const handle = setTimeout(async () => {
      try {
        let suppliers: any[] = [];
        if (supplierSearch && supplierSearch.trim().length > 0) {
          const res: any = await supplierAPI.searchSuppliers(supplierSearch, { limit: 10 });
          suppliers = res?.data || res?.suppliers || res || [];
        } else {
          const res: any = await supplierAPI.getSuppliers({ size: 10 });
          suppliers = res?.data?.items || res?.data?.suppliers || res?.items || res?.suppliers || [];
        }
        if (active) {
          const options = suppliers.map((s: any) => ({ id: s.id, name: s.name, supplier_code: s.supplier_code || '' }));
          // Ensure currently selected supplier stays in options to prevent flicker
          if (selectedSupplier && !options.find(o => o.id === selectedSupplier.id)) {
            options.unshift(selectedSupplier);
          }
          setSupplierOptions(options);
        }
      } catch (e) {
        if (active) setSupplierOptions([]);
      } finally {
        if (active) setSupplierLoading(false);
      }
    }, 300);
    return () => {
      active = false;
      clearTimeout(handle);
    };
  }, [supplierSearch, open]);

  // Load selected supplier details for edit state
  useEffect(() => {
    (async () => {
      if (!open) return;
      if (initialData?.supplier_id) {
        try {
          const res: any = await supplierAPI.getSupplier(initialData.supplier_id as number);
          const s = res?.data || res;
          const opt = s ? { id: s.id, name: s.name, supplier_code: s.supplier_code || '' } : null;
          setSelectedSupplier(opt);
        } catch (e) {
          // ignore
        }
      } else {
        setSelectedSupplier(null);
      }
    })();
  }, [open, initialData?.supplier_id]);

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.batch_type) {
      errors.batch_type = 'Batch type is required';
    }

    if (!formData.product_name.trim()) {
      errors.product_name = 'Product name is required';
    }

    if (!formData.quantity || parseFloat(formData.quantity) <= 0) {
      errors.quantity = 'Valid quantity is required';
    }

    if (!formData.unit) {
      errors.unit = 'Unit is required';
    }

    if (!formData.production_date) {
      errors.production_date = 'Production date is required';
    }

    if (formData.expiry_date && new Date(formData.expiry_date) <= new Date(formData.production_date)) {
      errors.expiry_date = 'Expiry date must be after production date';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const submitData = {
        ...formData,
        quantity: parseFloat(formData.quantity),
        supplier_id: formData.supplier_id || null
      };

      if (isEdit && initialData) {
        // Handle edit case; require an id in initialData
        const id = (initialData as any).id;
        if (!id) {
          throw new Error('Missing batch id for update');
        }
        await traceabilityAPI.updateBatch(id as number, submitData);
      } else {
        await traceabilityAPI.createBatch(submitData);
      }

      onSuccess();
      handleClose();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to save batch');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      batch_type: '',
      product_name: '',
      quantity: '',
      unit: '',
      production_date: '',
      expiry_date: '',
      lot_number: '',
      storage_location: '',
      storage_conditions: '',
      supplier_id: undefined
    });
    setError(null);
    setValidationErrors({});
    onClose();
  };

  const handleInputChange = (field: keyof BatchFormData, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear validation error when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const getBatchTypeColor = (type: string) => {
    const batchType = BATCH_TYPES.find(bt => bt.value === type);
    return batchType?.color || 'default';
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <InventoryIcon />
          <Typography variant="h6">
            {isEdit ? 'Edit Batch' : 'Register New Batch'}
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3} sx={{ mt: 1 }}>
          {/* Batch Type */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth error={!!validationErrors.batch_type}>
              <InputLabel>Batch Type *</InputLabel>
              <Select
                value={formData.batch_type}
                onChange={(e) => handleInputChange('batch_type', e.target.value)}
                label="Batch Type *"
              >
                {BATCH_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Chip 
                        label={type.label} 
                        color={type.color as any} 
                        size="small" 
                      />
                    </Box>
                  </MenuItem>
                ))}
              </Select>
              {validationErrors.batch_type && (
                <FormHelperText>{validationErrors.batch_type}</FormHelperText>
              )}
            </FormControl>
          </Grid>

          {/* Product Name (searchable) */}
          <Grid item xs={12} md={6}>
            <Autocomplete
              freeSolo
              options={filteredProductOptions.map(p => p.name)}
              value={formData.product_name}
              onChange={(_, val) => handleInputChange('product_name', (val as string) || '')}
              inputValue={formData.product_name}
              onInputChange={(_, val, reason) => {
                if (reason === 'input') {
                  setProductInput(val);
                  handleInputChange('product_name', val);
                }
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Product Name *"
                  error={!!validationErrors.product_name}
                  helperText={validationErrors.product_name}
                />
              )}
            />
          </Grid>

          {/* Quantity */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Quantity *"
              type="number"
              value={formData.quantity}
              onChange={(e) => handleInputChange('quantity', e.target.value)}
              error={!!validationErrors.quantity}
              helperText={validationErrors.quantity}
              inputProps={{ min: 0, step: 0.01 }}
            />
          </Grid>

          {/* Unit */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth error={!!validationErrors.unit}>
              <InputLabel>Unit *</InputLabel>
              <Select
                value={formData.unit}
                onChange={(e) => handleInputChange('unit', e.target.value)}
                label="Unit *"
              >
                {UNITS.map((unit) => (
                  <MenuItem key={unit} value={unit}>
                    {unit}
                  </MenuItem>
                ))}
              </Select>
              {validationErrors.unit && (
                <FormHelperText>{validationErrors.unit}</FormHelperText>
              )}
            </FormControl>
          </Grid>

          {/* Production Date */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Production Date *"
              type="date"
              value={formData.production_date}
              onChange={(e) => handleInputChange('production_date', e.target.value)}
              error={!!validationErrors.production_date}
              helperText={validationErrors.production_date}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          {/* Expiry Date */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Expiry Date"
              type="date"
              value={formData.expiry_date}
              onChange={(e) => handleInputChange('expiry_date', e.target.value)}
              error={!!validationErrors.expiry_date}
              helperText={validationErrors.expiry_date || 'Optional'}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          {/* Lot Number */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Lot Number"
              value={formData.lot_number}
              onChange={(e) => handleInputChange('lot_number', e.target.value)}
              helperText="Optional"
            />
          </Grid>

          {/* Storage Location */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Storage Location"
              value={formData.storage_location}
              onChange={(e) => handleInputChange('storage_location', e.target.value)}
              helperText="Optional"
            />
          </Grid>

          {/* Storage Conditions */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Storage Conditions</InputLabel>
              <Select
                value={formData.storage_conditions}
                onChange={(e) => handleInputChange('storage_conditions', e.target.value)}
                label="Storage Conditions"
              >
                <MenuItem value="">
                  <em>Select storage conditions</em>
                </MenuItem>
                {STORAGE_CONDITIONS.map((condition) => (
                  <MenuItem key={condition} value={condition}>
                    {condition.replace('_', ' ').toUpperCase()}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Supplier (searchable) */}
          <Grid item xs={12} md={6}>
            <Autocomplete
              options={supplierOptions}
              loading={supplierLoading}
              getOptionLabel={(opt) => (opt.name ? `${opt.name}${opt.supplier_code ? ` (${opt.supplier_code})` : ''}` : '')}
              value={selectedSupplier}
              onChange={(_, val) => {
                setSelectedSupplier(val);
                handleInputChange('supplier_id', val ? (val.id as number) : (undefined as any));
              }}
              onInputChange={(_, val, reason) => {
                if (reason === 'input') setSupplierSearch(val);
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Supplier (optional)"
                  placeholder="Search supplier by name/code"
                  helperText="Type to search suppliers"
                />
              )}
              isOptionEqualToValue={(opt, val) => opt.id === val.id}
            />
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button 
          onClick={handleClose} 
          startIcon={<CancelIcon />}
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
          disabled={loading}
        >
          {loading ? 'Saving...' : (isEdit ? 'Update Batch' : 'Register Batch')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BatchRegistrationForm; 