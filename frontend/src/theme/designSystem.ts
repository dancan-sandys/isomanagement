import { createTheme, Theme } from '@mui/material/styles';

// Enhanced ISO 22000 Status Colors with better contrast
export const ISO_STATUS_COLORS = {
  compliant: '#059669', // Enhanced Green - Compliant/Completed
  nonConformance: '#DC2626', // Enhanced Red - Non-conformance/Urgent
  pending: '#EA580C', // Enhanced Orange - Pending/Needs Review
  warning: '#D97706', // Enhanced Yellow - Warning
  info: '#2563EB', // Enhanced Blue - Information
  neutral: '#374151', // Enhanced Dark Gray - Neutral
} as const;

// Enhanced Professional Color Palette
export const PROFESSIONAL_COLORS = {
  primary: {
    main: '#1E40AF', // Enhanced Navy Blue
    light: '#3B82F6',
    dark: '#1E3A8A',
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
    elevated: '#FFFFFF',
  },
  text: {
    primary: '#1E293B',
    secondary: '#64748B',
    disabled: '#94A3B8',
  },
  divider: '#E2E8F0',
  border: '#CBD5E1',
  shadow: {
    light: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    medium: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    heavy: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    glow: '0 0 20px rgba(30, 64, 175, 0.15)',
  },
} as const;

// Enhanced Typography Scale
export const TYPOGRAPHY = {
  fontFamily: '"Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
  h1: {
    fontSize: '2.5rem',
    fontWeight: 800,
    lineHeight: 1.2,
    letterSpacing: '-0.025em',
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 700,
    lineHeight: 1.3,
    letterSpacing: '-0.02em',
  },
  h3: {
    fontSize: '1.5rem',
    fontWeight: 700,
    lineHeight: 1.4,
    letterSpacing: '-0.015em',
  },
  h4: {
    fontSize: '1.25rem',
    fontWeight: 600,
    lineHeight: 1.4,
    letterSpacing: '-0.01em',
  },
  h5: {
    fontSize: '1.125rem',
    fontWeight: 600,
    lineHeight: 1.4,
    letterSpacing: '-0.005em',
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
    fontWeight: 600,
    lineHeight: 1.4,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  button: {
    fontSize: '0.875rem',
    fontWeight: 600,
    lineHeight: 1.4,
    textTransform: 'none',
    letterSpacing: '0.025em',
  },
} as const;

// Enhanced Component Styles with better animations and effects
export const COMPONENT_STYLES = {
  card: {
    // Reduce default radius to avoid overly rounded/oval cards
    borderRadius: 12,
    boxShadow: PROFESSIONAL_COLORS.shadow.light,
    border: '1px solid #E2E8F0',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    '&:hover': {
      boxShadow: PROFESSIONAL_COLORS.shadow.medium,
      transform: 'translateY(-2px)',
    },
    '&:active': {
      transform: 'translateY(0px)',
    },
  },
  elevatedCard: {
    borderRadius: 14,
    boxShadow: PROFESSIONAL_COLORS.shadow.heavy,
    border: '1px solid #E2E8F0',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    '&:hover': {
      boxShadow: PROFESSIONAL_COLORS.shadow.glow,
      transform: 'translateY(-4px)',
    },
  },
  button: {
    borderRadius: 12,
    textTransform: 'none',
    fontWeight: 600,
    padding: '12px 24px',
    minHeight: 48,
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    '&:hover': {
      transform: 'translateY(-1px)',
      boxShadow: PROFESSIONAL_COLORS.shadow.medium,
    },
    '&:active': {
      transform: 'translateY(0px)',
    },
    '&.MuiButton-outlined': {
      borderColor: '#CBD5E1',
      backgroundColor: 'rgba(30, 64, 175, 0.02)',
      '&:hover': {
        borderColor: '#94A3B8',
        backgroundColor: 'rgba(30, 64, 175, 0.06)',
      },
    },
  },
  input: {
    borderRadius: 12,
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    '& .MuiOutlinedInput-root': {
      '& fieldset': {
        borderColor: '#CBD5E1',
        transition: 'border-color 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      },
      '&:hover fieldset': {
        borderColor: '#94A3B8',
      },
      '&.Mui-focused fieldset': {
        borderColor: '#1E40AF',
        borderWidth: '2px',
      },
    },
  },
  table: {
    '& .MuiTableCell-root': {
      borderBottom: '1px solid #E2E8F0',
      padding: '16px 20px',
      transition: 'background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    },
    '& .MuiTableHead-root .MuiTableCell-root': {
      backgroundColor: '#F8FAFC',
      fontWeight: 700,
      fontSize: '0.875rem',
      textTransform: 'uppercase',
      letterSpacing: '0.05em',
    },
    '& .MuiTableRow-root:hover .MuiTableCell-root': {
      backgroundColor: '#F1F5F9',
    },
  },
  statusChip: {
    borderRadius: 20,
    fontWeight: 700,
    fontSize: '0.75rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    padding: '6px 16px',
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    '&:hover': {
      transform: 'scale(1.05)',
    },
  },
  navigationItem: {
    borderRadius: 12,
    margin: '4px 8px',
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    '&:hover': {
      backgroundColor: 'rgba(30, 64, 175, 0.08)',
      transform: 'translateX(4px)',
    },
    '&.Mui-selected': {
      backgroundColor: '#1E40AF',
      color: '#FFFFFF',
      boxShadow: '0 4px 12px rgba(30, 64, 175, 0.3)',
      '&:hover': {
        backgroundColor: '#1E3A8A',
        transform: 'translateX(4px)',
      },
    },
  },
  metricCard: {
    borderRadius: 20,
    padding: '24px',
    background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',
    border: '1px solid #E2E8F0',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    },
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E2E8F0',
    '& .MuiLinearProgress-bar': {
      borderRadius: 4,
      transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },
} as const;

// Enhanced spacing system
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
} as const;

// Enhanced breakpoints
export const BREAKPOINTS = {
  xs: 0,
  sm: 600,
  md: 960,
  lg: 1280,
  xl: 1920,
} as const;

// Enhanced theme creation with better animations and effects
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
      borderRadius: 12,
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
          contained: {
            boxShadow: PROFESSIONAL_COLORS.shadow.light,
            '&:hover': {
              boxShadow: PROFESSIONAL_COLORS.shadow.medium,
            },
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
            boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
            borderBottom: `1px solid ${isLight ? PROFESSIONAL_COLORS.divider : '#334155'}`,
            backdropFilter: 'blur(10px)',
            background: isLight 
              ? 'rgba(255, 255, 255, 0.95)' 
              : 'rgba(30, 41, 59, 0.95)',
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            backgroundColor: isLight ? PROFESSIONAL_COLORS.background.sidebar : '#0F172A',
            borderRight: `1px solid ${isLight ? PROFESSIONAL_COLORS.divider : '#334155'}`,
            width: 280,
            backdropFilter: 'blur(10px)',
            boxShadow: isLight ? '0 10px 30px rgba(2, 6, 23, 0.08)' : '0 10px 30px rgba(2,6,23,0.5)',
          },
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            ...COMPONENT_STYLES.navigationItem,
            '& .MuiListItemIcon-root': {
              color: isLight ? '#334155' : '#E2E8F0',
            },
          },
        },
      },
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            ...COMPONENT_STYLES.progressBar,
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
        backgroundImage: 'none',
        borderRadius: 12,
          },
          elevation1: {
            boxShadow: PROFESSIONAL_COLORS.shadow.light,
          },
          elevation2: {
            boxShadow: PROFESSIONAL_COLORS.shadow.medium,
          },
          elevation3: {
            boxShadow: PROFESSIONAL_COLORS.shadow.heavy,
          },
        },
      },
      MuiPopover: {
        styleOverrides: {
          paper: {
            backdropFilter: 'blur(8px)',
          },
        },
      },
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            backgroundColor: isLight ? '#1E293B' : '#F1F5F9',
            color: isLight ? '#FFFFFF' : '#1E293B',
            fontSize: '0.75rem',
            fontWeight: 500,
            borderRadius: 8,
            boxShadow: PROFESSIONAL_COLORS.shadow.medium,
          },
        },
      },
      MuiAlert: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            fontWeight: 500,
          },
        },
      },
      MuiDialog: {
        styleOverrides: {
          paper: {
            borderRadius: 16,
            boxShadow: PROFESSIONAL_COLORS.shadow.heavy,
          },
        },
      },
      MuiSnackbar: {
        styleOverrides: {
          root: {
            '& .MuiSnackbarContent-root': {
              borderRadius: 12,
              boxShadow: PROFESSIONAL_COLORS.shadow.medium,
            },
          },
        },
      },
    },
  });
};

// Status chip variants
export const getStatusChipProps = (
  status:
    | 'compliant'
    | 'nonConformance'
    | 'pending'
    | 'warning'
    | 'info'
    | 'active'
    | 'inactive'
    | 'suspended'
    | 'approved'
    | 'rejected'
    | 'under_review'
    | 'passed'
    | 'failed'
    | 'pending_approval'
    | 'blacklisted') => {
  const statusConfig = {
    compliant: {
      color: 'success' as const,
      backgroundColor: '#F0FDF4',
      borderColor: '#BBF7D0',
      textColor: '#166534',
      iconColor: '#059669',
    },
    nonConformance: {
      color: 'error' as const,
      backgroundColor: '#FEF2F2',
      borderColor: '#FECACA',
      textColor: '#991B1B',
      iconColor: '#DC2626',
    },
    pending: {
      color: 'warning' as const,
      backgroundColor: '#FFFBEB',
      borderColor: '#FED7AA',
      textColor: '#92400E',
      iconColor: '#EA580C',
    },
    warning: {
      color: 'warning' as const,
      backgroundColor: '#FFFBEB',
      borderColor: '#FED7AA',
      textColor: '#92400E',
      iconColor: '#D97706',
    },
    info: {
      color: 'info' as const,
      backgroundColor: '#EFF6FF',
      borderColor: '#BFDBFE',
      textColor: '#1E40AF',
      iconColor: '#2563EB',
    },
    approved: {
      color: 'success' as const,
      backgroundColor: '#F0FDF4',
      borderColor: '#BBF7D0',
      textColor: '#166534',
      iconColor: '#059669',
    },
    rejected: {
      color: 'error' as const,
      backgroundColor: '#FEF2F2',
      borderColor: '#FECACA',
      textColor: '#991B1B',
      iconColor: '#DC2626',
    },
    under_review: {
      color: 'info' as const,
      backgroundColor: '#EFF6FF',
      borderColor: '#BFDBFE',
      textColor: '#1E40AF',
      iconColor: '#2563EB',
    },
    active: {
      color: 'success' as const,
      backgroundColor: '#F0FDF4',
      borderColor: '#BBF7D0',
      textColor: '#166534',
      iconColor: '#059669',
    },
    inactive: {
      color: 'default' as const,
      backgroundColor: '#F8FAFC',
      borderColor: '#E2E8F0',
      textColor: '#1F2937',
      iconColor: '#6B7280',    },
    suspended: {
      color: 'error' as const,
      backgroundColor: '#FEF2F2',
      borderColor: '#FECACA',
      textColor: '#991B1B',
      iconColor: '#DC2626',
    },
    passed: {
      color: 'success' as const,
      backgroundColor: '#F0FDF4',
      borderColor: '#BBF7D0',
      textColor: '#166534',
      iconColor: '#059669',
    },
    failed: {
      color: 'error' as const,
      backgroundColor: '#FEF2F2',
      borderColor: '#FECACA',
      textColor: '#991B1B',
      iconColor: '#DC2626',
    },
    pending_approval: {
      color: 'info' as const,
      backgroundColor: '#EFF6FF',
      borderColor: '#BFDBFE',
      textColor: '#1E40AF',
      iconColor: '#2563EB',
    },
    blacklisted: {
      color: 'error' as const,
      backgroundColor: '#FEF2F2',
      borderColor: '#FECACA',
      textColor: '#991B1B',
      iconColor: '#DC2626',
    },
  };

  return statusConfig[status];
};

// Enhanced role-based dashboard configurations
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