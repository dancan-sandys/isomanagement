import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import { prpAPI } from '../services/api';

const PRPProgramDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const programId = Number(id);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [program, setProgram] = useState<any>(null);
  const [checklists, setChecklists] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [programResp, checklistsResp] = await Promise.all([
          prpAPI.getProgram(programId),
          prpAPI.getChecklists(programId, { page: 1, size: 50 }),
        ]);
        setProgram(programResp?.data || programResp);
        setChecklists(checklistsResp?.data?.items || []);
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load program');
      } finally {
        setLoading(false);
      }
    };
    if (!Number.isNaN(programId)) load();
  }, [programId]);

  const getStatusColor = (status?: string) => {
    switch (String(status || '').toLowerCase()) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'suspended': return 'warning';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={360}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!program) return null;

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            {program.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Program Code: {program.program_code}
          </Typography>
        </Box>
        <Button variant="outlined" onClick={() => navigate('/prp?tab=programs')}>Back to Programs</Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>ISO Program Overview</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Category</Typography>
                  <Chip label={String(program.category || '').replace(/_/g,' ').toUpperCase()} size="small" />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Chip label={String(program.status || '').toUpperCase()} color={getStatusColor(program.status) as any} size="small" />
                </Grid>
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Objective</Typography>
                  <Typography variant="body1">{program.objective || '—'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Scope</Typography>
                  <Typography variant="body1">{program.scope || '—'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Responsible Department</Typography>
                  <Typography variant="body1">{program.responsible_department || '—'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Responsible Person</Typography>
                  <Typography variant="body1">{program.responsible_person || '—'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">SOP Reference</Typography>
                  <Typography variant="body1">{program.sop_reference || '—'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Monitoring / Verification</Typography>
                  <Typography variant="body1">
                    {(program.monitoring_frequency || '—') + ' / ' + (program.verification_frequency || '—')}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Acceptance Criteria</Typography>
                  <Typography variant="body1">{program.acceptance_criteria || '—'}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          <Box mt={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Program Checklists</Typography>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Checklist</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Scheduled</TableCell>
                        <TableCell>Due</TableCell>
                        <TableCell>Compliance</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {checklists.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={5} align="center">No checklists</TableCell>
                        </TableRow>
                      ) : (
                        checklists.map((c) => (
                          <TableRow key={c.id} hover>
                            <TableCell>
                              <Typography variant="body2" fontWeight="medium">{c.checklist_code}</Typography>
                              <Typography variant="body1" fontWeight="bold">{c.name}</Typography>
                            </TableCell>
                            <TableCell>
                              <Chip label={String(c.status || '').toUpperCase()} size="small" />
                            </TableCell>
                            <TableCell>{new Date(c.scheduled_date).toLocaleDateString()}</TableCell>
                            <TableCell>{new Date(c.due_date).toLocaleDateString()}</TableCell>
                            <TableCell>{Number(c.compliance_percentage || 0).toFixed(0)}%</TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Box>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Summary</Typography>
              <Grid container spacing={1}>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Total Checklists</Typography>
                  <Typography variant="h5">{program.checklist_count}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Overdue</Typography>
                  <Typography variant="h5" color={program.overdue_count > 0 ? 'error' : 'inherit'}>
                    {program.overdue_count}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Next Due Date</Typography>
                  <Typography variant="body1">{program.next_due_date ? new Date(program.next_due_date).toLocaleDateString() : '—'}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PRPProgramDetail;

