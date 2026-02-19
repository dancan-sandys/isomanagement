import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  Box,
  Typography,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Chip
} from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import { objectivesService } from '../../services/objectivesService';
import { Box as MuiBox } from '@mui/system';

interface ProgressEntryFormProps {
  open: boolean;
  objectiveId: number;
  onClose: () => void;
  onSubmit: () => void;
}

const validationSchema = yup.object({
  recorded_value: yup.number().required('Value is required').min(0, 'Value must be non-negative'),
  recorded_date: yup.date().required('Date is required').max(new Date(), 'Date cannot be in the future'),
  notes: yup.string().max(500, 'Notes must be less than 500 characters'),
});

const ProgressEntryForm: React.FC<ProgressEntryFormProps> = ({
  open,
  objectiveId,
  onClose,
  onSubmit
}) => {
  const [objective, setObjective] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evidenceFile, setEvidenceFile] = useState<File | null>(null);
  const [evidenceNotes, setEvidenceNotes] = useState<string>('');

  useEffect(() => {
    if (open) {
      loadObjective();
    }
  }, [open, objectiveId]);

  const loadObjective = async () => {
    try {
      const response = await objectivesService.getObjective(objectiveId);
      setObjective(response.data);
    } catch (err) {
      console.error('Error loading objective:', err);
    }
  };

  const formik = useFormik({
    initialValues: {
      recorded_value: '',
      recorded_date: new Date().toISOString().split('T')[0],
      notes: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        setLoading(true);
        setError(null);

        const progressData = {
          objective_id: objectiveId,
          recorded_value: parseFloat(values.recorded_value),
          recorded_date: values.recorded_date,
          notes: values.notes || null,
        };

        await objectivesService.createProgress(objectiveId, progressData);

        // If evidence selected, link it to the most recent progress entry
        if (evidenceFile) {
          try {
            const history = await objectivesService.getObjectiveProgress(objectiveId);
            const entries = history.data || [];
            const latest = entries
              .slice()
              .sort((a: any, b: any) => new Date(b.recorded_date).getTime() - new Date(a.recorded_date).getTime())[0];
            const progressId = latest?.id;
            await objectivesService.uploadEvidence(objectiveId, {
              file: evidenceFile,
              notes: evidenceNotes || undefined,
              progress_id: progressId,
            });
          } catch (e) {
            // Non-blocking: evidence upload failure should not prevent progress save
            console.error('Evidence upload failed', e);
          } finally {
            setEvidenceFile(null);
            setEvidenceNotes('');
          }
        }
        onSubmit();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to record progress');
        console.error('Error recording progress:', err);
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

  const calculateProgressPercentage = () => {
    if (!objective || !formik.values.recorded_value) return 0;
    const value = parseFloat(formik.values.recorded_value);
    return Math.min((value / objective.target_value) * 100, 100);
  };

  const getProgressStatus = () => {
    const percentage = calculateProgressPercentage();
    if (percentage >= 100) return { color: 'success', text: 'Completed' };
    if (percentage >= 75) return { color: 'success', text: 'On Track' };
    if (percentage >= 50) return { color: 'warning', text: 'In Progress' };
    return { color: 'error', text: 'Behind Schedule' };
  };

  const status = getProgressStatus();

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Record Progress Update
        {objective && (
          <Typography variant="subtitle2" color="textSecondary">
            {objective.title}
          </Typography>
        )}
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {objective && (
          <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Objective Details
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Target Value
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {objective.target_value} {objective.unit_of_measure}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Current Value
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {objective.current_value || objective.baseline_value || 0} {objective.unit_of_measure}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Start Date
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {objective.start_date ? new Date(objective.start_date).toLocaleDateString() : '—'}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Target Date
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {objective.target_date ? new Date(objective.target_date).toLocaleDateString() : '—'}
                </Typography>
              </Grid>
            </Grid>
          </Box>
        )}

        <Box component="form" onSubmit={formik.handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="recorded_value"
                label={`Recorded Value (${objective?.unit_of_measure || 'units'})`}
                type="number"
                value={formik.values.recorded_value}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.recorded_value && Boolean(formik.errors.recorded_value)}
                helperText={
                  (formik.touched.recorded_value && formik.errors.recorded_value) ||
                  (formik.values.recorded_value && `Progress: ${Math.round(calculateProgressPercentage())}%`)
                }
                required
                inputProps={{
                  step: "0.01",
                  min: 0
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                name="recorded_date"
                label="Recorded Date"
                type="date"
                value={formik.values.recorded_date}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.recorded_date && Boolean(formik.errors.recorded_date)}
                helperText={formik.touched.recorded_date && formik.errors.recorded_date}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                name="notes"
                label="Notes (Optional)"
                multiline
                rows={3}
                value={formik.values.notes}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.notes && Boolean(formik.errors.notes)}
                helperText={
                  (formik.touched.notes && formik.errors.notes) ||
                  "Add any relevant notes about this progress update"
                }
                placeholder="Describe any factors that influenced this progress, challenges encountered, or next steps..."
              />
            </Grid>

            {/* Evidence Attachment */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Evidence (optional)
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Button
                    variant="outlined"
                    component="label"
                    disabled={loading}
                  >
                    {evidenceFile ? 'Change File' : 'Attach File'}
                    <input
                      type="file"
                      hidden
                      onChange={(e) => {
                        const f = e.target.files && e.target.files[0];
                        setEvidenceFile(f || null);
                      }}
                    />
                  </Button>
                  {evidenceFile && (
                    <Typography variant="body2" sx={{ ml: 2, display: 'inline' }}>
                      {evidenceFile.name}
                    </Typography>
                  )}
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Evidence Notes (optional)"
                    value={evidenceNotes}
                    onChange={(e) => setEvidenceNotes(e.target.value)}
                  />
                </Grid>
              </Grid>
              <FormHelperText>
                If you attach a file, it will be linked to this progress entry.
              </FormHelperText>
            </Grid>

            {formik.values.recorded_value && (
              <Grid item xs={12}>
                <Box sx={{ p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Progress Preview
                  </Typography>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Typography variant="h6" color="primary">
                      {Math.round(calculateProgressPercentage())}%
                    </Typography>
                    <Chip
                      label={status.text}
                      color={status.color as any}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    This will update the objective's current progress to {formik.values.recorded_value} {objective?.unit_of_measure}
                  </Typography>
                </Box>
              </Grid>
            )}
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
          {loading ? 'Recording...' : 'Record Progress'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ProgressEntryForm;
