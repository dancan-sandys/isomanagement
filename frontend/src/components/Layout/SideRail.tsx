import React, { useMemo, useState } from 'react';
import {
  Box,
  IconButton,
  Tooltip,
  Stack,
  Typography,
  Popover,
  List,
  ListItemButton,
  ListItemText,
  Divider,
  Chip,
  Toolbar,
} from '@mui/material';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { getNavigationForUser, NAVIGATION_CONFIG, NavigationSection } from '../../theme/navigationConfig';

interface SideRailProps {
  onNavigate: (path: string) => void;
  isSelected: (path: string) => boolean;
}

const RAIL_WIDTH = 72;

const SideRail: React.FC<SideRailProps> = ({ onNavigate, isSelected }) => {
  const { user } = useSelector((state: RootState) => state.auth);
  const sections = useMemo<NavigationSection[]>(() => getNavigationForUser(user), [user]);

  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [activeSectionKey, setActiveSectionKey] = useState<string | null>(null);

  const handleOpen = (event: React.MouseEvent<HTMLElement>, sectionKey: string) => {
    setAnchorEl(event.currentTarget);
    setActiveSectionKey(sectionKey);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setActiveSectionKey(null);
  };

  return (
    <Box
      sx={{
        width: RAIL_WIDTH,
        position: 'fixed',
        top: 0,
        bottom: 0,
        left: 0,
        borderRight: '1px solid',
        borderColor: 'divider',
        backgroundColor: (theme) => theme.palette.mode === 'light' ? 'background.paper' : 'background.default',
        display: { xs: 'none', md: 'flex' },
        flexDirection: 'column',
        alignItems: 'center',
        py: 1,
        zIndex: 1199,
      }}
    >
      {/* Spacer to align icons beneath the AppBar while letting the rail fill the top-left corner */}
      <Toolbar sx={{ minHeight: { xs: 56, sm: 64 } }} />
      {/* Top brand/quick slot could go here in future */}
      <Stack spacing={0.5} alignItems="center" sx={{ width: '100%', mt: 1 }}>
        {sections.map((section) => {
          const sectionKey = Object.keys(NAVIGATION_CONFIG).find(
            key => NAVIGATION_CONFIG[key].title === section.title
          ) || '';
          const SectionIcon = section.icon;

          const selected = section.items.some((item) => isSelected(item.path));

          return (
            <Tooltip key={sectionKey} title={section.title} placement="right" arrow disableInteractive>
              <IconButton
                color={selected ? 'primary' : 'default'}
                onClick={(e) => handleOpen(e, sectionKey)}
                sx={{
                  width: RAIL_WIDTH - 16,
                  height: 48,
                  borderRadius: 2,
                  my: 0.5,
                  alignSelf: 'center',
                  '&:hover': { backgroundColor: 'action.hover', transform: 'translateX(2px)' },
                  transition: 'all 0.15s ease',
                  boxShadow: selected ? 2 : 'none',
                }}
                aria-haspopup="true"
                aria-expanded={activeSectionKey === sectionKey ? 'true' : undefined}
                aria-controls={activeSectionKey === sectionKey ? `section-popover-${sectionKey}` : undefined}
              >
                <SectionIcon />
              </IconButton>
            </Tooltip>
          );
        })}
      </Stack>

      <Popover
        id={activeSectionKey ? `section-popover-${activeSectionKey}` : undefined}
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        PaperProps={{ sx: { borderRadius: 2, minWidth: 300, boxShadow: 6 } }}
      >
        {activeSectionKey && (
          <Box sx={{ p: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, px: 1 }}>
              {NAVIGATION_CONFIG[activeSectionKey].title}
            </Typography>
            <Divider sx={{ mb: 1 }} />
            <List dense sx={{ maxHeight: 360, overflowY: 'auto' }}>
              {NAVIGATION_CONFIG[activeSectionKey].items.map((item) => (
                <ListItemButton
                  key={item.path}
                  onClick={() => {
                    handleClose();
                    onNavigate(item.path);
                  }}
                  selected={isSelected(item.path)}
                  sx={{ borderRadius: 1, mx: 1, mb: 0.5, '&.Mui-selected': { backgroundColor: 'primary.main', color: 'primary.contrastText' } }}
                >
                  <ListItemText
                    primary={
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Typography variant="body2" fontWeight={600}>{item.text}</Typography>
                      </Stack>
                    }
                  />
                </ListItemButton>
              ))}
            </List>
          </Box>
        )}
      </Popover>
    </Box>
  );
};

export default SideRail;


