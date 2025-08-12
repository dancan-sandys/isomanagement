import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Stack, Table, TableHead, TableRow, TableCell, TableBody, Button } from '@mui/material';
import { trainingAPI } from '../services/api';

const TrainingMatrix: React.FC = () => {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const data = await trainingAPI.getMyTrainingMatrix();
        setRows(data || []);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const exportCSV = () => {
    const header = ['Program Code', 'Program Title', 'Completed', 'In Progress', 'Last Attended', 'Last Certificate', 'Last Quiz %', 'Last Quiz Passed'];
    const lines = rows.map(r => [r.program_code, r.program_title, String(r.completed), String(r.in_progress), r.last_attended_at || '', r.last_certificate_issued_at || '', r.last_quiz_score ?? '', r.last_quiz_passed ?? ''].join(','));
    const csv = [header.join(','), ...lines].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'training_matrix.csv'; a.click(); window.URL.revokeObjectURL(url);
  };

  return (
    <Box p={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h5" fontWeight="bold">My Training Matrix</Typography>
        <Button onClick={exportCSV} variant="outlined">Export CSV</Button>
      </Stack>
      <Paper>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Program Code</TableCell>
              <TableCell>Program Title</TableCell>
              <TableCell>Completed</TableCell>
              <TableCell>In Progress</TableCell>
              <TableCell>Last Attended</TableCell>
              <TableCell>Last Certificate</TableCell>
              <TableCell>Last Quiz %</TableCell>
              <TableCell>Last Quiz Passed</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((r: any) => (
              <TableRow key={r.program_id}>
                <TableCell>{r.program_code}</TableCell>
                <TableCell>{r.program_title}</TableCell>
                <TableCell>{String(r.completed)}</TableCell>
                <TableCell>{String(r.in_progress)}</TableCell>
                <TableCell>{r.last_attended_at || '-'}</TableCell>
                <TableCell>{r.last_certificate_issued_at || '-'}</TableCell>
                <TableCell>{typeof r.last_quiz_score === 'number' ? r.last_quiz_score.toFixed(1) : '-'}</TableCell>
                <TableCell>{r.last_quiz_passed === null || r.last_quiz_passed === undefined ? '-' : String(r.last_quiz_passed)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
};

export default TrainingMatrix;


