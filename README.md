# ISO 22000 Food Safety Management Software for Dairy Processing

A comprehensive, cloud-enabled web-based software system designed to automate and support the implementation, maintenance, monitoring, and continual improvement of a Food Safety Management System (FSMS) based on ISO 22000:2018, specifically customized for dairy processing facilities.

## 🎯 Project Overview

This software provides a complete solution for dairy processing facilities to manage their food safety systems, including:

- **Document Control & Management**
- **HACCP Plan Development & Monitoring**
- **PRP (Prerequisite Programs) Management**
- **Traceability & Recall Management**
- **Supplier & Material Management**
- **Non-Conformance & CAPA Management**
- **Audit Management (Internal & External)**
- **Training & Competency Tracking**
- **Risk & Opportunity Management**
- **Management Review Processes**
- **Equipment Maintenance & Calibration**
- **Allergen & Label Control**
- **Customer Complaint Management**
- **Comprehensive Dashboards & Reporting**

## 🏗️ Architecture

- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Frontend**: React with TypeScript and Material-UI
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Authentication**: JWT with role-based access control
- **File Storage**: AWS S3 (configurable)
- **Mobile**: Progressive Web App (PWA) capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- SQLite (built-in with Python) - for development
- PostgreSQL 13+ (optional for development, required for production)

### Automated Setup (Recommended)

```bash
# Run the automated setup script
./scripts/setup.sh
```

### Manual Setup

#### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env if needed (SQLite is configured by default)

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn main:app --reload
```

#### Frontend Setup

```bash
cd frontend
npm install
npm start
```

#### Database Setup

**Development (SQLite):**
- No setup required - SQLite database is created automatically
- Database file: `backend/iso22000_fsms.db`

**Production (PostgreSQL):**
```bash
# Create database
createdb iso22000_fsms

# Run migrations (from backend directory)
alembic upgrade head
```

## 📁 Project Structure

```
iso/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configurations
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── alembic/            # Database migrations
│   ├── iso22000_fsms.db    # SQLite database (development)
│   └── tests/              # Backend tests
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── hooks/          # Custom hooks
│   │   └── utils/          # Utility functions
│   └── public/             # Static assets
├── docs/                   # Documentation
├── docker/                 # Docker configurations
└── scripts/                # Deployment and utility scripts
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
# For Development (SQLite) - No additional setup needed
DATABASE_URL=sqlite:///./iso22000_fsms.db
DATABASE_TYPE=sqlite

# For Production (PostgreSQL) - Uncomment and configure
# DATABASE_URL=postgresql://user:password@localhost/iso22000_fsms
# DATABASE_TYPE=postgresql

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=ISO 22000 FSMS
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development  # Change to 'production' for production deployment

# File Storage (optional for development)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1

# Email (optional for development)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Database Configuration

**Development (Default):**
- Uses SQLite database
- No additional setup required
- Database file: `backend/iso22000_fsms.db`
- Perfect for development and testing

**Production:**
- Uses PostgreSQL database
- Install PostgreSQL and psycopg2
- Update `.env` with PostgreSQL connection string
- Set `ENVIRONMENT=production`

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [User Manual](docs/user-manual.md)
- [Admin Guide](docs/admin-guide.md)
- [Deployment Guide](docs/deployment.md)

## 🚀 Deployment

### Development
```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm start
```

### Production
```bash
# Install production dependencies
cd backend
pip install -r requirements-production.txt

# Set environment to production
export ENVIRONMENT=production

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions, please contact the development team or create an issue in the repository.

---

**Note**: This software is designed specifically for dairy processing facilities implementing ISO 22000:2018. Ensure proper validation and testing before use in production environments.

## 🔄 Database Migration

When switching between SQLite and PostgreSQL:

```bash
# For SQLite to PostgreSQL migration
export ENVIRONMENT=production
alembic upgrade head

# For PostgreSQL to SQLite migration
export ENVIRONMENT=development
alembic upgrade head
``` 