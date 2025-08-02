import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Close,
  Download,
  ZoomIn,
  ZoomOut,
  Fullscreen,
  FullscreenExit,
} from '@mui/icons-material';
import { documentsAPI } from '../services/api';

interface DocumentViewerProps {
  open: boolean;
  onClose: () => void;
  documentId: number;
  documentTitle?: string;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({
  open,
  onClose,
  documentId,
  documentTitle = 'Document Viewer',
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [documentUrl, setDocumentUrl] = useState<string | null>(null);
  const [zoom, setZoom] = useState(100);
  const [fullscreen, setFullscreen] = useState(false);

  useEffect(() => {
    if (open && documentId) {
      loadDocument();
    }
  }, [open, documentId]);

  const loadDocument = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await documentsAPI.downloadDocument(documentId);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      setDocumentUrl(url);
    } catch (err: any) {
      setError(err.message || 'Failed to load document');
      console.error('Document loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await documentsAPI.downloadDocument(documentId);
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${documentTitle || 'document'}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message || 'Failed to download document');
      console.error('Download error:', err);
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 25, 200));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 25, 50));
  };

  const handleFullscreen = () => {
    setFullscreen(!fullscreen);
  };

  const handleClose = () => {
    if (documentUrl) {
      URL.revokeObjectURL(documentUrl);
      setDocumentUrl(null);
    }
    setZoom(100);
    setFullscreen(false);
    setError(null);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth={fullscreen ? false : 'lg'}
      fullWidth={!fullscreen}
      fullScreen={fullscreen}
      PaperProps={{
        sx: {
          height: fullscreen ? '100vh' : '80vh',
          maxHeight: fullscreen ? '100vh' : '80vh',
        },
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        pb: 1
      }}>
        <Typography variant="h6" noWrap sx={{ flex: 1 }}>
          {documentTitle}
        </Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Zoom In">
            <IconButton size="small" onClick={handleZoomIn}>
              <ZoomIn />
            </IconButton>
          </Tooltip>
          <Tooltip title="Zoom Out">
            <IconButton size="small" onClick={handleZoomOut}>
              <ZoomOut />
            </IconButton>
          </Tooltip>
          <Tooltip title={fullscreen ? 'Exit Fullscreen' : 'Fullscreen'}>
            <IconButton size="small" onClick={handleFullscreen}>
              {fullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Download">
            <IconButton size="small" onClick={handleDownload}>
              <Download />
            </IconButton>
          </Tooltip>
          <Tooltip title="Close">
            <IconButton size="small" onClick={handleClose}>
              <Close />
            </IconButton>
          </Tooltip>
        </Box>
      </DialogTitle>
      
      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column' }}>
        {loading && (
          <Box display="flex" justifyContent="center" alignItems="center" height="100%">
            <CircularProgress />
          </Box>
        )}
        
        {error && (
          <Box p={2}>
            <Alert severity="error">{error}</Alert>
          </Box>
        )}
        
        {documentUrl && !loading && !error && (
          <Box
            sx={{
              flex: 1,
              overflow: 'hidden',
              position: 'relative',
            }}
          >
            <iframe
              src={`${documentUrl}#toolbar=1&navpanes=1&scrollbar=1&zoom=${zoom}`}
              style={{
                width: '100%',
                height: '100%',
                border: 'none',
              }}
              title={documentTitle}
            />
          </Box>
        )}
      </DialogContent>
      
      <DialogActions sx={{ px: 2, py: 1 }}>
        <Typography variant="caption" color="text.secondary">
          Zoom: {zoom}%
        </Typography>
        <Button onClick={handleClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentViewer; 