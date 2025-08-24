#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database to be ready..."
/wait-for-it.sh postgres:5432 -t 60

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."
/wait-for-it.sh redis:6379 -t 60

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Create initial data if needed
echo "Checking for initial data..."
python -c "
import sys
sys.path.append('/app')
from app.core.database import get_db
from app.models.user import User
from app.models.rbac import Role
from sqlalchemy.orm import Session

db = next(get_db())
if not db.query(User).first():
    print('Creating initial admin user...')
    # Create admin role if it doesn't exist
    admin_role = db.query(Role).filter(Role.name == 'System Administrator').first()
    if not admin_role:
        admin_role = Role(name='System Administrator', description='System Administrator Role')
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)
    
    # Create admin user
    from app.core.security import get_password_hash
    admin_user = User(
        username='admin',
        email='admin@iso-system.com',
        full_name='System Administrator',
        hashed_password=get_password_hash('admin123'),
        role_id=admin_role.id,
        is_active=True,
        is_verified=True,
        status='ACTIVE'
    )
    db.add(admin_user)
    db.commit()
    print('Initial admin user created: admin/admin123')
else:
    print('Database already has users, skipping initial setup')
"

# Start the application
echo "Starting ISO 22000 FSMS Backend..."
exec gunicorn app.main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --timeout 120 \
    --keep-alive 5
