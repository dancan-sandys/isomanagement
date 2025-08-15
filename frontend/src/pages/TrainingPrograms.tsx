import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Typography, Paper, Stack, Button, TextField, Table, TableHead, TableRow, TableCell, TableBody, Dialog, DialogTitle, DialogContent, DialogActions, Autocomplete } from '@mui/material';
import { rbacAPI, Role } from '../services/rbacAPI';
import { trainingAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { AppDispatch, RootState } from '../store';
import { createProgram, deleteProgram, fetchPrograms } from '../store/slices/trainingSlice';
// duplicate import removed

const TrainingPrograms: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { programs } = useSelector((s: RootState) => s.training as any);
  const [search, setSearch] = useState('');
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ code: '', title: '', description: '', department: '' });
  const [roles, setRoles] = useState<Role[]>([]);
  const [assignOpen, setAssignOpen] = useState(false);
  const [selectedProgramId, setSelectedProgramId] = useState<number | null>(null);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [requiredList, setRequiredList] = useState<any[]>([]);

  useEffect(() => { dispatch(fetchPrograms()); }, [dispatch]);
  useEffect(() => { (async () => { const r = await rbacAPI.getRoles(); setRoles(r || []); })(); }, []);

  const onCreate = async () => {
    if (!form.code || !form.title) return;
    await dispatch(createProgram({ code: form.code, title: form.title, description: form.description || undefined, department: form.department || undefined }));
    setOpen(false);
    setForm({ code: '', title: '', description: '', department: '' });
  };

  return (
    <Box p={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h5" fontWeight="bold">Training Programs</Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField size="small" placeholder="Search" value={search} onChange={e => setSearch(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') dispatch(fetchPrograms(search)); }} />
          <Button variant="contained" onClick={() => setOpen(true)}>New Program</Button>
        </Stack>
      </Stack>

      <Paper>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Code</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {programs.map((p: any) => (
              <TableRow key={p.id} hover sx={{ cursor: 'pointer' }} onClick={() => navigate(`/training/programs/${p.id}`)}>
                <TableCell>{p.code}</TableCell>
                <TableCell>{p.title}</TableCell>
                <TableCell>{p.department || '-'}</TableCell>
                <TableCell>{p.created_at}</TableCell>
                <TableCell align="right">
                  <Button size="small" onClick={async (e) => { e.stopPropagation(); setSelectedProgramId(p.id); const list = await trainingAPI.listRequiredTrainings({ program_id: p.id }); setRequiredList(list || []); setAssignOpen(true); }}>Assign Required</Button>
                  <Button size="small" color="error" onClick={(e) => { e.stopPropagation(); dispatch(deleteProgram(p.id)); }}>Delete</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Training Program</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Code" value={form.code} onChange={e => setForm({ ...form, code: e.target.value })} />
            <TextField label="Title" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
            <TextField label="Department" value={form.department} onChange={e => setForm({ ...form, department: e.target.value })} />
            <TextField label="Description" multiline rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={onCreate}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* Assign Required Training */}
      <Dialog open={assignOpen} onClose={() => setAssignOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Assign Required Training</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Autocomplete
              options={roles}
              getOptionLabel={(r) => r.name}
              value={selectedRole}
              onChange={(_, val) => setSelectedRole(val)}
              renderInput={(params) => <TextField {...params} label="Role" placeholder="Select role" />}
            />
            <Button variant="contained" disabled={!selectedRole || !selectedProgramId} onClick={async () => {
              if (!selectedRole || !selectedProgramId) return;
              await trainingAPI.assignRequiredTraining({ role_id: selectedRole.id, program_id: selectedProgramId });
              const list = await trainingAPI.listRequiredTrainings({ program_id: selectedProgramId });
              setRequiredList(list || []);
            }}>Assign</Button>
            <Paper variant="outlined" sx={{ p: 1 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Role</TableCell>
                    <TableCell>Mandatory</TableCell>
                    <TableCell>Assigned</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {requiredList.map((r: any) => (
                    <TableRow key={r.id}>
                      <TableCell>{roles.find(x => x.id === r.role_id)?.name || r.role_id}</TableCell>
                      <TableCell>{String(r.is_mandatory)}</TableCell>
                      <TableCell>{r.created_at}</TableCell>
                      <TableCell align="right"><Button size="small" color="error" onClick={async () => { await trainingAPI.deleteRequiredTraining(r.id); const list = await trainingAPI.listRequiredTrainings({ program_id: selectedProgramId! }); setRequiredList(list || []); }}>Remove</Button></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Paper>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TrainingPrograms;


