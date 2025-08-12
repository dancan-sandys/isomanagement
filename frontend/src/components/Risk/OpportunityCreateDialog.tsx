import React, { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Grid, TextField, Select, MenuItem } from '@mui/material';
import riskAPI from '../../services/riskAPI';

interface Props { open: boolean; onClose: () => void; onCreated: () => void; }

const OpportunityCreateDialog: React.FC<Props> = ({ open, onClose, onCreated }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('process');
  const [classification, setClassification] = useState('business');
  const [feasibility, setFeasibility] = useState<number | ''>('');
  const [score, setScore] = useState<number | ''>('');

  const submit = async () => {
    if (!title) return;
    const payload: any = {
      item_type: 'opportunity',
      title,
      description,
      category,
      classification,
      opportunity_feasibility: typeof feasibility === 'number' ? feasibility : undefined,
      opportunity_score: typeof score === 'number' ? score : undefined,
    };
    await riskAPI.create(payload);
    onCreated();
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>New Opportunity</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 0.5 }}>
          <Grid item xs={12}>
            <TextField label="Title" fullWidth value={title} onChange={(e) => setTitle(e.target.value)} />
          </Grid>
          <Grid item xs={12}>
            <TextField label="Description" fullWidth multiline minRows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
          </Grid>
          <Grid item xs={12} md={6}>
            <Select fullWidth value={category} onChange={(e) => setCategory(e.target.value as string)}>
              <MenuItem value="process">Process</MenuItem>
              <MenuItem value="supplier">Supplier</MenuItem>
              <MenuItem value="staff">Staff</MenuItem>
              <MenuItem value="environment">Environment</MenuItem>
              <MenuItem value="customer">Customer</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </Grid>
          <Grid item xs={12} md={6}>
            <Select fullWidth value={classification} onChange={(e) => setClassification(e.target.value as string)}>
              <MenuItem value="food_safety">Food Safety</MenuItem>
              <MenuItem value="business">Business</MenuItem>
              <MenuItem value="customer">Customer</MenuItem>
            </Select>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField label="Feasibility (1-5)" type="number" fullWidth value={feasibility} onChange={(e) => setFeasibility(Number(e.target.value))} />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField label="Score" type="number" fullWidth value={score} onChange={(e) => setScore(Number(e.target.value))} />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={submit}>Create</Button>
      </DialogActions>
    </Dialog>
  );
};

export default OpportunityCreateDialog;


