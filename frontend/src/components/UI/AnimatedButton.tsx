import React, { useState } from 'react';
import {
  Button,
  ButtonProps,
  CircularProgress,
  Box,
  Tooltip,
} from '@mui/material';
import {
  Check,
  Error,
  Warning,
  Info,
} from '@mui/icons-material';

interface AnimatedButtonProps extends Omit<ButtonProps, 'color'> {
  loading?: boolean;
  success?: boolean;
  error?: boolean;
  warning?: boolean;
  info?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
  tooltip?: string;
  pulse?: boolean;
  glow?: boolean;
  ripple?: boolean;
  onAnimationComplete?: () => void;
}

const AnimatedButton: React.FC<AnimatedButtonProps> = ({
  loading = false,
  success = false,
  error = false,
  warning = false,
  info = false,
  icon,
  children,
  tooltip,
  pulse = false,
  glow = false,
  ripple = false,
  onAnimationComplete,
  ...props
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const getStatusColor = () => {
    if (success) return 'success';
    if (error) return 'error';
    if (warning) return 'warning';
    if (info) return 'info';
    return 'primary';
  };

  const getStatusIcon = () => {
    if (success) return <Check />;
    if (error) return <Error />;
    if (warning) return <Warning />;
    if (info) return <Info />;
    return null;
  };

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (ripple) {
      // Create ripple effect
      const button = event.currentTarget;
      const ripple = document.createElement('span');
      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = event.clientX - rect.left - size / 2;
      const y = event.clientY - rect.top - size / 2;
      
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = x + 'px';
      ripple.style.top = y + 'px';
      ripple.classList.add('ripple');
      
      button.appendChild(ripple);
      
      setTimeout(() => {
        ripple.remove();
      }, 600);
    }

    if (success && !showSuccess) {
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        onAnimationComplete?.();
      }, 2000);
    }

    props.onClick?.(event);
  };

  const buttonContent = (
    <Button
      {...props}
      color={getStatusColor()}
      onClick={handleClick}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      onMouseLeave={() => setIsPressed(false)}
      disabled={loading || props.disabled}
      sx={{
        position: 'relative',
        overflow: 'hidden',
        borderRadius: 3,
        fontWeight: 700,
        textTransform: 'none',
        letterSpacing: '0.025em',
        padding: '12px 24px',
        minHeight: 48,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        transform: isPressed ? 'scale(0.95)' : 'scale(1)',
        boxShadow: glow ? '0 0 20px rgba(30, 64, 175, 0.3)' : '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: glow 
            ? '0 0 30px rgba(30, 64, 175, 0.5)' 
            : '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        },
        '&:active': {
          transform: 'translateY(0px) scale(0.98)',
        },
        animation: pulse ? 'pulse 2s infinite' : 'none',
        '@keyframes pulse': {
          '0%': {
            boxShadow: '0 0 0 0 rgba(30, 64, 175, 0.7)',
          },
          '70%': {
            boxShadow: '0 0 0 10px rgba(30, 64, 175, 0)',
          },
          '100%': {
            boxShadow: '0 0 0 0 rgba(30, 64, 175, 0)',
          },
        },
        '& .ripple': {
          position: 'absolute',
          borderRadius: '50%',
          transform: 'scale(0)',
          animation: 'ripple 0.6s linear',
          backgroundColor: 'rgba(255, 255, 255, 0.3)',
        },
        '@keyframes ripple': {
          to: {
            transform: 'scale(4)',
            opacity: 0,
          },
        },
        ...props.sx,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {loading ? (
          <CircularProgress size={20} color="inherit" />
        ) : showSuccess ? (
          <Check sx={{ animation: 'bounce 0.6s' }} />
        ) : (
          <>
            {icon}
            {getStatusIcon()}
          </>
        )}
        <Box sx={{ 
          opacity: loading ? 0.7 : 1,
          transition: 'opacity 0.2s',
        }}>
          {children}
        </Box>
      </Box>
    </Button>
  );

  if (tooltip) {
    return (
      <Tooltip title={tooltip} arrow>
        {buttonContent}
      </Tooltip>
    );
  }

  return buttonContent;
};

export default AnimatedButton; 