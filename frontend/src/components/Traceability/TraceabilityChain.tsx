import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Add as AddIcon,
  Timeline as TimelineIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon
} from '@mui/icons-material';
import { TraceabilityChain as TraceabilityChainType, TraceabilityLink, Batch } from '../../types/traceability';
import { traceabilityAPI } from '../../services/traceabilityAPI';

interface TraceabilityChainProps {
  batchId: number;
  onLinkCreate?: (link: TraceabilityLink) => void;
  onLinkDelete?: (linkId: number) => void;
}

interface ChainNode {
  batch: Batch;
  level: number;
  direction: 'incoming' | 'outgoing';
  links: TraceabilityLink[];
}

const TraceabilityChain: React.FC<TraceabilityChainProps> = ({
  batchId,
  onLinkCreate,
  onLinkDelete
}) => {
  const [chainData, setChainData] = useState<TraceabilityChainType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [linkDialogOpen, setLinkDialogOpen] = useState(false);
  const [selectedNode, setSelectedNode] = useState<ChainNode | null>(null);
  const [zoom, setZoom] = useState(1);

  // Form state for creating links
  const [linkForm, setLinkForm] = useState({
    target_batch_id: '',
    link_type: '',
    quantity_used: '',
    process_step: ''
  });

  useEffect(() => {
    if (batchId) {
      loadTraceabilityChain();
    }
  }, [batchId]);

  const loadTraceabilityChain = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await traceabilityAPI.getTraceabilityChain(batchId);
      setChainData(data);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load traceability chain');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLink = async () => {
    try {
      setLoading(true);
      const linkData = {
        source_batch_id: batchId,
        target_batch_id: parseInt(linkForm.target_batch_id),
        link_type: linkForm.link_type,
        quantity_used: parseFloat(linkForm.quantity_used),
        process_step: linkForm.process_step
      };

      const newLink = await traceabilityAPI.createTraceabilityLink(linkData);
      onLinkCreate?.(newLink);
      setLinkDialogOpen(false);
      setLinkForm({
        target_batch_id: '',
        link_type: '',
        quantity_used: '',
        process_step: ''
      });
      loadTraceabilityChain();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create link');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteLink = async (linkId: number) => {
    if (!window.confirm('Are you sure you want to delete this link?')) {
      return;
    }

    try {
      await traceabilityAPI.deleteTraceabilityLink(linkId);
      onLinkDelete?.(linkId);
      loadTraceabilityChain();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to delete link');
    }
  };

  const getBatchTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'raw_milk': return 'primary';
      case 'additive': return 'secondary';
      case 'culture': return 'success';
      case 'packaging': return 'warning';
      case 'final_product': return 'info';
      case 'intermediate': return 'default';
      default: return 'default';
    }
  };

  const getLinkTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'ingredient': return 'primary';
      case 'product': return 'success';
      case 'process': return 'warning';
      default: return 'default';
    }
  };

  const renderChainNode = (node: ChainNode) => (
    <Card 
      key={node.batch.id} 
      variant="outlined" 
      sx={{ 
        mb: 2,
        border: node.direction === 'incoming' ? '2px solid #1976d2' : '2px solid #2e7d32',
        transform: `scale(${zoom})`,
        transition: 'transform 0.2s'
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="h6" sx={{ fontFamily: 'monospace' }}>
            {node.batch.batch_number}
          </Typography>
          <Box display="flex" gap={1}>
            <Chip 
              label={node.batch.batch_type.replace('_', ' ').toUpperCase()} 
              color={getBatchTypeColor(node.batch.batch_type)}
              size="small"
            />
            <Chip 
              label={node.direction.toUpperCase()} 
              color={node.direction === 'incoming' ? 'primary' : 'success'}
              size="small"
            />
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          {node.batch.product_name}
        </Typography>

        <Typography variant="body2">
          {node.batch.quantity} {node.batch.unit}
        </Typography>

        {node.links.length > 0 && (
          <Box mt={2}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Links:
            </Typography>
            {node.links.map((link) => (
              <Box key={link.id} display="flex" alignItems="center" gap={1} mb={1}>
                <Chip 
                  label={link.link_type.replace('_', ' ').toUpperCase()} 
                  color={getLinkTypeColor(link.link_type)}
                  size="small"
                />
                <Typography variant="body2">
                  {link.quantity_used} used in {link.process_step}
                </Typography>
                <IconButton 
                  size="small" 
                  color="error"
                  onClick={() => handleDeleteLink(link.id)}
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!chainData) {
    return (
      <Typography color="text.secondary" align="center">
        No traceability chain data available
      </Typography>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          Traceability Chain
        </Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Zoom In">
            <IconButton onClick={() => setZoom(Math.min(zoom + 0.1, 2))}>
              <ZoomInIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Zoom Out">
            <IconButton onClick={() => setZoom(Math.max(zoom - 0.1, 0.5))}>
              <ZoomOutIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setLinkDialogOpen(true)}
          >
            Add Link
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadTraceabilityChain}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Chain Visualization */}
      <Grid container spacing={3}>
        {/* Incoming Links */}
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom color="primary">
            Incoming (Ingredients)
          </Typography>
          {chainData.incoming_links.length === 0 ? (
            <Typography color="text.secondary" align="center">
              No incoming links
            </Typography>
          ) : (
            chainData.incoming_links.map((link) => (
              <Card key={link.id} variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    From Batch #{link.source_batch_id}
                  </Typography>
                  <Chip 
                    label={link.link_type.replace('_', ' ').toUpperCase()} 
                    color={getLinkTypeColor(link.link_type)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {link.quantity_used} used in {link.process_step}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(link.process_date).toLocaleDateString()}
                  </Typography>
                </CardContent>
              </Card>
            ))
          )}
        </Grid>

        {/* Outgoing Links */}
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom color="success.main">
            Outgoing (Products)
          </Typography>
          {chainData.outgoing_links.length === 0 ? (
            <Typography color="text.secondary" align="center">
              No outgoing links
            </Typography>
          ) : (
            chainData.outgoing_links.map((link) => (
              <Card key={link.id} variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    To Batch #{link.target_batch_id}
                  </Typography>
                  <Chip 
                    label={link.link_type.replace('_', ' ').toUpperCase()} 
                    color={getLinkTypeColor(link.link_type)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {link.quantity_used} used in {link.process_step}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(link.process_date).toLocaleDateString()}
                  </Typography>
                </CardContent>
              </Card>
            ))
          )}
        </Grid>
      </Grid>

      {/* Process Steps */}
      {chainData.process_steps.length > 0 && (
        <Box mt={4}>
          <Typography variant="h6" gutterBottom>
            Process Steps
          </Typography>
          <Grid container spacing={2}>
            {chainData.process_steps.map((step) => (
              <Grid item xs={12} md={6} key={step.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1">
                      {step.step_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {step.step_type}
                    </Typography>
                    <Typography variant="body2">
                      Quantity used: {step.quantity_used}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(step.step_date).toLocaleDateString()}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Create Link Dialog */}
      <Dialog open={linkDialogOpen} onClose={() => setLinkDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Traceability Link</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target Batch ID"
                type="number"
                value={linkForm.target_batch_id}
                onChange={(e) => setLinkForm({ ...linkForm, target_batch_id: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Link Type</InputLabel>
                <Select
                  value={linkForm.link_type}
                  onChange={(e) => setLinkForm({ ...linkForm, link_type: e.target.value })}
                  label="Link Type"
                >
                  <MenuItem value="ingredient">Ingredient</MenuItem>
                  <MenuItem value="product">Product</MenuItem>
                  <MenuItem value="process">Process</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Quantity Used"
                type="number"
                value={linkForm.quantity_used}
                onChange={(e) => setLinkForm({ ...linkForm, quantity_used: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Process Step"
                value={linkForm.process_step}
                onChange={(e) => setLinkForm({ ...linkForm, process_step: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLinkDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreateLink} variant="contained" disabled={loading}>
            Create Link
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TraceabilityChain; 