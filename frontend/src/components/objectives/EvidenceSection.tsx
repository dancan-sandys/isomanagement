import React, { useEffect, useRef, useState } from 'react';
import { Box, Button, Chip, CircularProgress, IconButton, List, ListItem, ListItemSecondaryAction, ListItemText, Typography, Tooltip } from '@mui/material';
import { CloudUpload as CloudUploadIcon, Delete as DeleteIcon, Verified as VerifiedIcon, Check as CheckIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import objectivesService from '../../services/objectivesService';
import { ObjectiveEvidence } from '../../types/objectives';

interface EvidenceSectionProps {
  objectiveId: number;
}

const EvidenceSection: React.FC<EvidenceSectionProps> = ({ objectiveId }) => {
  const [items, setItems] = useState<ObjectiveEvidence[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const res = await objectivesService.listEvidence(objectiveId);
      setItems(res.data || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [objectiveId]);

  const onUploadClick = () => fileInputRef.current?.click();

  const onFileSelected = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    const file = files[0];
    setUploading(true);
    try {
      await objectivesService.uploadEvidence(objectiveId, { file });
      await load();
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const onVerify = async (id: number) => {
    await objectivesService.verifyEvidence(objectiveId, id);
    await load();
  };

  const onDelete = async (id: number) => {
    await objectivesService.deleteEvidence(objectiveId, id);
    await load();
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
        <Typography variant="h6" id="evidence-heading">Evidence</Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh evidence">
            <IconButton aria-label="Refresh evidence" onClick={load}><RefreshIcon /></IconButton>
          </Tooltip>
          <input
            ref={fileInputRef}
            type="file"
            aria-label="Upload evidence file"
            onChange={onFileSelected}
            style={{ display: 'none' }}
          />
          <Button
            variant="outlined"
            startIcon={<CloudUploadIcon />}
            onClick={onUploadClick}
            aria-describedby="evidence-heading"
            disabled={uploading}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </Button>
        </Box>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" p={2}><CircularProgress /></Box>
      ) : items.length === 0 ? (
        <Typography variant="body2" color="textSecondary">No evidence uploaded.</Typography>
      ) : (
        <List aria-labelledby="evidence-heading">
          {items.map(ev => (
            <ListItem key={ev.id} divider>
              <ListItemText
                primary={ev.original_filename}
                secondary={`Uploaded ${new Date(ev.uploaded_at).toLocaleString()}${ev.notes ? ' • ' + ev.notes : ''}`}
              />
              <Chip label={ev.is_verified ? 'Verified' : 'Unverified'} color={ev.is_verified ? 'success' as any : 'default'} size="small" sx={{ mr: 1 }} />
              <ListItemSecondaryAction>
                {!ev.is_verified && (
                  <Tooltip title="Verify evidence">
                    <IconButton edge="end" aria-label="Verify evidence" onClick={() => onVerify(ev.id)}>
                      <CheckIcon />
                    </IconButton>
                  </Tooltip>
                )}
                <Tooltip title="Delete evidence">
                  <IconButton edge="end" aria-label="Delete evidence" onClick={() => onDelete(ev.id)}>
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
};

export default EvidenceSection;