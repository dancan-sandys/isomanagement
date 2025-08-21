import React, { useEffect, useState } from 'react';
import { Box, Stack, Typography, TextField, MenuItem, Select, InputLabel, FormControl, Button, Chip, Card, CardContent, Table, TableHead, TableRow, TableCell, TableBody } from '@mui/material';
import { auditsAPI, usersAPI } from '../services/api';

const AuditSchedule: React.FC = () => {
  const [audits, setAudits] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<{ department: string; auditor_id?: number; status: string }>(() => ({ department: '', auditor_id: undefined, status: '' }));
  const [userOptions, setUserOptions] = useState<Array<{ id: number; username: string; full_name?: string }>>([]);
  const [conflicts, setConflicts] = useState<{ total_conflicts: number; conflicts: any[] } | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const resp: any = await auditsAPI.listAudits({ department: filters.department || undefined, auditor_id: filters.auditor_id, status: filters.status || undefined, size: 200 });
      const items = resp?.items || resp?.data?.items || resp || [];
      setAudits(items);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);
  const checkConflicts = async () => {
    try {
      const res = await auditsAPI.detectScheduleConflicts({ department: filters.department || undefined, auditor_id: filters.auditor_id });
      setConflicts(res);
    } catch { setConflicts(null); }
  };
  useEffect(() => {
    (async () => {
      try {
        const resp: any = await usersAPI.getUsers({ page: 1, size: 50 });
        const items = (resp?.items || resp?.data?.items || resp?.data || resp || []) as Array<any>;
        setUserOptions(items.map((u) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch { setUserOptions([]); }
    })();
  }, []);

  return (
    <Box p={2}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2, gap: 1, flexWrap: 'wrap' }}>
        <Typography variant="h5">Audit Schedule</Typography>
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap' }}>
          <TextField size="small" label="Department" value={filters.department} onChange={(e) => setFilters({ ...filters, department: e.target.value })} />
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel>Auditor</InputLabel>
            <Select
              value={filters.auditor_id || ''}
              label="Auditor"
              onChange={(e) => setFilters({ ...filters, auditor_id: e.target.value ? Number(e.target.value) : undefined })}
            >
              <MenuItem value="">All</MenuItem>
              {userOptions.map((u) => (
                <MenuItem key={u.id} value={u.id}>{u.full_name ? `${u.full_name} (${u.username})` : u.username}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Status</InputLabel>
            <Select value={filters.status} label="Status" onChange={(e) => setFilters({ ...filters, status: String(e.target.value) })}>
              <MenuItem value="">All</MenuItem>
              <MenuItem value="planned">Planned</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="closed">Closed</MenuItem>
            </Select>
          </FormControl>
          <Button variant="contained" size="small" onClick={() => { load(); checkConflicts(); }}>Apply</Button>
          <Button variant="outlined" size="small" onClick={() => { setFilters({ department: '', auditor_id: undefined, status: '' }); load(); }}>Clear</Button>
          <Button variant="text" size="small" onClick={checkConflicts}>Check Conflicts</Button>
        </Stack>
      </Stack>

      {conflicts && (
        <Stack direction="row" spacing={1} sx={{ mb: 1, flexWrap: 'wrap' }}>
          <Chip color={conflicts.total_conflicts > 0 ? 'error' : 'success'} label={`Conflicts: ${conflicts.total_conflicts}`} />
        </Stack>
      )}

      <Card variant="outlined">
        <CardContent>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Auditor(s)</TableCell>
                <TableCell>Start</TableCell>
                <TableCell>End</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Overdue</TableCell>
                <TableCell>Update Dates</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {audits.map((a: any) => {
                const overdue = a.status !== 'completed' && a.end_date && new Date(a.end_date) < new Date();
                const [start, end] = [String(a.start_date || '').slice(0,10), String(a.end_date || '').slice(0,10)];
                const [newStart, setNewStart] = useState<string>(start);
                const [newEnd, setNewEnd] = useState<string>(end);
                return (
                  <TableRow key={a.id}>
                    <TableCell>{a.title}</TableCell>
                    <TableCell>{a.auditee_department || '-'}</TableCell>
                    <TableCell>{[a.lead_auditor_id, a.auditor_id].filter(Boolean).join(', ') || '-'}</TableCell>
                    <TableCell>{(a.start_date || '').toString().slice(0,10)}</TableCell>
                    <TableCell>{(a.end_date || '').toString().slice(0,10)}</TableCell>
                    <TableCell sx={{ textTransform: 'capitalize' }}>{String(a.status || '').replace('_',' ')}</TableCell>
                    <TableCell>{overdue ? <Chip color="error" label="Overdue" size="small" /> : '-'}</TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={1}>
                        <TextField size="small" type="date" value={newStart} onChange={(e) => setNewStart(e.target.value)} />
                        <TextField size="small" type="date" value={newEnd} onChange={(e) => setNewEnd(e.target.value)} />
                        <Button size="small" variant="outlined" onClick={async () => {
                          await auditsAPI.bulkUpdateSchedule([{ id: a.id, start_date: newStart || undefined, end_date: newEnd || undefined }]);
                          load(); checkConflicts();
                        }}>Save</Button>
                      </Stack>
                    </TableCell>
                  </TableRow>
                );
              })}
              {audits.length === 0 && (
                <TableRow><TableCell colSpan={7}>{loading ? 'Loading...' : 'No audits found'}</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AuditSchedule;

