from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
all_tables = inspector.get_table_names()

# Check for our new tables
new_tables = [
    'immediate_actions',
    'risk_assessments', 
    'escalation_rules',
    'preventive_actions',
    'effectiveness_monitoring'
]

print("Database Schema Implementation Status:")
print("=" * 50)

for table in new_tables:
    if table in all_tables:
        print(f"✓ {table} - CREATED")
        
        # Show table structure
        columns = inspector.get_columns(table)
        print(f"  Columns: {len(columns)}")
        
        # Show foreign keys
        foreign_keys = inspector.get_foreign_keys(table)
        print(f"  Foreign Keys: {len(foreign_keys)}")
        
        # Show indexes
        indexes = inspector.get_indexes(table)
        print(f"  Indexes: {len(indexes)}")
        print()
    else:
        print(f"✗ {table} - MISSING")
        print()

print("=" * 50)
print(f"Total new tables created: {sum(1 for table in new_tables if table in all_tables)}/{len(new_tables)}")
