from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('immediate_actions')
print('immediate_actions table columns:')
for col in columns:
    print(f'  - {col["name"]}: {col["type"]}')

# Check foreign keys
foreign_keys = inspector.get_foreign_keys('immediate_actions')
print('\nForeign keys:')
for fk in foreign_keys:
    print(f'  - {fk["constrained_columns"]} -> {fk["referred_table"]}.{fk["referred_columns"]}')

# Check indexes
indexes = inspector.get_indexes('immediate_actions')
print('\nIndexes:')
for idx in indexes:
    print(f'  - {idx["name"]}: {idx["column_names"]}')
