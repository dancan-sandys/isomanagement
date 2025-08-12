import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Stack, Button, TextField, Table, TableHead, TableRow, TableCell, TableBody, Dialog, DialogTitle, DialogContent, DialogActions, Select, MenuItem } from '@mui/material';
import { equipmentAPI } from '../services/equipmentAPI';

const EquipmentPage: React.FC = () => {
  const [list, setList] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: '', equipment_type: '', serial_number: '', location: '', notes: '' });
  const [planOpen, setPlanOpen] = useState(false);
  const [planForm, setPlanForm] = useState({ equipment_id: 0, frequency_days: 30, maintenance_type: 'preventive', notes: '' });
  const [woOpen, setWoOpen] = useState(false);
  const [woForm, setWoForm] = useState({ equipment_id: 0, plan_id: '', title: '', description: '' });
  const [workOrders, setWorkOrders] = useState<any[]>([]);
  // Calibration
  const [calOpen, setCalOpen] = useState(false);
  const [calForm, setCalForm] = useState({ equipment_id: 0, schedule_date: '', notes: '' });
  const [calUploadOpen, setCalUploadOpen] = useState(false);
  const [calUploadForm, setCalUploadForm] = useState<{ plan_id: number; file: File | null }>({ plan_id: 0, file: null });

  const load = async () => {
    const data = await equipmentAPI.list();
    setList(data || []);
    const wos = await equipmentAPI.listWorkOrders();
    setWorkOrders(wos || []);
  };
  useEffect(() => { load(); }, []);

  return (
    <Box p={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h5" fontWeight="bold">Equipment Register</Typography>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" onClick={() => setPlanOpen(true)}>New Maintenance Plan</Button>
          <Button variant="outlined" onClick={() => setWoOpen(true)}>New Work Order</Button>
          <Button variant="outlined" onClick={() => setCalOpen(true)}>New Calibration Plan</Button>
          <Button variant="outlined" onClick={() => setCalUploadOpen(true)}>Upload Calibration Certificate</Button>
          <Button variant="contained" onClick={() => setOpen(true)}>New Equipment</Button>
        </Stack>
      </Stack>
      <Paper>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Serial</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Created</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {list.map((e: any) => (
              <TableRow key={e.id}>
                <TableCell>{e.name}</TableCell>
                <TableCell>{e.equipment_type}</TableCell>
                <TableCell>{e.serial_number || '-'}</TableCell>
                <TableCell>{e.location || '-'}</TableCell>
                <TableCell>{e.created_at}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

      <Paper sx={{ mt: 2 }}>
        <Typography sx={{ p: 2 }} variant="subtitle1">Work Orders</Typography>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Equipment</TableCell>
              <TableCell>Plan</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Completed</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {workOrders.map((w: any) => (
              <TableRow key={w.id}>
                <TableCell>{w.id}</TableCell>
                <TableCell>{w.equipment_id}</TableCell>
                <TableCell>{w.plan_id || '-'}</TableCell>
                <TableCell>{w.title}</TableCell>
                <TableCell>{w.created_at}</TableCell>
                <TableCell>{w.completed_at || '-'}</TableCell>
                <TableCell align="right">
                  {!w.completed_at && (
                    <Button size="small" onClick={async () => { await equipmentAPI.completeWorkOrder(w.id); load(); }}>Mark Complete</Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Equipment</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
            <TextField label="Type" value={form.equipment_type} onChange={e => setForm({ ...form, equipment_type: e.target.value })} />
            <TextField label="Serial Number" value={form.serial_number} onChange={e => setForm({ ...form, serial_number: e.target.value })} />
            <TextField label="Location" value={form.location} onChange={e => setForm({ ...form, location: e.target.value })} />
            <TextField label="Notes" multiline rows={3} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => { await equipmentAPI.create({ ...form, serial_number: form.serial_number || undefined, location: form.location || undefined, notes: form.notes || undefined }); setOpen(false); setForm({ name: '', equipment_type: '', serial_number: '', location: '', notes: '' }); load(); }}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* Calibration plan dialog */}
      <Dialog open={calOpen} onClose={() => setCalOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Calibration Plan</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField type="number" label="Equipment ID" value={calForm.equipment_id} onChange={e => setCalForm({ ...calForm, equipment_id: Number(e.target.value || 0) })} />
            <TextField type="date" label="Schedule Date" InputLabelProps={{ shrink: true }} value={calForm.schedule_date} onChange={e => setCalForm({ ...calForm, schedule_date: e.target.value })} />
            <TextField label="Notes" multiline rows={3} value={calForm.notes} onChange={e => setCalForm({ ...calForm, notes: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCalOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            const isoDate = calForm.schedule_date ? new Date(calForm.schedule_date).toISOString() : new Date().toISOString();
            await equipmentAPI.createCalibrationPlan(calForm.equipment_id, { schedule_date: isoDate, notes: calForm.notes || undefined });
            setCalOpen(false);
            setCalForm({ equipment_id: 0, schedule_date: '', notes: '' });
          }}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* Calibration certificate upload dialog */}
      <Dialog open={calUploadOpen} onClose={() => setCalUploadOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Calibration Certificate</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField type="number" label="Calibration Plan ID" value={calUploadForm.plan_id} onChange={e => setCalUploadForm({ ...calUploadForm, plan_id: Number(e.target.value || 0) })} />
            <Button component="label" variant="outlined">
              {calUploadForm.file ? 'Change File' : 'Choose File'}
              <input hidden type="file" onChange={(e) => {
                const f = e.target.files && e.target.files[0];
                setCalUploadForm({ ...calUploadForm, file: f || null });
              }} />
            </Button>
            {calUploadForm.file && <Typography variant="body2">{calUploadForm.file.name}</Typography>}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCalUploadOpen(false)}>Cancel</Button>
          <Button variant="contained" disabled={!calUploadForm.plan_id || !calUploadForm.file} onClick={async () => {
            if (!calUploadForm.file) return;
            await equipmentAPI.uploadCalibrationCertificate(calUploadForm.plan_id, calUploadForm.file);
            setCalUploadOpen(false);
            setCalUploadForm({ plan_id: 0, file: null });
          }}>Upload</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={woOpen} onClose={() => setWoOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Work Order</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField type="number" label="Equipment ID" value={woForm.equipment_id} onChange={e => setWoForm({ ...woForm, equipment_id: Number(e.target.value || 0) })} />
            <TextField type="number" label="Plan ID (optional)" value={woForm.plan_id} onChange={e => setWoForm({ ...woForm, plan_id: e.target.value })} />
            <TextField label="Title" value={woForm.title} onChange={e => setWoForm({ ...woForm, title: e.target.value })} />
            <TextField label="Description" multiline rows={3} value={woForm.description} onChange={e => setWoForm({ ...woForm, description: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWoOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => { await equipmentAPI.createWorkOrder({ equipment_id: Number(woForm.equipment_id), plan_id: woForm.plan_id ? Number(woForm.plan_id) : undefined, title: woForm.title, description: woForm.description || undefined }); setWoOpen(false); setWoForm({ equipment_id: 0, plan_id: '', title: '', description: '' }); load(); }}>Create</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={planOpen} onClose={() => setPlanOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Maintenance Plan</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField type="number" label="Equipment ID" value={planForm.equipment_id} onChange={e => setPlanForm({ ...planForm, equipment_id: Number(e.target.value || 0) })} />
            <TextField type="number" label="Frequency (days)" value={planForm.frequency_days} onChange={e => setPlanForm({ ...planForm, frequency_days: Number(e.target.value || 0) })} />
            <Select value={planForm.maintenance_type} onChange={e => setPlanForm({ ...planForm, maintenance_type: e.target.value as any })}>
              <MenuItem value="preventive">Preventive</MenuItem>
              <MenuItem value="corrective">Corrective</MenuItem>
            </Select>
            <TextField label="Notes" multiline rows={3} value={planForm.notes} onChange={e => setPlanForm({ ...planForm, notes: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPlanOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => { await equipmentAPI.createMaintenancePlan(planForm.equipment_id, { frequency_days: planForm.frequency_days, maintenance_type: planForm.maintenance_type as any, notes: planForm.notes || undefined }); setPlanOpen(false); setPlanForm({ equipment_id: 0, frequency_days: 30, maintenance_type: 'preventive', notes: '' }); }}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EquipmentPage;


