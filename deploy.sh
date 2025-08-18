#!/bin/bash

# ISO 22000 FSMS - DigitalOcean Deployment Script
# This script automates the deployment process to DigitalOcean App Platform

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if doctl is installed
    if ! command_exists doctl; then
        print_error "doctl is not installed. Please install it first:"
        echo "  macOS: brew install doctl"
        echo "  Windows: scoop install doctl"
        echo "  Linux: snap install doctl"
        exit 1
    fi
    
    # Check if git is installed
    if ! command_exists git; then
        print_error "git is not installed. Please install it first."
        exit 1
    fi
    
    # Check if docker is installed (for local testing)
    if ! command_exists docker; then
        print_warning "Docker is not installed. Local testing will be skipped."
    fi
    
    print_success "Prerequisites check completed"
}

# Function to authenticate with DigitalOcean
authenticate_do() {
    print_status "Authenticating with DigitalOcean..."
    
    if ! doctl auth list >/dev/null 2>&1; then
        print_status "Please authenticate with DigitalOcean..."
        doctl auth init
    else
        print_success "Already authenticated with DigitalOcean"
    fi
}

# Function to check if app.yaml exists
check_config() {
    print_status "Checking configuration files..."
    
    if [ ! -f ".do/app.yaml" ]; then
        print_error ".do/app.yaml not found. Please create it first."
        exit 1
    fi
    
    if [ ! -f "backend/Dockerfile" ]; then
        print_error "backend/Dockerfile not found. Please create it first."
        exit 1
    fi
    
    if [ ! -f "frontend/Dockerfile" ]; then
        print_error "frontend/Dockerfile not found. Please create it first."
        exit 1
    fi
    
    print_success "Configuration files check completed"
}

# Function to test locally with Docker Compose
test_locally() {
    if ! command_exists docker; then
        print_warning "Skipping local test (Docker not available)"
        return
    fi
    
    print_status "Testing locally with Docker Compose..."
    
    if [ -f "docker-compose.yml" ]; then
        print_status "Building and starting services..."
        docker-compose up --build -d
        
        print_status "Waiting for services to be ready..."
        sleep 30
        
        # Test backend health
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend health check passed"
        else
            print_error "Backend health check failed"
            docker-compose logs backend
            exit 1
        fi
        
        # Test frontend
        if curl -f http://localhost:8080 >/dev/null 2>&1; then
            print_success "Frontend health check passed"
        else
            print_error "Frontend health check failed"
            docker-compose logs frontend
            exit 1
        fi
        
        print_status "Stopping local services..."
        docker-compose down
        
        print_success "Local testing completed"
    else
        print_warning "docker-compose.yml not found, skipping local test"
    fi
}

# Function to deploy to DigitalOcean
deploy_to_do() {
    print_status "Deploying to DigitalOcean App Platform..."
    
    # Check if app already exists
    if doctl apps list --format Name | grep -q "iso22000-fsms"; then
        print_status "App already exists, updating..."
        APP_ID=$(doctl apps list --format ID,Name | grep "iso22000-fsms" | awk '{print $1}')
        doctl apps update $APP_ID --spec .do/app.yaml
    else
        print_status "Creating new app..."
        doctl apps create --spec .do/app.yaml
    fi
    
    print_success "Deployment initiated"
}

# Function to wait for deployment
wait_for_deployment() {
    print_status "Waiting for deployment to complete..."
    
    # Get app ID
    APP_ID=$(doctl apps list --format ID,Name | grep "iso22000-fsms" | awk '{print $1}')
    
    if [ -z "$APP_ID" ]; then
        print_error "Could not find app ID"
        exit 1
    fi
    
    # Wait for deployment
    doctl apps wait-for-deployment $APP_ID
    
    print_success "Deployment completed"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    APP_ID=$(doctl apps list --format ID,Name | grep "iso22000-fsms" | awk '{print $1}')
    
    if [ -z "$APP_ID" ]; then
        print_error "Could not find app ID"
        exit 1
    fi
    
    # Wait a bit for the app to be fully ready
    sleep 30
    
    # Run migrations
    doctl apps run $APP_ID --command "alembic upgrade head"
    
    print_success "Database migrations completed"
}

# Function to perform health check
health_check() {
    print_status "Performing health check..."
    
    APP_ID=$(doctl apps list --format ID,Name | grep "iso22000-fsms" | awk '{print $1}')
    
    if [ -z "$APP_ID" ]; then
        print_error "Could not find app ID"
        exit 1
    fi
    
    # Get app URL
    APP_URL=$(doctl apps get $APP_ID --format URL --no-header)
    
    print_status "Checking health at $APP_URL"
    
    # Try health check for up to 5 minutes
    for i in {1..30}; do
        if curl -f "$APP_URL/health" >/dev/null 2>&1; then
            print_success "Health check passed!"
            break
        fi
        print_status "Health check attempt $i failed, retrying in 10 seconds..."
        sleep 10
    done
    
    # Final health check
    if ! curl -f "$APP_URL/health" >/dev/null 2>&1; then
        print_error "Health check failed after all attempts"
        exit 1
    fi
}

# Function to show app info
show_app_info() {
    print_status "Application Information:"
    
    APP_ID=$(doctl apps list --format ID,Name | grep "iso22000-fsms" | awk '{print $1}')
    
    if [ -z "$APP_ID" ]; then
        print_error "Could not find app ID"
        exit 1
    fi
    
    doctl apps get $APP_ID
    
    print_success "Deployment completed successfully!"
    print_status "Your app is now live at: $(doctl apps get $APP_ID --format URL --no-header)"
}

# Main deployment function
main() {
    echo "🚀 ISO 22000 FSMS - DigitalOcean Deployment"
    echo "=============================================="
    
    # Check if running in interactive mode
    if [ "$1" = "--non-interactive" ]; then
        INTERACTIVE=false
    else
        INTERACTIVE=true
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Authenticate with DigitalOcean
    authenticate_do
    
    # Check configuration
    check_config
    
    # Ask for local testing
    if [ "$INTERACTIVE" = true ]; then
        read -p "Do you want to test locally first? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            test_locally
        fi
    fi
    
    # Deploy to DigitalOcean
    deploy_to_do
    
    # Wait for deployment
    wait_for_deployment
    
    # Run migrations
    run_migrations
    
    # Health check
    health_check
    
    # Show app info
    show_app_info
}

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --non-interactive   Run in non-interactive mode (for CI/CD)"
    echo ""
    echo "This script will:"
    echo "  1. Check prerequisites (doctl, git, docker)"
    echo "  2. Authenticate with DigitalOcean"
    echo "  3. Check configuration files"
    echo "  4. Optionally test locally with Docker Compose"
    echo "  5. Deploy to DigitalOcean App Platform"
    echo "  6. Run database migrations"
    echo "  7. Perform health checks"
    echo "  8. Display application information"
}

# Parse command line arguments
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    --non-interactive)
        main "$1"
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac

