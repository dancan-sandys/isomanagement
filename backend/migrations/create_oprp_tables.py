"""
Migration script to create OPRP (Operational Prerequisite Program) tables
"""
import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def migrate():
    """Create OPRP tables"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'iso22000_fsms.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='oprps'")
        if cursor.fetchone():
            print("✓ oprps table already exists")
            conn.close()
            return True
        
        print("Creating oprps table...")
        
        # Create oprps table
        cursor.execute("""
            CREATE TABLE oprps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                hazard_id INTEGER NOT NULL,
                oprp_number VARCHAR(20) NOT NULL,
                oprp_name VARCHAR(200) NOT NULL,
                description TEXT,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                
                -- Operational limits (JSON)
                operational_limits TEXT,
                operational_limit_min REAL,
                operational_limit_max REAL,
                operational_limit_unit VARCHAR(50),
                operational_limit_description TEXT,
                
                -- Monitoring
                monitoring_frequency VARCHAR(100),
                monitoring_method TEXT,
                monitoring_responsible INTEGER,
                monitoring_equipment VARCHAR(100),
                
                -- Corrective actions
                corrective_actions TEXT,
                
                -- Verification
                verification_frequency VARCHAR(100),
                verification_method TEXT,
                verification_responsible INTEGER,
                
                -- Documentation
                monitoring_records TEXT,
                verification_records TEXT,
                
                -- OPRP-specific fields
                justification TEXT,
                objective TEXT,
                sop_reference TEXT,
                effectiveness_validation TEXT,
                validation_evidence TEXT,
                
                -- Risk integration fields
                risk_register_item_id INTEGER,
                risk_assessment_method VARCHAR(100),
                risk_assessment_date TIMESTAMP,
                risk_assessor_id INTEGER,
                risk_treatment_plan TEXT,
                risk_monitoring_frequency VARCHAR(100),
                risk_review_frequency VARCHAR(100),
                risk_control_effectiveness INTEGER,
                risk_residual_score INTEGER,
                risk_residual_level VARCHAR(50),
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                created_by INTEGER NOT NULL,
                
                -- Foreign keys
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (hazard_id) REFERENCES hazards(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (monitoring_responsible) REFERENCES users(id),
                FOREIGN KEY (verification_responsible) REFERENCES users(id),
                FOREIGN KEY (risk_register_item_id) REFERENCES risk_register(id),
                FOREIGN KEY (risk_assessor_id) REFERENCES users(id),
                
                -- Constraints
                UNIQUE (product_id, oprp_number)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX ix_oprps_product_id ON oprps(product_id)")
        cursor.execute("CREATE INDEX ix_oprps_hazard_id ON oprps(hazard_id)")
        cursor.execute("CREATE INDEX ix_oprps_status ON oprps(status)")
        cursor.execute("CREATE INDEX ix_oprps_product_hazard ON oprps(product_id, hazard_id)")
        cursor.execute("CREATE INDEX ix_oprps_status_created ON oprps(status, created_at)")
        
        print("✓ Created oprps table")
        print("✓ Created indexes")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("OPRP Tables Migration")
    print("Creating oprps table")
    print("=" * 60)
    print()
    
    success = migrate()
    
    if success:
        print("\nMigration completed successfully!")
        sys.exit(0)
    else:
        print("\nMigration failed!")
        sys.exit(1)


