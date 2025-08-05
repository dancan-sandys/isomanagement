import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Close,
  Assessment,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Warning,
  Error,
  Schedule,
  Person,
  Category,
  Description,
  Timeline,
  BarChart,
  PieChart,
  TableChart,
} from '@mui/icons-material';
import { documentsAPI } from '../../services/api';

interface DocumentAnalyticsDialogProps {
  open: boolean;
  onClose: () => void;
}

interface AnalyticsData {
  total_documents: number;
  documents_by_status: Record<string, number>;
  documents_by_category: Record<string, number>;
  documents_by_type: Record<string, number>;
  documents_by_department: Record<string, number>;
  documents_by_month: Record<string, number>;
  pending_reviews: number;
  expired_documents: number;
  documents_requiring_approval: number;
  average_approval_time: number;
  top_contributors: Array<{
    name: string;
    count: number;
  }>;
  recent_activity: Array<{
    id: number;
    action: string;
    document_title: string;
    user: string;
    timestamp: string;
  }>;
}

const DocumentAnalyticsDialog: React.FC<DocumentAnalyticsDialogProps> = ({
  open,
  onClose,
}) => {
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);

  useEffect(() => {
    if (open) {
      loadAnalytics();
    }
  }, [open]);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock analytics data - in real implementation, this would come from API
      const mockAnalytics: AnalyticsData = {
        total_documents: 156,
        documents_by_status: {
          approved: 89,
          draft: 23,
          under_review: 31,
          obsolete: 8,
          archived: 5,
        },
        documents_by_category: {
          haccp: 45,
          prp: 38,
          training: 22,
          audit: 18,
          maintenance: 15,
          supplier: 12,
          quality: 6,
        },
        documents_by_type: {
          procedure: 52,
          work_instruction: 34,
          form: 28,
          policy: 18,
          manual: 12,
          checklist: 8,
          plan: 4,
        },
        documents_by_department: {
          'Quality Assurance': 67,
          'Production': 45,
          'Maintenance': 23,
          'Management': 21,
        },
        documents_by_month: {
          '2024-01': 12,
          '2024-02': 15,
          '2024-03': 18,
          '2024-04': 22,
          '2024-05': 19,
          '2024-06': 25,
          '2024-07': 28,
          '2024-08': 17,
        },
        pending_reviews: 31,
        expired_documents: 8,
        documents_requiring_approval: 31,
        average_approval_time: 3.2,
        top_contributors: [
          { name: 'John Smith', count: 23 },
          { name: 'Sarah Johnson', count: 18 },
          { name: 'Mike Davis', count: 15 },
          { name: 'Lisa Wilson', count: 12 },
          { name: 'Tom Brown', count: 10 },
        ],
        recent_activity: [
          {
            id: 1,
            action: 'Document Created',
            document_title: 'HACCP Plan for Yogurt Production',
            user: 'John Smith',
            timestamp: '2024-08-05T10:30:00Z',
          },
          {
            id: 2,
            action: 'Document Approved',
            document_title: 'Cleaning Procedure SOP',
            user: 'Sarah Johnson',
            timestamp: '2024-08-05T09:15:00Z',
          },
          {
            id: 3,
            action: 'Document Updated',
            document_title: 'Quality Control Checklist',
            user: 'Mike Davis',
            timestamp: '2024-08-05T08:45:00Z',
          },
          {
            id: 4,
            action: 'Document Created',
            document_title: 'Maintenance Schedule',
            user: 'Lisa Wilson',
            timestamp: '2024-08-04T16:20:00Z',
          },
          {
            id: 5,
            action: 'Document Approved',
            document_title: 'Supplier Evaluation Form',
            user: 'Tom Brown',
            timestamp: '2024-08-04T14:30:00Z',
          },
        ],
      };
      
      setAnalytics(mockAnalytics);
    } catch (error: any) {
      setError(error.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const handleClose = () => {
    setAnalytics(null);
    setError(null);
    setSelectedTab(0);
    onClose();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'draft':
        return 'info';
      case 'under_review':
        return 'warning';
      case 'obsolete':
      case 'archived':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const renderOverview = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Description color="primary" sx={{ fontSize: 40 }} />
              <Box>
                <Typography variant="h4" fontWeight={700}>
                  {analytics?.total_documents}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Documents
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CheckCircle color="success" sx={{ fontSize: 40 }} />
              <Box>
                <Typography variant="h4" fontWeight={700}>
                  {analytics?.documents_by_status.approved}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Approved Documents
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Warning color="warning" sx={{ fontSize: 40 }} />
              <Box>
                <Typography variant="h4" fontWeight={700}>
                  {analytics?.pending_reviews}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pending Reviews
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Error color="error" sx={{ fontSize: 40 }} />
              <Box>
                <Typography variant="h4" fontWeight={700}>
                  {analytics?.expired_documents}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Expired Documents
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderStatusBreakdown = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Documents by Status" />
          <CardContent>
            <List>
              {analytics && Object.entries(analytics.documents_by_status).map(([status, count]) => (
                <ListItem key={status}>
                  <ListItemIcon>
                    <Chip
                      label={status.replace('_', ' ')}
                      color={getStatusColor(status) as any}
                      size="small"
                    />
                  </ListItemIcon>
                  <ListItemText
                    primary={count}
                    secondary={`${((count / analytics.total_documents) * 100).toFixed(1)}%`}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Documents by Category" />
          <CardContent>
            <List>
              {analytics && Object.entries(analytics.documents_by_category).map(([category, count]) => (
                <ListItem key={category}>
                  <ListItemIcon>
                    <Category color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={category.toUpperCase()}
                    secondary={`${count} documents`}
                  />
                  <Typography variant="body2" fontWeight={600}>
                    {count}
                  </Typography>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderActivity = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Top Contributors" />
          <CardContent>
            <List>
              {analytics?.top_contributors.map((contributor, index) => (
                <ListItem key={contributor.name}>
                  <ListItemIcon>
                    <Typography variant="h6" color="primary">
                      #{index + 1}
                    </Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary={contributor.name}
                    secondary={`${contributor.count} documents`}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Recent Activity" />
          <CardContent>
            <List>
              {analytics?.recent_activity.map((activity) => (
                <ListItem key={activity.id}>
                  <ListItemIcon>
                    <Timeline color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={activity.document_title}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {activity.action} by {activity.user}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatDate(activity.timestamp)}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderTrends = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardHeader title="Document Creation Trends" />
          <CardContent>
            <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Chart visualization would be implemented here
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Assessment color="primary" />
            <Typography variant="h6">
              Document Analytics & Insights
            </Typography>
          </Box>
          <IconButton onClick={handleClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {analytics && (
          <Box>
            <Tabs value={selectedTab} onChange={handleTabChange} sx={{ mb: 3 }}>
              <Tab label="Overview" />
              <Tab label="Breakdown" />
              <Tab label="Activity" />
              <Tab label="Trends" />
            </Tabs>

            {selectedTab === 0 && renderOverview()}
            {selectedTab === 1 && renderStatusBreakdown()}
            {selectedTab === 2 && renderActivity()}
            {selectedTab === 3 && renderTrends()}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={handleClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentAnalyticsDialog; 