#!/usr/bin/env python3
"""
PRP Data Migration Script - ISO 22002-1:2025 Compliance

This script migrates existing PRP data to the new enhanced PRP module
structure, ensuring data integrity and compliance with ISO 22002-1:2025.

Usage:
    python migrate_prp_data.py [--dry-run] [--backup] [--validate]
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.models.prp import (
    PRPProgram, PRPChecklist, PRPChecklistItem, RiskAssessment, 
    RiskControl, CorrectiveAction, PreventiveAction, RiskMatrix,
    PRPCategory, PRPFrequency, PRPStatus, RiskLevel, ChecklistStatus, CorrectiveActionStatus
)
from app.models.user import User
from app.core.database import Base, engine, SessionLocal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('prp_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PRPDataMigrator:
    """Handles migration of PRP data to the new enhanced structure"""
    
    def __init__(self, dry_run: bool = False, backup: bool = True, validate: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.validate = validate
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.migration_stats = {
            'programs_migrated': 0,
            'checklists_migrated': 0,
            'risk_assessments_migrated': 0,
            'corrective_actions_migrated': 0,
            'preventive_actions_migrated': 0,
            'errors': [],
            'warnings': []
        }
    
    def create_backup(self) -> bool:
        """Create backup of existing data"""
        try:
            logger.info("Creating backup of existing data...")
            
            if self.dry_run:
                logger.info("DRY RUN: Would create backup")
                return True
            
            # Create backup directory
            backup_dir = f"backup_prp_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Get all existing tables
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            # Backup each table
            for table in tables:
                if 'prp' in table.lower():
                    backup_file = os.path.join(backup_dir, f"{table}.json")
                    self._backup_table(table, backup_file)
            
            logger.info(f"Backup created in directory: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def _backup_table(self, table_name: str, backup_file: str):
        """Backup a single table to JSON file"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {table_name}"))
                rows = [dict(row._mapping) for row in result]
                
                with open(backup_file, 'w') as f:
                    json.dump(rows, f, indent=2, default=str)
                
                logger.info(f"Backed up {len(rows)} rows from {table_name}")
                
        except Exception as e:
            logger.error(f"Failed to backup table {table_name}: {e}")
    
    def validate_existing_data(self) -> bool:
        """Validate existing data structure and integrity"""
        try:
            logger.info("Validating existing data...")
            
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            # Check for required tables
            required_tables = ['prp_programs', 'prp_checklists']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")
                self.migration_stats['warnings'].append(f"Missing tables: {missing_tables}")
            
            # Validate data integrity
            with self.SessionLocal() as db:
                # Check for orphaned records
                self._validate_orphaned_records(db)
                
                # Check for data consistency
                self._validate_data_consistency(db)
            
            logger.info("Data validation completed")
            return len(self.migration_stats['errors']) == 0
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return False
    
    def _validate_orphaned_records(self, db):
        """Check for orphaned records"""
        try:
            # Check for checklists without programs
            orphaned_checklists = db.execute(text("""
                SELECT COUNT(*) FROM prp_checklists 
                WHERE program_id NOT IN (SELECT id FROM prp_programs)
            """)).scalar()
            
            if orphaned_checklists > 0:
                logger.warning(f"Found {orphaned_checklists} orphaned checklists")
                self.migration_stats['warnings'].append(f"Found {orphaned_checklists} orphaned checklists")
                
        except Exception as e:
            logger.error(f"Failed to validate orphaned records: {e}")
    
    def _validate_data_consistency(self, db):
        """Check data consistency"""
        try:
            # Check for invalid category values
            invalid_categories = db.execute(text("""
                SELECT DISTINCT category FROM prp_programs 
                WHERE category NOT IN (
                    'construction_and_layout', 'layout_of_premises', 'supplies_of_utilities',
                    'supporting_services', 'suitability_of_equipment', 'management_of_materials',
                    'prevention_of_cross_contamination', 'cleaning_and_sanitizing', 'pest_control',
                    'personnel_hygiene_facilities', 'personnel_hygiene_practices', 'reprocessing',
                    'product_recall_procedures', 'warehousing', 'product_information',
                    'food_defense', 'control_of_nonconforming_product', 'product_release'
                )
            """)).fetchall()
            
            if invalid_categories:
                logger.warning(f"Found invalid categories: {[cat[0] for cat in invalid_categories]}")
                self.migration_stats['warnings'].append(f"Invalid categories found: {[cat[0] for cat in invalid_categories]}")
                
        except Exception as e:
            logger.error(f"Failed to validate data consistency: {e}")
    
    def migrate_programs(self) -> bool:
        """Migrate existing PRP programs to new structure"""
        try:
            logger.info("Migrating PRP programs...")
            
            with self.SessionLocal() as db:
                # Get existing programs
                existing_programs = db.execute(text("""
                    SELECT * FROM prp_programs 
                    WHERE created_at IS NOT NULL
                """)).fetchall()
                
                for program_data in existing_programs:
                    try:
                        # Map old data to new structure
                        new_program = self._map_program_data(program_data)
                        
                        if not self.dry_run:
                            # Update existing program
                            db.execute(text("""
                                UPDATE prp_programs SET
                                    objective = :objective,
                                    scope = :scope,
                                    sop_reference = :sop_reference,
                                    frequency = :frequency,
                                    status = :status,
                                    assigned_to = :assigned_to,
                                    updated_at = :updated_at
                                WHERE id = :id
                            """), {
                                'objective': new_program.get('objective', 'Ensure compliance with PRP requirements'),
                                'scope': new_program.get('scope', 'Production area'),
                                'sop_reference': new_program.get('sop_reference', 'SOP-PRP-001'),
                                'frequency': new_program.get('frequency', 'daily'),
                                'status': new_program.get('status', 'active'),
                                'assigned_to': new_program.get('assigned_to'),
                                'updated_at': datetime.utcnow(),
                                'id': program_data.id
                            })
                        
                        self.migration_stats['programs_migrated'] += 1
                        logger.info(f"Migrated program: {program_data.program_code}")
                        
                    except Exception as e:
                        logger.error(f"Failed to migrate program {program_data.program_code}: {e}")
                        self.migration_stats['errors'].append(f"Program {program_data.program_code}: {e}")
                
                if not self.dry_run:
                    db.commit()
                
            logger.info(f"Successfully migrated {self.migration_stats['programs_migrated']} programs")
            return True
            
        except Exception as e:
            logger.error(f"Program migration failed: {e}")
            return False
    
    def _map_program_data(self, program_data) -> Dict[str, Any]:
        """Map old program data to new structure"""
        # Map old category values to new ISO 22002-1:2025 categories
        category_mapping = {
            'cleaning': 'cleaning_and_sanitizing',
            'sanitizing': 'cleaning_and_sanitizing',
            'pest': 'pest_control',
            'hygiene': 'personnel_hygiene_practices',
            'maintenance': 'suitability_of_equipment',
            'storage': 'warehousing',
            'transport': 'product_release',
            'supplier': 'management_of_materials'
        }
        
        old_category = getattr(program_data, 'category', 'cleaning_and_sanitizing')
        new_category = category_mapping.get(old_category.lower(), old_category)
        
        return {
            'objective': getattr(program_data, 'objective', 'Ensure compliance with PRP requirements'),
            'scope': getattr(program_data, 'scope', 'Production area'),
            'sop_reference': getattr(program_data, 'sop_reference', 'SOP-PRP-001'),
            'frequency': getattr(program_data, 'frequency', 'daily'),
            'status': getattr(program_data, 'status', 'active'),
            'assigned_to': getattr(program_data, 'assigned_to', None),
            'category': new_category
        }
    
    def migrate_checklists(self) -> bool:
        """Migrate existing PRP checklists to new structure"""
        try:
            logger.info("Migrating PRP checklists...")
            
            with self.SessionLocal() as db:
                # Get existing checklists
                existing_checklists = db.execute(text("""
                    SELECT * FROM prp_checklists 
                    WHERE created_at IS NOT NULL
                """)).fetchall()
                
                for checklist_data in existing_checklists:
                    try:
                        # Map old data to new structure
                        new_checklist = self._map_checklist_data(checklist_data)
                        
                        if not self.dry_run:
                            # Update existing checklist
                            db.execute(text("""
                                UPDATE prp_checklists SET
                                    checklist_code = :checklist_code,
                                    name = :name,
                                    description = :description,
                                    scheduled_date = :scheduled_date,
                                    due_date = :due_date,
                                    status = :status,
                                    assigned_to = :assigned_to,
                                    compliance_percentage = :compliance_percentage,
                                    updated_at = :updated_at
                                WHERE id = :id
                            """), {
                                'checklist_code': new_checklist.get('checklist_code'),
                                'name': new_checklist.get('name'),
                                'description': new_checklist.get('description'),
                                'scheduled_date': new_checklist.get('scheduled_date'),
                                'due_date': new_checklist.get('due_date'),
                                'status': new_checklist.get('status'),
                                'assigned_to': new_checklist.get('assigned_to'),
                                'compliance_percentage': new_checklist.get('compliance_percentage', 0.0),
                                'updated_at': datetime.utcnow(),
                                'id': checklist_data.id
                            })
                        
                        self.migration_stats['checklists_migrated'] += 1
                        logger.info(f"Migrated checklist: {checklist_data.id}")
                        
                    except Exception as e:
                        logger.error(f"Failed to migrate checklist {checklist_data.id}: {e}")
                        self.migration_stats['errors'].append(f"Checklist {checklist_data.id}: {e}")
                
                if not self.dry_run:
                    db.commit()
                
            logger.info(f"Successfully migrated {self.migration_stats['checklists_migrated']} checklists")
            return True
            
        except Exception as e:
            logger.error(f"Checklist migration failed: {e}")
            return False
    
    def _map_checklist_data(self, checklist_data) -> Dict[str, Any]:
        """Map old checklist data to new structure"""
        return {
            'checklist_code': getattr(checklist_data, 'checklist_code', f"CHK-{checklist_data.id:04d}"),
            'name': getattr(checklist_data, 'name', f"Checklist {checklist_data.id}"),
            'description': getattr(checklist_data, 'description', 'Migrated checklist'),
            'scheduled_date': getattr(checklist_data, 'scheduled_date', datetime.utcnow()),
            'due_date': getattr(checklist_data, 'due_date', datetime.utcnow() + timedelta(days=1)),
            'status': getattr(checklist_data, 'status', 'pending'),
            'assigned_to': getattr(checklist_data, 'assigned_to', None),
            'compliance_percentage': getattr(checklist_data, 'compliance_percentage', 0.0)
        }
    
    def create_default_risk_matrices(self) -> bool:
        """Create default risk matrices for the system"""
        try:
            logger.info("Creating default risk matrices...")
            
            with self.SessionLocal() as db:
                # Check if risk matrices already exist
                existing_matrices = db.execute(text("SELECT COUNT(*) FROM prp_risk_matrices")).scalar()
                
                if existing_matrices > 0:
                    logger.info("Risk matrices already exist, skipping creation")
                    return True
                
                # Create default risk matrix
                default_matrix = {
                    'matrix_name': 'Standard Risk Matrix',
                    'matrix_description': 'Default risk matrix for PRP assessments',
                    'likelihood_levels': ['Very Low', 'Low', 'Medium', 'High', 'Very High'],
                    'severity_levels': ['Very Low', 'Low', 'Medium', 'High', 'Very High'],
                    'risk_levels': {
                        'Very Low-Very Low': 'Very Low',
                        'Very Low-Low': 'Very Low',
                        'Very Low-Medium': 'Low',
                        'Very Low-High': 'Medium',
                        'Very Low-Very High': 'High',
                        'Low-Very Low': 'Very Low',
                        'Low-Low': 'Low',
                        'Low-Medium': 'Medium',
                        'Low-High': 'High',
                        'Low-Very High': 'High',
                        'Medium-Very Low': 'Low',
                        'Medium-Low': 'Medium',
                        'Medium-Medium': 'Medium',
                        'Medium-High': 'High',
                        'Medium-Very High': 'Very High',
                        'High-Very Low': 'Medium',
                        'High-Low': 'High',
                        'High-Medium': 'High',
                        'High-High': 'Very High',
                        'High-Very High': 'Very High',
                        'Very High-Very Low': 'High',
                        'Very High-Low': 'High',
                        'Very High-Medium': 'Very High',
                        'Very High-High': 'Very High',
                        'Very High-Very High': 'Critical'
                    },
                    'created_by': 1  # Default admin user
                }
                
                if not self.dry_run:
                    db.execute(text("""
                        INSERT INTO prp_risk_matrices (
                            matrix_name, matrix_description, likelihood_levels, 
                            severity_levels, risk_levels, created_by, created_at
                        ) VALUES (
                            :matrix_name, :matrix_description, :likelihood_levels,
                            :severity_levels, :risk_levels, :created_by, :created_at
                        )
                    """), {
                        **default_matrix,
                        'likelihood_levels': json.dumps(default_matrix['likelihood_levels']),
                        'severity_levels': json.dumps(default_matrix['severity_levels']),
                        'risk_levels': json.dumps(default_matrix['risk_levels']),
                        'created_at': datetime.utcnow()
                    })
                    db.commit()
                
                logger.info("Default risk matrix created successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create default risk matrices: {e}")
            return False
    
    def create_sample_data(self) -> bool:
        """Create sample data for testing and demonstration"""
        try:
            logger.info("Creating sample data...")
            
            if self.dry_run:
                logger.info("DRY RUN: Would create sample data")
                return True
            
            with self.SessionLocal() as db:
                # Create sample PRP programs for each category
                categories = [
                    'cleaning_and_sanitizing', 'pest_control', 'personnel_hygiene_practices',
                    'management_of_materials', 'warehousing', 'product_release'
                ]
                
                for i, category in enumerate(categories):
                    program = PRPProgram(
                        program_code=f"SAMPLE-{category.upper()}-{i+1:02d}",
                        name=f"Sample {category.replace('_', ' ').title()} Program",
                        description=f"Sample program for {category} demonstration",
                        category=category,
                        objective=f"Ensure proper {category.replace('_', ' ')}",
                        scope="Sample scope",
                        sop_reference=f"SOP-{category.upper()}-001",
                        frequency="daily",
                        status="active",
                        assigned_to=1,
                        created_by=1
                    )
                    db.add(program)
                
                db.commit()
                logger.info("Sample data created successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create sample data: {e}")
            return False
    
    def run_migration(self) -> bool:
        """Run the complete migration process"""
        try:
            logger.info("Starting PRP data migration...")
            
            # Step 1: Create backup
            if self.backup:
                if not self.create_backup():
                    logger.error("Backup creation failed, aborting migration")
                    return False
            
            # Step 2: Validate existing data
            if self.validate:
                if not self.validate_existing_data():
                    logger.warning("Data validation found issues, but continuing migration")
            
            # Step 3: Migrate programs
            if not self.migrate_programs():
                logger.error("Program migration failed")
                return False
            
            # Step 4: Migrate checklists
            if not self.migrate_checklists():
                logger.error("Checklist migration failed")
                return False
            
            # Step 5: Create default risk matrices
            if not self.create_default_risk_matrices():
                logger.error("Risk matrix creation failed")
                return False
            
            # Step 6: Create sample data (optional)
            if not self.dry_run:
                self.create_sample_data()
            
            # Step 7: Print migration summary
            self._print_migration_summary()
            
            logger.info("PRP data migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def _print_migration_summary(self):
        """Print migration summary"""
        logger.info("=" * 50)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Programs migrated: {self.migration_stats['programs_migrated']}")
        logger.info(f"Checklists migrated: {self.migration_stats['checklists_migrated']}")
        logger.info(f"Risk assessments migrated: {self.migration_stats['risk_assessments_migrated']}")
        logger.info(f"Corrective actions migrated: {self.migration_stats['corrective_actions_migrated']}")
        logger.info(f"Preventive actions migrated: {self.migration_stats['preventive_actions_migrated']}")
        
        if self.migration_stats['errors']:
            logger.error(f"Errors: {len(self.migration_stats['errors'])}")
            for error in self.migration_stats['errors']:
                logger.error(f"  - {error}")
        
        if self.migration_stats['warnings']:
            logger.warning(f"Warnings: {len(self.migration_stats['warnings'])}")
            for warning in self.migration_stats['warnings']:
                logger.warning(f"  - {warning}")
        
        logger.info("=" * 50)

def main():
    """Main function to run the migration"""
    parser = argparse.ArgumentParser(description='PRP Data Migration Script')
    parser.add_argument('--dry-run', action='store_true', help='Run migration without making changes')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    parser.add_argument('--no-validate', action='store_true', help='Skip data validation')
    
    args = parser.parse_args()
    
    # Create migrator instance
    migrator = PRPDataMigrator(
        dry_run=args.dry_run,
        backup=not args.no_backup,
        validate=not args.no_validate
    )
    
    # Run migration
    success = migrator.run_migration()
    
    if success:
        logger.info("Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
