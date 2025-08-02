import React, { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from './store';
import { getCurrentUser } from './store/slices/authSlice';

import Layout from './components/Layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import HACCP from './pages/HACCP';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import PRP from './pages/PRP';
import Suppliers from './pages/Suppliers';
import Traceability from './pages/Traceability';

function App() {
  const dispatch = useDispatch<AppDispatch>();
  const { token, isAuthenticated } = useSelector((state: RootState) => state.auth);

  // Initialize authentication check on app load
  useEffect(() => {
    console.log('App.tsx - useEffect - token:', !!token, 'isAuthenticated:', isAuthenticated);
    // Only check authentication if we have a token and are not already authenticated
    // This prevents duplicate calls that can cause loading state issues
    if (token && !isAuthenticated) {
      console.log('App.tsx - dispatching getCurrentUser');
      dispatch(getCurrentUser());
    }
  }, [dispatch, token, isAuthenticated]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/documents" element={<Documents />} />
                  <Route path="/haccp" element={<HACCP />} />
                              <Route path="/prp" element={<PRP />} />
            <Route path="/suppliers" element={<Suppliers />} />
            <Route path="/traceability" element={<Traceability />} />
                  {/* Add more routes here as we implement them */}
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Box>
  );
}

export default App; 