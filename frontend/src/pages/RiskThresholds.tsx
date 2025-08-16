import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Alert,
  Chip
} from '@mui/material';
import { Edit, Delete, Add } from '@mui/icons-material';
import { riskThresholdAPI } from '../services/api';

interface RiskThreshold {
  id: number;
  name: string;
  description?: string;
  scope_type: 'site' | 'product' | 'category';
  scope_id?: number;
  low_threshold: number;
  medium_threshold: number;
  high_threshold: number;
  likelihood_scale: number;
  severity_scale: number;
  calculation_method: 'multiplication' | 'addition' | 'matrix';
  created_at: string;
  created_by: number;
}

const RiskThresholds: React.FC = () => {
  const [thresholds, setThresholds] = useState<RiskThreshold[]>([]);
  const [open, setOpen] = useState(false);
  const [editingThreshold, setEditingThreshold] = useState<RiskThreshold | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    scope_type: 'site' as const,
    scope_id: undefined as number | undefined,
    low_threshold: 4,
    medium_threshold: 8,
    high_threshold: 15,
    likelihood_scale: 5,
    severity_scale: 5,
    calculation_method: 'multiplication' as const
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadThresholds();
  }, []);

  const loadThresholds = async () => {
    try {
      const response = await riskThresholdAPI.getAll();
      setThresholds(response.data.data.items);
    } catch (err: any) {
      setError('Failed to load risk thresholds');
    }
  };

  const handleSubmit = async () => {
    try {
      if (editingThreshold) {
        await riskThresholdAPI.update(editingThreshold.id, formData);
        setSuccess('Risk threshold updated successfully');
      } else {
        await riskThresholdAPI.create(formData);
        setSuccess('Risk threshold created successfully');
      }
      setOpen(false);
      setEditingThreshold(null);
      resetForm();
      loadThresholds();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save risk threshold');
    }
  };

  const handleEdit = (threshold: RiskThreshold) => {
    setEditingThreshold(threshold);
    setFormData({
      name: threshold.name,
      description: threshold.description || '',
      scope_type: threshold.scope_type,
      scope_id: threshold.scope_id,
      low_threshold: threshold.low_threshold,
      medium_threshold: threshold.medium_threshold,
      high_threshold: threshold.high_threshold,
      likelihood_scale: threshold.likelihood_scale,
      severity_scale: threshold.severity_scale,
      calculation_method: threshold.calculation_method
    });
    setOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this risk threshold?')) {
      try {
        await riskThresholdAPI.delete(id);
        setSuccess('Risk threshold deleted successfully');
        loadThresholds();
      } catch (err: any) {
        setError('Failed to delete risk threshold');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      scope_type: 'site',
      scope_id: undefined,
      low_threshold: 4,
      medium_threshold: 8,
      high_threshold: 15,
      likelihood_scale: 5,
      severity_scale: 5,
      calculation_method: 'multiplication'
    });
  };

  const handleOpen = () => {
    setEditingThreshold(null);
    resetForm();
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingThreshold(null);
    resetForm();
    setError(null);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Risk Threshold Management</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpen}
        >
          Add Risk Threshold
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Scope</TableCell>
              <TableCell>Low Threshold</TableCell>
              <TableCell>Medium Threshold</TableCell>
              <TableCell>High Threshold</TableCell>
              <TableCell>Calculation Method</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {thresholds.map((threshold) => (
              <TableRow key={threshold.id}>
                <TableCell>{threshold.name}</TableCell>
                <TableCell>
                  <Chip 
                    label={`${threshold.scope_type}${threshold.scope_id ? ` (ID: ${threshold.scope_id})` : ''}`}
                    color={threshold.scope_type === 'site' ? 'primary' : 'secondary'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{threshold.low_threshold}</TableCell>
                <TableCell>{threshold.medium_threshold}</TableCell>
                <TableCell>{threshold.high_threshold}</TableCell>
                <TableCell>{threshold.calculation_method}</TableCell>
                <TableCell>
                  <IconButton onClick={() => handleEdit(threshold)}>
                    <Edit />
                  </IconButton>
                  <IconButton onClick={() => handleDelete(threshold.id)}>
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingThreshold ? 'Edit Risk Threshold' : 'Add Risk Threshold'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <TextField
              label="Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
              required
            />
            <FormControl fullWidth>
              <InputLabel>Scope Type</InputLabel>
              <Select
                value={formData.scope_type}
                onChange={(e) => setFormData({ ...formData, scope_type: e.target.value as any })}
                label="Scope Type"
              >
                <MenuItem value="site">Site-wide</MenuItem>
                <MenuItem value="product">Product-specific</MenuItem>
                <MenuItem value="category">Category-specific</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Scope ID (optional)"
              type="number"
              value={formData.scope_id || ''}
              onChange={(e) => setFormData({ ...formData, scope_id: e.target.value ? Number(e.target.value) : undefined })}
              fullWidth
              helperText="Product ID or Category ID"
            />
            <TextField
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
            <TextField
              label="Low Threshold"
              type="number"
              value={formData.low_threshold}
              onChange={(e) => setFormData({ ...formData, low_threshold: Number(e.target.value) })}
              fullWidth
              required
            />
            <TextField
              label="Medium Threshold"
              type="number"
              value={formData.medium_threshold}
              onChange={(e) => setFormData({ ...formData, medium_threshold: Number(e.target.value) })}
              fullWidth
              required
            />
            <TextField
              label="High Threshold"
              type="number"
              value={formData.high_threshold}
              onChange={(e) => setFormData({ ...formData, high_threshold: Number(e.target.value) })}
              fullWidth
              required
            />
            <FormControl fullWidth>
              <InputLabel>Calculation Method</InputLabel>
              <Select
                value={formData.calculation_method}
                onChange={(e) => setFormData({ ...formData, calculation_method: e.target.value as any })}
                label="Calculation Method"
              >
                <MenuItem value="multiplication">Multiplication (L × S)</MenuItem>
                <MenuItem value="addition">Addition (L + S)</MenuItem>
                <MenuItem value="matrix">Matrix-based</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Likelihood Scale"
              type="number"
              value={formData.likelihood_scale}
              onChange={(e) => setFormData({ ...formData, likelihood_scale: Number(e.target.value) })}
              fullWidth
              required
            />
            <TextField
              label="Severity Scale"
              type="number"
              value={formData.severity_scale}
              onChange={(e) => setFormData({ ...formData, severity_scale: Number(e.target.value) })}
              fullWidth
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingThreshold ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RiskThresholds;
