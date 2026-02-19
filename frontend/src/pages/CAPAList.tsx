import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Typography, Paper, TextField, MenuItem, Button, Table, TableHead, TableRow, TableCell, TableBody, Pagination, Stack } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { AppDispatch, RootState } from '../store';
import { fetchCAPAList } from '../store/slices/ncSlice';

const CAPAList: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { capaList } = useSelector((s: RootState) => s.nc);
  const [status, setStatus] = useState('');
  const [responsible, setResponsible] = useState('');

  useEffect(() => {
    dispatch(fetchCAPAList({ page: 1, size: 20 }));
  }, [dispatch]);

  const onFilter = () => {
    dispatch(fetchCAPAList({ page: 1, size: capaList.size, status: status || undefined, responsible_person: responsible || undefined }));
  };

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight="bold" gutterBottom>CAPA Actions</Typography>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField label="Status" size="small" select value={status} onChange={e => setStatus(e.target.value)} sx={{ minWidth: 180 }}>
            <MenuItem value="">All</MenuItem>
            {['pending','assigned','in_progress','completed','verified','closed','overdue'].map(s => (<MenuItem key={s} value={s}>{s.split('_').join(' ')}</MenuItem>))}
          </TextField>
          <TextField label="Responsible (user id)" size="small" value={responsible} onChange={e => setResponsible(e.target.value)} />
          <Button variant="contained" onClick={onFilter}>Apply</Button>
        </Stack>
      </Paper>

      <Paper>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>CAPA #</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Responsible</TableCell>
              <TableCell>Target</TableCell>
              <TableCell>Progress</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {capaList.items.map((c: any) => (
              <TableRow key={c.id} hover sx={{ cursor: 'pointer' }} onClick={() => navigate(`/nonconformance/capas/${c.id}`)}>
                <TableCell>{c.capa_number}</TableCell>
                <TableCell>{c.title}</TableCell>
                <TableCell sx={{ textTransform: 'capitalize' }}>{String(c.status).split('_').join(' ')}</TableCell>
                <TableCell>{c.responsible_person}</TableCell>
                <TableCell>{c.target_completion_date}</TableCell>
                <TableCell>{c.progress_percentage}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <Box p={2} display="flex" justifyContent="flex-end">
          <Pagination page={capaList.page} count={capaList.pages} onChange={(_, p) => dispatch(fetchCAPAList({ page: p, size: capaList.size }))} />
        </Box>
      </Paper>
    </Box>
  );
};

export default CAPAList;

