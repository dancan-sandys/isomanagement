# NC/CAPA Quick Start Implementation Guide

## 🚀 Immediate Actions (Week 1)

### 1. Enhanced Non-Conformance Creation Form

**Current Issue**: Basic form with minimal fields
**Solution**: Create a comprehensive, guided NC creation workflow

#### **Backend Changes Needed:**

```python
# Add to ../backend/app/models/nonconformance.py

class ImmediateAction(Base):
    __tablename__ = "immediate_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    action_type = Column(String(50), nullable=False)  # containment, isolation, emergency_response
    description = Column(Text, nullable=False)
    implemented_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    implemented_at = Column(DateTime(timezone=True), nullable=False)
    effectiveness_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    verification_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    non_conformance = relationship("NonConformance")
    implemented_by_user = relationship("User", foreign_keys=[implemented_by])
    verified_by_user = relationship("User", foreign_keys=[verification_by])
```

#### **Frontend Changes Needed:**

```typescript
// Create src/components/NC/EnhancedNCCreation.tsx
import React, { useState } from 'react';
import { 
  Stepper, Step, StepLabel, StepContent,
  Box, Typography, TextField, Button, 
  FormControl, InputLabel, Select, MenuItem,
  Alert, Chip
} from '@mui/material';

interface NCCreationStep {
  title: string;
  description: string;
  component: React.ReactNode;
  validation: () => boolean;
}

const EnhancedNCCreation: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [ncData, setNcData] = useState({
    title: '',
    description: '',
    source: '',
    severity: 'medium',
    impact_area: '',
    location: '',
    batch_reference: '',
    product_reference: '',
    process_reference: '',
    immediate_actions: []
  });

  const steps: NCCreationStep[] = [
    {
      title: 'Basic Information',
      description: 'Enter the basic details of the non-conformance',
      component: <BasicInfoStep data={ncData} onChange={setNcData} />,
      validation: () => ncData.title && ncData.description && ncData.source
    },
    {
      title: 'Impact Assessment',
      description: 'Assess the impact and severity',
      component: <ImpactAssessmentStep data={ncData} onChange={setNcData} />,
      validation: () => ncData.severity && ncData.impact_area
    },
    {
      title: 'Immediate Actions',
      description: 'Define immediate containment actions',
      component: <ImmediateActionsStep data={ncData} onChange={setNcData} />,
      validation: () => true
    },
    {
      title: 'Review & Submit',
      description: 'Review all information and submit',
      component: <ReviewStep data={ncData} onSubmit={handleSubmit} />,
      validation: () => true
    }
  ];

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Create Non-Conformance
      </Typography>
      
      <Stepper activeStep={activeStep} orientation="vertical">
        {steps.map((step, index) => (
          <Step key={index}>
            <StepLabel>{step.title}</StepLabel>
            <StepContent>
              <Typography>{step.description}</Typography>
              <Box sx={{ mt: 2 }}>
                {step.component}
              </Box>
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  onClick={() => setActiveStep(index + 1)}
                  disabled={!step.validation()}
                  sx={{ mr: 1 }}
                >
                  {index === steps.length - 1 ? 'Submit' : 'Continue'}
                </Button>
                <Button
                  disabled={index === 0}
                  onClick={() => setActiveStep(index - 1)}
                >
                  Back
                </Button>
              </Box>
            </StepContent>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
};

export default EnhancedNCCreation;
```

### 2. Risk Assessment Integration

#### **Backend Changes:**

```python
# Add to ../backend/app/models/nonconformance.py

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    non_conformance_id = Column(Integer, ForeignKey("non_conformances.id"), nullable=False)
    food_safety_impact = Column(String(20), nullable=False)  # low, medium, high, critical
    regulatory_impact = Column(String(20), nullable=False)
    customer_impact = Column(String(20), nullable=False)
    business_impact = Column(String(20), nullable=False)
    overall_risk_score = Column(Float, nullable=False)
    risk_matrix_position = Column(String(10), nullable=False)  # e.g., "A1", "B3"
    requires_escalation = Column(Boolean, default=False)
    escalation_level = Column(String(20))  # supervisor, manager, director, executive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    non_conformance = relationship("NonConformance")
    created_by_user = relationship("User")
```

#### **Frontend Risk Matrix Component:**

```typescript
// Create src/components/NC/RiskMatrix.tsx
import React from 'react';
import { Box, Typography, Paper, Grid } from '@mui/material';

interface RiskMatrixProps {
  foodSafetyImpact: string;
  regulatoryImpact: string;
  customerImpact: string;
  businessImpact: string;
  onRiskChange: (risk: any) => void;
}

const RiskMatrix: React.FC<RiskMatrixProps> = ({
  foodSafetyImpact,
  regulatoryImpact,
  customerImpact,
  businessImpact,
  onRiskChange
}) => {
  const calculateRiskScore = () => {
    const impacts = [foodSafetyImpact, regulatoryImpact, customerImpact, businessImpact];
    const scores = impacts.map(impact => {
      switch(impact) {
        case 'low': return 1;
        case 'medium': return 2;
        case 'high': return 3;
        case 'critical': return 4;
        default: return 1;
      }
    });
    return scores.reduce((sum, score) => sum + score, 0) / scores.length;
  };

  const getRiskLevel = (score: number) => {
    if (score >= 3.5) return { level: 'Critical', color: '#d32f2f' };
    if (score >= 2.5) return { level: 'High', color: '#f57c00' };
    if (score >= 1.5) return { level: 'Medium', color: '#fbc02d' };
    return { level: 'Low', color: '#388e3c' };
  };

  const riskScore = calculateRiskScore();
  const riskLevel = getRiskLevel(riskScore);

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Risk Assessment Matrix
      </Typography>
      
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Impact Categories
            </Typography>
            {/* Impact selection controls */}
          </Box>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Box sx={{ 
            p: 2, 
            border: 2, 
            borderColor: riskLevel.color,
            borderRadius: 1,
            textAlign: 'center'
          }}>
            <Typography variant="h5" color={riskLevel.color}>
              Risk Level: {riskLevel.level}
            </Typography>
            <Typography variant="body2">
              Score: {riskScore.toFixed(1)}
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default RiskMatrix;
```

### 3. Enhanced Dashboard

#### **Create Executive Dashboard:**

```typescript
// Create src/components/NC/ExecutiveDashboard.tsx
import React, { useEffect, useState } from 'react';
import { 
  Box, Grid, Paper, Typography, Card, CardContent,
  LinearProgress, Chip, Alert
} from '@mui/material';
import { 
  TrendingUp, TrendingDown, Warning, CheckCircle,
  Error, Schedule, Assignment
} from '@mui/icons-material';

interface DashboardStats {
  total_ncs: number;
  open_ncs: number;
  critical_ncs: number;
  overdue_capas: number;
  completion_rate: number;
  avg_resolution_time: number;
  recent_trends: any[];
}

const ExecutiveDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch dashboard stats
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch('/api/nonconformance/dashboard/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LinearProgress />;
  if (!stats) return <Alert severity="error">Failed to load dashboard data</Alert>;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        NC/CAPA Executive Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total NCs
              </Typography>
              <Typography variant="h4">
                {stats.total_ncs}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card sx={{ borderColor: 'warning.main', border: 2 }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Open NCs
              </Typography>
              <Typography variant="h4" color="warning.main">
                {stats.open_ncs}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card sx={{ borderColor: 'error.main', border: 2 }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Critical NCs
              </Typography>
              <Typography variant="h4" color="error.main">
                {stats.critical_ncs}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card sx={{ borderColor: 'info.main', border: 2 }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Overdue CAPAs
              </Typography>
              <Typography variant="h4" color="info.main">
                {stats.overdue_capas}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Progress Indicators */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              CAPA Completion Rate
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Box sx={{ flex: 1, mr: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={stats.completion_rate} 
                  sx={{ height: 10, borderRadius: 5 }}
                />
              </Box>
              <Typography variant="body2">
                {stats.completion_rate}%
              </Typography>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Average Resolution Time
            </Typography>
            <Typography variant="h4" color="primary">
              {stats.avg_resolution_time} days
            </Typography>
          </Paper>
        </Grid>
        
        {/* Recent Trends */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Trends
            </Typography>
            <Grid container spacing={2}>
              {stats.recent_trends.map((trend, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Box sx={{ 
                    p: 2, 
                    border: 1, 
                    borderColor: 'divider',
                    borderRadius: 1
                  }}>
                    <Typography variant="subtitle2">
                      {trend.category}
                    </Typography>
                    <Typography variant="h6" color={trend.direction === 'up' ? 'error' : 'success'}>
                      {trend.direction === 'up' ? <TrendingUp /> : <TrendingDown />}
                      {trend.percentage}%
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ExecutiveDashboard;
```

## 🔧 Quick Wins (Week 2)

### 1. Enhanced NC List with Advanced Filtering

```typescript
// Update src/pages/NonConformance.tsx
import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, TextField, MenuItem, Button, 
  Table, TableHead, TableRow, TableCell, TableBody, 
  Pagination, Stack, Chip, IconButton, Tooltip,
  Accordion, AccordionSummary, AccordionDetails,
  FormControl, InputLabel, Select, Checkbox, FormControlLabel
} from '@mui/material';
import { 
  FilterList, Search, Clear, Save, 
  TrendingUp, TrendingDown, Warning, CheckCircle
} from '@mui/icons-material';

const EnhancedNonConformance: React.FC = () => {
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    source: '',
    severity: '',
    impact_area: '',
    date_from: '',
    date_to: '',
    assigned_to: '',
    requires_escalation: false,
    overdue: false
  });

  const [savedFilters, setSavedFilters] = useState([]);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  return (
    <Box p={3}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h5" fontWeight="bold">Non-Conformances</Typography>
        <Button variant="contained" onClick={() => setOpenCreate(true)}>
          Log New NC
        </Button>
      </Stack>

      {/* Enhanced Filter Panel */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Accordion expanded={showAdvancedFilters}>
          <AccordionSummary 
            expandIcon={<FilterList />}
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
          >
            <Typography variant="h6">Advanced Filters</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <TextField 
                  label="Search" 
                  size="small" 
                  value={filters.search} 
                  onChange={e => setFilters({...filters, search: e.target.value})}
                  InputProps={{
                    startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                  }}
                />
              </Grid>
              
              <Grid item xs={12} md={3}>
                <FormControl size="small" fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select 
                    value={filters.status} 
                    onChange={e => setFilters({...filters, status: e.target.value})}
                    label="Status"
                  >
                    <MenuItem value="">All</MenuItem>
                    {['open','under_investigation','root_cause_identified','capa_assigned','in_progress','completed','verified','closed'].map(s => (
                      <MenuItem key={s} value={s}>
                        {s.split('_').join(' ')}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={3}>
                <FormControl size="small" fullWidth>
                  <InputLabel>Severity</InputLabel>
                  <Select 
                    value={filters.severity} 
                    onChange={e => setFilters({...filters, severity: e.target.value})}
                    label="Severity"
                  >
                    <MenuItem value="">All</MenuItem>
                    {['low','medium','high','critical'].map(s => (
                      <MenuItem key={s} value={s}>
                        <Chip 
                          label={s} 
                          size="small" 
                          color={s === 'critical' ? 'error' : s === 'high' ? 'warning' : 'default'}
                        />
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={3}>
                <Stack direction="row" spacing={1}>
                  <Button 
                    variant="contained" 
                    onClick={onFilter}
                    startIcon={<FilterList />}
                  >
                    Apply
                  </Button>
                  <Button 
                    variant="outlined" 
                    onClick={() => setFilters({
                      search: '', status: '', source: '', severity: '', 
                      impact_area: '', date_from: '', date_to: '', 
                      assigned_to: '', requires_escalation: false, overdue: false
                    })}
                    startIcon={<Clear />}
                  >
                    Clear
                  </Button>
                </Stack>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      </Paper>

      {/* Enhanced Table */}
      <Paper>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>NC Number</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Risk Level</TableCell>
              <TableCell>Source</TableCell>
              <TableCell>Assigned To</TableCell>
              <TableCell>Reported</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(list.items || []).map((nc: any) => (
              <TableRow key={nc.id} hover sx={{ cursor: 'pointer' }}>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold">
                    {nc.nc_number}
                  </Typography>
                </TableCell>
                <TableCell>{nc.title}</TableCell>
                <TableCell>
                  <Chip 
                    label={String(nc.status).split('_').join(' ')} 
                    size="small"
                    color={nc.status === 'open' ? 'warning' : nc.status === 'completed' ? 'success' : 'default'}
                  />
                </TableCell>
                <TableCell>
                  <Chip 
                    label={nc.severity} 
                    size="small"
                    color={nc.severity === 'critical' ? 'error' : nc.severity === 'high' ? 'warning' : 'default'}
                  />
                </TableCell>
                <TableCell>
                  {nc.risk_assessment && (
                    <Chip 
                      label={nc.risk_assessment.risk_matrix_position} 
                      size="small"
                      color={nc.risk_assessment.requires_escalation ? 'error' : 'default'}
                    />
                  )}
                </TableCell>
                <TableCell sx={{ textTransform: 'uppercase' }}>{nc.source}</TableCell>
                <TableCell>{nc.assigned_to_name || 'Unassigned'}</TableCell>
                <TableCell>{nc.reported_date ? new Date(nc.reported_date).toLocaleDateString() : ''}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1}>
                    <Tooltip title="View Details">
                      <IconButton size="small" onClick={() => navigate(`/nonconformance/${nc.id}`)}>
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    {nc.requires_escalation && (
                      <Tooltip title="Requires Escalation">
                        <Warning color="error" />
                      </Tooltip>
                    )}
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
};
```

## 📋 Implementation Checklist

### **Week 1 - Foundation**
- [ ] Create database migration for immediate_actions table
- [ ] Create database migration for risk_assessments table
- [ ] Add API endpoints for immediate actions
- [ ] Add API endpoints for risk assessments
- [ ] Create EnhancedNCCreation component
- [ ] Create RiskMatrix component
- [ ] Update NonConformance page with enhanced filtering

### **Week 2 - Dashboard & UX**
- [ ] Create ExecutiveDashboard component
- [ ] Create OperationalDashboard component
- [ ] Add dashboard API endpoints
- [ ] Implement real-time statistics
- [ ] Add notification system foundation
- [ ] Create mobile-responsive layouts

### **Week 3 - Advanced Features**
- [ ] Implement escalation matrix
- [ ] Add bulk operations
- [ ] Create advanced reporting
- [ ] Add export functionality
- [ ] Implement audit trail enhancements

### **Week 4 - Testing & Polish**
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] User feedback integration
- [ ] Documentation updates
- [ ] Production deployment

## 🎯 Success Criteria

### **Immediate (Week 1)**
- [ ] Enhanced NC creation workflow implemented
- [ ] Risk assessment integration working
- [ ] Basic dashboard functional

### **Short Term (Week 2)**
- [ ] Advanced filtering operational
- [ ] Real-time statistics working
- [ ] Mobile responsiveness achieved

### **Medium Term (Week 4)**
- [ ] All features tested and working
- [ ] Performance optimized
- [ ] User adoption > 80%

This quick start implementation focuses on the most critical improvements that will provide immediate value while building the foundation for the comprehensive enhancement plan.
