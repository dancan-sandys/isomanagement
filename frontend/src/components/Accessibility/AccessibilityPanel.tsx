import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Slider,
  Button,
  Grid,
  Chip,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  Accessibility as AccessibilityIcon,
  Contrast as HighContrastIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  VolumeUp as VolumeUpIcon,
  VolumeOff as VolumeOffIcon,
} from "@mui/icons-material";

interface AccessibilitySettings {
  highContrast: boolean;
  fontSize: number;
  soundEnabled: boolean;
  reducedMotion: boolean;
  focusIndicator: boolean;
}

const AccessibilityPanel: React.FC = () => {
  const [settings, setSettings] = useState<AccessibilitySettings>({
    highContrast: false,
    fontSize: 16,
    soundEnabled: true,
    reducedMotion: false,
    focusIndicator: true,
  });

  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Apply accessibility settings to the document
    document.documentElement.style.fontSize = `${settings.fontSize}px`;
    
    if (settings.highContrast) {
      document.body.classList.add("high-contrast");
    } else {
      document.body.classList.remove("high-contrast");
    }

    if (settings.reducedMotion) {
      document.body.classList.add("reduced-motion");
    } else {
      document.body.classList.remove("reduced-motion");
    }

    if (settings.focusIndicator) {
      document.body.classList.add("focus-indicator");
    } else {
      document.body.classList.remove("focus-indicator");
    }
  }, [settings]);

  const handleSettingChange = (key: keyof AccessibilitySettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const resetSettings = () => {
    setSettings({
      highContrast: false,
      fontSize: 16,
      soundEnabled: true,
      reducedMotion: false,
      focusIndicator: true,
    });
  };

  return (
    <>
      {/* Floating Accessibility Button */}
      <Box
        sx={{
          position: "fixed",
          bottom: 20,
          right: 20,
          zIndex: 1000,
        }}
      >
        <Tooltip title="Accessibility Settings">
          <IconButton
            onClick={() => setIsOpen(!isOpen)}
            sx={{
              backgroundColor: "primary.main",
              color: "white",
              width: 56,
              height: 56,
              "&:hover": {
                backgroundColor: "primary.dark",
              },
            }}
          >
            <AccessibilityIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Accessibility Panel */}
      {isOpen && (
        <Card
          sx={{
            position: "fixed",
            bottom: 90,
            right: 20,
            width: 320,
            zIndex: 999,
            boxShadow: 3,
          }}
        >
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <AccessibilityIcon sx={{ mr: 1, verticalAlign: "middle" }} />
              Accessibility Settings
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.highContrast}
                      onChange={(e) => handleSettingChange("highContrast", e.target.checked)}
                    />
                  }
                  label="High Contrast Mode"
                />
              </Grid>

              <Grid item xs={12}>
                <Typography gutterBottom>Font Size</Typography>
                <Slider
                  value={settings.fontSize}
                  onChange={(e, value) => handleSettingChange("fontSize", value)}
                  min={12}
                  max={24}
                  step={1}
                  marks
                  valueLabelDisplay="auto"
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.soundEnabled}
                      onChange={(e) => handleSettingChange("soundEnabled", e.target.checked)}
                    />
                  }
                  label="Sound Notifications"
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.reducedMotion}
                      onChange={(e) => handleSettingChange("reducedMotion", e.target.checked)}
                    />
                  }
                  label="Reduced Motion"
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.focusIndicator}
                      onChange={(e) => handleSettingChange("focusIndicator", e.target.checked)}
                    />
                  }
                  label="Focus Indicators"
                />
              </Grid>

              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  onClick={resetSettings}
                  fullWidth
                >
                  Reset to Default
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}
    </>
  );
};

export default AccessibilityPanel;
