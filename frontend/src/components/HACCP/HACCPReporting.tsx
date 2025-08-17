import React from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Grid,
  Stack,
  Alert,
  Paper,
} from '@mui/material';
import {
  Download,
  Assessment,
  TrendingUp,
  VerifiedUser,
} from '@mui/icons-material';

const HACCPReporting: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Card>
        <CardHeader
          title="HACCP Reporting & Exports"
          subheader="Generate comprehensive reports and export data for regulatory compliance"
        />
        <CardContent>
          <Grid container spacing={3}>
            {/* HACCP Plan Report */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  HACCP Plan Report
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Generate comprehensive HACCP plan reports following FSIS guidebook structure
                </Typography>
                <Stack spacing={1}>
                  <Button
                    variant="outlined"
                    startIcon={<Download />}
                    fullWidth
                  >
                    Export PDF Report
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Download />}
                    fullWidth
                  >
                    Export Excel Report
                  </Button>
                </Stack>
              </Paper>
            </Grid>

            {/* Monitoring Trend Charts */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Monitoring Trend Charts
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Track CCP performance and compliance trends over time with interactive charts
                </Typography>
                <Stack spacing={1}>
                  <Button
                    variant="outlined"
                    startIcon={<TrendingUp />}
                    fullWidth
                  >
                    View Charts
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Download />}
                    fullWidth
                  >
                    Export Data
                  </Button>
                </Stack>
              </Paper>
            </Grid>

            {/* Audit Evidence Export */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Audit Evidence Export
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Generate audit-ready evidence packages with filters and date ranges
                </Typography>
                <Stack spacing={1}>
                  <Button
                    variant="outlined"
                    startIcon={<VerifiedUser />}
                    fullWidth
                  >
                    Export Evidence Package
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Assessment />}
                    fullWidth
                  >
                    Compliance Checklist
                  </Button>
                </Stack>
              </Paper>
            </Grid>

            {/* Compliance Dashboard */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Compliance Dashboard
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Real-time compliance metrics and performance indicators
                </Typography>
                <Stack spacing={1}>
                  <Button
                    variant="outlined"
                    startIcon={<Assessment />}
                    fullWidth
                  >
                    View Dashboard
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Download />}
                    fullWidth
                  >
                    Export Report
                  </Button>
                </Stack>
              </Paper>
            </Grid>
          </Grid>

          <Alert severity="info" sx={{ mt: 3 }}>
            All reports are generated following FDA/FSIS and ISO 22000:2018 compliance requirements.
          </Alert>
        </CardContent>
      </Card>
    </Box>
  );
};

export default HACCPReporting;
