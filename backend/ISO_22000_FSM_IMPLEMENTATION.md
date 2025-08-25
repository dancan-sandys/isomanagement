# ISO 22000:2018 Compliant Finite State Machine (FSM) Implementation

## Overview

This implementation provides an ISO 22000:2018 compliant finite state machine for production processes in the dairy processing industry. The system enables users to create processes, define stages, manage batches, and maintain comprehensive monitoring and traceability as required by food safety management standards.

## User Story Implementation

**User Story**: "The user creates the process then adds stages and batch of the product involved in the process when the user is ready they click on start process, the process then begins the first stage and the process is marked as in progress, the user can then come back to move the batch to the next stage until all stages are complete and the process is complete, at each stage, the user needs to log monitorings depending on the requirements of that stage."

### Implementation Details

#### 1. Process Creation with Stages
- **Endpoint**: `POST /api/v1/production/processes/fsm`
- **Purpose**: Create a new production process with predefined stages
- **Features**:
  - Creates process in `DRAFT` status
  - Defines multiple stages with sequence ordering
  - Associates with a specific batch
  - Supports ISO 22000:2018 compliance features

#### 2. Process Start
- **Endpoint**: `POST /api/v1/production/processes/{process_id}/start`
- **Purpose**: Start the process and activate the first stage
- **Features**:
  - Changes process status from `DRAFT` to `IN_PROGRESS`
  - Activates the first stage (sequence_order = 1)
  - Records start timestamp and operator
  - Creates initial transition record

#### 3. Stage Progression
- **Endpoint**: `POST /api/v1/production/processes/{process_id}/stages/{stage_id}/complete`
- **Purpose**: Complete current stage and move to next stage
- **Features**:
  - Validates completion requirements
  - Records stage completion details
  - Automatically advances to next stage
  - Marks process as complete when all stages finished

#### 4. Stage Monitoring
- **Endpoint**: `POST /api/v1/stages/{stage_id}/monitoring-logs`
- **Purpose**: Log monitoring data for the current stage
- **Features**:
  - Records measurements and observations
  - Validates against monitoring requirements
  - Tracks compliance with critical limits
  - Generates alerts for deviations

## Database Schema

### Core Tables

#### ProcessStage
```sql
CREATE TABLE process_stages (
    id INTEGER PRIMARY KEY,
    process_id INTEGER REFERENCES production_processes(id),
    stage_name VARCHAR(100) NOT NULL,
    stage_description TEXT,
    sequence_order INTEGER NOT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'skipped', 'failed'),
    is_critical_control_point BOOLEAN DEFAULT FALSE,
    is_operational_prp BOOLEAN DEFAULT FALSE,
    -- Timing fields
    planned_start_time TIMESTAMP,
    actual_start_time TIMESTAMP,
    planned_end_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    duration_minutes INTEGER,
    -- Personnel and responsibility
    assigned_operator_id INTEGER REFERENCES users(id),
    completed_by_id INTEGER REFERENCES users(id),
    approved_by_id INTEGER REFERENCES users(id),
    -- Documentation
    stage_notes TEXT,
    deviations_recorded TEXT,
    corrective_actions TEXT,
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

#### StageMonitoringRequirement
```sql
CREATE TABLE stage_monitoring_requirements (
    id INTEGER PRIMARY KEY,
    stage_id INTEGER REFERENCES process_stages(id),
    requirement_name VARCHAR(100) NOT NULL,
    requirement_type ENUM('temperature', 'time', 'ph', 'pressure', 'visual_inspection', 'weight', 'moisture', 'documentation', 'checklist', 'ccp_monitoring'),
    description TEXT,
    -- ISO 22000 Classification
    is_critical_limit BOOLEAN DEFAULT FALSE,
    is_operational_limit BOOLEAN DEFAULT FALSE,
    -- Monitoring parameters
    target_value FLOAT,
    tolerance_min FLOAT,
    tolerance_max FLOAT,
    unit_of_measure VARCHAR(20),
    monitoring_frequency VARCHAR(50),
    is_mandatory BOOLEAN DEFAULT TRUE,
    -- Equipment and method requirements
    equipment_required VARCHAR(100),
    measurement_method VARCHAR(100),
    calibration_required BOOLEAN DEFAULT FALSE,
    -- Compliance metadata
    regulatory_reference VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);
```

#### StageMonitoringLog
```sql
CREATE TABLE stage_monitoring_logs (
    id INTEGER PRIMARY KEY,
    stage_id INTEGER REFERENCES process_stages(id),
    requirement_id INTEGER REFERENCES stage_monitoring_requirements(id),
    -- Monitoring data
    monitoring_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    measured_value FLOAT,
    measured_text TEXT,
    is_within_limits BOOLEAN,
    -- Quality assessment
    pass_fail_status VARCHAR(20), -- 'pass', 'fail', 'warning', 'N/A'
    deviation_severity VARCHAR(20), -- 'minor', 'major', 'critical'
    -- Personnel and verification
    recorded_by INTEGER REFERENCES users(id) NOT NULL,
    verified_by INTEGER REFERENCES users(id),
    verification_timestamp TIMESTAMP,
    -- Equipment and method
    equipment_used VARCHAR(100),
    measurement_method VARCHAR(100),
    equipment_calibration_date TIMESTAMP,
    -- Documentation and notes
    notes TEXT,
    corrective_action_taken TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    -- Compliance tracking
    regulatory_requirement_met BOOLEAN DEFAULT TRUE,
    iso_clause_reference VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

## API Endpoints

### Process Management

#### Create Process with Stages
```http
POST /api/v1/production/processes/fsm
Content-Type: application/json
Authorization: Bearer {token}

{
  "batch_id": 123,
  "process_type": "yoghurt",
  "operator_id": 456,
  "notes": "Production run for organic yoghurt",
  "stages": [
    {
      "stage_name": "Milk Reception and Standardization",
      "stage_description": "Receive milk and adjust fat content",
      "sequence_order": 1,
      "is_critical_control_point": false,
      "is_operational_prp": true,
      "duration_minutes": 45,
      "completion_criteria": {
        "mandatory_monitoring_required": true,
        "fat_content_verification": true
      }
    },
    {
      "stage_name": "Pasteurization",
      "stage_description": "Heat treatment to eliminate pathogens - CRITICAL CONTROL POINT",
      "sequence_order": 2,
      "is_critical_control_point": true,
      "is_operational_prp": false,
      "duration_minutes": 60,
      "completion_criteria": {
        "mandatory_monitoring_required": true,
        "minimum_duration_minutes": 45,
        "temperature_time_verification": true
      }
    }
  ]
}
```

#### Start Process
```http
POST /api/v1/production/processes/123/start
Content-Type: application/json
Authorization: Bearer {token}

{
  "operator_id": 456,
  "start_notes": "Beginning production run 2024-001"
}
```

#### Complete Stage and Transition
```http
POST /api/v1/production/processes/123/stages/456/complete
Content-Type: application/json
Authorization: Bearer {token}

{
  "completion_notes": "Stage completed successfully",
  "deviations_recorded": "Minor temperature deviation at 10:15 AM",
  "corrective_actions": "Adjusted heat exchanger settings",
  "requires_approval": false
}
```

### Monitoring and Logging

#### Add Monitoring Requirement to Stage
```http
POST /api/v1/stages/456/monitoring-requirements
Content-Type: application/json
Authorization: Bearer {token}

{
  "requirement_name": "Pasteurization Temperature",
  "requirement_type": "temperature",
  "description": "Continuous temperature monitoring during pasteurization",
  "is_critical_limit": true,
  "target_value": 72.0,
  "tolerance_min": 71.5,
  "tolerance_max": 75.0,
  "unit_of_measure": "°C",
  "monitoring_frequency": "continuous",
  "is_mandatory": true,
  "equipment_required": "Calibrated thermometer",
  "measurement_method": "Electronic temperature probe",
  "calibration_required": true,
  "regulatory_reference": "ISO 22000:2018 Clause 8.5.4"
}
```

#### Log Monitoring Data
```http
POST /api/v1/stages/456/monitoring-logs
Content-Type: application/json
Authorization: Bearer {token}

{
  "requirement_id": 789,
  "measured_value": 72.3,
  "pass_fail_status": "pass",
  "equipment_used": "Thermometer TH-001",
  "measurement_method": "Electronic probe",
  "notes": "Temperature stable throughout process",
  "regulatory_requirement_met": true,
  "iso_clause_reference": "ISO 22000:2018 8.5.4"
}
```

### Template Management

#### Get ISO Template for Product Type
```http
GET /api/v1/production/templates/stages/yoghurt
Authorization: Bearer {token}
```

#### Create Process from ISO Template
```http
POST /api/v1/production/processes/fsm/from-template
Content-Type: application/json
Authorization: Bearer {token}

{
  "batch_id": 123,
  "process_type": "yoghurt",
  "operator_id": 456,
  "spec": {
    "target_fat_content": 3.25,
    "target_protein": 3.2
  }
}
```

## ISO 22000:2018 Compliance Features

### Critical Control Points (CCPs)
- **Definition**: Points where control is essential to prevent or eliminate food safety hazards
- **Implementation**: 
  - `is_critical_control_point = true` flag on stages
  - Mandatory monitoring requirements
  - Critical limit validation
  - Automatic alert generation for deviations

### Operational Prerequisite Programs (OPRPs)
- **Definition**: Prerequisite programs that control significant hazards
- **Implementation**:
  - `is_operational_prp = true` flag on stages
  - Operational limit monitoring
  - Documentation requirements

### Monitoring and Verification
- **Continuous Monitoring**: Real-time data collection for CCPs
- **Verification**: Independent checks of monitoring systems
- **Record Keeping**: Comprehensive documentation of all activities
- **Corrective Actions**: Systematic response to deviations

### Traceability
- **Forward Traceability**: Track products through all process stages
- **Backward Traceability**: Trace back to raw materials and suppliers
- **Batch Tracking**: Complete batch lifecycle management

## Predefined ISO Templates

### Fresh Milk Processing
1. Raw Milk Reception (OPRP)
2. Filtration and Clarification (OPRP)
3. HTST Pasteurization (CCP) - 72°C for 15 seconds
4. Rapid Cooling (OPRP) - Cool to ≤4°C
5. Packaging (OPRP)
6. Cold Storage (OPRP)

### Yoghurt Production
1. Milk Reception and Standardization (OPRP)
2. Homogenization (OPRP)
3. Pasteurization (CCP) - 85°C for 30 minutes
4. Cooling for Inoculation (OPRP)
5. Culture Inoculation (OPRP)
6. Fermentation (CCP) - pH monitoring
7. Cooling and Packaging (OPRP)
8. Cold Storage (OPRP)

### Cheese Manufacturing
1. Milk Reception and Testing (OPRP)
2. Pasteurization (CCP)
3. Cooling and Culture Addition (OPRP)
4. Acidification (CCP) - pH control
5. Renneting and Coagulation (OPRP)
6. Cutting and Draining (OPRP)
7. Pressing (OPRP)
8. Salting (OPRP)
9. Aging/Ripening (OPRP)

## Workflow Example

### 1. Create Process
```python
# User creates a yoghurt production process
response = requests.post('/api/v1/production/processes/fsm/from-template', {
    'batch_id': 123,
    'process_type': 'yoghurt',
    'operator_id': 456
})
process_id = response.json()['id']
# Status: DRAFT, stages created in PENDING status
```

### 2. Start Process
```python
# User starts the process when ready
response = requests.post(f'/api/v1/production/processes/{process_id}/start', {
    'operator_id': 456,
    'start_notes': 'Beginning production'
})
# Status: IN_PROGRESS, first stage activated
```

### 3. Monitor Current Stage
```python
# User logs monitoring data during pasteurization (CCP)
requests.post('/api/v1/stages/stage_id/monitoring-logs', {
    'requirement_id': temp_requirement_id,
    'measured_value': 85.2,
    'equipment_used': 'Thermometer TH-001',
    'pass_fail_status': 'pass'
})
# Monitoring data recorded, compliance verified
```

### 4. Complete Stage and Transition
```python
# User completes current stage and moves to next
response = requests.post(f'/api/v1/production/processes/{process_id}/stages/{stage_id}/complete', {
    'completion_notes': 'Pasteurization completed successfully',
    'deviations_recorded': 'None',
    'corrective_actions': 'None required'
})
# Current stage marked COMPLETED, next stage activated
```

### 5. Process Completion
```python
# When final stage is completed
# Process automatically marked as COMPLETED
# All stages in COMPLETED status
# End timestamp recorded
```

## Monitoring Requirements by Stage Type

### Pasteurization (CCP)
- **Temperature**: Continuous monitoring, 72°C ± 0.5°C
- **Time**: Minimum 15 seconds holding time
- **Equipment**: Calibrated thermometer and timer
- **Frequency**: Continuous during process
- **Alerts**: Critical alerts for temperature/time deviations

### Fermentation (CCP)
- **pH**: Every 30 minutes, target 4.5 ± 0.3
- **Temperature**: Hourly, 43°C ± 2°C
- **Equipment**: Calibrated pH meter and thermometer
- **Frequency**: Scheduled intervals
- **Alerts**: Critical alerts for pH deviations

### Cold Storage (OPRP)
- **Temperature**: Continuous, ≤4°C
- **Equipment**: Temperature loggers
- **Frequency**: Continuous monitoring
- **Alerts**: Warnings for temperature excursions

## Compliance and Validation

### ISO 22000:2018 Requirements Met
- ✅ Hazard analysis and CCP identification
- ✅ Monitoring procedures for CCPs
- ✅ Critical limits establishment
- ✅ Corrective action procedures
- ✅ Verification procedures
- ✅ Record keeping and documentation
- ✅ Traceability throughout process
- ✅ Management system requirements

### Validation Features
- **Template Validation**: Automatic ISO compliance checking
- **Stage Sequencing**: Enforced sequential processing
- **Monitoring Compliance**: Mandatory monitoring for CCPs
- **Documentation Requirements**: Complete audit trail
- **Deviation Management**: Systematic handling of non-conformances

## Benefits

### For Operations
- **Standardized Processes**: ISO-compliant templates reduce setup time
- **Guided Workflow**: Sequential stage progression prevents errors
- **Real-time Monitoring**: Immediate visibility into process status
- **Quality Assurance**: Automated compliance checking

### For Quality Management
- **Regulatory Compliance**: Built-in ISO 22000:2018 requirements
- **Audit Readiness**: Complete documentation and traceability
- **Risk Mitigation**: Systematic monitoring and control
- **Continuous Improvement**: Data-driven process optimization

### For Food Safety
- **CCP Management**: Rigorous control of critical points
- **Deviation Detection**: Immediate alerts for non-conformances
- **Corrective Actions**: Systematic response procedures
- **Verification**: Independent validation of control measures

This implementation provides a comprehensive, ISO 22000:2018 compliant finite state machine that fully addresses the user story requirements while ensuring food safety and regulatory compliance throughout the production process.