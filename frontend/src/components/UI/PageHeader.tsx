import React from 'react';
import {
  Box,
  Typography,
  Breadcrumbs,
  Link,
  Button,
  Stack,
  Divider,
  Chip,
} from '@mui/material';
import { NavigateNext, Add, Refresh, Download } from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';

interface BreadcrumbItem {
  label: string;
  path?: string;
}

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
  status?: {
    type: 'compliant' | 'nonConformance' | 'pending' | 'warning' | 'info';
    label: string;
  };
  showRefresh?: boolean;
  showAdd?: boolean;
  showExport?: boolean;
  onRefresh?: () => void;
  onAdd?: () => void;
  onExport?: () => void;
}

const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  breadcrumbs = [],
  actions,
  status,
  showRefresh = false,
  showAdd = false,
  showExport = false,
  onRefresh,
  onAdd,
  onExport,
}) => {
  const defaultActions = (
    <Stack direction="row" spacing={2}>
      {showRefresh && (
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={onRefresh}
          size="small"
          sx={{
            borderColor: 'divider',
            backgroundColor: 'rgba(30, 64, 175, 0.02)',
            '&:hover': {
              borderColor: 'text.disabled',
              backgroundColor: 'rgba(30, 64, 175, 0.06)'
            },
          }}
        >
          Refresh
        </Button>
      )}
      {showAdd && (
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={onAdd}
          size="small"
          sx={{
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            '&:hover': {
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
            }
          }}
        >
          Add New
        </Button>
      )}
      {showExport && (
        <Button
          variant="outlined"
          startIcon={<Download />}
          onClick={onExport}
          size="small"
          sx={{
            borderColor: 'divider',
            '&:hover': {
              borderColor: 'text.disabled'
            }
          }}
        >
          Export
        </Button>
      )}
    </Stack>
  );

  return (
    <Box sx={{ mb: 4 }}>
      {/* Breadcrumbs */}
      {breadcrumbs.length > 0 && (
        <Breadcrumbs
          separator={<NavigateNext fontSize="small" />}
          sx={{ mb: 2 }}
        >
          {breadcrumbs.map((item, index) => (
            <Link
              key={index}
              component={RouterLink}
              to={item.path || '#'}
              color={index === breadcrumbs.length - 1 ? 'text.primary' : 'inherit'}
              underline="hover"
              sx={{
                fontSize: '0.875rem',
                fontWeight: index === breadcrumbs.length - 1 ? 600 : 400,
              }}
            >
              {item.label}
            </Link>
          ))}
        </Breadcrumbs>
      )}

      {/* Header Content */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
              {title}
            </Typography>
            {status && (
              <Chip
                label={status.label}
                color={status.type === 'compliant' ? 'success' : 
                       status.type === 'nonConformance' ? 'error' :
                       status.type === 'pending' ? 'warning' : 'info'}
                size="small"
                sx={{
                  fontWeight: 600,
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                }}
              />
            )}
          </Box>
          {subtitle && (
            <Typography variant="body1" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        
        {/* Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {actions || defaultActions}
        </Box>
      </Box>

      <Divider sx={{ mt: 3 }} />
    </Box>
  );
};

export default PageHeader; 