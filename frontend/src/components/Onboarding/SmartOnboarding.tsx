import React, { useState, useEffect } from 'react';
import {
  Box,
  Dialog,
  DialogContent,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Typography,
  Card,
  CardContent,
  Avatar,
  Stack,
  Chip,
  IconButton,
  Fade,
  Grow,
  Paper,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  AutoAwesome,
  School,
  Security,
  Navigation,
  Dashboard,
  Assignment,
  People,
  Settings,
  CheckCircle,
  PlayArrow,
  Star,
  Lightbulb,
  Speed,
  Close,
  ArrowForward,
  ArrowBack,
  Rocket,
  EmojiObjects,
  Timeline,
  TrendingUp,
} from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  content: React.ReactNode;
  icon: React.ReactNode;
  estimatedTime: string;
  mandatory?: boolean;
  roleSpecific?: string[];
}

interface InteractiveTour {
  id: string;
  title: string;
  description: string;
  selector: string;
  position: 'top' | 'bottom' | 'left' | 'right';
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface SmartOnboardingProps {
  open: boolean;
  onClose: () => void;
  onComplete: () => void;
  isFirstTime?: boolean;
}

const SmartOnboarding: React.FC<SmartOnboardingProps> = ({
  open,
  onClose,
  onComplete,
  isFirstTime = false,
}) => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [activeStep, setActiveStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [userPreferences, setUserPreferences] = useState({
    skipBasics: false,
    focusAreas: [] as string[],
    experienceLevel: 'beginner' as 'beginner' | 'intermediate' | 'advanced',
  });

  const getOnboardingSteps = (): OnboardingStep[] => {
    const baseSteps: OnboardingStep[] = [
      {
        id: 'welcome',
        title: 'Welcome to ISO 22000 FSMS',
        description: 'Let\'s get you started with your food safety management journey',
        estimatedTime: '2 min',
        icon: <Rocket />,
        content: (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <Avatar sx={{ 
              width: 80, 
              height: 80, 
              bgcolor: 'primary.main', 
              mx: 'auto', 
              mb: 3,
              background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
            }}>
              <AutoAwesome fontSize="large" />
            </Avatar>
            <Typography variant="h4" fontWeight={700} sx={{ mb: 2 }}>
              Welcome, {user?.full_name?.split(' ')[0]}! 🎉
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 400, mx: 'auto' }}>
              Your role as <strong>{user?.role_name}</strong> gives you access to powerful tools for managing food safety compliance.
            </Typography>
            
            <Stack direction="row" spacing={2} justifyContent="center" sx={{ mb: 3 }}>
              <Chip 
                icon={<Security />} 
                label="ISO 22000 Compliant" 
                color="success" 
                variant="outlined" 
              />
              <Chip 
                icon={<Speed />} 
                label="Real-time Monitoring" 
                color="primary" 
                variant="outlined" 
              />
              <Chip 
                icon={<EmojiObjects />} 
                label="AI-Powered Insights" 
                color="warning" 
                variant="outlined" 
              />
            </Stack>

            <Alert severity="info" sx={{ borderRadius: 3, textAlign: 'left' }}>
              <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                What makes this special?
              </Typography>
              <List dense>
                <ListItem sx={{ py: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <CheckCircle color="success" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Smart automation reduces manual work by 60%" 
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
                <ListItem sx={{ py: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <CheckCircle color="success" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Real-time compliance monitoring and alerts" 
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
                <ListItem sx={{ py: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <CheckCircle color="success" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="AI-powered insights and recommendations" 
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              </List>
            </Alert>
          </Box>
        ),
      },
      {
        id: 'dashboard',
        title: 'Your Smart Dashboard',
        description: 'Discover your personalized control center',
        estimatedTime: '3 min',
        icon: <Dashboard />,
        content: (
          <Box sx={{ py: 2 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              Your dashboard is tailored to your role
            </Typography>
            
            <Stack spacing={3}>
              <Card sx={{ border: '1px solid', borderColor: 'primary.main', borderRadius: 3 }}>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                      <TrendingUp />
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={600}>
                        Smart Metrics
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Real-time KPIs and compliance scores
                      </Typography>
                    </Box>
                  </Stack>
                  <Typography variant="body2">
                    Your dashboard shows the metrics that matter most to your role. As a {user?.role_name}, 
                    you'll see compliance rates, task completion, and relevant alerts.
                  </Typography>
                </CardContent>
              </Card>

              <Card sx={{ border: '1px solid', borderColor: 'success.main', borderRadius: 3 }}>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                    <Avatar sx={{ bgcolor: 'success.main' }}>
                      <Assignment />
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={600}>
                        Priority Tasks
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        AI-prioritized workflow management
                      </Typography>
                    </Box>
                  </Stack>
                  <Typography variant="body2">
                    Tasks are automatically prioritized based on deadlines, compliance requirements, 
                    and business impact. Never miss a critical deadline again.
                  </Typography>
                </CardContent>
              </Card>

              <Card sx={{ border: '1px solid', borderColor: 'warning.main', borderRadius: 3 }}>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                    <Avatar sx={{ bgcolor: 'warning.main' }}>
                      <Lightbulb />
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={600}>
                        Smart Insights
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        AI-powered recommendations and alerts
                      </Typography>
                    </Box>
                  </Stack>
                  <Typography variant="body2">
                    Get proactive suggestions for improving compliance, reducing risks, 
                    and optimizing your food safety processes.
                  </Typography>
                </CardContent>
              </Card>
            </Stack>
          </Box>
        ),
      },
      {
        id: 'navigation',
        title: 'Smart Navigation',
        description: 'Navigate efficiently with intelligent search and shortcuts',
        estimatedTime: '2 min',
        icon: <Navigation />,
        content: (
          <Box sx={{ py: 2 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 3 }}>
              Navigate like a pro
            </Typography>
            
            <Stack spacing={3}>
              <Alert severity="info" sx={{ borderRadius: 3 }}>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                  🔍 Enhanced Search
                </Typography>
                <Typography variant="body2">
                  Type anything in the search bar - documents, products, suppliers, even "create HACCP plan" 
                  for quick actions. The search learns from your usage patterns.
                </Typography>
              </Alert>

              <Alert severity="success" sx={{ borderRadius: 3 }}>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                  ⚡ Quick Actions
                </Typography>
                <Typography variant="body2">
                  Access frequently used functions directly from search suggestions. 
                  No need to navigate through multiple menus.
                </Typography>
              </Alert>

              <Alert severity="warning" sx={{ borderRadius: 3 }}>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                  🔖 Smart Bookmarks
                </Typography>
                <Typography variant="body2">
                  The system automatically bookmarks pages you visit frequently and 
                  suggests them when relevant.
                </Typography>
              </Alert>

              <Paper sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 3 }}>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                  Pro Tip: Keyboard Shortcuts
                </Typography>
                <Stack spacing={1}>
                  <Typography variant="body2">• <strong>Ctrl + K</strong> - Quick search</Typography>
                  <Typography variant="body2">• <strong>Ctrl + D</strong> - Dashboard</Typography>
                  <Typography variant="body2">• <strong>Ctrl + N</strong> - Create new item</Typography>
                </Stack>
              </Paper>
            </Stack>
          </Box>
        ),
      },
    ];

    // Add role-specific steps
    const roleSpecificSteps: Record<string, OnboardingStep[]> = {
      'QA Manager': [
        {
          id: 'qa-specifics',
          title: 'QA Manager Tools',
          description: 'Your specialized compliance management features',
          estimatedTime: '4 min',
          icon: <Security />,
          roleSpecific: ['QA Manager'],
          content: (
            <Box sx={{ py: 2 }}>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 3 }}>
                QA Manager Superpowers
              </Typography>
              
              <Stack spacing={2}>
                <Card sx={{ borderLeft: '4px solid', borderColor: 'primary.main' }}>
                  <CardContent>
                    <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
                      📊 Compliance Dashboard
                    </Typography>
                    <Typography variant="body2">
                      Monitor real-time compliance scores, track CAPA effectiveness, 
                      and identify trends before they become issues.
                    </Typography>
                  </CardContent>
                </Card>

                <Card sx={{ borderLeft: '4px solid', borderColor: 'success.main' }}>
                  <CardContent>
                    <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
                      🔄 Automated Workflows
                    </Typography>
                    <Typography variant="body2">
                      Approval workflows, document version control, and audit scheduling 
                      happen automatically based on your predefined rules.
                    </Typography>
                  </CardContent>
                </Card>

                <Card sx={{ borderLeft: '4px solid', borderColor: 'warning.main' }}>
                  <CardContent>
                    <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
                      🤖 AI Risk Assessment
                    </Typography>
                    <Typography variant="body2">
                      Get AI-powered risk predictions, supplier performance insights, 
                      and proactive recommendations for preventive actions.
                    </Typography>
                  </CardContent>
                </Card>
              </Stack>
            </Box>
          ),
        },
      ],
      'Production Operator': [
        {
          id: 'operator-specifics',
          title: 'Operator Efficiency Tools',
          description: 'Streamlined daily operations and mobile-friendly interfaces',
          estimatedTime: '3 min',
          icon: <Speed />,
          roleSpecific: ['Production Operator'],
          content: (
            <Box sx={{ py: 2 }}>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 3 }}>
                Built for the Production Floor
              </Typography>
              
              <Stack spacing={2}>
                <Card sx={{ borderLeft: '4px solid', borderColor: 'primary.main' }}>
                  <CardContent>
                    <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
                      📱 Mobile-First Design
                    </Typography>
                    <Typography variant="body2">
                      All forms and checklists work perfectly on tablets and phones. 
                      Take photos, scan QR codes, and submit data directly from the floor.
                    </Typography>
                  </CardContent>
                </Card>

                <Card sx={{ borderLeft: '4px solid', borderColor: 'success.main' }}>
                  <CardContent>
                    <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
                      ⚡ Quick Entry Forms
                    </Typography>
                    <Typography variant="body2">
                      Smart forms with auto-completion, voice input, and offline capability. 
                      Spend less time on paperwork, more time on production.
                    </Typography>
                  </CardContent>
                </Card>

                <Card sx={{ borderLeft: '4px solid', borderColor: 'warning.main' }}>
                  <CardContent>
                    <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
                      🔔 Real-time Alerts
                    </Typography>
                    <Typography variant="body2">
                      Get instant notifications for CCP deviations, maintenance requirements, 
                      and quality checks. Never miss a critical measurement.
                    </Typography>
                  </CardContent>
                </Card>
              </Stack>
            </Box>
          ),
        },
      ],
    };

    const userRoleSteps = roleSpecificSteps[user?.role_name || ''] || [];
    return [...baseSteps, ...userRoleSteps];
  };

  const onboardingSteps = getOnboardingSteps();

  const handleNext = () => {
    if (activeStep < onboardingSteps.length - 1) {
      setCompletedSteps(prev => [...prev, activeStep]);
      setActiveStep(prev => prev + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep(prev => prev - 1);
    }
  };

  const handleComplete = () => {
    setCompletedSteps(prev => [...prev, activeStep]);
    onComplete();
  };

  const handleSkip = () => {
    onComplete();
  };

  const progress = ((activeStep + 1) / onboardingSteps.length) * 100;

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 4,
          minHeight: '70vh',
        }
      }}
    >
      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ position: 'relative', height: '100%' }}>
          {/* Header */}
          <Box sx={{ 
            p: 3, 
            background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
          }}>
            <IconButton 
              onClick={onClose}
              sx={{ 
                position: 'absolute', 
                top: 16, 
                right: 16, 
                color: 'white',
                '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' }
              }}
            >
              <Close />
            </IconButton>
            
            <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
              <Avatar sx={{ 
                bgcolor: 'rgba(255,255,255,0.2)', 
                width: 48, 
                height: 48,
                backdropFilter: 'blur(10px)',
              }}>
                {onboardingSteps[activeStep]?.icon}
              </Avatar>
              <Box>
                <Typography variant="h5" fontWeight={700}>
                  {onboardingSteps[activeStep]?.title}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  {onboardingSteps[activeStep]?.description}
                </Typography>
              </Box>
            </Stack>

            <Box sx={{ mb: 2 }}>
              <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1 }}>
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  Step {activeStep + 1} of {onboardingSteps.length}
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  {Math.round(progress)}% complete
                </Typography>
              </Stack>
              <LinearProgress 
                variant="determinate" 
                value={progress}
                sx={{ 
                  height: 6, 
                  borderRadius: 3,
                  bgcolor: 'rgba(255,255,255,0.2)',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 3,
                    bgcolor: 'white',
                  },
                }}
              />
            </Box>

            <Chip 
              label={`⏱️ ${onboardingSteps[activeStep]?.estimatedTime}`}
              size="small"
              sx={{ 
                bgcolor: 'rgba(255,255,255,0.2)', 
                color: 'white',
                '& .MuiChip-label': { fontWeight: 500 }
              }}
            />
          </Box>

          {/* Content */}
          <Box sx={{ p: 4, minHeight: 400 }}>
            <Fade in key={activeStep} timeout={300}>
              <Box>
                {onboardingSteps[activeStep]?.content}
              </Box>
            </Fade>
          </Box>

          {/* Footer */}
          <Box sx={{ 
            p: 3, 
            borderTop: '1px solid', 
            borderColor: 'divider',
            bgcolor: 'grey.50',
          }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Button
                onClick={handleSkip}
                color="inherit"
                disabled={activeStep === onboardingSteps.length - 1}
              >
                Skip Onboarding
              </Button>

              <Stack direction="row" spacing={1}>
                <Button
                  onClick={handleBack}
                  disabled={activeStep === 0}
                  startIcon={<ArrowBack />}
                  variant="outlined"
                >
                  Back
                </Button>
                <Button
                  onClick={handleNext}
                  variant="contained"
                  endIcon={activeStep === onboardingSteps.length - 1 ? <Star /> : <ArrowForward />}
                  sx={{
                    background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%)',
                    },
                  }}
                >
                  {activeStep === onboardingSteps.length - 1 ? 'Get Started!' : 'Next'}
                </Button>
              </Stack>
            </Stack>
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default SmartOnboarding;
