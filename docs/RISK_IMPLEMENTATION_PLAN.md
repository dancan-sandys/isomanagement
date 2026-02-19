# Risk Management Implementation Plan

## Phase 1: Database Schema Enhancements

### 1.1 Risk Management Framework Table

```python
# backend/app/models/risk_framework.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class RiskManagementFramework(Base):
    __tablename__ = "risk_management_framework"
    
    id = Column(Integer, primary_key=True)
    policy_statement = Column(Text, nullable=False)
    risk_appetite_statement = Column(Text, nullable=False)
    risk_tolerance_levels = Column(JSON, nullable=False)
    risk_criteria = Column(JSON, nullable=False)
    risk_assessment_methodology = Column(Text, nullable=False)
    risk_treatment_strategies = Column(JSON, nullable=False)
    monitoring_review_frequency = Column(Text, nullable=False)
    communication_plan = Column(Text, nullable=False)
    review_cycle = Column(String(50), nullable=False)
    next_review_date = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 1.2 Enhanced Risk Register Table

```python
# backend/app/models/risk.py (enhanced)
class RiskRegisterItem(Base):
    __tablename__ = "risk_register"
    
    # Existing fields...
    
    # ISO 31000:2018 compliant fields
    risk_context_id = Column(Integer, ForeignKey("risk_context.id"))
    risk_criteria_id = Column(Integer, ForeignKey("risk_criteria.id"))
    risk_assessment_method = Column(String(100), nullable=False)
    risk_assessment_date = Column(DateTime(timezone=True))
    risk_assessor_id = Column(Integer, ForeignKey("users.id"))
    risk_assessment_reviewed = Column(Boolean, default=False)
    risk_assessment_reviewer_id = Column(Integer, ForeignKey("users.id"))
    risk_assessment_review_date = Column(DateTime(timezone=True))
    
    # Risk treatment fields
    risk_treatment_strategy = Column(String(100))
    risk_treatment_plan = Column(Text)
    risk_treatment_cost = Column(Float)
    risk_treatment_benefit = Column(Text)
    risk_treatment_timeline = Column(Text)
    risk_treatment_approved = Column(Boolean, default=False)
    risk_treatment_approver_id = Column(Integer, ForeignKey("users.id"))
    risk_treatment_approval_date = Column(DateTime(timezone=True))
    
    # Residual risk fields
    residual_risk_score = Column(Integer)
    residual_risk_level = Column(Enum(RiskLevel))
    residual_risk_acceptable = Column(Boolean, default=False)
    residual_risk_justification = Column(Text)
    
    # Monitoring fields
    monitoring_frequency = Column(String(100))
    next_monitoring_date = Column(DateTime(timezone=True))
    monitoring_method = Column(Text)
    monitoring_responsible = Column(Integer, ForeignKey("users.id"))
    
    # Review fields
    review_frequency = Column(String(100))
    next_review_date = Column(DateTime(timezone=True))
    review_responsible = Column(Integer, ForeignKey("users.id"))
    last_review_date = Column(DateTime(timezone=True))
    review_outcome = Column(Text)
```

### 1.3 Database Migration

```python
# backend/alembic/versions/xxxx_enhance_risk_management.py
"""Enhance risk management for ISO 31000:2018 compliance

Revision ID: xxxx
Revises: previous_revision
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create risk_management_framework table
    op.create_table('risk_management_framework',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_statement', sa.Text(), nullable=False),
        sa.Column('risk_appetite_statement', sa.Text(), nullable=False),
        sa.Column('risk_tolerance_levels', sa.JSON(), nullable=False),
        sa.Column('risk_criteria', sa.JSON(), nullable=False),
        sa.Column('risk_assessment_methodology', sa.Text(), nullable=False),
        sa.Column('risk_treatment_strategies', sa.JSON(), nullable=False),
        sa.Column('monitoring_review_frequency', sa.Text(), nullable=False),
        sa.Column('communication_plan', sa.Text(), nullable=False),
        sa.Column('review_cycle', sa.String(length=50), nullable=False),
        sa.Column('next_review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add new columns to risk_register table
    op.add_column('risk_register', sa.Column('risk_context_id', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_criteria_id', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_assessment_method', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('risk_assessment_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('risk_register', sa.Column('risk_assessor_id', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_assessment_reviewed', sa.Boolean(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_assessment_reviewer_id', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_assessment_review_date', sa.DateTime(timezone=True), nullable=True))
    
    # Add risk treatment columns
    op.add_column('risk_register', sa.Column('risk_treatment_strategy', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_plan', sa.Text(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_cost', sa.Float(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_benefit', sa.Text(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_timeline', sa.Text(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_approved', sa.Boolean(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_approver_id', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_approval_date', sa.DateTime(timezone=True), nullable=True))
    
    # Add residual risk columns
    op.add_column('risk_register', sa.Column('residual_risk_score', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('residual_risk_level', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='risklevel'), nullable=True))
    op.add_column('risk_register', sa.Column('residual_risk_acceptable', sa.Boolean(), nullable=True))
    op.add_column('risk_register', sa.Column('residual_risk_justification', sa.Text(), nullable=True))
    
    # Add monitoring columns
    op.add_column('risk_register', sa.Column('monitoring_frequency', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('next_monitoring_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('risk_register', sa.Column('monitoring_method', sa.Text(), nullable=True))
    op.add_column('risk_register', sa.Column('monitoring_responsible', sa.Integer(), nullable=True))
    
    # Add review columns
    op.add_column('risk_register', sa.Column('review_frequency', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('next_review_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('risk_register', sa.Column('review_responsible', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('last_review_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('risk_register', sa.Column('review_outcome', sa.Text(), nullable=True))

def downgrade():
    op.drop_table('risk_management_framework')
    # Drop added columns from risk_register
    columns_to_drop = [
        'risk_context_id', 'risk_criteria_id', 'risk_assessment_method',
        'risk_assessment_date', 'risk_assessor_id', 'risk_assessment_reviewed',
        'risk_assessment_reviewer_id', 'risk_assessment_review_date',
        'risk_treatment_strategy', 'risk_treatment_plan', 'risk_treatment_cost',
        'risk_treatment_benefit', 'risk_treatment_timeline', 'risk_treatment_approved',
        'risk_treatment_approver_id', 'risk_treatment_approval_date',
        'residual_risk_score', 'residual_risk_level', 'residual_risk_acceptable',
        'residual_risk_justification', 'monitoring_frequency', 'next_monitoring_date',
        'monitoring_method', 'monitoring_responsible', 'review_frequency',
        'next_review_date', 'review_responsible', 'last_review_date', 'review_outcome'
    ]
    for column in columns_to_drop:
        op.drop_column('risk_register', column)
```

## Phase 2: Enhanced Service Layer

### 2.1 Risk Management Service

```python
# backend/app/services/risk_management_service.py
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import json

from app.models.risk import RiskRegisterItem, RiskAction
from app.models.risk_framework import RiskManagementFramework
from app.schemas.risk import RiskItemCreate, RiskItemUpdate, RiskFilter

class RiskManagementService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_framework(self) -> Optional[RiskManagementFramework]:
        """Get the current risk management framework"""
        return self.db.query(RiskManagementFramework).first()
    
    def create_framework(self, framework_data: Dict) -> RiskManagementFramework:
        """Create or update the risk management framework"""
        existing = self.get_framework()
        if existing:
            for key, value in framework_data.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            framework = existing
        else:
            framework = RiskManagementFramework(**framework_data)
            self.db.add(framework)
        
        self.db.commit()
        self.db.refresh(framework)
        return framework
    
    def assess_risk(self, risk_id: int, assessment_data: Dict) -> RiskRegisterItem:
        """Perform comprehensive risk assessment"""
        risk = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == risk_id).first()
        if not risk:
            raise ValueError("Risk not found")
        
        # Update assessment fields
        risk.risk_assessment_method = assessment_data.get('method', 'ISO_31000')
        risk.risk_assessment_date = datetime.utcnow()
        risk.risk_assessor_id = assessment_data.get('assessor_id')
        
        # Calculate risk score using ISO 31000 methodology
        severity = assessment_data.get('severity', 1)
        likelihood = assessment_data.get('likelihood', 1)
        detectability = assessment_data.get('detectability', 1)
        
        risk.risk_score = severity * likelihood * detectability
        
        # Determine risk level based on framework criteria
        framework = self.get_framework()
        if framework:
            tolerance_levels = framework.risk_tolerance_levels
            risk.risk_level = self._determine_risk_level(risk.risk_score, tolerance_levels)
        
        self.db.commit()
        self.db.refresh(risk)
        return risk
    
    def plan_risk_treatment(self, risk_id: int, treatment_data: Dict) -> RiskRegisterItem:
        """Plan risk treatment strategy"""
        risk = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == risk_id).first()
        if not risk:
            raise ValueError("Risk not found")
        
        # Update treatment fields
        risk.risk_treatment_strategy = treatment_data.get('strategy')
        risk.risk_treatment_plan = treatment_data.get('plan')
        risk.risk_treatment_cost = treatment_data.get('cost')
        risk.risk_treatment_benefit = treatment_data.get('benefit')
        risk.risk_treatment_timeline = treatment_data.get('timeline')
        
        # Calculate residual risk
        if treatment_data.get('residual_risk_score'):
            risk.residual_risk_score = treatment_data['residual_risk_score']
            risk.residual_risk_level = self._determine_risk_level(
                risk.residual_risk_score, 
                self.get_framework().risk_tolerance_levels if self.get_framework() else {}
            )
            risk.residual_risk_acceptable = risk.residual_risk_score <= 15  # Example threshold
        
        self.db.commit()
        self.db.refresh(risk)
        return risk
    
    def schedule_monitoring(self, risk_id: int, monitoring_data: Dict) -> RiskRegisterItem:
        """Schedule risk monitoring"""
        risk = self.db.query(RiskRegisterItem).filter(RiskRegisterItem.id == risk_id).first()
        if not risk:
            raise ValueError("Risk not found")
        
        risk.monitoring_frequency = monitoring_data.get('frequency')
        risk.monitoring_method = monitoring_data.get('method')
        risk.monitoring_responsible = monitoring_data.get('responsible_id')
        
        # Calculate next monitoring date
        frequency = monitoring_data.get('frequency', 'monthly')
        risk.next_monitoring_date = self._calculate_next_date(frequency)
        
        self.db.commit()
        self.db.refresh(risk)
        return risk
    
    def get_risk_dashboard_data(self) -> Dict:
        """Get comprehensive risk dashboard data"""
        total_risks = self.db.query(RiskRegisterItem).count()
        
        # Risk distribution by level
        risk_distribution = self.db.query(
            RiskRegisterItem.risk_level,
            func.count(RiskRegisterItem.id)
        ).group_by(RiskRegisterItem.risk_level).all()
        
        # Overdue reviews
        overdue_reviews = self.db.query(RiskRegisterItem).filter(
            RiskRegisterItem.next_review_date < datetime.utcnow()
        ).count()
        
        # Upcoming monitoring
        upcoming_monitoring = self.db.query(RiskRegisterItem).filter(
            and_(
                RiskRegisterItem.next_monitoring_date >= datetime.utcnow(),
                RiskRegisterItem.next_monitoring_date <= datetime.utcnow() + timedelta(days=7)
            )
        ).count()
        
        return {
            "total_risks": total_risks,
            "risk_distribution": dict(risk_distribution),
            "overdue_reviews": overdue_reviews,
            "upcoming_monitoring": upcoming_monitoring
        }
    
    def _determine_risk_level(self, score: int, tolerance_levels: Dict) -> str:
        """Determine risk level based on score and tolerance levels"""
        if score <= tolerance_levels.get('low_threshold', 15):
            return 'LOW'
        elif score <= tolerance_levels.get('medium_threshold', 50):
            return 'MEDIUM'
        elif score <= tolerance_levels.get('high_threshold', 100):
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def _calculate_next_date(self, frequency: str) -> datetime:
        """Calculate next date based on frequency"""
        now = datetime.utcnow()
        if frequency == 'daily':
            return now + timedelta(days=1)
        elif frequency == 'weekly':
            return now + timedelta(weeks=1)
        elif frequency == 'monthly':
            return now + timedelta(days=30)
        elif frequency == 'quarterly':
            return now + timedelta(days=90)
        else:
            return now + timedelta(days=30)  # Default to monthly
```

## Phase 3: Enhanced API Endpoints

### 3.1 Risk Management Framework Endpoints

```python
# backend/app/api/v1/endpoints/risk_framework.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.models.user import User
from app.schemas.common import ResponseModel
from app.services.risk_management_service import RiskManagementService

router = APIRouter()

@router.get("/framework", response_model=ResponseModel)
async def get_risk_framework(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current risk management framework"""
    service = RiskManagementService(db)
    framework = service.get_framework()
    return ResponseModel(
        success=True,
        message="Risk management framework retrieved",
        data=framework
    )

@router.post("/framework", response_model=ResponseModel)
async def create_risk_framework(
    framework_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update the risk management framework"""
    service = RiskManagementService(db)
    framework = service.create_framework(framework_data)
    return ResponseModel(
        success=True,
        message="Risk management framework updated",
        data=framework
    )

@router.post("/{risk_id}/assess", response_model=ResponseModel)
async def assess_risk(
    risk_id: int,
    assessment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Perform risk assessment"""
    service = RiskManagementService(db)
    risk = service.assess_risk(risk_id, assessment_data)
    return ResponseModel(
        success=True,
        message="Risk assessment completed",
        data=risk
    )

@router.post("/{risk_id}/treat", response_model=ResponseModel)
async def plan_risk_treatment(
    risk_id: int,
    treatment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Plan risk treatment"""
    service = RiskManagementService(db)
    risk = service.plan_risk_treatment(risk_id, treatment_data)
    return ResponseModel(
        success=True,
        message="Risk treatment planned",
        data=risk
    )

@router.get("/dashboard", response_model=ResponseModel)
async def get_risk_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get risk dashboard data"""
    service = RiskManagementService(db)
    dashboard_data = service.get_risk_dashboard_data()
    return ResponseModel(
        success=True,
        message="Risk dashboard data retrieved",
        data=dashboard_data
    )
```

## Phase 4: Frontend Enhancements

### 4.1 Risk Dashboard Component

```typescript
// frontend/src/components/Risk/RiskDashboard.tsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Alert,
} from '@mui/material';
import {
  Warning,
  CheckCircle,
  Schedule,
  TrendingUp,
  Assessment,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import { fetchRiskDashboard } from '../../store/slices/riskSlice';

interface RiskDashboardData {
  total_risks: number;
  risk_distribution: Record<string, number>;
  overdue_reviews: number;
  upcoming_monitoring: number;
}

const RiskDashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { dashboardData, loading, error } = useSelector((state: RootState) => state.risk);

  useEffect(() => {
    dispatch(fetchRiskDashboard());
  }, [dispatch]);

  if (loading) return <div>Loading...</div>;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Risk Management Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                Total Risks
              </Typography>
              <Typography variant="h3">
                {dashboardData?.total_risks || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="error">
                Overdue Reviews
              </Typography>
              <Typography variant="h3">
                {dashboardData?.overdue_reviews || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="warning.main">
                Upcoming Monitoring
              </Typography>
              <Typography variant="h3">
                {dashboardData?.upcoming_monitoring || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Distribution
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                {dashboardData?.risk_distribution && 
                  Object.entries(dashboardData.risk_distribution).map(([level, count]) => (
                    <Chip
                      key={level}
                      label={`${level}: ${count}`}
                      color={level === 'CRITICAL' ? 'error' : 
                             level === 'HIGH' ? 'warning' : 
                             level === 'MEDIUM' ? 'info' : 'success'}
                    />
                  ))
                }
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <List>
                <ListItem button>
                  <ListItemIcon>
                    <Assessment />
                  </ListItemIcon>
                  <ListItemText primary="Perform Risk Assessment" />
                </ListItem>
                <ListItem button>
                  <ListItemIcon>
                    <Schedule />
                  </ListItemIcon>
                  <ListItemText primary="Schedule Monitoring" />
                </ListItem>
                <ListItem button>
                  <ListItemIcon>
                    <TrendingUp />
                  </ListItemIcon>
                  <ListItemText primary="Review Risk Trends" />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RiskDashboard;
```

### 4.2 Risk Assessment Wizard

```typescript
// frontend/src/components/Risk/RiskAssessmentWizard.tsx
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stepper,
  Step,
  StepLabel,
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Grid,
} from '@mui/material';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store';
import { assessRisk } from '../../store/slices/riskSlice';

interface RiskAssessmentWizardProps {
  open: boolean;
  riskId: number;
  onClose: () => void;
  onComplete: () => void;
}

const RiskAssessmentWizard: React.FC<RiskAssessmentWizardProps> = ({
  open,
  riskId,
  onClose,
  onComplete,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [activeStep, setActiveStep] = useState(0);
  const [assessment, setAssessment] = useState({
    severity: 1,
    likelihood: 1,
    detectability: 1,
    method: 'ISO_31000',
    assessor_id: 1, // Get from current user
  });

  const steps = [
    'Risk Context',
    'Risk Analysis',
    'Risk Evaluation',
    'Risk Treatment',
    'Monitoring Plan',
  ];

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      // Complete assessment
      dispatch(assessRisk({ riskId, assessment }));
      onComplete();
      onClose();
    } else {
      setActiveStep(activeStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(activeStep - 1);
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Risk Context
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Risk Context Description"
                  placeholder="Describe the context in which this risk exists..."
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Risk Analysis
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Severity</InputLabel>
                  <Select
                    value={assessment.severity}
                    onChange={(e) => setAssessment({...assessment, severity: e.target.value})}
                  >
                    <MenuItem value={1}>1 - Negligible</MenuItem>
                    <MenuItem value={2}>2 - Minor</MenuItem>
                    <MenuItem value={3}>3 - Moderate</MenuItem>
                    <MenuItem value={4}>4 - Major</MenuItem>
                    <MenuItem value={5}>5 - Catastrophic</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Likelihood</InputLabel>
                  <Select
                    value={assessment.likelihood}
                    onChange={(e) => setAssessment({...assessment, likelihood: e.target.value})}
                  >
                    <MenuItem value={1}>1 - Rare</MenuItem>
                    <MenuItem value={2}>2 - Unlikely</MenuItem>
                    <MenuItem value={3}>3 - Possible</MenuItem>
                    <MenuItem value={4}>4 - Likely</MenuItem>
                    <MenuItem value={5}>5 - Almost Certain</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Detectability</InputLabel>
                  <Select
                    value={assessment.detectability}
                    onChange={(e) => setAssessment({...assessment, detectability: e.target.value})}
                  >
                    <MenuItem value={1}>1 - Easily Detectable</MenuItem>
                    <MenuItem value={2}>2 - Moderately Detectable</MenuItem>
                    <MenuItem value={3}>3 - Difficult</MenuItem>
                    <MenuItem value={4}>4 - Very Difficult</MenuItem>
                    <MenuItem value={5}>5 - Almost Undetectable</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        );

      default:
        return <Typography>Step content for step {step}</Typography>;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Risk Assessment Wizard</DialogTitle>
      <DialogContent>
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {renderStepContent(activeStep)}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleBack} disabled={activeStep === 0}>
          Back
        </Button>
        <Button onClick={handleNext} variant="contained">
          {activeStep === steps.length - 1 ? 'Complete' : 'Next'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RiskAssessmentWizard;
```

## Implementation Checklist

### Phase 1: Foundation (Week 1-2)
- [ ] Create database migration for enhanced risk tables
- [ ] Implement RiskManagementFramework model
- [ ] Enhance RiskRegisterItem model
- [ ] Create RiskManagementService
- [ ] Add framework management endpoints

### Phase 2: Core Features (Week 3-4)
- [ ] Implement risk assessment methodology
- [ ] Add risk treatment planning
- [ ] Create monitoring and review scheduling
- [ ] Build risk dashboard API
- [ ] Add risk analytics service

### Phase 3: Frontend (Week 5-6)
- [ ] Create RiskDashboard component
- [ ] Implement RiskAssessmentWizard
- [ ] Add risk management framework UI
- [ ] Build risk treatment planning interface
- [ ] Create monitoring schedule interface

### Phase 4: Integration (Week 7-8)
- [ ] Integrate with HACCP system
- [ ] Connect with PRP programs
- [ ] Link with audit findings
- [ ] Add notification system
- [ ] Implement reporting features

### Phase 5: Testing & Documentation (Week 9-10)
- [ ] Unit tests for all services
- [ ] Integration tests for API endpoints
- [ ] Frontend component testing
- [ ] User acceptance testing
- [ ] Documentation updates

## Expected Outcomes

1. **ISO 31000:2018 Compliance**: Full compliance with risk management standard
2. **ISO 22000:2018 Integration**: Seamless integration with food safety management
3. **Strategic Value**: Enterprise-wide risk management capabilities
4. **Operational Efficiency**: Streamlined risk assessment and treatment processes
5. **User Experience**: Intuitive and user-friendly risk management interface
6. **Continuous Improvement**: Built-in monitoring and review mechanisms
