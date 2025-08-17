from datetime import datetime, timedelta
from app.schemas.nonconformance import (
    ImmediateActionCreate, RiskAssessmentCreate, EscalationRuleCreate,
    PreventiveActionCreate, EffectivenessMonitoringCreate,
    ImmediateActionVerificationRequest, RiskAssessmentCalculationRequest
)

def test_immediate_action_schemas():
    """Test ImmediateAction schemas and validation."""
    print("Testing ImmediateAction schemas...")
    
    # Test valid data
    try:
        valid_data = {
            "non_conformance_id": 1,
            "action_type": "containment",
            "description": "This is a detailed description of the immediate action",
            "implemented_by": 1,
            "implemented_at": datetime.now()
        }
        action = ImmediateActionCreate(**valid_data)
        print("✓ Valid ImmediateActionCreate created successfully")
    except Exception as e:
        print(f"✗ Error creating valid ImmediateActionCreate: {e}")
    
    # Test invalid action_type
    try:
        invalid_data = valid_data.copy()
        invalid_data["action_type"] = "invalid_type"
        action = ImmediateActionCreate(**invalid_data)
        print("✗ Should have failed for invalid action_type")
    except ValueError as e:
        print(f"✓ Correctly caught invalid action_type: {e}")
    
    # Test short description
    try:
        invalid_data = valid_data.copy()
        invalid_data["description"] = "Short"
        action = ImmediateActionCreate(**invalid_data)
        print("✗ Should have failed for short description")
    except ValueError as e:
        print(f"✓ Correctly caught short description: {e}")


def test_risk_assessment_schemas():
    """Test RiskAssessment schemas and validation."""
    print("\nTesting RiskAssessment schemas...")
    
    # Test valid data
    try:
        valid_data = {
            "non_conformance_id": 1,
            "food_safety_impact": "high",
            "regulatory_impact": "medium",
            "customer_impact": "low",
            "business_impact": "medium",
            "overall_risk_score": 2.5,
            "risk_matrix_position": "B2",
            "requires_escalation": False,
            "escalation_level": None
        }
        assessment = RiskAssessmentCreate(**valid_data)
        print("✓ Valid RiskAssessmentCreate created successfully")
    except Exception as e:
        print(f"✗ Error creating valid RiskAssessmentCreate: {e}")
    
    # Test invalid impact level
    try:
        invalid_data = valid_data.copy()
        invalid_data["food_safety_impact"] = "invalid"
        assessment = RiskAssessmentCreate(**invalid_data)
        print("✗ Should have failed for invalid impact level")
    except ValueError as e:
        print(f"✓ Correctly caught invalid impact level: {e}")
    
    # Test invalid risk score
    try:
        invalid_data = valid_data.copy()
        invalid_data["overall_risk_score"] = 5.0
        assessment = RiskAssessmentCreate(**invalid_data)
        print("✗ Should have failed for invalid risk score")
    except ValueError as e:
        print(f"✓ Correctly caught invalid risk score: {e}")


def test_escalation_rule_schemas():
    """Test EscalationRule schemas and validation."""
    print("\nTesting EscalationRule schemas...")
    
    # Test valid data
    try:
        valid_data = {
            "rule_name": "High Risk Escalation",
            "rule_description": "Escalate when risk score is high",
            "trigger_condition": "risk_score",
            "trigger_value": 3.0,
            "escalation_level": "manager",
            "notification_recipients": '["user1@example.com", "user2@example.com"]',
            "escalation_timeframe": 24,
            "is_active": True
        }
        rule = EscalationRuleCreate(**valid_data)
        print("✓ Valid EscalationRuleCreate created successfully")
    except Exception as e:
        print(f"✗ Error creating valid EscalationRuleCreate: {e}")
    
    # Test invalid trigger condition
    try:
        invalid_data = valid_data.copy()
        invalid_data["trigger_condition"] = "invalid"
        rule = EscalationRuleCreate(**invalid_data)
        print("✗ Should have failed for invalid trigger condition")
    except ValueError as e:
        print(f"✓ Correctly caught invalid trigger condition: {e}")


def test_preventive_action_schemas():
    """Test PreventiveAction schemas and validation."""
    print("\nTesting PreventiveAction schemas...")
    
    # Test valid data
    try:
        valid_data = {
            "non_conformance_id": 1,
            "action_title": "Implement new training program",
            "action_description": "This is a detailed description of the preventive action that will be implemented",
            "action_type": "training",
            "priority": "high",
            "assigned_to": 1,
            "due_date": datetime.now() + timedelta(days=30),
            "status": "planned",
            "effectiveness_target": 95.0,
            "effectiveness_measured": None
        }
        action = PreventiveActionCreate(**valid_data)
        print("✓ Valid PreventiveActionCreate created successfully")
    except Exception as e:
        print(f"✗ Error creating valid PreventiveActionCreate: {e}")
    
    # Test invalid action type
    try:
        invalid_data = valid_data.copy()
        invalid_data["action_type"] = "invalid"
        action = PreventiveActionCreate(**invalid_data)
        print("✗ Should have failed for invalid action type")
    except ValueError as e:
        print(f"✓ Correctly caught invalid action type: {e}")


def test_effectiveness_monitoring_schemas():
    """Test EffectivenessMonitoring schemas and validation."""
    print("\nTesting EffectivenessMonitoring schemas...")
    
    # Test valid data
    try:
        valid_data = {
            "non_conformance_id": 1,
            "monitoring_period_start": datetime.now(),
            "monitoring_period_end": datetime.now() + timedelta(days=90),
            "metric_name": "Defect Rate",
            "metric_description": "Monitor defect rate reduction",
            "target_value": 2.0,
            "actual_value": None,
            "measurement_unit": "percentage",
            "measurement_frequency": "weekly",
            "measurement_method": "Statistical sampling",
            "status": "active",
            "achievement_percentage": None,
            "trend_analysis": None
        }
        monitoring = EffectivenessMonitoringCreate(**valid_data)
        print("✓ Valid EffectivenessMonitoringCreate created successfully")
    except Exception as e:
        print(f"✗ Error creating valid EffectivenessMonitoringCreate: {e}")
    
    # Test invalid measurement frequency
    try:
        invalid_data = valid_data.copy()
        invalid_data["measurement_frequency"] = "invalid"
        monitoring = EffectivenessMonitoringCreate(**invalid_data)
        print("✗ Should have failed for invalid measurement frequency")
    except ValueError as e:
        print(f"✓ Correctly caught invalid measurement frequency: {e}")


def test_specialized_request_schemas():
    """Test specialized request schemas."""
    print("\nTesting specialized request schemas...")
    
    # Test ImmediateActionVerificationRequest
    try:
        verification_data = {
            "verification_by": 1,
            "verification_date": datetime.now()
        }
        verification = ImmediateActionVerificationRequest(**verification_data)
        print("✓ Valid ImmediateActionVerificationRequest created successfully")
    except Exception as e:
        print(f"✗ Error creating ImmediateActionVerificationRequest: {e}")
    
    # Test RiskAssessmentCalculationRequest
    try:
        calculation_data = {
            "food_safety_impact": "high",
            "regulatory_impact": "medium",
            "customer_impact": "low",
            "business_impact": "medium"
        }
        calculation = RiskAssessmentCalculationRequest(**calculation_data)
        print("✓ Valid RiskAssessmentCalculationRequest created successfully")
    except Exception as e:
        print(f"✗ Error creating RiskAssessmentCalculationRequest: {e}")


if __name__ == "__main__":
    print("Testing NC/CAPA Pydantic Schemas")
    print("=" * 50)
    
    test_immediate_action_schemas()
    test_risk_assessment_schemas()
    test_escalation_rule_schemas()
    test_preventive_action_schemas()
    test_effectiveness_monitoring_schemas()
    test_specialized_request_schemas()
    
    print("\n" + "=" * 50)
    print("Schema testing completed!")

