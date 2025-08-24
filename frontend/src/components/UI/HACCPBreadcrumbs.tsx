import React from 'react';
import {
  Breadcrumbs,
  Link,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import {
  NavigateNext,
  Home,
  Science,
  Dashboard,
  Assessment,
  Schedule,
  Warning,
  Security,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';

interface HACCPBreadcrumbsProps {
  customTitle?: string;
  productName?: string;
}

const HACCPBreadcrumbs: React.FC<HACCPBreadcrumbsProps> = ({
  customTitle,
  productName,
}) => {
  const location = useLocation();
  const navigate = useNavigate();

  const getPageInfo = (path: string) => {
    const routeMapping: { [key: string]: { title: string; icon: React.ReactNode; color?: string } } = {
      '/haccp': { title: 'HACCP System', icon: <Science />, color: 'primary' },
      '/haccp/monitoring': { title: 'Monitoring Console', icon: <Science />, color: 'primary' },
      '/haccp/verification': { title: 'Verification Console', icon: <Security />, color: 'secondary' },
      '/haccp/schedules': { title: 'Schedules', icon: <Schedule />, color: 'info' },
      '/haccp/alerts': { title: 'Alerts', icon: <Warning />, color: 'warning' },
      '/haccp/reports': { title: 'Reports', icon: <Assessment />, color: 'success' },
      '/haccp/dashboard': { title: 'Advanced Dashboard', icon: <Dashboard />, color: 'error' },
    };

    return routeMapping[path] || { title: 'HACCP', icon: <Science />, color: 'primary' };
  };

  const pathSegments = location.pathname.split('/').filter(Boolean);
  const currentPageInfo = getPageInfo(location.pathname);

  return (
    <Box sx={{ mb: 2 }}>
      <Breadcrumbs
        separator={<NavigateNext fontSize="small" />}
        aria-label="HACCP navigation breadcrumb"
      >
        {/* Home */}
        <Link
          underline="hover"
          color="inherit"
          onClick={() => navigate('/dashboard')}
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            cursor: 'pointer',
            '&:hover': { color: 'primary.main' }
          }}
        >
          <Home sx={{ mr: 0.5 }} fontSize="inherit" />
          Dashboard
        </Link>

        {/* HACCP Root */}
        {pathSegments.length > 1 ? (
          <Link
            underline="hover"
            color="inherit"
            onClick={() => navigate('/haccp')}
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              cursor: 'pointer',
              '&:hover': { color: 'primary.main' }
            }}
          >
            <Science sx={{ mr: 0.5 }} fontSize="inherit" />
            HACCP
          </Link>
        ) : (
          <Typography 
            color="text.primary" 
            sx={{ display: 'flex', alignItems: 'center' }}
          >
            <Science sx={{ mr: 0.5 }} fontSize="inherit" />
            HACCP
          </Typography>
        )}

        {/* Product Detail */}
        {pathSegments.includes('products') && pathSegments.length === 3 && (
          <Link
            underline="hover"
            color="inherit"
            onClick={() => navigate('/haccp')}
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              cursor: 'pointer',
              '&:hover': { color: 'primary.main' }
            }}
          >
            Products
          </Link>
        )}

        {/* Current Page */}
        {pathSegments.length > 1 && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography 
              color="text.primary" 
              sx={{ display: 'flex', alignItems: 'center', fontWeight: 'medium' }}
            >
              {currentPageInfo.icon}
              <span style={{ marginLeft: 4 }}>
                {customTitle || currentPageInfo.title}
              </span>
            </Typography>
            {productName && (
              <Chip 
                label={productName} 
                size="small" 
                color={currentPageInfo.color as any}
                variant="outlined"
              />
            )}
          </Box>
        )}
      </Breadcrumbs>
    </Box>
  );
};

export default HACCPBreadcrumbs;