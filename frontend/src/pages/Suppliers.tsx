import React, { useState, useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  Button,
  Paper,
  Tabs,
  Tab,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
} from '@mui/material';
import {
  Dashboard,
  Business,
  Inventory,
  Assessment,
  LocalShipping,
  Description,
  Add,
  Analytics,
} from '@mui/icons-material';
import {
  fetchSupplierDashboard,
  fetchSuppliers,
  fetchMaterials,
  fetchEvaluations,
  fetchDeliveries,
} from '../store/slices/supplierSlice';
import { RootState, AppDispatch } from '../store';
import SupplierDashboard from '../components/Suppliers/SupplierDashboard';
import SupplierList from '../components/Suppliers/SupplierList';
import MaterialList from '../components/Materials/MaterialList';
import SupplierForm from '../components/Suppliers/SupplierForm';
import SupplierDocuments from '../components/Suppliers/SupplierDocuments';
import MaterialForm from '../components/Materials/MaterialForm';
import { Supplier, Material } from '../types/supplier';
import { useLocation } from 'react-router-dom';

const Suppliers: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const {
    dashboardError,
  } = useSelector((state: RootState) => state.supplier);

  const [activeTab, setActiveTab] = useState(0);
  const location = useLocation();
  const [showSupplierForm, setShowSupplierForm] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
  const [formMode, setFormMode] = useState<'create' | 'edit' | 'view'>('create');
  const [showMaterialForm, setShowMaterialForm] = useState(false);
  const [selectedMaterial, setSelectedMaterial] = useState<Material | null>(null);
  const [materialFormMode, setMaterialFormMode] = useState<'create' | 'edit' | 'view'>('create');

  const loadInitialData = useCallback(async () => {
    try {
      // Load only endpoints backed by the backend to avoid 404s
      await Promise.all([
        dispatch(fetchSupplierDashboard()),
        dispatch(fetchSuppliers({})),
        dispatch(fetchMaterials({})),
        dispatch(fetchEvaluations({})),
        dispatch(fetchDeliveries({})),
      ]);
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  }, [dispatch]);

  const initRef = React.useRef(false);
  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;
    loadInitialData();
  }, [loadInitialData]);

  // Support redirects like /suppliers?tab=1
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tabParam = params.get('tab');
    if (tabParam) {
      const idx = parseInt(tabParam, 10);
      if (!Number.isNaN(idx)) {
        setActiveTab(idx);
      }
    }
  }, [location.search]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleCreateSupplier = () => {
    setFormMode('create');
    setSelectedSupplier(null);
    setShowSupplierForm(true);
  };

  const handleEditSupplier = (supplier: Supplier) => {
    setFormMode('edit');
    setSelectedSupplier(supplier);
    setShowSupplierForm(true);
  };

  const handleViewSupplier = (supplier: Supplier) => {
    setFormMode('view');
    setSelectedSupplier(supplier);
    setShowSupplierForm(true);
  };

  const handleSaveSupplier = (supplier: Supplier) => {
    setShowSupplierForm(false);
    setSelectedSupplier(null);
    loadInitialData();
  };

  const handleCancelSupplier = () => {
    setShowSupplierForm(false);
    setSelectedSupplier(null);
  };

  const handleViewMaterial = (material: Material) => {
    setMaterialFormMode('view');
    setSelectedMaterial(material);
    setShowMaterialForm(true);
  };

  const handleEditMaterial = (material: Material) => {
    setMaterialFormMode('edit');
    setSelectedMaterial(material);
    setShowMaterialForm(true);
  };

  const handleCreateMaterial = () => {
    setMaterialFormMode('create');
    setSelectedMaterial(null);
    setShowMaterialForm(true);
  };

  const handleSaveMaterial = (material: Material) => {
    setShowMaterialForm(false);
    setSelectedMaterial(null);
    loadInitialData();
  };

  const handleCancelMaterial = () => {
    setShowMaterialForm(false);
    setSelectedMaterial(null);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return <SupplierDashboard />;
      case 1:
        return (
          <SupplierList
            onViewSupplier={handleViewSupplier}
            onEditSupplier={handleEditSupplier}
            onCreateSupplier={handleCreateSupplier}
          />
        );
      case 2:
        return (
          <MaterialList
            onViewMaterial={handleViewMaterial}
            onEditMaterial={handleEditMaterial}
            onCreateMaterial={handleCreateMaterial}
          />
        );
      case 3:
        return (
          <Box p={3}>
            <Typography variant="h6" gutterBottom>
              Evaluations
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Evaluation management component will be implemented here.
            </Typography>
          </Box>
        );
      case 4:
        return (
          <Box p={3}>
            <Typography variant="h6" gutterBottom>
              Deliveries
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Delivery management component will be implemented here.
            </Typography>
          </Box>
        );
      case 5:
        return (
          <Box p={3}>
            <SupplierDocuments />
          </Box>
        );
      default:
        return null;
    }
  };

  // Do not block the entire page on dashboard load; show a thin loader instead

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Supplier Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage suppliers, materials, evaluations, and incoming deliveries for food safety compliance
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<Analytics />}
            onClick={() => setActiveTab(0)}
          >
            Dashboard
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreateSupplier}
          >
            New Supplier
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {dashboardError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => {}}>
          {dashboardError}
        </Alert>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<Dashboard />} label="Dashboard" iconPosition="start" />
          <Tab icon={<Business />} label="Suppliers" iconPosition="start" />
          <Tab icon={<Inventory />} label="Materials" iconPosition="start" />
          <Tab icon={<Assessment />} label="Evaluations" iconPosition="start" />
          <Tab icon={<LocalShipping />} label="Deliveries" iconPosition="start" />
          <Tab icon={<Description />} label="Documents" iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {renderTabContent()}

      {/* Supplier Form Dialog */}
      <Dialog 
        open={showSupplierForm} 
        onClose={handleCancelSupplier}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {formMode === 'create' ? 'Create New Supplier' : 
           formMode === 'edit' ? 'Edit Supplier' : 'View Supplier'}
        </DialogTitle>
        <DialogContent>
          <SupplierForm
            supplierId={selectedSupplier?.id}
            mode={formMode}
            onSave={handleSaveSupplier}
            onCancel={handleCancelSupplier}
          />
        </DialogContent>
      </Dialog>

      {/* Material Form Dialog */}
      <Dialog 
        open={showMaterialForm} 
        onClose={handleCancelMaterial}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {materialFormMode === 'create' ? 'Create New Material' : 
           materialFormMode === 'edit' ? 'Edit Material' : 'View Material'}
        </DialogTitle>
        <DialogContent>
          <MaterialForm
            materialId={selectedMaterial?.id}
            mode={materialFormMode}
            onSave={handleSaveMaterial}
            onCancel={handleCancelMaterial}
          />
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default Suppliers;
            