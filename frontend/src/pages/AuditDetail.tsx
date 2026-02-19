import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Tabs, Tab, Stack, Typography, Button, TextField, Table, TableHead, TableRow, TableCell, TableBody, Dialog, DialogTitle, DialogContent, DialogActions, Autocomplete, Select, MenuItem, InputLabel, FormControl, IconButton, Alert } from '@mui/material';
import { Edit, AttachFile, Delete, UploadFile, Construction } from '@mui/icons-material';
import { auditsAPI, usersAPI } from '../services/api';

const AuditDetail: React.FC = () => {
  const { id } = useParams();
  const auditId = Number(id);
  const [tab, setTab] = useState(0);
  const [audit, setAudit] = useState<any | null>(null);
  const [items, setItems] = useState<any[]>([]);
  const [findings, setFindings] = useState<any[]>([]);
  const [addItemOpen, setAddItemOpen] = useState(false);
  const [newItem, setNewItem] = useState<any>({ clause_ref: '', question: '' });
  const [addFindingOpen, setAddFindingOpen] = useState(false);
  const [newFinding, setNewFinding] = useState<any>({ clause_ref: '', description: '', severity: 'minor' });
  const [editItemOpen, setEditItemOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<any | null>(null);
  const [itemAttachmentsOpen, setItemAttachmentsOpen] = useState(false);
  const [itemAttachments, setItemAttachments] = useState<any[]>([]);
  const [itemForAttachments, setItemForAttachments] = useState<number | null>(null);
  const [editFindingOpen, setEditFindingOpen] = useState(false);
  const [editingFinding, setEditingFinding] = useState<any | null>(null);
  const [findingAttachmentsOpen, setFindingAttachmentsOpen] = useState(false);
  const [findingAttachments, setFindingAttachments] = useState<any[]>([]);
  const [findingForAttachments, setFindingForAttachments] = useState<number | null>(null);
  const [attachments, setAttachments] = useState<any[]>([]);
  const [auditees, setAuditees] = useState<any[]>([]);
  const [addAuditeeOpen, setAddAuditeeOpen] = useState(false);
  const [userOptions, setUserOptions] = useState<any[]>([]);
  const [userOpen, setUserOpen] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [userSelected, setUserSelected] = useState<any | null>(null);
  const [role, setRole] = useState('');
  const [plan, setPlan] = useState<any | null>(null);
  const [planForm, setPlanForm] = useState<any>({ agenda: '', criteria_refs: '', sampling_plan: '', documents_to_review: '', logistics: '' });

  const load = async () => {
    const a = await auditsAPI.getAudit(auditId); setAudit(a);
    const att = await auditsAPI.listAttachments(auditId); setAttachments(att);
    const au = await auditsAPI.listAuditees?.(auditId).catch(() => []); if (au) setAuditees(au);
    const it = await auditsAPI.listChecklistItems(auditId); setItems(it);
    const fs = await auditsAPI.listFindings(auditId); setFindings(fs);
    try { const p = await auditsAPI.getPlan(auditId); setPlan(p); setPlanForm({ agenda: p.agenda || '', criteria_refs: p.criteria_refs || '', sampling_plan: p.sampling_plan || '', documents_to_review: p.documents_to_review || '', logistics: p.logistics || '' }); } catch {}
  };

  useEffect(() => { if (!Number.isNaN(auditId)) load(); }, [auditId]);

  useEffect(() => {
    let active = true;
    const q = userOpen ? userInput.trim() : '';
    if (!userOpen) return;
    if (q.length < 2) { setUserOptions([]); return; }
    const t = setTimeout(async () => {
      try {
        const resp: any = await usersAPI.getUsers({ page: 1, size: 10, search: q });
        const items = (resp?.data?.items || resp?.items || []) as Array<any>;
        if (active) setUserOptions(items.map((u) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch { if (active) setUserOptions([]); }
    }, 300);
    return () => { active = false; clearTimeout(t); };
  }, [userOpen, userInput]);

  const addAuditee = async () => {
    if (!userSelected?.id) return;
    await auditsAPI.addAuditee?.(auditId, userSelected.id, role);
    setAddAuditeeOpen(false); setUserSelected(null); setUserInput(''); setRole('');
    const au = await auditsAPI.listAuditees?.(auditId).catch(() => []); if (au) setAuditees(au);
  };

  if (!audit) return null;

  return (
    <Box p={3}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
        <Typography variant="h5">Audit: {audit.title}</Typography>
      </Stack>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Overview" />
        <Tab label="Checklist" />
        <Tab label="Findings" />
        <Tab label="Attachments" />
        <Tab label="Auditees" />
        <Tab label="Plan" />
      </Tabs>

      {tab === 0 && (
        <Stack spacing={1}>
          <Typography variant="body2">Type: {audit.audit_type}</Typography>
          <Typography variant="body2">Status: {audit.status}</Typography>
          <Typography variant="body2">Scope: {audit.scope || '-'}</Typography>
          <Typography variant="body2">Objectives: {audit.objectives || '-'}</Typography>
          <Typography variant="body2">Criteria: {audit.criteria || '-'}</Typography>
        </Stack>
      )}

      {tab === 1 && (
        <Box>
          <Stack direction="row" justifyContent="flex-end" sx={{ mb: 1 }}>
            <Button variant="contained" onClick={() => setAddItemOpen(true)}>Add Item</Button>
          </Stack>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Clause</TableCell>
                <TableCell>Question</TableCell>
                <TableCell>Response</TableCell>
                <TableCell>Score</TableCell>
                <TableCell>Comment</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((i: any) => (
                <TableRow key={i.id}>
                  <TableCell>{i.clause_ref}</TableCell>
                  <TableCell>{i.question}</TableCell>
                  <TableCell>{i.response || '-'}</TableCell>
                  <TableCell>{i.score ?? '-'}</TableCell>
                  <TableCell>{i.comment || '-'}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => { setEditingItem(i); setEditItemOpen(true); }}><Edit /></IconButton>
                    <IconButton size="small" onClick={async () => { setItemForAttachments(i.id); const list = await auditsAPI.listItemAttachments(i.id); setItemAttachments(list); setItemAttachmentsOpen(true); }}><AttachFile /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      )}

      {tab === 2 && (
        <Box>
          <Stack direction="row" justifyContent="flex-end" sx={{ mb: 1 }}>
            <Button variant="contained" onClick={() => setAddFindingOpen(true)}>Add Finding</Button>
          </Stack>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Clause</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {findings.map((f: any) => (
                <TableRow key={f.id}>
                  <TableCell>{f.clause_ref}</TableCell>
                  <TableCell>{f.description}</TableCell>
                  <TableCell>{f.severity}</TableCell>
                  <TableCell>{f.status}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => { setEditingFinding(f); setEditFindingOpen(true); }}><Edit /></IconButton>
                    <IconButton size="small" onClick={async () => { setFindingForAttachments(f.id); const list = await auditsAPI.listFindingAttachments(f.id); setFindingAttachments(list); setFindingAttachmentsOpen(true); }}><AttachFile /></IconButton>
                    <IconButton size="small" onClick={async () => { const nc = await auditsAPI.createNCFromFinding(f.id); window.open(`/nonconformance/${nc.id}`, '_blank'); }}><Construction /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      )}

      {tab === 3 && (
        <Box>
          <Stack direction="row" justifyContent="flex-end" sx={{ mb: 1 }}>
            <Button variant="outlined" startIcon={<UploadFile />} component="label">
              Upload
              <input hidden type="file" onChange={async (e) => {
                const file = e.target.files?.[0]; if (!file) return;
                await auditsAPI.uploadAttachment(auditId, file);
                const att = await auditsAPI.listAttachments(auditId); setAttachments(att);
                e.currentTarget.value = '';
              }} />
            </Button>
          </Stack>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Filename</TableCell>
                <TableCell>Uploaded</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {attachments.map((att: any) => (
                <TableRow key={att.id}>
                  <TableCell>{att.filename}</TableCell>
                  <TableCell>{att.uploaded_at}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => window.open(`/api/v1/audits/attachments/${att.id}/download`, '_blank')}><AttachFile /></IconButton>
                    <IconButton size="small" color="error" onClick={async () => { if (!window.confirm('Delete attachment?')) return; await auditsAPI.deleteAttachment(att.id); const att2 = await auditsAPI.listAttachments(auditId); setAttachments(att2); }}><Delete /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      )}

      {tab === 4 && (
        <Box>
          <Stack direction="row" justifyContent="flex-end" sx={{ mb: 1 }}>
            <Button variant="contained" onClick={() => setAddAuditeeOpen(true)}>Add Auditee</Button>
          </Stack>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Added</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {auditees.map((x: any) => (
                <TableRow key={x.id}>
                  <TableCell>{x.user_id}</TableCell>
                  <TableCell>{x.role || '-'}</TableCell>
                  <TableCell>{x.added_at}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      )}

      {tab === 5 && (
        <Box>
          {plan?.approved_at && (
            <Alert severity="success" sx={{ mb: 2 }}>Plan approved at {new Date(plan.approved_at).toLocaleString()}</Alert>
          )}
          <Stack spacing={2} sx={{ mb: 2 }}>
            <TextField label="Agenda" multiline minRows={2} value={planForm.agenda} onChange={(e) => setPlanForm({ ...planForm, agenda: e.target.value })} />
            <TextField label="Criteria Refs" multiline minRows={2} value={planForm.criteria_refs} onChange={(e) => setPlanForm({ ...planForm, criteria_refs: e.target.value })} />
            <TextField label="Sampling Plan" multiline minRows={2} value={planForm.sampling_plan} onChange={(e) => setPlanForm({ ...planForm, sampling_plan: e.target.value })} />
            <TextField label="Documents to Review" multiline minRows={2} value={planForm.documents_to_review} onChange={(e) => setPlanForm({ ...planForm, documents_to_review: e.target.value })} />
            <TextField label="Logistics" multiline minRows={2} value={planForm.logistics} onChange={(e) => setPlanForm({ ...planForm, logistics: e.target.value })} />
          </Stack>
          <Stack direction="row" spacing={1}>
            <Button variant="contained" onClick={async () => { const p = await auditsAPI.savePlan(auditId, planForm); setPlan(p); }}>Save Plan</Button>
            <Button variant="outlined" onClick={async () => { const p = await auditsAPI.approvePlan(auditId); setPlan(p); }}>Approve Plan</Button>
          </Stack>
        </Box>
      )}

      <Dialog open={addAuditeeOpen} onClose={() => setAddAuditeeOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Auditee</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Autocomplete
              options={userOptions}
              open={userOpen}
              onOpen={() => setUserOpen(true)}
              onClose={() => setUserOpen(false)}
              getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
              value={userSelected}
              onChange={(_, val) => setUserSelected(val)}
              inputValue={userInput}
              onInputChange={(_, val) => setUserInput(val)}
              isOptionEqualToValue={(opt, val) => opt.id === val.id}
              renderInput={(params) => <TextField {...params} label="User" placeholder="Type at least 2 characters" fullWidth />}
            />
            <TextField label="Role" value={role} onChange={(e) => setRole(e.target.value)} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddAuditeeOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={addAuditee}>Add</Button>
        </DialogActions>
      </Dialog>

      {/* Add Checklist Item */}
      <Dialog open={addItemOpen} onClose={() => setAddItemOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Checklist Item</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Clause Ref" value={newItem.clause_ref} onChange={(e) => setNewItem({ ...newItem, clause_ref: e.target.value })} />
            <TextField label="Question" value={newItem.question} onChange={(e) => setNewItem({ ...newItem, question: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddItemOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            await auditsAPI.addChecklistItem(auditId, newItem);
            setAddItemOpen(false); setNewItem({ clause_ref: '', question: '' });
            const it = await auditsAPI.listChecklistItems(auditId); setItems(it);
          }}>Add</Button>
        </DialogActions>
      </Dialog>

      {/* Add Finding */}
      <Dialog open={addFindingOpen} onClose={() => setAddFindingOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Finding</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Clause Ref" value={newFinding.clause_ref} onChange={(e) => setNewFinding({ ...newFinding, clause_ref: e.target.value })} />
            <TextField label="Description" multiline rows={3} value={newFinding.description} onChange={(e) => setNewFinding({ ...newFinding, description: e.target.value })} />
            <FormControl fullWidth>
              <InputLabel>Severity</InputLabel>
              <Select label="Severity" value={newFinding.severity} onChange={(e) => setNewFinding({ ...newFinding, severity: e.target.value })}>
                <MenuItem value="minor">Minor</MenuItem>
                <MenuItem value="major">Major</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddFindingOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            await auditsAPI.addFinding(auditId, newFinding);
            setAddFindingOpen(false); setNewFinding({ clause_ref: '', description: '', severity: 'minor' });
            const fs = await auditsAPI.listFindings(auditId); setFindings(fs);
          }}>Add</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Checklist Item */}
      <Dialog open={editItemOpen} onClose={() => setEditItemOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Checklist Item</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Clause Ref" value={editingItem?.clause_ref || ''} onChange={(e) => setEditingItem({ ...editingItem, clause_ref: e.target.value })} />
            <TextField label="Question" value={editingItem?.question || ''} onChange={(e) => setEditingItem({ ...editingItem, question: e.target.value })} />
            <FormControl fullWidth>
              <InputLabel>Response</InputLabel>
              <Select label="Response" value={editingItem?.response || ''} onChange={(e) => setEditingItem({ ...editingItem, response: e.target.value })}>
                <MenuItem value="conforming">Conforming</MenuItem>
                <MenuItem value="nonconforming">Nonconforming</MenuItem>
                <MenuItem value="not_applicable">Not Applicable</MenuItem>
              </Select>
            </FormControl>
            <TextField label="Score" type="number" value={editingItem?.score ?? ''} onChange={(e) => setEditingItem({ ...editingItem, score: e.target.value === '' ? null : Number(e.target.value) })} />
            <TextField label="Comment" multiline rows={2} value={editingItem?.comment || ''} onChange={(e) => setEditingItem({ ...editingItem, comment: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditItemOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            if (!editingItem) return;
            const payload: any = { clause_ref: editingItem.clause_ref, question: editingItem.question, response: editingItem.response || null, score: editingItem.score, comment: editingItem.comment };
            await auditsAPI.updateChecklistItem(editingItem.id, payload);
            setEditItemOpen(false); setEditingItem(null);
            const it = await auditsAPI.listChecklistItems(auditId); setItems(it);
          }}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Item Attachments */}
      <Dialog open={itemAttachmentsOpen} onClose={() => setItemAttachmentsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Item Attachments</DialogTitle>
        <DialogContent>
          <Stack direction="row" justifyContent="flex-end" sx={{ mb: 1 }}>
            <Button variant="outlined" startIcon={<UploadFile />} component="label">
              Upload
              <input hidden type="file" onChange={async (e) => {
                const file = e.target.files?.[0]; if (!file || !itemForAttachments) return;
                await auditsAPI.uploadItemAttachment(itemForAttachments, file);
                const list = await auditsAPI.listItemAttachments(itemForAttachments); setItemAttachments(list);
                e.currentTarget.value = '';
              }} />
            </Button>
          </Stack>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Filename</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {itemAttachments.map((att: any) => (
                <TableRow key={att.id}>
                  <TableCell>{att.filename}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => window.open(`/api/v1/audits/checklist/attachments/${att.id}/download`, '_blank')}><AttachFile /></IconButton>
                    <IconButton size="small" color="error" onClick={async () => { if (!itemForAttachments) return; if (!window.confirm('Delete attachment?')) return; await auditsAPI.deleteItemAttachment(att.id); const list = await auditsAPI.listItemAttachments(itemForAttachments); setItemAttachments(list); }}><Delete /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setItemAttachmentsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Finding */}
      <Dialog open={editFindingOpen} onClose={() => setEditFindingOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Finding</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Clause Ref" value={editingFinding?.clause_ref || ''} onChange={(e) => setEditingFinding({ ...editingFinding, clause_ref: e.target.value })} />
            <TextField label="Description" multiline rows={3} value={editingFinding?.description || ''} onChange={(e) => setEditingFinding({ ...editingFinding, description: e.target.value })} />
            <FormControl fullWidth>
              <InputLabel>Severity</InputLabel>
              <Select label="Severity" value={editingFinding?.severity || ''} onChange={(e) => setEditingFinding({ ...editingFinding, severity: e.target.value })}>
                <MenuItem value="minor">Minor</MenuItem>
                <MenuItem value="major">Major</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select label="Status" value={editingFinding?.status || ''} onChange={(e) => setEditingFinding({ ...editingFinding, status: e.target.value })}>
                <MenuItem value="open">Open</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="verified">Verified</MenuItem>
                <MenuItem value="closed">Closed</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditFindingOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            if (!editingFinding) return;
            const payload: any = { clause_ref: editingFinding.clause_ref, description: editingFinding.description, severity: editingFinding.severity, status: editingFinding.status };
            await auditsAPI.updateFinding(editingFinding.id, payload);
            setEditFindingOpen(false); setEditingFinding(null);
            const fs = await auditsAPI.listFindings(auditId); setFindings(fs);
          }}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Finding Attachments */}
      <Dialog open={findingAttachmentsOpen} onClose={() => setFindingAttachmentsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Finding Attachments</DialogTitle>
        <DialogContent>
          <Stack direction="row" justifyContent="flex-end" sx={{ mb: 1 }}>
            <Button variant="outlined" startIcon={<UploadFile />} component="label">
              Upload
              <input hidden type="file" onChange={async (e) => {
                const file = e.target.files?.[0]; if (!file || !findingForAttachments) return;
                await auditsAPI.uploadFindingAttachment(findingForAttachments, file);
                const list = await auditsAPI.listFindingAttachments(findingForAttachments); setFindingAttachments(list);
                e.currentTarget.value = '';
              }} />
            </Button>
          </Stack>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Filename</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {findingAttachments.map((att: any) => (
                <TableRow key={att.id}>
                  <TableCell>{att.filename}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => window.open(`/api/v1/audits/findings/attachments/${att.id}/download`, '_blank')}><AttachFile /></IconButton>
                    <IconButton size="small" color="error" onClick={async () => { if (!findingForAttachments) return; if (!window.confirm('Delete attachment?')) return; await auditsAPI.deleteFindingAttachment(att.id); const list = await auditsAPI.listFindingAttachments(findingForAttachments); setFindingAttachments(list); }}><Delete /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFindingAttachmentsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AuditDetail;


