import React, { useEffect, useMemo, useState } from 'react';
import { Box, Tabs, Tab, Stack, Typography, Button, Card, CardContent, Table, TableHead, TableRow, TableCell, TableBody, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Select, MenuItem, InputLabel, FormControl, Chip } from '@mui/material';
import { allergenLabelAPI, haccpAPI, usersAPI } from '../services/api';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

const AllergenLabel: React.FC = () => {
  const [tab, setTab] = useState(0);
  const [assessments, setAssessments] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [openAssess, setOpenAssess] = useState(false);
  const [assessForm, setAssessForm] = useState<any>({ product_id: '', risk_level: 'low' });
  const [openTpl, setOpenTpl] = useState(false);
  const [tplForm, setTplForm] = useState<any>({ name: '', description: '', product_id: '' });
  const [openVersion, setOpenVersion] = useState(false);
  const [versionForm, setVersionForm] = useState<any>({ template_id: '', content: '', change_description: '', change_reason: '' });
  const [versions, setVersions] = useState<Record<number, any[]>>({});
  const [approvals, setApprovals] = useState<Record<number, any[]>>({});
  const [approvalsOpen, setApprovalsOpen] = useState(false);
  const [approvalsCtx, setApprovalsCtx] = useState<{ templateId: number; versionId: number; templateName: string; versionNum: number } | null>(null);
  const currentUser = useSelector((s: RootState) => s.auth.user);
  const [approvers, setApprovers] = useState<Array<{ approver_id: number; approval_order: number }>>([]);

  const load = async () => {
    const [ass, prods, us, tpls] = await Promise.all([
      allergenLabelAPI.listAssessments(),
      haccpAPI.getProducts(),
      usersAPI.getUsers({ page: 1, size: 100 }),
      allergenLabelAPI.listTemplates(true),
    ]);
    setAssessments(ass?.data || ass?.items || ass || []);
    const items = prods?.data?.items || prods?.items || [];
    setProducts(items);
    setUsers((us?.data?.items || us?.items || []).map((u: any) => ({ id: u.id, label: u.full_name ? `${u.full_name} (${u.username})` : u.username })));
    const tplItems = tpls?.data || tpls || [];
    setTemplates(tplItems);
    // Preload versions per template for quick UI
    const vmap: Record<number, any[]> = {};
    for (const t of tplItems) {
      try { vmap[t.id] = await allergenLabelAPI.listTemplateVersions(t.id); } catch { vmap[t.id] = []; }
    }
    setVersions(vmap);
  };

  useEffect(() => { load(); }, []);

  const productName = (id?: number) => products.find((p: any) => p.id === id)?.name || '-';

  return (
    <Box>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
        <Typography variant="h5">Allergen & Label Control</Typography>
        <Stack direction="row" spacing={1}>
          {tab === 0 && <Button variant="contained" onClick={() => setOpenAssess(true)}>New Assessment</Button>}
          {tab === 1 && <>
            <Button variant="outlined" onClick={() => setOpenTpl(true)}>New Label Template</Button>
            <Button variant="contained" onClick={() => setOpenVersion(true)}>New Version</Button>
          </>}
        </Stack>
      </Stack>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Allergen Assessments" />
        <Tab label="Label Templates" />
      </Tabs>

      {tab === 0 && (
        <Card variant="outlined">
          <CardContent>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Product</TableCell>
                  <TableCell>Risk Level</TableCell>
                  <TableCell>Precautionary Labeling</TableCell>
                  <TableCell>Reviewed By</TableCell>
                  <TableCell>Updated</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {assessments.map((a: any) => (
                  <TableRow key={a.id}>
                    <TableCell>{productName(a.product_id)}</TableCell>
                    <TableCell sx={{ textTransform: 'capitalize' }}>{a.risk_level}</TableCell>
                    <TableCell>{a.precautionary_labeling || '-'}</TableCell>
                    <TableCell>{users.find(u => u.id === a.reviewed_by)?.label || '-'}</TableCell>
                    <TableCell>{(a.updated_at || a.created_at || '').toString().slice(0, 19).replace('T',' ')}</TableCell>
                  </TableRow>
                ))}
                {assessments.length === 0 && (
                  <TableRow><TableCell colSpan={5}><Typography variant="body2" color="text.secondary">No assessments yet.</Typography></TableCell></TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {tab === 1 && (
        <Card variant="outlined">
          <CardContent>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Product</TableCell>
                  <TableCell>Active</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Versions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {templates.map((t: any) => (
                  <TableRow key={t.id}>
                    <TableCell>{t.name}</TableCell>
                    <TableCell>{productName(t.product_id)}</TableCell>
                    <TableCell>{t.is_active ? 'Yes' : 'No'}</TableCell>
                    <TableCell>{(t.created_at || '').toString().slice(0,10)}</TableCell>
                    <TableCell>
                      <Stack spacing={0.5}>
                        {(versions[t.id] || []).map((v: any) => (
                          <Stack key={v.id} direction="row" alignItems="center" justifyContent="space-between">
                            <Typography variant="caption">v{v.version_number} • {v.status}</Typography>
                            <Stack direction="row" spacing={1}>
                              <Button size="small" onClick={async () => {
                                try { const blob = await allergenLabelAPI.exportVersionPDF(t.id, v.id); const url = window.URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `label_${t.id}_v${v.version_number}.pdf`; a.click(); window.URL.revokeObjectURL(url); } catch {}
                              }}>PDF</Button>
                              <Button size="small" variant="outlined" onClick={async () => {
                                try {
                                  const aps = await allergenLabelAPI.listVersionApprovals(t.id, v.id);
                                  setApprovals(prev => ({ ...prev, [v.id]: aps }));
                                  setApprovalsCtx({ templateId: t.id, versionId: v.id, templateName: t.name, versionNum: v.version_number });
                                  setApprovalsOpen(true);
                                } catch {}
                              }}>Approvals</Button>
                            </Stack>
                          </Stack>
                        ))}
                        {(versions[t.id] || []).length === 0 && <Typography variant="caption" color="text.secondary">No versions</Typography>}
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))}
                {templates.length === 0 && (
                  <TableRow><TableCell colSpan={4}><Typography variant="body2" color="text.secondary">No templates yet.</Typography></TableCell></TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Approvals Dialog */}
      <Dialog open={approvalsOpen} onClose={() => setApprovalsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Approvals{approvalsCtx ? ` • ${approvalsCtx.templateName} v${approvalsCtx.versionNum}` : ''}</DialogTitle>
        <DialogContent>
          <Stack spacing={1} sx={{ mt: 1 }}>
            {(approvalsCtx && approvals[approvalsCtx.versionId] ? approvals[approvalsCtx.versionId] : []).map((a: any) => (
              <Stack key={a.id} direction="row" alignItems="center" justifyContent="space-between">
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography variant="body2">Approver #{a.approver_id}</Typography>
                  <Chip size="small" label={a.status} color={a.status === 'approved' ? 'success' : a.status === 'rejected' ? 'error' : 'default'} />
                </Stack>
                {approvalsCtx && currentUser && a.approver_id === currentUser.id && a.status === 'pending' && (
                  <Stack direction="row" spacing={1}>
                    <Button size="small" variant="contained" onClick={async () => {
                      if (!approvalsCtx) return;
                      await allergenLabelAPI.approveTemplate(approvalsCtx.templateId, a.id);
                      const aps = await allergenLabelAPI.listVersionApprovals(approvalsCtx.templateId, approvalsCtx.versionId);
                      setApprovals(prev => ({ ...prev, [approvalsCtx.versionId]: aps }));
                      // refresh versions list to reflect status change
                      const vlist = await allergenLabelAPI.listTemplateVersions(approvalsCtx.templateId);
                      setVersions(prev => ({ ...prev, [approvalsCtx.templateId]: vlist }));
                    }}>Approve</Button>
                    <Button size="small" color="error" variant="outlined" onClick={async () => {
                      if (!approvalsCtx) return;
                      await allergenLabelAPI.rejectTemplate(approvalsCtx.templateId, a.id);
                      const aps = await allergenLabelAPI.listVersionApprovals(approvalsCtx.templateId, approvalsCtx.versionId);
                      setApprovals(prev => ({ ...prev, [approvalsCtx.versionId]: aps }));
                      const vlist = await allergenLabelAPI.listTemplateVersions(approvalsCtx.templateId);
                      setVersions(prev => ({ ...prev, [approvalsCtx.templateId]: vlist }));
                    }}>Reject</Button>
                  </Stack>
                )}
              </Stack>
            ))}
            {approvalsCtx && (!approvals[approvalsCtx.versionId] || approvals[approvalsCtx.versionId].length === 0) && (
              <Typography variant="body2" color="text.secondary">No approvals defined for this version.</Typography>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApprovalsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Create Assessment */}
      <Dialog open={openAssess} onClose={() => setOpenAssess(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Allergen Assessment</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Product</InputLabel>
              <Select label="Product" value={assessForm.product_id} onChange={(e) => setAssessForm({ ...assessForm, product_id: Number(e.target.value) })}>
                {products.map((p: any) => (<MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Risk Level</InputLabel>
              <Select label="Risk Level" value={assessForm.risk_level} onChange={(e) => setAssessForm({ ...assessForm, risk_level: e.target.value })}>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
            <TextField label="Precautionary Labeling" value={assessForm.precautionary_labeling || ''} onChange={(e) => setAssessForm({ ...assessForm, precautionary_labeling: e.target.value })} fullWidth />
            <TextField label="Control Measures" value={assessForm.control_measures || ''} onChange={(e) => setAssessForm({ ...assessForm, control_measures: e.target.value })} fullWidth multiline minRows={2} />
            <TextField label="Validation/Verification" value={assessForm.validation_verification || ''} onChange={(e) => setAssessForm({ ...assessForm, validation_verification: e.target.value })} fullWidth multiline minRows={2} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAssess(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => { await allergenLabelAPI.createAssessment({ ...assessForm, product_id: Number(assessForm.product_id) }); setOpenAssess(false); setAssessForm({ product_id: '', risk_level: 'low' }); const a = await allergenLabelAPI.listAssessments(); setAssessments(a?.data || a?.items || a || []); }}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* Create Template */}
      <Dialog open={openTpl} onClose={() => setOpenTpl(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Label Template</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Name" value={tplForm.name} onChange={(e) => setTplForm({ ...tplForm, name: e.target.value })} fullWidth />
            <TextField label="Description" value={tplForm.description} onChange={(e) => setTplForm({ ...tplForm, description: e.target.value })} fullWidth />
            <FormControl fullWidth>
              <InputLabel>Product (optional)</InputLabel>
              <Select label="Product (optional)" value={tplForm.product_id} onChange={(e) => setTplForm({ ...tplForm, product_id: e.target.value })}>
                <MenuItem value="">None</MenuItem>
                {products.map((p: any) => (<MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>))}
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenTpl(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => { await allergenLabelAPI.createTemplate({ ...tplForm, product_id: tplForm.product_id ? Number(tplForm.product_id) : null }); setOpenTpl(false); setTplForm({ name: '', description: '', product_id: '' }); const t = await allergenLabelAPI.listTemplates(true); setTemplates(t?.data || t || []); }}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* New Version */}
      <Dialog open={openVersion} onClose={() => setOpenVersion(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Label Version</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Template</InputLabel>
              <Select label="Template" value={versionForm.template_id} onChange={(e) => setVersionForm({ ...versionForm, template_id: Number(e.target.value) })}>
                {templates.map((t: any) => (<MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>))}
              </Select>
            </FormControl>
            <TextField label="Change Description" value={versionForm.change_description} onChange={(e) => setVersionForm({ ...versionForm, change_description: e.target.value })} fullWidth />
            <TextField label="Change Reason" value={versionForm.change_reason} onChange={(e) => setVersionForm({ ...versionForm, change_reason: e.target.value })} fullWidth />
            <TextField label="Content (JSON or Text)" value={versionForm.content} onChange={(e) => setVersionForm({ ...versionForm, content: e.target.value })} fullWidth multiline minRows={4} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenVersion(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => { if (!versionForm.template_id) return; await allergenLabelAPI.createTemplateVersion(Number(versionForm.template_id), { content: versionForm.content, change_description: versionForm.change_description, change_reason: versionForm.change_reason }); setOpenVersion(false); setVersionForm({ template_id: '', content: '', change_description: '', change_reason: '' }); }}>Create Version</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AllergenLabel;


