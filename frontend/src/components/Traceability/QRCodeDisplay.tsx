import React from 'react';
import {
  Box,
  Typography,
  Paper,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import {
  Print as PrintIcon,
  Download as DownloadIcon,
  ContentCopy as CopyIcon,
  QrCode as QrCodeIcon
} from '@mui/icons-material';
import { QRCodeData } from '../../types/traceability';

interface QRCodeDisplayProps {
  qrCodeData: QRCodeData;
  showActions?: boolean;
}

const QRCodeDisplay: React.FC<QRCodeDisplayProps> = ({
  qrCodeData,
  showActions = true
}) => {
  const handlePrint = () => {
    if (!qrCodeData.qr_code_image) return;
    const w = window.open('');
    if (!w) return;
    w.document.write(`<img src="${qrCodeData.qr_code_image}" style="max-width:100%" />`);
    w.document.close();
    w.focus();
    w.print();
    w.close();
  };

  const handleDownload = () => {
    if (!qrCodeData.qr_code_image) return;
    const a = document.createElement('a');
    a.href = qrCodeData.qr_code_image;
    a.download = `qrcode_${qrCodeData.batch_id || 'batch'}.png`;
    a.click();
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(qrCodeData.qr_code);
    // You could add a toast notification here
  };

  return (
    <Card variant="outlined">
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            QR Code
          </Typography>
          {showActions && (
            <Box display="flex" gap={1}>
              <Tooltip title="Copy QR Code">
                <IconButton size="small" onClick={handleCopy}>
                  <CopyIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Download">
                <IconButton size="small" onClick={handleDownload}>
                  <DownloadIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Print">
                <IconButton size="small" onClick={handlePrint}>
                  <PrintIcon />
                </IconButton>
              </Tooltip>
            </Box>
          )}
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              QR Code Value
            </Typography>
            <Paper 
              variant="outlined" 
              sx={{ 
                p: 2, 
                bgcolor: 'grey.50',
                fontFamily: 'monospace',
                fontSize: '0.9rem',
                textAlign: 'center',
                wordBreak: 'break-all'
              }}
            >
              {qrCodeData.qr_code}
            </Paper>
          </Grid>

          {qrCodeData.qr_code_image && (
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                QR Code Image
              </Typography>
              <Box 
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'center',
                  p: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1
                }}
              >
                <img 
                  src={qrCodeData.qr_code_image} 
                  alt="QR Code"
                  style={{ maxWidth: '200px', height: 'auto' }}
                />
              </Box>
            </Grid>
          )}

          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Data Payload
            </Typography>
            <Paper 
              variant="outlined" 
              sx={{ 
                p: 2, 
                bgcolor: 'grey.50',
                fontFamily: 'monospace',
                fontSize: '0.8rem',
                maxHeight: '150px',
                overflow: 'auto'
              }}
            >
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                {qrCodeData.data_payload}
              </pre>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Generated At
            </Typography>
            <Typography variant="body1">
              {new Date(qrCodeData.generated_at).toLocaleString()}
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default QRCodeDisplay; 