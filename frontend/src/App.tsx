import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout/Layout';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import HACCP from './pages/HACCP';
import HACCPProductDetail from './pages/HACCPProductDetail';
import PRP from './pages/PRP';
import Suppliers from './pages/Suppliers';
import SuppliersMetrics from './pages/SuppliersMetrics';
import Traceability from './pages/Traceability';
import NonConformance from './pages/NonConformance';
import NonConformanceDetail from './pages/NonConformanceDetail';
import CAPAList from './pages/CAPAList';
import CAPADetail from './pages/CAPADetail';
import TrainingPrograms from './pages/TrainingPrograms';
import TrainingProgramDetail from './pages/TrainingProgramDetail';
import TrainingMatrix from './pages/TrainingMatrix';
import Audits from './pages/Audits';
import AuditDetail from './pages/AuditDetail';
import Users from './pages/Users';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import RBAC from './pages/RBAC';
import ComingSoon from './components/UI/ComingSoon';
import EquipmentPage from './pages/Equipment';
import RoleBasedRoute from './components/Auth/RoleBasedRoute';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import DashboardAnalytics from './pages/DashboardAnalytics';
import DashboardReports from './pages/DashboardReports';
import RiskRegister from './pages/RiskRegister';
import OpportunitiesRegister from './pages/OpportunitiesRegister';
import OpportunityDetail from './pages/OpportunityDetail';
import RiskDetail from './pages/RiskDetail';

function App() {
  return (
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
                      <Route path="/dashboard/analytics" element={<DashboardAnalytics />} />
                      <Route path="/dashboard/reports" element={<DashboardReports />} />
                      
                      {/* Document Control - All authenticated users */}
                      <Route path="/documents" element={<Documents />} />
                      
                      {/* HACCP System - QA and Production roles */}
                      <Route path="/haccp" element={<HACCP />} />
                      <Route path="/haccp/products/:id" element={<HACCPProductDetail />} />
                      <Route path="/haccp/ccp" element={<Navigate to="/haccp" replace />} />
                      <Route path="/haccp/hazards" element={<Navigate to="/haccp" replace />} />
                      <Route path="/haccp/limits" element={<Navigate to="/haccp" replace />} />
                      <Route path="/haccp/monitoring" element={<Navigate to="/haccp" replace />} />
                      <Route path="/haccp/corrective" element={<Navigate to="/haccp" replace />} />
                      
                      {/* PRP Programs - Production and Maintenance roles */}
                      <Route path="/prp" element={<PRP />} />
                      <Route path="/prp/cleaning" element={<Navigate to="/prp?category=cleaning_sanitation&tab=programs" replace />} />
                      <Route path="/prp/maintenance" element={<Navigate to="/prp?category=maintenance&tab=programs" replace />} />
                      <Route path="/prp/pest-control" element={<Navigate to="/prp?category=pest_control&tab=programs" replace />} />
                      <Route path="/prp/hygiene" element={<Navigate to="/prp?category=staff_hygiene&tab=programs" replace />} />
                      <Route path="/prp/infrastructure" element={<Navigate to="/prp?category=infrastructure&tab=programs" replace />} />
                      
                      {/* Supplier Management - QA and Management roles */}
                      <Route path="/suppliers" element={<Suppliers />} />
                      <Route path="/suppliers/evaluation" element={<Navigate to="/suppliers?tab=3" replace />} />
                      <Route path="/suppliers/approved" element={<Navigate to="/suppliers?tab=1" replace />} />
                      <Route path="/suppliers/audits" element={
                        <ComingSoon 
                          title="Supplier Audits"
                          description="Supplier audit management is coming soon."
                          parentPath="/suppliers"
                          parentTitle="Suppliers"
                        />
                      } />
                      <Route path="/suppliers/metrics" element={<SuppliersMetrics />} />
                      
                      {/* Traceability - Production and QA roles */}
                      <Route path="/traceability" element={<Traceability />} />
                       
                       {/* Non-Conformance & CAPA */}
                       <Route path="/nonconformance" element={<NonConformance />} />
                       <Route path="/nonconformance/:id" element={<NonConformanceDetail />} />
                       <Route path="/nonconformance/capas" element={<CAPAList />} />
                       <Route path="/nonconformance/capas/:id" element={<CAPADetail />} />
                       {/* Training & Competence */}
                       <Route path="/training" element={<TrainingPrograms />} />
        <Route path="/training/programs/:id" element={<TrainingProgramDetail />} />
        <Route path="/training/matrix" element={<TrainingMatrix />} />
                      <Route path="/traceability/chain" element={<Navigate to="/traceability?tab=1" replace />} />
                      <Route path="/traceability/recall" element={<Navigate to="/traceability?tab=2" replace />} />
                      <Route path="/traceability/lots" element={<Navigate to="/traceability?tab=1" replace />} />
                      <Route path="/traceability/reports" element={<Navigate to="/traceability?tab=3" replace />} />
                      
                      {/* Audit Management - QA and Auditor roles */}
                      <Route path="/audits/internal" element={<Audits />} />
                      <Route path="/audits/external" element={<Audits />} />
                      <Route path="/audits/:id" element={<AuditDetail />} />
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
                      <Route path="/maintenance/equipment" element={<EquipmentPage />} />
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
                      <Route path="/compliance/risks" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Compliance Officer", "System Administrator"]} component={RiskRegister} />} />
                      <Route path="/compliance/opportunities" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Compliance Officer", "System Administrator"]} component={OpportunitiesRegister} />} />
                      <Route path="/compliance/opportunity/:id" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Compliance Officer", "System Administrator"]} component={OpportunityDetail} />} />
                      <Route path="/compliance/risk/:id" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Compliance Officer", "System Administrator"]} component={RiskDetail} />} />
                      <Route path="/compliance/regulatory" element={
                        <ComingSoon 
                          title="Regulatory Requirements"
                          description="Regulatory requirement management is coming soon."
                        />
                      } />
                      <Route path="/compliance/risk" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Compliance Officer", "System Administrator"]} component={RiskRegister} />} />
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
                      <Route path="/users" element={<RoleBasedRoute allowedRoles={["System Administrator", "QA Manager"]} component={Users} />} />
                      <Route path="/rbac" element={<RoleBasedRoute allowedRoles={["System Administrator", "QA Manager"]} component={RBAC} />} />
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
                      <Route path="/settings" element={<RoleBasedRoute allowedRoles={["System Administrator"]} component={Settings} />} />
                      <Route path="/settings/config" element={<Navigate to="/settings?tab=settings" replace />} />
                      <Route path="/settings/backup" element={<Navigate to="/settings?tab=system" replace />} />
                      <Route path="/settings/logs" element={<Navigate to="/settings?tab=system" replace />} />
                      
                      {/* Profile - All authenticated users */}
                      <Route path="/profile" element={<Profile />} />
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