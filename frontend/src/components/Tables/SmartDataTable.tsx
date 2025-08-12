import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  InputAdornment,
  IconButton,
  Menu,
  MenuItem,
  Checkbox,
  Chip,
  Button,
  Typography,
  Paper,
  Stack,
  Card,
  CardContent,
  Tooltip,
  Avatar,
  LinearProgress,
  Fade,
  Grow,
  Badge,
  Alert,
  Collapse,
  FormControl,
  Select,
  ListItemText,
} from '@mui/material';
import {
  Search,
  FilterList,
  Download,
  MoreVert,
  Visibility,
  Edit,
  Delete,
  Star,
  StarBorder,
  Sort,
  ViewColumn,
  Analytics,
  TrendingUp,
  AutoAwesome,
  CheckCircle,
  Warning,
  Speed,
  Insights,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';
import { dashboardAPI } from '../../services/api';

export interface TableColumn {
  id: string;
  label: string;
  sortable?: boolean;
  filterable?: boolean;
  type?: 'text' | 'number' | 'date' | 'status' | 'boolean' | 'custom';
  width?: string | number;
  align?: 'left' | 'center' | 'right';
  format?: (value: any, row?: any) => React.ReactNode;
  searchable?: boolean;
}

export interface TableAction {
  id: string;
  label: string;
  icon: React.ReactNode;
  onClick: (row: any) => void;
  disabled?: (row: any) => boolean;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
}

export interface SmartFilter {
  id: string;
  label: string;
  type: 'select' | 'dateRange' | 'numberRange' | 'boolean';
  options?: Array<{ label: string; value: any }>;
  defaultValue?: any;
}

export interface TableInsight {
  id: string;
  title: string;
  description: string;
  value: string | number;
  trend?: 'up' | 'down' | 'stable';
  type: 'success' | 'warning' | 'error' | 'info';
  icon: React.ReactNode;
}

interface SmartDataTableProps {
  title: string;
  columns: TableColumn[];
  data: any[];
  actions?: TableAction[];
  filters?: SmartFilter[];
  enableSearch?: boolean;
  enableBulkActions?: boolean;
  enableExport?: boolean;
  enableInsights?: boolean;
  enableColumnCustomization?: boolean;
  loading?: boolean;
  onRowClick?: (row: any) => void;
  bulkActions?: Array<{
    id: string;
    label: string;
    icon: React.ReactNode;
    onClick: (selectedRows: any[]) => void;
  }>;
  insights?: TableInsight[];
  tableType?: string; // For backend insight generation
}

const SmartDataTable: React.FC<SmartDataTableProps> = ({
  title,
  columns,
  data,
  actions = [],
  filters = [],
  enableSearch = true,
  enableBulkActions = true,
  enableExport = true,
  enableInsights = true,
  enableColumnCustomization = true,
  loading = false,
  onRowClick,
  bulkActions = [],
  insights = [],
  tableType,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedRows, setSelectedRows] = useState<any[]>([]);
  const [filterValues, setFilterValues] = useState<Record<string, any>>({});
  const [visibleColumns, setVisibleColumns] = useState<string[]>(columns.map(col => col.id));
  const [filterMenuAnchor, setFilterMenuAnchor] = useState<null | HTMLElement>(null);
  const [columnMenuAnchor, setColumnMenuAnchor] = useState<null | HTMLElement>(null);
  const [showInsights, setShowInsights] = useState(true);
  const [backendInsights, setBackendInsights] = useState<TableInsight[]>([]);

  // Smart filtering and searching
  const filteredAndSearchedData = useMemo(() => {
    let result = [...data];

    // Apply search
    if (searchQuery) {
      const searchableColumns = columns.filter(col => col.searchable !== false);
      result = result.filter(row =>
        searchableColumns.some(col => {
          const value = row[col.id];
          return value && value.toString().toLowerCase().includes(searchQuery.toLowerCase());
        })
      );
    }

    // Apply filters
    Object.entries(filterValues).forEach(([filterId, filterValue]) => {
      if (filterValue !== undefined && filterValue !== null && filterValue !== '') {
        const filter = filters.find(f => f.id === filterId);
        if (filter) {
          result = result.filter(row => {
            const rowValue = row[filterId];
            switch (filter.type) {
              case 'select':
                return Array.isArray(filterValue) 
                  ? filterValue.includes(rowValue)
                  : rowValue === filterValue;
              case 'boolean':
                return rowValue === filterValue;
              case 'dateRange':
                // Implement date range filtering
                return true;
              case 'numberRange':
                // Implement number range filtering
                return true;
              default:
                return true;
            }
          });
        }
      }
    });

    return result;
  }, [data, searchQuery, filterValues, columns, filters]);

  // Sorting
  const sortedData = useMemo(() => {
    if (!sortBy) return filteredAndSearchedData;

    return [...filteredAndSearchedData].sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];
      
      let comparison = 0;
      if (aValue < bValue) comparison = -1;
      if (aValue > bValue) comparison = 1;
      
      return sortOrder === 'desc' ? -comparison : comparison;
    });
  }, [filteredAndSearchedData, sortBy, sortOrder]);

  // Pagination
  const paginatedData = useMemo(() => {
    const startIndex = page * rowsPerPage;
    return sortedData.slice(startIndex, startIndex + rowsPerPage);
  }, [sortedData, page, rowsPerPage]);

  // Auto-generate insights
  const autoInsights = useMemo((): TableInsight[] => {
    if (!enableInsights || data.length === 0) return [];

    const generated: TableInsight[] = [];

    // Total records insight
    generated.push({
      id: 'total',
      title: 'Total Records',
      description: 'Total number of items in the table',
      value: data.length,
      type: 'info',
      icon: <Analytics />,
    });

    // Status distribution (if status column exists)
    const statusColumn = columns.find(col => col.id === 'status' || col.type === 'status');
    if (statusColumn) {
      const statusCounts = data.reduce<Record<string, number>>((acc, row) => {
        const status = row[statusColumn.id];
        acc[status] = (acc[status] || 0) + 1;
        return acc;
      }, {});

      const compliantCount = (statusCounts['compliant'] || statusCounts['active'] || statusCounts['approved'] || 0) as number;
      const totalWithStatus = Object.values(statusCounts).reduce((sum: number, count: number) => sum + count, 0);
      const complianceRate = totalWithStatus > 0 ? Math.round((compliantCount / totalWithStatus) * 100) : 0;

      generated.push({
        id: 'compliance',
        title: 'Compliance Rate',
        description: 'Percentage of compliant/approved items',
        value: `${complianceRate}%`,
        trend: complianceRate >= 90 ? 'up' : complianceRate >= 70 ? 'stable' : 'down',
        type: complianceRate >= 90 ? 'success' : complianceRate >= 70 ? 'warning' : 'error',
        icon: <CheckCircle />,
      });
    }

    // Recent activity (if date column exists)
    const dateColumn = columns.find(col => col.type === 'date' || col.id.includes('date') || col.id.includes('created'));
    if (dateColumn) {
      const now = new Date();
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      const recentCount = data.filter(row => {
        const date = new Date(row[dateColumn.id]);
        return date >= weekAgo;
      }).length;

      generated.push({
        id: 'recent',
        title: 'Recent Activity',
        description: 'Items added/updated in the last 7 days',
        value: recentCount,
        trend: recentCount > 0 ? 'up' : 'stable',
        type: recentCount > 0 ? 'success' : 'info',
        icon: <TrendingUp />,
      });
    }

    return generated;
  }, [data, columns, enableInsights]);

  const combinedInsights = [...autoInsights, ...insights];

  const handleSort = (columnId: string) => {
    if (sortBy === columnId) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(columnId);
      setSortOrder('asc');
    }
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedRows(paginatedData);
    } else {
      setSelectedRows([]);
    }
  };

  const handleSelectRow = (row: any) => {
    const isSelected = selectedRows.some(selected => selected.id === row.id);
    if (isSelected) {
      setSelectedRows(selectedRows.filter(selected => selected.id !== row.id));
    } else {
      setSelectedRows([...selectedRows, row]);
    }
  };

  const handleExport = () => {
    // Generate CSV export
    const headers = visibleColumns.map(colId => columns.find(col => col.id === colId)?.label || colId);
    const csvContent = [
      headers.join(','),
      ...sortedData.map(row => 
        visibleColumns.map(colId => {
          const value = row[colId];
          return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
        }).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s+/g, '_')}_export.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const renderCellContent = (column: TableColumn, row: any) => {
    const value = row[column.id];
    
    if (column.format) {
      return column.format(value, row);
    }
    
    switch (column.type) {
      case 'status':
        return (
          <Chip
            label={value}
            color={
              value === 'active' || value === 'compliant' || value === 'approved' ? 'success' :
              value === 'inactive' || value === 'non_compliant' || value === 'rejected' ? 'error' :
              value === 'pending' || value === 'under_review' ? 'warning' : 'default'
            }
            size="small"
            sx={{ borderRadius: 3 }}
          />
        );
      case 'boolean':
        return value ? <CheckCircle color="success" /> : <Warning color="error" />;
      case 'date':
        return new Date(value).toLocaleDateString();
      default:
        return value;
    }
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up': return <TrendingUp color="success" fontSize="small" />;
      case 'down': return <TrendingUp color="error" fontSize="small" sx={{ transform: 'rotate(180deg)' }} />;
      default: return null;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <LinearProgress sx={{ mb: 2 }} />
          <Typography variant="h6" align="center">Loading data...</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      {/* Smart Insights */}
      {enableInsights && combinedInsights.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
              <Typography variant="h6" fontWeight={600} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Insights color="primary" />
                Smart Insights
              </Typography>
              <IconButton onClick={() => setShowInsights(!showInsights)}>
                {showInsights ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Stack>
            
            <Collapse in={showInsights}>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
                {combinedInsights.map((insight, index) => (
                  <Grow in timeout={300 + index * 100} key={insight.id}>
                    <Paper sx={{ 
                      p: 2, 
                      border: '1px solid', 
                      borderColor: 'divider',
                      borderRadius: 3,
                      background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',
                    }}>
                      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
                        <Avatar sx={{ 
                          bgcolor: `${insight.type}.main`, 
                          width: 32, 
                          height: 32,
                        }}>
                          {insight.icon}
                        </Avatar>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6" fontWeight={700}>
                            {insight.value}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {insight.title}
                          </Typography>
                        </Box>
                        {getTrendIcon(insight.trend)}
                      </Stack>
                      <Typography variant="body2" color="text.secondary">
                        {insight.description}
                      </Typography>
                    </Paper>
                  </Grow>
                ))}
              </Box>
            </Collapse>
          </CardContent>
        </Card>
      )}

      {/* Table Controls */}
      <Card>
        <CardContent>
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
            <Typography variant="h5" fontWeight={700}>
              {title}
            </Typography>
            <Stack direction="row" spacing={1}>
              {enableColumnCustomization && (
                <Tooltip title="Customize columns">
                  <IconButton onClick={(e) => setColumnMenuAnchor(e.currentTarget)}>
                    <ViewColumn />
                  </IconButton>
                </Tooltip>
              )}
              {enableExport && (
                <Tooltip title="Export data">
                  <IconButton onClick={handleExport}>
                    <Download />
                  </IconButton>
                </Tooltip>
              )}
              {filters.length > 0 && (
                <Tooltip title="Filters">
                  <IconButton onClick={(e) => setFilterMenuAnchor(e.currentTarget)}>
                    <Badge badgeContent={Object.keys(filterValues).length} color="primary">
                      <FilterList />
                    </Badge>
                  </IconButton>
                </Tooltip>
              )}
            </Stack>
          </Stack>

          {/* Search and Bulk Actions */}
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
            {enableSearch && (
              <TextField
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                size="small"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ flex: 1, maxWidth: 400 }}
              />
            )}
            
            {enableBulkActions && selectedRows.length > 0 && (
              <Fade in>
                <Alert 
                  severity="info" 
                  sx={{ flex: 1 }}
                  action={
                    <Stack direction="row" spacing={1}>
                      {bulkActions.map(action => (
                        <Button
                          key={action.id}
                          size="small"
                          onClick={() => action.onClick(selectedRows)}
                          startIcon={action.icon}
                        >
                          {action.label}
                        </Button>
                      ))}
                    </Stack>
                  }
                >
                  {selectedRows.length} item(s) selected
                </Alert>
              </Fade>
            )}
          </Stack>

          {/* Data Table */}
          <TableContainer component={Paper} sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <Table>
              <TableHead sx={{ backgroundColor: 'grey.50' }}>
                <TableRow>
                  {enableBulkActions && (
                    <TableCell padding="checkbox">
                      <Checkbox
                        indeterminate={selectedRows.length > 0 && selectedRows.length < paginatedData.length}
                        checked={paginatedData.length > 0 && selectedRows.length === paginatedData.length}
                        onChange={handleSelectAll}
                      />
                    </TableCell>
                  )}
                  {columns
                    .filter(col => visibleColumns.includes(col.id))
                    .map(column => (
                      <TableCell
                        key={column.id}
                        align={column.align || 'left'}
                        style={{ width: column.width }}
                        sx={{ fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}
                      >
                        <Stack direction="row" alignItems="center" spacing={1}>
                          <span>{column.label}</span>
                          {column.sortable !== false && (
                            <IconButton
                              size="small"
                              onClick={() => handleSort(column.id)}
                              sx={{ 
                                opacity: sortBy === column.id ? 1 : 0.5,
                                transform: sortBy === column.id && sortOrder === 'desc' ? 'rotate(180deg)' : 'none',
                              }}
                            >
                              <Sort fontSize="small" />
                            </IconButton>
                          )}
                        </Stack>
                      </TableCell>
                    ))}
                  {actions.length > 0 && (
                    <TableCell align="center" sx={{ fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>
                      Actions
                    </TableCell>
                  )}
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedData.map((row, index) => (
                  <TableRow
                    key={row.id || index}
                    hover
                    onClick={onRowClick ? () => onRowClick(row) : undefined}
                    sx={{ 
                      cursor: onRowClick ? 'pointer' : 'default',
                      '&:hover': {
                        backgroundColor: 'rgba(30, 64, 175, 0.04)',
                      },
                    }}
                  >
                    {enableBulkActions && (
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedRows.some(selected => selected.id === row.id)}
                          onChange={() => handleSelectRow(row)}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </TableCell>
                    )}
                    {columns
                      .filter(col => visibleColumns.includes(col.id))
                      .map(column => (
                        <TableCell key={column.id} align={column.align || 'left'}>
                          {renderCellContent(column, row)}
                        </TableCell>
                      ))}
                    {actions.length > 0 && (
                      <TableCell align="center">
                        <Stack direction="row" spacing={0.5} justifyContent="center">
                          {actions.map(action => (
                            <Tooltip key={action.id} title={action.label}>
                              <IconButton
                                size="small"
                                color={action.color || 'default'}
                                disabled={action.disabled?.(row)}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  action.onClick(row);
                                }}
                              >
                                {action.icon}
                              </IconButton>
                            </Tooltip>
                          ))}
                        </Stack>
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          <TablePagination
            component="div"
            count={sortedData.length}
            page={page}
            onPageChange={(_, newPage) => setPage(newPage)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        </CardContent>
      </Card>

      {/* Filter Menu */}
      <Menu
        anchorEl={filterMenuAnchor}
        open={Boolean(filterMenuAnchor)}
        onClose={() => setFilterMenuAnchor(null)}
        PaperProps={{ sx: { minWidth: 300, p: 2 } }}
      >
        <Typography variant="h6" sx={{ mb: 2 }}>Filters</Typography>
        {filters.map(filter => (
          <Box key={filter.id} sx={{ mb: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>{filter.label}</Typography>
            {filter.type === 'select' && (
              <FormControl fullWidth size="small">
                <Select
                  value={filterValues[filter.id] || ''}
                  onChange={(e) => setFilterValues(prev => ({
                    ...prev,
                    [filter.id]: e.target.value
                  }))}
                  displayEmpty
                >
                  <MenuItem value="">All</MenuItem>
                  {filter.options?.map(option => (
                    <MenuItem key={option.value} value={option.value}>
                      <ListItemText primary={option.label} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
          </Box>
        ))}
        <Button
          fullWidth
          variant="outlined"
          onClick={() => {
            setFilterValues({});
            setFilterMenuAnchor(null);
          }}
        >
          Clear All Filters
        </Button>
      </Menu>

      {/* Column Menu */}
      <Menu
        anchorEl={columnMenuAnchor}
        open={Boolean(columnMenuAnchor)}
        onClose={() => setColumnMenuAnchor(null)}
        PaperProps={{ sx: { minWidth: 250, p: 2 } }}
      >
        <Typography variant="h6" sx={{ mb: 2 }}>Customize Columns</Typography>
        {columns.map(column => (
          <MenuItem key={column.id}>
            <Checkbox
              checked={visibleColumns.includes(column.id)}
              onChange={(e) => {
                if (e.target.checked) {
                  setVisibleColumns(prev => [...prev, column.id]);
                } else {
                  setVisibleColumns(prev => prev.filter(id => id !== column.id));
                }
              }}
            />
            <ListItemText primary={column.label} />
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
};

export default SmartDataTable;
