import React, { useEffect, useState } from 'react';
import { Box, Stack, Typography, Paper, Divider, Chip, TextField, Button, MenuItem, Select, Table, TableHead, TableRow, TableCell, TableBody, Autocomplete } from '@mui/material';
import { complaintsAPI, ncAPI } from '../services/api';
import { useParams } from 'react-router-dom';

const ComplaintDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const complaintId = Number(id);
  const [complaint, setComplaint] = useState<any>(null);
  const [communications, setCommunications] = useState<any[]>([]);
  const [investigation, setInvestigation] = useState<any | null>(null);
  const [statusUpdate, setStatusUpdate] = useState<string>('');
  const [newComm, setNewComm] = useState({ channel: 'email', sender: '', recipient: '', message: '' });
  const [invForm, setInvForm] = useState({ investigator_id: '', summary: '', root_cause_analysis_id: '', capa_action_id: '', outcome: '' });
  const [capaOptions, setCapaOptions] = useState<any[]>([]);

  const load = async () => {
    const comp = await complaintsAPI.get(complaintId);
    setComplaint(comp?.data || comp);
    const comms = await complaintsAPI.listCommunications(complaintId);
    setCommunications(comms?.data || comms || []);
    try {
      const inv = await complaintsAPI.getInvestigation(complaintId);
      const investigationData = inv?.data || inv || null;
      setInvestigation(investigationData);
      
      // Populate form with existing investigation data if available
      if (investigationData) {
        setInvForm({
          investigator_id: investigationData.investigator_id?.toString() || '',
          summary: investigationData.summary || '',
          root_cause_analysis_id: investigationData.root_cause_analysis_id?.toString() || '',
          capa_action_id: investigationData.capa_action_id?.toString() || '',
          outcome: investigationData.outcome || ''
        });
      }
    } catch (error) {
      console.error('Error loading investigation:', error);
    }

    // Load CAPAs for linked NC if available
    try {
      const ncId = (comp?.data || comp)?.non_conformance_id || comp?.non_conformance_id;
      if (ncId) {
        const capasRes = await ncAPI.getCAPAList({ non_conformance_id: Number(ncId), page: 1, size: 50 });
        const items = capasRes?.data?.items || capasRes?.items || [];
        setCapaOptions(items);
      } else {
        setCapaOptions([]);
      }
    } catch (e) {
      setCapaOptions([]);
    }
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
            <Button variant="contained" onClick={async () => { await complaintsAPI.addCommunication(complaintId, newComm as any); setNewComm({ channel: 'email', sender: '', recipient: '', message: '' }); load(); }}>Add</Button>
          </Stack>
        </Paper>

        <Paper sx={{ p: 2, flex: 1 }}>
          <Typography variant="subtitle1" fontWeight="bold">Investigation</Typography>
          
          {/* Display current investigation if exists */}
          {investigation && (
            <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="primary" gutterBottom>Current Investigation</Typography>
              {investigation.investigator_id && (
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Investigator ID:</strong> {investigation.investigator_id}
                </Typography>
              )}
              {investigation.summary && (
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Summary:</strong> {investigation.summary}
                </Typography>
              )}
              {investigation.root_cause_analysis_id && (
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>RCA ID:</strong> {investigation.root_cause_analysis_id}
                </Typography>
              )}
              {investigation.outcome && (
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Outcome:</strong> {investigation.outcome}
                </Typography>
              )}
              {investigation.start_date && (
                <Typography variant="body2" color="text.secondary">
                  <strong>Started:</strong> {new Date(investigation.start_date).toLocaleString()}
                </Typography>
              )}
            </Box>
          )}
          
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField 
              size="small" 
              label="Investigator ID" 
              value={invForm.investigator_id} 
              onChange={e => setInvForm({ ...invForm, investigator_id: e.target.value })}
              placeholder="Enter investigator ID"
            />
            <TextField 
              size="small" 
              label="Summary" 
              multiline 
              rows={3} 
              value={invForm.summary} 
              onChange={e => setInvForm({ ...invForm, summary: e.target.value })}
              placeholder="Enter investigation summary"
            />
            <TextField 
              size="small" 
              label="RCA ID (optional)" 
              value={invForm.root_cause_analysis_id} 
              onChange={e => setInvForm({ ...invForm, root_cause_analysis_id: e.target.value })}
              placeholder="Enter root cause analysis ID"
            />
            {complaint?.non_conformance_id && (
              <Autocomplete
                options={capaOptions}
                getOptionLabel={(o: any) => (o?.capa_number ? `${o.capa_number} — ${o.title}` : String(o))}
                value={
                  (capaOptions || []).find((o: any) => String(o.id) === String(invForm.capa_action_id)) || null
                }
                onChange={(_, value: any) => setInvForm({ ...invForm, capa_action_id: value?.id ? String(value.id) : '' })}
                renderInput={(params) => (
                  <TextField {...params} size="small" label="Link CAPA (optional)" placeholder="Select CAPA to link" />
                )}
              />
            )}
            <TextField 
              size="small" 
              label="Outcome" 
              multiline 
              rows={3} 
              value={invForm.outcome} 
              onChange={e => setInvForm({ ...invForm, outcome: e.target.value })}
              placeholder="Enter investigation outcome"
            />
            <Stack direction="row" spacing={1}>
              <Button 
                variant="outlined" 
                onClick={async () => { 
                  try {
                    await complaintsAPI.createInvestigation(complaintId, { 
                      investigator_id: invForm.investigator_id ? Number(invForm.investigator_id) : undefined, 
                      summary: invForm.summary || undefined 
                    }); 
                    load(); 
                    setInvForm({ investigator_id: '', summary: '', root_cause_analysis_id: '', outcome: '' });
                  } catch (error) {
                    console.error('Error creating investigation:', error);
                  }
                }}
              >
                Start Investigation
              </Button>
              <Button 
                variant="contained" 
                onClick={async () => { 
                  try {
                    await complaintsAPI.updateInvestigation(complaintId, { 
                      investigator_id: invForm.investigator_id ? Number(invForm.investigator_id) : undefined, 
                      root_cause_analysis_id: invForm.root_cause_analysis_id ? Number(invForm.root_cause_analysis_id) : undefined, 
                      capa_action_id: invForm.capa_action_id ? Number(invForm.capa_action_id) : undefined,
                      summary: invForm.summary || undefined, 
                      outcome: invForm.outcome || undefined 
                    }); 
                    load(); 
                    setInvForm({ investigator_id: '', summary: '', root_cause_analysis_id: '', capa_action_id: '', outcome: '' });
                  } catch (error) {
                    console.error('Error updating investigation:', error);
                  }
                }}
              >
                Update Investigation
              </Button>
            </Stack>
          </Stack>
        </Paper>
      </Stack>
    </Box>
  );
};

export default ComplaintDetailPage;


