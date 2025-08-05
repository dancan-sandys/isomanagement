import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Stack,
  Alert,
} from '@mui/material';
import {
  Construction,
  ArrowBack,
  Info,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface ComingSoonProps {
  title?: string;
  description?: string;
  parentPath?: string;
  parentTitle?: string;
}

const ComingSoon: React.FC<ComingSoonProps> = ({
  title = 'Feature Coming Soon',
  description = 'This feature is currently under development and will be available soon.',
  parentPath,
  parentTitle,
}) => {
  const navigate = useNavigate();

  const handleGoBack = () => {
    if (parentPath) {
      navigate(parentPath);
    } else {
      navigate(-1);
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Card>
        <CardContent>
          <Stack spacing={3} alignItems="center" textAlign="center">
            <Construction sx={{ fontSize: 64, color: 'primary.main' }} />
            
            <Box>
              <Typography variant="h4" fontWeight={600} gutterBottom>
                {title}
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                {description}
              </Typography>
            </Box>

            <Alert severity="info" sx={{ width: '100%' }}>
              <Typography variant="body2">
                <strong>Note:</strong> This feature is part of our ongoing development roadmap. 
                The core functionality is available in the main sections.
              </Typography>
            </Alert>

            <Stack direction="row" spacing={2}>
              {parentPath && parentTitle && (
                <Button
                  variant="contained"
                  startIcon={<ArrowBack />}
                  onClick={handleGoBack}
                >
                  Back to {parentTitle}
                </Button>
              )}
              <Button
                variant="outlined"
                onClick={() => navigate('/dashboard')}
              >
                Go to Dashboard
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ComingSoon; 