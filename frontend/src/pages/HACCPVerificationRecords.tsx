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
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
} from '@mui/material';
import { Refresh, PictureAsPdf, Visibility, Close } from '@mui/icons-material';
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
  result?: string | null;
  created_at: string | null;
}

const HACCPVerificationRecords: React.FC = () => {
  const [records, setRecords] = useState<VerificationRecordItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [recordTypeFilter, setRecordTypeFilter] = useState<string>('');
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
  const [viewerRecordId, setViewerRecordId] = useState<number | null>(null);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);
  const [loadingViewer, setLoadingViewer] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const currentUser = useSelector((s: RootState) => s.auth.user);
  const canViewRecords = !!currentUser && hasPermission(currentUser, 'haccp', 'view');

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
    if (canViewRecords) loadRecords();
  }, [canViewRecords, recordTypeFilter]);

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

  const handleViewPdf = async (record: VerificationRecordItem) => {
    setLoadingViewer(true);
    setViewerRecordId(null);
    setViewerUrl(null);
    try {
      const blob = await haccpAPI.downloadVerificationRecordPdf(record.id);
      const url = window.URL.createObjectURL(blob);
      setViewerUrl(url);
      setViewerRecordId(record.id);
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Failed to load PDF');
    } finally {
      setLoadingViewer(false);
    }
  };

  const handleCloseViewer = () => {
    if (viewerUrl) window.URL.revokeObjectURL(viewerUrl);
    setViewerUrl(null);
    setViewerRecordId(null);
  };

  if (!canViewRecords) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">You need HACCP view permission to view verification records.</Alert>
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
                <TableCell>Result</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {records.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
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
                    <TableCell>
                      {r.result ? (
                        <Chip
                          size="small"
                          label={r.result.toUpperCase()}
                          color={r.result === 'pass' ? 'success' : r.result === 'conditional' ? 'warning' : 'error'}
                          variant="outlined"
                        />
                      ) : '—'}
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        <Button
                          size="small"
                          startIcon={loadingViewer && viewerRecordId === r.id ? <CircularProgress size={16} /> : <Visibility />}
                          onClick={() => handleViewPdf(r)}
                          disabled={loadingViewer}
                        >
                          View
                        </Button>
                        <Button
                          size="small"
                          startIcon={downloadingId === r.id ? <CircularProgress size={16} /> : <PictureAsPdf />}
                          onClick={() => handleDownloadPdf(r.id)}
                          disabled={downloadingId !== null}
                        >
                          Download
                        </Button>
                      </Stack>
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

      <Dialog open={!!viewerUrl} onClose={handleCloseViewer} maxWidth="md" fullWidth PaperProps={{ sx: { height: '85vh' } }}>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6">
              {viewerRecordId != null
                ? (() => {
                    const rec = records.find((r) => r.id === viewerRecordId);
                    return rec
                      ? `Verification record: ${rec.ccp_name ?? rec.oprp_name ?? rec.record_type}${rec.verified_at ? ` (${new Date(rec.verified_at).toLocaleString()})` : ''}`
                      : `Verification record #${viewerRecordId}`;
                  })()
                : 'Verification record'}
            </Typography>
            <IconButton onClick={handleCloseViewer} size="small">
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers sx={{ p: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {viewerUrl && (
            <iframe
              src={viewerUrl}
              style={{ width: '100%', height: '100%', minHeight: 480, border: 'none' }}
              title="Verification record PDF"
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default HACCPVerificationRecords;
