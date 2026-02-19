import React from 'react';
import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { Box, Alert, Typography, Button } from '@mui/material';
import { Security, ArrowBack } from '@mui/icons-material';
import { RootState } from '../../store';
import { hasRole } from '../../store/slices/authSlice';

interface RoleBasedRouteProps {
  allowedRoles: string[];
  component: React.ComponentType<any> | (() => React.ReactElement);
}

const RoleBasedRoute: React.FC<RoleBasedRouteProps> = ({ allowedRoles, component: Component }) => {
  const { user } = useSelector((state: RootState) => state.auth);

  // Check if user has any of the allowed roles
  const hasRequiredRole = allowedRoles.some(role => hasRole(user, role));

  if (!hasRequiredRole) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Security sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
        <Typography variant="h4" gutterBottom color="error.main">
          Access Denied
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          You don't have permission to access this page. This feature requires one of the following roles:
        </Typography>
        
        <Alert severity="warning" sx={{ mb: 3, textAlign: 'left' }}>
          <Typography variant="body2">
            <strong>Required Roles:</strong>
          </Typography>
          <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
            {allowedRoles.map((role) => (
              <li key={role}>
                <Typography variant="body2">{role}</Typography>
              </li>
            ))}
          </ul>
          <Typography variant="body2" sx={{ mt: 1 }}>
            <strong>Your Role:</strong> {user?.role_name || 'Unknown'}
          </Typography>
        </Alert>

        <Button
          variant="contained"
          startIcon={<ArrowBack />}
          onClick={() => window.history.back()}
          sx={{ mr: 2 }}
        >
          Go Back
        </Button>
        <Button
          variant="outlined"
          onClick={() => window.location.href = '/'}
        >
          Go to Dashboard
        </Button>
      </Box>
    );
  }

  // Render the component if user has required role
  return <Component />;
};

export default RoleBasedRoute; 