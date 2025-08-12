import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Button,
  Stack,
  Divider,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Fab,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Slider,
} from '@mui/material';
import {
  Accessibility,
  TextFields,
  Visibility,
  VolumeUp,
  Keyboard,
  Mouse,
  Speed,
  Contrast,
  Close,
  Settings,
  ZoomIn,
  ZoomOut,
  Pause,
  PlayArrow,
} from '@mui/icons-material';
import { useAccessibility } from '../../hooks/useAccessibility';

interface AccessibilityPanelProps {
  open?: boolean;
  onClose?: () => void;
}

const AccessibilityPanel: React.FC<AccessibilityPanelProps> = ({
  open = false,
  onClose,
}) => {
  const {
    preferences,
    isKeyboardUser,
    updateFontSize,
    toggleKeyboardNavigation,
    announceToScreenReader,
  } = useAccessibility();

  const [isFloatingOpen, setIsFloatingOpen] = useState(false);

  const handleFontSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const size = event.target.value as 'small' | 'medium' | 'large' | 'xl';
    updateFontSize(size);
    announceToScreenReader(`Font size changed to ${size}`);
  };

  const fontSizeLabels = {
    small: 'Small (14px)',
    medium: 'Medium (16px)',
    large: 'Large (18px)',
    xl: 'Extra Large (20px)',
  };

  const AccessibilityContent = () => (
    <Box sx={{ p: 3, maxWidth: 400 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Typography variant="h6" fontWeight={600} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Accessibility color="primary" />
          Accessibility Settings
        </Typography>
        {onClose && (
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        )}
      </Stack>

      <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
        <Typography variant="body2">
          These settings help make the application more accessible. Changes are saved automatically.
        </Typography>
      </Alert>

      <Stack spacing={3}>
        {/* Font Size */}
        <Card variant="outlined" sx={{ borderRadius: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <TextFields color="primary" />
              <Typography variant="subtitle1" fontWeight={600}>
                Text Size
              </Typography>
            </Stack>
            
            <FormControl component="fieldset">
              <RadioGroup
                value={preferences.fontSize}
                onChange={handleFontSizeChange}
                name="font-size"
              >
                {Object.entries(fontSizeLabels).map(([value, label]) => (
                  <FormControlLabel
                    key={value}
                    value={value}
                    control={<Radio />}
                    label={label}
                    sx={{
                      fontSize: value === 'small' ? '0.875rem' : 
                               value === 'medium' ? '1rem' :
                               value === 'large' ? '1.125rem' : '1.25rem',
                    }}
                  />
                ))}
              </RadioGroup>
            </FormControl>
          </CardContent>
        </Card>

        {/* Motion and Animation */}
        <Card variant="outlined" sx={{ borderRadius: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <Speed color="primary" />
              <Typography variant="subtitle1" fontWeight={600}>
                Motion & Animation
              </Typography>
            </Stack>
            
            <Stack spacing={2}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" fontWeight={500}>
                    Reduced Motion
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {preferences.reducedMotion ? 'Animations are disabled' : 'Animations are enabled'}
                  </Typography>
                </Box>
                <Switch
                  checked={preferences.reducedMotion}
                  disabled
                  icon={<Pause />}
                  checkedIcon={<PlayArrow />}
                />
              </Box>
              
              <Typography variant="caption" color="text.secondary">
                This setting is automatically detected from your system preferences.
              </Typography>
            </Stack>
          </CardContent>
        </Card>

        {/* Visual Preferences */}
        <Card variant="outlined" sx={{ borderRadius: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <Visibility color="primary" />
              <Typography variant="subtitle1" fontWeight={600}>
                Visual Preferences
              </Typography>
            </Stack>
            
            <Stack spacing={2}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" fontWeight={500}>
                    High Contrast
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {preferences.highContrast ? 'High contrast enabled' : 'Normal contrast'}
                  </Typography>
                </Box>
                <Switch
                  checked={preferences.highContrast}
                  disabled
                  icon={<Contrast />}
                  checkedIcon={<Contrast />}
                />
              </Box>
              
              <Typography variant="caption" color="text.secondary">
                This setting is automatically detected from your system preferences.
              </Typography>
            </Stack>
          </CardContent>
        </Card>

        {/* Keyboard Navigation */}
        <Card variant="outlined" sx={{ borderRadius: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <Keyboard color="primary" />
              <Typography variant="subtitle1" fontWeight={600}>
                Keyboard Navigation
              </Typography>
            </Stack>
            
            <Stack spacing={2}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" fontWeight={500}>
                    Enhanced Focus Indicators
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Show clear focus outlines for keyboard navigation
                  </Typography>
                </Box>
                <Switch
                  checked={preferences.keyboardNavigation}
                  onChange={toggleKeyboardNavigation}
                />
              </Box>
              
              {isKeyboardUser && (
                <Alert severity="success" sx={{ borderRadius: 2 }}>
                  <Typography variant="caption">
                    Keyboard user detected! Enhanced focus indicators are automatically enabled.
                  </Typography>
                </Alert>
              )}
            </Stack>
          </CardContent>
        </Card>

        {/* Keyboard Shortcuts */}
        <Card variant="outlined" sx={{ borderRadius: 3 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
              Keyboard Shortcuts
            </Typography>
            
            <Stack spacing={1}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Quick Search</Typography>
                <Chip label="Ctrl + K" size="small" variant="outlined" />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Dashboard</Typography>
                <Chip label="Ctrl + D" size="small" variant="outlined" />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Create New</Typography>
                <Chip label="Ctrl + N" size="small" variant="outlined" />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Accessibility Panel</Typography>
                <Chip label="Alt + A" size="small" variant="outlined" />
              </Box>
            </Stack>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            startIcon={<ZoomIn />}
            onClick={() => {
              const keys = Object.keys(fontSizeLabels) as Array<'small' | 'medium' | 'large' | 'xl'>;
              const currentIndex = keys.indexOf(preferences.fontSize as 'small' | 'medium' | 'large' | 'xl');
              const nextIndex = Math.min(currentIndex + 1, keys.length - 1);
              const nextSize = keys[nextIndex];
              updateFontSize(nextSize);
              announceToScreenReader(`Font size increased to ${fontSizeLabels[nextSize]}`);
            }}
            disabled={preferences.fontSize === 'xl'}
            fullWidth
          >
            Increase Text
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<ZoomOut />}
            onClick={() => {
              const keys = Object.keys(fontSizeLabels) as Array<'small' | 'medium' | 'large' | 'xl'>;
              const currentIndex = keys.indexOf(preferences.fontSize as 'small' | 'medium' | 'large' | 'xl');
              const prevIndex = Math.max(currentIndex - 1, 0);
              const prevSize = keys[prevIndex];
              updateFontSize(prevSize);
              announceToScreenReader(`Font size decreased to ${fontSizeLabels[prevSize]}`);
            }}
            disabled={preferences.fontSize === 'small'}
            fullWidth
          >
            Decrease Text
          </Button>
        </Stack>
      </Stack>
    </Box>
  );

  if (open !== undefined) {
    // Controlled mode (drawer)
    return (
      <Drawer
        anchor="right"
        open={open}
        onClose={onClose}
        PaperProps={{
          sx: {
            width: { xs: '100%', sm: 440 },
            borderTopLeftRadius: { xs: 0, sm: 16 },
            borderBottomLeftRadius: { xs: 0, sm: 16 },
          },
        }}
      >
        <AccessibilityContent />
      </Drawer>
    );
  }

  // Floating mode (FAB + Drawer)
  return (
    <>
      <Tooltip title="Accessibility Settings (Alt + A)">
        <Fab
          color="primary"
          onClick={() => setIsFloatingOpen(true)}
          sx={{
            position: 'fixed',
            bottom: 24,
            left: 24,
            zIndex: 1000,
            background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%)',
              transform: 'scale(1.1)',
            },
          }}
        >
          <Accessibility />
        </Fab>
      </Tooltip>

      <Drawer
        anchor="right"
        open={isFloatingOpen}
        onClose={() => setIsFloatingOpen(false)}
        PaperProps={{
          sx: {
            width: { xs: '100%', sm: 440 },
            borderTopLeftRadius: { xs: 0, sm: 16 },
            borderBottomLeftRadius: { xs: 0, sm: 16 },
          },
        }}
      >
        <AccessibilityContent />
      </Drawer>
    </>
  );
};

export default AccessibilityPanel;
