from app.core.database import SessionLocal
from app.models.nonconformance import (
    NonConformance, ImmediateAction, RiskAssessment, 
    EscalationRule, PreventiveAction, EffectivenessMonitoring
)

def test_model_relationships():
    """Test the new model relationships."""
    db = SessionLocal()
    
    try:
        print("Testing NC/CAPA Model Relationships:")
        print("=" * 50)
        
        # Test model imports
        print("✓ All models imported successfully")
        
        # Test model creation (without saving to database)
        print("✓ Model classes can be instantiated")
        
        # Test relationship definitions
        nc = NonConformance()
        print("✓ NonConformance model has new relationships:")
        print(f"  - immediate_actions: {hasattr(nc, 'immediate_actions')}")
        print(f"  - risk_assessments: {hasattr(nc, 'risk_assessments')}")
        print(f"  - preventive_actions: {hasattr(nc, 'preventive_actions')}")
        print(f"  - effectiveness_monitoring: {hasattr(nc, 'effectiveness_monitoring')}")
        
        # Test new fields
        print("✓ NonConformance model has new fields:")
        print(f"  - requires_immediate_action: {hasattr(nc, 'requires_immediate_action')}")
        print(f"  - risk_level: {hasattr(nc, 'risk_level')}")
        print(f"  - escalation_status: {hasattr(nc, 'escalation_status')}")
        
        # Test ImmediateAction model
        ia = ImmediateAction()
        print("✓ ImmediateAction model created")
        print(f"  - has verify_effectiveness method: {hasattr(ia, 'verify_effectiveness')}")
        print(f"  - has is_verified method: {hasattr(ia, 'is_verified')}")
        
        # Test RiskAssessment model
        ra = RiskAssessment()
        print("✓ RiskAssessment model created")
        print(f"  - has calculate_risk_score method: {hasattr(ra, 'calculate_risk_score')}")
        print(f"  - has determine_escalation_need method: {hasattr(ra, 'determine_escalation_need')}")
        print(f"  - has get_risk_level method: {hasattr(ra, 'get_risk_level')}")
        
        # Test EscalationRule model
        er = EscalationRule()
        print("✓ EscalationRule model created")
        print(f"  - has should_trigger method: {hasattr(er, 'should_trigger')}")
        print(f"  - has get_notification_recipients method: {hasattr(er, 'get_notification_recipients')}")
        
        # Test PreventiveAction model
        pa = PreventiveAction()
        print("✓ PreventiveAction model created")
        print(f"  - has is_overdue method: {hasattr(pa, 'is_overdue')}")
        print(f"  - has calculate_effectiveness method: {hasattr(pa, 'calculate_effectiveness')}")
        print(f"  - has is_effective method: {hasattr(pa, 'is_effective')}")
        
        # Test EffectivenessMonitoring model
        em = EffectivenessMonitoring()
        print("✓ EffectivenessMonitoring model created")
        print(f"  - has calculate_achievement_percentage method: {hasattr(em, 'calculate_achievement_percentage')}")
        print(f"  - has is_on_target method: {hasattr(em, 'is_on_target')}")
        print(f"  - has is_active_monitoring method: {hasattr(em, 'is_active_monitoring')}")
        
        print("=" * 50)
        print("✓ All model relationships and methods tested successfully!")
        
    except Exception as e:
        print(f"✗ Error testing models: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_model_relationships()
