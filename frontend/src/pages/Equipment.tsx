import { Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@mui/material';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Stack,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Visibility as ViewIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { equipmentAPI } from '../services/equipmentAPI';

const EquipmentPage: React.FC = () => {
  const navigate = useNavigate();
  const [equipment, setEquipment] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Equipment Dialog
  const [equipmentDialog, setEquipmentDialog] = useState(false);
  const [equipmentForm, setEquipmentForm] = useState({
    name: '',
    equipment_type: '',
    serial_number: '',
    location: '',
    notes: '',
  });

  const loadData = async () => {
    setLoading(true);
    try {
      console.log('Loading equipment data...');
      const equipmentData = await equipmentAPI.list();
      console.log('Equipment data received:', equipmentData);
      setEquipment(equipmentData || []);
    } catch (error) {
      console.error('Error loading equipment:', error);
      setEquipment([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleEquipmentSubmit = async () => {
    try {
      await equipmentAPI.create(equipmentForm);
      setEquipmentDialog(false);
      setEquipmentForm({ name: '', equipment_type: '', serial_number: '', location: '', notes: '' });
      loadData();
    } catch (error) {
      console.error('Error creating equipment:', error);
    }
  };

  const getEquipmentTypeColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'production':
        return 'primary';
      case 'safety':
        return 'error';
      case 'monitoring':
        return 'info';
      case 'testing':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Stack>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Equipment Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage and monitor all equipment in the facility
          </Typography>
        </Stack>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setEquipmentDialog(true)}
            >
              Add Equipment
            </Button>
        </Stack>

        {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Paper sx={{ width: '100%', p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Equipment List ({equipment.length} items)
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Debug: Equipment count: {equipment.length}
          </Typography>
          </Box>

            <Grid container spacing={3}>
              {equipment.map((item) => (
                <Grid item xs={12} md={6} lg={4} key={item.id}>
                  <Card>
                    <CardContent>
                      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                        <Typography variant="h6" fontWeight="bold">
                          {item.name}
                        </Typography>
                        <Chip
                          label={item.equipment_type}
                          color={getEquipmentTypeColor(item.equipment_type)}
                          size="small"
                        />
                      </Stack>
                      <Stack spacing={1}>
                        <Typography variant="body2" color="text.secondary">
                          <strong>Serial:</strong> {item.serial_number || 'N/A'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          <strong>Location:</strong> {item.location || 'N/A'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          <strong>Created:</strong> {new Date(item.created_at).toLocaleDateString()}
                        </Typography>
                        {item.notes && (
                          <Typography variant="body2" color="text.secondary">
                            <strong>Notes:</strong> {item.notes}
                          </Typography>
                        )}
                      </Stack>
                    </CardContent>
                    <CardActions>
                  <Button 
                    size="small" 
                    startIcon={<ViewIcon />} 
                    variant="outlined"
                                            onClick={() => {
                          // Navigate to equipment details page
                          navigate(`/maintenance/equipment/${item.id}`);
                        }}
                  >
                    View Details
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
      </Paper>

        {/* Equipment Dialog */}
        <Dialog open={equipmentDialog} onClose={() => setEquipmentDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add New Equipment</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                label="Equipment Name"
                value={equipmentForm.name}
                onChange={(e) => setEquipmentForm({ ...equipmentForm, name: e.target.value })}
                fullWidth
                required
              />
            <TextField
              label="Equipment Type"
                  value={equipmentForm.equipment_type}
                  onChange={(e) => setEquipmentForm({ ...equipmentForm, equipment_type: e.target.value })}
              fullWidth
            />
              <TextField
                label="Serial Number"
                value={equipmentForm.serial_number}
                onChange={(e) => setEquipmentForm({ ...equipmentForm, serial_number: e.target.value })}
                fullWidth
              />
              <TextField
                label="Location"
                value={equipmentForm.location}
                onChange={(e) => setEquipmentForm({ ...equipmentForm, location: e.target.value })}
                fullWidth
              />
              <TextField
                label="Notes"
              multiline
              rows={3}
                value={equipmentForm.notes}
                onChange={(e) => setEquipmentForm({ ...equipmentForm, notes: e.target.value })}
                fullWidth
              />
          </Stack>
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setEquipmentDialog(false)}>Cancel</Button>
            <Button onClick={handleEquipmentSubmit} variant="contained">Add Equipment</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EquipmentPage;


