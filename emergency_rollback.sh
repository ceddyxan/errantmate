#!/bin/bash
# ===================================================================
# 🚨 EMERGENCY ROLLBACK SCRIPT - ErrantMate Production
# ===================================================================
# 
# USAGE: ./emergency_rollback.sh [backup_timestamp]
# 
# If no timestamp provided, uses the most recent backup
# ===================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo -e "${RED}🚨 EMERGENCY ROLLBACK - ErrantMate Production${NC}"
echo -e "${RED}================================================${NC}"
echo ""

# Get backup timestamp
if [ -z "$1" ]; then
    BACKUP_TIMESTAMP=$(ls -t backups/ | head -1 | sed 's/\///')
    print_warning "No backup specified, using most recent: $BACKUP_TIMESTAMP"
else
    BACKUP_TIMESTAMP="$1"
fi

BACKUP_DIR="backups/$BACKUP_TIMESTAMP"

if [ ! -d "$BACKUP_DIR" ]; then
    print_error "Backup directory not found: $BACKUP_DIR"
    print_error "Available backups:"
    ls -la backups/
    exit 1
fi

print_info "Using backup: $BACKUP_DIR"

# Confirm rollback
echo -e "${RED}⚠️  WARNING: This will rollback to a previous version!${NC}"
echo -e "${RED}⚠️  All recent changes will be LOST!${NC}"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    print_info "Rollback cancelled"
    exit 0
fi

# Stop application
print_info "Stopping application..."
if command -v systemctl >/dev/null 2>&1; then
    sudo systemctl stop errantmate || print_warning "Could not stop errantmate service"
fi

# Kill any running Python processes
pkill -f "python app.py" || true
pkill -f "gunicorn" || true

# Restore code
print_info "Restoring code from backup..."
tar -xzf "$BACKUP_DIR/code_backup.tar.gz" --strip-components=1

# Restore database
print_info "Restoring database..."
if [ -f "$BACKUP_DIR/database_backup.sql" ]; then
    # PostgreSQL
    print_info "Restoring PostgreSQL database..."
    psql errantmate_production < "$BACKUP_DIR/database_backup.sql"
elif [ -f "$BACKUP_DIR/deliveries.db" ]; then
    # SQLite
    print_info "Restoring SQLite database..."
    cp "$BACKUP_DIR/deliveries.db" .
else
    print_warning "No database backup found"
fi

# Restart application
print_info "Restarting application..."
if command -v systemctl >/dev/null 2>&1; then
    sudo systemctl start errantmate || print_warning "Could not start errantmate service"
else
    # Start manually
    nohup python app.py > app.log 2>&1 &
fi

# Verify rollback
print_info "Verifying rollback..."
sleep 5

if python verify_production.py; then
    print_status "🎉 Rollback completed successfully!"
    print_status "✅ Application is running with previous version"
else
    print_error "❌ Rollback verification failed"
    print_error "Please check the logs and manual intervention may be required"
    exit 1
fi

echo ""
print_status "🚨 Emergency rollback completed!"
print_info "Previous version is now running"
print_info "Backup used: $BACKUP_DIR"
