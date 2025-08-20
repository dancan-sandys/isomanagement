import React, { useEffect, useState } from 'react';
import { Box, Card, CardContent, Typography, Stack, Button, Table, TableHead, TableRow, TableCell, TableBody, IconButton, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Select, MenuItem, InputLabel, FormControl, Autocomplete, Chip, Tooltip } from '@mui/material';
import { Add, Edit, Delete, Download, AttachFile, Visibility } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { auditsAPI, usersAPI } from '../services/api';

const Audits: React.FC = () => {
  const navigate = useNavigate();
  const [audits, setAudits] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<any | null>(null);
  const [form, setForm] = useState<any>({ title: '', audit_type: 'internal', status: 'planned', auditee_department: '' });
  const [search, setSearch] = useState('');
  const [stats, setStats] = useState<any | null>(null);
  const [kpis, setKpis] = useState<any | null>(null);
  const [kpiFilters, setKpiFilters] = useState({ period: 'month' as 'month' | 'week' | 'quarter' | 'year', department: '', auditor_id: undefined as number | undefined });
  const [attachmentsOpen, setAttachmentsOpen] = useState(false);
  const [attachments, setAttachments] = useState<any[]>([]);
  const [attachmentsAuditId, setAttachmentsAuditId] = useState<number | null>(null);
  const [userOptions, setUserOptions] = useState<Array<{ id: number; username: string; full_name?: string }>>([]);
  const [leadOpen, setLeadOpen] = useState(false);
  const [auditorOpen, setAuditorOpen] = useState(false);
  const [leadInput, setLeadInput] = useState('');
  const [auditorInput, setAuditorInput] = useState('');
  const [leadSelected, setLeadSelected] = useState<{ id: number; username: string; full_name?: string } | null>(null);
  const [auditorSelected, setAuditorSelected] = useState<{ id: number; username: string; full_name?: string } | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      // Combine search with KPI filters for audit list
      const auditParams = { 
        search,
        department: kpiFilters.department || undefined,
        auditor_id: kpiFilters.auditor_id || undefined
      };
      const resp = await auditsAPI.listAudits(auditParams);
      setAudits(resp?.data?.items || resp?.items || resp || []);
      try {
        const s = await auditsAPI.getStats();
        setStats(s?.data || s || null);
      } catch (e) {
        setStats(null);
      }
      try {
        const k = await auditsAPI.getKpisOverview(kpiFilters);
        setKpis(k?.data || k || null);
      } catch (e) {
        setKpis(null);
      }
    } catch (e) {
      setAudits([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);
  useEffect(() => {
    // hydrate selected values when editing existing audit
    if (editing) {
      if (editing.lead_auditor_id) {
        const match = userOptions.find(u => u.id === editing.lead_auditor_id);
        if (match) setLeadSelected(match);
      }
      if (editing.auditor_id) {
        const match2 = userOptions.find(u => u.id === editing.auditor_id);
        if (match2) setAuditorSelected(match2);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editing, userOptions]);

  // Debounced user search like CAPA modal: trigger only when field is open and input length >= 2
  useEffect(() => {
    let active = true;
    const query = leadOpen ? leadInput.trim() : auditorOpen ? auditorInput.trim() : '';
    if (!(leadOpen || auditorOpen)) return;
    if (query.length < 2) {
      setUserOptions([]);
      return;
    }
    const t = setTimeout(async () => {
      try {
        const resp: any = await usersAPI.getUsers({ page: 1, size: 10, search: query });
        const items = (resp?.data?.items || resp?.items || []) as Array<any>;
        if (active) setUserOptions(items.map((u) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch {
        if (active) setUserOptions([]);
      }
    }, 300);
    return () => { active = false; clearTimeout(t); };
  }, [leadOpen, auditorOpen, leadInput, auditorInput]);

  const handleSubmit = async () => {
    const payload = { ...form };
    if (editing) {
      await auditsAPI.updateAudit(editing.id, payload);
    } else {
      await auditsAPI.createAudit(payload);
    }
    setOpen(false); setEditing(null); setForm({ title: '', audit_type: 'internal', status: 'planned', auditee_department: '' });
    setLeadSelected(null); setAuditorSelected(null); setLeadInput(''); setAuditorInput('');
    load();
  };

  const deleteAudit = async (row: any) => { if (window.confirm('Delete this audit?')) { await auditsAPI.deleteAudit(row.id); load(); } };
  const openAttachments = async (auditId: number) => {
    setAttachmentsAuditId(auditId);
    try {
      const list = await auditsAPI.listAttachments(auditId);
      setAttachments(list?.data || list || []);
    } catch (e) {
      setAttachments([]);
    }
    setAttachmentsOpen(true);
  };
  const removeAttachment = async (attachmentId: number) => {
    if (!attachmentsAuditId) return;
    if (!window.confirm('Delete this attachment?')) return;
    await auditsAPI.deleteAttachment(attachmentId);
    const list = await auditsAPI.listAttachments(attachmentsAuditId);
    setAttachments(list);
  };
  const downloadBlob = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename; a.click();
    window.URL.revokeObjectURL(url);
  };
  const exportList = async (format: 'pdf'|'xlsx') => {
    const exportFilters = { 
      search,
      department: kpiFilters.department || undefined,
      auditor_id: kpiFilters.auditor_id || undefined
    };
    const blob = await auditsAPI.exportAudits(format, exportFilters);
    downloadBlob(blob, `audits.${format}`);
  };
  const exportRow = async (row: any, format: 'pdf'|'xlsx') => {
    const blob = await auditsAPI.exportReport(row.id, format);
    downloadBlob(blob, `audit_${row.id}.${format}`);
  };

  return (
    <Box>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
        <Typography variant="h5">Audit Management</Typography>
        <Stack direction="row" spacing={1}>
          <TextField size="small" placeholder="Search audits" value={search} onChange={(e) => setSearch(e.target.value)} />
          <Button variant="outlined" onClick={load}>Search</Button>
          <Button variant="contained" startIcon={<Add />} onClick={() => setOpen(true)}>New Audit</Button>
        </Stack>
      </Stack>

      {stats && (
        <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap' }}>
          <Chip label={`Total: ${stats.total}`} />
          {Object.entries(stats.by_status || {}).map(([k,v]: any) => (
            <Chip key={k} label={`${k.replace('_',' ')}: ${v}`} />
          ))}
          {Object.entries(stats.by_type || {}).map(([k,v]: any) => (
            <Chip key={k} label={`${k}: ${v}`} />
          ))}
          <Tooltip title="Export list PDF"><Button size="small" startIcon={<Download />} onClick={() => exportList('pdf')}>Export PDF</Button></Tooltip>
          <Tooltip title="Export list XLSX"><Button size="small" variant="outlined" startIcon={<Download />} onClick={() => exportList('xlsx')}>Export XLSX</Button></Tooltip>
        </Stack>
      )}

      {kpis && (
        <Box sx={{ mb: 2 }}>
          {/* KPI Filters */}
          <Stack direction="row" spacing={2} sx={{ mb: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Period</InputLabel>
              <Select 
                value={kpiFilters.period} 
                label="Period"
                onChange={(e) => {
                  setKpiFilters({ ...kpiFilters, period: e.target.value as 'week' | 'month' | 'quarter' | 'year' });
                }}
              >
                <MenuItem value="week">Week</MenuItem>
                <MenuItem value="month">Month</MenuItem>
                <MenuItem value="quarter">Quarter</MenuItem>
                <MenuItem value="year">Year</MenuItem>
              </Select>
            </FormControl>
            <TextField 
              size="small" 
              label="Department" 
              value={kpiFilters.department}
              onChange={(e) => setKpiFilters({ ...kpiFilters, department: e.target.value })}
              onKeyPress={(e) => e.key === 'Enter' && load()}
              sx={{ minWidth: 150 }}
            />
            <Button 
              variant="contained" 
              size="small"
              onClick={() => load()}
            >
              Apply Filters
            </Button>
            <Button 
              variant="outlined" 
              size="small"
              onClick={() => {
                setKpiFilters({ period: 'month', department: '', auditor_id: undefined });
                load();
              }}
            >
              Clear Filters
            </Button>
          </Stack>
          
          {/* KPI Metrics */}
          <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
            {/* Core KPIs */}
            {typeof kpis.lead_time_days_avg === 'number' && <Chip color="primary" label={`Lead time avg: ${kpis.lead_time_days_avg.toFixed(1)} d`} />}
            {typeof kpis.on_time_audit_rate === 'number' && <Chip color="primary" label={`On-time rate: ${(kpis.on_time_audit_rate * 100).toFixed(0)}%`} />}
            {typeof kpis.finding_closure_days_avg === 'number' && <Chip color="primary" label={`Closure avg: ${kpis.finding_closure_days_avg.toFixed(1)} d`} />}
            
            {/* Audit Counts */}
            <Chip color="info" label={`Total: ${kpis.total_audits || 0}`} />
            <Chip color="success" label={`Completed: ${kpis.completed_audits || 0}`} />
            {kpis.overdue_audits > 0 && <Chip color="error" label={`Overdue: ${kpis.overdue_audits}`} />}
            
            {/* Finding Counts */}
            <Chip color="warning" label={`Findings: ${kpis.total_findings || 0}`} />
            {kpis.open_findings > 0 && <Chip color="warning" label={`Open: ${kpis.open_findings}`} />}
            {kpis.overdue_findings > 0 && <Chip color="error" label={`Overdue: ${kpis.overdue_findings}`} />}
            {kpis.critical_findings > 0 && <Chip color="error" label={`Critical: ${kpis.critical_findings}`} />}
          </Stack>
        </Box>
      )}

      <Card variant="outlined">
        <CardContent>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Auditee Dept</TableCell>
                <TableCell>Dates</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {audits.map((a) => (
                <TableRow key={a.id} hover>
                  <TableCell>{a.title}</TableCell>
                  <TableCell sx={{ textTransform: 'capitalize' }}>{String(a.audit_type || '').replace('_',' ')}</TableCell>
                  <TableCell sx={{ textTransform: 'capitalize' }}>{String(a.status || '').replace('_',' ')}</TableCell>
                  <TableCell>{a.auditee_department || '-'}</TableCell>
                  <TableCell>{(a.start_date || '').toString().slice(0,10)} {(a.end_date ? '→ ' + a.end_date.toString().slice(0,10) : '')}</TableCell>
                  <TableCell align="right">
                    <Tooltip title="View"><IconButton size="small" onClick={() => navigate(`/audits/${a.id}`)}><Visibility /></IconButton></Tooltip>
                    <Tooltip title="Edit"><IconButton size="small" onClick={() => { setEditing(a); setForm({ ...a, audit_type: a.audit_type, status: a.status }); setOpen(true); }}><Edit /></IconButton></Tooltip>
                    <Tooltip title="Attachments"><IconButton size="small" onClick={() => openAttachments(a.id)}><AttachFile /></IconButton></Tooltip>
                    <Tooltip title="Report PDF"><IconButton size="small" onClick={() => exportRow(a, 'pdf')}><Download /></IconButton></Tooltip>
                    <Tooltip title="Report XLSX"><IconButton size="small" onClick={() => exportRow(a, 'xlsx')}><Download /></IconButton></Tooltip>
                    <IconButton size="small" color="error" onClick={() => deleteAudit(a)}><Delete /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {audits.length === 0 && (
                <TableRow><TableCell colSpan={6}><Typography variant="body2" color="text.secondary">No audits found.</Typography></TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={open} onClose={() => { setOpen(false); setEditing(null); }} maxWidth="sm" fullWidth>
        <DialogTitle>{editing ? 'Edit Audit' : 'Create Audit'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} fullWidth />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select value={form.audit_type} label="Type" onChange={(e) => setForm({ ...form, audit_type: e.target.value })}>
                  <MenuItem value="internal">Internal</MenuItem>
                  <MenuItem value="external">External</MenuItem>
                  <MenuItem value="supplier">Supplier</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select value={form.status} label="Status" onChange={(e) => setForm({ ...form, status: e.target.value })}>
                  <MenuItem value="planned">Planned</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="closed">Closed</MenuItem>
                </Select>
              </FormControl>
            </Stack>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField type="date" label="Start Date" InputLabelProps={{ shrink: true }} value={form.start_date || ''} onChange={(e) => setForm({ ...form, start_date: e.target.value })} fullWidth />
              <TextField type="date" label="End Date" InputLabelProps={{ shrink: true }} value={form.end_date || ''} onChange={(e) => setForm({ ...form, end_date: e.target.value })} fullWidth />
            </Stack>
            <TextField label="Scope" value={form.scope || ''} onChange={(e) => setForm({ ...form, scope: e.target.value })} fullWidth multiline minRows={2} />
            <TextField label="Objectives" value={form.objectives || ''} onChange={(e) => setForm({ ...form, objectives: e.target.value })} fullWidth multiline minRows={2} />
            <TextField label="Criteria" value={form.criteria || ''} onChange={(e) => setForm({ ...form, criteria: e.target.value })} fullWidth multiline minRows={2} />
            <TextField label="Auditee Department" value={form.auditee_department || ''} onChange={(e) => setForm({ ...form, auditee_department: e.target.value })} fullWidth />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <Autocomplete
                options={userOptions}
                open={leadOpen}
                onOpen={() => setLeadOpen(true)}
                onClose={() => setLeadOpen(false)}
                getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                value={leadSelected}
                onChange={(_, val) => {
                  setLeadSelected(val);
                  setForm({ ...form, lead_auditor_id: val ? val.id : null });
                }}
                inputValue={leadInput}
                onInputChange={(_, val) => setLeadInput(val)}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
                renderInput={(params) => <TextField {...params} label="Lead Auditor" placeholder="Type at least 2 characters" fullWidth />}
              />
              <Autocomplete
                options={userOptions}
                open={auditorOpen}
                onOpen={() => setAuditorOpen(true)}
                onClose={() => setAuditorOpen(false)}
                getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                value={auditorSelected}
                onChange={(_, val) => {
                  setAuditorSelected(val);
                  setForm({ ...form, auditor_id: val ? val.id : null });
                }}
                inputValue={auditorInput}
                onInputChange={(_, val) => setAuditorInput(val)}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
                renderInput={(params) => <TextField {...params} label="Auditor" placeholder="Type at least 2 characters" fullWidth />}
              />
            </Stack>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setOpen(false); setEditing(null); }}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>{editing ? 'Save Changes' : 'Create'}</Button>
        </DialogActions>
      </Dialog>

      {/* Attachments dialog */}
      <Dialog open={attachmentsOpen} onClose={() => setAttachmentsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Audit Attachments</DialogTitle>
        <DialogContent>
          {attachments.length === 0 ? (
            <Typography variant="body2" color="text.secondary">No attachments</Typography>
          ) : (
            <Stack spacing={1} sx={{ mt: 1 }}>
              {attachments.map((att: any) => (
                <Stack key={att.id} direction="row" alignItems="center" justifyContent="space-between">
                  <Typography variant="body2">{att.filename}</Typography>
                  <Stack direction="row" spacing={1}>
                    <Button size="small" onClick={() => window.open(`/api/v1/audits/attachments/${att.id}/download`, '_blank')}>Download</Button>
                    <Button size="small" color="error" onClick={() => removeAttachment(att.id)}>Delete</Button>
                  </Stack>
                </Stack>
              ))}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAttachmentsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Audits;



