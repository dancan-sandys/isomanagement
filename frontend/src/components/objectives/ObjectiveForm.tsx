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
  Box,
  Typography,
  Alert,
  Chip,
  FormHelperText,
  Autocomplete
} from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import { objectivesService } from '../../services/objectivesService';
import { Objective, ObjectiveType, HierarchyLevel, MeasurementFrequency } from '../../types/objectives';

interface ObjectiveFormProps {
  open: boolean;
  objective?: Objective | null;
  onClose: () => void;
  onSubmit: () => void;
}

const validationSchema = yup.object({
  title: yup.string().required('Title is required').max(200, 'Title must be less than 200 characters'),
  description: yup.string().required('Description is required').max(1000, 'Description must be less than 1000 characters'),
  objective_type: yup.string().required('Objective type is required'),
  hierarchy_level: yup.string().required('Hierarchy level is required'),
  department_id: yup.number().nullable(),
  parent_objective_id: yup.number().nullable(),
  baseline_value: yup.number().min(0, 'Baseline value must be non-negative'),
  target_value: yup.number().required('Target value is required').min(0, 'Target value must be non-negative'),
  weight: yup.number().min(0, 'Weight must be non-negative').max(100, 'Weight must be between 0 and 100'),
  measurement_frequency: yup.string().required('Measurement frequency is required'),
  unit_of_measure: yup.string().required('Unit of measure is required'),
  start_date: yup.date().required('Start date is required'),
  target_date: yup.date().required('Target date is required').min(
    yup.ref('start_date'),
    'Target date must be after start date'
  ),
});

const ObjectiveForm: React.FC<ObjectiveFormProps> = ({
  open,
  objective,
  onClose,
  onSubmit
}) => {
  const [departments, setDepartments] = useState<any[]>([]);
  const [parentObjectives, setParentObjectives] = useState<Objective[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditing = !!objective;

  useEffect(() => {
    if (open) {
      loadFormData();
    }
  }, [open]);

  const loadFormData = async () => {
    try {
      // Load departments
      const deptResponse = await objectivesService.getDepartments();
      setDepartments(deptResponse.data || []);

      // Load parent objectives (for hierarchical relationships)
      const parentResponse = await objectivesService.getObjectives();
      setParentObjectives(parentResponse.data || []);
    } catch (err) {
      console.error('Error loading form data:', err);
    }
  };

  const formik = useFormik({
    initialValues: {
      title: objective?.title || '',
      description: objective?.description || '',
      objective_type: objective?.objective_type || 'operational',
      hierarchy_level: objective?.hierarchy_level || 'operational',
      department_id: objective?.department_id || null,
      parent_objective_id: objective?.parent_objective_id || null,
      baseline_value: objective?.baseline_value || 0,
      target_value: objective?.target_value || 0,
      weight: objective?.weight || 1,
      measurement_frequency: objective?.measurement_frequency || 'monthly',
      unit_of_measure: objective?.unit_of_measure || '',
      start_date: objective?.start_date ? new Date(objective.start_date).toISOString().split('T')[0] : '',
      target_date: objective?.target_date ? new Date(objective.target_date).toISOString().split('T')[0] : '',
      automated_calculation: objective?.automated_calculation || false,
      data_source: objective?.data_source || 'manual',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        setLoading(true);
        setError(null);

        const objectiveData = {
          ...values,
          department_id: values.department_id || null,
          parent_objective_id: values.parent_objective_id || null,
        };

        if (isEditing && objective) {
          await objectivesService.updateObjective(objective.id, { ...objectiveData, id: objective.id });
        } else {
          await objectivesService.createObjective(objectiveData);
        }

        onSubmit();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to save objective');
        console.error('Error saving objective:', err);
      } finally {
        setLoading(false);
      }
    },
  });

  const handleClose = () => {
    formik.resetForm();
    setError(null);
    onClose();
  };

  const getObjectiveTypeColor = (type: ObjectiveType) => {
    switch (type) {
      case 'corporate': return 'primary';
      case 'departmental': return 'secondary';
      case 'operational': return 'default';
      default: return 'default';
    }
  };

  const getHierarchyLevelColor = (level: HierarchyLevel) => {
    switch (level) {
      case 'strategic': return 'error';
      case 'tactical': return 'warning';
      case 'operational': return 'info';
      default: return 'default';
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {isEditing ? 'Edit Objective' : 'Create New Objective'}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={formik.handleSubmit} sx={{ mt: 1 }}>
          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                name="title"
                label="Objective Title"
                value={formik.values.title}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.title && Boolean(formik.errors.title)}
                helperText={formik.touched.title && formik.errors.title}
                required
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                name="description"
                label="Description"
                multiline
                rows={3}
                value={formik.values.description}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.description && Boolean(formik.errors.description)}
                helperText={formik.touched.description && formik.errors.description}
                required
              />
            </Grid>

            {/* Classification */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Classification
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={formik.touched.objective_type && Boolean(formik.errors.objective_type)}>
                <InputLabel>Objective Type</InputLabel>
                <Select
                  name="objective_type"
                  value={formik.values.objective_type}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  label="Objective Type"
                >
                  <MenuItem value="corporate">
                    <Chip label="Corporate" color="primary" size="small" />
                  </MenuItem>
                  <MenuItem value="departmental">
                    <Chip label="Departmental" color="secondary" size="small" />
                  </MenuItem>
                  <MenuItem value="operational">
                    <Chip label="Operational" color="default" size="small" />
                  </MenuItem>
                </Select>
                {formik.touched.objective_type && formik.errors.objective_type && (
                  <FormHelperText>{formik.errors.objective_type}</FormHelperText>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={formik.touched.hierarchy_level && Boolean(formik.errors.hierarchy_level)}>
                <InputLabel>Hierarchy Level</InputLabel>
                <Select
                  name="hierarchy_level"
                  value={formik.values.hierarchy_level}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  label="Hierarchy Level"
                >
                  <MenuItem value="strategic">
                    <Chip label="Strategic" color="error" size="small" />
                  </MenuItem>
                  <MenuItem value="tactical">
                    <Chip label="Tactical" color="warning" size="small" />
                  </MenuItem>
                  <MenuItem value="operational">
                    <Chip label="Operational" color="info" size="small" />
                  </MenuItem>
                </Select>
                {formik.touched.hierarchy_level && formik.errors.hierarchy_level && (
                  <FormHelperText>{formik.errors.hierarchy_level}</FormHelperText>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Department</InputLabel>
                <Select
                  name="department_id"
                  value={formik.values.department_id || ''}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  label="Department"
                >
                  <MenuItem value="">
                    <em>No Department</em>
                  </MenuItem>
                  {departments.map((dept) => (
                    <MenuItem key={dept.id} value={dept.id}>
                      {dept.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Parent Objective</InputLabel>
                <Select
                  name="parent_objective_id"
                  value={formik.values.parent_objective_id || ''}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  label="Parent Objective"
                >
                  <MenuItem value="">
                    <em>No Parent</em>
                  </MenuItem>
                  {parentObjectives
                    .filter(obj => obj.id !== objective?.id) // Exclude current objective when editing
                    .map((obj) => (
                      <MenuItem key={obj.id} value={obj.id}>
                        {obj.title}
                      </MenuItem>
                    ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Targets and Measurements */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Targets and Measurements
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="baseline_value"
                label="Baseline Value"
                type="number"
                value={formik.values.baseline_value}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.baseline_value && Boolean(formik.errors.baseline_value)}
                helperText={formik.touched.baseline_value && formik.errors.baseline_value}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="target_value"
                label="Target Value"
                type="number"
                value={formik.values.target_value}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.target_value && Boolean(formik.errors.target_value)}
                helperText={formik.touched.target_value && formik.errors.target_value}
                required
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="weight"
                label="Weight (%)"
                type="number"
                value={formik.values.weight}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.weight && Boolean(formik.errors.weight)}
                helperText={formik.touched.weight && formik.errors.weight}
                inputProps={{ min: 0, max: 100 }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="unit_of_measure"
                label="Unit of Measure"
                value={formik.values.unit_of_measure}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.unit_of_measure && Boolean(formik.errors.unit_of_measure)}
                helperText={formik.touched.unit_of_measure && formik.errors.unit_of_measure}
                placeholder="e.g., %, kg, liters, count"
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={formik.touched.measurement_frequency && Boolean(formik.errors.measurement_frequency)}>
                <InputLabel>Measurement Frequency</InputLabel>
                <Select
                  name="measurement_frequency"
                  value={formik.values.measurement_frequency}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  label="Measurement Frequency"
                >
                  <MenuItem value="daily">Daily</MenuItem>
                  <MenuItem value="weekly">Weekly</MenuItem>
                  <MenuItem value="monthly">Monthly</MenuItem>
                  <MenuItem value="quarterly">Quarterly</MenuItem>
                  <MenuItem value="annually">Annually</MenuItem>
                </Select>
                {formik.touched.measurement_frequency && formik.errors.measurement_frequency && (
                  <FormHelperText>{formik.errors.measurement_frequency}</FormHelperText>
                )}
              </FormControl>
            </Grid>

            {/* Timeline */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Timeline
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="start_date"
                label="Start Date"
                type="date"
                value={formik.values.start_date}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.start_date && Boolean(formik.errors.start_date)}
                helperText={formik.touched.start_date && formik.errors.start_date}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="target_date"
                label="Target Date"
                type="date"
                value={formik.values.target_date}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.target_date && Boolean(formik.errors.target_date)}
                helperText={formik.touched.target_date && formik.errors.target_date}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={() => formik.handleSubmit()}
          variant="contained"
          disabled={loading || !formik.isValid}
        >
          {loading ? 'Saving...' : (isEditing ? 'Update' : 'Create')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ObjectiveForm;
