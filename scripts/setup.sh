#!/bin/bash

# ISO 22000 FSMS Setup Script
# This script sets up the development environment for the ISO 22000 FSMS project

set -e  # Exit on any error

echo "🚀 Setting up ISO 22000 FSMS Development Environment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        print_error "Node.js is not installed. Please install Node.js 16+ first."
        exit 1
    fi
}

# Check if PostgreSQL is installed (optional for development)
check_postgres() {
    print_status "Checking PostgreSQL installation..."
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL found (optional for development)"
    else
        print_warning "PostgreSQL is not installed. This is optional for development."
        print_warning "SQLite will be used by default. PostgreSQL is only needed for production."
    fi
}

# Setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "backend/venv" ]; then
        cd backend
        python3 -m venv venv
        print_success "Virtual environment created"
        cd ..
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment and install dependencies
    print_status "Installing Python dependencies..."
    cd backend
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    print_success "Python dependencies installed"
}

# Setup Node.js dependencies
setup_node_deps() {
    print_status "Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
    print_success "Node.js dependencies installed"
}

# Setup database (SQLite for development)
setup_database() {
    print_status "Setting up database..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        # Production setup with PostgreSQL
        if command -v psql &> /dev/null; then
            if psql -lqt | cut -d \| -f 1 | grep -qw iso22000_fsms; then
                print_status "Database 'iso22000_fsms' already exists"
            else
                print_status "Creating database 'iso22000_fsms'..."
                createdb iso22000_fsms
                print_success "Database created"
            fi
        else
            print_error "PostgreSQL is required for production but not installed"
            exit 1
        fi
    else
        # Development setup with SQLite
        print_status "Using SQLite for development (no setup required)"
        print_success "SQLite database will be created automatically"
    fi
}

# Setup environment files
setup_env_files() {
    print_status "Setting up environment files..."
    
    # Backend environment file
    if [ ! -f "backend/.env" ]; then
        cp backend/env.example backend/.env
        print_success "Backend .env file created (using SQLite for development)"
    else
        print_status "Backend .env file already exists"
    fi
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    cd backend
    source venv/bin/activate
    
    # Initialize Alembic if not already done
    if [ ! -d "alembic/versions" ]; then
        alembic init alembic
        print_status "Alembic initialized"
    fi
    
    # Run migrations
    alembic upgrade head
    cd ..
    print_success "Database migrations completed"
}

# Create initial admin user
create_admin_user() {
    print_status "Creating initial admin user..."
    cd backend
    source venv/bin/activate
    
    # Create a Python script to add admin user
    cat > create_admin.py << 'EOF'
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus
from app.core.database import init_db

def create_admin_user():
    init_db()
    db = SessionLocal()
    
    # Check if admin user already exists
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print("Admin user already exists")
        return
    
    # Create admin user
    admin_user = User(
        username="admin",
        email="admin@iso22000.com",
        full_name="System Administrator",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=True
    )
    
    db.add(admin_user)
    db.commit()
    print("Admin user created successfully")
    print("Username: admin")
    print("Password: admin123")
    print("Please change the password after first login!")
    
    db.close()

if __name__ == "__main__":
    create_admin_user()
EOF

    python create_admin.py
    rm create_admin.py
    cd ..
}

# Main setup function
main() {
    echo "Starting setup process..."
    
    # Check prerequisites
    check_python
    check_node
    check_postgres
    
    # Setup environments
    setup_python_env
    setup_node_deps
    
    # Setup database
    setup_database
    setup_env_files
    
    # Run migrations
    run_migrations
    
    # Create admin user
    create_admin_user
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo "=================================================="
    echo ""
    echo "Next steps:"
    echo "1. Update backend/.env with your settings (optional for development)"
    echo "2. Start the backend server:"
    echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo "3. Start the frontend server:"
    echo "   cd frontend && npm start"
    echo "4. Access the application:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo ""
    echo "Default admin credentials:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""
    echo "⚠️  Remember to change the admin password after first login!"
    echo ""
    echo "📝 Notes:"
    echo "   - Using SQLite for development (no PostgreSQL required)"
    echo "   - Database file: backend/iso22000_fsms.db"
    echo "   - For production, install PostgreSQL and update .env"
}

# Run main function
main 