import {
  Dashboard,
  Description,
  Security,
  Assignment,
  LocalShipping,
  Timeline,
  People,
  Settings,
  Business,
  Assessment,
  School,
  Build,
  Inventory,
  Receipt,
  Report,
  VerifiedUser,
} from '@mui/icons-material';

// Navigation item interface
export interface NavigationItem {
  readonly text: string;
  readonly path: string;
  readonly icon?: React.ComponentType<any>;
  readonly badge?: number;
  readonly disabled?: boolean;
  readonly comingSoon?: boolean;
}

// Navigation section interface
export interface NavigationSection {
  readonly title: string;
  readonly icon: React.ComponentType<any>;
  readonly items: readonly NavigationItem[];
  readonly requiredRoles?: string[];
  readonly requiredPermissions?: string[];
  readonly order: number;
}

// Navigation configuration
export const NAVIGATION_CONFIG: Record<string, NavigationSection> = {
  dashboard: {
    title: 'Dashboard',
    icon: Dashboard,
    order: 1,
    items: [
      { text: 'Overview', path: '/dashboard' },
      { text: 'Analytics', path: '/dashboard/analytics', comingSoon: true },
      { text: 'Reports', path: '/dashboard/reports', comingSoon: true },
    ],
  },
  
  documents: {
    title: 'Document Control',
    icon: Description,
    order: 2,
    items: [
      { text: 'Document Register', path: '/documents' },
    ],
  },
  
  haccp: {
    title: 'HACCP System',
    icon: Security,
    order: 3,
    requiredRoles: ['QA Manager', 'QA Specialist', 'Production Manager', 'Production Operator', 'System Administrator'],
    items: [
      { text: 'HACCP Plans', path: '/haccp' },
      { text: 'CCP Management', path: '/haccp/ccp', comingSoon: true },
      { text: 'Hazard Analysis', path: '/haccp/hazards', comingSoon: true },
      { text: 'Critical Limits', path: '/haccp/limits', comingSoon: true },
      { text: 'Monitoring', path: '/haccp/monitoring', comingSoon: true },
      { text: 'Corrective Actions', path: '/haccp/corrective', comingSoon: true },
    ],
  },
  
  prp: {
    title: 'PRP Programs',
    icon: Assignment,
    order: 4,
    requiredRoles: ['Production Manager', 'Production Operator', 'Maintenance Manager', 'Maintenance Technician', 'System Administrator'],
    items: [
      { text: 'PRP Overview', path: '/prp' },
      { text: 'Cleaning & Sanitation', path: '/prp/cleaning', comingSoon: true },
      { text: 'Maintenance', path: '/prp/maintenance', comingSoon: true },
      { text: 'Pest Control', path: '/prp/pest-control', comingSoon: true },
      { text: 'Personal Hygiene', path: '/prp/hygiene', comingSoon: true },
      { text: 'Infrastructure', path: '/prp/infrastructure', comingSoon: true },
    ],
  },
  
  suppliers: {
    title: 'Supplier Management',
    icon: Business,
    order: 5,
    requiredRoles: ['QA Manager', 'QA Specialist', 'Production Manager', 'System Administrator'],
    items: [
      { text: 'Suppliers', path: '/suppliers' },
      { text: 'Supplier Evaluation', path: '/suppliers/evaluation', comingSoon: true },
      { text: 'Approved Suppliers', path: '/suppliers/approved', comingSoon: true },
      { text: 'Supplier Audits', path: '/suppliers/audits', comingSoon: true },
      { text: 'Performance Metrics', path: '/suppliers/metrics', comingSoon: true },
    ],
  },
  
  traceability: {
    title: 'Traceability',
    icon: Timeline,
    order: 6,
    requiredRoles: ['Production Manager', 'Production Operator', 'QA Manager', 'QA Specialist', 'System Administrator'],
    items: [
      { text: 'Batch Tracking', path: '/traceability' },
      { text: 'Traceability Chain', path: '/traceability/chain', comingSoon: true },
      { text: 'Product Recall', path: '/traceability/recall', comingSoon: true },
      { text: 'Lot Tracking', path: '/traceability/lots', comingSoon: true },
      { text: 'Traceability Reports', path: '/traceability/reports', comingSoon: true },
    ],
  },
  
  audits: {
    title: 'Audit Management',
    icon: Assessment,
    order: 7,
    requiredRoles: ['QA Manager', 'QA Specialist', 'Auditor', 'System Administrator'],
    items: [
      { text: 'Internal Audits', path: '/audits/internal', comingSoon: true },
      { text: 'External Audits', path: '/audits/external', comingSoon: true },
      { text: 'Audit Schedule', path: '/audits/schedule', comingSoon: true },
      { text: 'Findings & NCs', path: '/audits/findings', comingSoon: true },
      { text: 'Audit Reports', path: '/audits/reports', comingSoon: true },
    ],
  },
  
  training: {
    title: 'Training & Competence',
    icon: School,
    order: 8,
    requiredRoles: ['QA Manager', 'HR Manager', 'System Administrator'],
    items: [
      { text: 'Training Programs', path: '/training/programs', comingSoon: true },
      { text: 'Competence Assessment', path: '/training/assessment', comingSoon: true },
      { text: 'Training Records', path: '/training/records', comingSoon: true },
      { text: 'Certification Tracking', path: '/training/certification', comingSoon: true },
      { text: 'Training Calendar', path: '/training/calendar', comingSoon: true },
    ],
  },
  
  maintenance: {
    title: 'Maintenance',
    icon: Build,
    order: 9,
    requiredRoles: ['Maintenance Manager', 'Maintenance Technician', 'Production Manager', 'System Administrator'],
    items: [
      { text: 'Equipment Register', path: '/maintenance/equipment', comingSoon: true },
      { text: 'Preventive Maintenance', path: '/maintenance/preventive', comingSoon: true },
      { text: 'Work Orders', path: '/maintenance/work-orders', comingSoon: true },
      { text: 'Calibration', path: '/maintenance/calibration', comingSoon: true },
      { text: 'Maintenance History', path: '/maintenance/history', comingSoon: true },
    ],
  },
  
  inventory: {
    title: 'Inventory Management',
    icon: Inventory,
    order: 10,
    requiredRoles: ['Production Manager', 'Production Operator', 'Warehouse Manager', 'System Administrator'],
    items: [
      { text: 'Raw Materials', path: '/inventory/materials', comingSoon: true },
      { text: 'Finished Products', path: '/inventory/products', comingSoon: true },
      { text: 'Stock Levels', path: '/inventory/stock', comingSoon: true },
      { text: 'Inventory Counts', path: '/inventory/counts', comingSoon: true },
      { text: 'Inventory Reports', path: '/inventory/reports', comingSoon: true },
    ],
  },
  
  compliance: {
    title: 'Compliance',
    icon: VerifiedUser,
    order: 11,
    requiredRoles: ['QA Manager', 'QA Specialist', 'Compliance Officer', 'System Administrator'],
    items: [
      { text: 'Regulatory Requirements', path: '/compliance/regulatory', comingSoon: true },
      { text: 'Compliance Monitoring', path: '/compliance/monitoring', comingSoon: true },
      { text: 'Compliance Reports', path: '/compliance/reports', comingSoon: true },
      { text: 'Regulatory Updates', path: '/compliance/updates', comingSoon: true },
    ],
  },
  
  users: {
    title: 'User Management',
    icon: People,
    order: 12,
    requiredRoles: ['System Administrator', 'QA Manager'],
    items: [
      { text: 'Users', path: '/users' },
      { text: 'Roles & Permissions', path: '/rbac' },
      { text: 'User Groups', path: '/users/groups', comingSoon: true },
      { text: 'Access Logs', path: '/users/logs', comingSoon: true },
    ],
  },
  
  settings: {
    title: 'System Settings',
    icon: Settings,
    order: 13,
    requiredRoles: ['System Administrator'],
    items: [
      { text: 'Settings', path: '/settings' },
      { text: 'System Configuration', path: '/settings/config', comingSoon: true },
      { text: 'Backup & Restore', path: '/settings/backup', comingSoon: true },
      { text: 'System Logs', path: '/settings/logs', comingSoon: true },
    ],
  },
};

// Helper function to get navigation sections for a user
export const getNavigationForUser = (user: any): NavigationSection[] => {
  if (!user) return [];

  return Object.values(NAVIGATION_CONFIG)
    .filter(section => {
      // Check if user has required roles
      if (section.requiredRoles) {
        return section.requiredRoles.includes(user.role_name);
      }
      return true;
    })
    .sort((a, b) => a.order - b.order);
};

// Helper function to check if user has access to a specific path
export const hasAccessToPath = (user: any, path: string): boolean => {
  if (!user) return false;

  for (const section of Object.values(NAVIGATION_CONFIG)) {
    for (const item of section.items) {
      if (item.path === path) {
        if (section.requiredRoles) {
          return section.requiredRoles.includes(user.role_name);
        }
        return true;
      }
    }
  }
  return false;
};

// Helper function to get section for a path
export const getSectionForPath = (path: string): string | null => {
  for (const [sectionKey, section] of Object.entries(NAVIGATION_CONFIG)) {
    if (section.items.some(item => item.path === path)) {
      return sectionKey;
    }
  }
  return null;
};

// Helper function to get item for a path
export const getItemForPath = (path: string): NavigationItem | null => {
  for (const section of Object.values(NAVIGATION_CONFIG)) {
    const item = section.items.find(item => item.path === path);
    if (item) {
      return item;
    }
  }
  return null;
}; 