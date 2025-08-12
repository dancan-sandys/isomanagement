import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Alert,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Divider,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  TextareaAutosize,
  Slider,
  Rating,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Checkbox,
  Radio,
  RadioGroup,
  FormLabel,
  FormGroup,
} from '@mui/material';
import {
  Save,
  Cancel,
  Add,
  Delete,
  CheckCircle,
  ExpandMore,
  LocalShipping as LocalShippingIcon,
  AttachMoney as AttachMoneyIcon,
  Phone as PhoneIcon,
  Build as BuildIcon,
  CleanHands as HygieneIcon,
  Grade as GradeIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { format, parseISO, addMonths } from 'date-fns';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  createEvaluation,
  updateEvaluation,
  fetchEvaluation,
  fetchSuppliers,
} from '../../store/slices/supplierSlice';
import { RootState, AppDispatch } from '../../store';
import { Evaluation, EvaluationCreate, EvaluationUpdate, HygieneAuditDetailCreate, Supplier } from '../../types/supplier';
import { EnhancedCard } from '../UI';
import { EnhancedStatusChip } from '../UI';
import { NotificationToast } from '../UI';

interface EvaluationFormProps {
  evaluationId?: number;
  supplierId?: number;
  onSave?: (evaluation: Evaluation) => void;
  onCancel?: () => void;
  mode?: 'create' | 'edit' | 'view';
}

const validationSchema = Yup.object({
  supplier_id: Yup.number().required('Supplier is required'),
  evaluation_period: Yup.string().required('Evaluation period is required'),
  evaluation_date: Yup.string().required('Evaluation date is required'),
  quality_score: Yup.number().min(0).max(10).required('Quality score is required'),
  delivery_score: Yup.number().min(0).max(10).required('Delivery score is required'),
  price_score: Yup.number().min(0).max(10).required('Price score is required'),
  communication_score: Yup.number().min(0).max(10).required('Communication score is required'),
  technical_support_score: Yup.number().min(0).max(10).required('Technical support score is required'),
  hygiene_score: Yup.number().min(0).max(10).required('Hygiene score is required'),
  follow_up_required: Yup.boolean(),
  follow_up_date: Yup.string()
    .nullable()
    .when('follow_up_required', {
      is: true,
      then: (schema: Yup.StringSchema<string | null | undefined>) =>
        schema.required('Follow-up date is required when follow-up is required'),
      otherwise: (schema: Yup.StringSchema<string | null | undefined>) => schema.notRequired(),
    }),
});

const hygieneAuditAreas = [
  {
    area: 'Personal Hygiene',
    description: 'Employee hygiene practices, protective clothing, hand washing',
    max_score: 10,
  },
  {
    area: 'Facility Cleanliness',
    description: 'General cleanliness, pest control, waste management',
    max_score: 10,
  },
  {
    area: 'Equipment Sanitation',
    description: 'Equipment cleaning, maintenance, sanitization procedures',
    max_score: 10,
  },
  {
    area: 'Raw Material Handling',
    description: 'Storage conditions, contamination prevention, temperature control',
    max_score: 10,
  },
  {
    area: 'Process Controls',
    description: 'HACCP implementation, critical control points, monitoring',
    max_score: 10,
  },
  {
    area: 'Documentation',
    description: 'Record keeping, procedures, training documentation',
    max_score: 10,
  },
];

const EvaluationForm: React.FC<EvaluationFormProps> = ({
  evaluationId,
  supplierId,
  onSave,
  onCancel,
  mode = 'create',
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { suppliers, selectedEvaluation, evaluationsLoading, evaluationsError } = useSelector(
    (state: RootState) => state.supplier
  );

  const [activeStep, setActiveStep] = useState(0);
  const [hygieneAuditDetails, setHygieneAuditDetails] = useState<HygieneAuditDetailCreate[]>([]);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ open: false, message: '', severity: 'info' });

  const steps = [
    'Basic Information',
    'Quality Assessment',
    'Delivery Assessment',
    'Price Assessment',
    'Communication Assessment',
    'Technical Support Assessment',
    'Hygiene Assessment',
    'Overall Assessment',
    'Review & Save',
  ];

  type EvaluationFormValues = {
    supplier_id: number;
    evaluation_period: string;
    evaluation_date: string;
    quality_score: number;
    delivery_score: number;
    price_score: number;
    communication_score: number;
    technical_support_score: number;
    hygiene_score: number;
    quality_comments: string;
    delivery_comments: string;
    price_comments: string;
    communication_comments: string;
    technical_support_comments: string;
    hygiene_comments: string;
    issues_identified: string;
    improvement_actions: string;
    follow_up_required: boolean;
    follow_up_date: string;
    compliance_score: number;
    risk_assessment_score: number;
    corrective_actions: string[];
    verification_required: boolean;
    verification_date: string;
  };

  const formik = useFormik<EvaluationFormValues>({
    initialValues: {
      supplier_id: supplierId || 0,
      evaluation_period: '',
      evaluation_date: format(new Date(), 'yyyy-MM-dd'),
      quality_score: 0,
      delivery_score: 0,
      price_score: 0,
      communication_score: 0,
      technical_support_score: 0,
      hygiene_score: 0,
      quality_comments: '',
      delivery_comments: '',
      price_comments: '',
      communication_comments: '',
      technical_support_comments: '',
      hygiene_comments: '',
      issues_identified: '',
      improvement_actions: '',
      follow_up_required: false,
      follow_up_date: '',
      compliance_score: 0,
      risk_assessment_score: 0,
      corrective_actions: [],
      verification_required: false,
      verification_date: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        const evaluationData: EvaluationCreate = {
          ...values,
          hygiene_audit_details: hygieneAuditDetails,
        };

        if (mode === 'create') {
          const response = await dispatch(createEvaluation(evaluationData)).unwrap();
          setNotification({
            open: true,
            message: 'Evaluation created successfully',
            severity: 'success',
          });
          onSave?.(response);
        } else if (mode === 'edit' && evaluationId) {
          const response = await dispatch(updateEvaluation({
            evaluationId,
            evaluationData: evaluationData as EvaluationUpdate,
          })).unwrap();
          setNotification({
            open: true,
            message: 'Evaluation updated successfully',
            severity: 'success',
          });
          onSave?.(response);
        }
      } catch (error) {
        setNotification({
          open: true,
          message: 'Failed to save evaluation',
          severity: 'error',
        });
      }
    },
  });

  useEffect(() => {
    if (evaluationId && mode !== 'create') {
      dispatch(fetchEvaluation(evaluationId));
    }
    if (!suppliers?.items?.length) {
      dispatch(fetchSuppliers());
    }
  }, [evaluationId, mode, dispatch]);

  useEffect(() => {
    if (selectedEvaluation && mode !== 'create') {
      formik.setValues({
        supplier_id: selectedEvaluation.supplier_id,
        evaluation_period: selectedEvaluation.evaluation_period,
        evaluation_date: selectedEvaluation.evaluation_date,
        quality_score: selectedEvaluation.quality_score,
        delivery_score: selectedEvaluation.delivery_score,
        price_score: selectedEvaluation.price_score,
        communication_score: selectedEvaluation.communication_score,
        technical_support_score: selectedEvaluation.technical_support_score,
        hygiene_score: selectedEvaluation.hygiene_score,
        quality_comments: selectedEvaluation.quality_comments || '',
        delivery_comments: selectedEvaluation.delivery_comments || '',
        price_comments: selectedEvaluation.price_comments || '',
        communication_comments: selectedEvaluation.communication_comments || '',
        technical_support_comments: selectedEvaluation.technical_support_comments || '',
        hygiene_comments: selectedEvaluation.hygiene_comments || '',
        issues_identified: selectedEvaluation.issues_identified || '',
        improvement_actions: selectedEvaluation.improvement_actions || '',
        follow_up_required: selectedEvaluation.follow_up_required,
        follow_up_date: selectedEvaluation.follow_up_date || '',
        compliance_score: selectedEvaluation.compliance_score || 0,
        risk_assessment_score: selectedEvaluation.risk_assessment_score || 0,
        corrective_actions: selectedEvaluation.corrective_actions || [],
        verification_required: selectedEvaluation.verification_required || false,
        verification_date: selectedEvaluation.verification_date || '',
      });

      if (selectedEvaluation.hygiene_audit_details) {
        setHygieneAuditDetails(selectedEvaluation.hygiene_audit_details.map(detail => ({
          audit_area: detail.audit_area,
          score: detail.score,
          findings: detail.findings,
          corrective_actions: detail.corrective_actions,
          follow_up_required: detail.follow_up_required,
          follow_up_date: detail.follow_up_date,
        })));
      }
    }
  }, [selectedEvaluation, mode]);

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
    setHygieneAuditDetails([]);
  };

  const calculateOverallScore = () => {
    const scores = [
      formik.values.quality_score,
      formik.values.delivery_score,
      formik.values.price_score,
      formik.values.communication_score,
      formik.values.technical_support_score,
      formik.values.hygiene_score,
    ];
    return scores.reduce((sum, score) => sum + score, 0) / scores.length;
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'success';
    if (score >= 6) return 'warning';
    return 'error';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 9) return 'Excellent';
    if (score >= 8) return 'Very Good';
    if (score >= 7) return 'Good';
    if (score >= 6) return 'Satisfactory';
    if (score >= 5) return 'Needs Improvement';
    return 'Poor';
  };

  const handleHygieneAuditChange = (index: number, field: keyof HygieneAuditDetailCreate, value: any) => {
    const updatedDetails = [...hygieneAuditDetails];
    updatedDetails[index] = { ...updatedDetails[index], [field]: value };
    setHygieneAuditDetails(updatedDetails);
  };

  const addHygieneAuditDetail = () => {
    setHygieneAuditDetails([
      ...hygieneAuditDetails,
      {
        audit_area: '',
        score: 0,
        findings: '',
        corrective_actions: '',
        follow_up_required: false,
        follow_up_date: '',
      },
    ]);
  };

  const removeHygieneAuditDetail = (index: number) => {
    const updatedDetails = hygieneAuditDetails.filter((_, i) => i !== index);
    setHygieneAuditDetails(updatedDetails);
  };

  const renderBasicInformation = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <FormControl fullWidth error={formik.touched.supplier_id && Boolean(formik.errors.supplier_id)}>
          <InputLabel>Supplier</InputLabel>
          <Select
            name="supplier_id"
            value={formik.values.supplier_id}
            label="Supplier"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            disabled={mode === 'view'}
          >
            {suppliers?.items?.map((supplier) => (
              <MenuItem key={supplier.id} value={supplier.id}>
                {supplier.name} ({supplier.supplier_code})
              </MenuItem>
            ))}
          </Select>
          {formik.touched.supplier_id && formik.errors.supplier_id && (
            <FormHelperText>{formik.errors.supplier_id}</FormHelperText>
          )}
        </FormControl>
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          name="evaluation_period"
          label="Evaluation Period"
          value={formik.values.evaluation_period}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.evaluation_period && Boolean(formik.errors.evaluation_period)}
          helperText={formik.touched.evaluation_period && formik.errors.evaluation_period}
          disabled={mode === 'view'}
          required
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <DatePicker
            label="Evaluation Date"
            value={parseISO(formik.values.evaluation_date)}
            onChange={(date) => formik.setFieldValue('evaluation_date', format(date || new Date(), 'yyyy-MM-dd'))}
            slotProps={{ textField: { fullWidth: true, disabled: mode === 'view' } }}
          />
        </LocalizationProvider>
      </Grid>
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={formik.values.follow_up_required}
              onChange={formik.handleChange}
              name="follow_up_required"
              disabled={mode === 'view'}
            />
          }
          label="Follow-up Required"
        />
      </Grid>
      {formik.values.follow_up_required && (
        <Grid item xs={12} md={6}>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DatePicker
              label="Follow-up Date"
              value={formik.values.follow_up_date ? parseISO(formik.values.follow_up_date) : null}
              onChange={(date) => formik.setFieldValue('follow_up_date', date ? format(date, 'yyyy-MM-dd') : '')}
              slotProps={{ textField: { fullWidth: true, disabled: mode === 'view' } }}
            />
          </LocalizationProvider>
        </Grid>
      )}
    </Grid>
  );

  const renderScoreAssessment = (title: string, scoreField: string, commentsField: string, icon: React.ReactElement) => (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        {icon}
        <Typography variant="h6" fontWeight="bold">
          {title}
        </Typography>
      </Box>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" gutterBottom>
            Score: {formik.values[scoreField as keyof typeof formik.values]}/10
          </Typography>
          <Slider
            value={formik.values[scoreField as keyof typeof formik.values] as number}
            onChange={(_, value) => formik.setFieldValue(scoreField, value)}
            min={0}
            max={10}
            step={0.5}
            marks
            valueLabelDisplay="auto"
            disabled={mode === 'view'}
            sx={{ mt: 2 }}
          />
          <Box display="flex" justifyContent="space-between" mt={1}>
            <Typography variant="caption" color="text.secondary">Poor</Typography>
            <Typography variant="caption" color="text.secondary">Excellent</Typography>
          </Box>
        </Grid>
        <Grid item xs={12} md={6}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <Chip
              label={getScoreLabel(formik.values[scoreField as keyof typeof formik.values] as number)}
              color={getScoreColor(formik.values[scoreField as keyof typeof formik.values] as number) as any}
              size="small"
            />
            <Rating
              value={(formik.values[scoreField as keyof typeof formik.values] as number) / 2}
              readOnly
              precision={0.5}
            />
          </Box>
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={4}
            name={commentsField}
            label={`${title} Comments`}
            value={formik.values[commentsField as keyof typeof formik.values]}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            disabled={mode === 'view'}
            placeholder={`Enter detailed comments about ${title.toLowerCase()} performance...`}
          />
        </Grid>
      </Grid>
    </Box>
  );

  const renderHygieneAssessment = () => (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <HygieneIcon color="primary" />
        <Typography variant="h6" fontWeight="bold">
          Hygiene Assessment
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" gutterBottom>
            Overall Hygiene Score: {formik.values.hygiene_score}/10
          </Typography>
          <Slider
            value={formik.values.hygiene_score}
            onChange={(_, value) => formik.setFieldValue('hygiene_score', value)}
            min={0}
            max={10}
            step={0.5}
            marks
            valueLabelDisplay="auto"
            disabled={mode === 'view'}
            sx={{ mt: 2 }}
          />
          <Box display="flex" justifyContent="space-between" mt={1}>
            <Typography variant="caption" color="text.secondary">Poor</Typography>
            <Typography variant="caption" color="text.secondary">Excellent</Typography>
          </Box>
        </Grid>
        <Grid item xs={12} md={6}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <Chip
              label={getScoreLabel(formik.values.hygiene_score)}
              color={getScoreColor(formik.values.hygiene_score) as any}
              size="small"
            />
            <Rating
              value={formik.values.hygiene_score / 2}
              readOnly
              precision={0.5}
            />
          </Box>
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={4}
            name="hygiene_comments"
            label="Hygiene Comments"
            value={formik.values.hygiene_comments}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            disabled={mode === 'view'}
            placeholder="Enter detailed comments about hygiene performance..."
          />
        </Grid>
      </Grid>

      <Box mt={4}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" fontWeight="bold">
            Detailed Hygiene Audit
          </Typography>
          {mode !== 'view' && (
            <Button
              startIcon={<Add />}
              onClick={addHygieneAuditDetail}
              variant="outlined"
              size="small"
            >
              Add Audit Area
            </Button>
          )}
        </Box>

        {hygieneAuditDetails.map((detail, index) => (
          <Accordion key={index} sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box display="flex" justifyContent="space-between" alignItems="center" width="100%">
                <Typography variant="subtitle1">
                  {detail.audit_area || `Audit Area ${index + 1}`}
                </Typography>
                <Chip
                  label={`${detail.score}/10`}
                  color={getScoreColor(detail.score) as any}
                  size="small"
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Audit Area</InputLabel>
                    <Select
                      value={detail.audit_area}
                      label="Audit Area"
                      onChange={(e) => handleHygieneAuditChange(index, 'audit_area', e.target.value)}
                      disabled={mode === 'view'}
                    >
                      {hygieneAuditAreas.map((area) => (
                        <MenuItem key={area.area} value={area.area}>
                          {area.area}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Score: {detail.score}/10
                  </Typography>
                  <Slider
                    value={detail.score}
                    onChange={(_, value) => handleHygieneAuditChange(index, 'score', value)}
                    min={0}
                    max={10}
                    step={0.5}
                    disabled={mode === 'view'}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="Findings"
                    value={detail.findings}
                    onChange={(e) => handleHygieneAuditChange(index, 'findings', e.target.value)}
                    disabled={mode === 'view'}
                    placeholder="Describe findings for this audit area..."
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    label="Corrective Actions"
                    value={detail.corrective_actions}
                    onChange={(e) => handleHygieneAuditChange(index, 'corrective_actions', e.target.value)}
                    disabled={mode === 'view'}
                    placeholder="Describe required corrective actions..."
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={detail.follow_up_required}
                        onChange={(e) => handleHygieneAuditChange(index, 'follow_up_required', e.target.checked)}
                        disabled={mode === 'view'}
                      />
                    }
                    label="Follow-up Required"
                  />
                </Grid>
                {detail.follow_up_required && (
                  <Grid item xs={12} md={6}>
                    <LocalizationProvider dateAdapter={AdapterDateFns}>
                      <DatePicker
                        label="Follow-up Date"
                        value={detail.follow_up_date ? parseISO(detail.follow_up_date) : null}
                        onChange={(date) => handleHygieneAuditChange(index, 'follow_up_date', date ? format(date, 'yyyy-MM-dd') : '')}
                        slotProps={{ textField: { fullWidth: true, disabled: mode === 'view' } }}
                      />
                    </LocalizationProvider>
                  </Grid>
                )}
                {mode !== 'view' && (
                  <Grid item xs={12}>
                    <Button
                      color="error"
                      startIcon={<Delete />}
                      onClick={() => removeHygieneAuditDetail(index)}
                      size="small"
                    >
                      Remove Audit Area
                    </Button>
                  </Grid>
                )}
              </Grid>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    </Box>
  );

  const renderOverallAssessment = () => (
    <Box>
      <Typography variant="h6" fontWeight="bold" gutterBottom>
        Overall Assessment
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <EnhancedCard title="Evaluation Overview">
            <CardContent>
              <Typography variant="h5" fontWeight="bold" color="primary" gutterBottom>
                {calculateOverallScore().toFixed(1)}/10
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                Overall Score
              </Typography>
              <Chip
                label={getScoreLabel(calculateOverallScore())}
                color={getScoreColor(calculateOverallScore()) as any}
                size="medium"
              />
              <Rating
                value={calculateOverallScore() / 2}
                readOnly
                precision={0.5}
                size="large"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </EnhancedCard>
        </Grid>
        <Grid item xs={12} md={6}>
          <Box display="flex" flexDirection="column" gap={2}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="body2">Quality</Typography>
              <Chip label={`${formik.values.quality_score}/10`} size="small" />
            </Box>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="body2">Delivery</Typography>
              <Chip label={`${formik.values.delivery_score}/10`} size="small" />
            </Box>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="body2">Price</Typography>
              <Chip label={`${formik.values.price_score}/10`} size="small" />
            </Box>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="body2">Communication</Typography>
              <Chip label={`${formik.values.communication_score}/10`} size="small" />
            </Box>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="body2">Technical Support</Typography>
              <Chip label={`${formik.values.technical_support_score}/10`} size="small" />
            </Box>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="body2">Hygiene</Typography>
              <Chip label={`${formik.values.hygiene_score}/10`} size="small" />
            </Box>
          </Box>
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={4}
            name="issues_identified"
            label="Issues Identified"
            value={formik.values.issues_identified}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            disabled={mode === 'view'}
            placeholder="List any issues or concerns identified during the evaluation..."
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={4}
            name="improvement_actions"
            label="Improvement Actions"
            value={formik.values.improvement_actions}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            disabled={mode === 'view'}
            placeholder="Describe recommended improvement actions..."
          />
        </Grid>
      </Grid>
    </Box>
  );

  const renderReview = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Review Evaluation
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <EnhancedCard title="Performance Metrics">
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Evaluation Summary
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Supplier:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {suppliers?.items?.find(s => s.id === formik.values.supplier_id)?.name}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Period:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formik.values.evaluation_period}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Date:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {format(parseISO(formik.values.evaluation_date), 'MMM dd, yyyy')}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Overall Score:</Typography>
                  <Chip
                    label={`${calculateOverallScore().toFixed(1)}/10`}
                    color={getScoreColor(calculateOverallScore()) as any}
                    size="small"
                  />
                </Box>
              </Box>
            </CardContent>
          </EnhancedCard>
        </Grid>
        <Grid item xs={12} md={6}>
          <EnhancedCard title="Attachments">
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Score Breakdown
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                {[
                  { label: 'Quality', score: formik.values.quality_score },
                  { label: 'Delivery', score: formik.values.delivery_score },
                  { label: 'Price', score: formik.values.price_score },
                  { label: 'Communication', score: formik.values.communication_score },
                  { label: 'Technical Support', score: formik.values.technical_support_score },
                  { label: 'Hygiene', score: formik.values.hygiene_score },
                ].map((item) => (
                  <Box key={item.label} display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">{item.label}</Typography>
                    <Chip
                      label={`${item.score}/10`}
                      color={getScoreColor(item.score) as any}
                      size="small"
                    />
                  </Box>
                ))}
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
        return renderBasicInformation();
      case 1:
        return renderScoreAssessment('Quality Assessment', 'quality_score', 'quality_comments', <GradeIcon color="primary" />);
      case 2:
        return renderScoreAssessment('Delivery Assessment', 'delivery_score', 'delivery_comments', <LocalShippingIcon color="primary" />);
      case 3:
        return renderScoreAssessment('Price Assessment', 'price_score', 'price_comments', <AttachMoneyIcon color="primary" />);
      case 4:
        return renderScoreAssessment('Communication Assessment', 'communication_score', 'communication_comments', <PhoneIcon color="primary" />);
      case 5:
        return renderScoreAssessment('Technical Support Assessment', 'technical_support_score', 'technical_support_comments', <BuildIcon color="primary" />);
      case 6:
        return renderHygieneAssessment();
      case 7:
        return renderOverallAssessment();
      case 8:
        return renderReview();
      default:
        return null;
    }
  };

  if (evaluationsLoading) {
    return (
      <Box>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Loading evaluation...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            {mode === 'create' ? 'Create New Evaluation' : mode === 'edit' ? 'Edit Evaluation' : 'View Evaluation'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {mode === 'create' ? 'Conduct a comprehensive supplier evaluation' : 
             mode === 'edit' ? 'Update evaluation details' : 'Review evaluation details'}
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
              {activeStep === steps.length - 1 ? 'Save Evaluation' : 'Next'}
            </Button>
          )}
        </Box>
      </Box>

      {/* Error Alert */}
      {evaluationsError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => {}}>
          {evaluationsError}
        </Alert>
      )}

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
                  Save Evaluation
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

export default EvaluationForm; 