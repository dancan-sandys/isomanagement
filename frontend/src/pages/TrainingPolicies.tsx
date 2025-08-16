import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid, FormControl, InputLabel, Select, MenuItem, Button, Table, TableHead, TableRow, TableCell, TableBody, Alert } from '@mui/material';
import { trainingAPI } from '../services/api';

const TrainingPolicies: React.FC = () => {
  const [programs, setPrograms] = useState<any[]>([]);
  const [scoped, setScoped] = useState<any[]>([]);
  const [roleId, setRoleId] = useState<string>('');
  const [action, setAction] = useState<'monitor'|'verify'>('monitor');
  const [programId, setProgramId] = useState<string>('');
  const [ccpId, setCcpId] = useState<string>('');
  const [equipmentId, setEquipmentId] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const progs = await trainingAPI.getPrograms();
        setPrograms(progs || []);
      } catch (e: any) {
        setError(e?.message || 'Failed to load programs');
      }
    })();
  }, []);

  const refreshList = async () => {
    if (!roleId) return;
    try {
      const list = await trainingAPI.listScopedRequired({ role_id: parseInt(roleId) });
      setScoped(list || []);
    } catch (e: any) {
      setError(e?.message || 'Failed to load policies');
    }
  };

  useEffect(() => { refreshList(); }, [roleId]);

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight="bold" gutterBottom>Training Policies (HACCP Scoped Requirements)</Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth size="small">
              <InputLabel id="role-label">Role ID</InputLabel>
              <Select labelId="role-label" value={roleId} label="Role ID" onChange={(e) => setRoleId(e.target.value as string)}>
                {/* Simple numeric input via select for now; later: load roles */}
                {[1,2,3,4,5,6,7,8,9,10].map(id => (
                  <MenuItem key={id} value={String(id)}>{id}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={2}>
            <FormControl fullWidth size="small">
              <InputLabel id="action-label">Action</InputLabel>
              <Select labelId="action-label" value={action} label="Action" onChange={(e) => setAction(e.target.value as 'monitor'|'verify')}>
                <MenuItem value="monitor">Monitor</MenuItem>
                <MenuItem value="verify">Verify</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth size="small">
              <InputLabel id="program-label">Program</InputLabel>
              <Select labelId="program-label" value={programId} label="Program" onChange={(e) => setProgramId(e.target.value as string)}>
                {programs.map((p: any) => (
                  <MenuItem key={p.id} value={String(p.id)}>{p.code} — {p.title}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={2}>
            <FormControl fullWidth size="small">
              <InputLabel id="ccp-label">CCP ID</InputLabel>
              <Select labelId="ccp-label" value={ccpId} label="CCP ID" onChange={(e) => setCcpId(e.target.value as string)}>
                <MenuItem value="">(none)</MenuItem>
                {/* Placeholder selector; production would load CCPs by product */}
                {[1,2,3,4,5].map(id => (<MenuItem key={id} value={String(id)}>{id}</MenuItem>))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={2}>
            <FormControl fullWidth size="small">
              <InputLabel id="eq-label">Equipment ID</InputLabel>
              <Select labelId="eq-label" value={equipmentId} label="Equipment ID" onChange={(e) => setEquipmentId(e.target.value as string)}>
                <MenuItem value="">(none)</MenuItem>
                {[1,2,3,4,5].map(id => (<MenuItem key={id} value={String(id)}>{id}</MenuItem>))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={12}>
            <Button variant="contained" disabled={!roleId || !programId} onClick={async () => {
              try {
                await trainingAPI.assignScopedRequired({
                  role_id: parseInt(roleId),
                  action,
                  program_id: parseInt(programId),
                  ccp_id: ccpId ? parseInt(ccpId) : undefined,
                  equipment_id: equipmentId ? parseInt(equipmentId) : undefined,
                });
                await refreshList();
              } catch (e: any) {
                setError(e?.message || 'Failed to assign');
              }
            }}>Add Policy</Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Role</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Scope</TableCell>
              <TableCell>Program</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {scoped.map((rt: any) => {
              const program = programs.find((p: any) => p.id === rt.program_id);
              const progLabel = program ? `${program.code} — ${program.title}` : `#${rt.program_id}`;
              const scope = [rt.ccp_id ? `CCP ${rt.ccp_id}` : null, rt.equipment_id ? `EQ ${rt.equipment_id}` : null].filter(Boolean).join(' / ') || 'Role-wide';
              return (
                <TableRow key={rt.id}>
                  <TableCell>{rt.role_id}</TableCell>
                  <TableCell>{rt.action}</TableCell>
                  <TableCell>{scope}</TableCell>
                  <TableCell>{progLabel}</TableCell>
                  <TableCell align="right">
                    <Button size="small" color="error" onClick={async () => {
                      try {
                        await trainingAPI.deleteScopedRequired(rt.id);
                        await refreshList();
                      } catch (e: any) {
                        setError(e?.message || 'Failed to delete');
                      }
                    }}>Remove</Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
};

export default TrainingPolicies;


