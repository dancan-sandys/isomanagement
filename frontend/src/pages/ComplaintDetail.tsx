import React, { useEffect, useState } from 'react';
import { Box, Stack, Typography, Paper, Divider, Chip, TextField, Button, MenuItem, Select, Table, TableHead, TableRow, TableCell, TableBody } from '@mui/material';
import { complaintsAPI } from '../services/api';
import { useParams } from 'react-router-dom';

const ComplaintDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const complaintId = Number(id);
  const [complaint, setComplaint] = useState<any>(null);
  const [communications, setCommunications] = useState<any[]>([]);
  const [investigation, setInvestigation] = useState<any | null>(null);
  const [statusUpdate, setStatusUpdate] = useState<string>('');
  const [newComm, setNewComm] = useState({ channel: 'email', sender: '', recipient: '', message: '' });
  const [invForm, setInvForm] = useState({ investigator_id: '', summary: '', root_cause_analysis_id: '', outcome: '' });

  const load = async () => {
    const comp = await complaintsAPI.get(complaintId);
    setComplaint(comp?.data || comp);
    const comms = await complaintsAPI.listCommunications(complaintId);
    setCommunications(comms?.data || comms || []);
    try {
      const inv = await complaintsAPI.getInvestigation(complaintId);
      setInvestigation(inv?.data || inv || null);
    } catch {}
  };

  useEffect(() => { if (complaintId) load(); }, [complaintId]);

  return (
    <Box p={3}>
      {complaint && (
        <Paper sx={{ p: 2 }}>
          <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', md: 'center' }}>
            <Box>
              <Typography variant="h6" fontWeight="bold">Complaint {complaint.complaint_number}</Typography>
              <Typography variant="body2" color="text.secondary">{complaint.customer_name} • {new Date(complaint.complaint_date).toLocaleString()}</Typography>
            </Box>
            <Chip label={complaint.status} color="warning" />
          </Stack>

          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1">Details</Typography>
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{complaint.description}</Typography>
          <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
            <Chip label={`Class: ${complaint.classification}`} />
            <Chip label={`Severity: ${complaint.severity}`} />
            {complaint.batch_id && <Chip label={`Batch: ${complaint.batch_id}`} />}
            {complaint.non_conformance_id && <Chip label={`NC: ${complaint.non_conformance_id}`} onClick={() => (window.location.href = `/nonconformance/${complaint.non_conformance_id}`)} />}
          </Stack>

          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ mt: 2 }}>
            <Select value={statusUpdate || complaint.status} onChange={e => setStatusUpdate(e.target.value as string)} size="small">
              <MenuItem value="open">Open</MenuItem>
              <MenuItem value="under_investigation">Under Investigation</MenuItem>
              <MenuItem value="resolved">Resolved</MenuItem>
              <MenuItem value="closed">Closed</MenuItem>
            </Select>
            <Button variant="contained" onClick={async () => {
              await complaintsAPI.update(complaintId, { status: statusUpdate || complaint.status });
              load();
            }}>Update Status</Button>
          </Stack>
        </Paper>
      )}

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ mt: 3 }}>
        <Paper sx={{ p: 2, flex: 1 }}>
          <Typography variant="subtitle1" fontWeight="bold">Communication History</Typography>
          <Table size="small" sx={{ mt: 1 }}>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Channel</TableCell>
                <TableCell>From</TableCell>
                <TableCell>To</TableCell>
                <TableCell>Message</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {communications.map((m) => (
                <TableRow key={m.id}>
                  <TableCell>{new Date(m.communication_date).toLocaleString()}</TableCell>
                  <TableCell>{m.channel}</TableCell>
                  <TableCell>{m.sender || '-'}</TableCell>
                  <TableCell>{m.recipient || '-'}</TableCell>
                  <TableCell>{m.message}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1} sx={{ mt: 2 }}>
            <Select size="small" value={newComm.channel} onChange={e => setNewComm({ ...newComm, channel: e.target.value as string })}>
              <MenuItem value="email">Email</MenuItem>
              <MenuItem value="phone">Phone</MenuItem>
              <MenuItem value="meeting">Meeting</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
            <TextField size="small" label="From" value={newComm.sender} onChange={e => setNewComm({ ...newComm, sender: e.target.value })} />
            <TextField size="small" label="To" value={newComm.recipient} onChange={e => setNewComm({ ...newComm, recipient: e.target.value })} />
            <TextField size="small" fullWidth label="Message" value={newComm.message} onChange={e => setNewComm({ ...newComm, message: e.target.value })} />
            <Button variant="contained" onClick={async () => { await complaintsAPI.addCommunication(complaintId, newComm as any); setNewComm({ channel: 'email', sender: '', recipient: '', message: '' }); load(); }}>Send</Button>
          </Stack>
        </Paper>

        <Paper sx={{ p: 2, flex: 1 }}>
          <Typography variant="subtitle1" fontWeight="bold">Investigation</Typography>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField size="small" label="Investigator ID" value={invForm.investigator_id} onChange={e => setInvForm({ ...invForm, investigator_id: e.target.value })} />
            <TextField size="small" label="Summary" multiline rows={3} value={invForm.summary} onChange={e => setInvForm({ ...invForm, summary: e.target.value })} />
            <TextField size="small" label="RCA ID (optional)" value={invForm.root_cause_analysis_id} onChange={e => setInvForm({ ...invForm, root_cause_analysis_id: e.target.value })} />
            <TextField size="small" label="Outcome" multiline rows={3} value={invForm.outcome} onChange={e => setInvForm({ ...invForm, outcome: e.target.value })} />
            <Stack direction="row" spacing={1}>
              <Button variant="outlined" onClick={async () => { await complaintsAPI.createInvestigation(complaintId, { investigator_id: invForm.investigator_id ? Number(invForm.investigator_id) : undefined, summary: invForm.summary || undefined }); load(); }}>Start Investigation</Button>
              <Button variant="contained" onClick={async () => { await complaintsAPI.updateInvestigation(complaintId, { investigator_id: invForm.investigator_id ? Number(invForm.investigator_id) : undefined, root_cause_analysis_id: invForm.root_cause_analysis_id ? Number(invForm.root_cause_analysis_id) : undefined, summary: invForm.summary || undefined, outcome: invForm.outcome || undefined }); load(); }}>Update Investigation</Button>
            </Stack>
          </Stack>
        </Paper>
      </Stack>
    </Box>
  );
};

export default ComplaintDetailPage;


