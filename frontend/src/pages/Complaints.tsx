import React, { useEffect, useState } from 'react';
import { Box, Stack, Typography, Button, Paper, Table, TableHead, TableRow, TableCell, TableBody, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Select, Autocomplete } from '@mui/material';
import { complaintsAPI } from '../services/api';
import { traceabilityAPI } from '../services/api';

const ComplaintsPage: React.FC = () => {
  const [list, setList] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    customer_name: '',
    customer_contact: '',
    description: '',
    classification: 'other',
    severity: 'medium',
    batch_id: '',
    product_id: '',
    received_via: '',
    complaint_date: '',
  });
  const [batchOptions, setBatchOptions] = useState<any[]>([]);
  const [batchSearch, setBatchSearch] = useState<string>('');

  const load = async () => {
    const res = await complaintsAPI.list({ page: 1, size: 50 });
    setList(res?.data?.items || res?.items || []);
  };

  useEffect(() => { load(); }, []);

  return (
    <Box p={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h5" fontWeight="bold">Customer Complaints</Typography>
        <Button variant="contained" onClick={() => setOpen(true)}>Log Complaint</Button>
      </Stack>

      <Paper>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>No.</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Classification</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {list.map((c: any) => (
              <TableRow key={c.id} hover onClick={() => { window.location.href = `/complaints/${c.id}`; }}>
                <TableCell>{c.complaint_number}</TableCell>
                <TableCell>{c.complaint_date}</TableCell>
                <TableCell>{c.customer_name}</TableCell>
                <TableCell>{c.classification}</TableCell>
                <TableCell>{c.severity}</TableCell>
                <TableCell>{c.status}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Log Complaint</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Customer Name" value={form.customer_name} onChange={e => setForm({ ...form, customer_name: e.target.value })} />
            <TextField label="Customer Contact" value={form.customer_contact} onChange={e => setForm({ ...form, customer_contact: e.target.value })} />
            <TextField label="Description" multiline rows={4} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
            <Select value={form.classification} onChange={e => setForm({ ...form, classification: e.target.value as string })}>
              <MenuItem value="foreign_object">Foreign object</MenuItem>
              <MenuItem value="off_flavor">Off-flavor</MenuItem>
              <MenuItem value="packaging">Packaging</MenuItem>
              <MenuItem value="microbiology">Microbiology</MenuItem>
              <MenuItem value="allergen">Allergen</MenuItem>
              <MenuItem value="labelling">Labelling</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
            <Select value={form.severity} onChange={e => setForm({ ...form, severity: e.target.value as string })}>
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
            </Select>
            <Autocomplete
              options={batchOptions}
              getOptionLabel={(o: any) => (o?.batch_number ? `${o.batch_number} — ${o.product_name || ''}` : String(o))}
              onOpen={async () => {
                const res = await traceabilityAPI.getBatches({ page: 1, size: 20, search: batchSearch || undefined });
                const items = res?.data?.items || res?.items || [];
                setBatchOptions(items);
              }}
              onInputChange={async (_, value) => {
                setBatchSearch(value);
                const res = await traceabilityAPI.getBatches({ page: 1, size: 20, search: value || undefined });
                const items = res?.data?.items || res?.items || [];
                setBatchOptions(items);
              }}
              onChange={(_, value: any) => setForm({ ...form, batch_id: value?.id ? String(value.id) : '' })}
              renderInput={(params) => (
                <TextField {...params} label="Batch (searchable)" placeholder="Type to search batch number" />
              )}
            />
            <TextField type="number" label="Product ID (optional)" value={form.product_id} onChange={e => setForm({ ...form, product_id: e.target.value })} />
            <TextField label="Received Via" value={form.received_via} onChange={e => setForm({ ...form, received_via: e.target.value })} />
            <TextField type="date" label="Complaint Date" InputLabelProps={{ shrink: true }} value={form.complaint_date} onChange={e => setForm({ ...form, complaint_date: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            const payload = {
              ...form,
              batch_id: form.batch_id ? Number(form.batch_id) : undefined,
              product_id: form.product_id ? Number(form.product_id) : undefined,
              complaint_date: form.complaint_date ? new Date(form.complaint_date).toISOString() : undefined,
            };
            await complaintsAPI.create(payload);
            setOpen(false);
            setForm({ customer_name: '', customer_contact: '', description: '', classification: 'other', severity: 'medium', batch_id: '', product_id: '', received_via: '', complaint_date: '' });
            load();
          }}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ComplaintsPage;


