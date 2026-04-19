import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  TextField,
} from '@mui/material';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store';
import { createContactSurface } from '../../store/slices/haccpSlice';
import { ContactSurface } from '../../types/haccp';

interface ContactSurfaceDialogProps {
  open: boolean;
  onClose: () => void;
  onCreated?: (surface: ContactSurface) => void;
}

const initialForm = {
  name: '',
  composition: '',
  description: '',
  source: '',
  provenance: '',
  point_of_contact: '',
  material: '',
  main_processing_steps: '',
  packaging_material: '',
  storage_conditions: '',
  shelf_life: '',
  possible_inherent_hazards: '',
  fs_acceptance_criteria: '',
};

const ContactSurfaceDialog: React.FC<ContactSurfaceDialogProps> = ({ open, onClose, onCreated }) => {
  const dispatch = useDispatch<AppDispatch>();
  const [formData, setFormData] = useState(initialForm);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) {
      setFormData(initialForm);
      setErrors({});
      setSubmitting(false);
    }
  }, [open]);

  const handleChange = (field: keyof typeof formData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const validate = () => {
    const nextErrors: Record<string, string> = {};
    if (!formData.name.trim()) {
      nextErrors.name = 'Surface name is required';
    }
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    try {
      setSubmitting(true);
      const response = await dispatch(createContactSurface(formData)).unwrap();
      const surface = response?.data as ContactSurface | undefined;
      if (surface) {
        onCreated?.(surface);
      }
      onClose();
    } catch (error: any) {
      setErrors((prev) => ({ ...prev, submit: error?.toString() || 'Failed to create contact surface' }));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Add Contact Surface</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2} sx={{ mt: 0 }}>
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              label="Contact Surface"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              error={Boolean(errors.name)}
              helperText={errors.name || 'Provide a descriptive name (e.g., Pasteurizer Holding Tube)'}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Composition"
              value={formData.composition}
              onChange={(e) => handleChange('composition', e.target.value)}
              placeholder="304 stainless steel, HDPE, etc."
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Source / Supplier"
              value={formData.source}
              onChange={(e) => handleChange('source', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Provenance / History"
              value={formData.provenance}
              onChange={(e) => handleChange('provenance', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Surface Material"
              value={formData.material}
              onChange={(e) => handleChange('material', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Point of Contact"
              value={formData.point_of_contact}
              onChange={(e) => handleChange('point_of_contact', e.target.value)}
              placeholder="e.g., Raw milk receiving, post-pasteurization"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Main Processing Steps"
              value={formData.main_processing_steps}
              onChange={(e) => handleChange('main_processing_steps', e.target.value)}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description (Physical / Chemical / Biological)"
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              multiline
              rows={3}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Packaging Material / Container"
              value={formData.packaging_material}
              onChange={(e) => handleChange('packaging_material', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Storage Conditions"
              value={formData.storage_conditions}
              onChange={(e) => handleChange('storage_conditions', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Shelf Life / Service Interval"
              value={formData.shelf_life}
              onChange={(e) => handleChange('shelf_life', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Possible Inherent Hazards"
              value={formData.possible_inherent_hazards}
              onChange={(e) => handleChange('possible_inherent_hazards', e.target.value)}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Food Safety Acceptance Criteria"
              value={formData.fs_acceptance_criteria}
              onChange={(e) => handleChange('fs_acceptance_criteria', e.target.value)}
              multiline
              rows={2}
            />
          </Grid>
          {errors.submit && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                error
                value={errors.submit}
                helperText={errors.submit}
                InputProps={{ readOnly: true }}
              />
            </Grid>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={submitting}>
          Cancel
        </Button>
        <Button variant="contained" onClick={handleSubmit} disabled={submitting}>
          Save Contact Surface
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ContactSurfaceDialog;

