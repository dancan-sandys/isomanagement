import React, { useState, useEffect } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  Box,
  Typography,
  IconButton,
  Collapse,
  Slide,
} from '@mui/material';
import {
  Close,
  CheckCircle,
  Error,
  Warning,
  Info,
  Notifications,
} from '@mui/icons-material';

interface NotificationToastProps {
  open: boolean;
  message: string;
  title?: string;
  severity?: 'success' | 'error' | 'warning' | 'info';
  autoHideDuration?: number;
  onClose: () => void;
  action?: React.ReactNode;
  persistent?: boolean;
  animated?: boolean;
}

const NotificationToast: React.FC<NotificationToastProps> = ({
  open,
  message,
  title,
  severity = 'info',
  autoHideDuration = 6000,
  onClose,
  action,
  persistent = false,
  animated = true,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (open) {
      setIsVisible(true);
    }
  }, [open]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => {
      onClose();
    }, 300);
  };

  const getSeverityIcon = () => {
    switch (severity) {
      case 'success':
        return <CheckCircle />;
      case 'error':
        return <Error />;
      case 'warning':
        return <Warning />;
      case 'info':
        return <Info />;
      default:
        return <Notifications />;
    }
  };

  const getSeverityColor = () => {
    switch (severity) {
      case 'success':
        return '#059669';
      case 'error':
        return '#DC2626';
      case 'warning':
        return '#EA580C';
      case 'info':
        return '#2563EB';
      default:
        return '#64748B';
    }
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={persistent ? undefined : autoHideDuration}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      TransitionComponent={Slide}
      transitionDuration={300}
      sx={{
        '& .MuiSnackbarContent-root': {
          borderRadius: 16,
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          border: '1px solid',
          borderColor: 'divider',
          minWidth: 320,
          maxWidth: 480,
          background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',
          backdropFilter: 'blur(10px)',
        },
      }}
    >
      <Collapse in={isVisible} timeout={300}>
        <Alert
          severity={severity}
          onClose={handleClose}
          action={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {action}
              <IconButton
                size="small"
                onClick={handleClose}
                sx={{
                  color: 'inherit',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.04)',
                  },
                }}
              >
                <Close fontSize="small" />
              </IconButton>
            </Box>
          }
          icon={
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 32,
                height: 32,
                borderRadius: '50%',
                backgroundColor: `${getSeverityColor()}15`,
                color: getSeverityColor(),
                animation: animated ? 'bounce 0.6s ease-in-out' : 'none',
                '@keyframes bounce': {
                  '0%, 20%, 53%, 80%, 100%': {
                    transform: 'translate3d(0,0,0)',
                  },
                  '40%, 43%': {
                    transform: 'translate3d(0, -8px, 0)',
                  },
                  '70%': {
                    transform: 'translate3d(0, -4px, 0)',
                  },
                  '90%': {
                    transform: 'translate3d(0, -2px, 0)',
                  },
                },
              }}
            >
              {getSeverityIcon()}
            </Box>
          }
          sx={{
            width: '100%',
            borderRadius: 16,
            border: 'none',
            boxShadow: 'none',
            backgroundColor: 'transparent',
            '& .MuiAlert-message': {
              flex: 1,
            },
            '& .MuiAlert-action': {
              alignItems: 'flex-start',
              paddingTop: 1,
            },
          }}
        >
          <Box>
            {title && (
              <AlertTitle sx={{ fontWeight: 700, mb: 0.5 }}>
                {title}
              </AlertTitle>
            )}
            <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
              {message}
            </Typography>
          </Box>
        </Alert>
      </Collapse>
    </Snackbar>
  );
};

export default NotificationToast; 