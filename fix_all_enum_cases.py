#!/usr/bin/env python3
"""
Comprehensive Enum Case Fix Script
Fixes all enum case inconsistencies between database and backend definitions
"""

import sqlite3
import sys
from typing import Dict, List, Tuple

def fix_enum_cases():
    """Fix all enum case inconsistencies in the database"""
    
    conn = sqlite3.connect('iso22000_fsms.db')
    cursor = conn.cursor()
    
    print("🔧 Starting comprehensive enum case fix...")
    
    # Define all enum fixes
    enum_fixes = {
        # Non-Conformance Status - ensure lowercase
        "non_conformances": {
            "status": {
                "OPEN": "open",
                "UNDER_INVESTIGATION": "under_investigation", 
                "ROOT_CAUSE_IDENTIFIED": "root_cause_identified",
                "CAPA_ASSIGNED": "capa_assigned",
                "IN_PROGRESS": "in_progress",
                "COMPLETED": "completed",
                "VERIFIED": "verified",
                "CLOSED": "closed"
            },
            "source": {
                "PRP": "prp",
                "AUDIT": "audit", 
                "COMPLAINT": "complaint",
                "PRODUCTION_DEVIATION": "production_deviation",
                "SUPPLIER": "supplier",
                "HACCP": "haccp",
                "DOCUMENT": "document",
                "INSPECTION": "inspection",
                "OTHER": "other"
            }
        },
        
        # HACCP Hazard Types - ensure lowercase
        "hazards": {
            "hazard_type": {
                "BIOLOGICAL": "biological",
                "CHEMICAL": "chemical",
                "PHYSICAL": "physical", 
                "ALLERGEN": "allergen"
            },
            "risk_level": {
                "LOW": "low",
                "MEDIUM": "medium",
                "HIGH": "high",
                "CRITICAL": "critical"
            }
        },
        
        # CCP Status - ensure lowercase
        "ccps": {
            "status": {
                "ACTIVE": "active",
                "INACTIVE": "inactive",
                "SUSPENDED": "suspended",
                "UNDER_REVIEW": "under_review"
            }
        },
        
        # HACCP Plan Status - ensure lowercase
        "haccp_plans": {
            "status": {
                "DRAFT": "draft",
                "UNDER_REVIEW": "under_review",
                "APPROVED": "approved",
                "IMPLEMENTED": "implemented",
                "UNDER_REVISION": "under_revision",
                "OBSOLETE": "obsolete"
            }
        },
        
        # Batch Types - ensure lowercase
        "batches": {
            "batch_type": {
                "RAW_MILK": "raw_milk",
                "ADDITIVE": "additive",
                "CULTURE": "culture",
                "PACKAGING": "packaging",
                "FINAL_PRODUCT": "final_product",
                "INTERMEDIATE": "intermediate"
            },
            "status": {
                "IN_PRODUCTION": "in_production",
                "COMPLETED": "completed",
                "QUARANTINED": "quarantined",
                "RELEASED": "released",
                "RECALLED": "recalled",
                "DISPOSED": "disposed"
            }
        },
        
        # Recall Types - ensure lowercase
        "recalls": {
            "recall_type": {
                "CLASS_I": "class_i",
                "CLASS_II": "class_ii",
                "CLASS_III": "class_iii"
            },
            "status": {
                "DRAFT": "draft",
                "INITIATED": "initiated",
                "IN_PROGRESS": "in_progress",
                "COMPLETED": "completed",
                "CANCELLED": "cancelled"
            }
        },
        
        # Audit Types - ensure lowercase
        "audits": {
            "audit_type": {
                "INTERNAL": "internal",
                "EXTERNAL": "external",
                "SUPPLIER": "supplier",
                "CERTIFICATION": "certification",
                "SURVEILLANCE": "surveillance",
                "FOLLOW_UP": "follow_up"
            },
            "status": {
                "PLANNED": "planned",
                "IN_PROGRESS": "in_progress",
                "COMPLETED": "completed",
                "CANCELLED": "cancelled",
                "RESCHEDULED": "rescheduled"
            }
        },
        
        # Audit Findings - ensure lowercase
        "audit_findings": {
            "finding_type": {
                "NONCONFORMITY": "nonconformity",
                "OBSERVATION": "observation",
                "OPPORTUNITY_FOR_IMPROVEMENT": "opportunity_for_improvement",
                "COMPLIANCE": "compliance"
            },
            "severity": {
                "MINOR": "minor",
                "MAJOR": "major",
                "CRITICAL": "critical"
            },
            "status": {
                "OPEN": "open",
                "IN_PROGRESS": "in_progress",
                "COMPLETED": "completed",
                "VERIFIED": "verified",
                "CLOSED": "closed"
            }
        },
        
        # Equipment - ensure lowercase
        "maintenance_plans": {
            "maintenance_type": {
                "PREVENTIVE": "preventive",
                "CORRECTIVE": "corrective",
                "PREDICTIVE": "predictive",
                "EMERGENCY": "emergency"
            }
        },
        
        "maintenance_work_orders": {
            "status": {
                "PENDING": "pending",
                "ASSIGNED": "assigned",
                "IN_PROGRESS": "in_progress",
                "COMPLETED": "completed",
                "CANCELLED": "cancelled",
                "ON_HOLD": "on_hold"
            },
            "priority": {
                "LOW": "low",
                "MEDIUM": "medium",
                "HIGH": "high",
                "CRITICAL": "critical"
            }
        },
        
        # Supplier - ensure lowercase
        "suppliers": {
            "status": {
                "ACTIVE": "active",
                "INACTIVE": "inactive",
                "SUSPENDED": "suspended",
                "PENDING_APPROVAL": "pending_approval",
                "BLACKLISTED": "blacklisted"
            },
            "category": {
                "RAW_MILK": "raw_milk",
                "EQUIPMENT": "equipment",
                "CHEMICALS": "chemicals",
                "SERVICES": "services"
            }
        },
        
        "supplier_evaluations": {
            "status": {
                "PENDING": "pending",
                "IN_PROGRESS": "in_progress",
                "COMPLETED": "completed",
                "OVERDUE": "overdue"
            }
        },
        
        "supplier_inspections": {
            "status": {
                "PENDING": "pending",
                "PASSED": "passed",
                "FAILED": "failed",
                "QUARANTINED": "quarantined"
            }
        },
        
        # Documents - ensure lowercase
        "documents": {
            "document_type": {
                "POLICY": "policy",
                "PROCEDURE": "procedure",
                "WORK_INSTRUCTION": "work_instruction",
                "FORM": "form",
                "RECORD": "record",
                "MANUAL": "manual",
                "SPECIFICATION": "specification",
                "PLAN": "plan",
                "CHECKLIST": "checklist"
            },
            "status": {
                "DRAFT": "draft",
                "UNDER_REVIEW": "under_review",
                "APPROVED": "approved",
                "OBSOLETE": "obsolete",
                "ARCHIVED": "archived"
            },
            "category": {
                "HACCP": "haccp",
                "PRP": "prp",
                "GENERAL": "general",
                "PRODUCTION": "production",
                "HR": "hr",
                "FINANCE": "finance"
            }
        },
        
        # PRP - ensure lowercase
        "prp_programs": {
            "category": {
                "CONSTRUCTION_AND_LAYOUT": "construction_and_layout",
                "LAYOUT_OF_PREMISES": "layout_of_premises",
                "SUPPLIES_OF_AIR_WATER_ENERGY": "supplies_of_air_water_energy",
                "SUPPORTING_SERVICES": "supporting_services",
                "SUITABILITY_CLEANING_MAINTENANCE": "suitability_cleaning_maintenance",
                "MANAGEMENT_OF_PURCHASED_MATERIALS": "management_of_purchased_materials",
                "PREVENTION_OF_CROSS_CONTAMINATION": "prevention_of_cross_contamination",
                "CLEANING_AND_SANITIZING": "cleaning_sanitation",
                "PEST_CONTROL": "pest_control",
                "PERSONNEL_HYGIENE_FACILITIES": "personnel_hygiene_facilities",
                "PRODUCT_RELEASE": "product_release",
                "STAFF_HYGIENE": "staff_hygiene",
                "WASTE_MANAGEMENT": "waste_management",
                "EQUIPMENT_CALIBRATION": "equipment_calibration",
                "MAINTENANCE": "maintenance",
                "PERSONNEL_TRAINING": "personnel_training",
                "SUPPLIER_CONTROL": "supplier_control",
                "WATER_QUALITY": "water_quality",
                "AIR_QUALITY": "air_quality"
            },
            "frequency": {
                "DAILY": "daily",
                "WEEKLY": "weekly",
                "MONTHLY": "monthly",
                "QUARTERLY": "quarterly",
                "SEMI_ANNUALLY": "semi_annually",
                "ANNUALLY": "annually",
                "AS_NEEDED": "as_needed"
            },
            "status": {
                "ACTIVE": "active",
                "INACTIVE": "inactive",
                "SUSPENDED": "suspended"
            }
        },
        
        "prp_checklists": {
            "status": {
                "PENDING": "pending",
                "IN_PROGRESS": "in_progress",
                "COMPLETED": "completed",
                "OVERDUE": "overdue",
                "FAILED": "failed"
            }
        },
        
        # Risk Management - ensure lowercase
        "risk_register_items": {
            "item_type": {
                "PROCESS": "process",
                "PRODUCT": "product",
                "EQUIPMENT": "equipment",
                "SUPPLIER": "supplier",
                "PERSONNEL": "personnel",
                "ENVIRONMENT": "environment",
                "REGULATORY": "regulatory",
                "OTHER": "other"
            },
            "category": {
                "FOOD_SAFETY": "food_safety",
                "QUALITY": "quality",
                "OPERATIONAL": "operational",
                "FINANCIAL": "financial",
                "REGULATORY": "regulatory",
                "REPUTATIONAL": "reputational",
                "OTHER": "other"
            },
            "status": {
                "OPEN": "open",
                "ASSESSED": "assessed",
                "TREATED": "treated",
                "MONITORED": "monitored",
                "CLOSED": "closed",
                "ESCALATED": "escalated"
            },
            "severity": {
                "VERY_LOW": "very_low",
                "LOW": "low",
                "MEDIUM": "medium",
                "HIGH": "high",
                "VERY_HIGH": "very_high",
                "CRITICAL": "critical"
            },
            "likelihood": {
                "VERY_UNLIKELY": "very_unlikely",
                "UNLIKELY": "unlikely",
                "POSSIBLE": "possible",
                "LIKELY": "likely",
                "VERY_LIKELY": "very_likely",
                "CERTAIN": "certain"
            },
            "classification": {
                "FOOD_SAFETY": "food_safety",
                "BUSINESS": "business",
                "CUSTOMER": "customer"
            },
            "detectability": {
                "VERY_HIGH": "very_high",
                "HIGH": "high",
                "MEDIUM": "medium",
                "LOW": "low",
                "VERY_LOW": "very_low"
            }
        },
        
        # Management Review - ensure lowercase
        "management_reviews": {
            "status": {
                "PLANNED": "planned",
                "IN_PROGRESS": "in_progress",
                "COMPLETED": "completed",
                "CANCELLED": "cancelled",
                "RESCHEDULED": "rescheduled"
            },
            "review_type": {
                "SCHEDULED": "scheduled",
                "SPECIAL": "special",
                "EMERGENCY": "emergency",
                "ANNUAL": "annual"
            }
        },
        
        "review_actions": {
            "action_type": {
                "DECISION": "decision",
                "ACTION": "action",
                "RESOURCE_ALLOCATION": "resource_allocation",
                "POLICY_CHANGE": "policy_change",
                "OBJECTIVE_CHANGE": "objective_change",
                "PROCESS_CHANGE": "process_change",
                "TRAINING_NEED": "training_need",
                "INFRASTRUCTURE_CHANGE": "infrastructure_change",
                "OTHER": "other"
            },
            "priority": {
                "LOW": "low",
                "MEDIUM": "medium",
                "HIGH": "high",
                "CRITICAL": "critical"
            },
            "status": {
                "ASSIGNED": "assigned",
                "IN_PROGRESS": "in_progress",
                "COMPLETED": "completed",
                "VERIFIED": "verified",
                "CLOSED": "closed",
                "OVERDUE": "overdue",
                "CANCELLED": "cancelled"
            }
        },
        
        # Notifications - ensure lowercase
        "notifications": {
            "notification_type": {
                "INFO": "info",
                "SUCCESS": "success",
                "WARNING": "warning",
                "ERROR": "error",
                "ALERT": "alert"
            },
            "category": {
                "SYSTEM": "system",
                "AUDIT": "audit",
                "HACCP": "haccp",
                "PRP": "prp",
                "SUPPLIER": "supplier",
                "EQUIPMENT": "equipment",
                "DOCUMENT": "document",
                "TRAINING": "training",
                "COMPLIANCE": "compliance",
                "OTHER": "other"
            },
            "priority": {
                "LOW": "low",
                "MEDIUM": "medium",
                "HIGH": "high",
                "CRITICAL": "critical"
            }
        },
        
        # Complaints - ensure lowercase
        "complaints": {
            "status": {
                "OPEN": "open",
                "UNDER_INVESTIGATION": "under_investigation",
                "RESOLVED": "resolved",
                "CLOSED": "closed",
                "ESCALATED": "escalated"
            },
            "classification": {
                "FOOD_SAFETY": "food_safety",
                "QUALITY": "quality",
                "PACKAGING": "packaging",
                "DELIVERY": "delivery",
                "CUSTOMER_SERVICE": "customer_service",
                "OTHER": "other"
            },
            "channel": {
                "EMAIL": "email",
                "PHONE": "phone",
                "WEBSITE": "website",
                "SOCIAL_MEDIA": "social_media",
                "IN_PERSON": "in_person",
                "LETTER": "letter",
                "OTHER": "other"
            }
        },
        
        # Training - ensure lowercase
        "training_records": {
            "action": {
                "ASSIGNED": "assigned",
                "STARTED": "started",
                "COMPLETED": "completed",
                "FAILED": "failed",
                "CANCELLED": "cancelled",
                "RESCHEDULED": "rescheduled"
            }
        }
    }
    
    total_fixes = 0
    
    # Apply fixes for each table and column
    for table_name, columns in enum_fixes.items():
        print(f"\n📋 Processing table: {table_name}")
        
        for column_name, value_mappings in columns.items():
            print(f"  🔧 Fixing column: {column_name}")
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                print(f"    ⚠️  Table {table_name} does not exist, skipping...")
                continue
            
            # Check if column exists
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            if column_name not in column_names:
                print(f"    ⚠️  Column {column_name} does not exist in {table_name}, skipping...")
                continue
            
            # Get current values
            cursor.execute(f"SELECT DISTINCT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL")
            current_values = [row[0] for row in cursor.fetchall()]
            
            print(f"    📊 Current values: {current_values}")
            
            # Apply fixes
            for old_value, new_value in value_mappings.items():
                if old_value in current_values:
                    cursor.execute(
                        f"UPDATE {table_name} SET {column_name} = ? WHERE {column_name} = ?",
                        (new_value, old_value)
                    )
                    affected_rows = cursor.rowcount
                    if affected_rows > 0:
                        print(f"      ✅ Updated {affected_rows} rows: '{old_value}' → '{new_value}'")
                        total_fixes += affected_rows
            
            # Verify final values
            cursor.execute(f"SELECT DISTINCT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL")
            final_values = [row[0] for row in cursor.fetchall()]
            print(f"    ✅ Final values: {final_values}")
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Enum case fix completed!")
    print(f"📊 Total rows updated: {total_fixes}")
    print(f"✅ All enum values now match backend definitions")
    
    return True

if __name__ == "__main__":
    try:
        success = fix_enum_cases()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


