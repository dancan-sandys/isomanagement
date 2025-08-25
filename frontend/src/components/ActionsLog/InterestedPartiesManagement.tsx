import React, { useState, useEffect } from 'react';
import { actionsLogAPI } from '../../services/actionsLogAPI';
import { interestedPartiesAPI, InterestedParty as APIInterestedParty } from '../../services/interestedPartiesAPI';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Paper,
  Fab,
  Tabs,
  Tab,
  Rating,
  Divider,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  LinearProgress,
  Badge
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  Group as GroupIcon,
  Assessment as AssessmentIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Email as EmailIcon,
  Error as ErrorIcon,
  KeyboardArrowUp as PriorityHighIcon,
  Phone as PhoneIcon,
  LocationOn as LocationIcon,
  Language as WebsiteIcon,
  Assignment as AssignmentIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Close as CloseIcon
} from '@mui/icons-material';

interface InterestedParty {
  id: number;
  name: string;
  category: 'customer' | 'supplier' | 'regulator' | 'employee' | 'community' | 'investor' | 'competitor';
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  website?: string;
  description?: string;
  importance_level: number; // 1-5 rating
  satisfaction_level?: number; // 1-5 rating
  last_assessment_date?: string;
  next_assessment_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  expectations_count: number;
  actions_count: number;
  completed_actions_count: number;
}

interface PartyExpectation {
  id: number;
  party_id: number;
  expectation: string;
  category: 'quality' | 'delivery' | 'communication' | 'compliance' | 'innovation' | 'cost' | 'other';
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'identified' | 'addressed' | 'met' | 'exceeded';
  notes?: string;
  created_at: string;
  updated_at?: string;
}

interface PartyAction {
  id: number;
  party_id: number;
  expectation_id?: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  due_date?: string;
  completed_date?: string;
  assigned_to?: number;
  created_at: string;
  updated_at?: string;
}

interface InterestedPartiesManagementProps {
  onRefresh?: () => void;
}

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
      id={`parties-tabpanel-${index}`}
      aria-labelledby={`parties-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const InterestedPartiesManagement: React.FC<InterestedPartiesManagementProps> = ({ onRefresh }) => {
  const [parties, setParties] = useState<InterestedParty[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [selectedParty, setSelectedParty] = useState<InterestedParty | null>(null);
  const [partyActions, setPartyActions] = useState<PartyAction[]>([]);
  const [editingParty, setEditingParty] = useState<InterestedParty | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    name: '',
    category: 'customer' as 'customer' | 'supplier' | 'regulator' | 'employee' | 'community' | 'investor' | 'competitor',
    contact_person: '',
    email: '',
    phone: '',
    address: '',
    website: '',
    description: '',
    importance_level: 3,
    satisfaction_level: 3,
    is_active: true
  });

  useEffect(() => {
    loadParties();
  }, []);



  const loadParties = async () => {
    try {
      setLoading(true);
      setError(null);
      const apiParties = await interestedPartiesAPI.getInterestedParties();
      
      // Transform API response to match our interface (for now, fallback to mock data if empty)
      if (apiParties.length === 0) {
        // Use mock data as fallback
        const mockParties: InterestedParty[] = [
          {
            id: 1,
            name: 'ABC Supermarket Chain',
            category: 'customer',
            contact_person: 'John Smith',
            email: 'john.smith@abcsupermarket.com',
            phone: '+254-700-123-456',
            address: 'Nairobi, Kenya',
            website: 'www.abcsupermarket.com',
            description: 'Major retail chain with 50+ stores across Kenya',
            importance_level: 5,
            satisfaction_level: 4,
            last_assessment_date: '2025-07-15',
            next_assessment_date: '2025-10-15',
            is_active: true,
            created_at: '2025-01-15',
            expectations_count: 8,
            actions_count: 12,
            completed_actions_count: 9
          },
          {
            id: 2,
            name: 'Kenya Bureau of Standards (KEBS)',
            category: 'regulator',
            contact_person: 'Dr. Mary Wanjiku',
            email: 'mwanjiku@kebs.org',
            phone: '+254-20-694-8000',
            address: 'Nairobi, Kenya',
            website: 'www.kebs.org',
            description: 'National standards body responsible for food safety regulations',
            importance_level: 5,
            satisfaction_level: 3,
            last_assessment_date: '2025-06-20',
            next_assessment_date: '2025-09-20',
            is_active: true,
            created_at: '2025-01-10',
            expectations_count: 15,
            actions_count: 20,
            completed_actions_count: 18
          },
          {
            id: 3,
            name: 'Dairy Farmers Co-operative',
            category: 'supplier',
            contact_person: 'Peter Kamau',
            email: 'peter.kamau@dairyfarmers.co.ke',
            phone: '+254-733-456-789',
            address: 'Nakuru, Kenya',
            website: 'www.dairyfarmers.co.ke',
            description: 'Co-operative of 500+ dairy farmers supplying raw milk',
            importance_level: 4,
            satisfaction_level: 4,
            last_assessment_date: '2025-07-01',
            next_assessment_date: '2025-10-01',
            is_active: true,
            created_at: '2025-01-05',
            expectations_count: 6,
            actions_count: 8,
            completed_actions_count: 7
          }
        ];
        setParties(mockParties);
      } else {
        // Transform API parties to match our interface
        const transformedParties: InterestedParty[] = apiParties.map(party => ({
          id: party.id,
          name: party.name,
          category: party.category,
          contact_person: party.contact_person,
          email: party.contact_email,
          phone: party.contact_phone,
          address: party.address,
          website: party.website,
          description: party.description,
          importance_level: party.satisfaction_level || 3, // Use satisfaction as importance for now
          satisfaction_level: party.satisfaction_level,
          last_assessment_date: party.last_assessment_date,
          next_assessment_date: party.next_assessment_date,
          is_active: party.is_active,
          created_at: party.created_at,
          updated_at: party.updated_at,
          expectations_count: party.expectations_count || 0,
          actions_count: party.actions_count || 0,
          completed_actions_count: party.completed_actions_count || 0
        }));
        setParties(transformedParties);
      }
    } catch (err: any) {
      console.error('Error loading interested parties:', err);
      setError('Failed to load interested parties. Please try again.');
      // Fallback to mock data on error
      const mockParties: InterestedParty[] = [
        {
          id: 1,
          name: 'ABC Supermarket Chain',
          category: 'customer',
          contact_person: 'John Smith',
          email: 'john.smith@abcsupermarket.com',
          phone: '+254-700-123-456',
          address: 'Nairobi, Kenya',
          website: 'www.abcsupermarket.com',
          description: 'Major retail chain with 50+ stores across Kenya',
          importance_level: 5,
          satisfaction_level: 4,
          last_assessment_date: '2025-07-15',
          next_assessment_date: '2025-10-15',
          is_active: true,
          created_at: '2025-01-15',
          expectations_count: 8,
          actions_count: 12,
          completed_actions_count: 9
        },
        {
          id: 2,
          name: 'Kenya Bureau of Standards (KEBS)',
          category: 'regulator',
          contact_person: 'Dr. Mary Wanjiku',
          email: 'mwanjiku@kebs.org',
          phone: '+254-20-694-8000',
          address: 'Nairobi, Kenya',
          website: 'www.kebs.org',
          description: 'National standards body responsible for food safety regulations',
          importance_level: 5,
          satisfaction_level: 3,
          last_assessment_date: '2025-06-20',
          next_assessment_date: '2025-09-20',
          is_active: true,
          created_at: '2025-01-10',
          expectations_count: 15,
          actions_count: 20,
          completed_actions_count: 18
        },
        {
          id: 3,
          name: 'Dairy Farmers Co-operative',
          category: 'supplier',
          contact_person: 'Peter Kamau',
          email: 'peter.kamau@dairyfarmers.co.ke',
          phone: '+254-733-456-789',
          address: 'Nakuru, Kenya',
          website: 'www.dairyfarmers.co.ke',
          description: 'Co-operative of 500+ dairy farmers supplying raw milk',
          importance_level: 4,
          satisfaction_level: 4,
          last_assessment_date: '2025-07-01',
          next_assessment_date: '2025-10-01',
          is_active: true,
          created_at: '2025-01-05',
          expectations_count: 6,
          actions_count: 8,
          completed_actions_count: 7
        }
      ];
      setParties(mockParties);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateParty = () => {
    setEditingParty(null);
    setFormData({
      name: '',
      category: 'customer',
      contact_person: '',
      email: '',
      phone: '',
      address: '',
      website: '',
      description: '',
      importance_level: 3,
      satisfaction_level: 3,
      is_active: true
    });
    setDialogOpen(true);
  };

  const handleEditParty = (party: InterestedParty) => {
    setEditingParty(party);
    setFormData({
      name: party.name,
      category: party.category as 'customer' | 'supplier' | 'regulator' | 'employee' | 'community' | 'investor' | 'competitor',
      contact_person: party.contact_person || '',
      email: party.email || '',
      phone: party.phone || '',
      address: party.address || '',
      website: party.website || '',
      description: party.description || '',
      importance_level: party.importance_level,
      satisfaction_level: party.satisfaction_level || 3,
      is_active: party.is_active
    });
    setDialogOpen(true);
  };

  const handleSaveParty = async () => {
    try {
      // Mock save - replace with actual API call
      if (editingParty) {
        const updatedParties = parties.map(party =>
          party.id === editingParty.id
            ? { ...party, ...formData }
            : party
        );
        setParties(updatedParties);
      } else {
        const newParty: InterestedParty = {
          id: Math.max(...parties.map(p => p.id)) + 1,
          ...formData,
          created_at: new Date().toISOString(),
          expectations_count: 0,
          actions_count: 0,
          completed_actions_count: 0
        };
        setParties([...parties, newParty]);
      }

      setDialogOpen(false);
      if (onRefresh) onRefresh();
    } catch (err) {
      setError('Failed to save interested party. Please try again.');
      console.error('Error saving interested party:', err);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleViewPartyDetails = async (party: InterestedParty) => {
    setSelectedParty(party);
    setDetailViewOpen(true);
    
    // Load real actions for this party
    try {
      setLoading(true);
      const actionsData = await actionsLogAPI.getPartyActions(party.id);
      setPartyActions(actionsData.map(action => ({
        id: action.id,
        party_id: party.id,
        title: action.title,
        description: action.description,
        status: action.status === 'pending' ? 'open' : action.status as 'open' | 'in_progress' | 'completed' | 'cancelled',
        priority: action.priority,
        due_date: action.due_date,
        completed_date: action.completed_at,
        created_at: action.created_at
      })));
    } catch (err: any) {
      console.error('Error loading party actions:', err);
      setError('Failed to load actions for this party.');
      setPartyActions([]);
    } finally {
      setLoading(false);
    }
  };

  const getActionStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'pending':
        return 'warning';
      case 'cancelled':
        return 'error';
      case 'on_hold':
        return 'default';
      case 'overdue':
        return 'error';
      default:
        return 'default';
    }
  };

  const getActionPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'error';
      case 'urgent':
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

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'customer':
        return 'primary';
      case 'supplier':
        return 'secondary';
      case 'regulator':
        return 'error';
      case 'employee':
        return 'info';
      case 'community':
        return 'success';
      case 'investor':
        return 'warning';
      case 'competitor':
        return 'default';
      default:
        return 'default';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'customer':
        return <PersonIcon />;
      case 'supplier':
        return <BusinessIcon />;
      case 'regulator':
        return <AssessmentIcon />;
      case 'employee':
        return <GroupIcon />;
      case 'community':
        return <GroupIcon />;
      case 'investor':
        return <BusinessIcon />;
      case 'competitor':
        return <BusinessIcon />;
      default:
        return <PersonIcon />;
    }
  };

  const formatCategory = (category: string) => {
    return category.charAt(0).toUpperCase() + category.slice(1);
  };



  const filteredParties = () => {
    switch (activeTab) {
      case 0: // All Parties
        return parties;
      case 1: // Customers
        return parties.filter(party => party.category === 'customer');
      case 2: // Suppliers
        return parties.filter(party => party.category === 'supplier');
      case 3: // Regulators
        return parties.filter(party => party.category === 'regulator');
      case 4: // High Priority
        return parties.filter(party => party.importance_level >= 4);
      default:
        return parties;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5" component="h2">
          Interested Parties Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateParty}
        >
          Add Interested Party
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Parties Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="parties tabs">
            <Tab label="All Parties" />
            <Tab label="Customers" />
            <Tab label="Suppliers" />
            <Tab label="Regulators" />
            <Tab label="High Priority" />
          </Tabs>
        </Box>

        {/* All Parties Tab */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            {filteredParties().map((party) => (
              <Grid item xs={12} sm={6} md={4} key={party.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        {getCategoryIcon(party.category)}
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {party.name}
                        </Typography>
                      </Box>
                      <Chip
                        label={formatCategory(party.category)}
                        color={getCategoryColor(party.category) as any}
                        size="small"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {party.description}
                    </Typography>

                    {party.contact_person && (
                      <Box display="flex" alignItems="center" mb={1}>
                        <PersonIcon color="action" sx={{ mr: 1 }} fontSize="small" />
                        <Typography variant="body2">
                          {party.contact_person}
                        </Typography>
                      </Box>
                    )}

                    {party.email && (
                      <Box display="flex" alignItems="center" mb={1}>
                        <EmailIcon color="action" sx={{ mr: 1 }} fontSize="small" />
                        <Typography variant="body2">
                          {party.email}
                        </Typography>
                      </Box>
                    )}

                    <Box display="flex" alignItems="center" mb={2}>
                      <Box display="flex" alignItems="center" mr={2}>
                        <Typography variant="body2" color="text.secondary" mr={1}>
                          Importance:
                        </Typography>
                        <Rating
                          value={party.importance_level}
                          readOnly
                          size="small"
                          icon={<StarIcon color="error" />}
                          emptyIcon={<StarBorderIcon />}
                        />
                      </Box>
                      <Box display="flex" alignItems="center">
                        <Typography variant="body2" color="text.secondary" mr={1}>
                          Satisfaction:
                        </Typography>
                        <Rating
                          value={party.satisfaction_level || 0}
                          readOnly
                          size="small"
                          icon={<StarIcon color="success" />}
                          emptyIcon={<StarBorderIcon />}
                        />
                      </Box>
                    </Box>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditParty(party)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          color="info"
                          onClick={() => handleViewPartyDetails(party)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                        <IconButton size="small" color="secondary">
                          <AssessmentIcon />
                        </IconButton>
                      </Box>
                      <Chip
                        label={party.is_active ? 'Active' : 'Inactive'}
                        color={party.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Other tabs show the same filtered data */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            {filteredParties().map((party) => (
              <Grid item xs={12} sm={6} md={4} key={party.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        <PersonIcon />
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {party.name}
                        </Typography>
                      </Box>
                      <Chip label="Customer" color="primary" size="small" />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {party.description}
                    </Typography>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditParty(party)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          color="info"
                          onClick={() => handleViewPartyDetails(party)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                      <Rating
                        value={party.satisfaction_level || 0}
                        readOnly
                        size="small"
                        icon={<StarIcon color="success" />}
                        emptyIcon={<StarBorderIcon />}
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Grid container spacing={3}>
            {filteredParties().map((party) => (
              <Grid item xs={12} sm={6} md={4} key={party.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        <BusinessIcon />
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {party.name}
                        </Typography>
                      </Box>
                      <Chip label="Supplier" color="secondary" size="small" />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {party.description}
                    </Typography>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditParty(party)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          color="info"
                          onClick={() => handleViewPartyDetails(party)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                      <Rating
                        value={party.importance_level}
                        readOnly
                        size="small"
                        icon={<StarIcon color="error" />}
                        emptyIcon={<StarBorderIcon />}
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <Grid container spacing={3}>
            {filteredParties().map((party) => (
              <Grid item xs={12} sm={6} md={4} key={party.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        <AssessmentIcon />
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {party.name}
                        </Typography>
                      </Box>
                      <Chip label="Regulator" color="error" size="small" />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {party.description}
                    </Typography>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditParty(party)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          color="info"
                          onClick={() => handleViewPartyDetails(party)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Box>
                      <Chip
                        label={formatCategory(party.category)}
                        color={getCategoryColor(party.category) as any}
                        size="small"
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={4}>
          <Grid container spacing={3}>
            {filteredParties().map((party) => (
              <Grid item xs={12} sm={6} md={4} key={party.id}>
                <Card sx={{ border: '2px solid #f44336' }}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        <ErrorIcon color="error" />
                        <Typography variant="h6" sx={{ ml: 1, maxWidth: '70%' }}>
                          {party.name}
                        </Typography>
                      </Box>
                      <Chip
                        label="High Priority"
                        color="error"
                        size="small"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {party.description}
                    </Typography>

                    <Box display="flex" alignItems="center" mb={2}>
                      <Typography variant="body2" color="error" sx={{ mr: 1 }}>
                        Critical Importance:
                      </Typography>
                      <Rating
                        value={party.importance_level}
                        readOnly
                        size="small"
                        icon={<StarIcon color="error" />}
                        emptyIcon={<StarBorderIcon />}
                      />
                    </Box>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => handleEditParty(party)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          color="info"
                          onClick={() => handleViewPartyDetails(party)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                        <IconButton size="small" color="error">
                          <PriorityHighIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" color="error">
                        URGENT ATTENTION REQUIRED
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>
      </Paper>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingParty ? 'Edit Interested Party' : 'Add New Interested Party'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Party Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value as 'customer' | 'supplier' | 'regulator' | 'employee' | 'community' | 'investor' | 'competitor' })}
                  label="Category"
                >
                  <MenuItem value="customer">Customer</MenuItem>
                  <MenuItem value="supplier">Supplier</MenuItem>
                  <MenuItem value="regulator">Regulator</MenuItem>
                  <MenuItem value="employee">Employee</MenuItem>
                  <MenuItem value="community">Community</MenuItem>
                  <MenuItem value="investor">Investor</MenuItem>
                  <MenuItem value="competitor">Competitor</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Person"
                value={formData.contact_person}
                onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Website"
                value={formData.website}
                onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                margin="normal"
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Importance Level
                </Typography>
                <Rating
                  value={formData.importance_level}
                  onChange={(event, newValue) => {
                    setFormData({ ...formData, importance_level: newValue || 3 });
                  }}
                  icon={<StarIcon color="error" />}
                  emptyIcon={<StarBorderIcon />}
                />
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Satisfaction Level
                </Typography>
                <Rating
                  value={formData.satisfaction_level}
                  onChange={(event, newValue) => {
                    setFormData({ ...formData, satisfaction_level: newValue || 3 });
                  }}
                  icon={<StarIcon color="success" />}
                  emptyIcon={<StarBorderIcon />}
                />
              </Box>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                }
                label="Active"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveParty}>
            {editingParty ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Detailed View Dialog */}
      <Dialog 
        open={detailViewOpen} 
        onClose={() => setDetailViewOpen(false)} 
        maxWidth="lg" 
        fullWidth
        PaperProps={{
          sx: { minHeight: '70vh' }
        }}
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center">
              {selectedParty && getCategoryIcon(selectedParty.category)}
              <Typography variant="h5" sx={{ ml: 1 }}>
                {selectedParty?.name}
              </Typography>
            </Box>
            <IconButton onClick={() => setDetailViewOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedParty && (
            <Grid container spacing={3}>
              {/* Basic Information Card */}
              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Basic Information
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    
                    <Box display="flex" alignItems="center" mb={2}>
                      <Chip
                        label={formatCategory(selectedParty.category)}
                        color={getCategoryColor(selectedParty.category) as any}
                        icon={getCategoryIcon(selectedParty.category)}
                        sx={{ mr: 2 }}
                      />
                      <Chip
                        label={selectedParty.is_active ? 'Active' : 'Inactive'}
                        color={selectedParty.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </Box>

                    {selectedParty.description && (
                      <Box mb={2}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Description
                        </Typography>
                        <Typography variant="body1">
                          {selectedParty.description}
                        </Typography>
                      </Box>
                    )}

                    <Box display="flex" alignItems="center" mb={2}>
                      <Box display="flex" alignItems="center" mr={3}>
                        <Typography variant="body2" color="text.secondary" mr={1}>
                          Importance:
                        </Typography>
                        <Rating
                          value={selectedParty.importance_level}
                          readOnly
                          size="small"
                          icon={<StarIcon color="error" />}
                          emptyIcon={<StarBorderIcon />}
                        />
                      </Box>
                      <Box display="flex" alignItems="center">
                        <Typography variant="body2" color="text.secondary" mr={1}>
                          Satisfaction:
                        </Typography>
                        <Rating
                          value={selectedParty.satisfaction_level || 0}
                          readOnly
                          size="small"
                          icon={<StarIcon color="success" />}
                          emptyIcon={<StarBorderIcon />}
                        />
                      </Box>
                    </Box>

                    {selectedParty.last_assessment_date && (
                      <Box mb={1}>
                        <Typography variant="body2" color="text.secondary">
                          Last Assessment: {new Date(selectedParty.last_assessment_date).toLocaleDateString()}
                        </Typography>
                      </Box>
                    )}

                    {selectedParty.next_assessment_date && (
                      <Box mb={1}>
                        <Typography variant="body2" color="text.secondary">
                          Next Assessment: {new Date(selectedParty.next_assessment_date).toLocaleDateString()}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Contact Information Card */}
              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Contact Information
                    </Typography>
                    <Divider sx={{ mb: 2 }} />

                    {selectedParty.contact_person && (
                      <Box display="flex" alignItems="center" mb={2}>
                        <PersonIcon color="action" sx={{ mr: 2 }} />
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Contact Person
                          </Typography>
                          <Typography variant="body1">
                            {selectedParty.contact_person}
                          </Typography>
                        </Box>
                      </Box>
                    )}

                    {selectedParty.email && (
                      <Box display="flex" alignItems="center" mb={2}>
                        <EmailIcon color="action" sx={{ mr: 2 }} />
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Email
                          </Typography>
                          <Typography variant="body1">
                            {selectedParty.email}
                          </Typography>
                        </Box>
                      </Box>
                    )}

                    {selectedParty.phone && (
                      <Box display="flex" alignItems="center" mb={2}>
                        <PhoneIcon color="action" sx={{ mr: 2 }} />
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Phone
                          </Typography>
                          <Typography variant="body1">
                            {selectedParty.phone}
                          </Typography>
                        </Box>
                      </Box>
                    )}

                    {selectedParty.address && (
                      <Box display="flex" alignItems="center" mb={2}>
                        <LocationIcon color="action" sx={{ mr: 2 }} />
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Address
                          </Typography>
                          <Typography variant="body1">
                            {selectedParty.address}
                          </Typography>
                        </Box>
                      </Box>
                    )}

                    {selectedParty.website && (
                      <Box display="flex" alignItems="center" mb={2}>
                        <WebsiteIcon color="action" sx={{ mr: 2 }} />
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Website
                          </Typography>
                          <Typography variant="body1">
                            {selectedParty.website}
                          </Typography>
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Related Actions Card */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h6">
                        Related Actions ({partyActions.length})
                      </Typography>
                      <Badge badgeContent={partyActions.filter(a => a.status !== 'completed').length} color="primary">
                        <AssignmentIcon />
                      </Badge>
                    </Box>
                    <Divider sx={{ mb: 2 }} />

                    {partyActions.length === 0 ? (
                      <Box textAlign="center" py={4}>
                        <AssignmentIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="h6" color="text.secondary" gutterBottom>
                          No Actions Found
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          There are no actions currently linked to this interested party.
                        </Typography>
                      </Box>
                    ) : (
                      <List>
                        {partyActions.map((action, index) => (
                          <Box key={action.id}>
                            <ListItem>
                              <ListItemIcon>
                                {action.status === 'completed' ? (
                                  <CheckCircleIcon color="success" />
                                ) : action.status === 'in_progress' ? (
                                  <AssignmentIcon color="primary" />
                                ) : action.status === 'overdue' ? (
                                  <ErrorIcon color="error" />
                                ) : action.priority === 'critical' || action.priority === 'urgent' || action.priority === 'high' ? (
                                  <WarningIcon color="error" />
                                ) : (
                                  <AssignmentIcon color="action" />
                                )}
                              </ListItemIcon>
                              <ListItemText
                                primary={
                                  <Box display="flex" alignItems="center" gap={1}>
                                    <Typography variant="subtitle1">
                                      {action.title}
                                    </Typography>
                                    <Chip
                                      label={action.status.replace(/_/g, ' ').toUpperCase()}
                                      color={getActionStatusColor(action.status) as any}
                                      size="small"
                                    />
                                    <Chip
                                      label={action.priority.toUpperCase()}
                                      color={getActionPriorityColor(action.priority) as any}
                                      size="small"
                                      variant="outlined"
                                    />
                                  </Box>
                                }
                                secondary={
                                  <Box>
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                      {action.description}
                                    </Typography>
                                    <Box display="flex" alignItems="center" gap={2}>
                                      {action.due_date && (
                                        <Box display="flex" alignItems="center">
                                          <ScheduleIcon sx={{ fontSize: 16, mr: 0.5 }} />
                                          <Typography variant="caption">
                                            Due: {new Date(action.due_date).toLocaleDateString()}
                                          </Typography>
                                        </Box>
                                      )}
                                      {action.completed_date && (
                                        <Box display="flex" alignItems="center">
                                          <CheckCircleIcon sx={{ fontSize: 16, mr: 0.5 }} color="success" />
                                          <Typography variant="caption">
                                            Completed: {new Date(action.completed_date).toLocaleDateString()}
                                          </Typography>
                                        </Box>
                                      )}
                                      <Typography variant="caption" color="text.secondary">
                                        Created: {new Date(action.created_at).toLocaleDateString()}
                                      </Typography>
                                    </Box>
                                  </Box>
                                }
                              />
                              <ListItemSecondaryAction>
                                <IconButton size="small" color="primary">
                                  <VisibilityIcon />
                                </IconButton>
                              </ListItemSecondaryAction>
                            </ListItem>
                            {index < partyActions.length - 1 && <Divider />}
                          </Box>
                        ))}
                      </List>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailViewOpen(false)} variant="outlined">
            Close
          </Button>
          <Button 
            onClick={() => {
              setDetailViewOpen(false);
              handleEditParty(selectedParty!);
            }}
            variant="contained"
            startIcon={<EditIcon />}
          >
            Edit Party
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add party"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleCreateParty}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

export default InterestedPartiesManagement;

