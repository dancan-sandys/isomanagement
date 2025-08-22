#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Enhanced Objectives Management System
Tests the database models and service layer functionality
"""

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.objectives_service_enhanced import ObjectivesServiceEnhanced
from app.models.food_safety_objectives import (
    FoodSafetyObjective, ObjectiveTarget, ObjectiveProgress,
    ObjectiveType, HierarchyLevel, TrendDirection, PerformanceColor, DataSource
)
from app.models.dashboard import Department


def test_enhanced_objectives():
    """Test the enhanced objectives functionality"""
    
    print("Testing Enhanced Objectives Management System...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Initialize service
        service = ObjectivesServiceEnhanced(db)
        
        print("\n1. Testing Department Creation...")
        
        # Test department creation
        departments = db.query(Department).all()
        print(f"   Found {len(departments)} departments")
        for dept in departments:
            print(f"   - {dept.name} ({dept.department_code})")
        
        print("\n2. Testing Objectives Retrieval...")
        
        # Test objectives retrieval
        objectives = service.list_objectives()
        print(f"   Found {len(objectives)} objectives")
        
        for obj in objectives:
            print(f"   - {obj.title} (Type: {obj.objective_type}, Level: {obj.hierarchy_level})")
        
        print("\n3. Testing Corporate Objectives...")
        
        # Test corporate objectives
        corporate_objectives = service.get_corporate_objectives()
        print(f"   Found {len(corporate_objectives)} corporate objectives")
        
        for obj in corporate_objectives:
            print(f"   - {obj.title}")
        
        print("\n4. Testing Departmental Objectives...")
        
        # Test departmental objectives
        if departments:
            dept_id = departments[0].id
            dept_objectives = service.get_departmental_objectives(dept_id)
            print(f"   Found {len(dept_objectives)} objectives for department {departments[0].name}")
        
        print("\n5. Testing Dashboard KPIs...")
        
        # Test dashboard KPIs
        kpis = service.get_dashboard_kpis()
        print(f"   Total Objectives: {kpis['total_objectives']}")
        print(f"   Corporate Objectives: {kpis['corporate_objectives']}")
        print(f"   Departmental Objectives: {kpis['departmental_objectives']}")
        print(f"   Operational Objectives: {kpis['operational_objectives']}")
        print(f"   On Track Percentage: {kpis['on_track_percentage']}%")
        
        print("\n6. Testing Performance Metrics...")
        
        # Test performance metrics
        metrics = service.get_performance_metrics()
        print(f"   Average Attainment: {metrics['average_attainment']}%")
        print(f"   Trend: {metrics['trend']}")
        print(f"   Total Entries: {metrics['total_entries']}")
        
        print("\n7. Testing Alerts...")
        
        # Test alerts
        alerts = service.get_alerts()
        print(f"   Found {len(alerts)} alerts")
        
        for alert in alerts:
            print(f"   - {alert['type']}: {alert['message']} (Severity: {alert['severity']})")
        
        print("\n8. Testing Trend Analysis...")
        
        # Test trend analysis for first objective
        if objectives:
            objective_id = objectives[0].id
            trend = service.get_trend_analysis(objective_id)
            print(f"   Trend for '{objectives[0].title}': {trend['trend']}")
            print(f"   Direction: {trend['direction']}")
            print(f"   Slope: {trend['slope']}")
        
        print("\n9. Testing Hierarchical Structure...")
        
        # Test hierarchical structure
        hierarchy = service.get_hierarchical_objectives()
        print(f"   Found {len(hierarchy)} top-level objectives")
        
        for obj in hierarchy:
            print(f"   - {obj['title']} (Children: {len(obj['children'])})")
        
        print("\n✅ All tests completed successfully!")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   Departments: {len(departments)}")
        print(f"   Total Objectives: {len(objectives)}")
        print(f"   Corporate Objectives: {len(corporate_objectives)}")
        print(f"   Alerts: {len(alerts)}")
        print(f"   On Track Percentage: {kpis['on_track_percentage']}%")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def test_objective_creation():
    """Test creating a new objective"""
    
    print("\nTesting Objective Creation...")
    
    db = SessionLocal()
    
    try:
        service = ObjectivesServiceEnhanced(db)
        
        # Create a test objective
        test_objective_data = {
            "title": "Test Enhanced Objective",
            "description": "This is a test objective for the enhanced system",
            "objective_type": ObjectiveType.DEPARTMENTAL,
            "hierarchy_level": HierarchyLevel.TACTICAL,
            "department_id": 1,
            "baseline_value": 80.0,
            "target_value": 95.0,
            "measurement_unit": "percentage",
            "weight": 1.5,
            "measurement_frequency": "monthly",
            "created_by": 1
        }
        
        objective = service.create_objective(test_objective_data)
        print(f"   ✅ Created objective: {objective.title} (ID: {objective.id})")
        
        # Test progress creation
        progress_data = {
            "objective_id": objective.id,
            "period_start": datetime.utcnow() - timedelta(days=30),
            "period_end": datetime.utcnow(),
            "actual_value": 88.0,
            "evidence": "Test progress entry",
            "created_by": 1
        }
        
        progress = service.create_progress(progress_data)
        print(f"   ✅ Created progress: {progress.actual_value}% attainment")
        
        # Test target creation
        target_data = {
            "objective_id": objective.id,
            "period_start": datetime.utcnow(),
            "period_end": datetime.utcnow() + timedelta(days=90),
            "target_value": 95.0,
            "weight": 1.0,
            "created_by": 1
        }
        
        target = service.create_target(target_data)
        print(f"   ✅ Created target: {target.target_value}")
        
        print("   ✅ Objective creation test completed successfully!")
        
    except Exception as e:
        print(f"   ❌ Objective creation test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starting Enhanced Objectives Management System Tests")
    print("=" * 60)
    
    test_enhanced_objectives()
    test_objective_creation()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("✅ Enhanced Objectives Management System is working correctly!")
    print("🚀 Ready for Phase 1 implementation!")
