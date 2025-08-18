import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Button,
  Chip,
  Paper,
  Stack,
  Alert,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  LinearProgress,
  Pagination,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Menu,
  MenuItem as MenuItemComponent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Description,
  History,
  Approval,
  Visibility,
  Edit,
  Delete,
  Download,
  Warning,
  CheckCircle,
  Add,
  FilterList,
  Refresh,
  Archive,
  MoreVert,
  EditNote,
  History as HistoryIcon,
  Timeline,
  Assessment,
  FilterAlt,
  Clear,
  Compare,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { AppDispatch, RootState } from '../store';
import {
  fetchDocuments,
  fetchDocumentStats,
  deleteDocument,
  bulkUpdateStatus,
  archiveObsoleteDocuments,
  setFilters,
  clearFilters,
  setPagination,
  downloadDocument,
  downloadVersion,
  fetchPendingApprovals,
  approveApprovalStep,
  rejectApprovalStep,
} from '../store/slices/documentSlice';
import { hasRole, isSystemAdministrator } from '../store/slices/authSlice';
import PageHeader from '../components/UI/PageHeader';
import StatusChip from '../components/UI/StatusChip';
import DocumentUploadDialog from '../components/Documents/DocumentUploadDialog';
import DocumentViewDialog from '../components/Documents/DocumentViewDialog';
import DocumentVersionDialog from '../components/Documents/DocumentVersionDialog';
import DocumentChangeLogDialog from '../components/Documents/DocumentChangeLogDialog';
import DocumentTemplatesDialog from '../components/Documents/DocumentTemplatesDialog';
import DocumentWorkflowDialog from '../components/Documents/DocumentWorkflowDialog';
import DocumentAnalyticsDialog from '../components/Documents/DocumentAnalyticsDialog';
import DocumentComparisonDialog from '../components/Documents/DocumentComparisonDialog';
import DocumentEditDialog from '../components/Documents/DocumentEditDialog';
import { downloadFile } from '../utils/downloadUtils';
import { documentsAPI } from '../services/api';

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
      id={`documents-tabpanel-${index}`}
      aria-labelledby={`documents-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const Documents: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { user: currentUser } = useSelector((state: RootState) => state.auth);
  const { documents, stats, loading, error, pagination, filters, pendingApprovals } = useSelector((state: RootState) => state.documents);
  
  const [selectedTab, setSelectedTab] = useState(0);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [versionDialogOpen, setVersionDialogOpen] = useState(false);
  const [changeLogDialogOpen, setChangeLogDialogOpen] = useState(false);
  const [templatesDialogOpen, setTemplatesDialogOpen] = useState(false);
  const [workflowDialogOpen, setWorkflowDialogOpen] = useState(false);
  const [analyticsDialogOpen, setAnalyticsDialogOpen] = useState(false);
  const [comparisonDialogOpen, setComparisonDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<any>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState<number[]>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedDocumentForMenu, setSelectedDocumentForMenu] = useState<any>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [reasonDialog, setReasonDialog] = useState<{ open: boolean; action: 'obsolete'|'archive'|'activate'|null; doc: any | null; reason: string }>({ open: false, action: null, doc: null, reason: '' });
  const [distributeDialog, setDistributeDialog] = useState<{ open: boolean; doc: any | null }>( { open: false, doc: null } );
  const [distributionUsers, setDistributionUsers] = useState<any[]>([]);
  const [selectedDistributionUserIds, setSelectedDistributionUserIds] = useState<number[]>([]);
  const [searchText, setSearchText] = useState<string>(filters?.search || '');

  // Role-based permissions
  const canCreateDocuments = hasRole(currentUser, 'QA Manager') || 
                           hasRole(currentUser, 'QA Specialist') || 
                           hasRole(currentUser, 'Production Manager') ||
                           isSystemAdministrator(currentUser);

  const canApproveDocuments = hasRole(currentUser, 'QA Manager') || 
                             isSystemAdministrator(currentUser);

  const canDeleteDocuments = hasRole(currentUser, 'QA Manager') || 
                            isSystemAdministrator(currentUser);

  const canManageDocuments = hasRole(currentUser, 'QA Manager') || 
                            hasRole(currentUser, 'QA Specialist') || 
                            hasRole(currentUser, 'Production Manager') ||
                            isSystemAdministrator(currentUser);

  useEffect(() => {
    loadDocuments();
    loadStats();
    dispatch(fetchPendingApprovals());
  }, [pagination.page, filters]);

  // Debounce search to reduce churn and make UX fluid
  useEffect(() => {
    const t = setTimeout(() => {
      if (searchText !== filters.search) {
        dispatch(setFilters({ search: searchText }));
        dispatch(setPagination({ page: 1 }));
      }
    }, 300);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchText]);

  const loadDocuments = () => {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...filters,
    };
    dispatch(fetchDocuments(params));
  };

  const loadStats = () => {
    dispatch(fetchDocumentStats());
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, page: number) => {
    dispatch(setPagination({ page }));
  };

  const handleFilterChange = (field: string, value: any) => {
    dispatch(setFilters({ [field]: value }));
  };

  const handleFilterApply = () => {
    dispatch(setPagination({ page: 1 }));
    loadDocuments();
  };

  const handleFilterClear = () => {
    dispatch(clearFilters());
    dispatch(setPagination({ page: 1 }));
    loadDocuments();
  };

  const handleDocumentSelect = (document: any) => {
    setSelectedDocument(document);
    setViewDialogOpen(true);
  };

  const handleDocumentEdit = (document: any) => {
    setSelectedDocument(document);
    setEditDialogOpen(true);
  };

  const handleDocumentDelete = async (documentId: number) => {
    if (!canDeleteDocuments) {
      return;
    }
    
    if (window.confirm('Are you sure you want to delete this document?')) {
      await dispatch(deleteDocument(documentId));
      loadDocuments();
    }
  };

  const handleDownloadDocument = async (document: any) => {
    try {
      const blob = await dispatch(downloadDocument(document.id)).unwrap();
      const filename = document.original_filename || `${document.title}.pdf`;
      downloadFile(blob, filename);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handleViewVersions = (document: any) => {
    setSelectedDocument(document);
    setVersionDialogOpen(true);
  };

  const handleViewChangeLog = (document: any) => {
    setSelectedDocument(document);
    setChangeLogDialogOpen(true);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, document: any) => {
    setAnchorEl(event.currentTarget);
    setSelectedDocumentForMenu(document);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedDocumentForMenu(null);
  };

  const handleExport = async (format: 'pdf' | 'xlsx') => {
    try {
      const blob = await documentsAPI.exportDocuments(format, { ...filters, page: undefined, size: undefined });
      downloadFile(blob, `documents_export.${format}`);
    } catch (e) {
      console.error('Export failed', e);
    }
  };

  const handleBulkAction = async (action: string) => {
    if (selectedDocuments.length === 0) {
      return;
    }

    try {
      await dispatch(bulkUpdateStatus({ documentIds: selectedDocuments, action }));
      setSelectedDocuments([]);
      loadDocuments();
    } catch (error) {
      console.error('Bulk action failed:', error);
    }
  };

  const handleArchiveObsolete = async () => {
    try {
      await dispatch(archiveObsoleteDocuments());
      loadDocuments();
      loadStats();
    } catch (error) {
      console.error('Archive operation failed:', error);
    }
  };

  const getDocumentTypeIcon = (type: string) => {
    switch (type) {
      case 'procedure':
        return <Description color="primary" />;
      case 'work_instruction':
        return <Description color="secondary" />;
      case 'form':
        return <Description color="success" />;
      case 'policy':
        return <Description color="warning" />;
      case 'manual':
        return <Description color="error" />;
      case 'plan':
        return <Description color="info" />;
      case 'checklist':
        return <Description />;
      default:
        return <Description />;
    }
  };

  const getDocumentTypeLabel = (type?: string) => {
    if (!type || typeof type !== 'string') return 'Unknown';
    return type.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  const renderDocumentRegister = () => (
    <Box>
      {/* Guided process header */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ xs: 'flex-start', md: 'center' }} justifyContent="space-between">
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip label="Upload" color="primary" variant="outlined" onClick={() => setUploadDialogOpen(true)} />
              <Typography variant="body2">→</Typography>
              <Chip label="Review" color="info" variant="outlined" onClick={() => setSelectedTab(1)} />
              <Typography variant="body2">→</Typography>
              <Chip label="Approve" color="success" variant="outlined" onClick={() => setSelectedTab(1)} />
              <Typography variant="body2">→</Typography>
              <Chip label="Distribute" color="secondary" variant="outlined" onClick={() => setSelectedTab(0)} />
              <Typography variant="body2">→</Typography>
              <Chip label="Acknowledge" variant="outlined" />
            </Stack>
            <Stack direction="row" spacing={1}>
              <Button variant="contained" size="small" startIcon={<Add />} onClick={() => setUploadDialogOpen(true)}>New Document</Button>
              <Button variant="outlined" size="small" startIcon={<Approval />} onClick={() => setSelectedTab(1)}>
                Pending Approvals ({pendingApprovals?.length || 0})
              </Button>
              <Button variant="outlined" size="small" startIcon={<EditNote />} onClick={() => setTemplatesDialogOpen(true)}>Templates</Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>
      {/* Filters */}
      {showFilters && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Search documents..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  InputProps={{
                    startAdornment: <FilterAlt sx={{ mr: 1, color: 'text.secondary' }} />
                  }}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={filters.category}
                    onChange={(e) => handleFilterChange('category', e.target.value)}
                  >
                    <MenuItem value="">All Categories</MenuItem>
                    <MenuItem value="haccp">HACCP</MenuItem>
                    <MenuItem value="prp">PRP</MenuItem>
                    <MenuItem value="training">Training</MenuItem>
                    <MenuItem value="audit">Audit</MenuItem>
                    <MenuItem value="maintenance">Maintenance</MenuItem>
                    <MenuItem value="supplier">Supplier</MenuItem>
                    <MenuItem value="quality">Quality</MenuItem>
                    <MenuItem value="safety">Safety</MenuItem>
                    <MenuItem value="general">General</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                  >
                    <MenuItem value="">All Statuses</MenuItem>
                    <MenuItem value="draft">Created</MenuItem>
                    <MenuItem value="under_review">Reviewed</MenuItem>
                    <MenuItem value="approved">Approved</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={filters.document_type}
                    onChange={(e) => handleFilterChange('document_type', e.target.value)}
                  >
                    <MenuItem value="">All Types</MenuItem>
                    <MenuItem value="policy">Policy</MenuItem>
                    <MenuItem value="procedure">Procedure</MenuItem>
                    <MenuItem value="work_instruction">Work Instruction</MenuItem>
                    <MenuItem value="form">Form</MenuItem>
                    <MenuItem value="manual">Manual</MenuItem>
                    <MenuItem value="plan">Plan</MenuItem>
                    <MenuItem value="checklist">Checklist</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Department</InputLabel>
                  <Select
                    value={filters.department}
                    onChange={(e) => handleFilterChange('department', e.target.value)}
                  >
                    <MenuItem value="">All Departments</MenuItem>
                    <MenuItem value="Quality Assurance">Quality Assurance</MenuItem>
                    <MenuItem value="Production">Production</MenuItem>
                    <MenuItem value="Maintenance">Maintenance</MenuItem>
                    <MenuItem value="Management">Management</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={1}>
                <Stack direction="row" spacing={1}>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={handleFilterApply}
                    startIcon={<FilterAlt />}
                  >
                    Apply
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={handleFilterClear}
                    startIcon={<Clear />}
                  >
                    Clear
                  </Button>
                </Stack>
              </Grid>
              
              {/* Advanced Filters */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2, mb: 1 }}>
                  Advanced Filters
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  type="date"
                  label="Created From"
                  value={filters.date_from}
                  onChange={(e) => handleFilterChange('date_from', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  type="date"
                  label="Created To"
                  value={filters.date_to}
                  onChange={(e) => handleFilterChange('date_to', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  type="date"
                  label="Review Date From"
                  value={filters.review_date_from}
                  onChange={(e) => handleFilterChange('review_date_from', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  type="date"
                  label="Review Date To"
                  value={filters.review_date_to}
                  onChange={(e) => handleFilterChange('review_date_to', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Active filter chips */}
      {(() => {
        const active: Array<{ key: string; label: string; value: string }> = [];
        const labelMap: Record<string, string> = {
          category: 'Category',
          status: 'Status',
          document_type: 'Type',
          department: 'Department',
          date_from: 'Created From',
          date_to: 'Created To',
          review_date_from: 'Review From',
          review_date_to: 'Review To',
        };
        Object.entries(filters || {}).forEach(([k, v]) => {
          if (k === 'search') return;
          if (v) active.push({ key: k, label: labelMap[k] || k, value: String(v) });
        });
        return active.length > 0 ? (
          <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 2 }}>
            {active.map((f) => (
              <Chip
                key={f.key}
                label={`${f.label}: ${f.value}`}
                onDelete={() => handleFilterChange(f.key, '')}
                variant="outlined"
                size="small"
              />
            ))}
            <Button size="small" onClick={handleFilterClear} startIcon={<Clear />}>Clear All</Button>
          </Stack>
        ) : null;
      })()}

      {/* Document Table */}
        {selectedDocuments.length > 0 && (
        <Alert severity="info" sx={{ mb: 2 }}
          action={
            <Stack direction="row" spacing={1}>
              <Button size="small" onClick={() => handleBulkAction('archive')} startIcon={<Archive />}>Archive</Button>
              <Button size="small" color="warning" onClick={() => handleBulkAction('obsolete')} startIcon={<Warning />}>Mark Obsolete</Button>
              <Button size="small" variant="outlined" onClick={() => setSelectedDocuments([])}>Clear</Button>
            </Stack>
          }
        >
          {selectedDocuments.length} selected
        </Alert>
      )}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedDocuments.length === documents.length && documents.length > 0}
                  indeterminate={selectedDocuments.length > 0 && selectedDocuments.length < documents.length}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedDocuments(documents.map(doc => doc.id));
                    } else {
                      setSelectedDocuments([]);
                    }
                  }}
                />
              </TableCell>
              <TableCell>Document</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell>Review Date</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {documents.map((document) => (
              <TableRow key={document.id} hover onClick={() => handleDocumentSelect(document)} sx={{ cursor: 'pointer' }}>
                <TableCell padding="checkbox" onClick={(e) => e.stopPropagation()}>
                  <Checkbox
                    checked={selectedDocuments.includes(document.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedDocuments([...selectedDocuments, document.id]);
                      } else {
                        setSelectedDocuments(selectedDocuments.filter(id => id !== document.id));
                      }
                    }}
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getDocumentTypeIcon(document.document_type)}
                    <Box>
                      <Typography variant="body2" fontWeight={600}>
                        {document.title}
                      </Typography>
                  <Typography variant="caption" color="text.secondary">
                        {document.document_number || '—'} • v{document.version}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={getDocumentTypeLabel(document.document_type)} 
                    size="small" 
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <StatusChip
                    status={document.status === 'approved' ? 'compliant' : 
                           document.status === 'under_review' ? 'pending' : 
                           document.status === 'draft' ? 'warning' : 
                           document.status === 'obsolete' ? 'nonConformance' : 'info'}
                    label={document.status === 'draft' ? 'Created' : document.status === 'under_review' ? 'Reviewed' : document.status === 'approved' ? 'Approved' : (document.status || 'unknown').replace('_', ' ')}
                  />
                </TableCell>
                <TableCell>{document.department || '-'}</TableCell>
                <TableCell>{(document as any).owner_name || document.created_by || '—'}</TableCell>
                <TableCell>{document.review_date ? new Date(document.review_date).toLocaleDateString() : '—'}</TableCell>
                <TableCell align="right" onClick={(e) => e.stopPropagation()}>
                  <Stack direction="row" spacing={1} justifyContent="flex-end">
                    <Tooltip title="View Document">
                      <IconButton 
                        size="small" 
                        onClick={() => handleDocumentSelect(document)}
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    {canManageDocuments && (
                      <Tooltip title="Edit Document">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDocumentEdit(document)}
                        >
                          <Edit />
                        </IconButton>
                      </Tooltip>
                    )}
                    {document.file_path && (
                      <Tooltip title="Download">
                        <IconButton 
                          size="small"
                          onClick={() => handleDownloadDocument(document)}
                        >
                          <Download />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="More Actions">
                        <IconButton 
                          size="small" 
                        onClick={(e) => handleMenuOpen(e, document)}
                        >
                        <MoreVert />
                        </IconButton>
                      </Tooltip>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {pagination.pages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={pagination.pages}
            page={pagination.page}
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      )}

      {/* Document Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        {/* Removed direct Approve Document entry; use Workflow instead */}
        <MenuItemComponent onClick={() => {
          handleViewVersions(selectedDocumentForMenu);
          handleMenuClose();
        }}>
          <ListItemIcon>
            <HistoryIcon fontSize="small" />
          </ListItemIcon>
          View Version History
        </MenuItemComponent>
        <MenuItemComponent onClick={() => {
          handleViewChangeLog(selectedDocumentForMenu);
          handleMenuClose();
        }}>
          <ListItemIcon>
            <Timeline fontSize="small" />
          </ListItemIcon>
          View Change Log
        </MenuItemComponent>
        <MenuItemComponent onClick={() => {
          setSelectedDocument(selectedDocumentForMenu);
          setWorkflowDialogOpen(true);
          handleMenuClose();
        }}>
          <ListItemIcon>
            <Timeline fontSize="small" />
          </ListItemIcon>
          View Workflow
        </MenuItemComponent>
        {/* Removed conditional Approve entry; Workflow handles approvals */}
        <MenuItemComponent onClick={() => {
          setSelectedDocument(selectedDocumentForMenu);
          setComparisonDialogOpen(true);
          handleMenuClose();
        }}>
          <ListItemIcon>
            <Compare fontSize="small" />
          </ListItemIcon>
          Compare Versions
        </MenuItemComponent>
        {selectedDocumentForMenu?.file_path && (
          <MenuItemComponent onClick={() => {
            handleDownloadDocument(selectedDocumentForMenu);
            handleMenuClose();
          }}>
            <ListItemIcon>
              <Download fontSize="small" />
            </ListItemIcon>
            Download Current Version
          </MenuItemComponent>
        )}
        {canManageDocuments && (
          <MenuItemComponent onClick={() => {
            handleDocumentEdit(selectedDocumentForMenu);
            handleMenuClose();
          }}>
            <ListItemIcon>
              <Edit fontSize="small" />
            </ListItemIcon>
            Edit Document
          </MenuItemComponent>
        )}
        {canDeleteDocuments && (
          <MenuItemComponent 
            onClick={() => {
              handleDocumentDelete(selectedDocumentForMenu.id);
              handleMenuClose();
            }}
            sx={{ color: 'error.main' }}
          >
            <ListItemIcon>
              <Delete fontSize="small" color="error" />
            </ListItemIcon>
            Delete Document
          </MenuItemComponent>
        )}
        {/* Status transitions */}
        <MenuItemComponent onClick={() => { setReasonDialog({ open: true, action: 'obsolete', doc: selectedDocumentForMenu, reason: '' }); handleMenuClose(); }}>
          <ListItemIcon>
            <Archive fontSize="small" />
          </ListItemIcon>
          Mark Obsolete
        </MenuItemComponent>
        <MenuItemComponent onClick={() => { setReasonDialog({ open: true, action: 'archive', doc: selectedDocumentForMenu, reason: '' }); handleMenuClose(); }}>
          <ListItemIcon>
            <Archive fontSize="small" />
          </ListItemIcon>
          Archive
        </MenuItemComponent>
        <MenuItemComponent onClick={() => { setReasonDialog({ open: true, action: 'activate', doc: selectedDocumentForMenu, reason: '' }); handleMenuClose(); }}>
          <ListItemIcon>
            <Approval fontSize="small" />
          </ListItemIcon>
          Activate
        </MenuItemComponent>

        {/* Controlled distribution */}
        <MenuItemComponent onClick={async () => {
          try {
            // Lazy load users for selection
            const resp: any = await (await import('../services/api')).documentsAPI.getApprovalUsers();
            setDistributionUsers(resp.data || []);
          } catch (e) {
            console.error('Failed to load users', e);
          }
          setSelectedDistributionUserIds([]);
          setDistributeDialog({ open: true, doc: selectedDocumentForMenu });
          handleMenuClose();
        }}>
          <ListItemIcon>
            <Approval fontSize="small" />
          </ListItemIcon>
          Distribute
        </MenuItemComponent>
      </Menu>
    </Box>
  );

  const renderPendingApprovals = () => {
    return (
      <Grid container spacing={3}>
        {pendingApprovals.map((item: any) => (
          <Grid item xs={12} md={6} key={`${item.document_id}-${item.id || item.approval_id}`}>
            <Card>
              <CardHeader
                title={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Description color="warning" />
                    <Typography variant="h6" fontWeight={600}>
                      {item.document_title || item.title || `Document #${item.document_id}`}
                    </Typography>
                  </Box>
                }
                subheader={`${item.document_number || ''} ${item.version ? `• v${item.version}` : ''}`}
                action={<StatusChip status="pending" label="Your Approval Required" />}
              />
              <CardContent>
                <Stack spacing={2}>
                  <Box>
                    {item.created_by && (
                      <Typography variant="body2" color="text.secondary">Created by: {item.created_by}</Typography>
                    )}
                    {item.created_at && (
                      <Typography variant="body2" color="text.secondary">Requested: {new Date(item.created_at).toLocaleDateString()}</Typography>
                    )}
                  </Box>
                  <Stack direction="row" spacing={1}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<Approval />}
                      onClick={async () => {
                        try {
                          await dispatch(approveApprovalStep({ documentId: item.document_id, approvalId: item.id || item.approval_id })).unwrap();
                          dispatch(fetchPendingApprovals());
                          loadDocuments();
                        } catch (e) {
                          console.error('Approval failed', e);
                        }
                      }}
                    >
                      Approve
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={async () => {
                        try {
                          await dispatch(rejectApprovalStep({ documentId: item.document_id, approvalId: item.id || item.approval_id })).unwrap();
                          dispatch(fetchPendingApprovals());
                          loadDocuments();
                        } catch (e) {
                          console.error('Rejection failed', e);
                        }
                      }}
                    >
                      Reject
                    </Button>
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
        {pendingApprovals.length === 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <CheckCircle color="success" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No Pending Approvals
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  You have no approval tasks at the moment.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    );
  };

  const renderVersionControl = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardHeader
            title="Document Version History"
            titleTypographyProps={{ variant: 'h6', fontWeight: 600 }}
          />
          <CardContent>
            <List>
              {documents.map((doc) => (
                <ListItem key={doc.id} divider>
                  <ListItemIcon>
                    {getDocumentTypeIcon(doc.document_type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Typography variant="body1" fontWeight={500}>
                          {doc.title}
                        </Typography>
                        <Chip label={`v${doc.version}`} size="small" />
                        <StatusChip
                          status={doc.status === 'approved' ? 'compliant' : 
                                 doc.status === 'under_review' ? 'pending' : 
                                 doc.status === 'draft' ? 'warning' : 'info'}
                          label={doc.status === 'draft' ? 'Created' : doc.status === 'under_review' ? 'Reviewed' : doc.status === 'approved' ? 'Approved' : doc.status.replace('_', ' ')}
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {doc.document_number} • Created by: {doc.created_by}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Last Modified: {doc.updated_at ? new Date(doc.updated_at).toLocaleDateString() : 
                                         new Date(doc.created_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Stack direction="row" spacing={1}>
                      <Tooltip title="View History">
                        <IconButton 
                          size="small"
                          onClick={() => handleViewVersions(doc)}
                        >
                          <HistoryIcon />
                        </IconButton>
                      </Tooltip>
                      {doc.file_path && (
                        <Tooltip title="Download">
                          <IconButton size="small" onClick={() => handleDownloadDocument(doc)}>
                            <Download />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Stack>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  return (
    <Box>
      <PageHeader
        title="Document Control"
                      subtitle="Compli FSMS Document Management System"
        breadcrumbs={[
          { label: 'Dashboard', path: '/' },
          { label: 'Document Control', path: '/documents' }
        ]}
        showAdd={canCreateDocuments}
        showExport
        onAdd={() => setUploadDialogOpen(true)}
        onExport={() => handleExport('pdf')}
      />

      {/* Document Statistics */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Description color="primary" sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4" fontWeight={700}>
                      {stats.total_documents}
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
                  <Approval color="warning" sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4" fontWeight={700}>
                      {stats.documents_requiring_approval}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Pending Approval
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
                      {stats.documents_by_status.approved || 0}
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
                  <Warning color="error" sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4" fontWeight={700}>
                      {stats.expired_documents}
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
      )}

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => dispatch({ type: 'documents/clearError' })}>
          {error}
        </Alert>
      )}

      {stats?.expired_documents && stats.expired_documents > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Expired Documents:</strong> {stats.expired_documents} document(s) require review. 
            Please update or extend review dates to maintain compliance.
          </Typography>
        </Alert>
      )}

      {/* Action Bar */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Button
          variant="outlined"
          startIcon={<FilterAlt />}
          onClick={() => setShowFilters(!showFilters)}
        >
          {showFilters ? 'Hide' : 'Show'} Filters
        </Button>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadDocuments}
        >
          Refresh
        </Button>
        {selectedDocuments.length > 0 && (
          <>
            <Button
              variant="outlined"
              startIcon={<Archive />}
              onClick={() => handleBulkAction('archive')}
            >
              Archive Selected
            </Button>
            <Button
              variant="outlined"
              startIcon={<Delete />}
              onClick={() => handleBulkAction('delete')}
              color="error"
            >
              Delete Selected
            </Button>
          </>
        )}
        {canApproveDocuments && (
          <Button
            variant="outlined"
            startIcon={<Archive />}
            onClick={handleArchiveObsolete}
          >
            Archive Obsolete
          </Button>
        )}
        <Button
          variant="outlined"
          startIcon={<Description />}
          onClick={() => setTemplatesDialogOpen(true)}
        >
          Templates
        </Button>
        <Button
          variant="outlined"
          startIcon={<Assessment />}
          onClick={() => setAnalyticsDialogOpen(true)}
        >
          Analytics
        </Button>
      </Box>

      {/* Loading */}
      {loading && <LinearProgress sx={{ mb: 3 }} />}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          aria-label="document control tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Document Register" />
          <Tab label="Pending Approvals" />
          <Tab label="Version Control" />
        </Tabs>
      </Paper>

      <TabPanel value={selectedTab} index={0}>
        {renderDocumentRegister()}
      </TabPanel>
      <TabPanel value={selectedTab} index={1}>
        {renderPendingApprovals()}
      </TabPanel>
      <TabPanel value={selectedTab} index={2}>
        {renderVersionControl()}
      </TabPanel>

      {/* Dialogs */}
      <DocumentUploadDialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        onSuccess={() => {
          setUploadDialogOpen(false);
          loadDocuments();
        }}
      />

      <DocumentViewDialog
        open={viewDialogOpen}
        document={selectedDocument}
        onClose={() => setViewDialogOpen(false)}
        onEdit={() => {
          setViewDialogOpen(false);
          handleDocumentEdit(selectedDocument);
        }}
      />

      <DocumentVersionDialog
        open={versionDialogOpen}
        document={selectedDocument}
        onClose={() => setVersionDialogOpen(false)}
      />

      {/* Approval dialog removed in favor of Workflow dialog */}

      <DocumentChangeLogDialog
        open={changeLogDialogOpen}
        document={selectedDocument}
        onClose={() => setChangeLogDialogOpen(false)}
      />

      <DocumentTemplatesDialog
        open={templatesDialogOpen}
        onClose={() => setTemplatesDialogOpen(false)}
        onTemplateSelect={(template) => {
          console.log('Template selected:', template);
          // Handle template selection - could pre-fill upload form
        }}
      />

      <DocumentWorkflowDialog
        open={workflowDialogOpen}
        document={selectedDocument}
        onClose={() => setWorkflowDialogOpen(false)}
        onWorkflowUpdate={(workflow) => {
          console.log('Workflow updated:', workflow);
          // Handle workflow updates
        }}
      />

      <DocumentAnalyticsDialog
        open={analyticsDialogOpen}
        onClose={() => setAnalyticsDialogOpen(false)}
      />

      <DocumentComparisonDialog
        open={comparisonDialogOpen}
        document={selectedDocument}
        onClose={() => setComparisonDialogOpen(false)}
      />

      <DocumentEditDialog
        open={editDialogOpen}
        document={selectedDocument}
        onClose={() => setEditDialogOpen(false)}
        onSuccess={() => {
          setEditDialogOpen(false);
          loadDocuments();
        }}
      />

      {/* Reason Dialog for status transitions */}
      <Dialog open={reasonDialog.open} onClose={() => setReasonDialog({ open: false, action: null, doc: null, reason: '' })} maxWidth="sm" fullWidth>
        <DialogTitle>{reasonDialog.action === 'obsolete' ? 'Mark as Obsolete' : reasonDialog.action === 'archive' ? 'Archive Document' : 'Activate Document'}</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Reason (optional unless obsolete/archive)" value={reasonDialog.reason}
            onChange={(e) => setReasonDialog(prev => ({ ...prev, reason: e.target.value }))}
            multiline rows={3} sx={{ mt: 1 }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReasonDialog({ open: false, action: null, doc: null, reason: '' })}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            if (!reasonDialog.doc || !reasonDialog.action) return;
            try {
              if (reasonDialog.action === 'obsolete') {
                await (await import('../services/api')).documentsAPI.markObsolete(reasonDialog.doc.id, reasonDialog.reason || '');
              } else if (reasonDialog.action === 'archive') {
                await (await import('../services/api')).documentsAPI.archiveDocument(reasonDialog.doc.id, reasonDialog.reason || '');
              } else if (reasonDialog.action === 'activate') {
                await (await import('../services/api')).documentsAPI.activateDocument(reasonDialog.doc.id, reasonDialog.reason || '');
              }
              setReasonDialog({ open: false, action: null, doc: null, reason: '' });
              loadDocuments();
              loadStats();
            } catch (e) { console.error('Status change failed', e); }
          }}>Confirm</Button>
        </DialogActions>
      </Dialog>

      {/* Distribution Dialog */}
      <Dialog open={distributeDialog.open} onClose={() => setDistributeDialog({ open: false, doc: null })} maxWidth="sm" fullWidth>
        <DialogTitle>Distribute Document</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 1 }}>Select recipients</Typography>
          <Box sx={{ maxHeight: 300, overflowY: 'auto', border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 1 }}>
            {distributionUsers.map((u: any) => (
              <Box key={u.id} sx={{ display: 'flex', alignItems: 'center' }}>
                <Checkbox
                  checked={selectedDistributionUserIds.includes(u.id)}
                  onChange={(e) => {
                    setSelectedDistributionUserIds(prev => e.target.checked ? [...prev, u.id] : prev.filter(id => id !== u.id));
                  }}
                />
                <Typography variant="body2">{u.full_name || u.username} ({u.email})</Typography>
              </Box>
            ))}
            {distributionUsers.length === 0 && <Typography variant="body2" color="text.secondary">No users found.</Typography>}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDistributeDialog({ open: false, doc: null })}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            if (!distributeDialog.doc) return;
            try {
              await (await import('../services/api')).documentsAPI.distributeDocument(distributeDialog.doc.id, { user_ids: selectedDistributionUserIds });
              setDistributeDialog({ open: false, doc: null });
            } catch (e) { console.error('Distribute failed', e); }
          }} disabled={selectedDistributionUserIds.length === 0}>Send</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Documents; 