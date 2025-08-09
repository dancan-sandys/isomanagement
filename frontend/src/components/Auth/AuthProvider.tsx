import React, { useEffect, useState } from 'react';
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
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const initializeAuth = async () => {
      console.log('🔐 AuthProvider: Initializing authentication...');
      const token = getToken();
      const refreshToken = getRefreshToken();
      
      console.log('🔐 AuthProvider: Token exists:', !!token);
      console.log('🔐 AuthProvider: Refresh token exists:', !!refreshToken);

      if (token && isTokenValid(token)) {
        console.log('🔐 AuthProvider: Token is valid, getting current user...');
        // Token is valid, try to get current user
        try {
          await dispatch(getCurrentUser()).unwrap();
          console.log('🔐 AuthProvider: Successfully got current user');
        } catch (error) {
          console.error('🔐 AuthProvider: Failed to get current user:', error);
          // If getting user fails, try to refresh token
          if (refreshToken) {
            try {
              console.log('🔐 AuthProvider: Trying to refresh token...');
              await dispatch(refreshAuth()).unwrap();
              // After successful refresh, get user info
              await dispatch(getCurrentUser()).unwrap();
              console.log('🔐 AuthProvider: Successfully refreshed token and got user');
            } catch (refreshError) {
              console.error('🔐 AuthProvider: Token refresh failed:', refreshError);
              // Clear invalid tokens
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
            }
          } else {
            // No refresh token, clear access token
            localStorage.removeItem('access_token');
          }
        }
      } else if (refreshToken) {
        console.log('🔐 AuthProvider: Token invalid but refresh token exists, trying to refresh...');
        // Token is invalid but we have refresh token, try to refresh
        try {
          await dispatch(refreshAuth()).unwrap();
          await dispatch(getCurrentUser()).unwrap();
          console.log('🔐 AuthProvider: Successfully refreshed token and got user');
        } catch (error) {
          console.error('🔐 AuthProvider: Token refresh failed:', error);
          // Clear invalid tokens
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      } else {
        console.log('🔐 AuthProvider: No valid tokens, clearing any invalid ones...');
        // No valid tokens, clear any invalid ones
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
      
      setIsInitialized(true);
      console.log('🔐 AuthProvider: Authentication initialization complete');
    };

    initializeAuth();
  }, [dispatch]);

  // Show loading spinner while checking authentication
  if (!isInitialized || isLoading) {
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