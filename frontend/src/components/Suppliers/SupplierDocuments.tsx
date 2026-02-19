import React, { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Button, Chip, LinearProgress, Paper, Stack, Typography } from '@mui/material';
import { OpenInNew, Refresh } from '@mui/icons-material';
import { AppDispatch, RootState } from '../../store';
import { fetchDocuments, setFilters, setPagination } from '../../store/slices/documentSlice';
import SmartDataTable, { TableColumn, TableAction } from '../Tables/SmartDataTable';
import { useNavigate } from 'react-router-dom';

const SupplierDocuments: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { documents, loading } = useSelector((state: RootState) => state.documents);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (initialized) return;
    setInitialized(true);
    dispatch(setFilters({ category: 'supplier' }));
    dispatch(setPagination({ page: 1 }));
    dispatch(fetchDocuments({ page: 1, size: 10, category: 'supplier' }));
  }, [dispatch, initialized]);

  const columns: TableColumn[] = useMemo(() => [
    { id: 'document_number', label: 'Number', sortable: true },
    { id: 'title', label: 'Title', sortable: true, searchable: true },
    { id: 'document_type', label: 'Type', sortable: true, format: (v) => (typeof v === 'string' ? v.replace('_', ' ') : v) },
    { id: 'status', label: 'Status', sortable: true, type: 'status', format: (v) => <Chip size="small" label={(v || '').replace('_', ' ')} /> },
    { id: 'version', label: 'Version', sortable: true },
    { id: 'created_at', label: 'Created', sortable: true },
  ], []);

  const actions: TableAction[] = useMemo(() => [
    {
      id: 'open-docs',
      label: 'Open in Documents',
      icon: <OpenInNew fontSize="small" />,
      onClick: () => navigate('/documents?category=supplier'),
    },
  ], [navigate]);

  const handleRefresh = () => {
    dispatch(fetchDocuments({ page: 1, size: 10, category: 'supplier' }));
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Supplier Documents</Typography>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<OpenInNew />}
            onClick={() => navigate('/documents?category=supplier')}
          >
            Open in Documents
          </Button>
          <Button
            variant="contained"
            size="small"
            startIcon={<Refresh />}
            onClick={handleRefresh}
          >
            Refresh
          </Button>
        </Stack>
      </Box>
      <Paper>
        {loading && <LinearProgress />}
        <SmartDataTable
          title="Supplier Documents"
          columns={columns}
          data={documents}
          actions={actions}
          enableInsights={false}
          enableExport={false}
          enableColumnCustomization={false}
          loading={loading}
        />
      </Paper>
    </Box>
  );
};

export default SupplierDocuments;

