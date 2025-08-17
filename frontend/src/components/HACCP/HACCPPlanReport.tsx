import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Grid,
  Chip,
  Stack,
  Alert,
} from '@mui/material';
import {
  Download,
  Print,
  Science,
  Security,
  Warning,
  CheckCircle,
} from '@mui/icons-material';

const HACCPPlanReport: React.FC = () => {
  const [reportData] = useState({
    product: {
      name: 'Chicken Breast Fillets',
      code: 'CHK-001',
      category: 'Poultry',
      approvalDate: '2024-01-15',
    },
    hazards: [
      {
        id: '1',
        name: 'Salmonella spp.',
        type: 'biological',
        likelihood: 4,
        severity: 5,
        riskScore: 20,
        riskLevel: 'critical',
        isCCP: true,
      },
      {
        id: '2',
        name: 'Campylobacter spp.',
        type: 'biological',
        likelihood: 4,
        severity: 4,
        riskScore: 16,
        riskLevel: 'high',
        isCCP: true,
      },
      {
        id: '3',
        name: 'Metal fragments',
        type: 'physical',
        likelihood: 2,
        severity: 3,
        riskScore: 6,
        riskLevel: 'medium',
        isCCP: false,
      },
    ],
    ccps: [
      {
        id: '1',
        number: 1,
        name: 'Cooking Temperature Control',
        hazard: 'Salmonella spp., Campylobacter spp.',
        criticalLimit: '74°C minimum internal temperature',
        monitoring: 'Digital thermometer reading',
        frequency: 'Every batch',
        correctiveAction: 'Stop production, adjust parameters, hold product',
      },
      {
        id: '2',
        number: 2,
        name: 'Cooling Temperature Control',
        hazard: 'Pathogenic bacteria growth',
        criticalLimit: 'Cool to 4°C within 4 hours',
        monitoring: 'Temperature monitoring and time tracking',
        frequency: 'Every batch',
        correctiveAction: 'Adjust cooling parameters, extend time if necessary',
      },
    ],
  });

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getHazardIcon = (type: string) => {
    switch (type) {
      case 'biological':
        return <Science color="error" />;
      case 'chemical':
        return <Warning color="warning" />;
      case 'physical':
        return <CheckCircle color="info" />;
      default:
        return <Warning />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card>
        <CardHeader
          title="HACCP Plan Report"
          subheader={`Product: ${reportData.product.name} (${reportData.product.code})`}
          action={
            <Stack direction="row" spacing={1}>
              <Button
                variant="outlined"
                startIcon={<Download />}
              >
                Export PDF
              </Button>
              <Button
                variant="outlined"
                startIcon={<Download />}
              >
                Export Excel
              </Button>
              <Button
                variant="contained"
                startIcon={<Print />}
              >
                Generate Report
              </Button>
            </Stack>
          }
        />
        <CardContent>
          {/* Product Information */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Product Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  <strong>Product Name:</strong> {reportData.product.name}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Product Code:</strong> {reportData.product.code}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  <strong>Category:</strong> {reportData.product.category}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  <strong>Approval Date:</strong> {reportData.product.approvalDate}
                </Typography>
              </Grid>
            </Grid>
          </Paper>

          {/* Hazard Analysis Table */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Hazard Analysis Table
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Hazard</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Likelihood</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>Risk Score</TableCell>
                    <TableCell>Risk Level</TableCell>
                    <TableCell>CCP?</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reportData.hazards.map((hazard) => (
                    <TableRow key={hazard.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getHazardIcon(hazard.type)}
                          <Typography variant="body2">
                            {hazard.name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={hazard.type}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{hazard.likelihood}</TableCell>
                      <TableCell>{hazard.severity}</TableCell>
                      <TableCell>{hazard.riskScore}</TableCell>
                      <TableCell>
                        <Chip
                          label={hazard.riskLevel.toUpperCase()}
                          size="small"
                          color={getRiskColor(hazard.riskLevel) as any}
                        />
                      </TableCell>
                      <TableCell>
                        {hazard.isCCP ? (
                          <Chip
                            icon={<Security />}
                            label="CCP"
                            color="error"
                            size="small"
                            variant="outlined"
                          />
                        ) : (
                          <Typography variant="body2" color="textSecondary">
                            No
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          {/* CCP Summary */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Critical Control Points (CCPs)
            </Typography>
            {reportData.ccps.map((ccp) => (
              <Box key={ccp.id} sx={{ mb: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                <Typography variant="h6" gutterBottom>
                  CCP {ccp.number}: {ccp.name}
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Hazard:</strong> {ccp.hazard}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Critical Limit:</strong> {ccp.criticalLimit}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Monitoring:</strong> {ccp.monitoring}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Frequency:</strong> {ccp.frequency}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Corrective Action:</strong> {ccp.correctiveAction}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            ))}
          </Paper>

          <Alert severity="info">
            This report follows FSIS guidebook structure and includes all required HACCP plan elements.
          </Alert>
        </CardContent>
      </Card>
    </Box>
  );
};

export default HACCPPlanReport;
