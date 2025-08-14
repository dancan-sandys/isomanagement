import React, { useState } from 'react';
import { Box, Button, Card, CardContent, Typography, Alert, Stack } from '@mui/material';
import { api } from '../services/api';

const HiddenDemoTools: React.FC = () => {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const callEndpoint = async (url: string, label: string) => {
    setBusy(true);
    setMessage(null);
    setError(null);
    try {
      const res = await api.post(url);
      const data = (res as any)?.data || res; // our api wrapper returns data, but keep safe
      setMessage(data?.message || `${label} completed`);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Request failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 720, mx: 'auto', mt: 6 }}>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>Demo Utilities (Hidden)</Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Admin-only tools to reset and seed demo data. This page is intentionally not linked in menus.
          </Typography>
          <Stack spacing={2} mt={2}>
            {message && <Alert severity="success">{message}</Alert>}
            {error && <Alert severity="error">{error}</Alert>}
            <Button
              variant="outlined"
              disabled={busy}
              onClick={() => callEndpoint('/demo/reset', 'Reset DB')}
            >
              {busy ? 'Working…' : 'Reset Database'}
            </Button>
            <Button
              variant="contained"
              disabled={busy}
              onClick={() => callEndpoint('/demo/seed/engineering', 'Seed Engineering Demo')}
            >
              {busy ? 'Working…' : 'Seed Engineering Demo Data'}
            </Button>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
};

export default HiddenDemoTools;


