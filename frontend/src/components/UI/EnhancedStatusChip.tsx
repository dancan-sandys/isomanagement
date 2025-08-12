import React, { useState } from 'react';
import { Chip, ChipProps, Tooltip } from '@mui/material';
import { getStatusChipProps } from '../../theme/designSystem';

export type StatusType =
  | 'compliant'
  | 'nonConformance'
  | 'pending'
  | 'warning'
  | 'info'
  | 'approved'
  | 'rejected'
  | 'under_review'
  | 'active'
  | 'inactive'
  | 'suspended'
  | 'passed'
  | 'failed'
  | 'pending_approval'
  | 'blacklisted';

interface EnhancedStatusChipProps extends Omit<ChipProps, 'color'> {
  status: StatusType;
  label: string;
  size?: 'small' | 'medium';
  animated?: boolean;
  pulse?: boolean;
  glow?: boolean;
  tooltip?: string;
  onClick?: () => void;
}

const EnhancedStatusChip: React.FC<EnhancedStatusChipProps> = ({ 
  status, 
  label, 
  size = 'small',
  animated = false,
  pulse = false,
  glow = false,
  tooltip,
  onClick,
  ...props 
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const statusProps = getStatusChipProps(status);

  const chipContent = (
    <Chip
      label={label}
      color={statusProps.color}
      size={size}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      sx={{
        backgroundColor: statusProps.backgroundColor,
        border: `2px solid ${statusProps.borderColor}`,
        fontWeight: 700,
        fontSize: '0.75rem',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        padding: '6px 16px',
        borderRadius: 20,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        cursor: onClick ? 'pointer' : 'default',
        position: 'relative',
        overflow: 'hidden',
        '&:hover': {
          transform: onClick ? 'scale(1.05)' : 'scale(1.02)',
          boxShadow: glow ? '0 0 15px rgba(30, 64, 175, 0.4)' : '0 4px 12px rgba(0, 0, 0, 0.15)',
        },
        '&:active': {
          transform: 'scale(0.98)',
        },
        animation: pulse ? 'pulse 2s infinite' : 'none',
        '@keyframes pulse': {
          '0%': {
            boxShadow: `0 0 0 0 ${statusProps.borderColor}`,
          },
          '70%': {
            boxShadow: `0 0 0 6px ${statusProps.borderColor}40`,
          },
          '100%': {
            boxShadow: `0 0 0 0 ${statusProps.borderColor}00`,
          },
        },
        '&::before': animated ? {
          content: '""',
          position: 'absolute',
          top: 0,
          left: '-100%',
          width: '100%',
          height: '100%',
          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
          transition: 'left 0.5s',
        } : {},
        '&:hover::before': animated ? {
          left: '100%',
        } : {},
        '& .MuiChip-label': {
          color: statusProps.textColor,
          fontWeight: 700,
          transition: 'color 0.2s',
        },
        ...props.sx,
      }}
      {...props}
    />
  );

  if (tooltip) {
    return (
      <Tooltip title={tooltip} arrow>
        {chipContent}
      </Tooltip>
    );
  }

  return chipContent;
};

export default EnhancedStatusChip; 