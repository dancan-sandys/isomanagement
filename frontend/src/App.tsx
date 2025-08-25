import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import './styles/compact-layout.css'; // Import compact layout styles
import './utils/resizeObserverFix'; // Fix ResizeObserver loop errors
import Layout from './components/Layout/Layout';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import HACCP from './pages/HACCP';
import HACCPProductDetail from './pages/HACCPProductDetail';
import HACCPMonitoring from './pages/HACCPMonitoring';
import HACCPVerification from './pages/HACCPVerification';
import HACCPSchedules from './pages/HACCPSchedules';
import HACCPAlerts from './pages/HACCPAlerts';
import HACCPReports from './pages/HACCPReports';
import HACCPDashboard from './pages/HACCPDashboard';
import PRP from './pages/PRP';
import PRPProgramDetail from './pages/PRPProgramDetail';
import Suppliers from './pages/Suppliers';
import Traceability from './pages/Traceability';
import NonConformance from './pages/NonConformance';
import NonConformanceDetail from './pages/NonConformanceDetail';
import CAPAList from './pages/CAPAList';
import CAPADetail from './pages/CAPADetail';
import TrainingPrograms from './pages/TrainingPrograms';
import TrainingProgramDetail from './pages/TrainingProgramDetail';
import TrainingMatrix from './pages/TrainingMatrix';
import TrainingPolicies from './pages/TrainingPolicies';
import RiskThresholds from './pages/RiskThresholds';
import Audits from './pages/Audits';
import AuditSchedule from './pages/AuditSchedule';
import AuditFindings from './pages/AuditFindings';
import AuditReports from './pages/AuditReports';
import AuditDetail from './pages/AuditDetail';
import Users from './pages/Users';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import RBAC from './pages/RBAC';
import EquipmentPage from './pages/Equipment';
import EquipmentDetailsPage from './pages/EquipmentDetails';
import ComplaintsPage from './pages/Complaints';
import ComplaintDetail from './pages/ComplaintDetail';
import RoleBasedRoute from './components/Auth/RoleBasedRoute';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import DashboardAnalytics from './pages/DashboardAnalytics';
import ObjectivesPage from './pages/Objectives';
import DashboardReports from './pages/DashboardReports';
import RiskRegister from './pages/RiskRegister';
import OpportunitiesRegister from './pages/OpportunitiesRegister';
import OpportunityDetail from './pages/OpportunityDetail';
import ManagementReviews from './pages/ManagementReviews';
import ManagementReviewDetail from './pages/ManagementReviewDetail';
import ManagementReviewAnalytics from './pages/ManagementReviewAnalytics';
import ManagementReviewActions from './pages/ManagementReviewActions';
import ManagementReviewCalendar from './pages/ManagementReviewCalendar';
import ManagementReviewTemplates from './pages/ManagementReviewTemplates';
import RiskDetail from './pages/RiskDetail';
import AllergenLabel from './pages/AllergenLabel';
import AdvancedReporting from './pages/AdvancedReporting';
import AdvancedSecurity from './pages/AdvancedSecurity';
import HiddenDemoTools from './pages/HiddenDemoTools';
import ProductionPage from './pages/Production';
import ProductionProcessDetail from './pages/ProductionProcessDetail';
import Analytics from './pages/Analytics';
import ActionsLog from "./pages/ActionsLog";

function App() {
  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      minHeight: '100vh',
      // Compact spacing for better space utilization
      '& .MuiContainer-root': {
        paddingLeft: 2,
        paddingRight: 2,
      },
      '& .MuiGrid-container': {
        margin: 0,
      },
      '& .MuiCard-root': {
        marginBottom: 1,
      },
    }}>
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
                      <Route path="/objectives" element={<ObjectivesPage />} />
                      <Route path="/objectives/dashboard" element={<ObjectivesPage />} />
                      <Route path="/objectives/progress" element={<ObjectivesPage />} />
                      <Route path="/production" element={<ProductionPage />} />
                      <Route path="/production/processes/:id" element={<ProductionProcessDetail />} />
                      <Route path="/production/monitoring" element={<ProductionPage />} />
                      <Route path="/production/yield" element={<ProductionPage />} />
                      
                      {/* Document Control - All authenticated users */}
                      <Route path="/documents" element={<Documents />} />
                      
                      {/* HACCP System - QA and Production roles */}
                      <Route path="/haccp" element={<HACCP />} />
                      <Route path="/haccp/products/:id" element={<HACCPProductDetail />} />
                      <Route path="/haccp/monitoring" element={<HACCPMonitoring />} />
                      <Route path="/haccp/verification" element={<HACCPVerification />} />
                      <Route path="/haccp/schedules" element={<HACCPSchedules />} />
                      <Route path="/haccp/alerts" element={<HACCPAlerts />} />
                      <Route path="/haccp/reports" element={<HACCPReports />} />
                      <Route path="/haccp/dashboard" element={<HACCPDashboard />} />
                      <Route path="/haccp/ccp" element={<Navigate to="/haccp" replace />} />
                      <Route path="/haccp/hazards" element={<Navigate to="/haccp" replace />} />
                      <Route path="/haccp/limits" element={<Navigate to="/haccp" replace />} />
                      <Route path="/haccp/corrective" element={<Navigate to="/haccp" replace />} />
                      
                      {/* PRP Programs - Production and Maintenance roles */}
                      <Route path="/prp" element={<PRP />} />
                      <Route path="/prp/programs/:id" element={<PRPProgramDetail />} />
                      <Route path="/prp/cleaning" element={<Navigate to="/prp?category=cleaning_sanitation&tab=programs" replace />} />
                      <Route path="/prp/maintenance" element={<Navigate to="/prp?category=maintenance&tab=programs" replace />} />
                      <Route path="/prp/pest-control" element={<Navigate to="/prp?category=pest_control&tab=programs" replace />} />
                      <Route path="/prp/hygiene" element={<Navigate to="/prp?category=staff_hygiene&tab=programs" replace />} />
                      <Route path="/prp/infrastructure" element={<Navigate to="/prp?category=infrastructure&tab=programs" replace />} />
                      
                      {/* Supplier Management - QA and Management roles */}
                      <Route path="/suppliers" element={<Suppliers />} />
                      <Route path="/suppliers/evaluation" element={<Navigate to="/suppliers?tab=3" replace />} />
                      <Route path="/suppliers/approved" element={<Navigate to="/suppliers?tab=1" replace />} />
                      <Route path="/suppliers/audits" element={<Navigate to="/audits?type=supplier" replace />} />
                      {/* Performance Metrics removed; consolidated into Dashboard */}
                      
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
                      <Route path="/training/policies" element={<RoleBasedRoute allowedRoles={["System Administrator", "QA Manager"]} component={TrainingPolicies} />} />
          <Route path="/haccp/risk-thresholds" element={<RoleBasedRoute allowedRoles={["System Administrator", "QA Manager", "HACCP Team Leader"]} component={RiskThresholds} />} />
                      <Route path="/traceability/chain" element={<Navigate to="/traceability?tab=1" replace />} />
                      <Route path="/traceability/recall" element={<Navigate to="/traceability?tab=2" replace />} />
                      <Route path="/traceability/lots" element={<Navigate to="/traceability?tab=1" replace />} />
                      <Route path="/traceability/reports" element={<Navigate to="/traceability?tab=3" replace />} />
                      
                      {/* Audit Management - QA and Auditor roles */}
                      <Route path="/audits" element={<Audits />} />
                      <Route path="/audits/internal" element={<Navigate to="/audits" replace />} />
                      <Route path="/audits/external" element={<Navigate to="/audits" replace />} />
                      <Route path="/audits/:id" element={<AuditDetail />} />
                      <Route path="/audits/schedule" element={<AuditSchedule />} />
                      <Route path="/audits/findings" element={<AuditFindings />} />
                      <Route path="/audits/reports" element={<AuditReports />} />
                      
                      {/* Training & Competence - QA and HR roles */}
                      <Route path="/training/programs" element={<Navigate to="/training" replace />} />
                      <Route path="/training/assessment" element={<Navigate to="/training?tab=assessment" replace />} />
                      <Route path="/training/records" element={<Navigate to="/training?tab=records" replace />} />
                      <Route path="/training/certification" element={<Navigate to="/training?tab=certification" replace />} />
                      <Route path="/training/calendar" element={<Navigate to="/training?tab=calendar" replace />} />
                      
                      {/* Maintenance - Maintenance roles */}
                      <Route path="/maintenance/equipment" element={<EquipmentPage />} />
                      <Route path="/maintenance/equipment/:id" element={<EquipmentDetailsPage />} />
                      <Route path="/maintenance/preventive" element={<Navigate to="/maintenance/equipment?tab=preventive" replace />} />
                      <Route path="/maintenance/work-orders" element={<Navigate to="/maintenance/equipment?tab=work-orders" replace />} />
                      <Route path="/maintenance/calibration" element={<Navigate to="/maintenance/equipment?tab=calibration" replace />} />
                      <Route path="/maintenance/history" element={<Navigate to="/maintenance/equipment?tab=history" replace />} />
                      
                      {/* Inventory Management - Production and Warehouse roles */}
                      <Route path="/inventory/materials" element={<Navigate to="/traceability?tab=materials" replace />} />
                      <Route path="/inventory/products" element={<Navigate to="/traceability?tab=products" replace />} />
                      <Route path="/inventory/stock" element={<Navigate to="/traceability?tab=stock" replace />} />
                      <Route path="/inventory/counts" element={<Navigate to="/traceability?tab=counts" replace />} />
                      <Route path="/inventory/reports" element={<Navigate to="/traceability?tab=reports" replace />} />
                      
                      {/* Complaints */}
                      <Route path="/complaints" element={<ComplaintsPage />} />
                      <Route path="/complaints/:id" element={<ComplaintDetail />} />

                      {/* Compliance - QA and Compliance roles */}
                      <Route path="/compliance/risks" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Compliance Officer", "System Administrator"]} component={RiskRegister} />} />
                      <Route path="/compliance/opportunities" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Compliance Officer", "System Administrator"]} component={OpportunitiesRegister} />} />
                      <Route path="/compliance/opportunity/:id" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Compliance Officer", "System Administrator"]} component={OpportunityDetail} />} />
                      <Route path="/management-reviews" element={<RoleBasedRoute allowedRoles={["QA Manager", "Compliance Officer", "System Administrator"]} component={ManagementReviews} />} />
                      <Route path="/management-reviews/:id" element={<RoleBasedRoute allowedRoles={["QA Manager", "Compliance Officer", "System Administrator"]} component={ManagementReviewDetail} />} />
                      <Route path="/management-reviews/analytics" element={<RoleBasedRoute allowedRoles={["QA Manager", "Compliance Officer", "System Administrator"]} component={ManagementReviewAnalytics} />} />
                      <Route path="/management-reviews/actions" element={<RoleBasedRoute allowedRoles={["QA Manager", "Compliance Officer", "System Administrator"]} component={ManagementReviewActions} />} />
                      <Route path="/management-reviews/calendar" element={<RoleBasedRoute allowedRoles={["QA Manager", "Compliance Officer", "System Administrator"]} component={ManagementReviewCalendar} />} />
                      <Route path="/management-reviews/templates" element={<RoleBasedRoute allowedRoles={["QA Manager", "Compliance Officer", "System Administrator"]} component={ManagementReviewTemplates} />} />
                      <Route path="/compliance/risk/:id" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Compliance Officer", "System Administrator"]} component={RiskDetail} />} />
                      <Route path="/compliance/allergen-label" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Compliance Officer", "System Administrator"]} component={AllergenLabel} />} />
                      <Route path="/compliance/regulatory" element={<Navigate to="/compliance/risks" replace />} />
                      <Route path="/compliance/risk" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Compliance Officer", "System Administrator"]} component={RiskRegister} />} />
                      <Route path="/compliance/monitoring" element={<Navigate to="/dashboard/analytics" replace />} />
                      <Route path="/compliance/reports" element={<Navigate to="/dashboard/reports" replace />} />
                      <Route path="/compliance/updates" element={<Navigate to="/documents?category=regulatory" replace />} />
                      
                      {/* Analytics & Reporting - QA and Production roles */}
                      <Route path="/analytics" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Production Manager", "System Administrator"]} component={Analytics} />} />
                      <Route path="/analytics/kpis" element={<Navigate to="/analytics?tab=1" replace />} />
                      <Route path="/analytics/dashboards" element={<Navigate to="/analytics?tab=2" replace />} />
                      <Route path="/analytics/reports" element={<Navigate to="/analytics?tab=3" replace />} />
                      <Route path="/analytics/trends" element={<Navigate to="/analytics?tab=4" replace />} />
                      <Route path="/actions-log" element={<RoleBasedRoute allowedRoles={["QA Manager", "QA Specialist", "Production Manager", "System Administrator"]} component={ActionsLog} />} />
                      <Route path="/actions-log/parties" element={<Navigate to="/actions-log?tab=1" replace />} />
                      <Route path="/actions-log/analysis" element={<Navigate to="/actions-log?tab=2" replace />} />
                      
                      {/* User Management - System Administrators and QA Managers only */}
                      <Route path="/users" element={<RoleBasedRoute allowedRoles={["System Administrator", "QA Manager"]} component={Users} />} />
                      <Route path="/rbac" element={<RoleBasedRoute allowedRoles={["System Administrator", "QA Manager"]} component={RBAC} />} />
                      <Route path="/users/groups" element={<Navigate to="/rbac" replace />} />
                      <Route path="/users/logs" element={<Navigate to="/settings?tab=logs" replace />} />
                      
                      {/* System Settings - System Administrators only */}
                      <Route path="/settings" element={<RoleBasedRoute allowedRoles={["System Administrator"]} component={Settings} />} />
                      <Route path="/settings/config" element={<Navigate to="/settings?tab=settings" replace />} />
                      <Route path="/settings/backup" element={<Navigate to="/settings?tab=system" replace />} />
                      <Route path="/settings/logs" element={<Navigate to="/settings?tab=system" replace />} />
                       {/* Hidden demo tools (no menu link). Admin only. */}
                       <Route path="/internal/demo-tools" element={<RoleBasedRoute allowedRoles={["System Administrator"]} component={HiddenDemoTools} />} />
                      
                      {/* Profile - All authenticated users */}
                      <Route path="/profile" element={<Profile />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
        {/* Advanced Features Routes */}
        <Route path="/advanced-reporting" element={<AdvancedReporting />} />
        <Route path="/advanced-security" element={<AdvancedSecurity />} />
      </Routes>
    </Box>
  );
}

export default App;