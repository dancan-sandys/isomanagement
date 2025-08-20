import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Typography, Paper, TextField, MenuItem, Button, Table, TableHead, TableRow, TableCell, TableBody, Pagination, Stack, Dialog, DialogTitle, DialogContent } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { ncAPI } from '../services/api';
import { AppDispatch, RootState } from '../store';
import { fetchNonConformances } from '../store/slices/ncSlice';

const NonConformance: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { list } = useSelector((s: RootState) => s.nc);
  const navigate = useNavigate();
  const [openCreate, setOpenCreate] = useState(false);
  const [createPayload, setCreatePayload] = useState({ title: '', description: '', source: 'OTHER', severity: 'medium' });
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [source, setSource] = useState('');
  const [severity, setSeverity] = useState('');

  useEffect(() => {
    dispatch(fetchNonConformances({ page: 1, size: 20 }));
  }, [dispatch]);

  const onFilter = () => {
    dispatch(fetchNonConformances({ page: 1, size: list.size, search: search || undefined, status: status || undefined, source: source || undefined, severity: severity || undefined }));
  };

  return (
    <Box p={3}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h5" fontWeight="bold">Non-Conformances</Typography>
        <Button variant="contained" onClick={() => setOpenCreate(true)}>Log New NC</Button>
      </Stack>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField label="Search" size="small" value={search} onChange={e => setSearch(e.target.value)} />
          <TextField label="Status" size="small" select value={status} onChange={e => setStatus(e.target.value)} sx={{ minWidth: 180 }}>
            <MenuItem value="">All</MenuItem>
            {['OPEN','UNDER_INVESTIGATION','ROOT_CAUSE_IDENTIFIED','CAPA_ASSIGNED','IN_PROGRESS','COMPLETED','VERIFIED','CLOSED'].map(s => (<MenuItem key={s} value={s}>{s.split('_').join(' ')}</MenuItem>))}
          </TextField>
          <TextField label="Source" size="small" select value={source} onChange={e => setSource(e.target.value)} sx={{ minWidth: 180 }}>
            <MenuItem value="">All</MenuItem>
            {['PRP','HACCP','SUPPLIER','AUDIT','DOCUMENT','PRODUCTION_DEVIATION','COMPLAINT','OTHER'].map(s => (<MenuItem key={s} value={s}>{s.split('_').join(' ')}</MenuItem>))}
          </TextField>
          <TextField label="Severity" size="small" select value={severity} onChange={e => setSeverity(e.target.value)} sx={{ minWidth: 180 }}>
            <MenuItem value="">All</MenuItem>
            {['low','medium','high','critical'].map(s => (<MenuItem key={s} value={s}>{s}</MenuItem>))}
          </TextField>
          <Button variant="contained" onClick={onFilter}>Apply</Button>
        </Stack>
      </Paper>

      <Paper>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>NC Number</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Source</TableCell>
              <TableCell>Reported</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(list.items || []).map((nc: any) => (
              <TableRow key={nc.id} hover sx={{ cursor: 'pointer' }} onClick={() => navigate(`/nonconformance/${nc.id}`)}>
                <TableCell>{nc.nc_number}</TableCell>
                <TableCell>{nc.title}</TableCell>
                <TableCell sx={{ textTransform: 'capitalize' }}>{String(nc.status).split('_').join(' ')}</TableCell>
                <TableCell>{nc.severity}</TableCell>
                <TableCell sx={{ textTransform: 'uppercase' }}>{nc.source}</TableCell>
                <TableCell>{nc.reported_date ? new Date(nc.reported_date).toLocaleString() : ''}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <Box p={2} display="flex" justifyContent="flex-end">
          <Pagination page={list.page} count={list.pages} onChange={(_, p) => dispatch(fetchNonConformances({ page: p, size: list.size }))} />
        </Box>
      </Paper>

      {/* Create NC Modal */}
      <Dialog open={openCreate} onClose={() => setOpenCreate(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Log Non-Conformance</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Title" value={createPayload.title} onChange={e => setCreatePayload({ ...createPayload, title: e.target.value })} />
            <TextField label="Description" multiline minRows={3} value={createPayload.description} onChange={e => setCreatePayload({ ...createPayload, description: e.target.value })} />
            <TextField select label="Source" value={createPayload.source} onChange={e => setCreatePayload({ ...createPayload, source: e.target.value })}>
              {['PRP','HACCP','SUPPLIER','AUDIT','DOCUMENT','PRODUCTION_DEVIATION','COMPLAINT','OTHER'].map(s => (<MenuItem key={s} value={s}>{s.split('_').join(' ')}</MenuItem>))}
            </TextField>
            <TextField select label="Severity" value={createPayload.severity} onChange={e => setCreatePayload({ ...createPayload, severity: e.target.value })}>
              {['low','medium','high','critical'].map(s => (<MenuItem key={s} value={s}>{s}</MenuItem>))}
            </TextField>
            <Stack direction="row" spacing={2}>
              <Button variant="outlined" onClick={() => setOpenCreate(false)}>Cancel</Button>
              <Button variant="contained" onClick={async () => {
                const res = await ncAPI.createNonConformance(createPayload);
                setOpenCreate(false);
                dispatch(fetchNonConformances({ page: 1, size: list.size }));
                if (res?.data?.id) navigate(`/nonconformance/${res.data.id}`);
              }}>Create</Button>
            </Stack>
          </Stack>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default NonConformance;

