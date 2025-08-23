# Docker Deployment Guide - ISO 22000 FSMS

This guide provides step-by-step instructions for deploying the ISO 22000 FSMS application using Docker.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows 10/11
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 10GB free space
- **CPU**: 2 cores minimum (4 cores recommended)

### Verify Installation
```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Verify Docker is running
docker info
```

## 🚀 Quick Deployment

### Step 1: Clone and Prepare
```bash
# Clone the repository
git clone <repository-url>
cd isomanagement

# Copy environment template
cp docker.env.example .env
```

### Step 2: Configure Environment
Edit `.env` file with your settings:

```bash
# Required: Update these values
SECRET_KEY=your-super-secret-key-change-this-in-production
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional: Customize these
FROM_EMAIL=noreply@your-domain.com
FROM_NAME=Your Company Name
```

### Step 3: Build and Deploy
```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Step 4: Verify Deployment
```bash
# Check all services are healthy
docker-compose ps

# Test backend health
curl http://localhost:8080/api/v1/health

# Test frontend
curl http://localhost:8080/health
```

### Step 5: Access Application
- **Application**: http://localhost:8080
- **Default Admin**: `admin` / `admin123`

## 🔧 Detailed Configuration

### Environment Variables

#### Security Configuration
```bash
# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Token expiration settings
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### Database Configuration
```bash
# PostgreSQL (default - works with Docker)
DATABASE_URL=postgresql://iso22000_user:iso22000_password@postgres:5432/iso22000_fsms

# Redis (default - works with Docker)
REDIS_URL=redis://:redis_password@redis:6379/0
```

#### Email Configuration
```bash
# Gmail Example
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@your-domain.com
FROM_NAME=ISO 22000 FSMS

# Outlook Example
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
```

#### Application Settings
```bash
# Environment
ENVIRONMENT=production
DEBUG=False

# CORS (update with your domain)
ALLOWED_ORIGINS=["http://localhost:8080", "https://your-domain.com"]

# File upload limits
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=pdf,doc,docx,xls,xlsx,ppt,pptx,jpg,jpeg,png,gif
```

### Email Provider Setup

#### Gmail Setup
1. **Enable 2-Factor Authentication**
   - Go to Google Account settings
   - Enable 2FA on your account

2. **Generate App Password**
   - Go to Security settings
   - Select "App passwords"
   - Generate password for "Mail"
   - Use this password in `SMTP_PASSWORD`

3. **Configure .env**
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-character-app-password
   ```

#### Other Email Providers
- **Outlook/Hotmail**: Use `smtp-mail.outlook.com:587`
- **Yahoo**: Use `smtp.mail.yahoo.com:587`
- **Custom SMTP**: Use your provider's SMTP settings

## 🐳 Docker Services Overview

### Core Services

#### PostgreSQL Database
```yaml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: iso22000_fsms
    POSTGRES_USER: iso22000_user
    POSTGRES_PASSWORD: iso22000_password
  volumes:
    - postgres_data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U iso22000_user -d iso22000_fsms"]
```

#### Redis Cache
```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes --requirepass redis_password
  volumes:
    - redis_data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "-a", "redis_password", "ping"]
```

#### Backend API
```yaml
backend:
  build: ./backend
  environment:
    DATABASE_URL: postgresql://iso22000_user:iso22000_password@postgres:5432/iso22000_fsms
    REDIS_URL: redis://:redis_password@redis:6379/0
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
```

#### Frontend Application
```yaml
frontend:
  build: ./frontend
  environment:
    REACT_APP_API_URL: http://localhost:8080/api/v1
  depends_on:
    - backend
```

#### Nginx Reverse Proxy
```yaml
nginx:
  image: nginx:alpine
  ports:
    - "8080:80"
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - frontend
    - backend
```

### Optional Services

#### Backup Service
```bash
# Enable backup service
docker-compose --profile backup up -d

# Run manual backup
docker-compose run --rm backup

# Schedule backups
0 2 * * * cd /path/to/isomanagement && docker-compose run --rm backup
```

## 📊 Monitoring and Maintenance

### Health Monitoring
```bash
# Check service health
docker-compose ps

# Monitor resource usage
docker stats

# View real-time logs
docker-compose logs -f
```

### Log Management
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Search logs for errors
docker-compose logs | grep -i error

# Follow logs in real-time
docker-compose logs -f --tail=100
```

### Database Management
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U iso22000_user -d iso22000_fsms

# Run migrations
docker-compose exec backend alembic upgrade head

# Create backup
docker-compose run --rm backup

# Restore from backup
docker-compose exec postgres psql -U iso22000_user -d iso22000_fsms < backup_file.sql
```

### Performance Monitoring
```bash
# Check container resource usage
docker stats --no-stream

# Monitor specific container
docker stats backend frontend postgres redis

# Check disk usage
docker system df
```

## 🔄 Updates and Maintenance

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check for updates
docker-compose pull
docker-compose up -d
```

### Database Migrations
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

### Backup and Recovery
```bash
# Create backup
docker-compose run --rm backup

# List backups
ls -la backups/

# Restore from backup
docker-compose exec postgres psql -U iso22000_user -d iso22000_fsms < backups/backup_file.sql
```

## 🚀 Production Deployment

### Production Checklist
- [ ] Update `SECRET_KEY` with secure value
- [ ] Configure proper `ALLOWED_ORIGINS`
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Change default admin password
- [ ] Configure backup schedule
- [ ] Set up log rotation
- [ ] Configure resource limits

### SSL/TLS Setup
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Add certificates
cp your-cert.pem nginx/ssl/
cp your-key.pem nginx/ssl/

# Update nginx.conf for HTTPS
# Update ALLOWED_ORIGINS to include HTTPS URLs
```

### Scaling Configuration
```bash
# Scale backend workers
docker-compose up -d --scale backend=3

# Scale with load balancer
# Add additional nginx instances
```

### Security Hardening
```bash
# Update default passwords
# Configure firewall
# Set up intrusion detection
# Enable audit logging
# Configure backup encryption
```

## 🔍 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8080

# Change ports in docker-compose.yml
ports:
  - "8081:80"  # Change 8080 to 8081
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test database connection
docker-compose exec backend python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection successful')
"

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Email Configuration Issues
```bash
# Test email service
docker-compose exec backend python -c "
from app.services.email_service import EmailService
service = EmailService()
print('Email service enabled:', service.enabled)
print('SMTP host:', service.smtp_host)
print('SMTP port:', service.smtp_port)
"

# Check email logs
docker-compose logs backend | grep -i email
```

#### Memory Issues
```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Restart Docker Desktop

# Optimize container resources
docker-compose down
docker system prune -a
docker-compose up -d
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Optimize images
docker-compose build --no-cache

# Clean up unused resources
docker system prune -a

# Monitor application performance
docker-compose logs backend | grep -i performance
```

### Network Issues
```bash
# Check network connectivity
docker-compose exec backend ping postgres
docker-compose exec backend ping redis

# Check DNS resolution
docker-compose exec backend nslookup postgres

# Restart network
docker-compose down
docker network prune
docker-compose up -d
```

## 📈 Performance Optimization

### Backend Optimization
```bash
# Adjust Gunicorn workers
# Update docker-compose.yml backend service
command: gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Enable Redis caching
# Configure database connection pooling
# Optimize database queries
```

### Frontend Optimization
```bash
# Enable production builds
# Configure CDN for static assets
# Implement lazy loading
# Optimize bundle size
```

### Database Optimization
```bash
# Configure connection pooling
# Optimize indexes
# Regular maintenance
# Monitor query performance
```

## 🔐 Security Best Practices

### Container Security
- Use non-root users
- Keep images updated
- Scan for vulnerabilities
- Limit container privileges

### Network Security
- Use custom networks
- Configure firewall rules
- Enable SSL/TLS
- Monitor network traffic

### Data Security
- Encrypt sensitive data
- Regular backups
- Access control
- Audit logging

## 📞 Support and Resources

### Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)

### Community Support
- Docker Community Forums
- Stack Overflow
- GitHub Issues
- Development Team

### Monitoring Tools
- Docker Desktop
- Portainer
- Grafana
- Prometheus

---

**Note**: This guide covers the complete Docker deployment process. For production deployments, always follow security best practices and perform thorough testing before going live.
