import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Accessibility as AccessibilityIcon,
  Speed as SpeedIcon,
  TouchApp as TouchAppIcon,
} from '@mui/icons-material';
import { uxTesting, UXTestResult } from '../../utils/uxTesting';

interface TestCategory {
  name: string;
  icon: React.ReactNode;
  color: string;
  tests: UXTestResult[];
}

const UXTestDashboard: React.FC = () => {
  const [testResults, setTestResults] = useState<UXTestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [summary, setSummary] = useState<any>(null);

  const runTests = async () => {
    setIsRunning(true);
    try {
      const results = await uxTesting.runAllTests();
      setTestResults(results);
      setSummary(uxTesting.getTestSummary());
    } catch (error) {
      console.error('UX testing failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    runTests();
  }, []);

  const getStatusIcon = (passed: boolean) => {
    return passed ? (
      <CheckCircleIcon color="success" />
    ) : (
      <ErrorIcon color="error" />
    );
  };

  const getStatusColor = (passed: boolean) => {
    return passed ? 'success' : 'error';
  };

  const categories: TestCategory[] = [
    {
      name: 'Accessibility',
      icon: <AccessibilityIcon />,
      color: '#1976d2',
      tests: testResults.filter(r => r.testName.includes('Color Contrast') || r.testName.includes('Focus') || r.testName.includes('Touch') || r.testName.includes('Keyboard') || r.testName.includes('Screen Reader')),
    },
    {
      name: 'Performance',
      icon: <SpeedIcon />,
      color: '#2e7d32',
      tests: testResults.filter(r => r.testName.includes('Performance') || r.testName.includes('Load') || r.testName.includes('Response') || r.testName.includes('Scrolling')),
    },
    {
      name: 'Usability',
      icon: <TouchAppIcon />,
      color: '#ed6c02',
      tests: testResults.filter(r => !r.testName.includes('Color Contrast') && !r.testName.includes('Focus') && !r.testName.includes('Touch') && !r.testName.includes('Keyboard') && !r.testName.includes('Screen Reader') && !r.testName.includes('Performance') && !r.testName.includes('Load') && !r.testName.includes('Response') && !r.testName.includes('Scrolling')),
    },
  ];

  const downloadReport = () => {
    const report = uxTesting.generateReport();
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ux-testing-report.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!summary) {
    return (
      <Box p={3}>
        <Typography variant="h4" gutterBottom>
          UX Testing Dashboard
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          UX Testing Dashboard
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={runTests}
            disabled={isRunning}
          >
            {isRunning ? 'Running Tests...' : 'Run Tests'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={downloadReport}
          >
            Download Report
          </Button>
        </Box>
      </Box>

      {/* Overall Score */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Overall UX Score
          </Typography>
          <Box display="flex" alignItems="center" gap={2}>
            <LinearProgress
              variant="determinate"
              value={summary.overallScore}
              sx={{ flexGrow: 1, height: 12, borderRadius: 6 }}
            />
            <Typography variant="h4" fontWeight="bold">
              {summary.overallScore.toFixed(1)}%
            </Typography>
          </Box>
          <Box display="flex" gap={2} mt={2}>
            <Chip
              label={`${summary.passed} Passed`}
              color="success"
              size="small"
            />
            <Chip
              label={`${summary.failed} Failed`}
              color="error"
              size="small"
            />
            <Chip
              label={`${summary.total} Total`}
              color="default"
              size="small"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Category Scores */}
      <Grid container spacing={3} mb={3}>
        {categories.map((category) => {
          const categoryScore = category.tests.length > 0
            ? category.tests.reduce((sum, test) => sum + test.score, 0) / category.tests.length
            : 0;

          return (
            <Grid item xs={12} md={4} key={category.name}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={1} mb={2}>
                    <Box sx={{ color: category.color }}>
                      {category.icon}
                    </Box>
                    <Typography variant="h6">
                      {category.name}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={categoryScore}
                    sx={{ height: 8, borderRadius: 4, mb: 1 }}
                  />
                  <Typography variant="h4" fontWeight="bold" color={category.color}>
                    {categoryScore.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {category.tests.length} tests
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Detailed Results */}
      {categories.map((category) => (
        <Accordion key={category.name} sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" gap={2}>
              <Box sx={{ color: category.color }}>
                {category.icon}
              </Box>
              <Typography variant="h6">
                {category.name} Tests
              </Typography>
              <Chip
                label={`${category.tests.filter(t => t.passed).length}/${category.tests.length}`}
                color={category.tests.every(t => t.passed) ? 'success' : 'warning'}
                size="small"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <List>
              {category.tests.map((test, index) => (
                <ListItem key={index} divider>
                  <ListItemIcon>
                    {getStatusIcon(test.passed)}
                  </ListItemIcon>
                  <ListItemText
                    primary={test.testName}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {test.details}
                        </Typography>
                        {test.recommendations && test.recommendations.length > 0 && (
                          <Alert severity="warning" sx={{ mt: 1 }}>
                            <Typography variant="body2">
                              Recommendations:
                            </Typography>
                            <ul style={{ margin: 0, paddingLeft: 16 }}>
                              {test.recommendations.map((rec, i) => (
                                <li key={i}>{rec}</li>
                              ))}
                            </ul>
                          </Alert>
                        )}
                      </Box>
                    }
                  />
                  <Chip
                    label={`${test.score}%`}
                    color={getStatusColor(test.passed)}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>
      ))}

      {/* Recommendations */}
      {summary.failed > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Improvement Recommendations
            </Typography>
            <Alert severity="info">
              <Typography variant="body2">
                {summary.failed} tests failed. Review the detailed results above and implement the recommended improvements to enhance user experience and accessibility.
              </Typography>
            </Alert>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default UXTestDashboard;
