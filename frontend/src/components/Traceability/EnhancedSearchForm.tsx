import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Collapse,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  History as HistoryIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { SearchFilters, SearchResult, Batch } from '../../types/traceability';
import { traceabilityAPI } from '../../services/traceabilityAPI';

interface EnhancedSearchFormProps {
  onSearchResults?: (results: SearchResult<Batch>) => void;
  onSearchHistory?: (history: any[]) => void;
}

const BATCH_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'raw_milk', label: 'Raw Milk' },
  { value: 'additive', label: 'Additive' },
  { value: 'culture', label: 'Culture' },
  { value: 'packaging', label: 'Packaging' },
  { value: 'final_product', label: 'Final Product' },
  { value: 'intermediate', label: 'Intermediate' }
];

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'in_production', label: 'In Production' },
  { value: 'completed', label: 'Completed' },
  { value: 'quarantined', label: 'Quarantined' },
  { value: 'released', label: 'Released' },
  { value: 'recalled', label: 'Recalled' },
  { value: 'disposed', label: 'Disposed' }
];

const QUALITY_STATUS_OPTIONS = [
  { value: '', label: 'All Quality Statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'passed', label: 'Passed' },
  { value: 'failed', label: 'Failed' }
];

const EnhancedSearchForm: React.FC<EnhancedSearchFormProps> = ({
  onSearchResults,
  onSearchHistory
}) => {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    batch_type: '',
    status: '',
    quality_status: '',
    date_from: '',
    date_to: '',
    product_name: '',
    supplier_id: undefined,
    page: 1,
    size: 20
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResult<Batch> | null>(null);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [searchHistory, setSearchHistory] = useState<any[]>([]);

  // Load search history on component mount
  useEffect(() => {
    loadSearchHistory();
  }, []);

  const loadSearchHistory = () => {
    // Load search history from localStorage or API
    const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
    setSearchHistory(history);
    onSearchHistory?.(history);
  };

  const handleSearch = async () => {
    if (!filters.query.trim()) {
      setError('Please enter a search query');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const results = await traceabilityAPI.searchBatches(filters);
      setSearchResults(results);

      // Save to search history
      const historyItem = {
        query: filters.query,
        filters: { ...filters },
        result_count: results.total,
        search_date: new Date().toISOString()
      };

      const updatedHistory = [historyItem, ...searchHistory.slice(0, 9)];
      setSearchHistory(updatedHistory);
      localStorage.setItem('searchHistory', JSON.stringify(updatedHistory));

      onSearchResults?.(results);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleClearFilters = () => {
    setFilters({
      query: '',
      batch_type: '',
      status: '',
      quality_status: '',
      date_from: '',
      date_to: '',
      product_name: '',
      supplier_id: undefined,
      page: 1,
      size: 20
    });
    setSearchResults(null);
    setError(null);
  };

  const handleFilterChange = (field: keyof SearchFilters, value: string | number) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleHistoryItemClick = (historyItem: any) => {
    setFilters({
      ...historyItem.filters,
      page: 1
    });
    setFilters(prev => ({
      ...prev,
      query: historyItem.query
    }));
  };

  const getBatchTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'raw_milk': return 'primary';
      case 'additive': return 'secondary';
      case 'culture': return 'success';
      case 'packaging': return 'warning';
      case 'final_product': return 'info';
      case 'intermediate': return 'default';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'in_production': return 'primary';
      case 'completed': return 'success';
      case 'quarantined': return 'warning';
      case 'released': return 'info';
      case 'recalled': return 'error';
      case 'disposed': return 'default';
      default: return 'default';
    }
  };

  const getQualityStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'passed': return 'success';
      case 'failed': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Box>
      {/* Search Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Enhanced Search
          </Typography>
          
          {/* Basic Search */}
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Search batches..."
                value={filters.query}
                onChange={(e) => handleFilterChange('query', e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Box display="flex" gap={1}>
                <Button
                  variant="outlined"
                  startIcon={<FilterIcon />}
                  onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                >
                  {showAdvancedFilters ? 'Hide' : 'Show'} Filters
                </Button>
                <Button
                  variant="contained"
                  onClick={handleSearch}
                  disabled={loading || !filters.query.trim()}
                  startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                >
                  {loading ? 'Searching...' : 'Search'}
                </Button>
              </Box>
            </Grid>
          </Grid>

          {/* Advanced Filters */}
          <Collapse in={showAdvancedFilters}>
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Advanced Filters
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Batch Type</InputLabel>
                    <Select
                      value={filters.batch_type}
                      onChange={(e) => handleFilterChange('batch_type', e.target.value)}
                      label="Batch Type"
                    >
                      {BATCH_TYPES.map((type) => (
                        <MenuItem key={type.value} value={type.value}>
                          {type.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={filters.status}
                      onChange={(e) => handleFilterChange('status', e.target.value)}
                      label="Status"
                    >
                      {STATUS_OPTIONS.map((status) => (
                        <MenuItem key={status.value} value={status.value}>
                          {status.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Quality Status</InputLabel>
                    <Select
                      value={filters.quality_status}
                      onChange={(e) => handleFilterChange('quality_status', e.target.value)}
                      label="Quality Status"
                    >
                      {QUALITY_STATUS_OPTIONS.map((status) => (
                        <MenuItem key={status.value} value={status.value}>
                          {status.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Product Name"
                    value={filters.product_name}
                    onChange={(e) => handleFilterChange('product_name', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Date From"
                    type="date"
                    value={filters.date_from}
                    onChange={(e) => handleFilterChange('date_from', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Date To"
                    type="date"
                    value={filters.date_to}
                    onChange={(e) => handleFilterChange('date_to', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Supplier ID"
                    type="number"
                    value={filters.supplier_id || ''}
                    onChange={(e) => {
                      const value = e.target.value;
                      const parsedValue = value === '' ? '' : parseInt(value);
                      handleFilterChange('supplier_id', parsedValue);
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<ClearIcon />}
                    onClick={handleClearFilters}
                  >
                    Clear Filters
                  </Button>
                </Grid>
              </Grid>
            </Box>
          </Collapse>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Search History */}
      {searchHistory.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Searches
            </Typography>
            <Grid container spacing={1}>
              {searchHistory.slice(0, 5).map((item, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card variant="outlined" sx={{ cursor: 'pointer' }} onClick={() => handleHistoryItemClick(item)}>
                    <CardContent sx={{ py: 1 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {item.query}
                        </Typography>
                        <Chip 
                          label={`${item.result_count} results`} 
                          size="small" 
                          color="primary"
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(item.search_date).toLocaleString()}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Search Results */}
      {searchResults && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Search Results ({searchResults.total} found)
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Search time: {searchResults.search_time}ms
              </Typography>
            </Box>

            {searchResults.items.length === 0 ? (
              <Typography color="text.secondary" align="center">
                No results found
              </Typography>
            ) : (
              <Grid container spacing={2}>
                {searchResults.items.map((batch) => (
                  <Grid item xs={12} md={6} lg={4} key={batch.id}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                          <Typography variant="subtitle2" sx={{ fontFamily: 'monospace' }}>
                            {batch.batch_number}
                          </Typography>
                          <Box display="flex" gap={0.5}>
                            <Chip 
                              label={batch.batch_type.replace('_', ' ').toUpperCase()} 
                              color={getBatchTypeColor(batch.batch_type)}
                              size="small"
                            />
                            <Chip 
                              label={batch.status.replace('_', ' ').toUpperCase()} 
                              color={getStatusColor(batch.status)}
                              size="small"
                            />
                          </Box>
                        </Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {batch.product_name}
                        </Typography>
                        <Typography variant="body2">
                          {batch.quantity} {batch.unit}
                        </Typography>
                        <Chip 
                          label={batch.quality_status.toUpperCase()} 
                          color={getQualityStatusColor(batch.quality_status)}
                          size="small"
                          sx={{ mt: 1 }}
                        />
                        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                          {new Date(batch.production_date).toLocaleDateString()}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default EnhancedSearchForm; 