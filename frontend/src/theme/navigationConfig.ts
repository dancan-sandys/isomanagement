import {
  Dashboard,
  Description,
  Security,
  Assignment,
  Timeline,
  People,
  Settings,
  Business,
  Assessment,
  School,
  Build,
  Inventory,
  VerifiedUser,
  ReportProblem,
  SupportAgent,
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

// COMPACT Navigation configuration - Reduced spacing and optimized layout
export const NAVIGATION_CONFIG: Record<string, NavigationSection> = {
  dashboard: {
    title: 'Dashboard',
    icon: Dashboard,
    order: 1,
    items: [
      { text: 'Overview', path: '/dashboard' },
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
      { text: 'Risk Thresholds', path: '/haccp/risk-thresholds' },
    ],
  },
  
  prp: {
    title: 'PRP Programs',
    icon: Assignment,
    order: 4,
    requiredRoles: ['Production Manager', 'Production Operator', 'Maintenance Manager', 'Maintenance Technician', 'System Administrator'],
    items: [
      { text: 'PRP Overview', path: '/prp' },
    ],
  },
  
  suppliers: {
    title: 'Supplier Management',
    icon: Business,
    order: 5,
    requiredRoles: ['QA Manager', 'QA Specialist', 'Production Manager', 'System Administrator'],
    items: [
      { text: 'Suppliers', path: '/suppliers' },
      // Evaluation and Approved remain accessible via redirects but hidden from the menu
      // Supplier Audits hidden until implemented
    ],
  },
  
  traceability: {
    title: 'Traceability',
    icon: Timeline,
    order: 6,
    requiredRoles: ['Production Manager', 'Production Operator', 'QA Manager', 'QA Specialist', 'System Administrator'],
    items: [
      { text: 'Batch Tracking', path: '/traceability' },
      { text: 'Traceability Chain', path: '/traceability/chain' },
      { text: 'Product Recall', path: '/traceability/recall' },
      { text: 'Traceability Reports', path: '/traceability/reports' },
    ],
  },
  
  nonconformance: {
    title: 'Non-Conformance & CAPA',
    icon: ReportProblem,
    order: 7,
    requiredRoles: ['QA Manager', 'QA Specialist', 'Production Manager', 'System Administrator'],
    items: [
      { text: 'Non-Conformances', path: '/nonconformance' },
      { text: 'CAPA Actions', path: '/nonconformance/capas' },
    ],
  },
  complaints: {
    title: 'Customer Complaints',
    icon: SupportAgent,
    order: 8,
    requiredRoles: ['QA Manager', 'QA Specialist', 'Production Manager', 'System Administrator'],
    items: [
      { text: 'Complaints', path: '/complaints' },
    ],
  },
  
  audits: {
    title: 'Audit Management',
    icon: Assessment,
    order: 8,
    requiredRoles: ['QA Manager', 'QA Specialist', 'Auditor', 'System Administrator'],
    items: [
      { text: 'Internal Audits', path: '/audits/internal' },
      { text: 'External Audits', path: '/audits/external' },
      { text: 'Audit Schedule', path: '/audits/schedule' },
      { text: 'Findings & NCs', path: '/audits/findings' },
      { text: 'Audit Reports', path: '/audits/reports' },
    ],
  },
  
  training: {
    title: 'Training & Competence',
    icon: School,
    order: 9,
    requiredRoles: ['QA Manager', 'HR Manager', 'System Administrator'],
    items: [
      { text: 'Training Programs', path: '/training' },
      { text: 'My Training Matrix', path: '/training/matrix' },
      { text: 'Competence Assessment', path: '/training/assessment' },
      { text: 'Training Records', path: '/training/records' },
      { text: 'Certification Tracking', path: '/training/certification' },
      { text: 'Training Calendar', path: '/training/calendar' },
    ],
  },
  
  maintenance: {
    title: 'Maintenance',
    icon: Build,
    order: 10,
    requiredRoles: ['Maintenance Manager', 'Maintenance Technician', 'Production Manager', 'System Administrator'],
    items: [
      { text: 'Equipment Register', path: '/maintenance/equipment' },
      { text: 'Preventive Maintenance', path: '/maintenance/preventive' },
      { text: 'Work Orders', path: '/maintenance/work-orders' },
      { text: 'Calibration', path: '/maintenance/calibration' },
      { text: 'Maintenance History', path: '/maintenance/history' },
    ],
  },
  
  inventory: {
    title: 'Inventory Management',
    icon: Inventory,
    order: 11,
    requiredRoles: ['Production Manager', 'Production Operator', 'Warehouse Manager', 'System Administrator'],
    items: [
      { text: 'Raw Materials', path: '/inventory/materials' },
      { text: 'Finished Products', path: '/inventory/products' },
      { text: 'Stock Levels', path: '/inventory/stock' },
      { text: 'Inventory Counts', path: '/inventory/counts' },
      { text: 'Inventory Reports', path: '/inventory/reports' },
    ],
  },
  
  compliance: {
    title: 'Compliance',
    icon: VerifiedUser,
    order: 12,
    requiredRoles: ['QA Manager', 'QA Specialist', 'Compliance Officer', 'System Administrator'],
    items: [
      { text: 'Risks', path: '/compliance/risks' },
      { text: 'Opportunities', path: '/compliance/opportunities' },
      { text: 'Allergen & Label Control', path: '/compliance/allergen-label' },
    ],
  },
  management_reviews: {
    title: 'Management Reviews',
    icon: Assessment,
    order: 13,
    requiredRoles: ['QA Manager', 'Compliance Officer', 'System Administrator'],
    items: [
      { text: 'Reviews', path: '/management-reviews' },
      { text: 'Calendar', path: '/management-reviews/calendar' },
      { text: 'Action Items', path: '/management-reviews/actions' },
      { text: 'Templates', path: '/management-reviews/templates' },
      { text: 'Analytics', path: '/management-reviews/analytics' },
    ],
  },
  
  users: {
    title: 'User Management',
    icon: People,
    order: 14,
    requiredRoles: ['System Administrator', 'QA Manager'],
    items: [
      { text: 'Users', path: '/users' },
      { text: 'Roles & Permissions', path: '/rbac' },
    ],
  },
  
  settings: {
    title: 'System Settings',
    icon: Settings,
    order: 15,
    requiredRoles: ['System Administrator'],
    items: [
      { text: 'Settings', path: '/settings' },
      // Submenus removed until implemented
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