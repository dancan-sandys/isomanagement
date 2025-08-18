import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  Avatar,
} from '@mui/material';
import { LockOutlined } from '@mui/icons-material';
import { AppDispatch, RootState } from '../store';
import { login, clearError } from '../store/slices/authSlice';

const Login: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { isLoading, error, isAuthenticated } = useSelector((state: RootState) => state.auth);
  const [errorHint, setErrorHint] = useState<string | null>(null);

  // Debug logging
  console.log('Login component - isLoading:', isLoading, 'isAuthenticated:', isAuthenticated);

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [formErrors, setFormErrors] = useState({
    username: '',
    password: '',
  });
  const [showSuccess, setShowSuccess] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  // Clear error when component mounts
  useEffect(() => {
    dispatch(clearError());
  }, [dispatch]);

  // Clear success message when authentication state changes
  useEffect(() => {
    if (isAuthenticated) {
      setShowSuccess(false);
    }
  }, [isAuthenticated]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (formErrors[name as keyof typeof formErrors]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validateForm = () => {
    const errors = {
      username: '',
      password: '',
    };

    if (!formData.username.trim()) {
      errors.username = 'Username is required';
    }

    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    setFormErrors(errors);
    return !errors.username && !errors.password;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('Login form submitted with:', { username: formData.username, password: '***' });
    
    if (!validateForm()) {
      console.log('Form validation failed');
      return;
    }

    try {
      console.log('Dispatching login action...');
      const result = await dispatch(login({
        username: formData.username,
        password: formData.password,
      }) as any);
      
      console.log('Login result:', result);
      
      // Check if login was successful
      if (login.fulfilled.match(result)) {
        console.log('Login successful!');
        // Show success message briefly
        setShowSuccess(true);
        // Clear form data on successful login
        setFormData({
          username: '',
          password: '',
        });
        // Navigation will be handled by useEffect when isAuthenticated changes
      } else if (login.rejected.match(result)) {
        console.log('Login rejected:', result.error);
        // Ensure error is a string
        const errorMessage = typeof result.error === 'string' ? result.error : 'Login failed';
        console.log('Error message:', errorMessage);
        // Map backend messages for password policy/lockout/expiry hints
        const normalized = (errorMessage || '').toLowerCase();
        if (normalized.includes('locked') || normalized.includes('lockout')) {
          setErrorHint('Account locked due to multiple failed attempts. Please try again later or contact an administrator.');
        } else if (normalized.includes('expired')) {
          setErrorHint('Your password has expired. Please reset your password or contact support.');
        } else if (normalized.includes('invalid credentials')) {
          setErrorHint('Invalid username or password. Passwords are case sensitive and must meet the security policy.');
        } else {
          setErrorHint(null);
        }
      }
    } catch (error) {
      // Error is handled by the Redux slice
      console.error('Login error:', error);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <Avatar sx={{ m: 1, bgcolor: 'primary.main' }}>
            <LockOutlined />
          </Avatar>
          
          <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
                          Compli FSMS Login
          </Typography>

          {(error || errorHint) && (
            <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
              {typeof error === 'string' ? error : 'An error occurred during login'}
              {errorHint ? (
                <>
                  <br />
                  <Typography variant="caption" color="inherit">{errorHint}</Typography>
                </>
              ) : null}
            </Alert>
          )}

          {showSuccess && (
            <Alert severity="success" sx={{ width: '100%', mb: 2 }}>
              Login successful! Redirecting...
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus
              value={formData.username}
              onChange={handleInputChange}
              error={!!formErrors.username}
              helperText={formErrors.username}
              disabled={isLoading}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleInputChange}
              error={!!formErrors.password}
              helperText={formErrors.password}
              disabled={isLoading}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading}
            >
              {isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Sign In'
              )}
            </Button>
          </Box>

          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
            Demo Credentials:
            <br />
            Username: admin
            <br />
            Password: admin123
          </Typography>

          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Don't have an account?{' '}
              <Link to="/signup" style={{ color: 'inherit', textDecoration: 'none' }}>
                Sign up here
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login; 