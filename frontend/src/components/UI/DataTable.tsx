import React, { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Paper,
  Box,
  TextField,
  InputAdornment,
  IconButton,
  Tooltip,
  Typography,
  Stack,
} from '@mui/material';
import {
  Search,
  FilterList,
  Download,
  Visibility,
  Edit,
  Delete,
} from '@mui/icons-material';
import StatusChip, { StatusType } from './StatusChip';

export interface Column<T> {
  id: keyof T;
  label: string;
  sortable?: boolean;
  filterable?: boolean;
  width?: number | string;
  render?: (value: any, row: T) => React.ReactNode;
  statusField?: boolean;
}

export interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  title?: string;
  searchable?: boolean;
  filterable?: boolean;
  exportable?: boolean;
  selectable?: boolean;
  onRowClick?: (row: T) => void;
  onEdit?: (row: T) => void;
  onDelete?: (row: T) => void;
  onExport?: () => void;
  loading?: boolean;
  emptyMessage?: string;
}

type SortDirection = 'asc' | 'desc';

function DataTable<T extends Record<string, any>>({
  data,
  columns,
  title,
  searchable = true,
  filterable = true,
  exportable = true,
  selectable = false,
  onRowClick,
  onEdit,
  onDelete,
  onExport,
  loading = false,
  emptyMessage = 'No data available',
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<keyof T | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  // Filter and sort data
  const filteredAndSortedData = useMemo(() => {
    let filtered = data;

    // Apply search filter
    if (searchTerm && searchable) {
      filtered = filtered.filter((row) =>
        columns.some((column) => {
          const value = row[column.id];
          if (value == null) return false;
          return String(value).toLowerCase().includes(searchTerm.toLowerCase());
        })
      );
    }

    // Apply sorting
    if (sortBy) {
      filtered = [...filtered].sort((a, b) => {
        const aValue = a[sortBy];
        const bValue = b[sortBy];

        if (aValue == null && bValue == null) return 0;
        if (aValue == null) return 1;
        if (bValue == null) return -1;

        const comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        return sortDirection === 'desc' ? -comparison : comparison;
      });
    }

    return filtered;
  }, [data, searchTerm, sortBy, sortDirection, columns, searchable]);

  const handleSort = (columnId: keyof T) => {
    if (sortBy === columnId) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(columnId);
      setSortDirection('asc');
    }
  };

  const renderCell = (column: Column<T>, row: T) => {
    const value = row[column.id];

    if (column.render) {
      return column.render(value, row);
    }

    if (column.statusField && typeof value === 'string') {
      const statusMap: Record<string, StatusType> = {
        compliant: 'compliant',
        non_conformance: 'nonConformance',
        pending: 'pending',
        warning: 'warning',
        info: 'info',
      };
      
      return (
        <StatusChip
          status={statusMap[value] || 'info'}
          label={value.replace('_', ' ')}
        />
      );
    }

    if (value == null) return '-';
    return String(value);
  };

  return (
    <Paper sx={{ overflow: 'hidden' }}>
      {/* Table Header */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" fontWeight={600}>
            {title}
          </Typography>
          
          <Stack direction="row" spacing={2}>
            {searchable && (
              <TextField
                size="small"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search fontSize="small" />
                    </InputAdornment>
                  ),
                }}
                sx={{ minWidth: 250 }}
              />
            )}
            
            {exportable && onExport && (
              <Tooltip title="Export Data">
                <IconButton onClick={onExport} size="small">
                  <Download />
                </IconButton>
              </Tooltip>
            )}
          </Stack>
        </Stack>
      </Box>

      {/* Table */}
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: 'background.default' }}>
              {columns.map((column) => (
                <TableCell
                  key={String(column.id)}
                  sx={{
                    fontWeight: 600,
                    fontSize: '0.875rem',
                    width: column.width,
                    cursor: column.sortable ? 'pointer' : 'default',
                  }}
                  onClick={() => column.sortable && handleSort(column.id)}
                >
                  {column.sortable ? (
                    <TableSortLabel
                      active={sortBy === column.id}
                      direction={sortBy === column.id ? sortDirection : 'asc'}
                    >
                      {column.label}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
              
              {/* Action column */}
              {(onEdit || onDelete) && (
                <TableCell sx={{ fontWeight: 600, fontSize: '0.875rem', width: 120 }}>
                  Actions
                </TableCell>
              )}
            </TableRow>
          </TableHead>
          
          <TableBody>
            {filteredAndSortedData.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length + (onEdit || onDelete ? 1 : 0)}>
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography color="text.secondary">
                      {loading ? 'Loading...' : emptyMessage}
                    </Typography>
                  </Box>
                </TableCell>
              </TableRow>
            ) : (
              filteredAndSortedData.map((row, index) => (
                <TableRow
                  key={index}
                  hover
                  onClick={() => onRowClick?.(row)}
                  sx={{
                    cursor: onRowClick ? 'pointer' : 'default',
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  {columns.map((column) => (
                    <TableCell key={String(column.id)}>
                      {renderCell(column, row)}
                    </TableCell>
                  ))}
                  
                  {/* Action buttons */}
                  {(onEdit || onDelete) && (
                    <TableCell>
                      <Stack direction="row" spacing={1}>
                        {onEdit && (
                          <Tooltip title="Edit">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                onEdit(row);
                              }}
                            >
                              <Edit fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        {onDelete && (
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={(e) => {
                                e.stopPropagation();
                                onDelete(row);
                              }}
                            >
                              <Delete fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Stack>
                    </TableCell>
                  )}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}

export default DataTable; 