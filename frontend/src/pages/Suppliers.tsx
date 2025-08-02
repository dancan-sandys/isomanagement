import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Fab,
  Tooltip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Badge,
  Avatar,
  LinearProgress,
  Rating,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  ListItemAvatar,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import {
  Add,
  Visibility,
  Edit,
  Delete,
  Business,
  Warning,
  CheckCircle,
  Refresh,
  Search,
  FilterList,
  Assessment,
  LocalShipping,
  Inventory,
  Description,
  Person,
  Email,
  Phone,
  Language,
  LocationOn,
  Security,
  TrendingUp,
  TrendingDown,
  Dashboard,
  List as ListIcon,
  ViewList,
  CalendarMonth,
  Work,
  AddCircle,
  Inventory2,
  Build,
  Science,
  Support,
  Star,
  StarBorder,
  ExpandMore,
  AttachFile,
  Upload,
  Download,
  Verified,
  Pending,
  Block,
  Warning as WarningIcon,
  Error,
  Info,
} from '@mui/icons-material';
import { supplierAPI } from '../services/api';

interface Supplier {
  id: number;
  supplier_code: string;
  name: string;
  status: string;
  category: string;
  contact_person: string;
  email: string;
  phone: string;
  city: string;
  country: string;
  overall_score: number;
  risk_level: string;
  last_evaluation_date?: string;
  next_evaluation_date?: string;
  materials_count: number;
  recent_evaluation_score?: number;
  recent_delivery_date?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

interface Material {
  id: number;
  material_code: string;
  name: string;
  category: string;
  is_active: boolean;
  approval_status: string;
  description?: string;
  allergens?: string[];
  storage_conditions?: string;
  shelf_life_days?: number;
}

interface Evaluation {
  id: number;
  evaluation_period: string;
  evaluation_date: string;
  status: string;
  overall_score: number;
  quality_score?: number;
  delivery_score?: number;
  price_score?: number;
  communication_score?: number;
  technical_support_score?: number;
}

interface Delivery {
  id: number;
  delivery_number: string;
  delivery_date: string;
  material_name: string;
  quantity_received: number;
  unit: string;
  inspection_status: string;
}

const Suppliers: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [deliveries, setDeliveries] = useState<Delivery[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [openSupplierDialog, setOpenSupplierDialog] = useState(false);
  const [openMaterialDialog, setOpenMaterialDialog] = useState(false);
  const [openEvaluationDialog, setOpenEvaluationDialog] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterRiskLevel, setFilterRiskLevel] = useState('');
  
  const [supplierForm, setSupplierForm] = useState({
    supplier_code: '',
    name: '',
    category: '',
    contact_person: '',
    email: '',
    phone: '',
    website: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    business_registration_number: '',
    tax_identification_number: '',
    company_type: '',
    year_established: '',
    risk_level: 'low',
    notes: '',
  });

  const [materialForm, setMaterialForm] = useState({
    material_code: '',
    name: '',
    category: '',
    description: '',
    supplier_material_code: '',
    allergens: '',
    storage_conditions: '',
    shelf_life_days: '',
    handling_instructions: '',
  });

  const [evaluationForm, setEvaluationForm] = useState({
    evaluation_period: '',
    evaluation_date: '',
    quality_score: '',
    delivery_score: '',
    price_score: '',
    communication_score: '',
    technical_support_score: '',
    quality_comments: '',
    delivery_comments: '',
    price_comments: '',
    communication_comments: '',
    technical_support_comments: '',
    issues_identified: '',
    improvement_actions: '',
    follow_up_required: false,
    follow_up_date: '',
  });

  const [dashboardData, setDashboardData] = useState({
    total_suppliers: 0,
    active_suppliers: 0,
    overdue_evaluations: 0,
    suppliers_by_category: [],
    suppliers_by_risk: [],
    recent_evaluations: [],
    recent_deliveries: [],
  });

  const categoryIcons: { [key: string]: React.ReactElement } = {
    raw_milk: <Inventory />,
    additives: <AddCircle />,
    cultures: <Science />,
    packaging: <Inventory2 />,
    equipment: <Build />,
    chemicals: <Science />,
    services: <Support />,
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'suspended': return 'warning';
      case 'pending_approval': return 'info';
      case 'blacklisted': return 'error';
      default: return 'default';
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'default';
    }
  };

  const getCategoryDisplayName = (category: string) => {
    return category?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
  };

  const getStatusDisplayName = (status: string) => {
    return status?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
  };

  const getInspectionStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'passed': return 'success';
      case 'failed': return 'error';
      case 'pending': return 'warning';
      case 'quarantined': return 'error';
      default: return 'default';
    }
  };

  // Mock data for now - replace with actual API calls
  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setLoading(false);
      // Mock data
      setSuppliers([
        {
          id: 1,
          supplier_code: 'SUP001',
          name: 'Dairy Fresh Suppliers Ltd',
          status: 'active',
          category: 'raw_milk',
          contact_person: 'John Smith',
          email: 'john@dairyfresh.com',
          phone: '+1-555-0123',
          city: 'Toronto',
          country: 'Canada',
          overall_score: 4.2,
          risk_level: 'low',
          last_evaluation_date: '2024-01-15',
          next_evaluation_date: '2025-01-15',
          materials_count: 3,
          recent_evaluation_score: 4.2,
          recent_delivery_date: '2024-03-20',
          created_by: 'Admin User',
          created_at: '2023-01-01',
          updated_at: '2024-01-15',
        },
        {
          id: 2,
          supplier_code: 'SUP002',
          name: 'Packaging Solutions Inc',
          status: 'active',
          category: 'packaging',
          contact_person: 'Sarah Johnson',
          email: 'sarah@packaging.com',
          phone: '+1-555-0456',
          city: 'Vancouver',
          country: 'Canada',
          overall_score: 3.8,
          risk_level: 'medium',
          last_evaluation_date: '2024-02-10',
          next_evaluation_date: '2025-02-10',
          materials_count: 5,
          recent_evaluation_score: 3.8,
          recent_delivery_date: '2024-03-18',
          created_by: 'Admin User',
          created_at: '2023-02-01',
          updated_at: '2024-02-10',
        },
      ]);
    }, 1000);
  }, []);

  const filteredSuppliers = suppliers.filter(supplier => {
    const matchesSearch = !searchTerm || 
      supplier.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      supplier.supplier_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      supplier.contact_person.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = !filterCategory || supplier.category === filterCategory;
    const matchesStatus = !filterStatus || supplier.status === filterStatus;
    const matchesRiskLevel = !filterRiskLevel || supplier.risk_level === filterRiskLevel;
    
    return matchesSearch && matchesCategory && matchesStatus && matchesRiskLevel;
  });

  const renderDashboard = () => (
    <Grid container spacing={3} mb={3}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Suppliers
                </Typography>
                <Typography variant="h4">
                  {dashboardData.total_suppliers || suppliers.length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {dashboardData.active_suppliers || suppliers.filter(s => s.status === 'active').length} active
                </Typography>
              </Box>
              <Business color="primary" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Overdue Evaluations
                </Typography>
                <Typography variant="h4">
                  {dashboardData.overdue_evaluations || 2}
                </Typography>
                <Typography variant="body2" color="error">
                  Requires attention
                </Typography>
              </Box>
              <Warning color="error" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Average Score
                </Typography>
                <Typography variant="h4">
                  {suppliers.length > 0 
                    ? (suppliers.reduce((sum, s) => sum + s.overall_score, 0) / suppliers.length).toFixed(1)
                    : '0.0'
                  }
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Out of 5.0
                </Typography>
              </Box>
              <Star color="warning" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  High Risk Suppliers
                </Typography>
                <Typography variant="h4">
                  {suppliers.filter(s => s.risk_level === 'high').length}
                </Typography>
                <Typography variant="body2" color="error">
                  Monitor closely
                </Typography>
              </Box>
              <Error color="error" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderSuppliersList = () => (
    <Paper>
      <Box p={2}>
        <Grid container spacing={2} alignItems="center" mb={2}>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              placeholder="Search suppliers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={filterCategory}
                label="Category"
                onChange={(e) => setFilterCategory(e.target.value)}
              >
                <MenuItem value="">All Categories</MenuItem>
                <MenuItem value="raw_milk">Raw Milk</MenuItem>
                <MenuItem value="additives">Additives</MenuItem>
                <MenuItem value="cultures">Cultures</MenuItem>
                <MenuItem value="packaging">Packaging</MenuItem>
                <MenuItem value="equipment">Equipment</MenuItem>
                <MenuItem value="chemicals">Chemicals</MenuItem>
                <MenuItem value="services">Services</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                label="Status"
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
                <MenuItem value="suspended">Suspended</MenuItem>
                <MenuItem value="pending_approval">Pending Approval</MenuItem>
                <MenuItem value="blacklisted">Blacklisted</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Risk Level</InputLabel>
              <Select
                value={filterRiskLevel}
                label="Risk Level"
                onChange={(e) => setFilterRiskLevel(e.target.value)}
              >
                <MenuItem value="">All Risk Levels</MenuItem>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Refresh />}
              onClick={() => {
                setSearchTerm('');
                setFilterCategory('');
                setFilterStatus('');
                setFilterRiskLevel('');
              }}
            >
              Reset Filters
            </Button>
          </Grid>
        </Grid>
      </Box>
      
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Supplier</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Risk Level</TableCell>
              <TableCell>Score</TableCell>
              <TableCell>Materials</TableCell>
              <TableCell>Last Evaluation</TableCell>
              <TableCell>Next Evaluation</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={9} align="center">
                  <LinearProgress />
                  <Typography sx={{ mt: 1 }}>Loading suppliers...</Typography>
                </TableCell>
              </TableRow>
            ) : filteredSuppliers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No suppliers found
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={() => setOpenSupplierDialog(true)}
                    sx={{ mt: 2 }}
                  >
                    Add First Supplier
                  </Button>
                </TableCell>
              </TableRow>
            ) : (
              filteredSuppliers.map((supplier) => (
                <TableRow key={supplier.id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {supplier.supplier_code}
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {supplier.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {supplier.contact_person} • {supplier.city}, {supplier.country}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      icon={categoryIcons[supplier.category]}
                      label={getCategoryDisplayName(supplier.category)}
                      color="primary"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusDisplayName(supplier.status)}
                      color={getStatusColor(supplier.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={supplier.risk_level.toUpperCase()}
                      color={getRiskLevelColor(supplier.risk_level) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Rating 
                        value={supplier.overall_score} 
                        readOnly 
                        size="small"
                        precision={0.1}
                      />
                      <Typography variant="body2">
                        {supplier.overall_score.toFixed(1)}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {supplier.materials_count} materials
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {supplier.last_evaluation_date ? (
                      <Typography variant="body2">
                        {new Date(supplier.last_evaluation_date).toLocaleDateString()}
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        Never
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {supplier.next_evaluation_date ? (
                      <Typography 
                        variant="body2" 
                        color={new Date(supplier.next_evaluation_date) < new Date() ? 'error' : 'inherit'}
                      >
                        {new Date(supplier.next_evaluation_date).toLocaleDateString()}
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        Not scheduled
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="center">
                    <Box display="flex" gap={1}>
                      <Tooltip title="View Details">
                        <IconButton size="small">
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Add Material">
                        <IconButton 
                          size="small"
                          onClick={() => {
                            setSelectedSupplier(supplier);
                            setOpenMaterialDialog(true);
                          }}
                        >
                          <Add />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );

  const renderMaterialsList = () => (
    <Paper>
      <Box p={2}>
        <Typography variant="h6" gutterBottom>
          Materials Management
        </Typography>
        <Typography variant="body2" color="text.secondary" mb={2}>
          Track all materials provided by suppliers including specifications, allergens, and quality parameters
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenMaterialDialog(true)}
          sx={{ mb: 2 }}
        >
          Add Material
        </Button>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Material</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Supplier</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Allergens</TableCell>
                <TableCell>Shelf Life</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No materials found. Add materials to suppliers to see them here.
                  </Typography>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Paper>
  );

  const renderEvaluationsList = () => (
    <Paper>
      <Box p={2}>
        <Typography variant="h6" gutterBottom>
          Supplier Evaluations
        </Typography>
        <Typography variant="body2" color="text.secondary" mb={2}>
          Track supplier performance evaluations and quality assessments
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenEvaluationDialog(true)}
          sx={{ mb: 2 }}
        >
          New Evaluation
        </Button>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Supplier</TableCell>
                <TableCell>Period</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Overall Score</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Follow-up</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No evaluations found. Create evaluations to track supplier performance.
                  </Typography>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Paper>
  );

  const renderDeliveriesList = () => (
    <Paper>
      <Box p={2}>
        <Typography variant="h6" gutterBottom>
          Incoming Deliveries
        </Typography>
        <Typography variant="body2" color="text.secondary" mb={2}>
          Track incoming material deliveries, inspections, and quality control
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          sx={{ mb: 2 }}
        >
          Record Delivery
        </Button>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Delivery</TableCell>
                <TableCell>Supplier</TableCell>
                <TableCell>Material</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Inspection</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No deliveries found. Record incoming deliveries to track material flow.
                  </Typography>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Paper>
  );

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Supplier Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage suppliers, materials, evaluations, and incoming deliveries for food safety compliance
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenSupplierDialog(true)}
          size="large"
        >
          New Supplier
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {renderDashboard()}

      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={(e, newValue) => setActiveTab(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab 
            icon={<Dashboard />} 
            label="Overview" 
            iconPosition="start"
          />
          <Tab 
            icon={<Business />} 
            label="Suppliers" 
            iconPosition="start"
          />
          <Tab 
            icon={<Inventory />} 
            label="Materials" 
            iconPosition="start"
          />
          <Tab 
            icon={<Assessment />} 
            label="Evaluations" 
            iconPosition="start"
          />
          <Tab 
            icon={<LocalShipping />} 
            label="Deliveries" 
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                <List>
                  <ListItem divider>
                    <ListItemIcon>
                      <Assessment color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Dairy Fresh Suppliers Ltd - Q1 2024 Evaluation"
                      secondary="Overall Score: 4.2/5.0 • Completed on March 15, 2024"
                    />
                    <Chip label="COMPLETED" color="success" size="small" />
                  </ListItem>
                  <ListItem divider>
                    <ListItemIcon>
                      <LocalShipping color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Raw Milk Delivery - SUP001"
                      secondary="Quantity: 5000L • Inspection: Passed • March 20, 2024"
                    />
                    <Chip label="PASSED" color="success" size="small" />
                  </ListItem>
                  <ListItem divider>
                    <ListItemIcon>
                      <Warning color="warning" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Packaging Solutions Inc - Evaluation Due"
                      secondary="Next evaluation due on April 10, 2024"
                    />
                    <Chip label="OVERDUE" color="error" size="small" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Box display="flex" flexDirection="column" gap={2}>
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={() => setOpenSupplierDialog(true)}
                    fullWidth
                  >
                    Add New Supplier
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Assessment />}
                    onClick={() => setOpenEvaluationDialog(true)}
                    fullWidth
                  >
                    Create Evaluation
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<LocalShipping />}
                    fullWidth
                  >
                    Record Delivery
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Description />}
                    fullWidth
                  >
                    Generate Reports
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && renderSuppliersList()}
      {activeTab === 2 && renderMaterialsList()}
      {activeTab === 3 && renderEvaluationsList()}
      {activeTab === 4 && renderDeliveriesList()}

      {/* Create Supplier Dialog */}
      <Dialog open={openSupplierDialog} onClose={() => setOpenSupplierDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New Supplier</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} pt={1}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Supplier Code"
                  fullWidth
                  value={supplierForm.supplier_code}
                  onChange={(e) => setSupplierForm({ ...supplierForm, supplier_code: e.target.value })}
                  required
                  helperText="Unique identifier for the supplier"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Supplier Name"
                  fullWidth
                  value={supplierForm.name}
                  onChange={(e) => setSupplierForm({ ...supplierForm, name: e.target.value })}
                  required
                />
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={supplierForm.category}
                    label="Category"
                    onChange={(e) => setSupplierForm({ ...supplierForm, category: e.target.value })}
                  >
                    <MenuItem value="raw_milk">Raw Milk</MenuItem>
                    <MenuItem value="additives">Additives</MenuItem>
                    <MenuItem value="cultures">Cultures</MenuItem>
                    <MenuItem value="packaging">Packaging</MenuItem>
                    <MenuItem value="equipment">Equipment</MenuItem>
                    <MenuItem value="chemicals">Chemicals</MenuItem>
                    <MenuItem value="services">Services</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Risk Level</InputLabel>
                  <Select
                    value={supplierForm.risk_level}
                    label="Risk Level"
                    onChange={(e) => setSupplierForm({ ...supplierForm, risk_level: e.target.value })}
                  >
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
            <Typography variant="h6" sx={{ mt: 2 }}>Contact Information</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Contact Person"
                  fullWidth
                  value={supplierForm.contact_person}
                  onChange={(e) => setSupplierForm({ ...supplierForm, contact_person: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Email"
                  fullWidth
                  type="email"
                  value={supplierForm.email}
                  onChange={(e) => setSupplierForm({ ...supplierForm, email: e.target.value })}
                />
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Phone"
                  fullWidth
                  value={supplierForm.phone}
                  onChange={(e) => setSupplierForm({ ...supplierForm, phone: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Website"
                  fullWidth
                  value={supplierForm.website}
                  onChange={(e) => setSupplierForm({ ...supplierForm, website: e.target.value })}
                />
              </Grid>
            </Grid>
            <Typography variant="h6" sx={{ mt: 2 }}>Address</Typography>
            <TextField
              label="Address Line 1"
              fullWidth
              value={supplierForm.address_line1}
              onChange={(e) => setSupplierForm({ ...supplierForm, address_line1: e.target.value })}
            />
            <TextField
              label="Address Line 2"
              fullWidth
              value={supplierForm.address_line2}
              onChange={(e) => setSupplierForm({ ...supplierForm, address_line2: e.target.value })}
            />
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField
                  label="City"
                  fullWidth
                  value={supplierForm.city}
                  onChange={(e) => setSupplierForm({ ...supplierForm, city: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="State/Province"
                  fullWidth
                  value={supplierForm.state}
                  onChange={(e) => setSupplierForm({ ...supplierForm, state: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Postal Code"
                  fullWidth
                  value={supplierForm.postal_code}
                  onChange={(e) => setSupplierForm({ ...supplierForm, postal_code: e.target.value })}
                />
              </Grid>
            </Grid>
            <TextField
              label="Country"
              fullWidth
              value={supplierForm.country}
              onChange={(e) => setSupplierForm({ ...supplierForm, country: e.target.value })}
            />
            <Typography variant="h6" sx={{ mt: 2 }}>Business Information</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Business Registration Number"
                  fullWidth
                  value={supplierForm.business_registration_number}
                  onChange={(e) => setSupplierForm({ ...supplierForm, business_registration_number: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Tax Identification Number"
                  fullWidth
                  value={supplierForm.tax_identification_number}
                  onChange={(e) => setSupplierForm({ ...supplierForm, tax_identification_number: e.target.value })}
                />
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Company Type"
                  fullWidth
                  value={supplierForm.company_type}
                  onChange={(e) => setSupplierForm({ ...supplierForm, company_type: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Year Established"
                  fullWidth
                  type="number"
                  value={supplierForm.year_established}
                  onChange={(e) => setSupplierForm({ ...supplierForm, year_established: e.target.value })}
                />
              </Grid>
            </Grid>
            <TextField
              label="Notes"
              fullWidth
              multiline
              rows={3}
              value={supplierForm.notes}
              onChange={(e) => setSupplierForm({ ...supplierForm, notes: e.target.value })}
              helperText="Additional notes about the supplier"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenSupplierDialog(false)}>Cancel</Button>
          <Button variant="contained">
            Create Supplier
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Material Dialog */}
      <Dialog open={openMaterialDialog} onClose={() => setOpenMaterialDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Add New Material
          {selectedSupplier && (
            <Typography variant="body2" color="text.secondary">
              for {selectedSupplier.name}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} pt={1}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Material Code"
                  fullWidth
                  value={materialForm.material_code}
                  onChange={(e) => setMaterialForm({ ...materialForm, material_code: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Material Name"
                  fullWidth
                  value={materialForm.name}
                  onChange={(e) => setMaterialForm({ ...materialForm, name: e.target.value })}
                  required
                />
              </Grid>
            </Grid>
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={materialForm.description}
              onChange={(e) => setMaterialForm({ ...materialForm, description: e.target.value })}
            />
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Category"
                  fullWidth
                  value={materialForm.category}
                  onChange={(e) => setMaterialForm({ ...materialForm, category: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Supplier Material Code"
                  fullWidth
                  value={materialForm.supplier_material_code}
                  onChange={(e) => setMaterialForm({ ...materialForm, supplier_material_code: e.target.value })}
                />
              </Grid>
            </Grid>
            <TextField
              label="Allergens"
              fullWidth
              value={materialForm.allergens}
              onChange={(e) => setMaterialForm({ ...materialForm, allergens: e.target.value })}
              helperText="List allergens separated by commas"
            />
            <TextField
              label="Storage Conditions"
              fullWidth
              value={materialForm.storage_conditions}
              onChange={(e) => setMaterialForm({ ...materialForm, storage_conditions: e.target.value })}
            />
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Shelf Life (days)"
                  fullWidth
                  type="number"
                  value={materialForm.shelf_life_days}
                  onChange={(e) => setMaterialForm({ ...materialForm, shelf_life_days: e.target.value })}
                />
              </Grid>
            </Grid>
            <TextField
              label="Handling Instructions"
              fullWidth
              multiline
              rows={3}
              value={materialForm.handling_instructions}
              onChange={(e) => setMaterialForm({ ...materialForm, handling_instructions: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenMaterialDialog(false)}>Cancel</Button>
          <Button variant="contained">
            Create Material
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Evaluation Dialog */}
      <Dialog open={openEvaluationDialog} onClose={() => setOpenEvaluationDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Supplier Evaluation</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} pt={1}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Evaluation Period"
                  fullWidth
                  value={evaluationForm.evaluation_period}
                  onChange={(e) => setEvaluationForm({ ...evaluationForm, evaluation_period: e.target.value })}
                  required
                  helperText="e.g., Q1 2024"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Evaluation Date"
                  type="date"
                  fullWidth
                  value={evaluationForm.evaluation_date}
                  onChange={(e) => setEvaluationForm({ ...evaluationForm, evaluation_date: e.target.value })}
                  required
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
            <Typography variant="h6">Evaluation Scores (1-5 scale)</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Quality Score"
                  type="number"
                  fullWidth
                  value={evaluationForm.quality_score}
                  onChange={(e) => setEvaluationForm({ ...evaluationForm, quality_score: e.target.value })}
                  inputProps={{ min: 1, max: 5, step: 0.1 }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Delivery Score"
                  type="number"
                  fullWidth
                  value={evaluationForm.delivery_score}
                  onChange={(e) => setEvaluationForm({ ...evaluationForm, delivery_score: e.target.value })}
                  inputProps={{ min: 1, max: 5, step: 0.1 }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Price Score"
                  type="number"
                  fullWidth
                  value={evaluationForm.price_score}
                  onChange={(e) => setEvaluationForm({ ...evaluationForm, price_score: e.target.value })}
                  inputProps={{ min: 1, max: 5, step: 0.1 }}
                />
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Communication Score"
                  type="number"
                  fullWidth
                  value={evaluationForm.communication_score}
                  onChange={(e) => setEvaluationForm({ ...evaluationForm, communication_score: e.target.value })}
                  inputProps={{ min: 1, max: 5, step: 0.1 }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Technical Support Score"
                  type="number"
                  fullWidth
                  value={evaluationForm.technical_support_score}
                  onChange={(e) => setEvaluationForm({ ...evaluationForm, technical_support_score: e.target.value })}
                  inputProps={{ min: 1, max: 5, step: 0.1 }}
                />
              </Grid>
            </Grid>
            <Typography variant="h6">Comments</Typography>
            <TextField
              label="Quality Comments"
              fullWidth
              multiline
              rows={2}
              value={evaluationForm.quality_comments}
              onChange={(e) => setEvaluationForm({ ...evaluationForm, quality_comments: e.target.value })}
            />
            <TextField
              label="Delivery Comments"
              fullWidth
              multiline
              rows={2}
              value={evaluationForm.delivery_comments}
              onChange={(e) => setEvaluationForm({ ...evaluationForm, delivery_comments: e.target.value })}
            />
            <TextField
              label="Price Comments"
              fullWidth
              multiline
              rows={2}
              value={evaluationForm.price_comments}
              onChange={(e) => setEvaluationForm({ ...evaluationForm, price_comments: e.target.value })}
            />
            <TextField
              label="Communication Comments"
              fullWidth
              multiline
              rows={2}
              value={evaluationForm.communication_comments}
              onChange={(e) => setEvaluationForm({ ...evaluationForm, communication_comments: e.target.value })}
            />
            <TextField
              label="Technical Support Comments"
              fullWidth
              multiline
              rows={2}
              value={evaluationForm.technical_support_comments}
              onChange={(e) => setEvaluationForm({ ...evaluationForm, technical_support_comments: e.target.value })}
            />
            <Typography variant="h6">Issues & Improvements</Typography>
            <TextField
              label="Issues Identified"
              fullWidth
              multiline
              rows={3}
              value={evaluationForm.issues_identified}
              onChange={(e) => setEvaluationForm({ ...evaluationForm, issues_identified: e.target.value })}
              helperText="List any issues or problems identified during evaluation"
            />
            <TextField
              label="Improvement Actions"
              fullWidth
              multiline
              rows={3}
              value={evaluationForm.improvement_actions}
              onChange={(e) => setEvaluationForm({ ...evaluationForm, improvement_actions: e.target.value })}
              helperText="List actions required for improvement"
            />
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={6}>
                                 <FormControlLabel
                   control={
                     <Checkbox
                       checked={evaluationForm.follow_up_required}
                       onChange={(e) => setEvaluationForm({ ...evaluationForm, follow_up_required: e.target.checked })}
                     />
                   }
                   label="Follow-up Required"
                 />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Follow-up Date"
                  type="date"
                  fullWidth
                  value={evaluationForm.follow_up_date}
                  onChange={(e) => setEvaluationForm({ ...evaluationForm, follow_up_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  disabled={!evaluationForm.follow_up_required}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEvaluationDialog(false)}>Cancel</Button>
          <Button variant="contained">
            Create Evaluation
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button for Mobile */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setOpenSupplierDialog(true)}
      >
        <Add />
      </Fab>
    </Box>
  );
};

export default Suppliers;
            