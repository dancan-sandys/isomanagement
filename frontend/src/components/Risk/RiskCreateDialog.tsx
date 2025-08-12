import React, { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Grid, TextField, Select, MenuItem, Stack } from '@mui/material';
import riskAPI from '../../services/riskAPI';

interface Props {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}

const RiskCreateDialog: React.FC<Props> = ({ open, onClose, onCreated }) => {
  const [itemType, setItemType] = useState<'risk'|'opportunity'>('risk');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('process');
  const [classification, setClassification] = useState<'food_safety'|'business'|'customer'|' '>('food_safety');
  const [severity, setSeverity] = useState('low');
  const [likelihood, setLikelihood] = useState('unlikely');
  const [detectability, setDetectability] = useState('easily_detectable');

  const onSubmit = async () => {
    await riskAPI.create({
      item_type: itemType,
      title,
      description: description || undefined,
      category,
      classification: classification || undefined,
      severity,
      likelihood,
      detectability,
    });
    onCreated();
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>New Risk/Opportunity</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2} sx={{ mt: 0 }}>
          <Grid item xs={12} md={4}>
            <Select fullWidth size="small" value={itemType} onChange={(e) => setItemType(e.target.value as any)}>
              <MenuItem value="risk">Risk</MenuItem>
              <MenuItem value="opportunity">Opportunity</MenuItem>
            </Select>
          </Grid>
          <Grid item xs={12} md={8}>
            <TextField fullWidth label="Title" value={title} onChange={(e) => setTitle(e.target.value)} size="small" />
          </Grid>
          <Grid item xs={12}>
            <TextField fullWidth multiline minRows={3} label="Description" value={description} onChange={(e) => setDescription(e.target.value)} size="small" />
          </Grid>
          <Grid item xs={12} md={6}>
            <Select fullWidth size="small" value={category} onChange={(e) => setCategory(e.target.value as string)}>
              <MenuItem value="process">Process</MenuItem>
              <MenuItem value="supplier">Supplier</MenuItem>
              <MenuItem value="staff">Staff</MenuItem>
              <MenuItem value="environment">Environment</MenuItem>
              <MenuItem value="haccp">HACCP</MenuItem>
              <MenuItem value="prp">PRP</MenuItem>
              <MenuItem value="document">Document</MenuItem>
              <MenuItem value="training">Training</MenuItem>
              <MenuItem value="equipment">Equipment</MenuItem>
              <MenuItem value="compliance">Compliance</MenuItem>
              <MenuItem value="customer">Customer</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </Grid>
          <Grid item xs={12} md={6}>
            <Select fullWidth size="small" displayEmpty value={classification} onChange={(e) => setClassification(e.target.value as any)}>
              <MenuItem value="food_safety">Food Safety</MenuItem>
              <MenuItem value="business">Business</MenuItem>
              <MenuItem value="customer">Customer</MenuItem>
            </Select>
          </Grid>
          <Grid item xs={12} md={4}>
            <Select fullWidth size="small" value={severity} onChange={(e) => setSeverity(e.target.value as string)}>
              <MenuItem value="low">Severity: Low</MenuItem>
              <MenuItem value="medium">Severity: Medium</MenuItem>
              <MenuItem value="high">Severity: High</MenuItem>
              <MenuItem value="critical">Severity: Critical</MenuItem>
            </Select>
          </Grid>
          <Grid item xs={12} md={4}>
            <Select fullWidth size="small" value={likelihood} onChange={(e) => setLikelihood(e.target.value as string)}>
              <MenuItem value="rare">Likelihood: Rare</MenuItem>
              <MenuItem value="unlikely">Likelihood: Unlikely</MenuItem>
              <MenuItem value="possible">Likelihood: Possible</MenuItem>
              <MenuItem value="likely">Likelihood: Likely</MenuItem>
              <MenuItem value="almost_certain">Likelihood: Almost Certain</MenuItem>
            </Select>
          </Grid>
          <Grid item xs={12} md={4}>
            <Select fullWidth size="small" value={detectability} onChange={(e) => setDetectability(e.target.value as string)}>
              <MenuItem value="easily_detectable">Detectability: Easily detectable</MenuItem>
              <MenuItem value="moderately_detectable">Detectability: Moderately detectable</MenuItem>
              <MenuItem value="difficult">Detectability: Difficult</MenuItem>
              <MenuItem value="very_difficult">Detectability: Very difficult</MenuItem>
              <MenuItem value="almost_undetectable">Detectability: Almost undetectable</MenuItem>
            </Select>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={onSubmit} disabled={!title}>Create</Button>
      </DialogActions>
    </Dialog>
  );
};

export default RiskCreateDialog;


