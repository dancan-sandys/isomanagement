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
import RoleBasedRoute from './components/Auth/RoleBasedRoute';
import ProtectedRoute from './components/Auth/ProtectedRoute';

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
                      <Route path="/dashboard/analytics" element={
                        <ComingSoon 
                          title="Dashboard Analytics"
                          description="Advanced analytics and reporting features are coming soon."
                          parentPath="/dashboard"
                          parentTitle="Dashboard"
                        />
                      } />
                      <Route path="/dashboard/reports" element={
                        <ComingSoon 
                          title="Dashboard Reports"
                          description="Custom report generation is coming soon."
                          parentPath="/dashboard"
                          parentTitle="Dashboard"
                        />
                      } />
                      
                      {/* Document Control - All authenticated users */}
                      <Route path="/documents" element={<Documents />} />
                      
                      {/* HACCP System - QA and Production roles */}
                      <Route path="/haccp" element={<HACCP />} />
                      <Route path="/haccp/ccp" element={
                        <ComingSoon 
                          title="CCP Management"
                          description="Advanced CCP management features are coming soon. Basic CCP information is available in the main HACCP section."
                          parentPath="/haccp"
                          parentTitle="HACCP"
                        />
                      } />
                      <Route path="/haccp/hazards" element={
                        <ComingSoon 
                          title="Hazard Analysis"
                          description="Detailed hazard analysis tools are coming soon. Basic hazard information is available in the main HACCP section."
                          parentPath="/haccp"
                          parentTitle="HACCP"
                        />
                      } />
                      <Route path="/haccp/limits" element={
                        <ComingSoon 
                          title="Critical Limits"
                          description="Critical limit management is coming soon."
                          parentPath="/haccp"
                          parentTitle="HACCP"
                        />
                      } />
                      <Route path="/haccp/monitoring" element={
                        <ComingSoon 
                          title="Monitoring Systems"
                          description="Monitoring system management is coming soon."
                          parentPath="/haccp"
                          parentTitle="HACCP"
                        />
                      } />
                      <Route path="/haccp/corrective" element={
                        <ComingSoon 
                          title="Corrective Actions"
                          description="Corrective action management is coming soon."
                          parentPath="/haccp"
                          parentTitle="HACCP"
                        />
                      } />
                      
                      {/* PRP Programs - Production and Maintenance roles */}
                      <Route path="/prp" element={<PRP />} />
                      <Route path="/prp/cleaning" element={
                        <ComingSoon 
                          title="Cleaning & Sanitation"
                          description="Detailed cleaning and sanitation management is coming soon. Basic PRP information is available in the main PRP section."
                          parentPath="/prp"
                          parentTitle="PRP Programs"
                        />
                      } />
                      <Route path="/prp/maintenance" element={
                        <ComingSoon 
                          title="Maintenance Management"
                          description="Equipment maintenance tracking is coming soon. Basic PRP information is available in the main PRP section."
                          parentPath="/prp"
                          parentTitle="PRP Programs"
                        />
                      } />
                      <Route path="/prp/pest-control" element={
                        <ComingSoon 
                          title="Pest Control"
                          description="Pest control management is coming soon."
                          parentPath="/prp"
                          parentTitle="PRP Programs"
                        />
                      } />
                      <Route path="/prp/hygiene" element={
                        <ComingSoon 
                          title="Personal Hygiene"
                          description="Personal hygiene management is coming soon."
                          parentPath="/prp"
                          parentTitle="PRP Programs"
                        />
                      } />
                      <Route path="/prp/infrastructure" element={
                        <ComingSoon 
                          title="Infrastructure"
                          description="Infrastructure management is coming soon."
                          parentPath="/prp"
                          parentTitle="PRP Programs"
                        />
                      } />
                      
                      {/* Supplier Management - QA and Management roles */}
                      <Route path="/suppliers" element={<Suppliers />} />
                      <Route path="/suppliers/evaluation" element={
                        <ComingSoon 
                          title="Supplier Evaluation"
                          description="Advanced supplier evaluation tools are coming soon. Basic supplier information is available in the main Suppliers section."
                          parentPath="/suppliers"
                          parentTitle="Suppliers"
                        />
                      } />
                      <Route path="/suppliers/approved" element={
                        <ComingSoon 
                          title="Approved Suppliers"
                          description="Approved supplier management is coming soon."
                          parentPath="/suppliers"
                          parentTitle="Suppliers"
                        />
                      } />
                      <Route path="/suppliers/audits" element={
                        <ComingSoon 
                          title="Supplier Audits"
                          description="Supplier audit management is coming soon."
                          parentPath="/suppliers"
                          parentTitle="Suppliers"
                        />
                      } />
                      <Route path="/suppliers/metrics" element={
                        <ComingSoon 
                          title="Performance Metrics"
                          description="Supplier performance metrics are coming soon."
                          parentPath="/suppliers"
                          parentTitle="Suppliers"
                        />
                      } />
                      
                      {/* Traceability - Production and QA roles */}
                      <Route path="/traceability" element={<Traceability />} />
                      <Route path="/traceability/chain" element={
                        <ComingSoon 
                          title="Traceability Chain"
                          description="Detailed traceability chain visualization is coming soon. Basic traceability information is available in the main Traceability section."
                          parentPath="/traceability"
                          parentTitle="Traceability"
                        />
                      } />
                      <Route path="/traceability/recall" element={
                        <ComingSoon 
                          title="Product Recall"
                          description="Product recall management is coming soon."
                          parentPath="/traceability"
                          parentTitle="Traceability"
                        />
                      } />
                      <Route path="/traceability/lots" element={
                        <ComingSoon 
                          title="Lot Tracking"
                          description="Lot tracking management is coming soon."
                          parentPath="/traceability"
                          parentTitle="Traceability"
                        />
                      } />
                      <Route path="/traceability/reports" element={
                        <ComingSoon 
                          title="Traceability Reports"
                          description="Traceability reporting is coming soon."
                          parentPath="/traceability"
                          parentTitle="Traceability"
                        />
                      } />
                      
                      {/* Audit Management - QA and Auditor roles */}
                      <Route path="/audits/internal" element={
                        <ComingSoon 
                          title="Internal Audits"
                          description="Internal audit management is coming soon."
                        />
                      } />
                      <Route path="/audits/external" element={
                        <ComingSoon 
                          title="External Audits"
                          description="External audit management is coming soon."
                        />
                      } />
                      <Route path="/audits/schedule" element={
                        <ComingSoon 
                          title="Audit Schedule"
                          description="Audit scheduling is coming soon."
                        />
                      } />
                      <Route path="/audits/findings" element={
                        <ComingSoon 
                          title="Findings & NCs"
                          description="Audit findings management is coming soon."
                        />
                      } />
                      <Route path="/audits/reports" element={
                        <ComingSoon 
                          title="Audit Reports"
                          description="Audit reporting is coming soon."
                        />
                      } />
                      
                      {/* Training & Competence - QA and HR roles */}
                      <Route path="/training/programs" element={
                        <ComingSoon 
                          title="Training Programs"
                          description="Training program management is coming soon."
                        />
                      } />
                      <Route path="/training/assessment" element={
                        <ComingSoon 
                          title="Competence Assessment"
                          description="Competence assessment tools are coming soon."
                        />
                      } />
                      <Route path="/training/records" element={
                        <ComingSoon 
                          title="Training Records"
                          description="Training record management is coming soon."
                        />
                      } />
                      <Route path="/training/certification" element={
                        <ComingSoon 
                          title="Certification Tracking"
                          description="Certification tracking is coming soon."
                        />
                      } />
                      <Route path="/training/calendar" element={
                        <ComingSoon 
                          title="Training Calendar"
                          description="Training calendar management is coming soon."
                        />
                      } />
                      
                      {/* Maintenance - Maintenance roles */}
                      <Route path="/maintenance/equipment" element={
                        <ComingSoon 
                          title="Equipment Register"
                          description="Equipment register management is coming soon."
                        />
                      } />
                      <Route path="/maintenance/preventive" element={
                        <ComingSoon 
                          title="Preventive Maintenance"
                          description="Preventive maintenance management is coming soon."
                        />
                      } />
                      <Route path="/maintenance/work-orders" element={
                        <ComingSoon 
                          title="Work Orders"
                          description="Work order management is coming soon."
                        />
                      } />
                      <Route path="/maintenance/calibration" element={
                        <ComingSoon 
                          title="Calibration"
                          description="Calibration management is coming soon."
                        />
                      } />
                      <Route path="/maintenance/history" element={
                        <ComingSoon 
                          title="Maintenance History"
                          description="Maintenance history tracking is coming soon."
                        />
                      } />
                      
                      {/* Inventory Management - Production and Warehouse roles */}
                      <Route path="/inventory/materials" element={
                        <ComingSoon 
                          title="Raw Materials"
                          description="Raw material management is coming soon."
                        />
                      } />
                      <Route path="/inventory/products" element={
                        <ComingSoon 
                          title="Finished Products"
                          description="Finished product management is coming soon."
                        />
                      } />
                      <Route path="/inventory/stock" element={
                        <ComingSoon 
                          title="Stock Levels"
                          description="Stock level management is coming soon."
                        />
                      } />
                      <Route path="/inventory/counts" element={
                        <ComingSoon 
                          title="Inventory Counts"
                          description="Inventory count management is coming soon."
                        />
                      } />
                      <Route path="/inventory/reports" element={
                        <ComingSoon 
                          title="Inventory Reports"
                          description="Inventory reporting is coming soon."
                        />
                      } />
                      
                      {/* Compliance - QA and Compliance roles */}
                      <Route path="/compliance/regulatory" element={
                        <ComingSoon 
                          title="Regulatory Requirements"
                          description="Regulatory requirement management is coming soon."
                        />
                      } />
                      <Route path="/compliance/monitoring" element={
                        <ComingSoon 
                          title="Compliance Monitoring"
                          description="Compliance monitoring tools are coming soon."
                        />
                      } />
                      <Route path="/compliance/reports" element={
                        <ComingSoon 
                          title="Compliance Reports"
                          description="Compliance reporting is coming soon."
                        />
                      } />
                      <Route path="/compliance/updates" element={
                        <ComingSoon 
                          title="Regulatory Updates"
                          description="Regulatory update management is coming soon."
                        />
                      } />
                      
                      {/* User Management - System Administrators and QA Managers only */}
                      <Route path="/users" element={<Users />} />
                      <Route path="/rbac" element={<RBAC />} />
                      <Route path="/users/groups" element={
                        <ComingSoon 
                          title="User Groups"
                          description="User group management is coming soon."
                          parentPath="/users"
                          parentTitle="Users"
                        />
                      } />
                      <Route path="/users/logs" element={
                        <ComingSoon 
                          title="Access Logs"
                          description="Access log management is coming soon."
                          parentPath="/users"
                          parentTitle="Users"
                        />
                      } />
                      
                      {/* System Settings - System Administrators only */}
                      <Route path="/settings" element={<Settings />} />
                      <Route path="/settings/config" element={
                        <ComingSoon 
                          title="System Configuration"
                          description="System configuration management is coming soon."
                          parentPath="/settings"
                          parentTitle="Settings"
                        />
                      } />
                      <Route path="/settings/backup" element={
                        <ComingSoon 
                          title="Backup & Restore"
                          description="Backup and restore functionality is coming soon."
                          parentPath="/settings"
                          parentTitle="Settings"
                        />
                      } />
                      <Route path="/settings/logs" element={
                        <ComingSoon 
                          title="System Logs"
                          description="System log management is coming soon."
                          parentPath="/settings"
                          parentTitle="Settings"
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