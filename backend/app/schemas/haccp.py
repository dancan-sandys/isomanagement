from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


class HazardType(str, Enum):
    BIOLOGICAL = "biological"
    CHEMICAL = "chemical"
    PHYSICAL = "physical"
    ALLERGEN = "allergen"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CCPStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class DecisionTreeQuestion(str, Enum):
    Q1 = "Is control at this step necessary for safety?"
    Q2 = "Is it likely that contamination with identified hazard(s) may occur or increase to unacceptable level(s)?"
    Q3 = "Will a subsequent step eliminate or reduce the likely occurrence of a hazard to an acceptable level?"
    Q4 = "Is this step specifically designed to eliminate or reduce the likely occurrence of the hazard to an acceptable level?"


# Enhanced Critical Limits Schemas (Multi-parameter support)
class CriticalLimitParameter(BaseModel):
    parameter: str = Field(..., description="Parameter name (e.g., temperature, time, pH)")
    limit_type: Literal["numeric", "qualitative"] = Field("numeric", description="Type of limit")
    
    # Numeric limits
    min_value: Optional[float] = Field(None, description="Minimum value for numeric limits")
    max_value: Optional[float] = Field(None, description="Maximum value for numeric limits")
    unit: Optional[str] = Field(None, description="UCUM unit code (e.g., Cel, min, pH)")
    
    # Qualitative limits
    value: Optional[str] = Field(None, description="Expected value for qualitative limits")
    
    # Common fields
    condition: Optional[str] = Field(None, description="Condition when this limit applies")
    description: Optional[str] = Field(None, description="Description of the limit")
    
    @field_validator('limit_type')
    @classmethod
    def validate_limit_type(cls, v, values):
        if v == "numeric":
            if values.get('value') is not None:
                raise ValueError("Numeric limits should not have 'value' field")
            if values.get('min_value') is None and values.get('max_value') is None:
                raise ValueError("Numeric limits must have at least min_value or max_value")
        elif v == "qualitative":
            if values.get('min_value') is not None or values.get('max_value') is not None:
                raise ValueError("Qualitative limits should not have min_value or max_value")
            if values.get('value') is None:
                raise ValueError("Qualitative limits must have a 'value' field")
        return v
    
    @field_validator('unit')
    @classmethod
    def validate_ucum_unit(cls, v, values):
        """Validate UCUM unit for the parameter type"""
        if v is None:
            return v
        
        parameter = values.get('parameter', '').lower()
        if parameter in ['temperature', 'temp']:
            if not validate_ucum_unit('temperature', v):
                raise ValueError(f"Invalid temperature unit: {v}. Valid units: {UCUM_UNITS['temperature']}")
        elif parameter in ['time', 'duration']:
            if not validate_ucum_unit('time', v):
                raise ValueError(f"Invalid time unit: {v}. Valid units: {UCUM_UNITS['time']}")
        elif parameter in ['pressure', 'press']:
            if not validate_ucum_unit('pressure', v):
                raise ValueError(f"Invalid pressure unit: {v}. Valid units: {UCUM_UNITS['pressure']}")
        elif parameter in ['ph', 'ph_value']:
            if not validate_ucum_unit('ph', v):
                raise ValueError(f"Invalid pH unit: {v}. Valid units: {UCUM_UNITS['ph']}")
        elif parameter in ['aw', 'water_activity']:
            if not validate_ucum_unit('aw', v):
                raise ValueError(f"Invalid water activity unit: {v}. Valid units: {UCUM_UNITS['aw']}")
        elif parameter in ['concentration', 'conc']:
            if not validate_ucum_unit('concentration', v):
                raise ValueError(f"Invalid concentration unit: {v}. Valid units: {UCUM_UNITS['concentration']}")
        elif parameter in ['weight', 'mass']:
            if not validate_ucum_unit('weight', v):
                raise ValueError(f"Invalid weight unit: {v}. Valid units: {UCUM_UNITS['weight']}")
        elif parameter in ['volume', 'vol']:
            if not validate_ucum_unit('volume', v):
                raise ValueError(f"Invalid volume unit: {v}. Valid units: {UCUM_UNITS['volume']}")
        elif parameter in ['length', 'distance']:
            if not validate_ucum_unit('length', v):
                raise ValueError(f"Invalid length unit: {v}. Valid units: {UCUM_UNITS['length']}")
        elif parameter in ['area']:
            if not validate_ucum_unit('area', v):
                raise ValueError(f"Invalid area unit: {v}. Valid units: {UCUM_UNITS['area']}")
        elif parameter in ['flow', 'flow_rate']:
            if not validate_ucum_unit('flow', v):
                raise ValueError(f"Invalid flow unit: {v}. Valid units: {UCUM_UNITS['flow']}")
        elif parameter in ['speed', 'velocity']:
            if not validate_ucum_unit('speed', v):
                raise ValueError(f"Invalid speed unit: {v}. Valid units: {UCUM_UNITS['speed']}")
        elif parameter in ['energy']:
            if not validate_ucum_unit('energy', v):
                raise ValueError(f"Invalid energy unit: {v}. Valid units: {UCUM_UNITS['energy']}")
        elif parameter in ['power']:
            if not validate_ucum_unit('power', v):
                raise ValueError(f"Invalid power unit: {v}. Valid units: {UCUM_UNITS['power']}")
        
        return v

class ValidationEvidence(BaseModel):
    type: Literal["sop_reference", "scientific_study", "process_authority_letter", "validation_study", "regulatory_requirement"] = Field(..., description="Type of validation evidence")
    
    # SOP Reference
    document_id: Optional[int] = Field(None, description="ID of the referenced document")
    section: Optional[str] = Field(None, description="Section of the document")
    
    # Scientific Study
    reference: Optional[str] = Field(None, description="Study reference (journal, year, etc.)")
    study_id: Optional[str] = Field(None, description="Study identifier")
    
    # Process Authority Letter
    authority: Optional[str] = Field(None, description="Name of the process authority")
    date: Optional[str] = Field(None, description="Date of the letter")
    
    # Common fields
    description: str = Field(..., description="Description of the evidence")
    url: Optional[str] = Field(None, description="URL to the evidence document")

# UCUM Units for common food safety parameters
UCUM_UNITS = {
    "temperature": ["Cel", "K", "F"],  # Celsius, Kelvin, Fahrenheit
    "time": ["min", "h", "s"],  # minutes, hours, seconds
    "pressure": ["Pa", "kPa", "bar"],  # Pascal, kilopascal, bar
    "ph": ["pH"],  # pH units
    "aw": ["1"],  # Water activity (dimensionless)
    "concentration": ["g/L", "mg/L", "ppm", "ppb"],  # Concentration units
    "weight": ["g", "kg", "mg"],  # Weight units
    "volume": ["L", "mL", "m3"],  # Volume units
    "length": ["m", "cm", "mm"],  # Length units
    "area": ["m2", "cm2"],  # Area units
    "flow": ["L/min", "m3/h"],  # Flow rate units
    "speed": ["rpm", "m/s"],  # Speed units
    "energy": ["J", "kJ", "cal"],  # Energy units
    "power": ["W", "kW"],  # Power units
}

# Unit conversion factors (to base units)
UNIT_CONVERSIONS = {
    # Temperature conversions (to Celsius)
    "K": lambda x: x - 273.15,  # Kelvin to Celsius
    "F": lambda x: (x - 32) * 5/9,  # Fahrenheit to Celsius
    "Cel": lambda x: x,  # Celsius to Celsius (base unit)
    
    # Time conversions (to minutes)
    "s": lambda x: x / 60,  # seconds to minutes
    "min": lambda x: x,  # minutes to minutes (base unit)
    "h": lambda x: x * 60,  # hours to minutes
    
    # Pressure conversions (to Pa)
    "Pa": lambda x: x,  # Pascal to Pascal (base unit)
    "kPa": lambda x: x * 1000,  # kilopascal to Pascal
    "bar": lambda x: x * 100000,  # bar to Pascal
    
    # Weight conversions (to grams)
    "mg": lambda x: x / 1000,  # milligrams to grams
    "g": lambda x: x,  # grams to grams (base unit)
    "kg": lambda x: x * 1000,  # kilograms to grams
    
    # Volume conversions (to liters)
    "mL": lambda x: x / 1000,  # milliliters to liters
    "L": lambda x: x,  # liters to liters (base unit)
    "m3": lambda x: x * 1000,  # cubic meters to liters
}

def validate_ucum_unit(parameter_type: str, unit: str) -> bool:
    """Validate if a unit is valid for a given parameter type"""
    if parameter_type not in UCUM_UNITS:
        return False
    return unit in UCUM_UNITS[parameter_type]

def convert_to_base_unit(value: float, unit: str) -> tuple[float, str]:
    """Convert a value to its base unit"""
    if unit in UNIT_CONVERSIONS:
        converted_value = UNIT_CONVERSIONS[unit](value)
        # Return base unit name
        base_units = {
            "Cel": "Cel", "K": "Cel", "F": "Cel",
            "min": "min", "h": "min", "s": "min",
            "Pa": "Pa", "kPa": "Pa", "bar": "Pa",
            "g": "g", "kg": "g", "mg": "g",
            "L": "L", "mL": "L", "m3": "L"
        }
        return converted_value, base_units.get(unit, unit)
    return value, unit

def get_parameter_type_from_unit(unit: str) -> Optional[str]:
    """Get parameter type from unit"""
    for param_type, units in UCUM_UNITS.items():
        if unit in units:
            return param_type
    return None

# Unit conversion factors (to base units)
UNIT_CONVERSIONS = {
    # Temperature conversions (to Celsius)
    "K": lambda x: x - 273.15,  # Kelvin to Celsius
    "F": lambda x: (x - 32) * 5/9,  # Fahrenheit to Celsius
    "Cel": lambda x: x,  # Celsius to Celsius (base unit)
    
    # Time conversions (to minutes)
    "s": lambda x: x / 60,  # seconds to minutes
    "min": lambda x: x,  # minutes to minutes (base unit)
    "h": lambda x: x * 60,  # hours to minutes
    
    # Pressure conversions (to Pa)
    "Pa": lambda x: x,  # Pascal to Pascal (base unit)
    "kPa": lambda x: x * 1000,  # kilopascal to Pascal
    "bar": lambda x: x * 100000,  # bar to Pascal
    
    # Weight conversions (to grams)
    "mg": lambda x: x / 1000,  # milligrams to grams
    "g": lambda x: x,  # grams to grams (base unit)
    "kg": lambda x: x * 1000,  # kilograms to grams
    
    # Volume conversions (to liters)
    "mL": lambda x: x / 1000,  # milliliters to liters
    "L": lambda x: x,  # liters to liters (base unit)
    "m3": lambda x: x * 1000,  # cubic meters to liters
}

def validate_ucum_unit(parameter_type: str, unit: str) -> bool:
    """Validate if a unit is valid for a given parameter type"""
    if parameter_type not in UCUM_UNITS:
        return False
    return unit in UCUM_UNITS[parameter_type]

def convert_to_base_unit(value: float, unit: str) -> tuple[float, str]:
    """Convert a value to its base unit"""
    if unit in UNIT_CONVERSIONS:
        converted_value = UNIT_CONVERSIONS[unit](value)
        # Return base unit name
        base_units = {
            "Cel": "Cel", "K": "Cel", "F": "Cel",
            "min": "min", "h": "min", "s": "min",
            "Pa": "Pa", "kPa": "Pa", "bar": "Pa",
            "g": "g", "kg": "g", "mg": "g",
            "L": "L", "mL": "L", "m3": "L"
        }
        return converted_value, base_units.get(unit, unit)
    return value, unit

def get_parameter_type_from_unit(unit: str) -> Optional[str]:
    """Get parameter type from unit"""
    for param_type, units in UCUM_UNITS.items():
        if unit in units:
            return param_type
    return None


# Risk Assessment Schemas
class RiskThresholdCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    scope_type: str = Field(..., pattern="^(site|product|category)$")
    scope_id: Optional[int] = None
    low_threshold: int = Field(..., ge=1, le=25)
    medium_threshold: int = Field(..., ge=1, le=25)
    high_threshold: int = Field(..., ge=1, le=25)
    likelihood_scale: int = Field(5, ge=1, le=10)
    severity_scale: int = Field(5, ge=1, le=10)
    calculation_method: str = Field("multiplication", pattern="^(multiplication|addition|matrix)$")

    @field_validator('medium_threshold')
    @classmethod
    def validate_medium_threshold(cls, v, info):
        if 'low_threshold' in info.data and v <= info.data['low_threshold']:
            raise ValueError('medium_threshold must be greater than low_threshold')
        return v

    @field_validator('high_threshold')
    @classmethod
    def validate_high_threshold(cls, v, info):
        if 'medium_threshold' in info.data and v <= info.data['medium_threshold']:
            raise ValueError('high_threshold must be greater than medium_threshold')
        return v


class RiskThresholdUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    low_threshold: Optional[int] = Field(None, ge=1, le=25)
    medium_threshold: Optional[int] = Field(None, ge=1, le=25)
    high_threshold: Optional[int] = Field(None, ge=1, le=25)
    likelihood_scale: Optional[int] = Field(None, ge=1, le=10)
    severity_scale: Optional[int] = Field(None, ge=1, le=10)
    calculation_method: Optional[str] = Field(None, pattern="^(multiplication|addition|matrix)$")


class RiskThresholdResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    scope_type: str
    scope_id: Optional[int] = None
    low_threshold: int
    medium_threshold: int
    high_threshold: int
    likelihood_scale: int
    severity_scale: int
    calculation_method: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int

    model_config = {"from_attributes": True}


# Hazard Review Schemas
class HazardReviewCreate(BaseModel):
    hazard_id: int
    reviewer_id: int
    review_status: str = Field("pending", pattern="^(pending|approved|rejected)$")
    review_comments: Optional[str] = None
    hazard_identification_adequate: bool
    risk_assessment_appropriate: bool
    control_measures_suitable: bool
    ccp_determination_correct: bool


class HazardReviewUpdate(BaseModel):
    review_status: Optional[str] = Field(None, pattern="^(pending|approved|rejected)$")
    review_comments: Optional[str] = None
    hazard_identification_adequate: Optional[bool] = None
    risk_assessment_appropriate: Optional[bool] = None
    control_measures_suitable: Optional[bool] = None
    ccp_determination_correct: Optional[bool] = None


class HazardReviewResponse(BaseModel):
    id: int
    hazard_id: int
    reviewer_id: int
    review_status: str
    review_comments: Optional[str] = None
    review_date: Optional[datetime] = None
    hazard_identification_adequate: bool
    risk_assessment_appropriate: bool
    control_measures_suitable: bool
    ccp_determination_correct: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    reviewer_name: Optional[str] = None

    model_config = {"from_attributes": True}


# Product Management Schemas
class ProductCreate(BaseModel):
    product_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    formulation: Optional[str] = None
    allergens: Optional[str] = None
    shelf_life_days: Optional[int] = Field(None, ge=1)
    storage_conditions: Optional[str] = None
    packaging_type: Optional[str] = Field(None, max_length=100)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    formulation: Optional[str] = None
    allergens: Optional[str] = None
    shelf_life_days: Optional[int] = Field(None, ge=1)
    storage_conditions: Optional[str] = None
    packaging_type: Optional[str] = Field(None, max_length=100)
    haccp_plan_approved: Optional[bool] = None
    haccp_plan_version: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    product_code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    formulation: Optional[str] = None
    allergens: Optional[str] = None
    shelf_life_days: Optional[int] = None
    storage_conditions: Optional[str] = None
    packaging_type: Optional[str] = None
    haccp_plan_approved: bool
    haccp_plan_version: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Process Flow Schemas
class ProcessFlowCreate(BaseModel):
    step_number: int = Field(..., ge=1)
    step_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    equipment: Optional[str] = Field(None, max_length=100)
    temperature: Optional[float] = None
    time_minutes: Optional[float] = Field(None, ge=0)
    ph: Optional[float] = Field(None, ge=0, le=14)
    aw: Optional[float] = Field(None, ge=0, le=1)
    parameters: Optional[Dict[str, Any]] = None


class ProcessFlowUpdate(BaseModel):
    step_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    equipment: Optional[str] = Field(None, max_length=100)
    temperature: Optional[float] = None
    time_minutes: Optional[float] = Field(None, ge=0)
    ph: Optional[float] = Field(None, ge=0, le=14)
    aw: Optional[float] = Field(None, ge=0, le=1)
    parameters: Optional[Dict[str, Any]] = None


class ProcessFlowResponse(BaseModel):
    id: int
    step_number: int
    step_name: str
    description: Optional[str] = None
    equipment: Optional[str] = None
    temperature: Optional[float] = None
    time_minutes: Optional[float] = None
    ph: Optional[float] = None
    aw: Optional[float] = None
    parameters: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Hazard Schemas
class HazardCreate(BaseModel):
    process_step_id: int
    hazard_type: HazardType
    hazard_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    rationale: Optional[str] = None  # Reasoning for hazard identification and assessment
    prp_reference_ids: Optional[List[int]] = None  # Array of PRP/SOP document IDs
    references: Optional[List[Dict[str, Any]]] = None  # Array of reference documents
    likelihood: int = Field(..., ge=1, le=5)
    severity: int = Field(..., ge=1, le=5)
    control_measures: Optional[str] = None
    is_controlled: bool = False
    control_effectiveness: Optional[int] = Field(None, ge=1, le=5)
    is_ccp: bool = False
    ccp_justification: Optional[str] = None


class HazardUpdate(BaseModel):
    hazard_type: Optional[HazardType] = None
    hazard_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    rationale: Optional[str] = None  # Reasoning for hazard identification and assessment
    prp_reference_ids: Optional[List[int]] = None  # Array of PRP/SOP document IDs
    references: Optional[List[Dict[str, Any]]] = None  # Array of reference documents
    likelihood: Optional[int] = Field(None, ge=1, le=5)
    severity: Optional[int] = Field(None, ge=1, le=5)
    control_measures: Optional[str] = None
    is_controlled: Optional[bool] = None
    control_effectiveness: Optional[int] = Field(None, ge=1, le=5)
    is_ccp: Optional[bool] = None
    ccp_justification: Optional[str] = None


class HazardResponse(BaseModel):
    id: int
    process_step_id: int
    hazard_type: HazardType
    hazard_name: str
    description: Optional[str] = None
    rationale: Optional[str] = None  # Reasoning for hazard identification and assessment
    prp_reference_ids: Optional[List[int]] = None  # Array of PRP/SOP document IDs
    references: Optional[List[Dict[str, Any]]] = None  # Array of reference documents
    likelihood: int
    severity: int
    risk_score: int
    risk_level: RiskLevel
    control_measures: Optional[str] = None
    is_controlled: bool
    control_effectiveness: Optional[int] = None
    is_ccp: bool
    ccp_justification: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# CCP Schemas
class CCPCreate(BaseModel):
    hazard_id: int
    ccp_number: str = Field(..., min_length=1, max_length=20)
    ccp_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    
    # Enhanced critical limits
    critical_limits: Optional[List[CriticalLimitParameter]] = None
    validation_evidence: Optional[List[ValidationEvidence]] = None
    
    # Legacy fields for backward compatibility
    critical_limit_min: Optional[float] = None
    critical_limit_max: Optional[float] = None
    critical_limit_unit: Optional[str] = Field(None, max_length=50)
    critical_limit_description: Optional[str] = None
    
    monitoring_frequency: Optional[str] = Field(None, max_length=100)
    monitoring_method: Optional[str] = None
    monitoring_responsible: Optional[int] = None
    monitoring_equipment: Optional[str] = Field(None, max_length=100)
    corrective_actions: Optional[str] = None
    verification_frequency: Optional[str] = Field(None, max_length=100)
    verification_method: Optional[str] = None
    verification_responsible: Optional[int] = None
    monitoring_records: Optional[str] = None
    verification_records: Optional[str] = None


class CCPUpdate(BaseModel):
    ccp_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[CCPStatus] = None
    
    # Enhanced critical limits
    critical_limits: Optional[List[CriticalLimitParameter]] = None
    validation_evidence: Optional[List[ValidationEvidence]] = None
    
    # Legacy fields for backward compatibility
    critical_limit_min: Optional[float] = None
    critical_limit_max: Optional[float] = None
    critical_limit_unit: Optional[str] = Field(None, max_length=50)
    critical_limit_description: Optional[str] = None
    
    monitoring_frequency: Optional[str] = Field(None, max_length=100)
    monitoring_method: Optional[str] = None
    monitoring_responsible: Optional[int] = None
    monitoring_equipment: Optional[str] = Field(None, max_length=100)
    corrective_actions: Optional[str] = None
    verification_frequency: Optional[str] = Field(None, max_length=100)
    verification_method: Optional[str] = None
    verification_responsible: Optional[int] = None
    monitoring_records: Optional[str] = None
    verification_records: Optional[str] = None


class CCPResponse(BaseModel):
    id: int
    ccp_number: str
    ccp_name: str
    description: Optional[str] = None
    status: CCPStatus
    
    # Enhanced critical limits
    critical_limits: Optional[List[Dict[str, Any]]] = None
    validation_evidence: Optional[List[Dict[str, Any]]] = None
    limits_summary: Optional[str] = None
    
    # Legacy fields for backward compatibility
    critical_limit_min: Optional[float] = None
    critical_limit_max: Optional[float] = None
    critical_limit_unit: Optional[str] = None
    critical_limit_description: Optional[str] = None
    
    monitoring_frequency: Optional[str] = None
    monitoring_method: Optional[str] = None
    monitoring_responsible: Optional[int] = None
    monitoring_equipment: Optional[str] = None
    corrective_actions: Optional[str] = None
    verification_frequency: Optional[str] = None
    verification_method: Optional[str] = None
    verification_responsible: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Monitoring Log Schemas
class MonitoringLogCreate(BaseModel):
    batch_number: Optional[str] = Field(None, min_length=1, max_length=50)
    batch_id: Optional[int] = None
    measured_value: float
    unit: Optional[str] = Field(None, max_length=20)
    additional_parameters: Optional[Dict[str, Any]] = None
    observations: Optional[str] = None
    evidence_files: Optional[str] = None
    corrective_action_taken: bool = False
    corrective_action_description: Optional[str] = None
    corrective_action_by: Optional[int] = None
    equipment_id: Optional[int] = None


class MonitoringLogResponse(BaseModel):
    id: int
    batch_number: Optional[str] = None
    batch_id: Optional[int] = None
    monitoring_time: datetime
    measured_value: float
    unit: Optional[str] = None
    is_within_limits: bool
    additional_parameters: Optional[Dict[str, Any]] = None
    observations: Optional[str] = None
    evidence_files: Optional[str] = None
    corrective_action_taken: bool
    corrective_action_description: Optional[str] = None
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Verification Log Schemas
class VerificationLogCreate(BaseModel):
    verification_method: Optional[str] = None
    verification_result: Optional[str] = None
    is_compliant: bool = True
    samples_tested: Optional[int] = Field(None, ge=0)
    test_results: Optional[Dict[str, Any]] = None
    equipment_calibration: Optional[bool] = None
    calibration_date: Optional[datetime] = None
    evidence_files: Optional[str] = None


class VerificationLogResponse(BaseModel):
    id: int
    verification_date: datetime
    verification_method: Optional[str] = None
    verification_result: Optional[str] = None
    is_compliant: bool
    samples_tested: Optional[int] = None
    test_results: Optional[Dict[str, Any]] = None
    equipment_calibration: Optional[bool] = None
    calibration_date: Optional[datetime] = None
    evidence_files: Optional[str] = None
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Decision Tree Schemas
class DecisionTreeStep(BaseModel):
    question: DecisionTreeQuestion
    answer: bool
    explanation: Optional[str] = None


class DecisionTreeResult(BaseModel):
    is_ccp: bool
    justification: str
    steps: List[DecisionTreeStep]


# HACCP Plan Schemas
class HACCPPlanStatus(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    OBSOLETE = "obsolete"


class HACCPPlanCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    content: str = Field(..., description="Serialized JSON or rich text content")
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None


class HACCPPlanUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = None
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    status: Optional[HACCPPlanStatus] = None


class HACCPPlanResponse(BaseModel):
    id: int
    product_id: int
    title: str
    description: Optional[str]
    status: HACCPPlanStatus
    version: str
    effective_date: Optional[datetime]
    review_date: Optional[datetime]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class HACCPPlanVersionCreate(BaseModel):
    content: str
    change_description: Optional[str] = None
    change_reason: Optional[str] = None


class HACCPPlanVersionResponse(BaseModel):
    id: int
    plan_id: int
    version_number: str
    content: str
    change_description: Optional[str]
    created_by: int
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class HACCPPlanApprovalCreate(BaseModel):
    approver_id: int
    approval_order: int
    comments: Optional[str] = None


class HACCPPlanApprovalResponse(BaseModel):
    id: int
    plan_id: int
    approver_id: int
    approval_order: int
    status: str
    comments: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# Flowchart Schemas
class FlowchartNode(BaseModel):
    id: str
    type: str  # "process", "decision", "start", "end"
    label: str
    x: float
    y: float
    data: Optional[Dict[str, Any]] = None


class FlowchartEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None


class FlowchartData(BaseModel):
    nodes: List[FlowchartNode]
    edges: List[FlowchartEdge]


# Dashboard Schemas
class HACCPDashboardStats(BaseModel):
    total_products: int
    approved_plans: int
    total_ccps: int
    active_ccps: int
    out_of_spec_count: int
    recent_logs: List[Dict[str, Any]]


# Report Schemas
class HACCPReportRequest(BaseModel):
    product_id: int
    report_type: str = Field(..., pattern="^(summary|detailed|monitoring|verification)$")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_charts: bool = True
    format: str = Field("pdf", pattern="^(pdf|excel|html)$")

# Decision Tree Schemas (Codex Alimentarius)
class DecisionTreeAnswer(BaseModel):
    answer: bool
    justification: Optional[str] = None

class DecisionTreeQuestionResponse(BaseModel):
    question_number: int
    answer: bool
    justification: Optional[str] = None

class DecisionTreeCreate(BaseModel):
    hazard_id: int
    q1_answer: bool
    q1_justification: Optional[str] = None

class DecisionTreeUpdate(BaseModel):
    q1_answer: Optional[bool] = None
    q1_justification: Optional[str] = None
    q2_answer: Optional[bool] = None
    q2_justification: Optional[str] = None
    q3_answer: Optional[bool] = None
    q3_justification: Optional[bool] = None
    q4_answer: Optional[bool] = None
    q4_justification: Optional[str] = None

class DecisionTreeResponse(BaseModel):
    id: int
    hazard_id: int
    q1_answer: Optional[bool] = None
    q1_justification: Optional[str] = None
    q1_answered_by: Optional[int] = None
    q1_answered_at: Optional[datetime] = None
    q2_answer: Optional[bool] = None
    q2_justification: Optional[str] = None
    q2_answered_by: Optional[int] = None
    q2_answered_at: Optional[datetime] = None
    q3_answer: Optional[bool] = None
    q3_justification: Optional[str] = None
    q3_answered_by: Optional[int] = None
    q3_answered_at: Optional[datetime] = None
    q4_answer: Optional[bool] = None
    q4_justification: Optional[str] = None
    q4_answered_by: Optional[int] = None
    q4_answered_at: Optional[datetime] = None
    is_ccp: Optional[bool] = None
    decision_reasoning: Optional[str] = None
    decision_date: Optional[datetime] = None
    decision_by: Optional[int] = None
    status: str
    current_question: int
    can_proceed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Product Risk Configuration Schemas (ISO 22000 compliant)
class ProductRiskConfigCreate(BaseModel):
    calculation_method: Literal["multiplication", "addition", "matrix"] = "multiplication"
    likelihood_scale: int = Field(ge=1, le=10, default=5)
    severity_scale: int = Field(ge=1, le=10, default=5)
    low_threshold: int = Field(ge=1, default=4)
    medium_threshold: int = Field(ge=1, default=8)
    high_threshold: int = Field(ge=1, default=15)
    
    @field_validator('medium_threshold')
    @classmethod
    def validate_threshold_order(cls, v, values):
        if 'low_threshold' in values.data and v <= values.data['low_threshold']:
            raise ValueError('medium_threshold must be greater than low_threshold')
        return v
    
    @field_validator('high_threshold')
    @classmethod
    def validate_high_threshold(cls, v, values):
        if 'medium_threshold' in values.data and v <= values.data['medium_threshold']:
            raise ValueError('high_threshold must be greater than medium_threshold')
        return v

class ProductRiskConfigUpdate(BaseModel):
    calculation_method: Optional[Literal["multiplication", "addition", "matrix"]] = None
    likelihood_scale: Optional[int] = Field(None, ge=1, le=10)
    severity_scale: Optional[int] = Field(None, ge=1, le=10)
    low_threshold: Optional[int] = Field(None, ge=1)
    medium_threshold: Optional[int] = Field(None, ge=1)
    high_threshold: Optional[int] = Field(None, ge=1)

class ProductRiskConfigResponse(BaseModel):
    id: int
    product_id: int
    calculation_method: str
    likelihood_scale: int
    severity_scale: int
    low_threshold: int
    medium_threshold: int
    high_threshold: int
    created_at: datetime
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Monitoring Schedule Schemas
class MonitoringScheduleCreate(BaseModel):
    ccp_id: int
    schedule_type: str = Field(..., pattern="^(interval|cron|manual)$")
    interval_minutes: Optional[int] = Field(None, ge=1)
    cron_expression: Optional[str] = Field(None, max_length=100)
    tolerance_window_minutes: int = Field(default=15, ge=1, le=1440)  # 1 minute to 24 hours
    is_active: bool = True


class MonitoringScheduleUpdate(BaseModel):
    schedule_type: Optional[str] = Field(None, pattern="^(interval|cron|manual)$")
    interval_minutes: Optional[int] = Field(None, ge=1)
    cron_expression: Optional[str] = Field(None, max_length=100)
    tolerance_window_minutes: Optional[int] = Field(None, ge=1, le=1440)
    is_active: Optional[bool] = None


class MonitoringScheduleResponse(BaseModel):
    id: int
    ccp_id: int
    schedule_type: str
    interval_minutes: Optional[int] = None
    cron_expression: Optional[str] = None
    tolerance_window_minutes: int
    is_active: bool
    last_scheduled_time: Optional[datetime] = None
    next_due_time: Optional[datetime] = None
    created_at: datetime
    created_by: int
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class MonitoringScheduleStatus(BaseModel):
    """Status information for monitoring schedule"""
    schedule_id: int
    ccp_id: int
    ccp_name: str
    is_due: bool
    is_overdue: bool
    next_due_time: Optional[datetime] = None
    last_monitoring_time: Optional[datetime] = None
    tolerance_window_minutes: int
    schedule_type: str
    is_active: bool


# Verification Program Schemas
class VerificationProgramCreate(BaseModel):
    ccp_id: int
    verification_type: str = Field(..., pattern="^(record_review|direct_observation|sampling_testing|calibration_check)$")
    frequency: str = Field(..., pattern="^(daily|weekly|monthly|quarterly|custom)$")
    frequency_value: Optional[int] = Field(None, ge=1)
    required_verifier_role: Optional[str] = None
    verification_criteria: Optional[str] = None
    sampling_plan: Optional[str] = None
    is_active: bool = True


class VerificationProgramResponse(BaseModel):
    id: int
    ccp_id: int
    verification_type: str
    frequency: str
    frequency_value: Optional[int] = None
    last_verification_date: Optional[datetime] = None
    next_verification_date: Optional[datetime] = None
    is_active: bool
    required_verifier_role: Optional[str] = None
    verification_criteria: Optional[str] = None
    sampling_plan: Optional[str] = None
    created_at: datetime
    created_by: int
    updated_at: datetime
    
    model_config = {"from_attributes": True}

# Verification Program Schemas
class VerificationProgramCreate(BaseModel):
    ccp_id: int
    verification_type: str = Field(..., pattern="^(record_review|direct_observation|sampling_testing|calibration_check)$")
    frequency: str = Field(..., pattern="^(daily|weekly|monthly|quarterly|custom)$")
    frequency_value: Optional[int] = Field(None, ge=1)
    required_verifier_role: Optional[str] = None
    verification_criteria: Optional[str] = None
    sampling_plan: Optional[str] = None
    is_active: bool = True


class VerificationProgramUpdate(BaseModel):
    verification_type: Optional[str] = Field(None, pattern="^(record_review|direct_observation|sampling_testing|calibration_check)$")
    frequency: Optional[str] = Field(None, pattern="^(daily|weekly|monthly|quarterly|custom)$")
    frequency_value: Optional[int] = Field(None, ge=1)
    required_verifier_role: Optional[str] = None
    verification_criteria: Optional[str] = None
    sampling_plan: Optional[str] = None
    is_active: Optional[bool] = None


class VerificationProgramResponse(BaseModel):
    id: int
    ccp_id: int
    verification_type: str
    frequency: str
    frequency_value: Optional[int] = None
    last_verification_date: Optional[datetime] = None
    next_verification_date: Optional[datetime] = None
    is_active: bool
    required_verifier_role: Optional[str] = None
    verification_criteria: Optional[str] = None
    sampling_plan: Optional[str] = None
    created_at: datetime
    created_by: int
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Validation Schemas
class ValidationCreate(BaseModel):
    ccp_id: int
    validation_type: str = Field(..., pattern="^(process_authority_letter|scientific_study|validation_test|expert_opinion)$")
    validation_title: str = Field(..., min_length=1, max_length=200)
    validation_description: Optional[str] = None
    document_id: Optional[int] = None
    external_reference: Optional[str] = Field(None, max_length=500)
    validation_date: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    validation_result: Optional[str] = None
    critical_limits_validated: Optional[str] = None
    is_active: bool = True


class ValidationUpdate(BaseModel):
    validation_type: Optional[str] = Field(None, pattern="^(process_authority_letter|scientific_study|validation_test|expert_opinion)$")
    validation_title: Optional[str] = Field(None, min_length=1, max_length=200)
    validation_description: Optional[str] = None
    document_id: Optional[int] = None
    external_reference: Optional[str] = Field(None, max_length=500)
    validation_date: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    validation_result: Optional[str] = None
    critical_limits_validated: Optional[str] = None
    is_active: Optional[bool] = None


class ValidationResponse(BaseModel):
    id: int
    ccp_id: int
    validation_type: str
    validation_title: str
    validation_description: Optional[str] = None
    document_id: Optional[int] = None
    external_reference: Optional[str] = None
    validation_date: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool
    validation_result: Optional[str] = None
    critical_limits_validated: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_status: str
    review_notes: Optional[str] = None
    created_at: datetime
    created_by: int
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ValidationReviewRequest(BaseModel):
    review_status: str = Field(..., pattern="^(pending|approved|rejected)$")
    review_notes: Optional[str] = None

# Validation Schemas
class ValidationCreate(BaseModel):
    ccp_id: int
    validation_type: str = Field(..., pattern="^(process_authority_letter|scientific_study|validation_test|expert_opinion)$")
    validation_title: str = Field(..., min_length=1, max_length=200)
    validation_description: Optional[str] = None
    document_id: Optional[int] = None
    external_reference: Optional[str] = Field(None, max_length=500)
    validation_date: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    validation_result: Optional[str] = None
    critical_limits_validated: Optional[str] = None
    is_active: bool = True


class ValidationResponse(BaseModel):
    id: int
    ccp_id: int
    validation_type: str
    validation_title: str
    validation_description: Optional[str] = None
    document_id: Optional[int] = None
    external_reference: Optional[str] = None
    validation_date: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool
    validation_result: Optional[str] = None
    critical_limits_validated: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_status: str
    review_notes: Optional[str] = None
    created_at: datetime
    created_by: int
    updated_at: datetime
    
    model_config = {"from_attributes": True}

# Evidence Attachment Schemas
class EvidenceAttachmentCreate(BaseModel):
    record_type: str = Field(..., pattern="^(monitoring_log|verification_log|validation|ccp|hazard)$")
    record_id: int
    document_id: int
    evidence_type: str = Field(..., pattern="^(photo|document|certificate|test_result|calibration|sop|other)$")
    description: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None


class EvidenceAttachmentResponse(BaseModel):
    id: int
    record_type: str
    record_id: int
    document_id: int
    evidence_type: str
    description: Optional[str] = None
    upload_date: datetime
    uploaded_by: int
    file_size: Optional[int] = None 
    file_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    event_type: str
    event_description: str
    record_type: str
    record_id: int
    user_id: int
    user_role: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    changed_fields: Optional[str] = None
    signature_hash: Optional[str] = None
    signature_timestamp: Optional[datetime] = None
    signature_method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}
