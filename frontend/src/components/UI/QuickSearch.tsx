import React, { useState, useEffect } from 'react';
import {
  TextField,
  InputAdornment,
  Popper,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Typography,
  Box,
  Chip,
  CircularProgress,
  ClickAwayListener,
} from '@mui/material';
import {
  Search,
  Description,
  Security,
  Assignment,
  Timeline,
  Warning,
  Person,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';

interface SearchResult {
  id: string;
  title: string;
  type: 'document' | 'haccp' | 'prp' | 'nc' | 'user' | 'audit';
  path: string;
  description?: string;
  status?: string;
}

interface QuickSearchProps {
  placeholder?: string;
  fullWidth?: boolean;
}

const QuickSearch: React.FC<QuickSearchProps> = ({
  placeholder = "Search documents, HACCP plans, NCs...",
  fullWidth = false,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  
  const navigate = useNavigate();

  const performSearch = async (term: string) => {
    if (!term.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      // Start with documents search since BE supports it robustly
      const resp = await api.get('/documents', { params: { search: term, page: 1, size: 5 } });
      const docs = resp?.data?.data?.items || resp?.data?.items || [];
      const docResults: SearchResult[] = docs.map((d: any) => ({
        id: String(d.id),
        title: d.title || d.document_number,
        type: 'document',
        path: `/documents`,
        description: d.description,
        status: d.status,
      }));

      // Future: extend to HACCP/PRP/NC using their list endpoints
      setResults(docResults);
    } catch (e) {
      setResults([]);
    } finally {
    setLoading(false);
    }
  };

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      performSearch(searchTerm);
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [searchTerm]);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchTerm(value);
    setOpen(value.length > 0);
  };

  const handleResultClick = (result: SearchResult) => {
    navigate(result.path);
    setSearchTerm('');
    setOpen(false);
  };

  const handleInputFocus = (event: React.FocusEvent<HTMLInputElement>) => {
    setAnchorEl(event.currentTarget);
    if (searchTerm.length > 0) {
      setOpen(true);
    }
  };

  const handleClickAway = () => {
    setOpen(false);
  };

  const getTypeIcon = (type: SearchResult['type']) => {
    switch (type) {
      case 'document':
        return <Description fontSize="small" />;
      case 'haccp':
        return <Security fontSize="small" />;
      case 'prp':
        return <Assignment fontSize="small" />;
      case 'nc':
        return <Warning fontSize="small" />;
      case 'audit':
        return <Timeline fontSize="small" />;
      case 'user':
        return <Person fontSize="small" />;
      default:
        return <Description fontSize="small" />;
    }
  };

  const getTypeColor = (type: SearchResult['type']) => {
    switch (type) {
      case 'document':
        return 'primary';
      case 'haccp':
        return 'error';
      case 'prp':
        return 'warning';
      case 'nc':
        return 'error';
      case 'audit':
        return 'info';
      case 'user':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <ClickAwayListener onClickAway={handleClickAway}>
      <Box sx={{ position: 'relative' }}>
        <TextField
          fullWidth={fullWidth}
          size="small"
          placeholder={placeholder}
          value={searchTerm}
          onChange={handleSearchChange}
          onFocus={handleInputFocus}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search fontSize="small" />
              </InputAdornment>
            ),
            endAdornment: loading ? (
              <InputAdornment position="end">
                <CircularProgress size={20} />
              </InputAdornment>
            ) : undefined,
          }}
          sx={{
            minWidth: fullWidth ? '100%' : 300,
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
              backgroundColor: 'background.paper',
              boxShadow: '0 1px 2px rgba(0,0,0,0.04) inset',
            },
          }}
        />

        <Popper
          open={open && (results.length > 0 || loading)}
          anchorEl={anchorEl}
          placement="bottom-start"
          style={{ zIndex: 1300, width: anchorEl?.offsetWidth }}
        >
          <Paper
            elevation={8}
            sx={{
              mt: 1,
              maxHeight: 400,
              overflow: 'auto',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 2,
              backdropFilter: 'blur(8px)',
              background: (theme) => theme.palette.mode === 'light'
                ? 'rgba(255,255,255,0.9)'
                : 'rgba(2,6,23,0.9)',
            }}
          >
            {loading ? (
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <CircularProgress size={20} />
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Searching...
                </Typography>
              </Box>
            ) : results.length > 0 ? (
              <List dense>
                {results.map((result) => (
                  <ListItem
                    key={result.id}
                    button
                    onClick={() => handleResultClick(result)}
                    sx={{
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    }}
                  >
                    <ListItemIcon>
                      {getTypeIcon(result.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" fontWeight={500}>
                            {result.title}
                          </Typography>
                          <Chip
                            label={result.type.toUpperCase()}
                            size="small"
                            color={getTypeColor(result.type)}
                            sx={{ fontSize: '0.625rem', height: 20 }}
                          />
                        </Box>
                      }
                      secondary={
                        <Typography variant="caption" color="text.secondary">
                          {result.description}
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            ) : searchTerm.length > 0 ? (
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  No results found
                </Typography>
              </Box>
            ) : null}
          </Paper>
        </Popper>
      </Box>
    </ClickAwayListener>
  );
};

export default QuickSearch; 