import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import { Provider } from 'react-redux';
import { store } from './store';

import { ThemeProvider } from './theme/ThemeProvider';
import Layout from './components/Layout/Layout';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import HACCP from './pages/HACCP';
import PRP from './pages/PRP';
import Suppliers from './pages/Suppliers';
import Traceability from './pages/Traceability';
import Users from './pages/Users';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import RBAC from './pages/RBAC';
import ComingSoon from './components/UI/ComingSoon';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import RoleBasedRoute from './components/Auth/RoleBasedRoute';

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      {/* Dashboard - All authenticated users */}
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      
                      {/* Document Control - All authenticated users */}
                      <Route path="/documents" element={
                        <RoleBasedRoute 
                          allowedRoles={[
                            'System Administrator',
                            'QA Manager',
                            'QA Specialist',
                            'Production Manager',
                            'Production Operator',
                            'Maintenance Manager',
                            'Maintenance Technician',
                            'Auditor'
                          ]}
                          component={Documents}
                        />
                      } />
                      <Route path="/documents/versions" element={
                        <ComingSoon 
                          title="Document Version Control"
                          description="Advanced version control features are coming soon. Basic version management is available in the main Documents section."
                          parentPath="/documents"
                          parentTitle="Documents"
                        />
                      } />
                      <Route path="/documents/approval" element={
                        <ComingSoon 
                          title="Document Approval Workflow"
                          description="Enhanced approval workflow features are coming soon. Basic approval is available in the main Documents section."
                          parentPath="/documents"
                          parentTitle="Documents"
                        />
                      } />
                      
                      {/* User Management - System Administrators and QA Managers only */}
                      <Route path="/users" element={
                        <RoleBasedRoute 
                          allowedRoles={['System Administrator', 'QA Manager']}
                          component={Users}
                        />
                      } />
                      <Route path="/rbac" element={
                        <RoleBasedRoute 
                          allowedRoles={['System Administrator']}
                          component={RBAC}
                        />
                      } />
                      
                      {/* HACCP System - QA and Production roles */}
                      <Route path="/haccp" element={
                        <RoleBasedRoute 
                          allowedRoles={[
                            'System Administrator',
                            'QA Manager',
                            'QA Specialist',
                            'Production Manager',
                            'Production Operator',
                            'Maintenance Manager',
                            'Maintenance Technician',
                            'Auditor'
                          ]}
                          component={HACCP}
                        />
                      } />
                      <Route path="/haccp/ccp" element={
                        <RoleBasedRoute 
                          allowedRoles={['QA Manager', 'QA Specialist', 'Production Manager', 'System Administrator']}
                          component={
                            () => (
                              <ComingSoon 
                                title="CCP Management"
                                description="Advanced CCP management features are coming soon. Basic CCP information is available in the main HACCP section."
                                parentPath="/haccp"
                                parentTitle="HACCP"
                              />
                            )
                          }
                        />
                      } />
                      <Route path="/haccp/hazards" element={
                        <RoleBasedRoute 
                          allowedRoles={['QA Manager', 'QA Specialist', 'Production Manager', 'System Administrator']}
                          component={
                            () => (
                              <ComingSoon 
                                title="Hazard Analysis"
                                description="Detailed hazard analysis tools are coming soon. Basic hazard information is available in the main HACCP section."
                                parentPath="/haccp"
                                parentTitle="HACCP"
                              />
                            )
                          }
                        />
                      } />
                      
                      {/* PRP Programs - Production and Maintenance roles */}
                      <Route path="/prp" element={
                        <RoleBasedRoute 
                          allowedRoles={['Production Manager', 'Production Operator', 'Maintenance', 'System Administrator']}
                          component={PRP}
                        />
                      } />
                      <Route path="/prp/cleaning" element={
                        <RoleBasedRoute 
                          allowedRoles={['Production Manager', 'Production Operator', 'Maintenance', 'System Administrator']}
                          component={
                            () => (
                              <ComingSoon 
                                title="Cleaning & Sanitation"
                                description="Detailed cleaning and sanitation management is coming soon. Basic PRP information is available in the main PRP section."
                                parentPath="/prp"
                                parentTitle="PRP Programs"
                              />
                            )
                          }
                        />
                      } />
                      <Route path="/prp/maintenance" element={
                        <RoleBasedRoute 
                          allowedRoles={['Production Manager', 'Production Operator', 'Maintenance', 'System Administrator']}
                          component={
                            () => (
                              <ComingSoon 
                                title="Maintenance Management"
                                description="Equipment maintenance tracking is coming soon. Basic PRP information is available in the main PRP section."
                                parentPath="/prp"
                                parentTitle="PRP Programs"
                              />
                            )
                          }
                        />
                      } />
                      
                      {/* Supplier Management - QA and Management roles */}
                      <Route path="/suppliers" element={
                        <RoleBasedRoute 
                          allowedRoles={['QA Manager', 'QA Specialist', 'Production Manager', 'System Administrator']}
                          component={Suppliers}
                        />
                      } />
                      <Route path="/suppliers/evaluation" element={
                        <RoleBasedRoute 
                          allowedRoles={['QA Manager', 'QA Specialist', 'Production Manager', 'System Administrator']}
                          component={
                            () => (
                              <ComingSoon 
                                title="Supplier Evaluation"
                                description="Advanced supplier evaluation tools are coming soon. Basic supplier information is available in the main Suppliers section."
                                parentPath="/suppliers"
                                parentTitle="Suppliers"
                              />
                            )
                          }
                        />
                      } />
                      
                      {/* Traceability - Production and QA roles */}
                      <Route path="/traceability" element={
                        <RoleBasedRoute 
                          allowedRoles={['Production Manager', 'Production Operator', 'QA Manager', 'QA Specialist', 'System Administrator']}
                          component={Traceability}
                        />
                      } />
                      <Route path="/traceability/chain" element={
                        <RoleBasedRoute 
                          allowedRoles={['Production Manager', 'Production Operator', 'QA Manager', 'QA Specialist', 'System Administrator']}
                          component={
                            () => (
                              <ComingSoon 
                                title="Traceability Chain"
                                description="Detailed traceability chain visualization is coming soon. Basic traceability information is available in the main Traceability section."
                                parentPath="/traceability"
                                parentTitle="Traceability"
                              />
                            )
                          }
                        />
                      } />
                      
                      {/* System Settings - System Administrators only */}
                      <Route path="/settings" element={
                        <RoleBasedRoute 
                          allowedRoles={['System Administrator']}
                          component={Settings}
                        />
                      } />
                      
                      {/* Profile - All authenticated users */}
                      <Route path="/profile" element={<Profile />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Box>
      </ThemeProvider>
    </Provider>
  );
}

export default App; 