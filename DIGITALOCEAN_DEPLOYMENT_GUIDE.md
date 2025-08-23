# DigitalOcean App Platform Deployment Guide (No Docker)

## 🚀 Overview

This guide will walk you through deploying your ISO 22000 Food Safety Management System to DigitalOcean App Platform without using Docker containers.

## 📋 Prerequisites

### Required Accounts
- [DigitalOcean Account](https://www.digitalocean.com/)
- [GitHub Account](https://github.com/) (for source code)
- [GitHub Personal Access Token](https://github.com/settings/tokens) (for deployment)

### Required Tools
- [DigitalOcean CLI (doctl)](https://docs.digitalocean.com/reference/doctl/how-to/install/)
- [Git](https://git-scm.com/)

### Required Services
- DigitalOcean Spaces (for file storage)
- SMTP service (Gmail, SendGrid, etc.)
- Custom domain (optional but recommended)

## 🔧 Phase 1: Environment Setup

### Step 1: Prepare Your Repository

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for DigitalOcean App Platform deployment"
   git push origin main
   ```

2. **Verify all deployment files are present**:
   - `.do/app.yaml`
   - `frontend/nginx.conf`
   - `backend/requirements.txt`
   - `frontend/package.json`

### Step 2: Set Up DigitalOcean Spaces

1. **Create a Spaces bucket**:
   - Go to DigitalOcean Console → Spaces
   - Create a new Space named `iso22000-fsms-files`
   - Choose a region (recommend same as your app)

2. **Configure CORS for the Space**:
   ```json
   [
     {
       "AllowedOrigins": ["*"],
       "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
       "AllowedHeaders": ["*"],
       "MaxAgeSeconds": 3000
     }
   ]
   ```

3. **Generate API Keys**:
   - Go to API → Spaces Keys
   - Generate a new key pair
   - Save the Access Key and Secret Key

### Step 3: Set Up Email Service

1. **Configure Gmail App Password** (recommended):
   - Enable 2-factor authentication on your Gmail account
   - Generate an App Password
   - Use this password in your SMTP configuration

2. **Alternative: Use SendGrid**:
   - Create a SendGrid account
   - Verify your domain
   - Generate an API key

## 🧪 Phase 2: Local Testing

### Step 1: Test Backend Locally

1. **Set up Python environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Test backend startup**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Verify backend is running**:
   - Check http://localhost:8000/health
   - Test API endpoints

### Step 2: Test Frontend Locally

1. **Set up Node.js environment**:
   ```bash
   cd frontend
   npm install
   ```

2. **Test frontend build**:
   ```bash
   npm run build
   ```

3. **Test frontend development server**:
   ```bash
   npm start
   ```

## ☁️ Phase 3: DigitalOcean Deployment

### Step 1: Install and Configure doctl

1. **Install doctl**:
   ```bash
   # macOS
   brew install doctl
   
   # Windows
   scoop install doctl
   
   # Linux
   snap install doctl
   ```

2. **Authenticate with DigitalOcean**:
   ```bash
   doctl auth init
   ```

### Step 2: Create the App

1. **Deploy using app.yaml**:
   ```bash
   doctl apps create --spec .do/app.yaml
   ```

2. **Or deploy via DigitalOcean Console**:
   - Go to Apps → Create App
   - Connect your GitHub repository
   - Select the repository and branch
   - Configure the services as defined in `app.yaml`

### Step 3: Configure Environment Variables

1. **Set up secrets in DigitalOcean Console**:
   - Go to your app → Settings → Environment Variables
   - Add all the environment variables from the app.yaml file

2. **Required secrets**:
   ```
   SECRET_KEY=your-strong-random-key
   SMTP_HOST=smtp.gmail.com
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SPACES_ACCESS_KEY=your-spaces-access-key
   SPACES_SECRET_KEY=your-spaces-secret-key
   ```

### Step 4: Configure Database

1. **Set up PostgreSQL database**:
   - DigitalOcean will create a managed PostgreSQL cluster
   - The connection string will be automatically provided
   - Run database migrations:
     ```bash
     # Connect to your app and run migrations
     doctl apps run <app-id> --command "alembic upgrade head"
     ```

## 🔒 Phase 4: Security Configuration

### Step 1: SSL/TLS Setup

1. **Custom domain setup** (recommended):
   - Purchase a domain (e.g., `yourcompany.com`)
   - Add DNS records pointing to your DigitalOcean app
   - DigitalOcean will automatically provision SSL certificates

2. **Update CORS settings**:
   - Update `ALLOWED_ORIGINS` in your environment variables
   - Include your custom domain

### Step 2: Security Headers

1. **Verify security headers are set**:
   - Check that nginx is serving with proper security headers
   - Verify CSP, X-Frame-Options, etc. are configured

### Step 3: Access Control

1. **Set up admin user**:
   ```bash
   # Connect to your app and create admin user
   doctl apps run <app-id> --command "python -c \"from app.scripts.create_admin_user import create_admin_user; create_admin_user()\""
   ```

## 📊 Phase 5: Monitoring and Maintenance

### Step 1: Set Up Monitoring

1. **DigitalOcean Monitoring**:
   - Enable monitoring for your app
   - Set up alerts for CPU, memory, and disk usage
   - Monitor database performance

2. **Application Monitoring**:
   - Set up logging aggregation
   - Configure error tracking (Sentry recommended)
   - Set up uptime monitoring

### Step 2: Backup Strategy

1. **Database backups**:
   - DigitalOcean provides automated backups
   - Test restore procedures regularly
   - Keep backup retention for 30 days minimum

2. **File storage backups**:
   - Configure Spaces versioning
   - Set up cross-region replication if needed

### Step 3: Performance Optimization

1. **Database optimization**:
   - Monitor slow queries
   - Add database indexes as needed
   - Configure connection pooling

2. **Application optimization**:
   - Enable caching where appropriate
   - Optimize static file serving
   - Monitor API response times

## 🔄 Phase 6: CI/CD Pipeline

### Step 1: GitHub Actions Setup

1. **Create `.github/workflows/deploy.yml`**:
   ```yaml
   name: Deploy to DigitalOcean
   
   on:
     push:
       branches: [main]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Deploy to DigitalOcean
           uses: digitalocean/action-doctl@v2
           with:
             token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
           run: |
             doctl apps update <app-id> --spec .do/app.yaml
   ```

2. **Add secrets to GitHub**:
   - Go to your repository → Settings → Secrets
   - Add `DIGITALOCEAN_ACCESS_TOKEN`

### Step 2: Automated Testing

1. **Add test workflow**:
   ```yaml
   name: Test
   
   on:
     pull_request:
       branches: [main]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: '3.11'
         - name: Install dependencies
           run: |
             cd backend
             pip install -r requirements.txt
         - name: Run tests
           run: |
             cd backend
             pytest
   ```

## 🚨 Troubleshooting

### Common Issues

1. **Build failures**:
   - Check Python dependencies in requirements.txt
   - Verify all imports are available
   - Check for missing environment variables

2. **Database connection issues**:
   - Verify DATABASE_URL is correct
   - Check database is accessible from app
   - Run database migrations

3. **CORS errors**:
   - Update ALLOWED_ORIGINS with correct domains
   - Check frontend API_URL configuration
   - Verify SSL certificates

4. **File upload issues**:
   - Check Spaces credentials
   - Verify bucket permissions
   - Check CORS configuration

### Debug Commands

```bash
# Check app status
doctl apps get <app-id>

# View app logs
doctl apps logs <app-id>

# Run commands in app
doctl apps run <app-id> --command "your-command"

# Check database connection
doctl apps run <app-id> --command "python -c \"from app.core.database import SessionLocal; db = SessionLocal(); print('DB OK')\""
```

## 📈 Scaling and Optimization

### Horizontal Scaling

1. **Increase instance count**:
   - Update `instance_count` in `app.yaml`
   - Monitor performance metrics
   - Scale based on traffic patterns

2. **Database scaling**:
   - Upgrade database plan as needed
   - Consider read replicas for heavy read workloads
   - Monitor connection pool usage

### Performance Optimization

1. **Caching strategy**:
   - Implement Redis caching for frequently accessed data
   - Use CDN for static assets
   - Enable browser caching

2. **Database optimization**:
   - Add indexes for slow queries
   - Optimize database queries
   - Use connection pooling

## 🔄 Maintenance Procedures

### Regular Maintenance

1. **Weekly**:
   - Check application logs
   - Monitor performance metrics
   - Review security alerts

2. **Monthly**:
   - Update dependencies
   - Review and rotate secrets
   - Test backup and restore procedures

3. **Quarterly**:
   - Security audit
   - Performance review
   - Capacity planning

### Update Procedures

1. **Application updates**:
   ```bash
   # Update app.yaml with new version
   # Push to GitHub
   # DigitalOcean will automatically deploy
   ```

2. **Database migrations**:
   ```bash
   # Run migrations after deployment
   doctl apps run <app-id> --command "alembic upgrade head"
   ```

## 📞 Support and Resources

### Documentation
- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://create-react-app.dev/docs/production-build/)

### Community Support
- [DigitalOcean Community](https://www.digitalocean.com/community)
- [FastAPI Community](https://github.com/tiangolo/fastapi/discussions)
- [React Community](https://reactjs.org/community/support.html)

### Professional Support
- Consider DigitalOcean Premium Support for production applications
- Engage with FastAPI and React consultants for complex issues

---

## ✅ Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] Local testing completed
- [ ] DigitalOcean Spaces configured
- [ ] Email service configured
- [ ] Environment variables set
- [ ] Database created and migrated
- [ ] SSL certificates configured
- [ ] Monitoring enabled
- [ ] Backup strategy implemented
- [ ] CI/CD pipeline configured
- [ ] Performance testing completed
- [ ] Security audit passed
- [ ] Documentation updated
- [ ] Team training completed

---

**Congratulations!** Your ISO 22000 FSMS is now deployed and ready for production use. Remember to regularly monitor, maintain, and update your application to ensure optimal performance and security.
