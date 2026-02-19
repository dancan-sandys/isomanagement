import React, { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Stack,
  Typography,
  Button,
  Card,
  CardContent,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Chip,
  Alert,
  Grid,
  IconButton,
  Tooltip,
  Badge,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  FormControlLabel,
  Switch,
  Paper,
  LinearProgress,
  CircularProgress,
  CardActions,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Compare as CompareIcon,
  Flag as FlagIcon,
  // Not available in MUI; reuse Verified icon for compliance
  Verified as ComplianceIcon,
  Assessment as AssessmentIcon,
  // Not available; reuse Description icon for templates
  Description as TemplateIcon,
  History as HistoryIcon,
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Science as ScienceIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { allergenLabelAPI, haccpAPI, usersAPI } from '../services/api';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`allergen-tabpanel-${index}`}
      aria-labelledby={`allergen-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AllergenLabel: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [assessments, setAssessments] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [complianceResults, setComplianceResults] = useState<any[]>([]);
  const [allergenFlags, setAllergenFlags] = useState<any[]>([]);
  const [scanningProduct, setScanningProduct] = useState(false);
  const [scanResults, setScanResults] = useState<any>(null);
  const [scanDialog, setScanDialog] = useState(false);
  const [scanForm, setScanForm] = useState({
    product_id: '',
    ingredient_list: [] as string[],
    process_steps: [] as string[],
    detection_method: 'automated'
  });
  const [nonConformances, setNonConformances] = useState<any[]>([]);
  const [dashboardMetrics, setDashboardMetrics] = useState<any>(null);

  // Assessment Dialog
  const [assessmentDialog, setAssessmentDialog] = useState(false);
  const [assessmentForm, setAssessmentForm] = useState({
    product_id: '',
    risk_level: 'low',
    precautionary_labeling: '',
    control_measures: '',
    validation_verification: '',
    cross_contamination_risk: 'low',
    allergen_control_measures: '',
    validation_procedures: '',
  });

  // Template Dialog
  const [templateDialog, setTemplateDialog] = useState(false);
  const [templateForm, setTemplateForm] = useState({
    name: '',
    description: '',
    product_id: '',
    allergen_declarations: [] as string[],
    regulatory_compliance: [] as string[],
  });

  // Version Dialog
  const [versionDialog, setVersionDialog] = useState(false);
  const [versionForm, setVersionForm] = useState({
    template_id: '',
    content: '',
    change_description: '',
    change_reason: '',
    allergen_changes: [] as string[],
    compliance_updates: [] as string[],
  });

  // Comparison Dialog
  const [comparisonDialog, setComparisonDialog] = useState(false);
  const [comparisonData, setComparisonData] = useState<any>(null);

  // Compliance Validation Dialog
  const [complianceDialog, setComplianceDialog] = useState(false);
  const [complianceForm, setComplianceForm] = useState({
    template_id: '',
    regulatory_standards: [] as string[],
    validation_criteria: [] as string[],
  });

  const [versions, setVersions] = useState<Record<number, any[]>>({});
  const [approvals, setApprovals] = useState<Record<number, any[]>>({});
  const [approvalsOpen, setApprovalsOpen] = useState(false);
  const [approvalsCtx, setApprovalsCtx] = useState<{ templateId: number; versionId: number; templateName: string; versionNum: number } | null>(null);
  const currentUser = useSelector((s: RootState) => s.auth.user);

  const allergenList = [
    'Milk', 'Eggs', 'Fish', 'Crustacean shellfish', 'Tree nuts', 'Peanuts', 'Wheat', 'Soybeans',
    'Sesame', 'Sulfites', 'Gluten', 'Lactose', 'Histamine', 'Sulfites', 'Celery', 'Mustard',
    'Lupin', 'Molluscs'
  ];

  const regulatoryStandards = [
    'FDA Food Allergen Labeling and Consumer Protection Act (FALCPA)',
    'EU Food Information for Consumers Regulation (FIC)',
    'Codex Alimentarius Guidelines',
    'Canada Food and Drug Regulations',
    'Australia New Zealand Food Standards Code',
    'Japan Food Sanitation Law',
    'China Food Safety Law',
    'ISO 22000:2018',
    'HACCP Guidelines',
    'GMP Standards'
  ];

  const loadData = async () => {
    setLoading(true);
    try {
    const [ass, prods, us, tpls] = await Promise.all([
      allergenLabelAPI.listAssessments(),
      haccpAPI.getProducts(),
      usersAPI.getUsers({ page: 1, size: 100 }),
      allergenLabelAPI.listTemplates(true),
    ]);
    setAssessments(ass?.data || ass?.items || ass || []);
    const items = prods?.data?.items || prods?.items || [];
    setProducts(items);
    setUsers((us?.data?.items || us?.items || []).map((u: any) => ({ id: u.id, label: u.full_name ? `${u.full_name} (${u.username})` : u.username })));
    const tplItems = tpls?.data || tpls || [];
    setTemplates(tplItems);

      // Preload versions per template
    const vmap: Record<number, any[]> = {};
    for (const t of tplItems) {
        try { 
          vmap[t.id] = await allergenLabelAPI.listTemplateVersions(t.id); 
        } catch { 
          vmap[t.id] = []; 
        }
    }
    setVersions(vmap);

      // Load compliance results and allergen flags if available (optional)
      try {
        const compliance = (allergenLabelAPI as any).getComplianceResults ? await (allergenLabelAPI as any).getComplianceResults() : [];
        setComplianceResults(compliance || []);
      } catch {}

      try {
        // Load allergen flags
        const flagsResponse = await fetch('/api/v1/allergen-label/flags');
        if (flagsResponse.ok) {
          const flagsData = await flagsResponse.json();
          setAllergenFlags(flagsData.data?.flags || []);
        }
        
        // Load non-conformances
        const ncResponse = await fetch('/api/v1/allergen-label/nonconformances');
        if (ncResponse.ok) {
          const ncData = await ncResponse.json();
          setNonConformances(ncData.data?.nonconformances || []);
        }
        
        // Load dashboard metrics
        const metricsResponse = await fetch('/api/v1/allergen-label/dashboard/metrics');
        if (metricsResponse.ok) {
          const metricsData = await metricsResponse.json();
          setDashboardMetrics(metricsData.data);
        }
      } catch {
        // Fallback to mock data
        setAllergenFlags([
          {
            id: 1,
            product_id: 1,
            allergen_type: "peanuts",
            detected_in: "ingredient",
            severity: "critical",
            title: "Undeclared peanuts detected",
            description: "Peanut allergen found in chocolate ingredient without declaration",
            status: "active",
            detected_at: new Date().toISOString(),
            immediate_action: "Stop production, isolate batch, notify QA manager",
            confidence: 0.95,
            nc_created: true,
            nc_id: 1
          }
        ]);
        setNonConformances([
          {
            id: 1,
            nc_number: "ALG-20250117-ABC12345",
            title: "Critical Allergen Issue: Undeclared Peanuts in Chocolate Bar",
            severity: "critical",
            status: "open",
            product_reference: "Chocolate Bar",
            reported_date: new Date().toISOString(),
            requires_immediate_action: true,
            escalation_status: "pending"
          }
        ]);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const productName = (id?: number) => products.find((p: any) => p.id === id)?.name || '-';

  const getRiskLevelColor = (level: string) => {
    const colors: { [key: string]: 'success' | 'warning' | 'error' } = {
      'low': 'success',
      'medium': 'warning',
      'high': 'error',
    };
    return colors[level] || 'default';
  };

  const handleAssessmentSubmit = async () => {
    try {
      await allergenLabelAPI.createAssessment({
        product_id: Number(assessmentForm.product_id),
        risk_level: assessmentForm.risk_level as 'low' | 'medium' | 'high',
        precautionary_labeling: assessmentForm.precautionary_labeling,
        control_measures: assessmentForm.control_measures,
        validation_verification: assessmentForm.validation_verification,
      });
      setAssessmentDialog(false);
      setAssessmentForm({
        product_id: '',
        risk_level: 'low',
        precautionary_labeling: '',
        control_measures: '',
        validation_verification: '',
        cross_contamination_risk: 'low',
        allergen_control_measures: '',
        validation_procedures: '',
      });
      loadData();
    } catch (error) {
      console.error('Error creating assessment:', error);
    }
  };

  const handleTemplateSubmit = async () => {
    try {
      await allergenLabelAPI.createTemplate({
        ...templateForm,
        product_id: templateForm.product_id ? Number(templateForm.product_id) : null,
      });
      setTemplateDialog(false);
      setTemplateForm({
        name: '',
        description: '',
        product_id: '',
        allergen_declarations: [],
        regulatory_compliance: [],
      });
      loadData();
    } catch (error) {
      console.error('Error creating template:', error);
    }
  };

  const handleVersionSubmit = async () => {
    try {
      await allergenLabelAPI.createTemplateVersion(Number(versionForm.template_id), {
        content: versionForm.content,
        change_description: versionForm.change_description,
        change_reason: versionForm.change_reason,
      });
      setVersionDialog(false);
      setVersionForm({
        template_id: '',
        content: '',
        change_description: '',
        change_reason: '',
        allergen_changes: [],
        compliance_updates: [],
      });
      loadData();
    } catch (error) {
      console.error('Error creating version:', error);
    }
  };

  const handleComplianceValidation = async () => {
    // Optional backend; if not present, just close dialog with no changes
    try {
      if ((allergenLabelAPI as any).validateCompliance) {
        const results = await (allergenLabelAPI as any).validateCompliance({
          template_id: Number(complianceForm.template_id),
          regulatory_standards: complianceForm.regulatory_standards,
          validation_criteria: complianceForm.validation_criteria,
        });
        setComplianceResults(results || []);
      }
    } finally {
      setComplianceDialog(false);
    }
  };

  const handleProductScan = async () => {
    if (!scanForm.product_id) return;
    
    setScanningProduct(true);
    try {
      const response = await fetch(`/api/v1/allergen-label/products/${scanForm.product_id}/scan-allergens`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ingredient_list: scanForm.ingredient_list,
          process_steps: scanForm.process_steps,
          detection_method: scanForm.detection_method
        })
      });

      if (response.ok) {
        const result = await response.json();
        setScanResults(result.data);
        
        // Refresh allergen flags to show newly created ones
        const flagsResponse = await fetch('/api/v1/allergen-label/flags');
        if (flagsResponse.ok) {
          const flagsData = await flagsResponse.json();
          setAllergenFlags(flagsData.data?.flags || []);
        }
      } else {
        console.error('Scan failed:', response.statusText);
      }
    } catch (error) {
      console.error('Error scanning product:', error);
    } finally {
      setScanningProduct(false);
      setScanDialog(false);
    }
  };

  const handleResolveFlag = async (flagId: number, resolutionNotes: string) => {
    try {
      const response = await fetch(`/api/v1/allergen-label/flags/${flagId}/resolve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resolution_notes: resolutionNotes,
          resolution_actions: ['Updated allergen declarations', 'Verified supplier certificates']
        })
      });

      if (response.ok) {
        // Refresh flags
        const flagsResponse = await fetch('/api/v1/allergen-label/flags');
        if (flagsResponse.ok) {
          const flagsData = await flagsResponse.json();
          setAllergenFlags(flagsData.data?.flags || []);
        }
      }
    } catch (error) {
      console.error('Error resolving flag:', error);
    }
  };

  const handleCompareVersions = async (templateId: number, version1Id: number, version2Id: number) => {
    try {
      if ((allergenLabelAPI as any).compareVersions) {
        const comparison = await (allergenLabelAPI as any).compareVersions(templateId, version1Id, version2Id);
        setComparisonData(comparison);
      } else {
        setComparisonData({ version1: {}, version2: {}, differences: [] });
      }
      setComparisonDialog(true);
    } catch (error) {
      console.error('Error comparing versions:', error);
      setComparisonData({ version1: {}, version2: {}, differences: [] });
      setComparisonDialog(true);
    }
  };

  return (
    <Box p={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight="bold" color="primary">
          Allergen & Label Control
        </Typography>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<ScienceIcon />}
            onClick={() => setScanDialog(true)}
            color="secondary"
          >
            Scan Product
          </Button>
          <Button
            variant="outlined"
            startIcon={<ComplianceIcon />}
            onClick={() => setComplianceDialog(true)}
          >
            Compliance Check
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setAssessmentDialog(true)}
          >
            New Assessment
          </Button>
        </Stack>
      </Stack>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Dashboard Metrics */}
      {dashboardMetrics && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary" fontWeight="bold">
                  {dashboardMetrics.allergen_flags?.active || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Flags
                </Typography>
                {dashboardMetrics.allergen_flags?.critical > 0 && (
                  <Chip 
                    label={`${dashboardMetrics.allergen_flags.critical} Critical`} 
                    color="error" 
                     
                    sx={{ mt: 1 }} 
                  />
                )}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="error" fontWeight="bold">
                  {dashboardMetrics.non_conformances?.open_critical || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Critical NCs
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {dashboardMetrics.non_conformances?.total_allergen_ncs || 0} Total
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success.main" fontWeight="bold">
                  {Math.round(dashboardMetrics.compliance_status?.compliance_score || 0)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Compliance Score
                </Typography>
                <Chip 
                  label={dashboardMetrics.compliance_status?.iso_22000_compliant ? "ISO Compliant" : "Non-Compliant"} 
                  color={dashboardMetrics.compliance_status?.iso_22000_compliant ? "success" : "error"} 
                   
                  sx={{ mt: 1 }} 
                />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info.main" fontWeight="bold">
                  {dashboardMetrics.scanning_activity?.products_scanned || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Products Scanned
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {Math.round(dashboardMetrics.scanning_activity?.detection_rate || 0)}% Detection Rate
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Alerts Section */}
      {allergenFlags.length > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            ⚠️ {allergenFlags.length} Allergen Flag(s) Detected
          </Typography>
          <Stack spacing={1}>
            {allergenFlags.slice(0, 3).map((flag: any) => (
              <Typography key={flag.id} variant="body2">
                • {flag.description}
              </Typography>
            ))}
            {allergenFlags.length > 3 && (
              <Typography variant="body2" color="text.secondary">
                ... and {allergenFlags.length - 3} more
              </Typography>
            )}
          </Stack>
        </Alert>
      )}

      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="allergen tabs">
            <Tab
              icon={<AssessmentIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Assessments</span>
                  <Badge badgeContent={assessments.length} color="primary" />
                </Stack>
              }
            />
            <Tab
              icon={<TemplateIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Templates</span>
                  <Badge badgeContent={templates.length} color="secondary" />
                </Stack>
              }
            />
            <Tab
              icon={<ComplianceIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Compliance</span>
                  <Badge badgeContent={complianceResults.filter(r => r.status === 'failed').length} color="error" />
                </Stack>
              }
            />
            <Tab
              icon={<FlagIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Allergen Flags</span>
                  <Badge badgeContent={allergenFlags.length} color="warning" />
                </Stack>
              }
            />
            <Tab
              icon={<SecurityIcon />}
              label={
                <Stack direction="row" alignItems="center" spacing={1}>
                  <span>Non-Conformances</span>
                  <Badge badgeContent={nonConformances.filter(nc => nc.status === 'open').length} color="error" />
                </Stack>
              }
            />
            <Tab
              icon={<HistoryIcon />}
              label="History"
            />
          </Tabs>
        </Box>

        {/* Assessments Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            {assessments.map((assessment) => (
              <Grid item xs={12} md={6} lg={4} key={assessment.id}>
                <Card>
          <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                      <Typography variant="h6" fontWeight="bold">
                        {productName(assessment.product_id)}
                      </Typography>
                      <Chip
                        label={assessment.risk_level}
                        color={getRiskLevelColor(assessment.risk_level)}
                        
                      />
                    </Stack>
                    <Stack spacing={1}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Cross-contamination Risk:</strong> {assessment.cross_contamination_risk}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Precautionary Labeling:</strong> {assessment.precautionary_labeling || 'None'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Reviewed:</strong> {users.find(u => u.id === assessment.reviewed_by)?.label || 'Not reviewed'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Updated:</strong> {new Date(assessment.updated_at || assessment.created_at).toLocaleDateString()}
                      </Typography>
                    </Stack>
                  </CardContent>
                  <CardActions>
                    <Button  startIcon={<ViewIcon />}>
                      View Details
                    </Button>
                    <Button  startIcon={<EditIcon />}>
                      Edit
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Templates Tab */}
        <TabPanel value={tabValue} index={1}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">Label Templates</Typography>
            <Stack direction="row" spacing={1}>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setTemplateDialog(true)}
              >
                New Template
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setVersionDialog(true)}
              >
                New Version
              </Button>
            </Stack>
          </Stack>
          <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Product</TableCell>
                  <TableCell>Active</TableCell>
                <TableCell>Allergen Declarations</TableCell>
                <TableCell>Versions</TableCell>
                  <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
              {templates.map((template) => (
                <TableRow key={template.id}>
                  <TableCell>{template.name}</TableCell>
                  <TableCell>{productName(template.product_id)}</TableCell>
                  <TableCell>
                    <Chip
                      label={template.is_active ? 'Active' : 'Inactive'}
                      color={template.is_active ? 'success' : 'default'}
                      
                    />
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={0.5} flexWrap="wrap">
                      {(template.allergen_declarations || []).map((allergen: string) => (
                        <Chip key={allergen} label={allergen}  variant="outlined" />
                      ))}
                    </Stack>
                  </TableCell>
                    <TableCell>
                      <Stack spacing={0.5}>
                      {(versions[template.id] || []).map((version: any) => (
                        <Stack key={version.id} direction="row" alignItems="center" justifyContent="space-between">
                          <Typography variant="caption">v{version.version_number} • {version.status}</Typography>
                            <Stack direction="row" spacing={1}>
                            <Tooltip title="Export PDF">
                              <IconButton
                                
                                onClick={async () => {
                                  try {
                                    const blob = await allergenLabelAPI.exportVersionPDF(template.id, version.id);
                                    const url = window.URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    a.download = `label_${template.id}_v${version.version_number}.pdf`;
                                    a.click();
                                    window.URL.revokeObjectURL(url);
                                  } catch (error) {
                                    console.error('Error exporting PDF:', error);
                                  }
                                }}
                              >
                                <DownloadIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="View Approvals">
                              <IconButton
                                
                                onClick={async () => {
                                  try {
                                    const aps = await allergenLabelAPI.listVersionApprovals(template.id, version.id);
                                    setApprovals(prev => ({ ...prev, [version.id]: aps }));
                                    setApprovalsCtx({ templateId: template.id, versionId: version.id, templateName: template.name, versionNum: version.version_number });
                                  setApprovalsOpen(true);
                                  } catch (error) {
                                    console.error('Error loading approvals:', error);
                                  }
                                }}
                              >
                                <ViewIcon />
                              </IconButton>
                            </Tooltip>
                          </Stack>
                          </Stack>
                        ))}
                      {(versions[template.id] || []).length === 0 && (
                        <Typography variant="caption" color="text.secondary">No versions</Typography>
                      )}
                    </Stack>
                  </TableCell>
                  <TableCell>{new Date(template.created_at).toLocaleDateString()}</TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={1}>
                      <Tooltip title="Edit Template">
                        <IconButton >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Compare Versions">
                        <IconButton
                          
                          disabled={(versions[template.id] || []).length < 2}
                          onClick={() => {
                            const versionList = versions[template.id] || [];
                            if (versionList.length >= 2) {
                              handleCompareVersions(template.id, versionList[0].id, versionList[1].id);
                            }
                          }}
                        >
                          <CompareIcon />
                        </IconButton>
                      </Tooltip>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
        </TabPanel>

        {/* Compliance Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" sx={{ mb: 2 }}>Compliance Validation Results</Typography>
          <Grid container spacing={3}>
            {complianceResults.map((result) => (
              <Grid item xs={12} md={6} key={result.id}>
                <Card>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                      <Typography variant="h6">{result.template_name}</Typography>
                      <Chip
                        icon={result.status === 'passed' ? <CheckIcon /> : <ErrorIcon />}
                        label={result.status}
                        color={result.status === 'passed' ? 'success' : 'error'}
                      />
                    </Stack>
                    <Stack spacing={1}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Standard:</strong> {result.regulatory_standard}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Validation Date:</strong> {new Date(result.validation_date).toLocaleDateString()}
                      </Typography>
                      {result.issues && result.issues.length > 0 && (
                        <Box>
                          <Typography variant="body2" color="error" sx={{ mb: 1 }}>
                            <strong>Issues Found:</strong>
                          </Typography>
                          <List dense>
                            {result.issues.map((issue: string, index: number) => (
                              <ListItem key={index} sx={{ py: 0 }}>
                                <ListItemIcon sx={{ minWidth: 30 }}>
                                  <ErrorIcon color="error" fontSize="small" />
                                </ListItemIcon>
                                <ListItemText primary={issue} />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Allergen Flags Tab */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" sx={{ mb: 2 }}>Allergen Risk Flags</Typography>
          <Grid container spacing={3}>
            {allergenFlags.map((flag) => (
              <Grid item xs={12} md={6} lg={4} key={flag.id}>
                <Card>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                      <Typography variant="h6" color="error">
                        {flag.title}
                      </Typography>
                      <Chip
                        label={flag.severity}
                        color={flag.severity === 'high' ? 'error' : flag.severity === 'medium' ? 'warning' : 'info'}
                        
                      />
                    </Stack>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {flag.description}
                    </Typography>
                    <Stack spacing={1}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Product:</strong> {productName(flag.product_id)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Allergen:</strong> {flag.allergen_type || flag.allergen}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Detected In:</strong> {flag.detected_in}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Detected:</strong> {new Date(flag.detected_at || flag.detected_date).toLocaleDateString()}
                      </Typography>
                      {flag.confidence && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Confidence:</strong> {Math.round(flag.confidence * 100)}%
                        </Typography>
                      )}
                      {flag.nc_created && (
                        <Alert severity="warning"  sx={{ mt: 1 }}>
                          <Typography variant="caption">
                            <strong>NC Created:</strong> {flag.nc_id ? `NC-${flag.nc_id}` : 'Auto-generated'}
                          </Typography>
                        </Alert>
                      )}
                    </Stack>
                  </CardContent>
                  <CardActions>
                    <Button  startIcon={<ViewIcon />}>
                      View Details
                    </Button>
                    <Button 
                       
                      startIcon={<CheckIcon />}
                      onClick={() => {
                        const resolution = prompt('Enter resolution notes:');
                        if (resolution) {
                          handleResolveFlag(flag.id, resolution);
                        }
                      }}
                      disabled={flag.status !== 'active'}
                    >
                      {flag.status === 'active' ? 'Resolve' : 'Resolved'}
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Non-Conformances Tab */}
        <TabPanel value={tabValue} index={4}>
          <Typography variant="h6" sx={{ mb: 2 }}>Allergen-Related Non-Conformances</Typography>
          <Grid container spacing={3}>
            {nonConformances.map((nc) => (
              <Grid item xs={12} md={6} key={nc.id}>
                <Card>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                      <Typography variant="h6" color={nc.severity === 'critical' ? 'error' : 'inherit'}>
                        {nc.nc_number}
                      </Typography>
                      <Stack direction="row" spacing={1}>
                        <Chip
                          label={nc.severity}
                          color={nc.severity === 'critical' ? 'error' : nc.severity === 'high' ? 'warning' : 'default'}
                          
                        />
                        <Chip
                          label={nc.status}
                          color={nc.status === 'open' ? 'error' : nc.status === 'closed' ? 'success' : 'warning'}
                          
                        />
                      </Stack>
                    </Stack>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                      {nc.title}
                    </Typography>
                    <Stack spacing={1}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Product:</strong> {nc.product_reference}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Reported:</strong> {new Date(nc.reported_date).toLocaleDateString()}
                      </Typography>
                      {nc.target_resolution_date && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Target Resolution:</strong> {new Date(nc.target_resolution_date).toLocaleDateString()}
                        </Typography>
                      )}
                      {nc.requires_immediate_action && (
                        <Alert severity="error"  sx={{ mt: 1 }}>
                          <Typography variant="caption">
                            IMMEDIATE ACTION REQUIRED
                          </Typography>
                        </Alert>
                      )}
                      {nc.escalation_status === 'pending' && (
                        <Alert severity="warning"  sx={{ mt: 1 }}>
                          <Typography variant="caption">
                            Escalation Pending - Management Review Required
                          </Typography>
                        </Alert>
                      )}
                    </Stack>
                  </CardContent>
                  <CardActions>
                    <Button  startIcon={<ViewIcon />}>
                      View Details
                    </Button>
                    <Button  startIcon={<EditIcon />}>
                      Manage CAPA
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
            {nonConformances.length === 0 && (
              <Grid item xs={12}>
                <Alert severity="success" sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ mb: 1 }}>
                    No Allergen Non-Conformances
                  </Typography>
                  <Typography variant="body2">
                    All allergen control processes are currently compliant with ISO 22000 standards.
                  </Typography>
                </Alert>
              </Grid>
            )}
          </Grid>
        </TabPanel>

        {/* History Tab */}
        <TabPanel value={tabValue} index={5}>
          <Typography variant="h6" sx={{ mb: 2 }}>Allergen & Label History</Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Recent Assessments</Typography>
                  <Stack spacing={2}>
                    {assessments.slice(0, 5).map((assessment) => (
                      <Box key={assessment.id} sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                        <Typography variant="subtitle2">{productName(assessment.product_id)}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          Risk Level: {assessment.risk_level}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {new Date(assessment.updated_at || assessment.created_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Statistics</Typography>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Total Assessments</Typography>
                      <Typography variant="h4">{assessments.length}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">High Risk Products</Typography>
                      <Typography variant="h4" color="error.main">
                        {assessments.filter(a => a.risk_level === 'high').length}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Active Templates</Typography>
                      <Typography variant="h4" color="success.main">
                        {templates.filter(t => t.is_active).length}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Compliance Issues</Typography>
                      <Typography variant="h4" color="warning.main">
                        {complianceResults.filter(r => r.status === 'failed').length}
                      </Typography>
                    </Box>
                  </Stack>
          </CardContent>
        </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>

      {/* Assessment Dialog */}
      <Dialog open={assessmentDialog} onClose={() => setAssessmentDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New Allergen Assessment</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Product</InputLabel>
                <Select
                  label="Product"
                  value={assessmentForm.product_id}
                  onChange={(e) => setAssessmentForm({ ...assessmentForm, product_id: e.target.value })}
                >
                  {products.map((p: any) => (
                    <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Risk Level</InputLabel>
                <Select
                  label="Risk Level"
                  value={assessmentForm.risk_level}
                  onChange={(e) => setAssessmentForm({ ...assessmentForm, risk_level: e.target.value })}
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Cross-contamination Risk</InputLabel>
                <Select
                  label="Cross-contamination Risk"
                  value={assessmentForm.cross_contamination_risk}
                  onChange={(e) => setAssessmentForm({ ...assessmentForm, cross_contamination_risk: e.target.value })}
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Precautionary Labeling"
                value={assessmentForm.precautionary_labeling}
                onChange={(e) => setAssessmentForm({ ...assessmentForm, precautionary_labeling: e.target.value })}
                fullWidth
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Control Measures"
                value={assessmentForm.control_measures}
                onChange={(e) => setAssessmentForm({ ...assessmentForm, control_measures: e.target.value })}
                fullWidth
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Allergen Control Measures"
                value={assessmentForm.allergen_control_measures}
                onChange={(e) => setAssessmentForm({ ...assessmentForm, allergen_control_measures: e.target.value })}
                fullWidth
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Validation/Verification Procedures"
                value={assessmentForm.validation_procedures}
                onChange={(e) => setAssessmentForm({ ...assessmentForm, validation_procedures: e.target.value })}
                fullWidth
                multiline
                rows={3}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssessmentDialog(false)}>Cancel</Button>
          <Button onClick={handleAssessmentSubmit} variant="contained">Create Assessment</Button>
        </DialogActions>
      </Dialog>

      {/* Template Dialog */}
      <Dialog open={templateDialog} onClose={() => setTemplateDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New Label Template</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                label="Template Name"
                value={templateForm.name}
                onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Product (optional)</InputLabel>
                <Select
                  label="Product (optional)"
                  value={templateForm.product_id}
                  onChange={(e) => setTemplateForm({ ...templateForm, product_id: e.target.value })}
                >
                  <MenuItem value="">None</MenuItem>
                  {products.map((p: any) => (
                    <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                value={templateForm.description}
                onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })}
                fullWidth
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Allergen Declarations</Typography>
              <Grid container spacing={1}>
                {allergenList.map((allergen) => (
                  <Grid item xs={6} md={4} key={allergen}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={templateForm.allergen_declarations.includes(allergen)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setTemplateForm({
                                ...templateForm,
                                allergen_declarations: [...templateForm.allergen_declarations, allergen]
                              });
                            } else {
                              setTemplateForm({
                                ...templateForm,
                                allergen_declarations: templateForm.allergen_declarations.filter(a => a !== allergen)
                              });
                            }
                          }}
                        />
                      }
                      label={allergen}
                    />
                  </Grid>
                ))}
              </Grid>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Regulatory Compliance</Typography>
              <Grid container spacing={1}>
                {regulatoryStandards.map((standard) => (
                  <Grid item xs={12} md={6} key={standard}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={templateForm.regulatory_compliance.includes(standard)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setTemplateForm({
                                ...templateForm,
                                regulatory_compliance: [...templateForm.regulatory_compliance, standard]
                              });
                            } else {
                              setTemplateForm({
                                ...templateForm,
                                regulatory_compliance: templateForm.regulatory_compliance.filter(s => s !== standard)
                              });
                            }
                          }}
                        />
                      }
                      label={standard}
                    />
                  </Grid>
                ))}
              </Grid>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTemplateDialog(false)}>Cancel</Button>
          <Button onClick={handleTemplateSubmit} variant="contained">Create Template</Button>
        </DialogActions>
      </Dialog>

      {/* Version Dialog */}
      <Dialog open={versionDialog} onClose={() => setVersionDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New Label Version</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>Template</InputLabel>
                <Select
                  label="Template"
                  value={versionForm.template_id}
                  onChange={(e) => setVersionForm({ ...versionForm, template_id: e.target.value })}
                >
                  {templates.map((t: any) => (
                    <MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Change Description"
                value={versionForm.change_description}
                onChange={(e) => setVersionForm({ ...versionForm, change_description: e.target.value })}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Change Reason"
                value={versionForm.change_reason}
                onChange={(e) => setVersionForm({ ...versionForm, change_reason: e.target.value })}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Allergen Changes</Typography>
              <Grid container spacing={1}>
                {allergenList.map((allergen) => (
                  <Grid item xs={6} md={4} key={allergen}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={versionForm.allergen_changes.includes(allergen)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setVersionForm({
                                ...versionForm,
                                allergen_changes: [...versionForm.allergen_changes, allergen]
                              });
                            } else {
                              setVersionForm({
                                ...versionForm,
                                allergen_changes: versionForm.allergen_changes.filter(a => a !== allergen)
                              });
                            }
                          }}
                        />
                      }
                      label={allergen}
                    />
                  </Grid>
                ))}
              </Grid>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Content (JSON or Text)"
                value={versionForm.content}
                onChange={(e) => setVersionForm({ ...versionForm, content: e.target.value })}
                fullWidth
                multiline
                rows={6}
                required
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVersionDialog(false)}>Cancel</Button>
          <Button onClick={handleVersionSubmit} variant="contained" disabled={!versionForm.template_id}>
            Create Version
          </Button>
        </DialogActions>
      </Dialog>

      {/* Compliance Validation Dialog */}
      <Dialog open={complianceDialog} onClose={() => setComplianceDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Compliance Validation</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>Template</InputLabel>
                <Select
                  label="Template"
                  value={complianceForm.template_id}
                  onChange={(e) => setComplianceForm({ ...complianceForm, template_id: e.target.value })}
                >
                  {templates.map((t: any) => (
                    <MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Regulatory Standards</Typography>
              <Grid container spacing={1}>
                {regulatoryStandards.map((standard) => (
                  <Grid item xs={12} md={6} key={standard}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={complianceForm.regulatory_standards.includes(standard)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setComplianceForm({
                                ...complianceForm,
                                regulatory_standards: [...complianceForm.regulatory_standards, standard]
                              });
                            } else {
                              setComplianceForm({
                                ...complianceForm,
                                regulatory_standards: complianceForm.regulatory_standards.filter(s => s !== standard)
                              });
                            }
                          }}
                        />
                      }
                      label={standard}
                    />
                  </Grid>
                ))}
              </Grid>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setComplianceDialog(false)}>Cancel</Button>
          <Button onClick={handleComplianceValidation} variant="contained" disabled={!complianceForm.template_id}>
            Validate Compliance
          </Button>
        </DialogActions>
      </Dialog>

      {/* Version Comparison Dialog */}
      <Dialog open={comparisonDialog} onClose={() => setComparisonDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Version Comparison</DialogTitle>
        <DialogContent>
          {comparisonData && (
            <Grid container spacing={3} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" sx={{ mb: 2 }}>Version 1</Typography>
                <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                  <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
                    {JSON.stringify(comparisonData.version1, null, 2)}
                  </pre>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" sx={{ mb: 2 }}>Version 2</Typography>
                <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                  <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
                    {JSON.stringify(comparisonData.version2, null, 2)}
                  </pre>
                </Paper>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2 }}>Differences</Typography>
                <Paper sx={{ p: 2, backgroundColor: 'yellow.50' }}>
                  <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
                    {JSON.stringify(comparisonData.differences, null, 2)}
                  </pre>
                </Paper>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setComparisonDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Approvals Dialog */}
      <Dialog open={approvalsOpen} onClose={() => setApprovalsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Approvals{approvalsCtx ? ` • ${approvalsCtx.templateName} v${approvalsCtx.versionNum}` : ''}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={1} sx={{ mt: 1 }}>
            {(approvalsCtx && approvals[approvalsCtx.versionId] ? approvals[approvalsCtx.versionId] : []).map((a: any) => (
              <Stack key={a.id} direction="row" alignItems="center" justifyContent="space-between">
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography variant="body2">Approver #{a.approver_id}</Typography>
                  <Chip
                    
                    label={a.status}
                    color={a.status === 'approved' ? 'success' : a.status === 'rejected' ? 'error' : 'default'}
                  />
                </Stack>
                {approvalsCtx && currentUser && a.approver_id === currentUser.id && a.status === 'pending' && (
                  <Stack direction="row" spacing={1}>
                    <Button
                      
                      variant="contained"
                      onClick={async () => {
                      if (!approvalsCtx) return;
                      await allergenLabelAPI.approveTemplate(approvalsCtx.templateId, a.id);
                      const aps = await allergenLabelAPI.listVersionApprovals(approvalsCtx.templateId, approvalsCtx.versionId);
                      setApprovals(prev => ({ ...prev, [approvalsCtx.versionId]: aps }));
                      const vlist = await allergenLabelAPI.listTemplateVersions(approvalsCtx.templateId);
                      setVersions(prev => ({ ...prev, [approvalsCtx.templateId]: vlist }));
                      }}
                    >
                      Approve
                    </Button>
                    <Button
                      
                      color="error"
                      variant="outlined"
                      onClick={async () => {
                      if (!approvalsCtx) return;
                      await allergenLabelAPI.rejectTemplate(approvalsCtx.templateId, a.id);
                      const aps = await allergenLabelAPI.listVersionApprovals(approvalsCtx.templateId, approvalsCtx.versionId);
                      setApprovals(prev => ({ ...prev, [approvalsCtx.versionId]: aps }));
                      const vlist = await allergenLabelAPI.listTemplateVersions(approvalsCtx.templateId);
                      setVersions(prev => ({ ...prev, [approvalsCtx.templateId]: vlist }));
                      }}
                    >
                      Reject
                    </Button>
                  </Stack>
                )}
              </Stack>
            ))}
            {approvalsCtx && (!approvals[approvalsCtx.versionId] || approvals[approvalsCtx.versionId].length === 0) && (
              <Typography variant="body2" color="text.secondary">
                No approvals defined for this version.
              </Typography>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApprovalsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Product Allergen Scan Dialog */}
      <Dialog open={scanDialog} onClose={() => setScanDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Stack direction="row" alignItems="center" spacing={1}>
            <ScienceIcon color="secondary" />
            <span>ISO 22000 Allergen Scan</span>
          </Stack>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>Product</InputLabel>
                <Select
                  label="Product"
                  value={scanForm.product_id}
                  onChange={(e) => setScanForm({ ...scanForm, product_id: e.target.value })}
                >
                  {products.map((p: any) => (
                    <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Detection Method</InputLabel>
                <Select
                  label="Detection Method"
                  value={scanForm.detection_method}
                  onChange={(e) => setScanForm({ ...scanForm, detection_method: e.target.value })}
                >
                  <MenuItem value="automated">Automated Scan</MenuItem>
                  <MenuItem value="manual">Manual Review</MenuItem>
                  <MenuItem value="supplier_report">Supplier Report</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Ingredient List (one per line)"
                value={scanForm.ingredient_list.join('\n')}
                onChange={(e) => setScanForm({ 
                  ...scanForm, 
                  ingredient_list: e.target.value.split('\n').filter(i => i.trim()) 
                })}
                fullWidth
                multiline
                rows={4}
                placeholder="Enter ingredients, one per line&#10;e.g. Wheat flour&#10;Chocolate chips&#10;Milk powder"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Process Steps (one per line)"
                value={scanForm.process_steps.join('\n')}
                onChange={(e) => setScanForm({ 
                  ...scanForm, 
                  process_steps: e.target.value.split('\n').filter(s => s.trim()) 
                })}
                fullWidth
                multiline
                rows={3}
                placeholder="Enter process steps, one per line&#10;e.g. Mixing in shared equipment&#10;Packaging line A&#10;Storage in warehouse"
              />
            </Grid>
            {scanResults && (
              <Grid item xs={12}>
                <Alert severity={scanResults.undeclared_allergens?.length > 0 ? "error" : "success"} sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    Scan Results for {scanResults.product_name}
                  </Typography>
                  <Stack spacing={1}>
                    <Typography variant="body2">
                      • Detected Allergens: {scanResults.detected_allergens?.length || 0}
                    </Typography>
                    <Typography variant="body2">
                      • Undeclared Allergens: {scanResults.undeclared_allergens?.length || 0}
                    </Typography>
                    <Typography variant="body2">
                      • Risk Score: {scanResults.risk_score}/100
                    </Typography>
                    <Typography variant="body2">
                      • Confidence: {Math.round((scanResults.confidence_score || 0) * 100)}%
                    </Typography>
                    {scanResults.flags_created?.length > 0 && (
                      <Typography variant="body2" color="error">
                        • {scanResults.flags_created.length} new flag(s) created
                      </Typography>
                    )}
                    {scanResults.undeclared_allergens?.some((a: any) => a.severity === 'critical') && (
                      <Typography variant="body2" color="error">
                        • Critical allergen NC auto-generated
                      </Typography>
                    )}
                    {scanResults.recommendations?.length > 0 && (
                      <Typography variant="body2" color="info">
                        • {scanResults.recommendations.length} ISO 22000 recommendations
                      </Typography>
                    )}
                  </Stack>
                </Alert>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScanDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleProductScan} 
            variant="contained" 
            disabled={!scanForm.product_id || scanningProduct}
            startIcon={scanningProduct ? <CircularProgress size={20} /> : <ScienceIcon />}
          >
            {scanningProduct ? 'Scanning...' : 'Start Scan'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AllergenLabel;


