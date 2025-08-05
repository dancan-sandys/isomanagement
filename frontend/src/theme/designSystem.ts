import { createTheme, Theme } from '@mui/material/styles';

// ISO 22000 Status Colors
export const ISO_STATUS_COLORS = {
  compliant: '#2E7D32', // Green - Compliant/Completed
  nonConformance: '#D32F2F', // Red - Non-conformance/Urgent
  pending: '#F57C00', // Orange - Pending/Needs Review
  warning: '#FF8F00', // Yellow - Warning
  info: '#1976D2', // Blue - Information
  neutral: '#424242', // Dark Gray - Neutral
} as const;

// Professional Color Palette
export const PROFESSIONAL_COLORS = {
  primary: {
    main: '#1E3A8A', // Navy Blue
    light: '#3B82F6',
    dark: '#1E40AF',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#64748B', // Slate Gray
    light: '#94A3B8',
    dark: '#475569',
    contrastText: '#FFFFFF',
  },
  background: {
    default: '#F8FAFC',
    paper: '#FFFFFF',
    sidebar: '#F1F5F9',
    card: '#FFFFFF',
  },
  text: {
    primary: '#1E293B',
    secondary: '#64748B',
    disabled: '#94A3B8',
  },
  divider: '#E2E8F0',
  border: '#CBD5E1',
} as const;

// Typography Scale
export const TYPOGRAPHY = {
  fontFamily: '"Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
  h1: {
    fontSize: '2.5rem',
    fontWeight: 700,
    lineHeight: 1.2,
    letterSpacing: '-0.02em',
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 600,
    lineHeight: 1.3,
    letterSpacing: '-0.01em',
  },
  h3: {
    fontSize: '1.5rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h4: {
    fontSize: '1.25rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1.125rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h6: {
    fontSize: '1rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  body1: {
    fontSize: '1rem',
    fontWeight: 400,
    lineHeight: 1.6,
  },
  body2: {
    fontSize: '0.875rem',
    fontWeight: 400,
    lineHeight: 1.6,
  },
  caption: {
    fontSize: '0.75rem',
    fontWeight: 500,
    lineHeight: 1.4,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  button: {
    fontSize: '0.875rem',
    fontWeight: 600,
    lineHeight: 1.4,
    textTransform: 'none',
  },
} as const;

// Component Styles
export const COMPONENT_STYLES = {
  card: {
    borderRadius: 12,
    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    border: '1px solid #E2E8F0',
    transition: 'all 0.2s ease-in-out',
    '&:hover': {
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    },
  },
  button: {
    borderRadius: 8,
    textTransform: 'none',
    fontWeight: 600,
    padding: '8px 16px',
    minHeight: 40,
  },
  input: {
    borderRadius: 8,
    '& .MuiOutlinedInput-root': {
      '& fieldset': {
        borderColor: '#CBD5E1',
      },
      '&:hover fieldset': {
        borderColor: '#94A3B8',
      },
      '&.Mui-focused fieldset': {
        borderColor: '#1E3A8A',
      },
    },
  },
  table: {
    '& .MuiTableCell-root': {
      borderBottom: '1px solid #E2E8F0',
      padding: '12px 16px',
    },
    '& .MuiTableHead-root .MuiTableCell-root': {
      backgroundColor: '#F8FAFC',
      fontWeight: 600,
      fontSize: '0.875rem',
    },
  },
  statusChip: {
    borderRadius: 16,
    fontWeight: 600,
    fontSize: '0.75rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    padding: '4px 12px',
  },
} as const;

// Spacing System
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

// Breakpoints
export const BREAKPOINTS = {
  xs: 0,
  sm: 600,
  md: 960,
  lg: 1280,
  xl: 1920,
} as const;

// Create the main theme
export const createISOTheme = (mode: 'light' | 'dark' = 'light'): Theme => {
  const isLight = mode === 'light';
  
  return createTheme({
    palette: {
      mode,
      primary: PROFESSIONAL_COLORS.primary,
      secondary: PROFESSIONAL_COLORS.secondary,
      background: {
        default: isLight ? PROFESSIONAL_COLORS.background.default : '#0F172A',
        paper: isLight ? PROFESSIONAL_COLORS.background.paper : '#1E293B',
      },
      text: {
        primary: isLight ? PROFESSIONAL_COLORS.text.primary : '#F1F5F9',
        secondary: isLight ? PROFESSIONAL_COLORS.text.secondary : '#94A3B8',
      },
      divider: isLight ? PROFESSIONAL_COLORS.divider : '#334155',
      error: {
        main: ISO_STATUS_COLORS.nonConformance,
      },
      warning: {
        main: ISO_STATUS_COLORS.pending,
      },
      info: {
        main: ISO_STATUS_COLORS.info,
      },
      success: {
        main: ISO_STATUS_COLORS.compliant,
      },
    },
    typography: {
      fontFamily: TYPOGRAPHY.fontFamily,
      h1: TYPOGRAPHY.h1,
      h2: TYPOGRAPHY.h2,
      h3: TYPOGRAPHY.h3,
      h4: TYPOGRAPHY.h4,
      h5: TYPOGRAPHY.h5,
      h6: TYPOGRAPHY.h6,
      body1: TYPOGRAPHY.body1,
      body2: TYPOGRAPHY.body2,
      caption: TYPOGRAPHY.caption,
      button: TYPOGRAPHY.button,
    },
    shape: {
      borderRadius: 8,
    },
    spacing: 8,
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            ...COMPONENT_STYLES.card,
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            ...COMPONENT_STYLES.button,
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            ...COMPONENT_STYLES.input,
          },
        },
      },
      MuiTable: {
        styleOverrides: {
          root: {
            ...COMPONENT_STYLES.table,
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            ...COMPONENT_STYLES.statusChip,
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: isLight ? '#FFFFFF' : '#1E293B',
            color: isLight ? PROFESSIONAL_COLORS.text.primary : '#F1F5F9',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
            borderBottom: `1px solid ${isLight ? PROFESSIONAL_COLORS.divider : '#334155'}`,
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            backgroundColor: isLight ? PROFESSIONAL_COLORS.background.sidebar : '#0F172A',
            borderRight: `1px solid ${isLight ? PROFESSIONAL_COLORS.divider : '#334155'}`,
            width: 280,
          },
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            margin: '4px 8px',
            '&.Mui-selected': {
              backgroundColor: isLight ? PROFESSIONAL_COLORS.primary.main : '#1E3A8A',
              color: '#FFFFFF',
              '&:hover': {
                backgroundColor: isLight ? PROFESSIONAL_COLORS.primary.dark : '#1E40AF',
              },
            },
          },
        },
      },
    },
  });
};

// Status chip variants
export const getStatusChipProps = (status: 'compliant' | 'nonConformance' | 'pending' | 'warning' | 'info') => {
  const statusConfig = {
    compliant: {
      color: 'success' as const,
      backgroundColor: '#F0FDF4',
      borderColor: '#BBF7D0',
    },
    nonConformance: {
      color: 'error' as const,
      backgroundColor: '#FEF2F2',
      borderColor: '#FECACA',
    },
    pending: {
      color: 'warning' as const,
      backgroundColor: '#FFFBEB',
      borderColor: '#FED7AA',
    },
    warning: {
      color: 'warning' as const,
      backgroundColor: '#FFFBEB',
      borderColor: '#FED7AA',
    },
    info: {
      color: 'info' as const,
      backgroundColor: '#EFF6FF',
      borderColor: '#BFDBFE',
    },
  };

  return statusConfig[status];
};

// Role-based dashboard configurations
export const ROLE_DASHBOARDS = {
  qaManager: {
    title: 'QA Manager Dashboard',
    sections: [
      { title: 'Non-Conformance Trends', type: 'chart' },
      { title: 'CAPA Deadlines', type: 'list' },
      { title: 'Document Version Alerts', type: 'alerts' },
      { title: 'Audit Schedule', type: 'calendar' },
    ],
  },
  operator: {
    title: 'Operator Dashboard',
    sections: [
      { title: "Today's Tasks", type: 'checklist' },
      { title: 'Checklist Reminders', type: 'list' },
      { title: 'Quick Input Forms', type: 'forms' },
      { title: 'Recent Activities', type: 'activity' },
    ],
  },
  auditor: {
    title: 'Auditor Dashboard',
    sections: [
      { title: 'Compliance Scorecards', type: 'metrics' },
      { title: 'Audit Logs', type: 'table' },
      { title: 'Evidence Review Panel', type: 'gallery' },
      { title: 'Findings Summary', type: 'summary' },
    ],
  },
  executive: {
    title: 'Executive Dashboard',
    sections: [
      { title: 'Audit Success Rate', type: 'metric' },
      { title: 'Open CAPAs', type: 'count' },
      { title: 'Compliance Overview', type: 'chart' },
      { title: 'Risk Assessment', type: 'risk' },
    ],
  },
} as const;

// Navigation structure aligned with ISO 22000:2018 - PRIORITIZED FUNCTIONAL FEATURES
export const ISO_NAVIGATION = {
  dashboard: {
    title: 'Dashboard',
    items: [
      { text: 'Overview', path: '/dashboard' },
    ],
  },
  documents: {
    title: 'Document Control',
    items: [
      { text: 'Document Register', path: '/documents' },
      { text: 'Version Control', path: '/documents/versions' },
      { text: 'Approval Workflow', path: '/documents/approval' },
    ],
  },
  users: {
    title: 'User Management',
    items: [
      { text: 'Users', path: '/users' },
      { text: 'Roles & Permissions', path: '/rbac' },
    ],
  },
  haccp: {
    title: 'HACCP System',
    items: [
      { text: 'HACCP Plans', path: '/haccp' },
      { text: 'CCP Management', path: '/haccp/ccp' },
      { text: 'Hazard Analysis', path: '/haccp/hazards' },
    ],
  },
  prp: {
    title: 'PRP Programs',
    items: [
      { text: 'PRP Overview', path: '/prp' },
      { text: 'Cleaning & Sanitation', path: '/prp/cleaning' },
      { text: 'Maintenance', path: '/prp/maintenance' },
    ],
  },
  suppliers: {
    title: 'Supplier Management',
    items: [
      { text: 'Suppliers', path: '/suppliers' },
      { text: 'Supplier Evaluation', path: '/suppliers/evaluation' },
    ],
  },
  traceability: {
    title: 'Traceability',
    items: [
      { text: 'Batch Tracking', path: '/traceability' },
      { text: 'Traceability Chain', path: '/traceability/chain' },
    ],
  },
  settings: {
    title: 'System Settings',
    items: [
      { text: 'Settings', path: '/settings' },
      { text: 'Profile', path: '/profile' },
    ],
  },
} as const;

export default createISOTheme; 