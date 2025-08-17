import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Checkbox,
  FormControlLabel,
  Stack,
  Alert,
  Paper,
  Chip,
} from '@mui/material';
import {
  Download,
  FilterList,
  DateRange,
  AttachFile,
  VerifiedUser,
  Science,
  Security,
} from '@mui/icons-material';

const AuditEvidenceExport: React.FC = () => {
  const [dateRange, setDateRange] = useState('30days');
  const [evidenceType, setEvidenceType] = useState('all');
  const [includeAttachments, setIncludeAttachments] = useState(true);
  const [includeSignatures, setIncludeSignatures] = useState(true);

  const dateRangeOptions = [
    { value: '7days', label: 'Last 7 Days' },
    { value: '30days', label: 'Last 30 Days' },
    { value: '90days', label: 'Last 90 Days' },
    { value: '1year', label: 'Last Year' },
    { value: 'custom', label: 'Custom Range' },
  ];

  const evidenceTypeOptions = [
    { value: 'all', label: 'All Evidence Types' },
    { value: 'monitoring', label: 'Monitoring Logs' },
    { value: 'verification', label: 'Verification Records' },
    { value: 'corrective_actions', label: 'Corrective Actions' },
    { value: 'calibration', label: 'Calibration Records' },
    { value: 'training', label: 'Training Records' },
  ];

  const handleExportEvidence = () => {
    console.log('Exporting audit evidence...');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card>
        <CardHeader
          title="Audit-Ready Evidence Export"
          subheader="Generate comprehensive evidence packages for regulatory audits"
          action={
            <Button
              variant="contained"
              startIcon={<Download />}
              onClick={handleExportEvidence}
            >
              Export Evidence Package
            </Button>
          }
        />
        <CardContent>
          {/* Export Configuration */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Export Configuration
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Date Range</InputLabel>
                  <Select
                    value={dateRange}
                    label="Date Range"
                    onChange={(e) => setDateRange(e.target.value)}
                  >
                    {dateRangeOptions.map(option => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Evidence Type</InputLabel>
                  <Select
                    value={evidenceType}
                    label="Evidence Type"
                    onChange={(e) => setEvidenceType(e.target.value)}
                  >
                    {evidenceTypeOptions.map(option => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={includeAttachments}
                      onChange={(e) => setIncludeAttachments(e.target.checked)}
                    />
                  }
                  label="Include File Attachments"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={includeSignatures}
                      onChange={(e) => setIncludeSignatures(e.target.checked)}
                    />
                  }
                  label="Include Digital Signatures"
                />
              </Grid>
            </Grid>
          </Paper>

          {/* Evidence Summary */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Evidence Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} bgcolor="info.light" borderRadius={1}>
                  <Typography variant="h4" color="info.dark">
                    1,247
                  </Typography>
                  <Typography variant="body2" color="info.dark">
                    Total Records
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} bgcolor="success.light" borderRadius={1}>
                  <Typography variant="h4" color="success.dark">
                    156
                  </Typography>
                  <Typography variant="body2" color="success.dark">
                    Monitoring Logs
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} bgcolor="warning.light" borderRadius={1}>
                  <Typography variant="h4" color="warning.dark">
                    89
                  </Typography>
                  <Typography variant="body2" color="warning.dark">
                    Verification Records
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} bgcolor="error.light" borderRadius={1}>
                  <Typography variant="h4" color="error.dark">
                    23
                  </Typography>
                  <Typography variant="body2" color="error.dark">
                    Corrective Actions
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* Compliance Checklist */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Audit Compliance Checklist
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Stack spacing={1}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip icon={<VerifiedUser />} label="Complete" color="success" size="small" />
                    <Typography variant="body2">HACCP Plan Documentation</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip icon={<Science />} label="Complete" color="success" size="small" />
                    <Typography variant="body2">Hazard Analysis Records</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip icon={<Security />} label="Complete" color="success" size="small" />
                    <Typography variant="body2">CCP Monitoring Records</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip icon={<AttachFile />} label="Complete" color="success" size="small" />
                    <Typography variant="body2">Validation Evidence</Typography>
                  </Box>
                </Stack>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Stack spacing={1}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip icon={<VerifiedUser />} label="Complete" color="success" size="small" />
                    <Typography variant="body2">Corrective Action Records</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip icon={<Science />} label="Complete" color="success" size="small" />
                    <Typography variant="body2">Verification Activities</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip icon={<Security />} label="Complete" color="success" size="small" />
                    <Typography variant="body2">Training Records</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip icon={<AttachFile />} label="Complete" color="success" size="small" />
                    <Typography variant="body2">Equipment Calibration</Typography>
                  </Box>
                </Stack>
              </Grid>
            </Grid>
          </Paper>

          {/* Export Options */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Export Options
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Alert severity="info">
                  <Typography variant="body2">
                    <strong>PDF Export:</strong> Complete audit package with all evidence and signatures
                  </Typography>
                </Alert>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Alert severity="info">
                  <Typography variant="body2">
                    <strong>Excel Export:</strong> Structured data for analysis and reporting
                  </Typography>
                </Alert>
              </Grid>
              <Grid item xs={12}>
                <Alert severity="success">
                  <Typography variant="body2">
                    <strong>Audit Ready:</strong> All evidence is properly documented, signed, and ready for regulatory review
                  </Typography>
                </Alert>
              </Grid>
            </Grid>
          </Paper>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AuditEvidenceExport;
