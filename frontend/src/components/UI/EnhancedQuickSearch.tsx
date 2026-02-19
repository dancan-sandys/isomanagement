import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Chip,
  InputAdornment,
  Fade,
  Divider,
  Avatar,
  Stack,
  Skeleton,
} from '@mui/material';
import {
  Search,
  Description,
  Assignment,
  People,
  Business,
  Settings,
  History,
  TrendingUp,
  Star,
  AccessTime,
  AutoAwesome,
  Lightbulb,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { searchAPI } from '../../services/api';

interface SearchResult {
  id: string;
  title: string;
  description: string;
  category: string;
  path: string;
  icon: React.ReactNode;
  priority: number;
  lastUsed?: Date;
  isBookmarked?: boolean;
}

interface SearchSuggestion {
  id: string;
  text: string;
  category: string;
  icon: React.ReactNode;
  action: () => void;
}

interface EnhancedQuickSearchProps {
  placeholder?: string;
  fullWidth?: boolean;
}

const EnhancedQuickSearch: React.FC<EnhancedQuickSearchProps> = ({
  placeholder = "Search everything...",
  fullWidth = false,
}) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const searchRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);

  // Simulate search data
  const searchData: SearchResult[] = [
    {
      id: '1',
      title: 'HACCP Plan - Milk Processing',
      description: 'Critical Control Points for pasteurized milk products',
      category: 'HACCP',
      path: '/haccp/products/1',
      icon: <Assignment color="primary" />,
      priority: 10,
      lastUsed: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
      isBookmarked: true,
    },
    {
      id: '2',
      title: 'Supplier Evaluation - Dairy Farms Inc',
      description: 'Monthly supplier performance review',
      category: 'Suppliers',
      path: '/suppliers',
      icon: <Business color="success" />,
      priority: 8,
    },
    {
      id: '3',
      title: 'PRP Checklist - Sanitation',
      description: 'Daily sanitation verification checklist',
      category: 'PRP',
      path: '/prp',
      icon: <Assignment color="warning" />,
      priority: 9,
    },
    {
      id: '4',
      title: 'Document Control Policy',
      description: 'ISO 22000 document control procedures',
      category: 'Documents',
      path: '/documents',
      icon: <Description color="info" />,
      priority: 7,
    },
    {
      id: '5',
      title: 'User Management',
      description: 'Manage system users and permissions',
      category: 'System',
      path: '/users',
      icon: <People color="secondary" />,
      priority: 6,
    },
  ];

  // Smart suggestions based on role and context
  const smartSuggestions: SearchSuggestion[] = [
    {
      id: 'quick-1',
      text: 'Create new HACCP plan',
      category: 'Quick Actions',
      icon: <AutoAwesome color="primary" />,
      action: () => navigate('/haccp'),
    },
    {
      id: 'quick-2',
      text: 'Schedule supplier audit',
      category: 'Quick Actions',
      icon: <Lightbulb color="warning" />,
      action: () => navigate('/suppliers'),
    },
    {
      id: 'recent-1',
      text: 'Yesterday: "CCP monitoring"',
      category: 'Recent Searches',
      icon: <History color="action" />,
      action: () => setQuery('CCP monitoring'),
    },
    {
      id: 'trending-1',
      text: 'Trending: "Non-conformance reports"',
      category: 'Trending',
      icon: <TrendingUp color="success" />,
      action: () => setQuery('Non-conformance reports'),
    },
  ];

  useEffect(() => {
    // Real search with debouncing
    const timer = setTimeout(() => {
      if (query.length > 1) {
        performSearch(query);
      } else {
        setResults([]);
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const performSearch = async (searchQuery: string) => {
    setLoading(true);
    try {
      const response = await searchAPI.smartSearch(searchQuery, user?.id ? String(user.id) : undefined);
      
      // Transform backend results to component format
      const transformedResults = response.results?.map((result: any) => ({
        id: result.id,
        title: result.title,
        description: result.description,
        category: result.category,
        path: result.path,
        icon: getCategoryIcon(result.category),
        priority: result.priority || 5,
        lastUsed: result.last_used ? new Date(result.last_used) : undefined,
        isBookmarked: result.is_bookmarked || false
      })) || [];

      setResults(transformedResults);

      // Transform suggestions
      const transformedSuggestions = response.suggestions?.map((suggestion: any) => ({
        id: suggestion.id,
        text: suggestion.text,
        category: suggestion.category,
        icon: getSuggestionIcon(suggestion.action_type),
        action: () => {
          if (suggestion.action_type === 'create') {
            // Handle create actions
            navigate('/create');
          } else if (suggestion.action_type === 'navigate') {
            navigate(suggestion.path || '/');
          } else {
            setQuery(suggestion.text);
          }
        }
      })) || [];

      setSuggestions(transformedSuggestions);

      // Track search analytics
      if (user?.id) {
        searchAPI.trackSearch(String(user.id), searchQuery, transformedResults.length);
      }
    } catch (error) {
      console.error('Search error:', error);
      // Fallback to basic search if API fails
      const filtered = searchData.filter(item => 
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.category.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setResults(filtered);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'haccp': return <Assignment color="primary" />;
      case 'suppliers': return <Business color="success" />;
      case 'prp': return <Assignment color="warning" />;
      case 'documents': return <Description color="info" />;
      case 'system': return <People color="secondary" />;
      default: return <Description color="action" />;
    }
  };

  const getSuggestionIcon = (actionType: string) => {
    switch (actionType) {
      case 'create': return <AutoAwesome color="primary" />;
      case 'navigate': return <TrendingUp color="success" />;
      case 'search': return <History color="action" />;
      default: return <Lightbulb color="warning" />;
    }
  };

  useEffect(() => {
    // Close search on outside click
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleResultClick = (result: SearchResult) => {
    // Add to recent searches
    setRecentSearches(prev => [query, ...prev.filter(s => s !== query)].slice(0, 5));
    
    // Track selection analytics
    if (user?.id) {
      searchAPI.trackSearch(String(user.id), query, results.length, result.id);
    }
    
    navigate(result.path);
    setIsOpen(false);
    setQuery('');
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    suggestion.action();
    setIsOpen(false);
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'HACCP': 'primary',
      'Suppliers': 'success',
      'PRP': 'warning',
      'Documents': 'info',
      'System': 'secondary',
      'Quick Actions': 'primary',
      'Recent Searches': 'default',
      'Trending': 'success',
    };
    return colors[category] || 'default';
  };

  const renderSkeletons = () => (
    <>
      {[1, 2, 3].map((item) => (
        <ListItem key={item}>
          <ListItemIcon>
            <Skeleton variant="circular" width={24} height={24} />
          </ListItemIcon>
          <ListItemText
            primary={<Skeleton width="60%" height={20} />}
            secondary={<Skeleton width="80%" height={16} />}
          />
        </ListItem>
      ))}
    </>
  );

  return (
    <Box ref={searchRef} sx={{ position: 'relative', width: fullWidth ? '100%' : 400 }}>
      <TextField
        fullWidth={fullWidth}
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => setIsOpen(true)}
        size="small"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search color="action" fontSize="small" />
            </InputAdornment>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 3,
            backgroundColor: 'background.paper',
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
            },
            '&.Mui-focused': {
              boxShadow: '0 8px 24px rgba(30, 64, 175, 0.2)',
            },
          },
        }}
      />

      {isOpen && (
        <Fade in timeout={200}>
          <Paper
            elevation={8}
            sx={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              mt: 1,
              borderRadius: 3,
              maxHeight: 400,
              overflow: 'auto',
              zIndex: 1300,
              border: '1px solid',
              borderColor: 'divider',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            }}
          >
            {query.length > 1 ? (
              // Search Results
              <>
                {loading ? (
                  <List>{renderSkeletons()}</List>
                ) : results.length > 0 ? (
                  <>
                    <Box sx={{ p: 2, pb: 1 }}>
                      <Typography variant="caption" color="text.secondary" fontWeight={600}>
                        SEARCH RESULTS ({results.length})
                      </Typography>
                    </Box>
                    <List sx={{ py: 0 }}>
                      {results.map((result) => (
                        <ListItem
                          key={result.id}
                          button
                          onClick={() => handleResultClick(result)}
                          sx={{
                            borderRadius: 2,
                            mx: 1,
                            mb: 0.5,
                            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                            '&:hover': {
                              backgroundColor: 'rgba(30, 64, 175, 0.06)',
                              transform: 'translateX(4px)',
                            },
                          }}
                        >
                          <ListItemIcon sx={{ minWidth: 40 }}>
                            {result.icon}
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Stack direction="row" alignItems="center" spacing={1}>
                                <Typography variant="body2" fontWeight={600}>
                                  {result.title}
                                </Typography>
                                {result.isBookmarked && (
                                  <Star fontSize="small" color="warning" />
                                )}
                                <Chip
                                  label={result.category}
                                  size="small"
                                  color={getCategoryColor(result.category) as any}
                                  variant="outlined"
                                  sx={{ height: 20, fontSize: '0.625rem' }}
                                />
                              </Stack>
                            }
                            secondary={
                              <Box>
                                <Typography variant="caption" color="text.secondary">
                                  {result.description}
                                </Typography>
                                {result.lastUsed && (
                                  <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mt: 0.5 }}>
                                    <AccessTime fontSize="inherit" color="action" />
                                    <Typography variant="caption" color="text.secondary">
                                      Last used {result.lastUsed.toLocaleTimeString()}
                                    </Typography>
                                  </Stack>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </>
                ) : (
                  <Box sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      No results found for "{query}"
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Try searching for HACCP, PRP, suppliers, or documents
                    </Typography>
                  </Box>
                )}
              </>
            ) : (
              // Suggestions and Quick Actions
              <>
                <Box sx={{ p: 2, pb: 1 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={600}>
                    QUICK ACTIONS & SUGGESTIONS
                  </Typography>
                </Box>
                <List sx={{ py: 0 }}>
                  {smartSuggestions.map((suggestion, index) => (
                    <React.Fragment key={suggestion.id}>
                      {index > 0 && suggestion.category !== smartSuggestions[index - 1].category && (
                        <Divider sx={{ my: 1 }} />
                      )}
                      <ListItem
                        button
                        onClick={() => handleSuggestionClick(suggestion)}
                        sx={{
                          borderRadius: 2,
                          mx: 1,
                          mb: 0.5,
                          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                          '&:hover': {
                            backgroundColor: 'rgba(30, 64, 175, 0.06)',
                            transform: 'translateX(4px)',
                          },
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 40 }}>
                          {suggestion.icon}
                        </ListItemIcon>
                        <ListItemText
                          primary={suggestion.text}
                          secondary={suggestion.category}
                        />
                      </ListItem>
                    </React.Fragment>
                  ))}
                </List>
              </>
            )}
          </Paper>
        </Fade>
      )}
    </Box>
  );
};

export default EnhancedQuickSearch;
