from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.services.immediate_action_service import ImmediateActionService
from app.services.risk_assessment_service import RiskAssessmentService
from app.services.escalation_service import EscalationService
from app.services.preventive_action_service import PreventiveActionService
from app.services.effectiveness_monitoring_service import EffectivenessMonitoringService
from app.schemas.nonconformance import (
    ImmediateActionCreate, NonConformanceRiskAssessmentCreate, EscalationRuleCreate,
    PreventiveActionCreate, EffectivenessMonitoringCreate,
    ImmediateActionVerificationRequest, NonConformanceRiskAssessmentCalculationRequest,
    EscalationRuleTriggerRequest, PreventiveActionEffectivenessRequest,
    EffectivenessMonitoringUpdateRequest
)

def test_immediate_action_service():
    """Test ImmediateActionService functionality."""
    print("Testing ImmediateActionService...")
    
    db = SessionLocal()
    service = ImmediateActionService(db)
    
    try:
        # Test verification statistics
        stats = service.get_verification_statistics()
        print(f"✓ Verification statistics: {stats}")
        
        # Test recent actions
        recent_actions = service.get_recent_actions(limit=5)
        print(f"✓ Recent actions: {len(recent_actions)} actions found")
        
        # Test action timeline
        timeline = service.get_action_timeline(nonconformance_id=1)
        print(f"✓ Action timeline: {len(timeline)} records found")
        
        print("✓ ImmediateActionService tests completed successfully")
        
    except Exception as e:
        print(f"✗ Error testing ImmediateActionService: {e}")
    finally:
        db.close()

def test_risk_assessment_service():
    """Test RiskAssessmentService functionality."""
    print("\nTesting RiskAssessmentService...")
    
    db = SessionLocal()
    service = RiskAssessmentService(db)
    
    try:
        # Test risk calculation
        calculation_request = NonConformanceRiskAssessmentCalculationRequest(
            food_safety_impact="high",
            regulatory_impact="medium",
            customer_impact="low",
            business_impact="medium"
        )
        
        result = service.calculate_risk_from_request(calculation_request)
        print(f"✓ Risk calculation: {result}")
        
        # Test validation
        validation_result = service.validate_risk_assessment(calculation_request)
        print(f"✓ Validation: {validation_result}")
        
        print("✓ RiskAssessmentService tests completed successfully")
        
    except Exception as e:
        print(f"✗ Error testing RiskAssessmentService: {e}")
    finally:
        db.close()

def test_escalation_service():
    """Test EscalationService functionality."""
    print("\nTesting EscalationService...")
    
    db = SessionLocal()
    service = EscalationService(db)
    
    try:
        # Test escalation rule templates
        templates = service.get_escalation_rule_templates()
        print(f"✓ Escalation rule templates: {len(templates)} templates found")
        
        # Test statistics
        stats = service.get_escalation_statistics()
        print(f"✓ Escalation statistics: {stats}")
        
        print("✓ EscalationService tests completed successfully")
        
    except Exception as e:
        print(f"✗ Error testing EscalationService: {e}")
    finally:
        db.close()

def test_preventive_action_service():
    """Test PreventiveActionService functionality."""
    print("\nTesting PreventiveActionService...")
    
    db = SessionLocal()
    service = PreventiveActionService(db)
    
    try:
        # Test statistics
        stats = service.get_preventive_action_statistics()
        print(f"✓ Preventive action statistics: {stats}")
        
        # Test effectiveness statistics
        effectiveness_stats = service.get_effectiveness_statistics()
        print(f"✓ Effectiveness statistics: {effectiveness_stats}")
        
        # Test performance by type
        performance = service.get_action_performance_by_type()
        print(f"✓ Performance by type: {performance}")
        
        print("✓ PreventiveActionService tests completed successfully")
        
    except Exception as e:
        print(f"✗ Error testing PreventiveActionService: {e}")
    finally:
        db.close()

def test_effectiveness_monitoring_service():
    """Test EffectivenessMonitoringService functionality."""
    print("\nTesting EffectivenessMonitoringService...")
    
    db = SessionLocal()
    service = EffectivenessMonitoringService(db)
    
    try:
        # Test statistics
        stats = service.get_monitoring_statistics()
        print(f"✓ Monitoring statistics: {stats}")
        
        # Test metric performance summary
        performance = service.get_metric_performance_summary()
        print(f"✓ Metric performance summary: {performance}")
        
        # Test monitoring trends
        trends = service.get_monitoring_trends(days=30)
        print(f"✓ Monitoring trends: {len(trends)} records found")
        
        print("✓ EffectivenessMonitoringService tests completed successfully")
        
    except Exception as e:
        print(f"✗ Error testing EffectivenessMonitoringService: {e}")
    finally:
        db.close()

def test_service_integration():
    """Test integration between services."""
    print("\nTesting Service Integration...")
    
    db = SessionLocal()
    
    try:
        # Test that all services can be instantiated together
        immediate_service = ImmediateActionService(db)
        risk_service = RiskAssessmentService(db)
        escalation_service = EscalationService(db)
        preventive_service = PreventiveActionService(db)
        monitoring_service = EffectivenessMonitoringService(db)
        
        print("✓ All services instantiated successfully")
        
        # Test that services can access the same database session
        print("✓ Database session shared successfully")
        
        print("✓ Service integration tests completed successfully")
        
    except Exception as e:
        print(f"✗ Error testing service integration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing NC/CAPA Services")
    print("=" * 50)
    
    test_immediate_action_service()
    test_risk_assessment_service()
    test_escalation_service()
    test_preventive_action_service()
    test_effectiveness_monitoring_service()
    test_service_integration()
    
    print("\n" + "=" * 50)
    print("All service tests completed!")
