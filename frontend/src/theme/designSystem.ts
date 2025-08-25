import { createTheme, Theme } from '@mui/material/styles';

export const ISO_STATUS_COLORS = {
  compliant: '#059669',
  nonConformance: '#DC2626',
  pending: '#EA580C',
  warning: '#D97706',
  info: '#2563EB',
  neutral: '#374151',
  effective: '#059669',
  atRisk: '#DC2626',
} as const;

export const PROFESSIONAL_COLORS = {
  primary: {
    main: '#1E40AF',
    light: '#3B82F6',
    dark: '#1E3A8A',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#64748B',
    light: '#94A3B8',
    dark: '#475569',
    contrastText: '#FFFFFF',
  },
  accent: {
    main: '#10B981',
    light: '#34D399',
    dark: '#059669',
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

export const TYPOGRAPHY = {
  fontFamily: '"Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
  h1: { fontSize: '2.5rem', fontWeight: 800, lineHeight: 1.2, letterSpacing: '-0.025em' },
  h2: { fontSize: '2rem', fontWeight: 700, lineHeight: 1.3, letterSpacing: '-0.02em' },
  h3: { fontSize: '1.5rem', fontWeight: 700, lineHeight: 1.4, letterSpacing: '-0.015em' },
  h4: { fontSize: '1.25rem', fontWeight: 600, lineHeight: 1.4, letterSpacing: '-0.01em' },
  h5: { fontSize: '1.125rem', fontWeight: 600, lineHeight: 1.4, letterSpacing: '-0.005em' },
  h6: { fontSize: '1rem', fontWeight: 600, lineHeight: 1.4 },
  body1: { fontSize: '1rem', fontWeight: 400, lineHeight: 1.6 },
  body2: { fontSize: '0.875rem', fontWeight: 400, lineHeight: 1.6 },
  caption: { fontSize: '0.75rem', fontWeight: 600, lineHeight: 1.4, textTransform: 'uppercase', letterSpacing: '0.05em' },
  button: { fontSize: '0.875rem', fontWeight: 600, lineHeight: 1.4, textTransform: 'none', letterSpacing: '0.025em' },
} as const;

export const COMPONENT_STYLES = {
  card: {
    borderRadius: 12,
    boxShadow: PROFESSIONAL_COLORS.shadow.light,
    border: '1px solid #E2E8F0',
  },
  button: {
    borderRadius: 12,
    textTransform: 'none',
    fontWeight: 600,
    padding: '12px 24px',
    minHeight: 48,
  },
  input: {
    borderRadius: 12,
  },
} as const;

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
    | 'blacklisted'
    | 'in_spec'
    | 'out_of_spec'
) => {
  const statusConfig: Record<string, { color: 'default' | 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info'; backgroundColor: string; borderColor: string; textColor: string; iconColor: string; }> = {
    compliant: { color: 'success', backgroundColor: '#F0FDF4', borderColor: '#BBF7D0', textColor: '#166534', iconColor: '#059669' },
    nonConformance: { color: 'error', backgroundColor: '#FEF2F2', borderColor: '#FECACA', textColor: '#991B1B', iconColor: '#DC2626' },
    pending: { color: 'warning', backgroundColor: '#FFFBEB', borderColor: '#FED7AA', textColor: '#92400E', iconColor: '#EA580C' },
    warning: { color: 'warning', backgroundColor: '#FFFBEB', borderColor: '#FED7AA', textColor: '#92400E', iconColor: '#D97706' },
    info: { color: 'info', backgroundColor: '#EFF6FF', borderColor: '#BFDBFE', textColor: '#1E40AF', iconColor: '#2563EB' },
    approved: { color: 'success', backgroundColor: '#F0FDF4', borderColor: '#BBF7D0', textColor: '#166534', iconColor: '#059669' },
    rejected: { color: 'error', backgroundColor: '#FEF2F2', borderColor: '#FECACA', textColor: '#991B1B', iconColor: '#DC2626' },
    under_review: { color: 'info', backgroundColor: '#EFF6FF', borderColor: '#BFDBFE', textColor: '#1E40AF', iconColor: '#2563EB' },
    active: { color: 'success', backgroundColor: '#F0FDF4', borderColor: '#BBF7D0', textColor: '#166534', iconColor: '#059669' },
    inactive: { color: 'default', backgroundColor: '#F8FAFC', borderColor: '#E2E8F0', textColor: '#1F2937', iconColor: '#6B7280' },
    suspended: { color: 'error', backgroundColor: '#FEF2F2', borderColor: '#FECACA', textColor: '#991B1B', iconColor: '#DC2626' },
    pending_approval: { color: 'info', backgroundColor: '#EFF6FF', borderColor: '#BFDBFE', textColor: '#1E40AF', iconColor: '#2563EB' },
    blacklisted: { color: 'error', backgroundColor: '#FEF2F2', borderColor: '#FECACA', textColor: '#991B1B', iconColor: '#DC2626' },
    passed: { color: 'success', backgroundColor: '#F0FDF4', borderColor: '#BBF7D0', textColor: '#166534', iconColor: '#059669' },
    failed: { color: 'error', backgroundColor: '#FEF2F2', borderColor: '#FECACA', textColor: '#991B1B', iconColor: '#DC2626' },
    in_spec: { color: 'success', backgroundColor: '#ECFDF5', borderColor: '#A7F3D0', textColor: '#065F46', iconColor: '#10B981' },
    out_of_spec: { color: 'error', backgroundColor: '#FEF2F2', borderColor: '#FECACA', textColor: '#991B1B', iconColor: '#DC2626' },
  };

  return statusConfig[status] || {
    color: 'default',
    backgroundColor: '#F8FAFC',
    borderColor: '#E2E8F0',
    textColor: '#1F2937',
    iconColor: '#6B7280',
  };
};

export const createISOTheme = (mode: 'light' | 'dark' = 'light'): Theme => {
  return createTheme({
    palette: {
      mode,
      primary: { main: PROFESSIONAL_COLORS.primary.main },
      secondary: { main: PROFESSIONAL_COLORS.secondary.main },
    },
    typography: {
      fontFamily: TYPOGRAPHY.fontFamily,
    } as any,
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: COMPONENT_STYLES.button.borderRadius,
          },
        },
      },
    },
  });
};

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

export const ISO_NAVIGATION = {
  dashboard: { title: 'Dashboard', items: [{ text: 'Overview', path: '/dashboard' }] },
  documents: { title: 'Document Control', items: [{ text: 'Document Register', path: '/documents' }] },
  users: { title: 'User Management', items: [{ text: 'Users', path: '/users' }, { text: 'Roles & Permissions', path: '/rbac' }] },
  haccp: { title: 'HACCP System', items: [{ text: 'HACCP Plans', path: '/haccp' }, { text: 'CCP Management', path: '/haccp/ccp' }, { text: 'Hazard Analysis', path: '/haccp/hazards' }] },
  prp: { title: 'PRP Programs', items: [{ text: 'PRP Overview', path: '/prp' }, { text: 'Cleaning & Sanitation', path: '/prp/cleaning' }, { text: 'Maintenance', path: '/prp/maintenance' }] },
  suppliers: { title: 'Supplier Management', items: [{ text: 'Suppliers', path: '/suppliers' }, { text: 'Supplier Evaluation', path: '/suppliers/evaluation' }] },
  traceability: { title: 'Traceability', items: [{ text: 'Batch Tracking', path: '/traceability' }, { text: 'Traceability Chain', path: '/traceability/chain' }] },
  settings: { title: 'System Settings', items: [{ text: 'Settings', path: '/settings' }, { text: 'Profile', path: '/profile' }] },
} as const;

export default createISOTheme;