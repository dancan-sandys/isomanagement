import React, { useEffect, useState } from 'react';
import { Box, Stack, Typography, TextField, FormControl, InputLabel, Select, MenuItem, Button, Card, CardContent, Table, TableHead, TableRow, TableCell, TableBody, Chip, IconButton, Checkbox } from '@mui/material';
import { Construction, Edit } from '@mui/icons-material';
import { auditsAPI } from '../services/api';

const AuditFindings: React.FC = () => {
  const [auditId, setAuditId] = useState<string>('');
  const [findings, setFindings] = useState<any[]>([]);
  const [filters, setFilters] = useState<{ severity: string; status: string }>({ severity: '', status: '' });
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<number[]>([]);
  const [analytics, setAnalytics] = useState<any | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      if (auditId) {
        const resp = await auditsAPI.listFindings(Number(auditId));
        let items: any[] = resp?.data || resp || [];
        if (filters.severity) items = items.filter(f => String(f.severity) === filters.severity);
        if (filters.status) items = items.filter(f => String(f.status) === filters.status);
        setFindings(items);
      } else {
        const resp = await auditsAPI.listAllFindings({ severity: filters.severity || undefined, status: filters.status || undefined, size: 100 });
        const items: any[] = resp?.items || resp?.data?.items || resp || [];
        setFindings(items);
      }
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [auditId, filters]);
  useEffect(() => { (async () => { try { const a = await auditsAPI.getFindingsAnalytics(); setAnalytics(a); } catch { setAnalytics(null); } })(); }, []);

  const toggleSelect = (id: number) => {
    setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  return (
    <Box p={2}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2, gap: 1, flexWrap: 'wrap' }}>
        <Typography variant="h5">Audit Findings</Typography>
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap' }}>
          <TextField size="small" label="Audit ID (optional)" value={auditId} onChange={(e) => setAuditId(e.target.value)} sx={{ width: 160 }} />
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Severity</InputLabel>
            <Select value={filters.severity} label="Severity" onChange={(e) => setFilters({ ...filters, severity: String(e.target.value) })}>
              <MenuItem value="">All</MenuItem>
              <MenuItem value="minor">Minor</MenuItem>
              <MenuItem value="major">Major</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Status</InputLabel>
            <Select value={filters.status} label="Status" onChange={(e) => setFilters({ ...filters, status: String(e.target.value) })}>
              <MenuItem value="">All</MenuItem>
              <MenuItem value="open">Open</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="verified">Verified</MenuItem>
              <MenuItem value="closed">Closed</MenuItem>
            </Select>
          </FormControl>
          <Button variant="contained" size="small" onClick={load}>Apply</Button>
          <Button variant="outlined" size="small" onClick={() => { setFilters({ severity: '', status: '' }); load(); }}>Clear</Button>
        </Stack>
      </Stack>

      <Card variant="outlined">
        <CardContent>
          {analytics && (
            <Stack direction="row" spacing={1} sx={{ mb: 1, flexWrap: 'wrap' }}>
              <Chip label={`Open: ${analytics.open_findings}`} color="warning" />
              <Chip label={`Overdue: ${analytics.overdue_findings}`} color={analytics.overdue_findings > 0 ? 'error' : 'default'} />
              <Chip label={`Critical: ${analytics.critical_findings}`} color={analytics.critical_findings > 0 ? 'error' : 'default'} />
              {typeof analytics.average_closure_days === 'number' && (
                <Chip label={`Avg closure: ${analytics.average_closure_days.toFixed(1)} d`} color="info" />
              )}
            </Stack>
          )}

          {selected.length > 0 && (
            <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
              <Button size="small" variant="contained" onClick={async () => { await auditsAPI.bulkUpdateFindingsStatus(selected, 'in_progress'); setSelected([]); load(); }}>Mark In Progress</Button>
              <Button size="small" variant="outlined" onClick={async () => { await auditsAPI.bulkUpdateFindingsStatus(selected, 'closed'); setSelected([]); load(); }}>Close</Button>
            </Stack>
          )}

          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox"><Checkbox size="small" indeterminate={selected.length>0 && selected.length<findings.length} checked={findings.length>0 && selected.length===findings.length} onChange={(e) => setSelected(e.target.checked ? findings.map(f=>f.id) : [])} /></TableCell>
                <TableCell>Clause</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Target Date</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {findings.map((f: any) => (
                <TableRow key={f.id}>
                  <TableCell padding="checkbox"><Checkbox size="small" checked={selected.includes(f.id)} onChange={() => toggleSelect(f.id)} /></TableCell>
                  <TableCell>{f.clause_ref || '-'}</TableCell>
                  <TableCell>{f.description}</TableCell>
                  <TableCell>{String(f.severity)}</TableCell>
                  <TableCell>{String(f.status)}</TableCell>
                  <TableCell>{(f.target_completion_date || '').toString().slice(0,10)}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small"><Edit /></IconButton>
                    <IconButton size="small" onClick={async () => { const nc = await auditsAPI.createNCFromFinding(f.id); window.open(`/nonconformance/${nc.id}`, '_blank'); }}><Construction /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {findings.length === 0 && (
                <TableRow><TableCell colSpan={6}>{loading ? 'Loading...' : 'No findings found'}</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AuditFindings;

