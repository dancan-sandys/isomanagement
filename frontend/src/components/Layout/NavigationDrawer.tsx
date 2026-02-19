import React, { useState } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Collapse,
  Typography,
  Chip,
  Avatar,
  Divider,
} from '@mui/material';
import {
  ExpandLess,
  ExpandMore,
  Person,
} from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { getNavigationForUser, NavigationSection, NAVIGATION_CONFIG } from '../../theme/navigationConfig';
import EnhancedQuickSearch from '../UI/EnhancedQuickSearch';

interface NavigationDrawerProps {
  onNavigate: (path: string) => void;
  isSelected: (path: string) => boolean;
}

const NavigationDrawer: React.FC<NavigationDrawerProps> = ({
  onNavigate,
  isSelected,
}) => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [expandedSections, setExpandedSections] = useState<string[]>(['dashboard']);

  const handleSectionToggle = (sectionKey: string) => {
    setExpandedSections(prev => 
      prev.includes(sectionKey) 
        ? prev.filter(key => key !== sectionKey)
        : [...prev, sectionKey]
    );
  };

  const navigationSections = getNavigationForUser(user);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
              <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}> {/* Reduced padding from 3 to 2 */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}> {/* Reduced gap and margin */}
          <Box sx={{ 
            width: 40, 
            height: 40, 
            borderRadius: 2, 
            backgroundColor: 'primary.main',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white'
          }}>
            <Typography variant="h6" fontWeight={700}>
              C
            </Typography>
          </Box>
          <Box>
            <Typography variant="h6" fontWeight={700} noWrap>
              Compli FSMS
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Food Safety Management System
            </Typography>
          </Box>
        </Box>
        
        {/* Enhanced Quick Search */}
        <EnhancedQuickSearch placeholder="Search…" fullWidth />
      </Box>

      {/* User Info */}
      {user && (
        <Box sx={{ p: 1.5, borderBottom: 1, borderColor: 'divider' }}> {/* Reduced padding from 2 to 1.5 */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}> {/* Reduced gap and margin */}
            <Avatar sx={{ width: 32, height: 32 }}>
              {user.profile_picture ? (
                <img src={user.profile_picture} alt={user.full_name} />
              ) : (
                <Person fontSize="small" />
              )}
            </Avatar>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="body2" fontWeight={600} noWrap>
                {user.full_name}
              </Typography>
              <Typography variant="caption" color="text.secondary" noWrap>
                {user.role_name || 'Unknown Role'}
              </Typography>
            </Box>
          </Box>
          <Chip 
            label={user.department || 'No Department'} 
            size="small" 
            color="primary" 
            variant="outlined"
          />
        </Box>
      )}

      {/* Navigation */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List sx={{ py: 1 }}>
          {navigationSections.map((section) => {
            const sectionKey = Object.keys(NAVIGATION_CONFIG).find(
              key => NAVIGATION_CONFIG[key].title === section.title
            ) || '';
            const isExpanded = expandedSections.includes(sectionKey);
            const hasSelectedItem = section.items.some(item => isSelected(item.path));
            const SectionIcon = section.icon;
            
            return (
              <Box key={sectionKey}>
                <ListItem disablePadding>
                  <ListItemButton
                    onClick={() => handleSectionToggle(sectionKey)}
                    sx={{
                      mx: 1,
                      mb: 0.5,
                      borderRadius: 2,
                      backgroundColor: hasSelectedItem ? 'action.selected' : 'transparent',
                      '&:hover': {
                        backgroundColor: 'rgba(30, 64, 175, 0.06)',
                      },
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <SectionIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary={section.title}
                      primaryTypographyProps={{
                        fontWeight: hasSelectedItem ? 600 : 400,
                      }}
                    />
                    {isExpanded ? <ExpandLess /> : <ExpandMore />}
                  </ListItemButton>
                </ListItem>
                
                <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                  <List component="div" disablePadding>
                    {section.items.map((item) => {
                      const selected = isSelected(item.path);
                      return (
                        <ListItem key={item.path} disablePadding>
                          <ListItemButton
                            onClick={() => !item.disabled && onNavigate(item.path)}
                            selected={selected}
                            disabled={item.disabled}
                            sx={{
                              pl: 4,
                              mx: 1,
                              mb: 0.5,
                              borderRadius: 2,
                              '&.Mui-selected': {
                                backgroundColor: 'primary.main',
                                color: 'primary.contrastText',
                                '&:hover': {
                                  backgroundColor: 'primary.dark',
                                },
                              },
                              '&.Mui-disabled': {
                                opacity: 0.6,
                              },
                              '&:hover': {
                                backgroundColor: 'rgba(30, 64, 175, 0.06)',
                                transform: 'translateX(4px)',
                                transition: 'all 0.2s cubic-bezier(0.4,0,0.2,1)'
                              },
                            }}
                          >
                            <ListItemText 
                              primary={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Typography
                                    variant="body2"
                                    fontWeight={selected ? 600 : 400}
                                  >
                                    {item.text}
                                  </Typography>
                                  {item.badge && (
                                    <Chip
                                      label={item.badge}
                                      size="small"
                                      color="error"
                                      sx={{ height: 20, fontSize: '0.625rem' }}
                                    />
                                  )}
                                </Box>
                              }
                            />
                          </ListItemButton>
                        </ListItem>
                      );
                    })}
                  </List>
                </Collapse>
              </Box>
            );
          })}
        </List>
      </Box>
    </Box>
  );
};

export default NavigationDrawer; 