import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  InputAdornment,
  Chip,
  Tooltip,
  TableSortLabel
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  TableChart as TableChartIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  FilterList as FilterListIcon
} from '@mui/icons-material';

import { dashboardService } from '../../../services/dashboardService';
import { KPIDefinition, DashboardAlert, DashboardStats } from '../../../types/dashboard';

interface TableWidgetProps {
  config: {
    data_source: 'kpis' | 'alerts' | 'recent_activity';
    columns?: string[];
    page_size?: number;
    sortable?: boolean;
    filterable?: boolean;
    title?: string;
    refresh_interval?: number;
  };
  dashboardStats?: DashboardStats | null;
  kpiDefinitions: KPIDefinition[];
  selectedDepartment?: number | null;
  isEditMode?: boolean;
}

interface TableRow {
  id: string | number;
  [key: string]: any;
}

interface TableColumn {
  id: string;
  label: string;
  sortable?: boolean;
  format?: (value: any) => string;
  align?: 'left' | 'center' | 'right';
}

const TableWidget: React.FC<TableWidgetProps> = ({
  config,
  dashboardStats,
  kpiDefinitions,
  selectedDepartment,
  isEditMode = false
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<TableRow[]>([]);
  const [columns, setColumns] = useState<TableColumn[]>([]);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  
  // Table state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(config.page_size || 10);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    loadTableData();
  }, [config.data_source, selectedDepartment, config.columns]);

  useEffect(() => {
    // Auto-refresh if configured
    const refreshInterval = config.refresh_interval || 300000; // 5 minutes default
    
    if (refreshInterval > 0) {
      const interval = setInterval(loadTableData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [config.refresh_interval]);

  const loadTableData = async () => {
    try {
      setLoading(true);
      setError(null);

      let tableData: TableRow[] = [];
      let tableColumns: TableColumn[] = [];

      switch (config.data_source) {
        case 'kpis':
          await loadKPIData(tableData, tableColumns);
          break;
        case 'alerts':
          await loadAlertsData(tableData, tableColumns);
          break;
        case 'recent_activity':
          await loadRecentActivityData(tableData, tableColumns);
          break;
        default:
          throw new Error(`Unknown data source: ${config.data_source}`);
      }

      setData(tableData);
      setColumns(tableColumns);

    } catch (err) {
      console.error('Error loading table data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load table data');
    } finally {
      setLoading(false);
    }
  };

  const loadKPIData = async (tableData: TableRow[], tableColumns: TableColumn[]) => {
    // Get latest KPI values
    const kpiValuesPromises = kpiDefinitions.map(async kpi => {
      const values = await dashboardService.getKPITrendData(kpi.id, 1, selectedDepartment);
      const latestValue = values.length > 0 ? values[0] : null;
      
      return {
        id: kpi.id,
        name: kpi.display_name,
        category: kpi.category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        current_value: latestValue ? Number(latestValue.value) : 0,
        target_value: kpi.target_value ? Number(kpi.target_value) : null,
        unit: kpi.unit || '',
        status: latestValue ? getKPIStatus(Number(latestValue.value), kpi.target_value ? Number(kpi.target_value) : null, kpi.target_operator) : 'No Data',
        last_updated: latestValue ? new Date(latestValue.calculated_at).toLocaleString() : 'Never'
      };
    });

    const kpiData = await Promise.all(kpiValuesPromises);
    tableData.push(...kpiData);

    // Define columns
    tableColumns.push(
      { id: 'name', label: 'KPI Name', sortable: true },
      { id: 'category', label: 'Category', sortable: true },
      { 
        id: 'current_value', 
        label: 'Current Value', 
        sortable: true, 
        align: 'right',
        format: (value: number, row: TableRow) => dashboardService.formatKPIValue(value, row.unit)
      },
      { 
        id: 'target_value', 
        label: 'Target', 
        sortable: true, 
        align: 'right',
        format: (value: number | null, row: TableRow) => value !== null ? dashboardService.formatKPIValue(value, row.unit) : 'N/A'
      },
      { id: 'status', label: 'Status', sortable: true, align: 'center' },
      { id: 'last_updated', label: 'Last Updated', sortable: true }
    );
  };

  const loadAlertsData = async (tableData: TableRow[], tableColumns: TableColumn[]) => {
    const alerts = await dashboardService.getDashboardAlerts(50);
    
    const alertData = alerts.map(alert => ({
      id: alert.id,
      name: alert.name,
      level: alert.alert_level,
      description: alert.description || 'No description',
      threshold_value: alert.threshold_value,
      last_triggered: alert.last_triggered_at ? new Date(alert.last_triggered_at).toLocaleString() : 'Never',
      trigger_count: alert.trigger_count,
      status: alert.is_active ? 'Active' : 'Inactive',
      created_at: new Date(alert.created_at).toLocaleString()
    }));

    tableData.push(...alertData);

    // Define columns
    tableColumns.push(
      { id: 'name', label: 'Alert Name', sortable: true },
      { id: 'level', label: 'Level', sortable: true, align: 'center' },
      { id: 'description', label: 'Description', sortable: false },
      { id: 'threshold_value', label: 'Threshold', sortable: true, align: 'right' },
      { id: 'trigger_count', label: 'Triggers', sortable: true, align: 'right' },
      { id: 'status', label: 'Status', sortable: true, align: 'center' },
      { id: 'last_triggered', label: 'Last Triggered', sortable: true }
    );
  };

  const loadRecentActivityData = async (tableData: TableRow[], tableColumns: TableColumn[]) => {
    // Mock recent activity data
    const recentActivity = [
      {
        id: 1,
        action: 'KPI Calculated',
        resource: 'CCP Compliance Rate',
        user: 'System',
        timestamp: new Date(Date.now() - 5 * 60 * 1000).toLocaleString(),
        details: 'Automated calculation completed'
      },
      {
        id: 2,
        action: 'Alert Triggered',
        resource: 'Temperature Deviation',
        user: 'HACCP Monitor',
        timestamp: new Date(Date.now() - 15 * 60 * 1000).toLocaleString(),
        details: 'Critical limit exceeded'
      },
      {
        id: 3,
        action: 'Dashboard Viewed',
        resource: 'Executive Dashboard',
        user: 'John Smith',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toLocaleString(),
        details: 'Dashboard accessed'
      }
    ];

    tableData.push(...recentActivity);

    // Define columns
    tableColumns.push(
      { id: 'action', label: 'Action', sortable: true },
      { id: 'resource', label: 'Resource', sortable: true },
      { id: 'user', label: 'User', sortable: true },
      { id: 'timestamp', label: 'Time', sortable: true },
      { id: 'details', label: 'Details', sortable: false }
    );
  };

  const getKPIStatus = (currentValue: number, targetValue: number | null, operator: string): string => {
    if (!targetValue) return 'No Target';
    
    const status = dashboardService.determineKPIStatus(currentValue, targetValue, operator);
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const handleRefresh = () => {
    loadTableData();
    handleMenuClose();
  };

  const handleExportData = () => {
    // Export table data as CSV
    const headers = columns.map(col => col.label).join(',');
    const rows = filteredAndSortedData.map(row => 
      columns.map(col => {
        let value = row[col.id];
        if (col.format) {
          value = col.format(value, row);
        }
        // Escape commas and quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          value = `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    ).join('\n');
    
    const csv = `${headers}\n${rows}`;
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `${config.title || config.data_source}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    
    URL.revokeObjectURL(url);
    handleMenuClose();
  };

  const handleSort = (columnId: string) => {
    if (sortBy === columnId) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(columnId);
      setSortDirection('asc');
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Filter and sort data
  const filteredAndSortedData = React.useMemo(() => {
    let filtered = data;

    // Apply search filter
    if (searchTerm) {
      filtered = data.filter(row =>
        Object.values(row).some(value =>
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Apply sorting
    if (sortBy) {
      filtered = [...filtered].sort((a, b) => {
        let aValue = a[sortBy];
        let bValue = b[sortBy];

        // Handle numeric values
        if (typeof aValue === 'number' && typeof bValue === 'number') {
          return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
        }

        // Handle string values
        aValue = String(aValue).toLowerCase();
        bValue = String(bValue).toLowerCase();

        if (sortDirection === 'asc') {
          return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        } else {
          return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
        }
      });
    }

    return filtered;
  }, [data, searchTerm, sortBy, sortDirection]);

  const paginatedData = filteredAndSortedData.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const renderCellContent = (value: any, column: TableColumn, row: TableRow) => {
    if (column.format) {
      value = column.format(value, row);
    }

    // Special rendering for certain column types
    if (column.id === 'status') {
      const color = 
        value === 'Good' || value === 'Active' || value === 'Excellent' ? 'success' :
        value === 'Warning' || value === 'Acceptable' ? 'warning' :
        value === 'Critical' || value === 'Inactive' ? 'error' : 'default';
      
      return (
        <Chip
          label={value}
          size="small"
          color={color as any}
          variant="outlined"
        />
      );
    }

    if (column.id === 'level') {
      const color = 
        value === 'info' ? 'info' :
        value === 'warning' ? 'warning' : 'error';
      
      return (
        <Chip
          label={value.toUpperCase()}
          size="small"
          color={color as any}
          variant="filled"
        />
      );
    }

    return value;
  };

  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader
          title={<Skeleton variant="text" width="60%" />}
          action={<Skeleton variant="circular" width={40} height={40} />}
        />
        <CardContent>
          {Array.from({ length: 5 }).map((_, index) => (
            <Skeleton key={index} variant="text" height={40} sx={{ mb: 1 }} />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardHeader
          title={
            <Typography variant="h6" color="error">
              Table Error
            </Typography>
          }
        />
        <CardContent>
          <Typography color="error" variant="body2">
            {error}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card 
      sx={{ 
        height: '100%',
        border: isEditMode ? '2px dashed #ccc' : 'none',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <TableChartIcon color="primary" />
            <Typography variant="h6">
              {config.title || `${config.data_source.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Table`}
            </Typography>
            <Chip 
              label={`${filteredAndSortedData.length} rows`}
              size="small" 
              color="primary" 
              variant="outlined" 
            />
          </Box>
        }
        action={
          <Box display="flex" alignItems="center" gap={1}>
            {config.filterable && (
              <TextField
                size="small"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  )
                }}
                sx={{ width: 200 }}
              />
            )}
            
            <IconButton onClick={handleMenuOpen}>
              <MoreVertIcon />
            </IconButton>
          </Box>
        }
        sx={{ pb: 1 }}
      />
      
      <CardContent sx={{ pt: 0, flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <TableContainer sx={{ flex: 1 }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell
                    key={column.id}
                    align={column.align || 'left'}
                    sx={{ fontWeight: 600 }}
                  >
                    {config.sortable && column.sortable ? (
                      <TableSortLabel
                        active={sortBy === column.id}
                        direction={sortBy === column.id ? sortDirection : 'asc'}
                        onClick={() => handleSort(column.id)}
                      >
                        {column.label}
                      </TableSortLabel>
                    ) : (
                      column.label
                    )}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedData.map((row) => (
                <TableRow key={row.id} hover>
                  {columns.map((column) => (
                    <TableCell
                      key={column.id}
                      align={column.align || 'left'}
                    >
                      {renderCellContent(row[column.id], column, row)}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredAndSortedData.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </CardContent>

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleRefresh}>
          <RefreshIcon sx={{ mr: 1 }} />
          Refresh Data
        </MenuItem>
        <MenuItem onClick={handleExportData}>
          <DownloadIcon sx={{ mr: 1 }} />
          Export CSV
        </MenuItem>
      </Menu>

      {/* Edit Mode Overlay */}
      {isEditMode && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'move'
          }}
        >
          <Typography variant="caption" sx={{ 
            backgroundColor: 'white',
            padding: '4px 8px',
            borderRadius: 1,
            fontWeight: 600
          }}>
            Table Widget
          </Typography>
        </Box>
      )}
    </Card>
  );
};

export default TableWidget;