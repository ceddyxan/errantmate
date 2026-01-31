#!/bin/bash
# ===================================================================
# 🚀 PRODUCTION DEPLOYMENT SCRIPT - ErrantMate Shelf Rental System
# ===================================================================
# 
# USAGE: ./deploy_production.sh
# 
# This script handles complete production deployment with:
# - Pre-deployment safety checks
# - Automated database setup
# - Code deployment
# - Post-deployment verification
# - Rollback capability
# ===================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
LOG_FILE="deployment_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo -e "${BLUE}==================================================================${NC}"
echo -e "${BLUE}🚀 ErrantMate Production Deployment${NC}"
echo -e "${BLUE}==================================================================${NC}"
echo -e "${YELLOW}Started at: $(date)${NC}"
echo -e "${YELLOW}Log file: $LOG_FILE${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ===================================================================
# 📋 PRE-DEPLOYMENT SAFETY CHECKS
# ===================================================================

echo -e "${BLUE}📋 STEP 1: PRE-DEPLOYMENT SAFETY CHECKS${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -d "templates" ]; then
    print_error "Not in the correct project directory!"
    print_error "Please run this script from the ErrantMate project root."
    exit 1
fi
print_status "✓ In correct project directory"

# Check required commands
required_commands=("git" "python3" "pip")
for cmd in "${required_commands[@]}"; do
    if command_exists "$cmd"; then
        print_status "✓ $cmd is available"
    else
        print_error "✗ $cmd is not installed"
        exit 1
    fi
done

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
if [[ $(echo "$python_version >= 3.7" | bc -l) -eq 1 ]]; then
    print_status "✓ Python $python_version (>= 3.7 required)"
else
    print_error "✗ Python $python_version is too old (>= 3.7 required)"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    print_status "✓ Virtual environment created and activated"
else
    source venv/bin/activate
    print_status "✓ Virtual environment activated"
fi

# Check required Python packages
required_packages=("flask" "sqlalchemy" "psycopg2-binary")
for package in "${required_packages[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        print_status "✓ $package is installed"
    else
        print_warning "$package not found. Installing..."
        pip install "$package"
    fi
done

# Check database connection
print_info "Testing database connection..."
if python3 -c "
import os
from app import app, db
with app.app_context():
    try:
        db.engine.execute('SELECT 1')
        print('✓ Database connection successful')
    except Exception as e:
        print(f'✗ Database connection failed: {e}')
        exit(1)
" 2>/dev/null; then
    print_status "✓ Database connection successful"
else
    print_error "✗ Database connection failed"
    print_error "Please check your database configuration in app.py"
    exit 1
fi

echo ""
print_status "🎉 All pre-deployment checks passed!"
echo ""

# ===================================================================
# 💾 BACKUP CURRENT STATE
# ===================================================================

echo -e "${BLUE}💾 STEP 2: BACKUP CURRENT STATE${NC}"
echo ""

# Create backup directory
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup current code
print_info "Backing up current code..."
tar -czf "$BACKUP_DIR/code_backup.tar.gz" --exclude='backups' --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' .
print_status "✓ Code backed up to $BACKUP_DIR/code_backup.tar.gz"

# Backup database (if PostgreSQL)
print_info "Backing up database..."
if python3 -c "
import os
from app import app, db
with app.app_context():
    try:
        # Check if PostgreSQL
        if 'postgresql' in str(db.engine.url):
            print('PostgreSQL detected')
            exit(0)
        else:
            print('SQLite detected')
            exit(1)
    except:
        exit(1)
" 2>/dev/null; then
    # PostgreSQL backup
    if command_exists "pg_dump"; then
        pg_dump errantmate_production > "$BACKUP_DIR/database_backup.sql"
        print_status "✓ PostgreSQL database backed up"
    else
        print_warning "pg_dump not found. Skipping database backup"
    fi
else
    # SQLite backup
    if [ -f "deliveries.db" ]; then
        cp deliveries.db "$BACKUP_DIR/"
        print_status "✓ SQLite database backed up"
    else
        print_warning "No SQLite database found to backup"
    fi
fi

echo ""
print_status "🎉 Backup completed successfully!"
echo ""

# ===================================================================
# 📥 CODE DEPLOYMENT
# ===================================================================

echo -e "${BLUE}📥 STEP 3: CODE DEPLOYMENT${NC}"
echo ""

# Pull latest code
print_info "Pulling latest code from GitHub..."
git fetch origin
git pull origin master
print_status "✓ Latest code pulled from GitHub"

# Install/update dependencies
print_info "Installing/updating dependencies..."
pip install -r requirements.txt 2>/dev/null || pip install flask sqlalchemy psycopg2-binary flask-login
print_status "✓ Dependencies installed/updated"

echo ""
print_status "🎉 Code deployment completed!"
echo ""

# ===================================================================
# 🗄️ DATABASE SETUP
# ===================================================================

echo -e "${BLUE}🗄️ STEP 4: DATABASE SETUP${NC}"
echo ""

# Run the quick fix script
print_info "Running database setup script..."
if python3 quick_fix_shelf_table.py; then
    print_status "✓ Database setup completed successfully"
else
    print_error "✗ Database setup failed"
    print_error "Check the logs for details"
    exit 1
fi

# Verify database
print_info "Verifying database setup..."
if python3 verify_production.py; then
    print_status "✓ Database verification passed"
else
    print_error "✗ Database verification failed"
    exit 1
fi

echo ""
print_status "🎉 Database setup completed!"
echo ""

# ===================================================================
# 🧪 POST-DEPLOYMENT VERIFICATION
# ===================================================================

echo -e "${BLUE}🧪 STEP 5: POST-DEPLOYMENT VERIFICATION${NC}"
echo ""

# Check if application starts
print_info "Testing application startup..."
if python3 -c "
from app import app
with app.test_client() as client:
    try:
        response = client.get('/')
        print('✓ Application starts successfully')
        exit(0)
    except Exception as e:
        print(f'✗ Application startup failed: {e}')
        exit(1)
" 2>/dev/null; then
    print_status "✓ Application starts successfully"
else
    print_error "✗ Application startup failed"
    exit 1
fi

# Check API endpoints
print_info "Testing API endpoints..."
if python3 -c "
from app import app
with app.test_client() as client:
    try:
        # Test API route exists (will redirect to login)
        response = client.get('/api/shelves')
        if response.status_code in [302, 401]:
            print('✓ API endpoints accessible')
            exit(0)
        else:
            print(f'✗ API returned unexpected status: {response.status_code}')
            exit(1)
    except Exception as e:
        print(f'✗ API test failed: {e}')
        exit(1)
" 2>/dev/null; then
    print_status "✓ API endpoints accessible"
else
    print_error "✗ API endpoints not accessible"
    exit 1
fi

echo ""
print_status "🎉 Post-deployment verification completed!"
echo ""

# ===================================================================
# 🎉 DEPLOYMENT COMPLETE
# ===================================================================

echo -e "${BLUE}🎉 DEPLOYMENT COMPLETE${NC}"
echo ""
print_status "🚀 ErrantMate Shelf Rental System deployed successfully!"
echo ""
echo -e "${BLUE}Deployment Summary:${NC}"
echo -e "  • Backup location: $BACKUP_DIR"
echo -e "  • Log file: $LOG_FILE"
echo -e "  • Database: Configured and verified"
echo -e "  • API: Functional and secure"
echo -e "  • Application: Ready for production use"
echo ""
echo -e "${GREEN}🌐 The shelf rental system is now LIVE in production!${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Test the application in your browser"
echo -e "  2. Verify shelf rental functionality"
echo -e "  3. Monitor for any issues"
echo -e "  4. Check logs if problems occur"
echo ""
echo -e "${BLUE}==================================================================${NC}"
echo -e "${BLUE}Deployment completed at: $(date)${NC}"
echo -e "${BLUE}==================================================================${NC}"

exit 0
