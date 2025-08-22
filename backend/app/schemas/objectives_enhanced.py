#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Pydantic schemas for Objectives Management System
Supports corporate and departmental objectives with advanced tracking
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ObjectiveType(str, Enum):
    CORPORATE = "corporate"
    DEPARTMENTAL = "departmental"
    OPERATIONAL = "operational"


class HierarchyLevel(str, Enum):
    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"


class TrendDirection(str, Enum):
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"


class PerformanceColor(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class DataSource(str, Enum):
    MANUAL = "manual"
    SYSTEM = "system"
    INTEGRATION = "integration"


# Base schemas
class ObjectiveBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Objective title")
    description: Optional[str] = Field(None, description="Objective description")
    category: Optional[str] = Field(None, max_length=100, description="Objective category")
    objective_type: ObjectiveType = Field(ObjectiveType.OPERATIONAL, description="Type of objective")
    hierarchy_level: HierarchyLevel = Field(HierarchyLevel.OPERATIONAL, description="Hierarchy level")
    parent_objective_id: Optional[int] = Field(None, description="Parent objective ID for hierarchical relationships")
    department_id: Optional[int] = Field(None, description="Department ID for departmental objectives")
    baseline_value: Optional[float] = Field(None, description="Baseline value for the objective")
    target_value: Optional[float] = Field(None, description="Target value for the objective")
    measurement_unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    weight: float = Field(1.0, ge=0.0, le=10.0, description="Weight for KPI calculations")
    measurement_frequency: Optional[str] = Field(None, max_length=100, description="Measurement frequency")
    frequency: Optional[str] = Field(None, max_length=100, description="Review frequency")
    responsible_person_id: Optional[int] = Field(None, description="Responsible person ID")
    review_frequency: Optional[str] = Field(None, max_length=100, description="Review frequency")
    automated_calculation: bool = Field(False, description="Whether calculation is automated")
    data_source: DataSource = Field(DataSource.MANUAL, description="Data source for tracking")


class ObjectiveCreate(ObjectiveBase):
    objective_code: Optional[str] = Field(None, max_length=50, description="Objective code (auto-generated if not provided)")


class ObjectiveUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    objective_type: Optional[ObjectiveType] = None
    hierarchy_level: Optional[HierarchyLevel] = None
    parent_objective_id: Optional[int] = None
    department_id: Optional[int] = None
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    measurement_unit: Optional[str] = Field(None, max_length=50)
    weight: Optional[float] = Field(None, ge=0.0, le=10.0)
    measurement_frequency: Optional[str] = Field(None, max_length=100)
    frequency: Optional[str] = Field(None, max_length=100)
    responsible_person_id: Optional[int] = None
    review_frequency: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, description="Objective status")
    automated_calculation: Optional[bool] = None
    data_source: Optional[DataSource] = None


class Objective(ObjectiveBase):
    id: int
    objective_code: str
    status: str = Field(..., description="Objective status")
    trend_direction: Optional[TrendDirection] = None
    performance_color: Optional[PerformanceColor] = None
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    last_updated_by: Optional[int] = None
    last_updated_at: Optional[datetime] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    responsible_person_name: Optional[str] = None
    department_name: Optional[str] = None
    parent_objective_title: Optional[str] = None
    
    class Config:
        from_attributes = True


# Target schemas
class ObjectiveTargetBase(BaseModel):
    period_start: datetime = Field(..., description="Period start date")
    period_end: datetime = Field(..., description="Period end date")
    target_value: float = Field(..., description="Target value for the period")
    lower_threshold: Optional[float] = Field(None, description="Lower threshold")
    upper_threshold: Optional[float] = Field(None, description="Upper threshold")
    weight: float = Field(1.0, ge=0.0, le=10.0, description="Weight for this target")
    is_lower_better: bool = Field(False, description="Whether lower values are better")


class ObjectiveTargetCreate(ObjectiveTargetBase):
    objective_id: int = Field(..., description="Objective ID")
    department_id: Optional[int] = Field(None, description="Department ID")


class ObjectiveTargetUpdate(BaseModel):
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    target_value: Optional[float] = None
    lower_threshold: Optional[float] = None
    upper_threshold: Optional[float] = None
    weight: Optional[float] = Field(None, ge=0.0, le=10.0)
    is_lower_better: Optional[bool] = None


class ObjectiveTarget(ObjectiveTargetBase):
    id: int
    objective_id: int
    department_id: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Progress schemas
class ObjectiveProgressBase(BaseModel):
    period_start: datetime = Field(..., description="Period start date")
    period_end: datetime = Field(..., description="Period end date")
    actual_value: float = Field(..., description="Actual value achieved")
    evidence: Optional[str] = Field(None, description="Evidence or notes")


class ObjectiveProgressCreate(ObjectiveProgressBase):
    objective_id: int = Field(..., description="Objective ID")
    department_id: Optional[int] = Field(None, description="Department ID")


class ObjectiveProgressUpdate(BaseModel):
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    actual_value: Optional[float] = None
    evidence: Optional[str] = None


class ObjectiveProgress(ObjectiveProgressBase):
    id: int
    objective_id: int
    department_id: Optional[int] = None
    attainment_percent: Optional[float] = None
    status: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Dashboard and analytics schemas
class DashboardKPIs(BaseModel):
    total_objectives: int
    corporate_objectives: int
    departmental_objectives: int
    operational_objectives: int
    recent_progress_entries: int
    on_track_percentage: float
    performance_breakdown: Dict[str, int]


class PerformanceMetrics(BaseModel):
    average_attainment: float
    trend: str
    monthly_averages: List[float]
    total_entries: int


class TrendAnalysis(BaseModel):
    trend: str
    direction: Optional[TrendDirection]
    slope: float
    values: List[float]
    periods: int


class PerformanceAlert(BaseModel):
    type: str
    objective_id: int
    objective_title: str
    message: str
    severity: str
    attainment_percent: Optional[float] = None


# Hierarchical structure schemas
class ObjectiveTreeNode(BaseModel):
    id: int
    title: str
    objective_type: ObjectiveType
    hierarchy_level: HierarchyLevel
    department_id: Optional[int] = None
    children: List['ObjectiveTreeNode'] = []


ObjectiveTreeNode.model_rebuild()


class ObjectiveHierarchy(BaseModel):
    objectives: List[ObjectiveTreeNode]


# Department schemas
class DepartmentBase(BaseModel):
    department_code: str = Field(..., min_length=1, max_length=50, description="Department code")
    name: str = Field(..., min_length=1, max_length=200, description="Department name")
    description: Optional[str] = Field(None, description="Department description")
    parent_department_id: Optional[int] = Field(None, description="Parent department ID")
    manager_id: Optional[int] = Field(None, description="Department manager ID")
    color_code: Optional[str] = Field(None, max_length=7, description="Color code for UI display")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    department_code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    parent_department_id: Optional[int] = None
    manager_id: Optional[int] = None
    status: Optional[str] = Field(None, description="Department status")
    color_code: Optional[str] = Field(None, max_length=7)


class Department(DepartmentBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int
    
    # Related data
    manager_name: Optional[str] = None
    parent_department_name: Optional[str] = None
    objectives_count: Optional[int] = None
    
    class Config:
        from_attributes = True


# Bulk operations schemas
class BulkProgressCreate(BaseModel):
    objective_id: int
    progress_entries: List[ObjectiveProgressCreate]


class BulkTargetCreate(BaseModel):
    objective_id: int
    targets: List[ObjectiveTargetCreate]


# Response schemas
class ObjectivesListResponse(BaseModel):
    objectives: List[Objective]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class ObjectivesDashboardResponse(BaseModel):
    kpis: DashboardKPIs
    performance_metrics: PerformanceMetrics
    alerts: List[PerformanceAlert]
    recent_objectives: List[Objective]


class ObjectiveDetailResponse(BaseModel):
    objective: Objective
    targets: List[ObjectiveTarget]
    progress: List[ObjectiveProgress]
    trend_analysis: TrendAnalysis
    child_objectives: List[Objective]


# Filter schemas
class ObjectiveFilters(BaseModel):
    objective_type: Optional[ObjectiveType] = None
    department_id: Optional[int] = None
    hierarchy_level: Optional[HierarchyLevel] = None
    status: Optional[str] = None
    performance_color: Optional[PerformanceColor] = None
    trend_direction: Optional[TrendDirection] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# Export schemas
class ObjectivesExport(BaseModel):
    objectives: List[Objective]
    targets: List[ObjectiveTarget]
    progress: List[ObjectiveProgress]
    departments: List[Department]
    export_date: datetime
    export_format: str = "json"
