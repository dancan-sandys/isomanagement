import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { getCurrentUser, refreshAuth } from '../../store/slices/authSlice';
import { getToken, getRefreshToken, isTokenValid } from '../../utils/auth';

interface AuthProviderProps {
  children: React.ReactNode;
}

const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { isAuthenticated, isLoading } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = getToken();
      const refreshToken = getRefreshToken();

      if (token && isTokenValid(token)) {
        // Token is valid, try to get current user
        try {
          await dispatch(getCurrentUser()).unwrap();
        } catch (error) {
          // If getting user fails, try to refresh token
          if (refreshToken) {
            try {
              await dispatch(refreshAuth()).unwrap();
              // After successful refresh, get user info
              await dispatch(getCurrentUser()).unwrap();
            } catch (refreshError) {
              console.error('Token refresh failed:', refreshError);
            }
          }
        }
      } else if (refreshToken) {
        // Token is invalid but we have refresh token, try to refresh
        try {
          await dispatch(refreshAuth()).unwrap();
          await dispatch(getCurrentUser()).unwrap();
        } catch (error) {
          console.error('Token refresh failed:', error);
        }
      }
    };

    initializeAuth();
  }, [dispatch]);

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px'
      }}>
        Loading...
      </div>
    );
  }

  return <>{children}</>;
};

export default AuthProvider; 