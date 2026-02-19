import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  IconButton,
  Tooltip,
  LinearProgress,
  Chip,
} from '@mui/material';
import {
  MoreVert,
  TrendingUp,
  TrendingDown,
  Remove,
} from '@mui/icons-material';
import StatusChip, { StatusType } from '../UI/StatusChip';

interface DashboardCardProps {
  title: string;
  subtitle?: string;
  value?: string | number;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
    label: string;
  };
  status?: {
    type: StatusType;
    label: string;
  };
  progress?: {
    value: number;
    label: string;
    color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning';
  };
  actions?: React.ReactNode;
  children?: React.ReactNode;
  onClick?: () => void;
  variant?: 'default' | 'metric' | 'chart' | 'list';
  icon?: React.ReactNode;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  subtitle,
  value,
  trend,
  status,
  progress,
  actions,
  children,
  onClick,
  variant = 'default',
  icon,
}) => {
  const getTrendIcon = (direction: 'up' | 'down' | 'neutral') => {
    switch (direction) {
      case 'up':
        return <TrendingUp fontSize="small" color="success" />;
      case 'down':
        return <TrendingDown fontSize="small" color="error" />;
      case 'neutral':
        return <Remove fontSize="small" color="action" />;
    }
  };

  const getTrendColor = (direction: 'up' | 'down' | 'neutral') => {
    switch (direction) {
      case 'up':
        return 'success.main';
      case 'down':
        return 'error.main';
      case 'neutral':
        return 'text.secondary';
    }
  };

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s ease-in-out',
        '&:hover': onClick ? {
          boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
          transform: 'translateY(-2px)',
        } : {},
      }}
      onClick={onClick}
    >
      <CardHeader
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6" fontWeight={600}>
              {title}
            </Typography>
            {status && (
              <StatusChip
                status={status.type}
                label={status.label}
                size="small"
              />
            )}
          </Box>
        }
        subheader={subtitle}
        action={
          actions && (
            <IconButton size="small">
              <MoreVert />
            </IconButton>
          )
        }
        sx={{
          pb: variant === 'metric' ? 1 : 2,
        }}
      />

      <CardContent sx={{ flex: 1, pt: 0 }}>
        {variant === 'metric' && (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              {icon && (
                <Box sx={{ color: 'primary.main' }}>
                  {icon}
                </Box>
              )}
              <Typography variant="h3" fontWeight={700}>
                {value}
              </Typography>
            </Box>
            
            {trend && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                {getTrendIcon(trend.direction)}
                <Typography
                  variant="body2"
                  sx={{ color: getTrendColor(trend.direction) }}
                >
                  {trend.value}% {trend.label}
                </Typography>
              </Box>
            )}

            {progress && (
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    {progress.label}
                  </Typography>
                  <Typography variant="caption" fontWeight={600}>
                    {progress.value}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={progress.value}
                  color={progress.color || 'primary'}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
            )}
          </Box>
        )}

        {variant === 'chart' && (
          <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {children || (
              <Typography variant="body2" color="text.secondary">
                Chart placeholder
              </Typography>
            )}
          </Box>
        )}

        {variant === 'list' && (
          <Box>
            {children}
          </Box>
        )}

        {variant === 'default' && children}
      </CardContent>
    </Card>
  );
};

export default DashboardCard; 