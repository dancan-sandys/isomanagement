import React, { useEffect, useState } from 'react';
import { Box, Stack, Typography, TextField, Button, Card, CardContent, Table, TableHead, TableRow, TableCell, TableBody, Chip, MenuItem, Select, InputLabel, FormControl } from '@mui/material';
import { auditsAPI } from '../services/api';

const AuditReports: React.FC = () => {
  const [audits, setAudits] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<{ search: string; status: string; type: string }>({ search: '', status: '', type: '' });

  const load = async () => {
    setLoading(true);
    try {
      const resp: any = await auditsAPI.listAudits({ search: filters.search || undefined, status: filters.status || undefined, audit_type: (filters.type as any) || undefined, size: 100 });
      const items = resp?.items || resp?.data?.items || resp || [];
      setAudits(items);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename; a.click();
    window.URL.revokeObjectURL(url);
  };

  const exportList = async (format: 'pdf'|'xlsx') => {
    const blob = await auditsAPI.exportAudits(format, { search: filters.search || undefined, status: filters.status || undefined, audit_type: filters.type || undefined });
    downloadBlob(blob, `audits.${format}`);
  };

  return (
    <Box p={2}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2, gap: 1, flexWrap: 'wrap' }}>
        <Typography variant="h5">Audit Reports</Typography>
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap' }}>
          <TextField size="small" placeholder="Search" value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} />
          <FormControl size="small" sx={{ minWidth: 130 }}>
            <InputLabel>Status</InputLabel>
            <Select value={filters.status} label="Status" onChange={(e) => setFilters({ ...filters, status: String(e.target.value) })}>
              <MenuItem value="">All</MenuItem>
              <MenuItem value="planned">Planned</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="closed">Closed</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 130 }}>
            <InputLabel>Type</InputLabel>
            <Select value={filters.type} label="Type" onChange={(e) => setFilters({ ...filters, type: String(e.target.value) })}>
              <MenuItem value="">All</MenuItem>
              <MenuItem value="internal">Internal</MenuItem>
              <MenuItem value="external">External</MenuItem>
              <MenuItem value="supplier">Supplier</MenuItem>
            </Select>
          </FormControl>
          <Button variant="contained" size="small" onClick={load}>Search</Button>
          <Button variant="outlined" size="small" onClick={() => { setFilters({ search: '', status: '', type: '' }); load(); }}>Clear</Button>
          <Button size="small" onClick={() => exportList('pdf')}>Export PDF</Button>
          <Button size="small" variant="outlined" onClick={() => exportList('xlsx')}>Export XLSX</Button>
        </Stack>
      </Stack>

      <Card variant="outlined">
        <CardContent>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Start</TableCell>
                <TableCell>End</TableCell>
                <TableCell>Report</TableCell>
                <TableCell>Approval</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {audits.map((a: any) => (
                <TableRow key={a.id}>
                  <TableCell>{a.title}</TableCell>
                  <TableCell sx={{ textTransform: 'capitalize' }}>{String(a.audit_type || '').replace('_',' ')}</TableCell>
                  <TableCell sx={{ textTransform: 'capitalize' }}>{String(a.status || '').replace('_',' ')}</TableCell>
                  <TableCell>{(a.start_date || '').toString().slice(0,10)}</TableCell>
                  <TableCell>{(a.end_date || '').toString().slice(0,10)}</TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1}>
                      <Button size="small" onClick={async () => { const blob = await auditsAPI.exportReport(a.id, 'pdf'); const name = `audit_${a.id}.pdf`; const url = window.URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = name; link.click(); window.URL.revokeObjectURL(url); }}>PDF</Button>
                      <Button size="small" variant="outlined" onClick={async () => { const blob = await auditsAPI.exportReport(a.id, 'xlsx'); const name = `audit_${a.id}.xlsx`; const url = window.URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = name; link.click(); window.URL.revokeObjectURL(url); }}>XLSX</Button>
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1}>
                      <Button size="small" onClick={async () => { await auditsAPI.approveReport(a.id); alert('Report approved'); }}>Approve</Button>
                      <Button size="small" variant="outlined" onClick={async () => { const h = await auditsAPI.getReportHistory(a.id); const items = h?.items || []; const msg = items.map((r: any) => `v${r.version} by ${r.approved_by} at ${r.approved_at}`).join('\n') || 'No history'; alert(msg); }}>History</Button>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
              {audits.length === 0 && (
                <TableRow><TableCell colSpan={6}>{loading ? 'Loading...' : 'No audits found'}</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AuditReports;

