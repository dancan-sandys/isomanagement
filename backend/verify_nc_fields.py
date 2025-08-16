from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('non_conformances')
column_names = [col["name"] for col in columns]

new_fields = ['requires_immediate_action', 'risk_level', 'escalation_status']

print("New fields added to non_conformances table:")
print("=" * 50)

for field in new_fields:
    if field in column_names:
        print(f"✓ {field} - ADDED")
    else:
        print(f"✗ {field} - MISSING")

print("=" * 50)
print(f"Total new fields added: {sum(1 for field in new_fields if field in column_names)}/{len(new_fields)}")
