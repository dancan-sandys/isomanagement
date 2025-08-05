import React from 'react';
import { Chip, ChipProps } from '@mui/material';
import { getStatusChipProps } from '../../theme/designSystem';

export type StatusType = 'compliant' | 'nonConformance' | 'pending' | 'warning' | 'info';

interface StatusChipProps extends Omit<ChipProps, 'color'> {
  status: StatusType;
  label: string;
  size?: 'small' | 'medium';
}

const StatusChip: React.FC<StatusChipProps> = ({ 
  status, 
  label, 
  size = 'small',
  ...props 
}) => {
  const statusProps = getStatusChipProps(status);

  return (
    <Chip
      label={label}
      color={statusProps.color}
      size={size}
      sx={{
        backgroundColor: statusProps.backgroundColor,
        border: `1px solid ${statusProps.borderColor}`,
        fontWeight: 600,
        fontSize: '0.75rem',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        '& .MuiChip-label': {
          color: statusProps.color === 'success' ? '#166534' : 
                 statusProps.color === 'error' ? '#991B1B' :
                 statusProps.color === 'warning' ? '#92400E' :
                 '#1E40AF',
        },
      }}
      {...props}
    />
  );
};

export default StatusChip; 