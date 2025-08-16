# Traceability and Recall Management Implementation Plan

## Overview
This document provides a detailed implementation plan for enhancing the traceability and recall management module to achieve full ISO 22000:2018, ISO 22005:2007, and ISO 22002-1:2025 compliance.

## Phase 1: Core Compliance Foundation (Weeks 1-2)

### 1.1 Enhanced Database Models

#### 1.1.1 TraceabilityNode Model
```python
# Add to backend/app/models/traceability.py
class TraceabilityNode(Base):
    __tablename__ = "traceability_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    node_type = Column(String(50), nullable=False)  # supplier, production, distribution, customer
    node_level = Column(Integer, nullable=False)  # 1=immediate, 2=one-up, 3=two-up, etc.
    relationship_type = Column(String(50), nullable=False)  # ingredient, packaging, process, storage
    ccp_related = Column(Boolean, default=False)
    ccp_id = Column(Integer, ForeignKey("ccps.id"))
    verification_required = Column(Boolean, default=True)
    verification_status = Column(String(20), default="pending")
    verification_date = Column(DateTime(timezone=True))
    verified_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
```

#### 1.1.2 RecallClassification Model
```python
class RecallClassification(Base):
    __tablename__ = "recall_classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    recall_id = Column(Integer, ForeignKey("recalls.id"), nullable=False)
    health_risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    affected_population = Column(Text)  # vulnerable groups affected
    exposure_route = Column(String(50))  # ingestion, contact, inhalation
    severity_assessment = Column(Text)
    probability_assessment = Column(Text)
    risk_score = Column(Integer)  # Calculated risk score
    classification_date = Column(DateTime(timezone=True), nullable=False)
    classified_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### 1.1.3 RecallCommunication Model
```python
class RecallCommunication(Base):
    __tablename__ = "recall_communications"
    
    id = Column(Integer, primary_key=True, index=True)
    recall_id = Column(Integer, ForeignKey("recalls.id"), nullable=False)
    stakeholder_type = Column(String(50), nullable=False)  # customer, supplier, regulator, public
    communication_method = Column(String(50), nullable=False)  # email, phone, press, social
    message_template = Column(Text, nullable=False)
    sent_date = Column(DateTime(timezone=True))
    sent_by = Column(Integer, ForeignKey("users.id"))
    confirmation_received = Column(Boolean, default=False)
    response_time = Column(Integer)  # hours to respond
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 1.2 Database Migration
```python
# Create migration file: backend/alembic/versions/xxx_add_traceability_enhancements.py
"""Add traceability enhancements

Revision ID: xxx
Revises: previous_revision
Create Date: 2025-01-XX

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create traceability_nodes table
    op.create_table(
        'traceability_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('node_type', sa.String(50), nullable=False),
        sa.Column('node_level', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(50), nullable=False),
        sa.Column('ccp_related', sa.Boolean(), default=False),
        sa.Column('ccp_id', sa.Integer(), nullable=True),
        sa.Column('verification_required', sa.Boolean(), default=True),
        sa.Column('verification_status', sa.String(20), default='pending'),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id']),
        sa.ForeignKeyConstraint(['ccp_id'], ['ccps.id']),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create recall_classifications table
    op.create_table(
        'recall_classifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recall_id', sa.Integer(), nullable=False),
        sa.Column('health_risk_level', sa.String(20), nullable=False),
        sa.Column('affected_population', sa.Text(), nullable=True),
        sa.Column('exposure_route', sa.String(50), nullable=True),
        sa.Column('severity_assessment', sa.Text(), nullable=True),
        sa.Column('probability_assessment', sa.Text(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('classification_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('classified_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['recall_id'], ['recalls.id']),
        sa.ForeignKeyConstraint(['classified_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create recall_communications table
    op.create_table(
        'recall_communications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recall_id', sa.Integer(), nullable=False),
        sa.Column('stakeholder_type', sa.String(50), nullable=False),
        sa.Column('communication_method', sa.String(50), nullable=False),
        sa.Column('message_template', sa.Text(), nullable=False),
        sa.Column('sent_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_by', sa.Integer(), nullable=True),
        sa.Column('confirmation_received', sa.Boolean(), default=False),
        sa.Column('response_time', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['recall_id'], ['recalls.id']),
        sa.ForeignKeyConstraint(['sent_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('recall_communications')
    op.drop_table('recall_classifications')
    op.drop_table('traceability_nodes')
```

### 1.3 Enhanced Service Layer

#### 1.3.1 TraceabilityService Enhancements
```python
# Add to backend/app/services/traceability_service.py

def create_traceability_node(self, node_data: Dict[str, Any], created_by: int) -> TraceabilityNode:
    """Create a new traceability node"""
    node = TraceabilityNode(
        batch_id=node_data['batch_id'],
        node_type=node_data['node_type'],
        node_level=node_data['node_level'],
        relationship_type=node_data['relationship_type'],
        ccp_related=node_data.get('ccp_related', False),
        ccp_id=node_data.get('ccp_id'),
        verification_required=node_data.get('verification_required', True),
        created_by=created_by
    )
    
    self.db.add(node)
    self.db.commit()
    self.db.refresh(node)
    
    return node

def get_one_up_one_back_trace(self, batch_id: int, depth: int = 2) -> Dict[str, Any]:
    """Get one-up, one-back traceability for a batch"""
    # Get upstream trace (suppliers, ingredients)
    upstream_trace = self._get_upstream_trace(batch_id, depth)
    
    # Get downstream trace (customers, distribution)
    downstream_trace = self._get_downstream_trace(batch_id, depth)
    
    return {
        "batch_id": batch_id,
        "upstream_trace": upstream_trace,
        "downstream_trace": downstream_trace,
        "trace_completeness": self._calculate_trace_completeness(batch_id),
        "verification_status": self._get_verification_status(batch_id)
    }

def _get_upstream_trace(self, batch_id: int, depth: int) -> List[Dict[str, Any]]:
    """Get upstream traceability chain"""
    trace_chain = []
    current_batch_id = batch_id
    
    for level in range(1, depth + 1):
        # Get parent batches
        parent_batches = self.db.query(TraceabilityLink).filter(
            TraceabilityLink.linked_batch_id == current_batch_id,
            TraceabilityLink.relationship_type.in_(['ingredient', 'packaging', 'raw_material'])
        ).all()
        
        if not parent_batches:
            break
            
        level_data = {
            "level": level,
            "batches": []
        }
        
        for link in parent_batches:
            batch = self.db.query(Batch).filter(Batch.id == link.batch_id).first()
            if batch:
                level_data["batches"].append({
                    "batch_id": batch.id,
                    "batch_number": batch.batch_number,
                    "product_name": batch.product_name,
                    "supplier": self._get_supplier_info(batch.supplier_id),
                    "ccp_related": self._is_ccp_related(batch.id),
                    "verification_status": self._get_verification_status(batch.id)
                })
        
        trace_chain.append(level_data)
        current_batch_id = parent_batches[0].batch_id
    
    return trace_chain

def _get_downstream_trace(self, batch_id: int, depth: int) -> List[Dict[str, Any]]:
    """Get downstream traceability chain"""
    trace_chain = []
    current_batch_id = batch_id
    
    for level in range(1, depth + 1):
        # Get child batches
        child_batches = self.db.query(TraceabilityLink).filter(
            TraceabilityLink.batch_id == current_batch_id,
            TraceabilityLink.relationship_type.in_(['product', 'packaged_product', 'distributed_product'])
        ).all()
        
        if not child_batches:
            break
            
        level_data = {
            "level": level,
            "batches": []
        }
        
        for link in child_batches:
            batch = self.db.query(Batch).filter(Batch.id == link.linked_batch_id).first()
            if batch:
                level_data["batches"].append({
                    "batch_id": batch.id,
                    "batch_number": batch.batch_number,
                    "product_name": batch.product_name,
                    "customer": self._get_customer_info(batch.id),
                    "distribution_location": self._get_distribution_info(batch.id),
                    "verification_status": self._get_verification_status(batch.id)
                })
        
        trace_chain.append(level_data)
        current_batch_id = child_batches[0].linked_batch_id
    
    return trace_chain
```

#### 1.3.2 RecallService Enhancements
```python
# Add to backend/app/services/traceability_service.py

def classify_recall(self, recall_id: int, classification_data: Dict[str, Any], classified_by: int) -> RecallClassification:
    """Classify a recall based on health risk assessment"""
    
    # Calculate risk score
    risk_score = self._calculate_risk_score(classification_data)
    
    classification = RecallClassification(
        recall_id=recall_id,
        health_risk_level=classification_data['health_risk_level'],
        affected_population=classification_data.get('affected_population'),
        exposure_route=classification_data.get('exposure_route'),
        severity_assessment=classification_data.get('severity_assessment'),
        probability_assessment=classification_data.get('probability_assessment'),
        risk_score=risk_score,
        classification_date=datetime.utcnow(),
        classified_by=classified_by
    )
    
    self.db.add(classification)
    self.db.commit()
    self.db.refresh(classification)
    
    # Update recall status based on classification
    self._update_recall_status_based_on_classification(recall_id, classification)
    
    return classification

def _calculate_risk_score(self, classification_data: Dict[str, Any]) -> int:
    """Calculate risk score based on severity and probability"""
    severity_scores = {
        'low': 1,
        'medium': 2,
        'high': 3,
        'critical': 4
    }
    
    probability_scores = {
        'low': 1,
        'medium': 2,
        'high': 3,
        'very_high': 4
    }
    
    severity_score = severity_scores.get(classification_data['health_risk_level'], 1)
    probability_score = probability_scores.get(classification_data.get('probability_level', 'low'), 1)
    
    return severity_score * probability_score

def create_recall_communication(self, recall_id: int, communication_data: Dict[str, Any], sent_by: int) -> RecallCommunication:
    """Create a recall communication record"""
    
    communication = RecallCommunication(
        recall_id=recall_id,
        stakeholder_type=communication_data['stakeholder_type'],
        communication_method=communication_data['communication_method'],
        message_template=communication_data['message_template'],
        sent_date=datetime.utcnow(),
        sent_by=sent_by
    )
    
    self.db.add(communication)
    self.db.commit()
    self.db.refresh(communication)
    
    # Send actual communication
    self._send_communication(communication)
    
    return communication
```

### 1.4 API Endpoints

#### 1.4.1 Enhanced Traceability Endpoints
```python
# Add to backend/app/api/v1/endpoints/traceability.py

@router.get("/batches/{batch_id}/trace/one-up-one-back", response_model=ResponseModel)
async def get_one_up_one_back_trace(
    batch_id: int,
    depth: int = Query(2, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get one-up, one-back traceability for a batch"""
    try:
        service = TraceabilityService(db)
        trace_data = service.get_one_up_one_back_trace(batch_id, depth)
        
        return ResponseModel(
            success=True,
            message="Traceability data retrieved successfully",
            data=trace_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve traceability data: {str(e)}"
        )

@router.post("/traceability-nodes", response_model=ResponseModel)
async def create_traceability_node(
    node_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new traceability node"""
    try:
        service = TraceabilityService(db)
        node = service.create_traceability_node(node_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Traceability node created successfully",
            data={"id": node.id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create traceability node: {str(e)}"
        )
```

#### 1.4.2 Enhanced Recall Endpoints
```python
# Add to backend/app/api/v1/endpoints/traceability.py

@router.post("/recalls/{recall_id}/classify", response_model=ResponseModel)
async def classify_recall(
    recall_id: int,
    classification_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Classify a recall based on health risk assessment"""
    try:
        service = TraceabilityService(db)
        classification = service.classify_recall(recall_id, classification_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Recall classified successfully",
            data={"id": classification.id, "risk_score": classification.risk_score}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to classify recall: {str(e)}"
        )

@router.post("/recalls/{recall_id}/communications", response_model=ResponseModel)
async def create_recall_communication(
    recall_id: int,
    communication_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a recall communication"""
    try:
        service = TraceabilityService(db)
        communication = service.create_recall_communication(recall_id, communication_data, current_user.id)
        
        return ResponseModel(
            success=True,
            message="Recall communication created successfully",
            data={"id": communication.id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recall communication: {str(e)}"
        )
```

## Phase 2: User Experience Enhancements (Weeks 3-4)

### 2.1 Frontend Components

#### 2.1.1 One-Click Traceability Component
```typescript
// Create: frontend/src/components/Traceability/OneClickTraceability.tsx
import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Grid
} from '@mui/material';
import { Timeline as TimelineIcon } from '@mui/icons-material';
import { traceabilityAPI } from '../../services/traceabilityAPI';

interface OneClickTraceabilityProps {
  batchId: number;
  batchNumber: string;
}

const OneClickTraceability: React.FC<OneClickTraceabilityProps> = ({ batchId, batchNumber }) => {
  const [loading, setLoading] = useState(false);
  const [traceData, setTraceData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTrace = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await traceabilityAPI.getOneUpOneBackTrace(batchId, 2);
      setTraceData(data);
    } catch (err) {
      setError('Failed to retrieve traceability data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <TimelineIcon sx={{ mr: 1 }} />
          <Typography variant="h6">One-Click Traceability</Typography>
        </Box>
        
        <Button
          variant="contained"
          onClick={handleTrace}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <TimelineIcon />}
          fullWidth
        >
          {loading ? 'Tracing...' : `Trace Batch ${batchNumber}`}
        </Button>
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        
        {traceData && (
          <Box mt={3}>
            <Typography variant="h6" gutterBottom>
              Traceability Results
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" color="primary">
                  Upstream Trace (Suppliers)
                </Typography>
                {traceData.upstream_trace.map((level: any, index: number) => (
                  <Box key={index} mt={1}>
                    <Typography variant="body2" color="textSecondary">
                      Level {level.level}
                    </Typography>
                    {level.batches.map((batch: any, batchIndex: number) => (
                      <Box key={batchIndex} ml={2} mt={0.5}>
                        <Typography variant="body2">
                          {batch.batch_number} - {batch.product_name}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                ))}
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" color="primary">
                  Downstream Trace (Customers)
                </Typography>
                {traceData.downstream_trace.map((level: any, index: number) => (
                  <Box key={index} mt={1}>
                    <Typography variant="body2" color="textSecondary">
                      Level {level.level}
                    </Typography>
                    {level.batches.map((batch: any, batchIndex: number) => (
                      <Box key={batchIndex} ml={2} mt={0.5}>
                        <Typography variant="body2">
                          {batch.batch_number} - {batch.product_name}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                ))}
              </Grid>
            </Grid>
            
            <Box mt={2}>
              <Typography variant="body2" color="textSecondary">
                Trace Completeness: {traceData.trace_completeness}%
              </Typography>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default OneClickTraceability;
```

#### 2.1.2 Smart Recall Wizard Component
```typescript
// Create: frontend/src/components/Traceability/SmartRecallWizard.tsx
import React, { useState } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Card,
  CardContent,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Alert
} from '@mui/material';
import { traceabilityAPI } from '../../services/traceabilityAPI';

const steps = [
  'Issue Discovery',
  'Risk Assessment',
  'Affected Products',
  'Communication Plan',
  'Review & Submit'
];

const SmartRecallWizard: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    issue_discovered_date: '',
    health_risk_level: '',
    affected_population: '',
    exposure_route: '',
    affected_products: '',
    affected_batches: '',
    communication_method: '',
    regulatory_notification_required: false
  });

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmit = async () => {
    try {
      // Create recall
      const recallData = {
        recall_type: formData.health_risk_level === 'critical' ? 'class_i' : 'class_ii',
        title: formData.title,
        description: formData.description,
        reason: formData.description,
        issue_discovered_date: formData.issue_discovered_date,
        total_quantity_affected: 0, // Will be calculated
        assigned_to: 1 // Current user
      };
      
      const recall = await traceabilityAPI.createRecall(recallData);
      
      // Classify recall
      const classificationData = {
        health_risk_level: formData.health_risk_level,
        affected_population: formData.affected_population,
        exposure_route: formData.exposure_route
      };
      
      await traceabilityAPI.classifyRecall(recall.id, classificationData);
      
      // Create communication
      const communicationData = {
        stakeholder_type: 'customer',
        communication_method: formData.communication_method,
        message_template: `Recall notification for ${formData.title}`
      };
      
      await traceabilityAPI.createRecallCommunication(recall.id, communicationData);
      
      alert('Recall created successfully!');
    } catch (error) {
      console.error('Failed to create recall:', error);
      alert('Failed to create recall');
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Issue Discovery
            </Typography>
            <TextField
              fullWidth
              label="Issue Title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Issue Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              type="datetime-local"
              label="Issue Discovered Date"
              value={formData.issue_discovered_date}
              onChange={(e) => setFormData({ ...formData, issue_discovered_date: e.target.value })}
              margin="normal"
              InputLabelProps={{ shrink: true }}
            />
          </Box>
        );
      
      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Risk Assessment
            </Typography>
            <FormControl fullWidth margin="normal">
              <InputLabel>Health Risk Level</InputLabel>
              <Select
                value={formData.health_risk_level}
                onChange={(e) => setFormData({ ...formData, health_risk_level: e.target.value })}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Affected Population"
              value={formData.affected_population}
              onChange={(e) => setFormData({ ...formData, affected_population: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Exposure Route"
              value={formData.exposure_route}
              onChange={(e) => setFormData({ ...formData, exposure_route: e.target.value })}
              margin="normal"
            />
          </Box>
        );
      
      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Affected Products
            </Typography>
            <TextField
              fullWidth
              label="Affected Products"
              value={formData.affected_products}
              onChange={(e) => setFormData({ ...formData, affected_products: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Affected Batches"
              value={formData.affected_batches}
              onChange={(e) => setFormData({ ...formData, affected_batches: e.target.value })}
              margin="normal"
            />
          </Box>
        );
      
      case 3:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Communication Plan
            </Typography>
            <FormControl fullWidth margin="normal">
              <InputLabel>Communication Method</InputLabel>
              <Select
                value={formData.communication_method}
                onChange={(e) => setFormData({ ...formData, communication_method: e.target.value })}
              >
                <MenuItem value="email">Email</MenuItem>
                <MenuItem value="phone">Phone</MenuItem>
                <MenuItem value="press">Press Release</MenuItem>
                <MenuItem value="social">Social Media</MenuItem>
              </Select>
            </FormControl>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.regulatory_notification_required}
                  onChange={(e) => setFormData({ ...formData, regulatory_notification_required: e.target.checked })}
                />
              }
              label="Regulatory Notification Required"
            />
          </Box>
        );
      
      case 4:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Review & Submit
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              Please review all information before submitting the recall.
            </Alert>
            <Typography variant="body2" gutterBottom>
              <strong>Title:</strong> {formData.title}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Risk Level:</strong> {formData.health_risk_level}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Affected Products:</strong> {formData.affected_products}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Communication Method:</strong> {formData.communication_method}
            </Typography>
          </Box>
        );
      
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Smart Recall Wizard
        </Typography>
        
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {renderStepContent(activeStep)}
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>
          
          <Box>
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                onClick={handleSubmit}
              >
                Submit Recall
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default SmartRecallWizard;
```

## Phase 3: Mobile Optimization (Weeks 5-6)

### 3.1 QR Code Scanning Implementation
```typescript
// Create: frontend/src/components/Traceability/QRCodeScanner.tsx
import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import { QrCodeScanner as QrCodeScannerIcon } from '@mui/icons-material';
import { traceabilityAPI } from '../../services/traceabilityAPI';

const QRCodeScanner: React.FC = () => {
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const startScanning = async () => {
    try {
      setScanning(true);
      setError(null);
      
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      
      // Initialize QR code detection
      // This would require a QR code detection library like jsQR
      
    } catch (err) {
      setError('Failed to access camera');
      console.error(err);
    }
  };

  const stopScanning = () => {
    setScanning(false);
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
    }
  };

  const handleScanResult = async (result: string) => {
    try {
      stopScanning();
      
      // Parse QR code data (assuming it contains batch information)
      const batchData = JSON.parse(result);
      
      // Get traceability information
      const traceData = await traceabilityAPI.getOneUpOneBackTrace(batchData.batch_id, 2);
      setScanResult(traceData);
      
    } catch (err) {
      setError('Invalid QR code or failed to retrieve batch information');
      console.error(err);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          QR Code Scanner
        </Typography>
        
        {!scanning ? (
          <Button
            variant="contained"
            onClick={startScanning}
            startIcon={<QrCodeScannerIcon />}
            fullWidth
          >
            Start Scanning
          </Button>
        ) : (
          <Box>
            <video
              ref={videoRef}
              style={{ width: '100%', maxWidth: '400px' }}
            />
            <Button
              variant="outlined"
              onClick={stopScanning}
              fullWidth
              sx={{ mt: 2 }}
            >
              Stop Scanning
            </Button>
          </Box>
        )}
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        
        {scanResult && (
          <Box mt={3}>
            <Typography variant="h6" gutterBottom>
              Scan Results
            </Typography>
            <Typography variant="body2">
              Batch: {scanResult.batch_id}
            </Typography>
            <Typography variant="body2">
              Trace Completeness: {scanResult.trace_completeness}%
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default QRCodeScanner;
```

## Phase 4: Testing and Validation (Weeks 7-8)

### 4.1 Test Cases

#### 4.1.1 Traceability Tests
```python
# Create: backend/tests/test_traceability_enhancements.py
import pytest
from app.services.traceability_service import TraceabilityService
from app.models.traceability import Batch, TraceabilityNode, TraceabilityLink

class TestTraceabilityEnhancements:
    
    def test_one_up_one_back_traceability(self, db_session):
        """Test one-up, one-back traceability functionality"""
        service = TraceabilityService(db_session)
        
        # Create test batches
        batch1 = Batch(
            batch_number="TEST-001",
            batch_type="raw_milk",
            product_name="Raw Milk",
            quantity=1000,
            unit="L",
            production_date=datetime.utcnow(),
            created_by=1
        )
        db_session.add(batch1)
        db_session.commit()
        
        batch2 = Batch(
            batch_number="TEST-002",
            batch_type="final_product",
            product_name="Cheese",
            quantity=100,
            unit="kg",
            production_date=datetime.utcnow(),
            created_by=1
        )
        db_session.add(batch2)
        db_session.commit()
        
        # Create traceability link
        link = TraceabilityLink(
            batch_id=batch2.id,
            linked_batch_id=batch1.id,
            relationship_type="ingredient",
            usage_date=datetime.utcnow(),
            created_by=1
        )
        db_session.add(link)
        db_session.commit()
        
        # Test traceability
        trace_data = service.get_one_up_one_back_trace(batch2.id, 2)
        
        assert trace_data["batch_id"] == batch2.id
        assert len(trace_data["upstream_trace"]) > 0
        assert trace_data["trace_completeness"] > 0
    
    def test_recall_classification(self, db_session):
        """Test recall classification functionality"""
        service = TraceabilityService(db_session)
        
        # Create test recall
        recall = Recall(
            recall_number="TEST-RECALL-001",
            recall_type="class_ii",
            status="draft",
            title="Test Recall",
            description="Test recall description",
            reason="Test reason",
            issue_discovered_date=datetime.utcnow(),
            assigned_to=1,
            created_by=1
        )
        db_session.add(recall)
        db_session.commit()
        
        # Classify recall
        classification_data = {
            "health_risk_level": "medium",
            "affected_population": "General public",
            "exposure_route": "ingestion"
        }
        
        classification = service.classify_recall(recall.id, classification_data, 1)
        
        assert classification.recall_id == recall.id
        assert classification.health_risk_level == "medium"
        assert classification.risk_score > 0
```

#### 4.1.2 Frontend Tests
```typescript
// Create: frontend/src/components/Traceability/__tests__/OneClickTraceability.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import OneClickTraceability from '../OneClickTraceability';
import { traceabilityAPI } from '../../../services/traceabilityAPI';

// Mock the API
jest.mock('../../../services/traceabilityAPI');

describe('OneClickTraceability', () => {
  const mockTraceData = {
    batch_id: 1,
    upstream_trace: [
      {
        level: 1,
        batches: [
          {
            batch_id: 2,
            batch_number: "SUPPLIER-001",
            product_name: "Raw Milk",
            supplier: "Dairy Farm A",
            ccp_related: true,
            verification_status: "verified"
          }
        ]
      }
    ],
    downstream_trace: [],
    trace_completeness: 85,
    verification_status: "verified"
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders trace button', () => {
    render(<OneClickTraceability batchId={1} batchNumber="TEST-001" />);
    
    expect(screen.getByText('Trace Batch TEST-001')).toBeInTheDocument();
  });

  it('shows loading state when tracing', async () => {
    (traceabilityAPI.getOneUpOneBackTrace as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockTraceData), 100))
    );

    render(<OneClickTraceability batchId={1} batchNumber="TEST-001" />);
    
    fireEvent.click(screen.getByText('Trace Batch TEST-001'));
    
    expect(screen.getByText('Tracing...')).toBeInTheDocument();
  });

  it('displays traceability results after successful trace', async () => {
    (traceabilityAPI.getOneUpOneBackTrace as jest.Mock).mockResolvedValue(mockTraceData);

    render(<OneClickTraceability batchId={1} batchNumber="TEST-001" />);
    
    fireEvent.click(screen.getByText('Trace Batch TEST-001'));
    
    await waitFor(() => {
      expect(screen.getByText('Traceability Results')).toBeInTheDocument();
      expect(screen.getByText('Upstream Trace (Suppliers)')).toBeInTheDocument();
      expect(screen.getByText('SUPPLIER-001 - Raw Milk')).toBeInTheDocument();
      expect(screen.getByText('Trace Completeness: 85%')).toBeInTheDocument();
    });
  });

  it('shows error message when trace fails', async () => {
    (traceabilityAPI.getOneUpOneBackTrace as jest.Mock).mockRejectedValue(
      new Error('API Error')
    );

    render(<OneClickTraceability batchId={1} batchNumber="TEST-001" />);
    
    fireEvent.click(screen.getByText('Trace Batch TEST-001'));
    
    await waitFor(() => {
      expect(screen.getByText('Failed to retrieve traceability data')).toBeInTheDocument();
    });
  });
});
```

## Implementation Checklist

### Phase 1: Core Compliance (Weeks 1-2)
- [ ] **Database Models**
  - [ ] Add TraceabilityNode model
  - [ ] Add RecallClassification model
  - [ ] Add RecallCommunication model
  - [ ] Create database migration
  - [ ] Test migration on development database

- [ ] **Service Layer**
  - [ ] Implement one-up, one-back traceability
  - [ ] Add recall classification functionality
  - [ ] Add recall communication functionality
  - [ ] Integrate with HACCP CCPs
  - [ ] Add verification procedures

- [ ] **API Endpoints**
  - [ ] Add traceability node endpoints
  - [ ] Add recall classification endpoints
  - [ ] Add recall communication endpoints
  - [ ] Enhance existing traceability endpoints
  - [ ] Add verification endpoints

### Phase 2: User Experience (Weeks 3-4)
- [ ] **Frontend Components**
  - [ ] Create OneClickTraceability component
  - [ ] Create SmartRecallWizard component
  - [ ] Create visual traceability chain component
  - [ ] Add real-time notifications
  - [ ] Enhance dashboard with traceability metrics

- [ ] **User Interface**
  - [ ] Redesign traceability page layout
  - [ ] Add interactive traceability diagrams
  - [ ] Implement guided recall workflow
  - [ ] Add quick action buttons
  - [ ] Improve mobile responsiveness

### Phase 3: Mobile Optimization (Weeks 5-6)
- [ ] **Mobile Features**
  - [ ] Implement QR code scanning
  - [ ] Add offline traceability capabilities
  - [ ] Create mobile push notifications
  - [ ] Add voice command support
  - [ ] Optimize for touch interfaces

- [ ] **Progressive Web App**
  - [ ] Add service worker for offline functionality
  - [ ] Implement app manifest
  - [ ] Add install prompts
  - [ ] Enable background sync
  - [ ] Add offline data storage

### Phase 4: Testing and Deployment (Weeks 7-8)
- [ ] **Testing**
  - [ ] Write comprehensive unit tests
  - [ ] Create integration tests
  - [ ] Perform user acceptance testing
  - [ ] Conduct performance testing
  - [ ] Test mobile functionality

- [ ] **Deployment**
  - [ ] Deploy to staging environment
  - [ ] Conduct final testing
  - [ ] Deploy to production
  - [ ] Monitor system performance
  - [ ] Address post-deployment issues

## Success Criteria

### Technical Success Criteria
- [ ] 100% of batches traceable one-up, one-back
- [ ] < 2 second response time for traceability queries
- [ ] 99.9% system availability
- [ ] < 0.1% error rate in traceability data
- [ ] Mobile app works offline for core functions

### Business Success Criteria
- [ ] 100% ISO 22000/22005 compliance
- [ ] 95% user adoption of new features
- [ ] 90%+ recall effectiveness rate
- [ ] 100% recall team training completion
- [ ] < 2 hour recall response time

### User Experience Success Criteria
- [ ] One-click traceability works for all batches
- [ ] Smart recall wizard reduces recall creation time by 50%
- [ ] Mobile app receives 4+ star rating
- [ ] 90% of users find interface intuitive
- [ ] Zero critical usability issues

This implementation plan provides a comprehensive roadmap for transforming the current traceability and recall management system into a world-class, ISO-compliant, user-friendly solution that exceeds industry standards and user expectations.
