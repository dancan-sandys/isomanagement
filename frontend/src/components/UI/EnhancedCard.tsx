import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  IconButton,
  Tooltip,
  Chip,
  Skeleton,
  Fade,
  Grow,
} from '@mui/material';
import {
  MoreVert,
  TrendingUp,
  TrendingDown,
  Remove,
  Star,
  Favorite,
  Share,
} from '@mui/icons-material';
import StatusChip, { StatusType } from './StatusChip';

interface EnhancedCardProps {
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
  variant?: 'default' | 'metric' | 'chart' | 'list' | 'featured';
  loading?: boolean;
  favorite?: boolean;
  onFavorite?: () => void;
  onShare?: () => void;
  elevation?: 'light' | 'medium' | 'heavy';
  animation?: 'fade' | 'grow' | 'slide';
  delay?: number;
}

const EnhancedCard: React.FC<EnhancedCardProps> = ({
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
  loading = false,
  favorite = false,
  onFavorite,
  onShare,
  elevation = 'light',
  animation = 'fade',
  delay = 0,
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

  const getElevationStyle = () => {
    switch (elevation) {
      case 'light':
        return {
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        };
      case 'medium':
        return {
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        };
      case 'heavy':
        return {
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        };
      default:
        return {};
    }
  };

  const getAnimationComponent = () => {
    const props = {
      in: true,
      timeout: 300 + delay,
      style: { transformOrigin: '0 0 0' },
    };

    switch (animation) {
      case 'fade':
        return Fade;
      case 'grow':
        return Grow;
      case 'slide':
        return Fade; // Fallback to fade for slide effect
      default:
        return Fade;
    }
  };

  const AnimationComponent = getAnimationComponent();

  const cardContent = (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        borderRadius: variant === 'featured' ? 24 : 16,
        background: variant === 'featured' 
          ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          : 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',
        color: variant === 'featured' ? 'white' : 'inherit',
        ...getElevationStyle(),
        '&:hover': onClick ? {
          transform: 'translateY(-4px)',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        } : {},
        '&:active': onClick ? {
          transform: 'translateY(-2px)',
        } : {},
        position: 'relative',
        overflow: 'hidden',
        '&::before': variant === 'featured' ? {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%)',
          transform: 'translateX(-100%)',
          transition: 'transform 0.6s',
        } : {},
        '&:hover::before': variant === 'featured' ? {
          transform: 'translateX(100%)',
        } : {},
      }}
      onClick={onClick}
    >
      <CardHeader
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography 
              variant="h6" 
              fontWeight={700}
              sx={{ 
                color: variant === 'featured' ? 'white' : 'inherit',
                textShadow: variant === 'featured' ? '0 1px 2px rgba(0,0,0,0.1)' : 'none',
              }}
            >
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
        subheader={
          subtitle && (
            <Typography 
              variant="body2" 
              sx={{ 
                color: variant === 'featured' ? 'rgba(255,255,255,0.8)' : 'text.secondary',
                mt: 0.5,
              }}
            >
              {subtitle}
            </Typography>
          )
        }
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {onFavorite && (
              <Tooltip title={favorite ? 'Remove from favorites' : 'Add to favorites'}>
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onFavorite();
                  }}
                  sx={{
                    color: favorite ? 'warning.main' : variant === 'featured' ? 'white' : 'text.secondary',
                    '&:hover': {
                      color: 'warning.main',
                      transform: 'scale(1.1)',
                    },
                  }}
                >
                  <Favorite fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {onShare && (
              <Tooltip title="Share">
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onShare();
                  }}
                  sx={{
                    color: variant === 'featured' ? 'white' : 'text.secondary',
                    '&:hover': {
                      color: 'primary.main',
                      transform: 'scale(1.1)',
                    },
                  }}
                >
                  <Share fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {actions && (
              <IconButton size="small">
                <MoreVert />
              </IconButton>
            )}
          </Box>
        }
        sx={{
          pb: variant === 'metric' ? 1 : 2,
        }}
      />

      <CardContent sx={{ flex: 1, pt: 0 }}>
        {loading ? (
          <Box>
            <Skeleton variant="text" width="60%" height={32} />
            <Skeleton variant="text" width="40%" height={24} />
            <Skeleton variant="rectangular" width="100%" height={100} sx={{ mt: 2, borderRadius: 2 }} />
          </Box>
        ) : variant === 'metric' ? (
          <Box>
            <Typography 
              variant="h3" 
              fontWeight={800}
              sx={{ 
                mb: 1,
                color: (variant as string) === 'featured' ? 'white' : 'inherit',
                textShadow: (variant as string) === 'featured' ? '0 2px 4px rgba(0,0,0,0.1)' : 'none',
              }}
            >
              {value}
            </Typography>
            
            {trend && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                {getTrendIcon(trend.direction)}
                <Typography
                  variant="body2"
                  sx={{ 
                    color: getTrendColor(trend.direction),
                    fontWeight: 600,
                  }}
                >
                  {trend.value}% {trend.label}
                </Typography>
              </Box>
            )}

            {progress && (
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      color: (variant as string) === 'featured' ? 'rgba(255,255,255,0.8)' : 'text.secondary',
                      fontWeight: 500,
                    }}
                  >
                    {progress.label}
                  </Typography>
                  <Typography 
                    variant="caption" 
                    fontWeight={700}
                    sx={{ 
                      color: (variant as string) === 'featured' ? 'white' : 'inherit',
                    }}
                  >
                    {progress.value}%
                  </Typography>
                </Box>
                <Box
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: (variant as string) === 'featured' ? 'rgba(255,255,255,0.2)' : '#E2E8F0',
                    overflow: 'hidden',
                  }}
                >
                  <Box
                    sx={{
                      height: '100%',
                      width: `${progress.value}%`,
                      backgroundColor: progress.color === 'success' ? '#059669' :
                                   progress.color === 'error' ? '#DC2626' :
                                   progress.color === 'warning' ? '#EA580C' :
                                   (variant as string) === 'featured' ? 'white' : '#1E40AF',
                      borderRadius: 4,
                      transition: 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
                    }}
                  />
                </Box>
              </Box>
            )}
          </Box>
        ) : variant === 'chart' ? (
          <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {children || (
              <Typography 
                variant="body2" 
                sx={{ 
                  color: (variant as string) === 'featured' ? 'rgba(255,255,255,0.8)' : 'text.secondary',
                }}
              >
                Chart placeholder
              </Typography>
            )}
          </Box>
        ) : variant === 'list' ? (
          <Box>
            {children}
          </Box>
        ) : variant === 'default' ? (
          <Box>
            {children}
          </Box>
        ) : null}
      </CardContent>
    </Card>
  );

  return (
    <AnimationComponent
      in={true}
      timeout={300 + delay}
      style={{ transformOrigin: '0 0 0' }}
    >
      {cardContent}
    </AnimationComponent>
  );
};

export default EnhancedCard; 