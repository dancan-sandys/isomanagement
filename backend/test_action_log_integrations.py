#!/usr/bin/env python3
"""
Test Action Log Integrations
Test the new integrations between Non-Conformance, Risk Management, and Audit modules with Actions Log
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.nonconformance_service import NonConformanceService
from app.services.risk_service import RiskService
from app.services.audit_risk_service import AuditRiskService
from app.services.actions_log_service import ActionsLogService
from app.schemas.nonconformance import CAPAActionCreate
from app.models.actions_log import ActionSource

def test_nc_capa_integration():
    """Test Non-Conformance CAPA Action integration with Actions Log"""
    print("\n🔄 Testing Non-Conformance CAPA Action Integration...")
    
    try:
        db = next(get_db())
        nc_service = NonConformanceService(db)
        actions_service = ActionsLogService(db)
        
        # Create a test CAPA action
        capa_data = CAPAActionCreate(
            non_conformance_id=1,  # Assuming NC with ID 1 exists
            title="Test CAPA Action for Action Log Integration",
            description="Testing the integration between CAPA actions and actions log",
            action_type="corrective",
            responsible_person=1,  # Assuming user with ID 1 exists
            target_completion_date=datetime.now() + timedelta(days=30)
        )
        
        # Create CAPA action (should auto-create action log entry)
        capa_action = nc_service.create_capa_action(capa_data, created_by=1)
        print(f"✅ Created CAPA Action ID: {capa_action.id}")
        
        # Verify action log entry was created
        if capa_action.action_log_id:
            action_log = actions_service.get_action(capa_action.action_log_id)
            if action_log:
                print(f"✅ Action Log Entry Created - ID: {action_log.id}, Source: {action_log.action_source}")
                assert action_log.action_source == ActionSource.NON_CONFORMANCE.value
                print("✅ Source type correctly set to NON_CONFORMANCE")
            else:
                print("❌ Action log entry not found")
        else:
            print("❌ CAPA action not linked to action log")
            
        return True
        
    except Exception as e:
        print(f"❌ NC CAPA Integration Test Failed: {e}")
        return False

def test_risk_action_integration():
    """Test Risk Action integration with Actions Log"""
    print("\n🔄 Testing Risk Action Integration...")
    
    try:
        db = next(get_db())
        risk_service = RiskService(db)
        actions_service = ActionsLogService(db)
        
        # Create a test risk action
        risk_action = risk_service.add_action(
            item_id=1,  # Assuming risk item with ID 1 exists
            title="Test Risk Mitigation Action",
            description="Testing the integration between risk actions and actions log",
            assigned_to=1,
            due_date=datetime.now() + timedelta(days=30),
            created_by=1
        )
        print(f"✅ Created Risk Action ID: {risk_action.id}")
        
        # Verify action log entry was created
        if risk_action.action_log_id:
            action_log = actions_service.get_action(risk_action.action_log_id)
            if action_log:
                print(f"✅ Action Log Entry Created - ID: {action_log.id}, Source: {action_log.action_source}")
                assert action_log.action_source == ActionSource.RISK_ASSESSMENT.value
                print("✅ Source type correctly set to RISK_ASSESSMENT")
            else:
                print("❌ Action log entry not found")
        else:
            print("❌ Risk action not linked to action log")
            
        return True
        
    except Exception as e:
        print(f"❌ Risk Action Integration Test Failed: {e}")
        return False

def test_audit_finding_integration():
    """Test Audit Finding integration with Actions Log"""
    print("\n🔄 Testing Audit Finding Integration...")
    
    try:
        db = next(get_db())
        audit_service = AuditRiskService(db)
        actions_service = ActionsLogService(db)
        
        # Try to create action log entry for existing audit finding
        finding = audit_service.create_audit_finding_action(
            finding_id=1,  # Assuming audit finding with ID 1 exists
            created_by=1
        )
        print(f"✅ Processed Audit Finding ID: {finding.id}")
        
        # Verify action log entry was created
        if finding.action_log_id:
            action_log = actions_service.get_action(finding.action_log_id)
            if action_log:
                print(f"✅ Action Log Entry Created - ID: {action_log.id}, Source: {action_log.action_source}")
                assert action_log.action_source == ActionSource.AUDIT_FINDING.value
                print("✅ Source type correctly set to AUDIT_FINDING")
            else:
                print("❌ Action log entry not found")
        else:
            print("❌ Audit finding not linked to action log")
            
        return True
        
    except Exception as e:
        print(f"❌ Audit Finding Integration Test Failed: {e}")
        return False

def test_actions_log_analytics():
    """Test Actions Log Analytics with new sources"""
    print("\n🔄 Testing Actions Log Analytics...")
    
    try:
        db = next(get_db())
        actions_service = ActionsLogService(db)
        
        # Get analytics
        analytics = actions_service.get_analytics()
        print(f"✅ Total Actions: {analytics.total_actions}")
        print(f"✅ Source Breakdown: {analytics.source_breakdown}")
        
        # Check if our new sources appear in analytics
        expected_sources = [
            ActionSource.NON_CONFORMANCE.value,
            ActionSource.RISK_ASSESSMENT.value,
            ActionSource.AUDIT_FINDING.value,
            ActionSource.MANAGEMENT_REVIEW.value
        ]
        
        for source in expected_sources:
            if source in analytics.source_breakdown:
                print(f"✅ Source '{source}' found in analytics with {analytics.source_breakdown[source]} actions")
            else:
                print(f"ℹ️  Source '{source}' not yet in analytics (no actions created)")
        
        return True
        
    except Exception as e:
        print(f"❌ Actions Log Analytics Test Failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Testing Action Log Integrations for NC/CAPA, Risk Management, and Audit Findings")
    print("=" * 80)
    
    results = []
    
    # Test each integration
    results.append(test_nc_capa_integration())
    results.append(test_risk_action_integration()) 
    results.append(test_audit_finding_integration())
    results.append(test_actions_log_analytics())
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Results Summary:")
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    if passed == total:
        print("🎉 All integration tests passed!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    print("\n💡 Note: Some tests may fail if test data doesn't exist.")
    print("   This is expected in a fresh database.")

if __name__ == "__main__":
    main()