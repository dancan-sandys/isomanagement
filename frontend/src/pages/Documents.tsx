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
  Badge,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  LinearProgress,
  CircularProgress,
  Pagination,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  InputAdornment,
  Menu,
  MenuItem as MenuItemComponent,
} from '@mui/material';
import {
  Description,
  CloudUpload,
  History,
  Approval,
  Visibility,
  Edit,
  Delete,
  Download,
  Share,
  Warning,
  CheckCircle,
  Schedule,
  Add,
  FilterList,
  Search,
  Refresh,
  Archive,
  FileCopy,
  Lock,
  LockOpen,
  MoreVert,
  Upload,
  GetApp,
  VisibilityOff,
  EditNote,
  History as HistoryIcon,
  Timeline,
  Assessment,
  TrendingUp,
  TrendingDown,
  FilterAlt,
  Clear,
  CalendarToday,
  AccessTime,
  Person,
  Business,
  Category,
  Label,
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
  fetchExpiredDocuments,
  setFilters,
  clearFilters,
  setPagination,
  setSelectedDocument,
  downloadDocument,
  downloadVersion,
  fetchDocumentVersions,
  fetchChangeLog,
} from '../store/slices/documentSlice';
import { hasRole, isSystemAdministrator, canManageUsers } from '../store/slices/authSlice';
import PageHeader from '../components/UI/PageHeader';
import StatusChip from '../components/UI/StatusChip';
import DocumentUploadDialog from '../components/Documents/DocumentUploadDialog';
import DocumentViewDialog from '../components/Documents/DocumentViewDialog';
import DocumentVersionDialog from '../components/Documents/DocumentVersionDialog';
import DocumentApprovalDialog from '../components/Documents/DocumentApprovalDialog';
import DocumentChangeLogDialog from '../components/Documents/DocumentChangeLogDialog';
import DocumentTemplatesDialog from '../components/Documents/DocumentTemplatesDialog';
import DocumentWorkflowDialog from '../components/Documents/DocumentWorkflowDialog';
import DocumentAnalyticsDialog from '../components/Documents/DocumentAnalyticsDialog';
import DocumentComparisonDialog from '../components/Documents/DocumentComparisonDialog';
import { downloadFile, formatFileSize, getFileIcon } from '../utils/downloadUtils';

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
  const navigate = useNavigate();
  const { user: currentUser } = useSelector((state: RootState) => state.auth);
  const { documents, stats, loading, error, pagination, filters } = useSelector((state: RootState) => state.documents);
  
  const [selectedTab, setSelectedTab] = useState(0);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [versionDialogOpen, setVersionDialogOpen] = useState(false);
  const [approvalDialogOpen, setApprovalDialogOpen] = useState(false);
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
  }, [pagination.page, filters]);

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
    // Navigate to edit page or open edit dialog
    console.log('Edit document:', document);
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

  const handleDownloadVersion = async (documentId: number, versionId: number, filename: string) => {
    try {
      const blob = await dispatch(downloadVersion({ documentId, versionId })).unwrap();
      downloadFile(blob, filename);
    } catch (error) {
      console.error('Version download failed:', error);
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

  const getDocumentTypeLabel = (type: string) => {
    return type.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'under_review':
        return 'warning';
      case 'draft':
        return 'info';
      case 'obsolete':
        return 'error';
      case 'archived':
        return 'default';
      default:
        return 'default';
    }
  };

  const renderDocumentRegister = () => (
    <Box>
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
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  InputProps={{
                    startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
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
                    <MenuItem value="draft">Draft</MenuItem>
                    <MenuItem value="under_review">Under Review</MenuItem>
                    <MenuItem value="approved">Approved</MenuItem>
                    <MenuItem value="obsolete">Obsolete</MenuItem>
                    <MenuItem value="archived">Archived</MenuItem>
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

      {/* Document Table */}
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
              <TableCell>Created By</TableCell>
              <TableCell>Last Modified</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {documents.map((document) => (
              <TableRow key={document.id} hover>
                <TableCell padding="checkbox">
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
                        {document.document_number} • v{document.version}
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
                    label={document.status.replace('_', ' ')}
                  />
                </TableCell>
                <TableCell>{document.department || '-'}</TableCell>
                <TableCell>{document.created_by}</TableCell>
                <TableCell>
                  {document.updated_at ? new Date(document.updated_at).toLocaleDateString() : 
                   new Date(document.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1}>
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
        {canApproveDocuments && (
          <MenuItemComponent onClick={() => {
            setSelectedDocument(selectedDocumentForMenu);
            setApprovalDialogOpen(true);
            handleMenuClose();
          }}>
            <ListItemIcon>
              <Approval fontSize="small" />
            </ListItemIcon>
            Approve Document
          </MenuItemComponent>
        )}
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
        {canApproveDocuments && selectedDocumentForMenu?.status === 'under_review' && (
          <MenuItemComponent onClick={() => {
            setSelectedDocument(selectedDocumentForMenu);
            setApprovalDialogOpen(true);
            handleMenuClose();
          }}>
            <ListItemIcon>
              <Approval fontSize="small" />
            </ListItemIcon>
            Approve Document
          </MenuItemComponent>
        )}
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
      </Menu>
    </Box>
  );

  const renderPendingApprovals = () => {
    const pendingDocs = documents.filter(doc => doc.status === 'under_review');
    
    return (
      <Grid container spacing={3}>
        {pendingDocs.map((doc) => (
          <Grid item xs={12} md={6} key={doc.id}>
            <Card>
              <CardHeader
                title={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getDocumentTypeIcon(doc.document_type)}
                    <Typography variant="h6" fontWeight={600}>
                      {doc.title}
                    </Typography>
                  </Box>
                }
                subheader={`${doc.document_number} • v${doc.version} • ${doc.department || 'No Department'}`}
                action={
                  <StatusChip
                    status="pending"
                    label="Under Review"
                  />
                }
              />
              <CardContent>
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Created by: {doc.created_by}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Last Modified: {doc.updated_at ? new Date(doc.updated_at).toLocaleDateString() : 
                                     new Date(doc.created_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                  <Stack direction="row" spacing={1}>
                    {canApproveDocuments && (
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<Approval />}
                        onClick={() => {
                          setSelectedDocument(doc);
                          setApprovalDialogOpen(true);
                        }}
                      >
                        Approve
                      </Button>
                    )}
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<Visibility />}
                      onClick={() => handleDocumentSelect(doc)}
                    >
                      View
                    </Button>
                    {canManageDocuments && (
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<Edit />}
                        onClick={() => handleDocumentEdit(doc)}
                      >
                        Edit
                      </Button>
                    )}
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
        {pendingDocs.length === 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <CheckCircle color="success" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No Pending Approvals
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  All documents are either approved or in draft status.
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
                          label={doc.status.replace('_', ' ')}
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
                      <Tooltip title="Share">
                        <IconButton size="small">
                          <Share />
                        </IconButton>
                      </Tooltip>
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
        subtitle="ISO 22000 Document Management System"
        breadcrumbs={[
          { label: 'Dashboard', path: '/' },
          { label: 'Document Control', path: '/documents' }
        ]}
        showAdd={canCreateDocuments}
        showExport
        onAdd={() => setUploadDialogOpen(true)}
        onExport={() => console.log('Export documents')}
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

      <DocumentApprovalDialog
        open={approvalDialogOpen}
        document={selectedDocument}
        onClose={() => setApprovalDialogOpen(false)}
        onSuccess={() => {
          setApprovalDialogOpen(false);
          loadDocuments();
        }}
      />

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
    </Box>
  );
};

export default Documents; 