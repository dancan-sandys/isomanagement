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
      const resp = await auditsAPI.listAudits({ search });
      setAudits(resp.data?.items || resp.items || []);
      const s = await auditsAPI.getStats();
      setStats(s);
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
    const list = await auditsAPI.listAttachments(auditId);
    setAttachments(list);
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
    const blob = await auditsAPI.exportAudits(format, { search });
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
                    <Button size="small" onClick={() => window.open(`${process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'}/audits/attachments/${att.id}/download`, '_blank')}>Download</Button>
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



