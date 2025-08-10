import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  FormControlLabel,
  Switch,
  Checkbox,
  Radio,
  RadioGroup,
  FormLabel,
  FormGroup,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  Divider,
  Badge,
  Avatar,
  Rating,
  Slider,
  Stepper,
  Step,
  StepLabel,
  Alert as MuiAlert,
  Snackbar,
} from '@mui/material';
import {
  Save,
  Cancel,
  CheckCircle,
  Error,
  Warning,
  Info,
  Add,
  Delete,
  Edit,
  Visibility,
  Schedule,
  Notifications,
  Settings,
  Upload,
  Download,
  Archive,
  RestoreFromTrash,
  History,
  Timeline,
  Analytics,
  TrendingUp,
  TrendingDown,
  Star,
  StarBorder,
  Block,
  Pending,
  Verified,
  LocalOffer,
  Grade,
  Score,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat,
  ArrowUpward,
  ArrowDownward,
  Remove,
  ExpandMore,
  ExpandLess,
  KeyboardArrowRight,
  KeyboardArrowDown,
  Business,
  Person,
  Email,
  Phone as PhoneIcon,
  LocationOn,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  LocalShipping as LocalShippingIcon,
  Inventory as InventoryIcon,
  Science,
  Build,
  Support,
  AddCircle,
  Inventory2,
  CheckCircleOutline,
  Cancel as CancelIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  VerifiedUser,
  PendingActions,
  DoNotDisturb,
  Approval,
  Block as Reject,
  FileUpload,
  FileDownload,
  Description as DescriptionIcon,
  Category,
  Storage,
  Timer,
  HealthAndSafety as Safety,
  Coronavirus as Allergen,
  LocalOffer as LocalOfferIcon,
  QrCode,
  QrCodeScanner as Barcode,
  Receipt,
  Assignment,
  Checklist as ChecklistIcon,
  Grade as GradeIcon,
  Score as ScoreIcon,
  TrendingUp as TrendingUpIcon2,
  TrendingDown as TrendingDownIcon2,
  TrendingFlat as TrendingFlatIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Remove as RemoveIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  KeyboardArrowRight as KeyboardArrowRightIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
  CleanHands as Hygiene,
  DeviceThermostat as Temperature,
  LocalShipping,
  Build as BuildIcon,
  Security,
  Warning as WarningIcon2,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon2,
  Info as InfoIcon2,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  Schedule as ScheduleIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Archive as ArchiveIcon,
  RestoreFromTrash as RestoreFromTrashIcon,
  History as HistoryIcon,
  Timeline as TimelineIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon3,
  TrendingDown as TrendingDownIcon3,
  TrendingFlat as TrendingFlatIcon2,
  ArrowUpward as ArrowUpwardIcon2,
  ArrowDownward as ArrowDownwardIcon2,
  Remove as RemoveIcon2,
  ExpandMore as ExpandMoreIcon2,
  ExpandLess as ExpandLessIcon2,
  KeyboardArrowRight as KeyboardArrowRightIcon2,
  KeyboardArrowDown as KeyboardArrowDownIcon2,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { format, parseISO } from 'date-fns';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  InspectionChecklist,
  InspectionChecklistCreate,
  ChecklistItem,
  ChecklistItemUpdate,
  Delivery,
} from '../../types/supplier';
import { EnhancedCard } from '../UI';
import { EnhancedStatusChip } from '../UI';
import { NotificationToast } from '../UI';

interface InspectionChecklistProps {
  deliveryId: number;
  checklistId?: number;
  onSave?: (checklist: InspectionChecklist) => void;
  onCancel?: () => void;
  mode?: 'create' | 'edit' | 'view';
}

const validationSchema = Yup.object({
  delivery_id: Yup.number().required('Delivery is required'),
  checklist_type: Yup.string().required('Checklist type is required'),
  inspector: Yup.string().required('Inspector is required'),
  comments: Yup.string().max(500, 'Comments must not exceed 500 characters'),
});

const defaultChecklistItems = {
  receiving: [
    {
      item_number: 1,
      category: 'Documentation',
      description: 'Certificate of Analysis (COA)',
      requirement: 'COA must be present and valid',
      acceptable_criteria: 'COA is attached and within expiry date',
      max_score: 10,
      risk_level: 'high' as const,
    },
    {
      item_number: 2,
      category: 'Temperature Control',
      description: 'Temperature upon arrival',
      requirement: 'Temperature must be within acceptable range',
      acceptable_criteria: 'Temperature is within specified limits',
      max_score: 10,
      risk_level: 'critical' as const,
    },
    {
      item_number: 3,
      category: 'Packaging',
      description: 'Package integrity',
      requirement: 'Packaging must be intact and clean',
      acceptable_criteria: 'No damage, contamination, or leaks',
      max_score: 10,
      risk_level: 'medium' as const,
    },
    {
      item_number: 4,
      category: 'Visual Inspection',
      description: 'Product appearance',
      requirement: 'Product must meet visual quality standards',
      acceptable_criteria: 'No visible defects, mold, or contamination',
      max_score: 10,
      risk_level: 'high' as const,
    },
    {
      item_number: 5,
      category: 'Labeling',
      description: 'Product labeling',
      requirement: 'Labels must be complete and accurate',
      acceptable_criteria: 'All required information is present and legible',
      max_score: 10,
      risk_level: 'medium' as const,
    },
  ],
  storage: [
    {
      item_number: 1,
      category: 'Temperature Monitoring',
      description: 'Storage temperature control',
      requirement: 'Temperature must be maintained within limits',
      acceptable_criteria: 'Temperature logs show consistent control',
      max_score: 10,
      risk_level: 'critical' as const,
    },
    {
      item_number: 2,
      category: 'Hygiene',
      description: 'Storage area cleanliness',
      requirement: 'Storage area must be clean and organized',
      acceptable_criteria: 'No pests, debris, or contamination',
      max_score: 10,
      risk_level: 'high' as const,
    },
    {
      item_number: 3,
      category: 'Segregation',
      description: 'Product segregation',
      requirement: 'Products must be properly segregated',
      acceptable_criteria: 'No cross-contamination risks',
      max_score: 10,
      risk_level: 'medium' as const,
    },
  ],
  processing: [
    {
      item_number: 1,
      category: 'Equipment Sanitation',
      description: 'Equipment cleanliness',
      requirement: 'Equipment must be clean and sanitized',
      acceptable_criteria: 'No visible residue or contamination',
      max_score: 10,
      risk_level: 'high' as const,
    },
    {
      item_number: 2,
      category: 'Process Controls',
      description: 'Critical control points',
      requirement: 'CCPs must be monitored and controlled',
      acceptable_criteria: 'All CCPs are within limits',
      max_score: 10,
      risk_level: 'critical' as const,
    },
    {
      item_number: 3,
      category: 'Personal Hygiene',
      description: 'Employee hygiene practices',
      requirement: 'Employees must follow hygiene protocols',
      acceptable_criteria: 'Proper protective equipment and hand washing',
      max_score: 10,
      risk_level: 'high' as const,
    },
  ],
  packaging: [
    {
      item_number: 1,
      category: 'Packaging Materials',
      description: 'Packaging integrity',
      requirement: 'Packaging must be suitable and clean',
      acceptable_criteria: 'No damage or contamination',
      max_score: 10,
      risk_level: 'medium' as const,
    },
    {
      item_number: 2,
      category: 'Labeling',
      description: 'Product labeling accuracy',
      requirement: 'Labels must be accurate and complete',
      acceptable_criteria: 'All required information is present',
      max_score: 10,
      risk_level: 'high' as const,
    },
    {
      item_number: 3,
      category: 'Sealing',
      description: 'Package sealing',
      requirement: 'Packages must be properly sealed',
      acceptable_criteria: 'No leaks or compromised seals',
      max_score: 10,
      risk_level: 'medium' as const,
    },
  ],
  shipping: [
    {
      item_number: 1,
      category: 'Temperature Control',
      description: 'Shipping temperature',
      requirement: 'Temperature must be maintained during shipping',
      acceptable_criteria: 'Temperature monitoring shows control',
      max_score: 10,
      risk_level: 'critical' as const,
    },
    {
      item_number: 2,
      category: 'Packaging',
      description: 'Shipping package integrity',
      requirement: 'Packages must be secure for shipping',
      acceptable_criteria: 'No damage or compromised packaging',
      max_score: 10,
      risk_level: 'medium' as const,
    },
    {
      item_number: 3,
      category: 'Documentation',
      description: 'Shipping documentation',
      requirement: 'All shipping documents must be complete',
      acceptable_criteria: 'Required documents are present and accurate',
      max_score: 10,
      risk_level: 'medium' as const,
    },
  ],
};

const InspectionChecklistComponent: React.FC<InspectionChecklistProps> = ({
  deliveryId,
  checklistId,
  onSave,
  onCancel,
  mode = 'create',
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [checklistItems, setChecklistItems] = useState<ChecklistItem[]>([]);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ open: false, message: '', severity: 'info' });

  const steps = [
    'Checklist Setup',
    'Item Inspection',
    'Compliance Assessment',
    'Review & Complete',
  ];

  const formik = useFormik({
    initialValues: {
      delivery_id: deliveryId,
      checklist_type: 'receiving' as const,
      inspector: '',
      comments: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        const checklistData: InspectionChecklistCreate = {
          ...values,
          items: checklistItems.map(item => ({
            item_number: item.item_number,
            category: item.category,
            description: item.description,
            requirement: item.requirement,
            acceptable_criteria: item.acceptable_criteria,
            max_score: item.max_score,
            risk_level: item.risk_level,
          })),
        };

        // Here you would call your API to save the checklist
        console.log('Saving checklist:', checklistData);
        
        setNotification({
          open: true,
          message: 'Checklist saved successfully',
          severity: 'success',
        });
        
        onSave?.({
          id: checklistId || 1,
          delivery_id: deliveryId,
          checklist_type: values.checklist_type,
          status: 'completed',
          inspector: values.inspector,
          inspection_date: format(new Date(), 'yyyy-MM-dd'),
          completion_date: format(new Date(), 'yyyy-MM-dd'),
          overall_score: calculateOverallScore(),
          items: checklistItems,
          comments: values.comments,
          created_at: format(new Date(), 'yyyy-MM-dd'),
          updated_at: format(new Date(), 'yyyy-MM-dd'),
        });
      } catch (error) {
        setNotification({
          open: true,
          message: 'Failed to save checklist',
          severity: 'error',
        });
      }
    },
  });

  useEffect(() => {
    if (formik.values.checklist_type) {
      const defaultItems = defaultChecklistItems[formik.values.checklist_type];
      setChecklistItems(defaultItems.map(item => ({
        ...item,
        id: Math.random(),
        checklist_id: checklistId || 1,
        status: 'pending',
        score: 0,
        inspector_comments: '',
        corrective_action_required: false,
        corrective_action: '',
        follow_up_required: false,
        follow_up_date: '',
        verification_required: false,
        verification_completed: false,
        verification_date: '',
        verification_by: '',
        compliance_impact: 'minor',
      })));
    }
  }, [formik.values.checklist_type, checklistId]);

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      formik.submitForm();
    } else {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    formik.resetForm();
    setChecklistItems([]);
  };

  const calculateOverallScore = () => {
    if (checklistItems.length === 0) return 0;
    const totalScore = checklistItems.reduce((sum, item) => sum + (item.score || 0), 0);
    const maxPossibleScore = checklistItems.reduce((sum, item) => sum + item.max_score, 0);
    return maxPossibleScore > 0 ? (totalScore / maxPossibleScore) * 10 : 0;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed': return 'success';
      case 'failed': return 'error';
      case 'pending': return 'warning';
      case 'not_applicable': return 'default';
      default: return 'default';
    }
  };

  const getRiskLevelColor = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const handleItemUpdate = (index: number, field: keyof ChecklistItemUpdate, value: any) => {
    const updatedItems = [...checklistItems];
    updatedItems[index] = { ...updatedItems[index], [field]: value };
    setChecklistItems(updatedItems);
  };

  const renderChecklistSetup = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <FormControl fullWidth error={formik.touched.checklist_type && Boolean(formik.errors.checklist_type)}>
          <InputLabel>Checklist Type</InputLabel>
          <Select
            name="checklist_type"
            value={formik.values.checklist_type}
            label="Checklist Type"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            disabled={mode === 'view'}
          >
            <MenuItem value="receiving">Receiving Inspection</MenuItem>
            <MenuItem value="storage">Storage Inspection</MenuItem>
            <MenuItem value="processing">Processing Inspection</MenuItem>
            <MenuItem value="packaging">Packaging Inspection</MenuItem>
            <MenuItem value="shipping">Shipping Inspection</MenuItem>
          </Select>
          {formik.touched.checklist_type && formik.errors.checklist_type && (
            <FormHelperText>{formik.errors.checklist_type}</FormHelperText>
          )}
        </FormControl>
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          name="inspector"
          label="Inspector Name"
          value={formik.values.inspector}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.inspector && Boolean(formik.errors.inspector)}
          helperText={formik.touched.inspector && formik.errors.inspector}
          disabled={mode === 'view'}
          required
        />
      </Grid>
      <Grid item xs={12}>
        <TextField
          fullWidth
          multiline
          rows={3}
          name="comments"
          label="General Comments"
          value={formik.values.comments}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.comments && Boolean(formik.errors.comments)}
          helperText={formik.touched.comments && formik.errors.comments}
          disabled={mode === 'view'}
          placeholder="Enter any general comments about the inspection..."
        />
      </Grid>
    </Grid>
  );

  const renderItemInspection = () => (
    <Box>
      <Typography variant="h6" fontWeight="bold" gutterBottom>
        Inspection Items
      </Typography>
      
      {checklistItems.map((item, index) => (
        <Accordion key={index} sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box display="flex" justifyContent="space-between" alignItems="center" width="100%">
              <Box>
                <Typography variant="subtitle1" fontWeight="bold">
                  {item.description}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {item.category}
                </Typography>
              </Box>
              <Box display="flex" gap={1}>
                <Chip
                  label={item.status}
                  color={getStatusColor(item.status) as any}
                  size="small"
                />
                <Chip
                  label={`${item.score || 0}/${item.max_score}`}
                  color={item.score === item.max_score ? 'success' : 'warning'}
                  size="small"
                />
                <Chip
                  label={item.risk_level}
                  color={getRiskLevelColor(item.risk_level) as any}
                  size="small"
                  variant="outlined"
                />
              </Box>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Requirement: {item.requirement}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Acceptable Criteria: {item.acceptable_criteria}
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth disabled={mode === 'view'}>
                  <FormLabel>Status</FormLabel>
                  <RadioGroup
                    value={item.status}
                    onChange={(e) => handleItemUpdate(index, 'status', e.target.value)}
                  >
                    <FormControlLabel value="passed" control={<Radio />} label="Passed" />
                    <FormControlLabel value="failed" control={<Radio />} label="Failed" />
                    <FormControlLabel value="not_applicable" control={<Radio />} label="Not Applicable" />
                  </RadioGroup>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Score: {item.score || 0}/{item.max_score}
                </Typography>
                <Slider
                  value={item.score || 0}
                  onChange={(_, value) => handleItemUpdate(index, 'score', value)}
                  min={0}
                  max={item.max_score}
                  step={0.5}
                  disabled={mode === 'view'}
                  marks
                  valueLabelDisplay="auto"
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Inspector Comments"
                  value={item.inspector_comments}
                  onChange={(e) => handleItemUpdate(index, 'inspector_comments', e.target.value)}
                  disabled={mode === 'view'}
                  placeholder="Enter detailed comments about this inspection item..."
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={item.corrective_action_required}
                      onChange={(e) => handleItemUpdate(index, 'corrective_action_required', e.target.checked)}
                      disabled={mode === 'view'}
                    />
                  }
                  label="Corrective Action Required"
                />
              </Grid>
              
              {item.corrective_action_required && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    label="Corrective Action"
                    value={item.corrective_action}
                    onChange={(e) => handleItemUpdate(index, 'corrective_action', e.target.value)}
                    disabled={mode === 'view'}
                    placeholder="Describe the required corrective action..."
                  />
                </Grid>
              )}
              
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={item.follow_up_required}
                      onChange={(e) => handleItemUpdate(index, 'follow_up_required', e.target.checked)}
                      disabled={mode === 'view'}
                    />
                  }
                  label="Follow-up Required"
                />
              </Grid>
              
              {item.follow_up_required && (
                <Grid item xs={12} md={6}>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DatePicker
                      label="Follow-up Date"
                      value={item.follow_up_date ? parseISO(item.follow_up_date) : null}
                      onChange={(date) => handleItemUpdate(index, 'follow_up_date', date ? format(date, 'yyyy-MM-dd') : '')}
                      slotProps={{ textField: { fullWidth: true, disabled: mode === 'view' } }}
                    />
                  </LocalizationProvider>
                </Grid>
              )}
            </Grid>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );

  const renderComplianceAssessment = () => (
    <Box>
      <Typography variant="h6" fontWeight="bold" gutterBottom>
        Compliance Assessment
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <EnhancedCard title="Overall Score">
            <CardContent>
              <Typography variant="h4" fontWeight="bold" color="primary" gutterBottom>
                {calculateOverallScore().toFixed(1)}/10
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                Overall Compliance Score
              </Typography>
              <Chip
                label={calculateOverallScore() >= 8 ? 'Compliant' : calculateOverallScore() >= 6 ? 'Minor Issues' : 'Non-Compliant'}
                color={calculateOverallScore() >= 8 ? 'success' : calculateOverallScore() >= 6 ? 'warning' : 'error'}
                size="medium"
              />
            </CardContent>
          </EnhancedCard>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <EnhancedCard title="Inspection Summary">
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Summary
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Total Items:</Typography>
                  <Typography variant="body2" fontWeight="bold">{checklistItems.length}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Passed:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    {checklistItems.filter(item => item.status === 'passed').length}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Failed:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="error.main">
                    {checklistItems.filter(item => item.status === 'failed').length}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Corrective Actions:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="warning.main">
                    {checklistItems.filter(item => item.corrective_action_required).length}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Follow-ups:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="info.main">
                    {checklistItems.filter(item => item.follow_up_required).length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </EnhancedCard>
        </Grid>
        
        <Grid item xs={12}>
          <EnhancedCard title="Quality Alerts">
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Failed Items Requiring Attention
              </Typography>
              {checklistItems.filter(item => item.status === 'failed').length > 0 ? (
                <List>
                  {checklistItems.filter(item => item.status === 'failed').map((item, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Error color="error" />
                      </ListItemIcon>
                      <ListItemText
                        primary={item.description}
                        secondary={`${item.category} - Score: ${item.score}/${item.max_score}`}
                      />
                      <Chip
                        label={item.risk_level}
                        color={getRiskLevelColor(item.risk_level) as any}
                        size="small"
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No failed items
                </Typography>
              )}
            </CardContent>
          </EnhancedCard>
        </Grid>
      </Grid>
    </Box>
  );

  const renderReview = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Review Checklist
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <EnhancedCard title="Inspection Evidence">
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Checklist Information
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Type:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formik.values.checklist_type.replace('_', ' ').toUpperCase()}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Inspector:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formik.values.inspector}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Date:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {format(new Date(), 'MMM dd, yyyy')}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Overall Score:</Typography>
                  <Chip
                    label={`${calculateOverallScore().toFixed(1)}/10`}
                    color={calculateOverallScore() >= 8 ? 'success' : calculateOverallScore() >= 6 ? 'warning' : 'error'}
                    size="small"
                  />
                </Box>
              </Box>
            </CardContent>
          </EnhancedCard>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <EnhancedCard title="Next Actions">
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Compliance Status
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Status:</Typography>
                  <Chip
                    label={calculateOverallScore() >= 8 ? 'Compliant' : 'Non-Compliant'}
                    color={calculateOverallScore() >= 8 ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Items Passed:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    {checklistItems.filter(item => item.status === 'passed').length}/{checklistItems.length}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Critical Issues:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="error.main">
                    {checklistItems.filter(item => item.status === 'failed' && item.risk_level === 'critical').length}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Follow-ups:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="warning.main">
                    {checklistItems.filter(item => item.follow_up_required).length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </EnhancedCard>
        </Grid>
      </Grid>
    </Box>
  );

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return renderChecklistSetup();
      case 1:
        return renderItemInspection();
      case 2:
        return renderComplianceAssessment();
      case 3:
        return renderReview();
      default:
        return null;
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            {mode === 'create' ? 'Create Inspection Checklist' : mode === 'edit' ? 'Edit Checklist' : 'View Checklist'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {mode === 'create' ? 'Conduct a comprehensive inspection' : 
             mode === 'edit' ? 'Update inspection details' : 'Review inspection details'}
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            onClick={onCancel}
            startIcon={<Cancel />}
          >
            Cancel
          </Button>
          {mode !== 'view' && (
            <Button
              variant="contained"
              onClick={handleNext}
              startIcon={<Save />}
              disabled={!formik.isValid || formik.isSubmitting}
            >
              {activeStep === steps.length - 1 ? 'Complete Checklist' : 'Next'}
            </Button>
          )}
        </Box>
      </Box>

      {/* Stepper */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Form Content */}
      <Paper sx={{ p: 3 }}>
        <form onSubmit={formik.handleSubmit}>
          {renderStepContent(activeStep)}
          
          {/* Navigation */}
          <Box display="flex" justifyContent="space-between" mt={4}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
            >
              Back
            </Button>
            <Box display="flex" gap={2}>
              <Button
                variant="outlined"
                onClick={handleReset}
              >
                Reset
              </Button>
              {activeStep === steps.length - 1 ? (
                <Button
                  variant="contained"
                  type="submit"
                  disabled={!formik.isValid || formik.isSubmitting}
                  startIcon={<Save />}
                >
                  Complete Checklist
                </Button>
              ) : (
                <Button
                  variant="contained"
                  onClick={handleNext}
                  disabled={!formik.isValid}
                >
                  Next
                </Button>
              )}
            </Box>
          </Box>
        </form>
      </Paper>

      {/* Notification Toast */}
      <NotificationToast
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={() => setNotification({ ...notification, open: false })}
      />
    </Box>
  );
};

export default InspectionChecklistComponent; 