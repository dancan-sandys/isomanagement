import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  CircularProgress,
  Alert,
  Stack,
} from '@mui/material';
import { Refresh, PictureAsPdf } from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { hasPermission } from '../store/slices/authSlice';
import { haccpAPI } from '../services/haccpAPI';

interface VerificationRecordItem {
  id: number;
  record_type: string;
  ccp_id: number | null;
  oprp_id: number | null;
  monitoring_log_id: number | null;
  product_id: number | null;
  product_name: string | null;
  ccp_name: string | null;
  oprp_name: string | null;
  verified_at: string;
  verified_by: number;
  verifier_name: string | null;
  created_at: string | null;
}

const HACCPVerificationRecords: React.FC = () => {
  const [records, setRecords] = useState<VerificationRecordItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [recordTypeFilter, setRecordTypeFilter] = useState<string>('');
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const currentUser = useSelector((s: RootState) => s.auth.user);
  const canAdmin = !!currentUser && hasPermission(currentUser, 'haccp', 'admin');

  const loadRecords = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: { record_type?: string; skip?: number; limit?: number } = { skip: 0, limit: 100 };
      if (recordTypeFilter && recordTypeFilter !== 'all') params.record_type = recordTypeFilter;
      const res = await haccpAPI.getVerificationRecords(params);
      const payload = res?.data ?? res;
      const items = payload?.items ?? [];
      setRecords(items);
      setTotal(payload?.total ?? items.length);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load verification records');
      setRecords([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (canAdmin) loadRecords();
  }, [canAdmin, recordTypeFilter]);

  const handleDownloadPdf = async (recordId: number) => {
    setDownloadingId(recordId);
    try {
      const blob = await haccpAPI.downloadVerificationRecordPdf(recordId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `verification_record_${recordId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Failed to download PDF');
    } finally {
      setDownloadingId(null);
    }
  };

  if (!canAdmin) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">You need HACCP admin permission to view verification records.</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Verification Records
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        PDFs generated when monitoring logs are verified. Filter by record type (CCP or OPRP).
      </Typography>

      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel>Record type</InputLabel>
          <Select
            value={recordTypeFilter || 'all'}
            label="Record type"
            onChange={(e) => setRecordTypeFilter(e.target.value === 'all' ? '' : e.target.value)}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="ccp">CCP</MenuItem>
            <MenuItem value="oprp">OPRP</MenuItem>
          </Select>
        </FormControl>
        <Button startIcon={<Refresh />} onClick={loadRecords} disabled={loading}>
          Refresh
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Type</TableCell>
                <TableCell>Product</TableCell>
                <TableCell>CCP / OPRP</TableCell>
                <TableCell>Verified at</TableCell>
                <TableCell>Verified by</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {records.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No verification records yet. Records are created when a monitoring log is verified.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                records.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell>
                      <Chip
                        size="small"
                        label={r.record_type.toUpperCase()}
                        color={r.record_type === 'ccp' ? 'primary' : 'secondary'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{r.product_name ?? '—'}</TableCell>
                    <TableCell>{r.ccp_name ?? r.oprp_name ?? '—'}</TableCell>
                    <TableCell>{r.verified_at ? new Date(r.verified_at).toLocaleString() : '—'}</TableCell>
                    <TableCell>{r.verifier_name ?? `User ${r.verified_by}`}</TableCell>
                    <TableCell align="right">
                      <Button
                        size="small"
                        startIcon={downloadingId === r.id ? <CircularProgress size={16} /> : <PictureAsPdf />}
                        onClick={() => handleDownloadPdf(r.id)}
                        disabled={downloadingId !== null}
                      >
                        Download PDF
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      {total > 0 && !loading && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Showing {records.length} of {total} record(s).
        </Typography>
      )}
    </Box>
  );
};

export default HACCPVerificationRecords;
