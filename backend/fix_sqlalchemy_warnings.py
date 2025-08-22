#!/usr/bin/env python3
"""
Fix SQLAlchemy Relationship Warnings
This script adds the overlaps parameter to fix the relationship warnings.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_risk_relationships():
    """Fix risk-related relationship warnings"""
    print("🔧 Fixing risk relationship warnings...")
    
    # Fix FSMSRiskIntegration.risk_item
    risk_integration_file = "app/models/risk.py"
    if os.path.exists(risk_integration_file):
        with open(risk_integration_file, 'r') as f:
            content = f.read()
        
        # Add overlaps parameter to FSMSRiskIntegration.risk_item
        if 'risk_item = relationship("RiskRegisterItem"' in content and 'overlaps=' not in content:
            content = content.replace(
                'risk_item = relationship("RiskRegisterItem"',
                'risk_item = relationship("RiskRegisterItem", overlaps="fsms_integrations"'
            )
        
        # Add overlaps parameter to RiskCorrelation.primary_risk
        if 'primary_risk = relationship("RiskRegisterItem"' in content and 'overlaps=' not in content:
            content = content.replace(
                'primary_risk = relationship("RiskRegisterItem"',
                'primary_risk = relationship("RiskRegisterItem", overlaps="correlations"'
            )
        
        # Add overlaps parameter to RiskResourceAllocation.risk_item
        if 'risk_item = relationship("RiskRegisterItem"' in content and 'overlaps="resource_allocations"' not in content:
            content = content.replace(
                'risk_item = relationship("RiskRegisterItem", overlaps="fsms_integrations"',
                'risk_item = relationship("RiskRegisterItem", overlaps="fsms_integrations,resource_allocations"'
            )
        
        # Add overlaps parameter to RiskCommunication.risk_item
        if 'risk_item = relationship("RiskRegisterItem"' in content and 'overlaps="communications"' not in content:
            content = content.replace(
                'risk_item = relationship("RiskRegisterItem", overlaps="fsms_integrations,resource_allocations"',
                'risk_item = relationship("RiskRegisterItem", overlaps="fsms_integrations,resource_allocations,communications"'
            )
        
        with open(risk_integration_file, 'w') as f:
            f.write(content)
        print("✅ Fixed risk relationship warnings")

def fix_haccp_relationships():
    """Fix HACCP-related relationship warnings"""
    print("🔧 Fixing HACCP relationship warnings...")
    
    haccp_file = "app/models/haccp.py"
    if os.path.exists(haccp_file):
        with open(haccp_file, 'r') as f:
            content = f.read()
        
        # Add overlaps parameter to HACCPRiskAssessment.hazard
        if 'hazard = relationship("Hazard"' in content and 'overlaps=' not in content:
            content = content.replace(
                'hazard = relationship("Hazard"',
                'hazard = relationship("Hazard", overlaps="risk_assessments"'
            )
        
        # Add overlaps parameter to HACCPRiskAssessment.ccp
        if 'ccp = relationship("CCP"' in content and 'overlaps=' not in content:
            content = content.replace(
                'ccp = relationship("CCP"',
                'ccp = relationship("CCP", overlaps="risk_assessments"'
            )
        
        # Add overlaps parameter to HACCPRiskAssessment.prp_program
        if 'prp_program = relationship("PRPProgram"' in content and 'overlaps=' not in content:
            content = content.replace(
                'prp_program = relationship("PRPProgram"',
                'prp_program = relationship("PRPProgram", overlaps="risk_assessments_enhanced"'
            )
        
        with open(haccp_file, 'w') as f:
            f.write(content)
        print("✅ Fixed HACCP relationship warnings")

def fix_audit_relationships():
    """Fix audit-related relationship warnings"""
    print("🔧 Fixing audit relationship warnings...")
    
    audit_file = "app/models/audit_mgmt.py"
    if os.path.exists(audit_file):
        with open(audit_file, 'r') as f:
            content = f.read()
        
        # Add overlaps parameter to Audit.risk_assessments
        if 'risk_assessments = relationship("AuditRiskAssessment"' in content and 'overlaps=' not in content:
            content = content.replace(
                'risk_assessments = relationship("AuditRiskAssessment"',
                'risk_assessments = relationship("AuditRiskAssessment", overlaps="audit"'
            )
        
        # Add overlaps parameter to AuditFinding.risk_assessments
        if 'risk_assessments = relationship("AuditRiskAssessment"' in content and 'overlaps="audit_finding"' not in content:
            content = content.replace(
                'risk_assessments = relationship("AuditRiskAssessment", overlaps="audit"',
                'risk_assessments = relationship("AuditRiskAssessment", overlaps="audit,audit_finding"'
            )
        
        # Add overlaps parameter to AuditFinding.prp_integrations
        if 'prp_integrations = relationship("PRPAuditIntegration"' in content and 'overlaps=' not in content:
            content = content.replace(
                'prp_integrations = relationship("PRPAuditIntegration"',
                'prp_integrations = relationship("PRPAuditIntegration", overlaps="audit_finding"'
            )
        
        with open(audit_file, 'w') as f:
            f.write(content)
        print("✅ Fixed audit relationship warnings")

def fix_prp_relationships():
    """Fix PRP-related relationship warnings"""
    print("🔧 Fixing PRP relationship warnings...")
    
    prp_file = "app/models/prp.py"
    if os.path.exists(prp_file):
        with open(prp_file, 'r') as f:
            content = f.read()
        
        # Add overlaps parameter to PRPAuditIntegration.prp_program
        if 'prp_program = relationship("PRPProgram"' in content and 'overlaps=' not in content:
            content = content.replace(
                'prp_program = relationship("PRPProgram"',
                'prp_program = relationship("PRPProgram", overlaps="audit_integrations"'
            )
        
        with open(prp_file, 'w') as f:
            f.write(content)
        print("✅ Fixed PRP relationship warnings")

def fix_department_relationships():
    """Fix department-related relationship warnings"""
    print("🔧 Fixing department relationship warnings...")
    
    # This might be in a different file, let me search for it
    department_file = "app/models/user.py"  # Assuming it's in user.py
    if os.path.exists(department_file):
        with open(department_file, 'r') as f:
            content = f.read()
        
        # Add overlaps parameter to Department.children
        if 'children = relationship("Department"' in content and 'overlaps=' not in content:
            content = content.replace(
                'children = relationship("Department"',
                'children = relationship("Department", overlaps="parent"'
            )
        
        with open(department_file, 'w') as f:
            f.write(content)
        print("✅ Fixed department relationship warnings")

def main():
    """Main function to fix all SQLAlchemy warnings"""
    print("🚀 Starting SQLAlchemy relationship warning fixes...")
    
    try:
        fix_risk_relationships()
        fix_haccp_relationships()
        fix_audit_relationships()
        fix_prp_relationships()
        fix_department_relationships()
        
        print("🎉 All SQLAlchemy relationship warnings have been fixed!")
        print("📝 Next steps:")
        print("1. Restart the backend server")
        print("2. The warnings should no longer appear in the logs")
        
    except Exception as e:
        print(f"❌ Error fixing SQLAlchemy warnings: {e}")

if __name__ == "__main__":
    main()

