import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Tooltip,
  Collapse,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Autocomplete,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  CircularProgress,
  alpha
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  Save as SaveIcon,
  Bookmark as BookmarkIcon,
  BookmarkBorder as BookmarkBorderIcon,
  ExpandMore as ExpandMoreIcon,
  QrCode as QrCodeIcon,
  Business as BusinessIcon,
  LocalShipping as LocalShippingIcon,
  Inventory as InventoryIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Timeline as TimelineIcon,
  Security as SecurityIcon,
  VerifiedUser as VerifiedUserIcon
} from '@mui/icons-material';
import { traceabilityAPI } from '../../services/traceabilityAPI';

interface EnhancedSearchFilterProps {
  searchType: 'batches' | 'recalls';
  onSearch: (results: any) => void;
  onClear?: () => void;
  initialFilters?: any;
}

interface SearchFilters {
  // Common filters
  query: string;
  date_from: string;
  date_to: string;
  status: string;
  
  // Batch-specific filters
  batch_type: string;
  quality_status: string;
  gtin: string;
  sscc: string;
  hierarchical_lot_number: string;
  supplier_name: string;
  product_name: string;
  
  // Recall-specific filters
  recall_type: string;
  health_risk_level: string;
  urgency_level: string;
  affected_population: string;
  
  // Advanced filters
  trace_completeness_min: number;
  trace_completeness_max: number;
  verification_status: string;
  ccp_alerts: boolean;
  regulatory_compliance: boolean;
  
  // Saved search
  saved_search_name: string;
}

interface SavedSearch {
  id: string;
  name: string;
  filters: SearchFilters;
  search_type: 'batches' | 'recalls';
  created_at: string;
  is_default: boolean;
}

const EnhancedSearchFilter: React.FC<EnhancedSearchFilterProps> = ({
  searchType,
  onSearch,
  onClear,
  initialFilters
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showSavedSearches, setShowSavedSearches] = useState(false);
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    date_from: '',
    date_to: '',
    status: '',
    batch_type: '',
    quality_status: '',
    gtin: '',
    sscc: '',
    hierarchical_lot_number: '',
    supplier_name: '',
    product_name: '',
    recall_type: '',
    health_risk_level: '',
    urgency_level: '',
    affected_population: '',
    trace_completeness_min: 0,
    trace_completeness_max: 100,
    verification_status: '',
    ccp_alerts: false,
    regulatory_compliance: false,
    saved_search_name: ''
  });

  // Predefined options
  const batchTypes = [
    'raw_milk',
    'additive',
    'culture',
    'packaging',
    'final_product',
    'intermediate'
  ];

  const statusOptions = [
    'in_production',
    'completed',
    'quarantined',
    'released',
    'recalled',
    'disposed'
  ];

  const qualityStatusOptions = [
    'pending',
    'passed',
    'failed'
  ];

  const recallTypes = [
    'voluntary',
    'mandatory',
    'market_withdrawal'
  ];

  const healthRiskLevels = [
    'class_i',
    'class_ii',
    'class_iii'
  ];

  const urgencyLevels = [
    'immediate',
    'urgent',
    'standard'
  ];

  const verificationStatuses = [
    'verified',
    'pending',
    'failed',
    'not_applicable'
  ];

  useEffect(() => {
    if (initialFilters) {
      setFilters(prev => ({ ...prev, ...initialFilters }));
    }
    loadSavedSearches();
  }, [initialFilters]);

  const loadSavedSearches = () => {
    // Load saved searches from localStorage
    const saved = localStorage.getItem(`saved_searches_${searchType}`);
    if (saved) {
      setSavedSearches(JSON.parse(saved));
    }
  };

  const saveSearch = () => {
    if (!filters.saved_search_name.trim()) {
      setError('Please enter a name for the saved search');
      return;
    }

    const newSavedSearch: SavedSearch = {
      id: Date.now().toString(),
      name: filters.saved_search_name,
      filters: { ...filters },
      search_type: searchType,
      created_at: new Date().toISOString(),
      is_default: false
    };

    const updatedSearches = [...savedSearches, newSavedSearch];
    setSavedSearches(updatedSearches);
    localStorage.setItem(`saved_searches_${searchType}`, JSON.stringify(updatedSearches));
    
    setFilters(prev => ({ ...prev, saved_search_name: '' }));
    setError(null);
  };

  const loadSavedSearch = (savedSearch: SavedSearch) => {
    setFilters(savedSearch.filters);
    setShowSavedSearches(false);
  };

  const deleteSavedSearch = (searchId: string) => {
    const updatedSearches = savedSearches.filter(search => search.id !== searchId);
    setSavedSearches(updatedSearches);
    localStorage.setItem(`saved_searches_${searchType}`, JSON.stringify(updatedSearches));
  };

  const updateFilter = (field: keyof SearchFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSearch = async () => {
    setLoading(true);
    setError(null);

    try {
      let results;
      
      if (searchType === 'batches') {
        // Use enhanced GS1 search if GS1 fields are provided
        if (filters.gtin || filters.sscc || filters.hierarchical_lot_number) {
          results = await traceabilityAPI.searchEnhancedBatchesGS1({
            gtin: filters.gtin,
            sscc: filters.sscc,
            hierarchical_lot_number: filters.hierarchical_lot_number,
            product_name: filters.product_name,
            batch_type: filters.batch_type,
            status: filters.status,
            quality_status: filters.quality_status,
            date_from: filters.date_from,
            date_to: filters.date_to
          });
        } else {
          results = await traceabilityAPI.getBatches({
            search: filters.query,
            batch_type: filters.batch_type,
            status: filters.status,
            quality_status: filters.quality_status,
            product_name: filters.product_name,
            date_from: filters.date_from,
            date_to: filters.date_to
          });
        }
      } else {
        results = await traceabilityAPI.getRecalls({
          search: filters.query,
          recall_type: filters.recall_type,
          status: filters.status,
          date_from: filters.date_from,
          date_to: filters.date_to
        });
      }

      onSearch(results);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setFilters({
      query: '',
      date_from: '',
      date_to: '',
      status: '',
      batch_type: '',
      quality_status: '',
      gtin: '',
      sscc: '',
      hierarchical_lot_number: '',
      supplier_name: '',
      product_name: '',
      recall_type: '',
      health_risk_level: '',
      urgency_level: '',
      affected_population: '',
      trace_completeness_min: 0,
      trace_completeness_max: 100,
      verification_status: '',
      ccp_alerts: false,
      regulatory_compliance: false,
      saved_search_name: ''
    });
    onClear?.();
  };

  const renderBasicFilters = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Search Query"
          value={filters.query}
          onChange={(e) => updateFilter('query', e.target.value)}
          placeholder={searchType === 'batches' ? 'Search by batch number, product name, lot number...' : 'Search by issue type, description...'}
          helperText="Use fuzzy search for better results"
        />
      </Grid>

      <Grid item xs={12} md={3}>
        <TextField
          fullWidth
          type="date"
          label="From Date"
          value={filters.date_from}
          onChange={(e) => updateFilter('date_from', e.target.value)}
          InputLabelProps={{ shrink: true }}
        />
      </Grid>

      <Grid item xs={12} md={3}>
        <TextField
          fullWidth
          type="date"
          label="To Date"
          value={filters.date_to}
          onChange={(e) => updateFilter('date_to', e.target.value)}
          InputLabelProps={{ shrink: true }}
        />
      </Grid>

      <Grid item xs={12} md={4}>
        <FormControl fullWidth>
          <InputLabel>Status</InputLabel>
          <Select
            value={filters.status}
            onChange={(e) => updateFilter('status', e.target.value)}
            label="Status"
          >
            <MenuItem value="">All Statuses</MenuItem>
            {statusOptions.map(status => (
              <MenuItem key={status} value={status}>
                {status.replace('_', ' ').toUpperCase()}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      {searchType === 'batches' && (
        <>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Batch Type</InputLabel>
              <Select
                value={filters.batch_type}
                onChange={(e) => updateFilter('batch_type', e.target.value)}
                label="Batch Type"
              >
                <MenuItem value="">All Types</MenuItem>
                {batchTypes.map(type => (
                  <MenuItem key={type} value={type}>
                    {type.replace('_', ' ').toUpperCase()}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Quality Status</InputLabel>
              <Select
                value={filters.quality_status}
                onChange={(e) => updateFilter('quality_status', e.target.value)}
                label="Quality Status"
              >
                <MenuItem value="">All Quality Statuses</MenuItem>
                {qualityStatusOptions.map(status => (
                  <MenuItem key={status} value={status}>
                    {status.toUpperCase()}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </>
      )}

      {searchType === 'recalls' && (
        <>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Recall Type</InputLabel>
              <Select
                value={filters.recall_type}
                onChange={(e) => updateFilter('recall_type', e.target.value)}
                label="Recall Type"
              >
                <MenuItem value="">All Types</MenuItem>
                {recallTypes.map(type => (
                  <MenuItem key={type} value={type}>
                    {type.replace('_', ' ').toUpperCase()}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Health Risk Level</InputLabel>
              <Select
                value={filters.health_risk_level}
                onChange={(e) => updateFilter('health_risk_level', e.target.value)}
                label="Health Risk Level"
              >
                <MenuItem value="">All Risk Levels</MenuItem>
                {healthRiskLevels.map(level => (
                  <MenuItem key={level} value={level}>
                    {level.replace('_', ' ').toUpperCase()}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </>
      )}
    </Grid>
  );

  const renderGS1Filters = () => (
    <Accordion>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1}>
          <QrCodeIcon color="primary" />
          <Typography variant="h6">GS1 Compliance Filters</Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="GTIN (Global Trade Item Number)"
              value={filters.gtin}
              onChange={(e) => updateFilter('gtin', e.target.value)}
              placeholder="e.g., 12345678901234"
              helperText="14-digit Global Trade Item Number"
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="SSCC (Serial Shipping Container Code)"
              value={filters.sscc}
              onChange={(e) => updateFilter('sscc', e.target.value)}
              placeholder="e.g., 123456789012345678"
              helperText="18-digit Serial Shipping Container Code"
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Hierarchical Lot Number"
              value={filters.hierarchical_lot_number}
              onChange={(e) => updateFilter('hierarchical_lot_number', e.target.value)}
              placeholder="e.g., LOT2024-001-001"
              helperText="Hierarchical lot numbering system"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Product Name"
              value={filters.product_name}
              onChange={(e) => updateFilter('product_name', e.target.value)}
              placeholder="Search by product name"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Supplier Name"
              value={filters.supplier_name}
              onChange={(e) => updateFilter('supplier_name', e.target.value)}
              placeholder="Search by supplier name"
            />
          </Grid>
        </Grid>
      </AccordionDetails>
    </Accordion>
  );

  const renderAdvancedFilters = () => (
    <Accordion>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1}>
          <FilterIcon color="primary" />
          <Typography variant="h6">Advanced Filters</Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography gutterBottom>Trace Completeness Range</Typography>
            <Box px={2}>
              <Slider
                value={[filters.trace_completeness_min, filters.trace_completeness_max]}
                onChange={(_, value) => {
                  updateFilter('trace_completeness_min', value[0]);
                  updateFilter('trace_completeness_max', value[1]);
                }}
                valueLabelDisplay="auto"
                min={0}
                max={100}
                marks={[
                  { value: 0, label: '0%' },
                  { value: 50, label: '50%' },
                  { value: 100, label: '100%' }
                ]}
              />
            </Box>
            <Typography variant="body2" color="text.secondary">
              {filters.trace_completeness_min}% - {filters.trace_completeness_max}%
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Verification Status</InputLabel>
              <Select
                value={filters.verification_status}
                onChange={(e) => updateFilter('verification_status', e.target.value)}
                label="Verification Status"
              >
                <MenuItem value="">All Statuses</MenuItem>
                {verificationStatuses.map(status => (
                  <MenuItem key={status} value={status}>
                    {status.replace('_', ' ').toUpperCase()}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <FormGroup>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={filters.ccp_alerts}
                    onChange={(e) => updateFilter('ccp_alerts', e.target.checked)}
                  />
                }
                label="Has CCP Alerts"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={filters.regulatory_compliance}
                    onChange={(e) => updateFilter('regulatory_compliance', e.target.checked)}
                  />
                }
                label="Regulatory Compliance Issues"
              />
            </FormGroup>
          </Grid>
        </Grid>
      </AccordionDetails>
    </Accordion>
  );

  const renderSavedSearches = () => (
    <Dialog open={showSavedSearches} onClose={() => setShowSavedSearches(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <BookmarkIcon color="primary" />
          <Typography variant="h6">Saved Searches</Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        {savedSearches.length === 0 ? (
          <Typography color="text.secondary" textAlign="center" py={3}>
            No saved searches found
          </Typography>
        ) : (
          <List>
            {savedSearches.map((search) => (
              <ListItem key={search.id} divider>
                <ListItemIcon>
                  <BookmarkIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={search.name}
                  secondary={`Created: ${new Date(search.created_at).toLocaleDateString()}`}
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={() => loadSavedSearch(search)}
                    size="small"
                  >
                    <SearchIcon />
                  </IconButton>
                  <IconButton
                    edge="end"
                    onClick={() => deleteSavedSearch(search.id)}
                    size="small"
                  >
                    <ClearIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowSavedSearches(false)}>Close</Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={2} mb={3}>
          <SearchIcon color="primary" sx={{ fontSize: 32 }} />
          <Box flex={1}>
            <Typography variant="h5" fontWeight={600}>
              Enhanced Search & Filtering
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {searchType === 'batches' ? 'Advanced batch search with GS1 compliance' : 'Comprehensive recall search and filtering'}
            </Typography>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {renderBasicFilters()}

        {searchType === 'batches' && renderGS1Filters()}

        {renderAdvancedFilters()}

        <Box display="flex" alignItems="center" gap={2} mt={3} flexWrap="wrap">
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </Button>

          <Button
            variant="outlined"
            startIcon={<ClearIcon />}
            onClick={handleClear}
          >
            Clear
          </Button>

          <Button
            variant="outlined"
            startIcon={<BookmarkBorderIcon />}
            onClick={() => setShowSavedSearches(true)}
          >
            Saved Searches
          </Button>

          <Box display="flex" alignItems="center" gap={1} ml="auto">
            <TextField
              size="small"
              label="Save Search As"
              value={filters.saved_search_name}
              onChange={(e) => updateFilter('saved_search_name', e.target.value)}
              placeholder="Enter search name"
              sx={{ minWidth: 200 }}
            />
            <Button
              variant="outlined"
              startIcon={<SaveIcon />}
              onClick={saveSearch}
              disabled={!filters.saved_search_name.trim()}
            >
              Save
            </Button>
          </Box>
        </Box>

        {renderSavedSearches()}
      </CardContent>
    </Card>
  );
};

export default EnhancedSearchFilter;
