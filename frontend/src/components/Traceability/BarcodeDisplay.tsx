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
  ContentCopy as CopyIcon
} from '@mui/icons-material';
import { BarcodeData } from '../../types/traceability';

interface BarcodeDisplayProps {
  barcodeData: BarcodeData;
  showActions?: boolean;
}

const BarcodeDisplay: React.FC<BarcodeDisplayProps> = ({
  barcodeData,
  showActions = true
}) => {
  const handlePrint = () => {
    // Implement print functionality
    console.log('Print barcode:', barcodeData.barcode);
  };

  const handleDownload = () => {
    // Implement download functionality
    console.log('Download barcode:', barcodeData.barcode);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(barcodeData.barcode);
    // You could add a toast notification here
  };

  return (
    <Card variant="outlined">
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            Barcode
          </Typography>
          {showActions && (
            <Box display="flex" gap={1}>
              <Tooltip title="Copy Barcode">
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
              Barcode Type
            </Typography>
            <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
              {barcodeData.barcode_type}
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Barcode Value
            </Typography>
            <Paper 
              variant="outlined" 
              sx={{ 
                p: 2, 
                bgcolor: 'grey.50',
                fontFamily: 'monospace',
                fontSize: '1.2rem',
                textAlign: 'center',
                letterSpacing: '0.2em'
              }}
            >
              {barcodeData.barcode}
            </Paper>
          </Grid>

          {barcodeData.barcode_image && (
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Barcode Image
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
                  src={barcodeData.barcode_image} 
                  alt="Barcode"
                  style={{ maxWidth: '100%', height: 'auto' }}
                />
              </Box>
            </Grid>
          )}

          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Generated At
            </Typography>
            <Typography variant="body1">
              {new Date(barcodeData.generated_at).toLocaleString()}
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default BarcodeDisplay; 