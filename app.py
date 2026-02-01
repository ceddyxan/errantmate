from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import inspect, text

from datetime import datetime, timedelta, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps

from collections import defaultdict

from logging.handlers import RotatingFileHandler



import csv

import io

import os

import platform

import secrets

import logging

import time



# Initialize Flask app

app = Flask(__name__)



# Secure secret key configuration

secret_key = os.environ.get('SECRET_KEY')

flask_env = os.environ.get('FLASK_ENV', 'development')

debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'



if not secret_key:

    if flask_env == 'development' or debug_mode:

        # Generate a secure random key for development

        secret_key = secrets.token_hex(32)

        print(f"Generated development secret key: {secret_key[:16]}...")

    else:

        raise ValueError("SECRET_KEY environment variable is required in production")

app.secret_key = secret_key



# Database configuration - PostgreSQL for production, SQLite for development

database_url = os.environ.get('DATABASE_URL')

flask_env = os.environ.get('FLASK_ENV', 'development')



if not database_url:

    # Default to SQLite for local development

    database_url = 'sqlite:///deliveries.db'

    print(f"Using SQLite for local development: {database_url}")



# For production, ensure PostgreSQL is used

if flask_env == 'production' and not database_url.startswith('postgres'):

    raise ValueError("DATABASE_URL must be a PostgreSQL connection string in production")



app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# Initialize database

db = SQLAlchemy(app)



# Automatic database migration function

def ensure_database_schema():

    """Ensure all required tables exist in the database"""

    with app.app_context():

        try:

            # Log database connection info

            app.logger.info(f"Database URL: {database_url}")

            app.logger.info(f"Flask Environment: {flask_env}")

            

            inspector = inspect(db.engine)

            existing_tables = inspector.get_table_names()

            app.logger.info(f"Existing tables: {existing_tables}")

            

            # Required tables for the application

            required_tables = ['users', 'delivery', 'audit_log']

            

            missing_tables = [table for table in required_tables if table not in existing_tables]

            

            if missing_tables:

                app.logger.info(f"Creating missing tables: {missing_tables}")

                

                # Try to create tables individually for better error handling

                for table_name in missing_tables:

                    try:

                        if table_name == 'users':

                            # Create users table specifically

                            from sqlalchemy import text

                            

                            # Check if we're using PostgreSQL

                            if database_url.startswith('postgres'):

                                db.session.execute(text("""

                                    CREATE TABLE IF NOT EXISTS users (

                                        id SERIAL PRIMARY KEY,

                                        username VARCHAR(80) UNIQUE NOT NULL,

                                        email VARCHAR(120) UNIQUE,

                                        phone_number VARCHAR(20) UNIQUE,

                                        password_hash VARCHAR(255) NOT NULL,

                                        role VARCHAR(20) DEFAULT 'user',

                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                                        is_active BOOLEAN DEFAULT TRUE

                                    )

                                """))

                            else:

                                # SQLite syntax

                                db.session.execute(text("""

                                    CREATE TABLE IF NOT EXISTS users (

                                        id INTEGER PRIMARY KEY AUTOINCREMENT,

                                        username VARCHAR(80) UNIQUE NOT NULL,

                                        email VARCHAR(120) UNIQUE,

                                        phone_number VARCHAR(20) UNIQUE,

                                        password_hash VARCHAR(255) NOT NULL,

                                        role VARCHAR(20) DEFAULT 'user',

                                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                                        is_active BOOLEAN DEFAULT TRUE

                                    )

                                """))

                            

                            db.session.commit()

                            app.logger.info(f"Successfully created users table")

                        else:

                            # For other tables, use SQLAlchemy's create_all

                            db.create_all()

                            app.logger.info(f"Successfully created {table_name} table")

                    except Exception as table_error:

                        app.logger.error(f"Failed to create {table_name} table: {str(table_error)}")

                        db.session.rollback()

                

                # Verify tables were created

                inspector = inspect(db.engine)

                new_tables = inspector.get_table_names()

                created_tables = [table for table in missing_tables if table in new_tables]

                

                if created_tables:

                    app.logger.info(f"Successfully created tables: {created_tables}")

                else:

                    app.logger.error(f"Failed to create tables: {missing_tables}")

                    # Don't fail in production, just log the error

                    if flask_env == 'production':

                        app.logger.warning("Continuing despite table creation failure - tables may need manual creation")

            else:

                app.logger.info("All required tables exist")

                

        except Exception as e:

            app.logger.error(f"Database migration error: {str(e)}")

            if flask_env == 'production':

                # In production, log error but continue (don't crash the app)

                app.logger.warning("Continuing despite migration error - manual table creation may be required")

            else:

                # In development, log the error but continue

                app.logger.warning("Continuing despite database setup error")



# Run automatic migration on startup

ensure_database_schema()





# Configure logging

if not app.debug:

    # Production logging configuration

    if not os.path.exists('logs'):

        os.mkdir('logs')

    

    file_handler = RotatingFileHandler('logs/errantmate.log', maxBytes=10240000, backupCount=10)

    file_handler.setFormatter(logging.Formatter(

        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'

    ))

    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)

    

    app.logger.setLevel(logging.INFO)

    app.logger.info('ErrantMate startup')

else:

    # Development logging

    logging.basicConfig(level=logging.DEBUG)



# Use simple datetime (browser local time will be set from frontend)



def get_current_time():

    """Get current datetime."""

    return datetime.now()



def get_local_time(current_time=None):

    """Get current time."""

    if current_time is None:

        return get_current_time()

    return current_time



# Rate limiting for login attempts

LOGIN_ATTEMPT_LIMIT = 5  # Max 5 attempts

LOGIN_ATTEMPT_WINDOW = 300  # 5 minutes window

login_attempts = defaultdict(list)



def is_rate_limited(ip_address):

    """Check if IP address is rate limited for login attempts."""

    now = time.time()

    # Remove old attempts outside the window

    login_attempts[ip_address] = [

        attempt_time for attempt_time in login_attempts[ip_address]

        if now - attempt_time < LOGIN_ATTEMPT_WINDOW

    ]

    

    # Check if limit exceeded

    if len(login_attempts[ip_address]) >= LOGIN_ATTEMPT_LIMIT:

        return True

    

    # Add current attempt

    login_attempts[ip_address].append(now)

    return False



# Initialize database tables with robust error handling

def ensure_database_tables():

    """Ensure database tables exist with simple, reliable approach."""

    try:

        with app.app_context():

            # Simple approach: just create all tables

            print("Creating database tables...")

            db.create_all()

            

            # Verify tables exist

            inspector = db.inspect(db.engine)

            tables = inspector.get_table_names()

            required_tables = ['user', 'delivery', 'audit_log']

            

            

            if all(table in tables for table in required_tables):

                print("All required tables exist")

                

                # Create default admin user if not exists

                try:

                    admin_user = User.query.filter_by(username='admin').first()

                    if not admin_user:

                        admin_user = User(

                            username='admin',

                            role='admin',

                            is_active=True

                        )

                        admin_user.set_password('ErrantMate@24!')

                        db.session.add(admin_user)

                        db.session.commit()

                        print("Default admin user created")

                    else:

                        print("Admin user already exists")

                except Exception as admin_error:

                    print(f"Warning: Could not create admin user: {admin_error}")

                

                return True

            else:

                missing = [table for table in required_tables if table not in tables]

                return False

                

    except Exception as e:

        print(f"Error: {e}")

        return False



# Models

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=True)

    phone_number = db.Column(db.String(20), unique=True, nullable=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default='user')  # 'admin', 'user', or 'staff'

    created_at = db.Column(db.DateTime, default=get_current_time)

    is_active = db.Column(db.Boolean, default=True)

    

    def set_password(self, password):

        self.password_hash = generate_password_hash(password)

    

    def check_password(self, password):

        return check_password_hash(self.password_hash, password)

    

    def is_admin(self):

        return self.role == 'admin'

    

    def __repr__(self):

        return f'<User {self.username} ({self.role})>'

    

    def is_staff(self):

        return self.role in ['admin', 'staff']

    

    def can_view_reports(self):

        return self.role == 'admin'



class Delivery(db.Model):

    __tablename__ = 'delivery'

    id = db.Column(db.Integer, primary_key=True)

    display_id = db.Column(db.String(20), unique=True, nullable=False)

    sender_name = db.Column(db.String(100), nullable=False)

    sender_phone = db.Column(db.String(20), nullable=False)

    recipient_name = db.Column(db.String(100), nullable=False)

    recipient_phone = db.Column(db.String(20), nullable=False)

    recipient_address = db.Column(db.String(200), nullable=False)

    delivery_person = db.Column(db.String(100), nullable=True)

    goods_type = db.Column(db.String(100), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)

    amount = db.Column(db.Float, nullable=False)

    expenses = db.Column(db.Float, default=0.0)

    payment_by = db.Column(db.String(50), nullable=False, default='M-Pesa')

    status = db.Column(db.String(20), default='Pending')

    created_at = db.Column(db.DateTime, default=get_current_time)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    

    # Relationship to User

    creator = db.relationship('User', backref='deliveries')



    def __repr__(self):

        return f'<Delivery {self.display_id}>'



class AuditLog(db.Model):

    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    username = db.Column(db.String(80), nullable=False)

    action = db.Column(db.String(100), nullable=False)  # LOGIN, LOGOUT, CREATE, UPDATE, DELETE, VIEW, EXPORT

    resource_type = db.Column(db.String(50), nullable=True)  # USER, DELIVERY, REPORT

    resource_id = db.Column(db.String(50), nullable=True)  # ID of the affected resource

    details = db.Column(db.Text, nullable=True)  # Additional details about the action

    ip_address = db.Column(db.String(45), nullable=True)  # User's IP address

    user_agent = db.Column(db.String(500), nullable=True)  # Browser/device info

    timestamp = db.Column(db.DateTime, default=get_current_time)

    

    # Relationship to User

    user = db.relationship('User', backref='audit_logs')

    

    def __repr__(self):

        return f'<AuditLog {self.action} by {self.username} at {self.timestamp}>'

class Shelf(db.Model):
    __tablename__ = 'shelf'
    
    id = db.Column(db.String(10), primary_key=True)  # e.g., A-01, B-02
    status = db.Column(db.String(20), default='available')  # available, occupied, maintenance
    size = db.Column(db.String(10), nullable=False)  # Small, Large
    price = db.Column(db.Integer, nullable=False)  # Monthly fee in KSh
    customer_name = db.Column(db.String(100), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=True)
    rented_date = db.Column(db.Date, nullable=True)
    items_description = db.Column(db.Text, nullable=True)
    rental_period = db.Column(db.Integer, nullable=True)  # in months
    maintenance_reason = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Shelf {self.id} - {self.status}>'

def generate_display_id():

    """Generate a unique display ID for new deliveries."""

    now = get_local_time()  # Use local time for display ID generation

    date_str = now.strftime('%y%m%d')

    

    # Get the last delivery for TODAY only to reset sequence daily

    today_start = get_current_time().replace(hour=0, minute=0, second=0, microsecond=0)

    today_deliveries = Delivery.query.filter(Delivery.created_at >= today_start).order_by(Delivery.created_at.desc()).all()

    

    # Count deliveries made today to determine the next sequence number

    today_count = len(today_deliveries)

    next_sequence = today_count + 1

    

    # Generate display ID

    display_id = f"{date_str}{str(next_sequence).zfill(4)}"

    

    # Check if this display_id already exists (race condition protection)

    max_attempts = 10

    for attempt in range(max_attempts):

        existing = Delivery.query.filter_by(display_id=display_id).first()

        if not existing:

            return display_id

        

        # If it exists, increment and try again

        next_sequence += 1

        display_id = f"{date_str}{str(next_sequence).zfill(4)}"

    

    # If we still have a conflict after max attempts, use a timestamp-based fallback

    import time

    timestamp_suffix = str(int(time.time()))[-4:]

    return f"{date_str}{timestamp_suffix}"



def get_date_ranges():

    """Get common date ranges used throughout the application."""

    now = get_local_time()

    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    

    # Week: Sunday to Saturday

    week_start = today - timedelta(days=today.weekday())

    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)

    

    # Month: First day to last day of current month

    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if now.month == 12:

        month_end = now.replace(year=now.year+1, month=1, day=1) - timedelta(microseconds=1)

    else:

        month_end = now.replace(month=now.month+1, day=1) - timedelta(microseconds=1)

    

    # Year: First day to last day of current year

    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    year_end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)

    

    return {

        'today': (today, today_end),

        'week': (week_start, week_end),

        'month': (month_start, month_end),

        'year': (year_start, year_end),

        'all': (datetime(2000, 1, 1), today_end)  # All time from year 2000

    }



@app.route('/create-admin')

def create_admin():

    """Create initial admin user (remove after use)."""

    try:

        # Check if admin already exists

        admin = User.query.filter_by(username='admin').first()

        if admin:

            return jsonify({'status': 'exists', 'message': 'Admin user already exists'})

        

        # Create admin user

        admin = User(

            username='admin',

            role='admin'

        )

        admin.set_password('ErrantMate@24!')  # Change this password!

        

        db.session.add(admin)

        db.session.commit()

        

        return jsonify({'status': 'success', 'message': 'Admin user created', 'username': 'admin', 'password': 'ErrantMate@24!'})

    except Exception as e:

        return jsonify({'status': 'error', 'error': str(e)}), 500



@app.route('/health')

def health_check():

    """Health check endpoint for Render."""

    try:

        # Test database connection

        db.session.execute(text('SELECT 1'))

        return jsonify({'status': 'healthy', 'database': 'connected'}), 200

    except Exception as e:

        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500



@app.route('/check-db')

def check_database():

    """Check database status and tables."""

    try:

        inspector = inspect(db.engine)

        tables = inspector.get_table_names()

        

        # Check if all required tables exist

        required_tables = ['user', 'delivery', 'audit_log']

        missing_tables = [table for table in required_tables if table not in tables]

        

        if missing_tables:

            return jsonify({

                'status': 'incomplete', 

                'message': f'Missing tables: {missing_tables}',

                'existing_tables': tables

            }), 200

        

        # Test queries

        user_count = User.query.count()

        delivery_count = Delivery.query.count()

        

        return jsonify({

            'status': 'ready',

            'message': 'Database is ready',

            'tables': tables,

            'users': user_count,

            'deliveries': delivery_count

        }), 200

        

    except Exception as e:

        return jsonify({'status': 'error', 'error': str(e)}), 500



@app.route('/init-db')

def init_database():

    """Initialize database tables (call once after deployment)."""

    try:

        with app.app_context():

            db.create_all()

            return jsonify({'status': 'success', 'message': 'Database initialized'}), 200

    except Exception as e:

        return jsonify({'status': 'error', 'error': str(e)}), 500



@app.route('/')

def dashboard():

    """Render the dashboard with operational statistics and overview."""

    try:

        # Get all deliveries for statistics

        deliveries = Delivery.query.order_by(Delivery.created_at.desc()).all()

        

        # Calculate statistics

        total_deliveries = len(deliveries)

        pending_count = len([d for d in deliveries if d.status == 'Pending'])

        in_transit_count = len([d for d in deliveries if d.status == 'In Transit'])

        delivered_count = len([d for d in deliveries if d.status == 'Delivered'])

        

        # Active deliveries (pending + in transit)

        active_deliveries = pending_count + in_transit_count

        

        # Today's completed deliveries

        today = get_current_time().date()

        completed_today = len([d for d in deliveries if d.status == 'Delivered' and d.created_at.date() == today])

        

        # Monthly completion rate

        current_month = get_current_time().date().replace(day=1)

        month_deliveries = [d for d in deliveries if d.created_at.date() >= current_month]

        month_delivered = [d for d in month_deliveries if d.status == 'Delivered']

        completion_rate = round((len(month_delivered) / len(month_deliveries) * 100), 1) if month_deliveries else 0

        

        # Today's deliveries (filter by date only, since database now stores browser local time)

        today_deliveries = [d for d in deliveries if d.created_at.date() == today]

        

        # Financial statistics

        total_revenue = sum(float(d.amount) for d in deliveries if d.amount)  # Use actual delivery amounts as revenue

        total_expenses = 0  # No operational costs by default

        

        recent_activities = []

        for delivery in deliveries[:10]:

            time_ago = get_time_ago(delivery.created_at) if delivery.created_at else "Unknown"

            recent_activities.append({

                'display_id': delivery.display_id,

                'status': delivery.status,

                'time_ago': time_ago,

                'created_at': delivery.created_at.isoformat() if delivery.created_at else None

            })

        

        # Convert deliveries to dictionaries for JSON serialization

        deliveries_dict = []

        for delivery in deliveries[:10]:

            time_ago = get_time_ago(delivery.created_at) if delivery.created_at else "Unknown"

            deliveries_dict.append({

                'id': delivery.id,

                'display_id': delivery.display_id,

                'sender_name': delivery.sender_name,

                'recipient_name': delivery.recipient_name,

                'recipient_address': delivery.recipient_address,

                'status': delivery.status,

                'created_at': delivery.created_at.isoformat() if delivery.created_at else None,

                'time_ago': get_time_ago(delivery.created_at) if delivery.created_at else "Unknown",

                'time_ago': time_ago,

                'delivery_person': delivery.delivery_person

            })

        

        return render_template('index.html', 

                             deliveries=deliveries_dict,

                             total_deliveries=total_deliveries,

                             active_deliveries=active_deliveries,

                             completed_today=completed_today,

                             completion_rate=completion_rate,

                             pending_count=pending_count,

                             in_transit_count=in_transit_count,

                             delivered_count=delivered_count,

                             today_deliveries=today_deliveries,

                             recent_activities=recent_activities,

                             total_revenue=total_revenue,

                             total_expenses=total_expenses)

    except Exception as e:

        app.logger.error(f"Error loading dashboard: {str(e)}")

        flash('An error occurred while loading the dashboard.', 'danger')

        return render_template('index.html', 

                             deliveries=[],

                             total_deliveries=0,

                             active_deliveries=0,

                             completed_today=0,

                             completion_rate=0,

                             pending_count=0,

                             in_transit_count=0,

                             delivered_count=0,

                             today_deliveries=[],

                             recent_activities=[],

                             total_revenue=0.0,

                             total_expenses=0.0)



def get_time_ago(created_at):

    """Calculate time ago string for a datetime."""

    if not created_at:

        return "Unknown"

    

    now = get_current_time()

    

    # Simple comparison since both are naive datetimes

    diff = now - created_at

    

    if diff.days > 0:

        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"

    elif diff.seconds > 3600:

        hours = diff.seconds // 3600

        return f"{hours} hour{'s' if hours > 1 else ''} ago"

    elif diff.seconds > 60:

        minutes = diff.seconds // 60

        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"

    else:

        return "Just now"



# Audit Logging Functions

def log_audit(action, resource_type=None, resource_id=None, details=None):

    """Log an audit event for security monitoring."""

    try:

        # Get user information from session

        user_id = session.get('user_id')

        username = session.get('username', 'Unknown')

        

        # Get request information

        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'Unknown'))

        user_agent = request.headers.get('User-Agent', 'Unknown')[:500]  # Limit length

        

        # Create audit log entry

        audit_log = AuditLog(

            user_id=user_id,

            username=username,

            action=action,

            resource_type=resource_type,

            resource_id=str(resource_id) if resource_id else None,

            details=details,

            ip_address=ip_address,

            user_agent=user_agent

        )

        

        db.session.add(audit_log)

        db.session.commit()

        

    except Exception as e:

        # Don't fail the main operation if audit logging fails

        app.logger.error(f"Error logging audit event: {str(e)}")

        db.session.rollback()



def log_login(user, success=True, reason=None):

    """Log login attempts."""

    action = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"

    details = f"Login attempt for user {user.username}"

    if not success:

        details += f" - {reason}" if reason else " - Invalid credentials"

    else:

        details += f" - Role: {user.role}"

    

    log_audit(action, resource_type="USER", resource_id=user.id, details=details)



def log_logout():

    """Log logout events."""

    username = session.get('username', 'Unknown')

    details = f"User {username} logged out"

    log_audit("LOGOUT", resource_type="USER", details=details)



def log_delivery_action(action, delivery_id, details=None):

    """Log delivery-related actions."""

    log_audit(action, resource_type="DELIVERY", resource_id=delivery_id, details=details)



def log_export(period, format='CSV'):

    """Log export actions."""

    details = f"Exported {period} report in {format} format"

    log_audit("EXPORT", resource_type="REPORT", details=details)



def log_page_view(page):

    """Log page views for monitoring."""

    details = f"Viewed {page} page"

    log_audit("VIEW", resource_type="PAGE", details=details)



# Database check decorator to prevent recurring errors

def database_required(f):

    """Decorator to ensure database tables exist before executing route."""

    @wraps(f)

    def decorated_function(*args, **kwargs):

        try:

            # Quick check if tables exist

            inspector = inspect(db.engine)

            tables = inspector.get_table_names()

            required_tables = ['user', 'delivery', 'audit_log']

            

            if not all(table in tables for table in required_tables):

                # Try to create tables if missing

                if not ensure_database_tables():

                    return jsonify({

                        'error': 'Database tables missing',

                        'message': 'Please visit /force-init-db to initialize database',

                        'status': 'database_error'

                    }), 503

            

            return f(*args, **kwargs)

            

        except Exception as e:

            return jsonify({

                'error': 'Database connection failed',

                'message': str(e),

                'status': 'database_error'

            }), 503

    return decorated_function



# Login required decorator

def login_required(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if 'user_id' not in session:

            return redirect(url_for('login', next=request.url))

        return f(*args, **kwargs)

    return decorated_function



# Admin required decorator

def admin_required(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if 'user_id' not in session:

            return redirect(url_for('login', next=request.url))

        if session.get('user_role') != 'admin':

            flash('Admin access required', 'danger')

            return redirect(url_for('add_delivery'))

        return f(*args, **kwargs)

    return decorated_function



# Login required decorator for API endpoints (returns JSON instead of redirects)

def login_required_api(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if 'user_id' not in session:

            return jsonify({

                'error': 'Authentication required',

                'redirect': '/login'

            }), 401

        return f(*args, **kwargs)

    return decorated_function



# Admin required decorator for API endpoints (returns JSON instead of redirects)

def admin_required_api(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if 'user_id' not in session:

            return jsonify({

                'error': 'Authentication required',

                'redirect': '/login'

            }), 401

        if session.get('user_role') != 'admin':

            return jsonify({

                'error': 'Admin access required'

            }), 403

        return f(*args, **kwargs)

    return decorated_function



# Staff required decorator for delivery person privileges

def staff_required(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if 'user_id' not in session:

            if request.is_json:

                return jsonify({'error': 'Authentication required'}), 401

            return redirect(url_for('login'))

        

        user = User.query.get(session['user_id'])

        if not user or not user.is_staff():

            if request.is_json:

                return jsonify({'error': 'Staff access required'}), 403

            flash('Staff access required for this operation', 'error')

            return redirect(url_for('dashboard'))

    

    return decorated_function



# Staff required decorator for API endpoints

def staff_required_api(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if 'user_id' not in session:

            return jsonify({'error': 'Authentication required'}), 401

        

        user = User.query.get(session['user_id'])

        if not user or not user.is_staff():

            return jsonify({'error': 'Staff access required'}), 403

    

    return decorated_function



@app.route('/reset-db')

@admin_required_api

def reset_database():

    """Reset database completely - admin only with confirmation."""

    # Require confirmation parameter

    confirm = request.args.get('confirm')

    if confirm != 'RESET_CONFIRMED':

        return jsonify({

            'status': 'error', 

            'error': 'Confirmation required. Add ?confirm=RESET_CONFIRMED to proceed'

        }), 400

    

    # Log the reset attempt

    user_id = session.get('user_id')

    username = session.get('username', 'Unknown')

    app.logger.warning(f"Database reset initiated by admin user {username} (ID: {user_id})")

    

    try:

        with app.app_context():

            # Drop all tables

            db.drop_all()

            # Create all tables fresh

            app.logger.info("Database tables dropped and recreated successfully")

            return jsonify({

                'status': 'success', 

                'message': 'Database reset successfully',

                'performed_by': username,

                'timestamp': get_current_time().isoformat()

            }), 200

    except Exception as e:

        app.logger.error(f"Database reset failed: {str(e)}")

        return jsonify({'status': 'error', 'error': str(e)}), 500



@app.route('/force-init-db')

@admin_required_api

def force_init_database():

    """Force database initialization with admin protection and confirmation."""

    # Require confirmation parameter

    confirm = request.args.get('confirm')

    if confirm != 'FORCE_INIT_CONFIRMED':

        return jsonify({

            'status': 'error', 

            'error': 'Confirmation required. Add ?confirm=FORCE_INIT_CONFIRMED to proceed'

        }), 400

    

    # Log the force init attempt

    user_id = session.get('user_id')

    username = session.get('username', 'Unknown')

    app.logger.warning(f"Database force initialization initiated by admin user {username} (ID: {user_id})")

    

    try:

        with app.app_context():

            

            # Drop all tables

            print("Dropping existing tables...")

            app.logger.info("Dropping existing database tables")

            db.drop_all()

            

            # Create all tables

            print("Creating tables...")

            app.logger.info("Creating fresh database tables")

            db.create_all()

            

            # Verify tables were created

            inspector = inspect(db.engine)

            tables = inspector.get_table_names()

            required_tables = ['user', 'delivery', 'audit_log']

            

            if all(table in tables for table in required_tables):

                

                # Create default admin user

                admin_user = User.query.filter_by(username='admin').first()

                if not admin_user:

                    admin_user = User(

                        username='admin',

                        role='admin',

                        is_active=True

                    )

                    admin_user.set_password('ErrantMate@24!')

                    db.session.add(admin_user)

                    db.session.commit()

                    print("Default admin user created")

                    app.logger.info("Default admin user created successfully")

                else:

                    print("Admin user already exists")

                    app.logger.info("Admin user already exists")

                

                return jsonify({

                    'status': 'success', 

                    'message': 'Database force initialized successfully',

                    'tables': tables,

                    'database_url': str(app.config['SQLALCHEMY_DATABASE_URI']),

                    'admin_created': True,

                    'performed_by': username,

                    'timestamp': get_current_time().isoformat()

                }), 200

            else:

                missing = [table for table in required_tables if table not in tables]

                raise Exception(f"Missing tables: {missing}")

            

    except Exception as e:

        import traceback

        error_details = traceback.format_exc()

        app.logger.error(f"Database force initialization failed: {str(e)}\n{error_details}")

        

        return jsonify({

            'status': 'error', 

            'error': str(e),

            'traceback': error_details

        }), 500



@app.route('/add_delivery', methods=['GET', 'POST'])

@login_required

@database_required

def add_delivery():

    """Handle adding a new delivery."""

    if request.method == 'GET':

        # Log page view

        log_page_view("Add Delivery")

    if request.method == 'POST':

        try:

            # Use browser local time if provided, otherwise use current time

            browser_local_time = request.form.get('browser_local_time')

            if browser_local_time:

                # Parse browser local time directly as naive datetime (no timezone conversion)

                current_time = datetime.fromisoformat(browser_local_time)

            else:

                # Fallback to current time if browser time not available

                current_time = get_current_time()

            

            delivery = Delivery(

                display_id=generate_display_id(),

                sender_name=request.form['sender_name'],

                sender_phone=request.form['sender_phone'],

                recipient_name=request.form['recipient_name'],

                recipient_phone=request.form['recipient_phone'],

                recipient_address=request.form['recipient_address'],

                goods_type=request.form['goods_type'],

                quantity=int(request.form['quantity']),

                amount=float(request.form['amount']),

                expenses=0.0,  # Will be set later via Quick Actions

                payment_by=request.form.get('payment_by', 'M-Pesa'),  # Use form value or default

                status=request.form.get('status', 'Pending'),

                created_at=current_time,  # Use browser local time

                created_by=session.get('user_id'),  # Set the creator

                delivery_person=session.get('username') if session.get('user_role') == 'staff' else None  # Auto-assign to staff users

            )

            db.session.add(delivery)

            db.session.commit()

            

            # Log delivery creation

            details = f"Created delivery {delivery.display_id}: {delivery.sender_name} -> {delivery.recipient_name} ({delivery.goods_type}, KSh{delivery.amount})"

            log_delivery_action("CREATE", delivery.id, details)

            

            flash('Delivery added successfully!', 'success')

            return redirect(url_for('add_delivery'))

        except Exception as e:

            db.session.rollback()

            app.logger.error(f"Error adding delivery: {str(e)}")

            

            # Check for specific database errors

            error_str = str(e).lower()

            if 'duplicate key' in error_str or 'unique constraint' in error_str:

                # Try again with a new display ID

                try:

                    # Generate a new display ID with timestamp fallback

                    import time

                    now = get_local_time()

                    date_str = now.strftime('%y%m%d')

                    timestamp_suffix = str(int(time.time()))[-4:]

                    new_display_id = f"{date_str}{timestamp_suffix}"

                    

                    delivery = Delivery(

                        display_id=new_display_id,

                        sender_name=request.form['sender_name'],

                        sender_phone=request.form['sender_phone'],

                        recipient_name=request.form['recipient_name'],

                        recipient_phone=request.form['recipient_phone'],

                        recipient_address=request.form['recipient_address'],

                        goods_type=request.form['goods_type'],

                        quantity=int(request.form['quantity']),

                        amount=float(request.form['amount']),

                        expenses=0.0,  # Will be set later via Quick Actions

                        payment_by=request.form.get('payment_by', 'M-Pesa'),  # Use form value or default

                        status=request.form.get('status', 'Pending'),

                        created_at=current_time,  # Use browser local time

                        created_by=session.get('user_id'),  # Set the creator

                        delivery_person=session.get('username') if session.get('user_role') == 'staff' else None  # Auto-assign to staff users

                    )

                    db.session.add(delivery)

                    db.session.commit()

                    

                    # Log delivery creation

                    details = f"Created delivery {delivery.display_id}: {delivery.sender_name} -> {delivery.recipient_name} ({delivery.goods_type}, KSh{delivery.amount})"

                    log_delivery_action("CREATE", delivery.id, details)

                    

                    flash('Delivery added successfully!', 'success')

                    return redirect(url_for('add_delivery'))

                    

                except Exception as retry_error:

                    db.session.rollback()

                    app.logger.error(f"Retry failed for delivery creation: {str(retry_error)}")

                    flash('System is experiencing high traffic. Please try again in a moment.', 'warning')

            else:

                flash('Error adding delivery. Please check the form and try again.', 'danger')

    return render_template('add_delivery.html')



@app.route('/api/update_delivery_status', methods=['POST'])

@login_required_api

@database_required

def api_update_delivery_status():

    """Update delivery status and assign delivery person for staff and admin users"""

    try:

        # Check if user is staff or admin

        user_id = session.get('user_id')

        if not user_id:

            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        

        user = User.query.get(user_id)

        if not user or not user.is_staff():

            return jsonify({'success': False, 'error': 'Staff or admin access required'}), 403

        

        data = request.get_json()

        delivery_id = data.get('delivery_id')

        new_status = data.get('status')

        delivery_person = data.get('delivery_person')

        

        if not delivery_id or not new_status:

            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        

        if new_status not in ['Pending', 'In Transit', 'Delivered']:

            return jsonify({'success': False, 'error': 'Invalid status'}), 400

        

        delivery = Delivery.query.get_or_404(delivery_id)

        

        # Additional validation: Staff users can only update their own assigned deliveries

        if user.role == 'staff' and delivery.delivery_person and delivery.delivery_person != user.username:

            return jsonify({

                'success': False, 

                'error': 'You can only update status for deliveries assigned to you'

            }), 403

        

        delivery.status = new_status

        

        # Only assign delivery person if it's provided (for staff users)

        if delivery_person:

            delivery.delivery_person = delivery_person

        

        db.session.commit()

        

        message = f'Status updated to {new_status}'

        if delivery_person:

            message += f' and assigned to {delivery_person}'

        

        return jsonify({

            'success': True,

            'message': message

        })

        

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error updating delivery status: {str(e)}")

        return jsonify({'success': False, 'error': 'Error updating delivery status'}), 500



@app.route('/update_status/<int:delivery_id>/<status>', methods=['GET', 'POST'])

@login_required

@database_required

def update_status(delivery_id, status):

    """Update the status of a delivery."""

    try:

        # Check if user is staff or admin

        user_id = session.get('user_id')

        if not user_id:

            if request.is_json:

                return jsonify({'success': False, 'error': 'Authentication required'}), 401

            return redirect(url_for('login'))

        

        user = User.query.get(user_id)

        if not user or not user.is_staff():

            if request.is_json:

                return jsonify({'success': False, 'error': 'Staff or admin access required'}), 403

            flash('Staff or admin access required', 'error')

            return redirect(url_for('dashboard'))

        

        delivery = Delivery.query.get_or_404(delivery_id)

        

        # Additional validation: Staff users can only update their own assigned deliveries

        if user.role == 'staff' and delivery.delivery_person and delivery.delivery_person != user.username:

            if request.is_json:

                return jsonify({

                    'success': False, 

                    'error': 'You can only update status for deliveries assigned to you'

                }), 403

            flash('You can only update status for deliveries assigned to you', 'error')

            return redirect(url_for('dashboard'))

        

        delivery.status = status

        db.session.commit()

        

        # Check if this is an AJAX request

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:

            return jsonify({

                'success': True,

                'message': f'Delivery status updated to {status}',

                'new_status': status

            })

        else:

            flash(f'Delivery status updated to {status}', 'success')

            return redirect(url_for('dashboard'))

            

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error updating status: {str(e)}")

        

        # Check if this is an AJAX request

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:

            return jsonify({

                'success': False,

                'error': 'Error updating status'

            }), 500

        else:

            flash('Error updating status', 'danger')

            return redirect(url_for('dashboard'))



@app.route('/delete_delivery/<int:delivery_id>', methods=['DELETE'])

@database_required

def delete_delivery(delivery_id):

    """Delete a delivery."""

    try:

        delivery = Delivery.query.get_or_404(delivery_id)

        db.session.delete(delivery)

        db.session.commit()

        return jsonify({'success': True, 'message': 'Delivery deleted successfully'})

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error deleting delivery: {str(e)}", exc_info=True)

        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/login', methods=['GET', 'POST'])

def login():

    """Handle user login."""

    if request.method == 'POST':

        # Get client IP for rate limiting

        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))

        

        # Check rate limiting

        if is_rate_limited(client_ip):

            app.logger.warning(f'Rate limit exceeded for IP: {client_ip}')

            flash('Too many login attempts. Please try again later.', 'danger')

            return render_template('login.html')

        

        username = request.form.get('username', '').strip()

        password = request.form.get('password', '')

        

        if not username or not password:

            flash('Please enter both username and password', 'danger')

            return render_template('login.html')

        

        user = User.query.filter_by(username=username).first()

        

        if user and user.check_password(password) and user.is_active:

            session['user_id'] = user.id

            session['username'] = user.username

            session['user_role'] = user.role  # Store user role in session

            session.permanent = True

            

            # Log successful login

            log_login(user, success=True)

            

            # Redirect to the page they were trying to access, or role-appropriate page

            next_page = request.args.get('next')

            if next_page:

                return redirect(next_page)

            

            # Role-based redirect

            if user.role == 'admin':

                return redirect(url_for('reports'))

            elif user.role == 'staff':

                return redirect(url_for('add_delivery'))

            else:

                return redirect(url_for('add_delivery'))

        else:

            # Log failed login attempt

            if username:

                # Try to get user for logging (even if password is wrong)

                user = User.query.filter_by(username=username).first()

                if user:

                    log_login(user, success=False, reason="Invalid password")

                else:

                    log_login(User(username=username, id=0), success=False, reason="User not found")

            flash('Invalid username or password', 'danger')

    

    return render_template('login.html')



@app.route('/logout')

def logout():

    """Handle user logout."""

    # Log logout before clearing session

    log_logout()

    session.clear()

    flash('You have been logged out successfully', 'info')

    return redirect(url_for('login'))



@app.route('/reports')

@admin_required

@database_required

def reports():

    """Render the reports page - Admin only."""

    try:

        # Log page view

        log_page_view("Reports")

        # Get recent deliveries (last 10)

        recent_deliveries = Delivery.query.order_by(Delivery.created_at.desc()).limit(10).all()

        return render_template('reports.html', recent_deliveries=recent_deliveries)

    except Exception as e:

        app.logger.error(f"Error loading reports page: {str(e)}", exc_info=True)

        return render_template('reports.html', recent_deliveries=[])



@app.route('/rent_shelf')

@login_required

@database_required

def rent_shelf():

    """Render the rent a shelf page - Available to all users."""

    try:

        # Log page view

        log_page_view("Rent a Shelf")

        

        # Get initial shelf data for server-side rendering
        shelves = Shelf.query.all()
        shelves_data = []
        
        for shelf in shelves:
            shelf_dict = {
                'id': shelf.id,
                'status': shelf.status,
                'size': shelf.size,
                'price': shelf.price,
                'customer': shelf.customer_name,
                'phone': shelf.customer_phone,
                'rentedDate': shelf.rented_date.strftime('%Y-%m-%d') if shelf.rented_date else None,
                'itemsDescription': shelf.items_description,
                'rentalPeriod': shelf.rental_period,
                'reason': shelf.maintenance_reason
            }
            shelves_data.append(shelf_dict)

        return render_template('rent_shelf.html', shelves_data=shelves_data)

    except Exception as e:

        app.logger.error(f"Error loading rent shelf page: {str(e)}", exc_info=True)

        return render_template('rent_shelf.html')

@app.route('/api/shelves', methods=['GET'])
@login_required
@database_required
def get_shelves():
    """Get all shelves with role-based filtering."""
    try:
        shelves = Shelf.query.all()
        shelves_data = []
        
        for shelf in shelves:
            shelf_dict = {
                'id': shelf.id,
                'status': shelf.status,
                'size': shelf.size,
                'price': shelf.price,
                'customer': shelf.customer_name,
                'phone': shelf.customer_phone,
                'rentedDate': shelf.rented_date.strftime('%Y-%m-%d') if shelf.rented_date else None,
                'itemsDescription': shelf.items_description,
                'rentalPeriod': shelf.rental_period,
                'reason': shelf.maintenance_reason
            }
            shelves_data.append(shelf_dict)
        
        return jsonify(shelves_data), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching shelves: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/test/db', methods=['GET'])
@login_required
@database_required
def test_database():
    """Test database connection and shelf table."""
    try:
        # Test basic database connection
        shelves = Shelf.query.limit(1).all()
        app.logger.info(f"Database test successful - found {len(shelves)} shelves")
        
        return jsonify({
            'success': True,
            'message': 'Database connection successful',
            'shelves_found': len(shelves)
        })
    except Exception as e:
        app.logger.error(f"Database test failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Database connection failed'
        }), 500

@app.route('/api/debug/rent', methods=['POST'])
@login_required
@database_required
def debug_rent_shelf():
    """Debug endpoint to see what data is being sent."""
    try:
        data = request.get_json()
        app.logger.info(f"DEBUG: Raw request data: {data}")
        app.logger.info(f"DEBUG: Request headers: {dict(request.headers)}")
        
        return jsonify({
            'success': True,
            'received_data': data,
            'message': 'Debug endpoint - check logs for details'
        })
    except Exception as e:
        app.logger.error(f"DEBUG endpoint error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Debug endpoint failed'
        }), 500

@app.route('/api/shelves/rent', methods=['POST'])
@login_required
@database_required
def rent_shelf_api():
    """Rent a shelf - update shelf status and customer information."""
    try:
        data = request.get_json()
        
        # Log the received data for debugging
        app.logger.info(f"Received rent shelf request data: {data}")
        
        shelf_id = data.get('shelfId')  # Changed from shelf_id to shelfId
        customer_name = data.get('customerName')  # Changed from customerName to customer_name
        customer_phone = data.get('customerPhone')  # Changed from customerPhone to customer_phone
        items_description = data.get('itemsDescription')  # Changed from itemsDescription to items_description
        rental_period = data.get('rentalPeriod')  # Changed from rentalPeriod to rental_period
        
        # Log extracted fields for debugging
        app.logger.info(f"Extracted fields - shelfId: {shelf_id}, customerName: {customer_name}, customerPhone: {customer_phone}")
        
        # Validate required fields
        if not shelf_id or not customer_name or not customer_phone:
            app.logger.warning(f"Missing required fields - shelfId: {shelf_id}, customerName: {customer_name}, customerPhone: {customer_phone}")
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Find the shelf
        shelf = Shelf.query.filter_by(id=shelf_id).first()
        if not shelf:
            return jsonify({'success': False, 'error': 'Shelf not found'}), 404
        
        # Check if shelf is available
        if shelf.status != 'available':
            return jsonify({'success': False, 'error': 'Shelf is not available'}), 400
        
        # Update shelf information
        shelf.status = 'occupied'
        shelf.customer_name = customer_name
        shelf.customer_phone = customer_phone
        shelf.rented_date = datetime.utcnow().date()
        shelf.items_description = items_description
        shelf.rental_period = rental_period
        shelf.maintenance_reason = None  # Clear any maintenance reason
        shelf.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            app.logger.info(f"Successfully committed shelf rental for {shelf_id}")
        except Exception as db_error:
            app.logger.error(f"Database commit error: {str(db_error)}", exc_info=True)
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Database error occurred'}), 500
        
        # Log the action
        try:
            log_action(
                username=session.get('username', 'unknown'),
                action=f"Rented shelf {shelf_id} to {customer_name}",
                details=f"Phone: {customer_phone}, Period: {rental_period} months"
            )
            app.logger.info(f"Successfully logged rental action for {shelf_id}")
        except Exception as log_error:
            app.logger.warning(f"Failed to log action but rental succeeded: {str(log_error)}")
            # Don't fail the request if logging fails
        
        return jsonify({
            'success': True, 
            'message': f'Shelf {shelf_id} successfully rented to {customer_name}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error renting shelf: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/shelves/stats', methods=['GET'])
@login_required
@database_required
def get_shelf_stats():
    """Get shelf statistics for reports."""
    try:
        available = Shelf.query.filter_by(status='available').count()
        occupied = Shelf.query.filter_by(status='occupied').count()
        maintenance = Shelf.query.filter_by(status='maintenance').count()
        
        # Calculate monthly revenue from occupied shelves
        occupied_shelves = Shelf.query.filter_by(status='occupied').all()
        revenue = sum(shelf.price for shelf in occupied_shelves)
        
        return jsonify({
            'available': available,
            'occupied': occupied,
            'maintenance': maintenance,
            'revenue': revenue
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching shelf stats: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500



@app.route('/get_delivery_persons')

@staff_required

@database_required

def get_delivery_persons():

    """Get delivery persons and their delivery counts for a specific period."""

    try:

        # Get period parameter from query string

        period = request.args.get('period', 'all')

        

        # Calculate date range based on period

        end_date = get_current_time()

        if period == 'today':

            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        elif period == 'week':

            start_date = end_date - timedelta(days=7)

        elif period == 'month':

            start_date = end_date - timedelta(days=30)

        else:  # all

            start_date = end_date - timedelta(days=365)  # Limit to 1 year for performance

        

        # Get all staff users (admin and staff roles)

        staff_users = User.query.filter(User.role.in_(['admin', 'staff']), User.is_active == True).all()

        

        # Get all deliveries with non-empty delivery person within the date range

        deliveries = Delivery.query.filter(

            Delivery.delivery_person != '',

            Delivery.delivery_person.isnot(None),

            Delivery.created_at.between(start_date, end_date)

        ).all()

        

        persons_data = {}

        for delivery in deliveries:

            person = delivery.delivery_person or 'Unknown'

            if person not in persons_data:

                persons_data[person] = {

                    'name': person,

                    'deliveries': 0,

                    'revenue': 0.0,

                    'completed': 0,

                    'pending_count': 0,

                    'delivered_count': 0,

                    'daily_deliveries': {}

                }

            

            persons_data[person]['deliveries'] += 1

            persons_data[person]['revenue'] += float(delivery.amount or 0)

            if delivery.status == 'Delivered':

                persons_data[person]['completed'] += 1

            

            # Count pending deliveries

            if delivery.status == 'Pending':

                persons_data[person]['pending_count'] += 1

            

            # Count delivered deliveries

            if delivery.status == 'Delivered' or delivery.status == 'delivered':

                persons_data[person]['delivered_count'] += 1

            

            # Group by date

            delivery_date = delivery.created_at.strftime('%Y-%m-%d')

            if delivery_date not in persons_data[person]['daily_deliveries']:

                persons_data[person]['daily_deliveries'][delivery_date] = []

            

            persons_data[person]['daily_deliveries'][delivery_date].append({

                'display_id': delivery.display_id,

                'amount': float(delivery.amount) if delivery.amount else 0.0,

                'expenses': float(delivery.expenses) if delivery.expenses else 0.0,

                'status': delivery.status

            })

        

        # Add staff users who haven't been assigned deliveries yet

        for staff_user in staff_users:

            if staff_user.username not in persons_data:

                persons_data[staff_user.username] = {

                    'name': staff_user.username,

                    'deliveries': 0,

                    'revenue': 0.0,

                    'completed': 0,

                    'pending_count': 0,

                    'delivered_count': 0,

                    'daily_deliveries': {}

                }

        

        # Convert to list and sort by delivery count (descending)

        result = list(persons_data.values())

        result.sort(key=lambda x: x['deliveries'], reverse=True)

        

        return jsonify(result)

    except Exception as e:

        app.logger.error(f"Error getting delivery persons: {str(e)}")

        return jsonify([])



@app.route('/get_summary')

@admin_required

@database_required

def get_summary():

    """Get summary statistics for deliveries."""

    try:

        dates = get_date_ranges()

        

        # Get all deliveries for detailed filtering

        all_deliveries = Delivery.query.order_by(Delivery.created_at.desc()).all()

        

        # Convert deliveries to dictionary format for JSON response

        deliveries_data = []

        for delivery in all_deliveries:

            delivery_dict = {

                'id': delivery.id,

                'display_id': delivery.display_id,

                'sender_name': delivery.sender_name,

                'recipient_name': delivery.recipient_name,

                'status': delivery.status,

                'amount': float(delivery.amount) if delivery.amount else 0.0,

                'expenses': float(delivery.expenses) if delivery.expenses else 0.0,

                'delivery_person': delivery.delivery_person or '',

                'created_at': delivery.created_at.isoformat() if delivery.created_at else None,

                'time_ago': get_time_ago(delivery.created_at) if delivery.created_at else "Unknown"

            }

            deliveries_data.append(delivery_dict)

        

        def get_summary_data(query):

            """Helper function to get summary data for a query."""

            deliveries = query.all()

            total_amount = sum(float(d.amount) for d in deliveries if d.amount)  # Use actual delivery amounts as revenue
            total_expenses = 0  # No operational costs by default

            return {

                'total_deliveries': len(deliveries),

                'total_amount': total_amount,

                'total_expenses': total_expenses,

                'pending': len([d for d in deliveries if d.status == 'Pending']),

                'in_transit': len([d for d in deliveries if d.status == 'In Transit']),

                'delivered': len([d for d in deliveries if d.status == 'Delivered'])

            }

        

        return jsonify({

            'deliveries': deliveries_data,  # Add individual delivery records

            'summary': {

                'total_revenue': sum(float(d.amount) for d in all_deliveries if d.amount),  # Use actual delivery amounts as revenue
                'total_expenses': 0,  # No operational costs by default
                'total_deliveries': len(all_deliveries),

                'pending': len([d for d in all_deliveries if d.status == 'Pending']),

                'in_transit': len([d for d in all_deliveries if d.status == 'In Transit']),

                'delivered': len([d for d in all_deliveries if d.status == 'Delivered'])

            },

            'today': get_summary_data(Delivery.query.filter(Delivery.created_at >= dates['today'][0])),

            'week': get_summary_data(Delivery.query.filter(Delivery.created_at >= dates['week'][0])),

            'month': get_summary_data(Delivery.query.filter(Delivery.created_at >= dates['month'][0])),

            'year': get_summary_data(Delivery.query.filter(Delivery.created_at >= dates['year'][0])),

            'all': get_summary_data(Delivery.query.filter(Delivery.created_at >= dates['all'][0]))

        })

    except Exception as e:

        app.logger.error(f"Error getting summary: {str(e)}")

        return jsonify({'error': str(e)}), 500



@app.route('/export/<period>')

@login_required

@database_required

def export(period):

    """Export deliveries data as CSV for the specified period."""

    try:

        date_ranges = get_date_ranges()

        

        # Define date ranges using the new format

        if period == 'daily':

            start_date, end_date = date_ranges['today']

            filename = f'deliveries_{get_current_time().strftime("%Y-%m-%d")}.csv'

            date_range = 'today'

        elif period == 'weekly':

            start_date, end_date = date_ranges['week']

            filename = f'deliveries_week_{get_current_time().strftime("%Y-%U")}.csv'

            date_range = 'this week'

        elif period == 'monthly':

            start_date, end_date = date_ranges['month']

            filename = f'deliveries_{get_current_time().strftime("%Y-%m")}.csv'

            date_range = 'this month'

        elif period == 'yearly':

            start_date, end_date = date_ranges['year']

            filename = f'deliveries_{get_current_time().year}.csv'

            date_range = 'this year'

        elif period == 'all':

            start_date, end_date = date_ranges['all']

            filename = f'deliveries_all_time_{get_current_time().strftime("%Y-%m-%d")}.csv'

            date_range = 'all time'

        else:  # default to yearly for backward compatibility

            start_date, end_date = date_ranges['year']

            filename = f'deliveries_{get_current_time().year}.csv'

            date_range = 'this year'

        

        # Query deliveries

        deliveries = Delivery.query.filter(

            Delivery.created_at.between(start_date, end_date)

        ).order_by(Delivery.created_at.desc()).all()

        

        if not deliveries:

            flash(f'No delivery records found for {date_range}.', 'info')

            return redirect(url_for('reports'))

        

        # Generate CSV

        si = io.StringIO()

        writer = csv.writer(si)

        

        # Write header

        writer.writerow([

            'ID', 'Display ID', 'Sender', 'Recipient', 'Delivery Person',

            'Goods Type', 'Quantity', 'Amount (KSh)', 'Expenses (KSh)', 'Profit (KSh)', 'Status', 'Created At'

        ])

        

        # Write data

        for delivery in deliveries:

            profit = delivery.amount - delivery.expenses

            writer.writerow([

                str(delivery.id),

                f"'{delivery.display_id}",

                delivery.sender_name,

                delivery.recipient_name,

                delivery.delivery_person,

                delivery.goods_type,

                delivery.quantity,

                f"{delivery.amount:.2f}",

                f"{delivery.expenses:.2f}",

                f"{profit:.2f}",

                delivery.status,

                delivery.created_at.strftime('%Y-%m-%d %H:%M')

            ])

        

        # Log export action

        log_export(date_range, 'CSV')

        

        # Create response

        response = make_response(si.getvalue().encode('utf-8'))

        response.headers['Content-Disposition'] = f'attachment; filename={filename}'

        response.headers['Content-type'] = 'text/csv; charset=utf-8'

        return response

        

    except Exception as e:

        app.logger.error(f"Error exporting {period} data: {str(e)}")

        flash(f'Error exporting {period} data: {str(e)}', 'danger')

        return jsonify({'error': str(e)}), 500



@app.route('/get_delivery_details/<int:delivery_id>')

@login_required

@database_required

def get_delivery_details(delivery_id):

    """Get detailed information for a specific delivery."""

    try:

        delivery = Delivery.query.get(delivery_id)

        if not delivery:

            return jsonify({'error': 'Delivery not found'}), 404

        

        # Convert delivery to dictionary for JSON response - only use existing fields

        delivery_data = {

            'id': delivery.id,

            'display_id': delivery.display_id,

            'sender_name': delivery.sender_name,

            'sender_phone': delivery.sender_phone,

            'sender_address': '',  # Field doesn't exist in model

            'recipient_name': delivery.recipient_name,

            'recipient_phone': delivery.recipient_phone,

            'recipient_address': delivery.recipient_address,

            'status': delivery.status,

            'amount': delivery.amount,

            'expenses': delivery.expenses,

            'delivery_person': delivery.delivery_person,

            'notes': '',  # Field doesn't exist in model

            'goods_type': delivery.goods_type,

            'quantity': delivery.quantity,

            'payment_by': delivery.payment_by,

            'created_at': delivery.created_at.isoformat() if delivery.created_at else None,

                'time_ago': get_time_ago(delivery.created_at) if delivery.created_at else "Unknown",

            'updated_at': delivery.created_at.isoformat() if delivery.created_at else None  # Use created_at since updated_at doesn't exist

        }

        

        return jsonify(delivery_data)

        

    except Exception as e:

        app.logger.error(f"Error getting delivery details for ID {delivery_id}: {str(e)}")

        return jsonify({'error': 'Failed to load delivery details'}), 500



@app.route('/get_delivery_by_display_id/<display_id>')

@login_required

@database_required

def get_delivery_by_display_id(display_id):

    """Get delivery details by display ID (for Quick Reassign functionality)."""

    try:

        delivery = Delivery.query.filter_by(display_id=display_id).first()

        if not delivery:

            return jsonify({'error': 'Delivery not found'}), 404

        

        # Convert delivery to dictionary for JSON response

        delivery_data = {

            'id': delivery.id,

            'display_id': delivery.display_id,

            'sender_name': delivery.sender_name,

            'sender_phone': delivery.sender_phone,

            'sender_address': '',  # Field doesn't exist in model

            'recipient_name': delivery.recipient_name,

            'recipient_phone': delivery.recipient_phone,

            'recipient_address': delivery.recipient_address,

            'status': delivery.status,

            'amount': delivery.amount,

            'expenses': delivery.expenses,

            'delivery_person': delivery.delivery_person,

            'notes': '',  # Field doesn't exist in model

            'goods_type': delivery.goods_type,

            'quantity': delivery.quantity,

            'payment_by': delivery.payment_by,

            'created_at': delivery.created_at.isoformat() if delivery.created_at else None,

            'time_ago': get_time_ago(delivery.created_at) if delivery.created_at else "Unknown",

            'updated_at': delivery.created_at.isoformat() if delivery.created_at else None  # Use created_at since updated_at doesn't exist

        }

        

        return jsonify(delivery_data)

        

    except Exception as e:

        app.logger.error(f"Error getting delivery details for display ID {display_id}: {str(e)}")

        return jsonify({'error': 'Failed to load delivery details'}), 500



def normalize_phone_number(phone):

    """Normalize phone number to a standard format for comparison."""

    if not phone:

        return phone

    

    # Remove all non-digit characters

    digits_only = ''.join(c for c in phone if c.isdigit())

    

    # If starts with '254' (Kenya country code), keep as is

    if digits_only.startswith('254') and len(digits_only) >= 12:

        return digits_only

    

    # If starts with '0' and has 10 digits (Kenyan local format), convert to international

    if digits_only.startswith('0') and len(digits_only) == 10:

        return '254' + digits_only[1:]

    

    # If starts with '7' or '1' and has 9 digits (Kenyan mobile without prefix), add 254

    if len(digits_only) == 9 and (digits_only.startswith('7') or digits_only.startswith('1')):

        return '254' + digits_only

    

    # Otherwise return as is

    return digits_only



@app.route('/search_delivery_by_display_id', methods=['GET'])

@database_required

def search_delivery_by_display_id():

    """Search delivery by Display ID or Phone Number for dashboard search functionality."""

    try:

        search_query = request.args.get('display_id', '').strip()

        

        if not search_query:

            return jsonify({'success': False, 'error': 'Search value is required'}), 400

        

        delivery = None

        

        # First try to search by Display ID

        delivery = Delivery.query.filter_by(display_id=search_query).first()

        

        # If not found by Display ID, try searching by Phone Number

        if not delivery:

            # Clean phone number - remove spaces, dashes, plus signs, etc.

            cleaned_phone = ''.join(c for c in search_query if c.isdigit())

            if len(cleaned_phone) >= 9:  # Only search if we have at least 9 digits

                # Normalize the search phone number

                normalized_search = normalize_phone_number(cleaned_phone)

                

                # Get all deliveries and check phone numbers manually for better matching

                all_deliveries = Delivery.query.all()

                for d in all_deliveries:

                    # Clean and normalize the stored phone number

                    stored_phone_clean = ''.join(c for c in d.recipient_phone if c.isdigit())

                    normalized_stored = normalize_phone_number(stored_phone_clean)

                    

                    # Check if normalized numbers match or if one contains the other

                    if (normalized_search == normalized_stored or 

                        normalized_search in stored_phone_clean or 

                        stored_phone_clean.endswith(normalized_search[-9:]) or

                        normalized_search.endswith(stored_phone_clean[-9:])):

                        delivery = d

                        break

        

        if not delivery:

            return jsonify({'success': False, 'error': 'Delivery not found'}), 404

        

        # Return only the required fields: Display ID, Recipient Name, Recipient Number, Status

        delivery_data = {

            'display_id': delivery.display_id,

            'recipient_name': delivery.recipient_name,

            'recipient_phone': delivery.recipient_phone,

            'status': delivery.status

        }

        

        return jsonify({'success': True, 'delivery': delivery_data})

        

    except Exception as e:

        app.logger.error(f"Error searching delivery by query '{search_query}': {str(e)}")

        return jsonify({'success': False, 'error': 'Search failed'}), 500



@app.route('/update_delivery/<int:delivery_id>', methods=['PUT'])

@login_required

@database_required

def update_delivery_details(delivery_id):

    """Update delivery details."""

    try:

        delivery = Delivery.query.get(delivery_id)

        if not delivery:

            return jsonify({'error': 'Delivery not found'}), 404

        

        data = request.get_json()

        if not data:

            return jsonify({'error': 'No data provided'}), 400

        

        # Update delivery fields

        delivery.sender_name = data.get('sender_name', delivery.sender_name)

        delivery.sender_phone = data.get('sender_phone', delivery.sender_phone)

        delivery.recipient_name = data.get('recipient_name', delivery.recipient_name)

        delivery.recipient_phone = data.get('recipient_phone', delivery.recipient_phone)

        delivery.recipient_address = data.get('recipient_address', delivery.recipient_address)

        delivery.goods_type = data.get('goods_type', delivery.goods_type)

        delivery.quantity = data.get('quantity', delivery.quantity)

        delivery.amount = data.get('amount', delivery.amount)

        delivery.payment_by = data.get('payment_by', delivery.payment_by)  # Use form value or keep existing

        delivery.status = data.get('status', delivery.status)

        

        db.session.commit()

        

        return jsonify({

            'success': True, 

            'message': 'Delivery updated successfully'

        })

        

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error updating delivery {delivery_id}: {str(e)}")

        return jsonify({'error': 'Failed to update delivery'}), 500



@app.route('/get_unassigned_deliveries')

@login_required

@database_required

def get_unassigned_deliveries():

    """Get deliveries that don't have a delivery person assigned."""

    try:

        # Get deliveries where delivery_person is null, empty, or not assigned

        unassigned_deliveries = Delivery.query.filter(

            (Delivery.delivery_person.is_(None)) | 

            (Delivery.delivery_person == '') |

            (Delivery.delivery_person == 'None')

        ).order_by(Delivery.created_at.desc()).limit(20).all()

        

        deliveries_data = []

        for delivery in unassigned_deliveries:

            deliveries_data.append({

                'id': delivery.id,

                'display_id': delivery.display_id,

                'sender_name': delivery.sender_name,

                'recipient_name': delivery.recipient_name,

                'created_at': delivery.created_at.strftime('%Y-%m-%d %H:%M')

            })

        

        return jsonify(deliveries_data)

    except Exception as e:

        app.logger.error(f"Error fetching unassigned deliveries: {str(e)}")

        return jsonify([])



@app.route('/get_users')

@admin_required_api

@database_required

def get_users():

    """Get all users for admin management."""

    try:

        # Get all users (both active and inactive)

        users = User.query.order_by(User.is_active.desc(), User.username).all()

        users_data = []

        for user in users:

            users_data.append({

                'id': user.id,

                'username': user.username,

                'role': user.role,

                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else None,

                'is_active': user.is_active,

                'is_admin': user.is_admin()

            })

        return jsonify(users_data)

    except Exception as e:

        app.logger.error(f"Error getting users: {str(e)}")

        return jsonify({'error': 'Failed to load users'}), 500



@app.route('/debug/test_db')

def debug_test_db():

    """Test database connectivity and basic operations."""

    try:

        # Test basic database connection using raw SQL

        result = db.session.execute('SELECT 1')

        test_row = result.fetchone()

        

        # Test User model

        user_count = User.query.count()

        

        # Test creating a test user (and rollback)

        test_user = User(username='test_user_debug', role='user')

        test_user.set_password('test123')

        db.session.add(test_user)

        db.session.flush()  # Don't commit yet

        

        test_user_id = test_user.id

        db.session.rollback()  # Rollback the test user

        

        return jsonify({

            'success': True,

            'message': 'Database is working correctly',

            'details': {

                'connection': 'OK',

                'test_query_result': str(test_row),

                'user_count': user_count,

                'test_user_id_created': test_user_id,

                'test_user_rollback': 'OK'

            }

        })

        

    except Exception as e:

        return jsonify({

            'success': False,

            'error': str(e),

            'message': 'Database test failed'

        }), 500



@app.route('/debug/session')

def debug_session():

    """Debug endpoint to check session and authentication state."""

    session_info = {

        'session_data': dict(session),

        'is_authenticated': 'user_id' in session,

        'user_role': session.get('user_role'),

        'username': session.get('username')

    }

    

    # Check if admin user exists

    try:

        admin_user = User.query.filter_by(username='admin').first()

        session_info['admin_user_exists'] = admin_user is not None

        if admin_user:

            session_info['admin_user_active'] = admin_user.is_active

            session_info['admin_user_role'] = admin_user.role

    except Exception as e:

        session_info['admin_user_check_error'] = str(e)

    

    # Count total users

    try:

        user_count = User.query.count()

        session_info['total_users'] = user_count

    except Exception as e:

        session_info['user_count_error'] = str(e)

    

    return jsonify(session_info)



@app.route('/debug/check_users', methods=['GET'])

@admin_required

@database_required

def debug_check_users():

    """Debug endpoint to check all users in production"""

    try:

        users = User.query.order_by(User.username).all()

        user_list = []

        

        for user in users:

            user_list.append({

                'username': user.username,

                'role': user.role,

                'is_active': user.is_active,

                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else None

            })

        

        # Check for Peter specifically

        peter_users = [u for u in user_list if 'peter' in u['username'].lower()]

        

        return jsonify({

            'all_users': user_list,

            'peter_users': peter_users,

            'total_users': len(user_list)

        })

        

    except Exception as e:

        return jsonify({'error': str(e)}), 500



@app.route('/debug/create_peter', methods=['POST'])

@admin_required

@database_required

def debug_create_peter():

    """Debug endpoint to create Peter user"""

    try:

        data = request.get_json()

        role = data.get('role', 'staff')

        password = data.get('password', 'peter123')

        

        # Check if Peter already exists

        existing = User.query.filter_by(username='peter').first()

        if existing:

            return jsonify({'error': 'Peter already exists'}), 400

        

        # Create Peter user

        peter = User(username='peter', role=role, is_active=True)

        peter.set_password(password)

        db.session.add(peter)

        db.session.commit()

        

        return jsonify({

            'success': True,

            'message': f'Peter created with role: {role}',

            'username': 'peter',

            'password': password

        })

        

    except Exception as e:

        db.session.rollback()

        return jsonify({'error': str(e)}), 500



@app.route('/debug/delete_user_tool')

def debug_delete_user_tool():

    """Serve the delete user tool HTML page"""

    try:

        with open('delete_user_tool.html', 'r') as f:

            return f.read()

    except FileNotFoundError:

        return "Delete user tool not found", 404



@app.route('/debug/delete_user', methods=['POST'])

@admin_required

@database_required

def debug_delete_user():

    """Debug endpoint to delete a user"""

    try:

        data = request.get_json()

        username = data.get('username')

        

        if not username:

            return jsonify({'error': 'Username is required'}), 400

        

        # Find the user

        user = User.query.filter_by(username=username).first()

        if not user:

            return jsonify({'error': f'User "{username}" not found'}), 404

        

        # Don't allow deleting the currently logged in admin

        if username == session.get('username'):

            return jsonify({'error': 'Cannot delete your own account'}), 400

        

        # Store user info for response

        user_info = {

            'username': user.username,

            'role': user.role,

            'is_active': user.is_active,

            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else None

        }

        

        # Delete the user

        db.session.delete(user)

        db.session.commit()

        

        return jsonify({

            'success': True,

            'message': f'User "{username}" deleted successfully',

            'deleted_user': user_info

        })

        

    except Exception as e:

        db.session.rollback()

        return jsonify({'error': str(e)}), 500



@app.route('/debug/create_admin', methods=['POST'])

def debug_create_admin():

    """Debug endpoint to create admin user."""

    try:

        # Check if admin already exists

        existing_admin = User.query.filter_by(username='admin').first()

        if existing_admin:

            return jsonify({

                'success': False,

                'error': 'Admin user already exists',

                'admin_info': {

                    'username': existing_admin.username,

                    'role': existing_admin.role,

                    'is_active': existing_admin.is_active,

                    'id': existing_admin.id

                }

            })

        

        # Create new admin

        admin_user = User(

            username='admin',

            role='admin',

            is_active=True

        )

        admin_user.set_password('ErrantMate@24!')

        db.session.add(admin_user)

        db.session.commit()

        

        return jsonify({

            'success': True,

            'message': 'Admin user created successfully',

            'admin_info': {

                'username': admin_user.username,

                'role': admin_user.role,

                'is_active': admin_user.is_active,

                'id': admin_user.id

            }

        })

        

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error creating admin user: {str(e)}")

        return jsonify({

            'success': False,

            'error': str(e)

        }), 500



# ==================== NEW USER MANAGEMENT SYSTEM ====================



@app.route('/api/health')

def api_health():

    """Health check endpoint"""

    return jsonify({

        'status': 'healthy',

        'message': 'API is working',

        'routes_registered': [str(rule) for rule in app.url_map.iter_rules()]

    })



# api_test endpoint removed to avoid duplicate function name conflicts



@app.route('/api/users/public', methods=['GET'])

@database_required

def api_get_users_public():

    """Get all users - PUBLIC VERSION FOR TESTING"""

    try:

        users = User.query.filter_by(is_active=True).all()

        # Check if current user is admin

        current_user_id = session.get('user_id')

        current_user = User.query.get(current_user_id) if current_user_id else None

        is_admin = current_user and current_user.role == 'admin'

        users_data = []

        for user in users:

            user_data = {

                'id': user.id,

                'username': user.username,

                'role': user.role,

                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else None,

                'is_admin': user.is_admin(),

                'can_edit': user.username != 'admin'

            }

            # Add password information for admin users viewing user/staff roles

            if is_admin and user.role in ['user', 'staff']:

                user_data.update({

                    'password_hash': user.password_hash,

                    'show_password': True  # Flag to indicate password can be viewed

                })

            users_data.append(user_data)

        return jsonify({

            'success': True,

            'users': users_data

        })

    except Exception as e:

        app.logger.error(f"Error getting users: {str(e)}")

        return jsonify({'success': False, 'error': 'Failed to load users'}), 500



@app.route('/api/users', methods=['GET'])

@admin_required_api

@database_required

def api_get_users():

    """Get all users - NEW CLEAN VERSION"""

    try:

        users = User.query.filter_by(is_active=True).all()

        return jsonify({

            'success': True,

            'users': [

                {

                    'id': user.id,

                    'username': user.username,

                    'role': user.role,

                    'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else None,

                    'is_admin': user.is_admin(),

                    'can_edit': user.username != 'admin'

                }

                for user in users

            ]

        })

    except Exception as e:

        app.logger.error(f"Error getting users: {str(e)}")

        return jsonify({'success': False, 'error': 'Failed to load users'}), 500



@app.route('/api/users/public', methods=['POST'])

@database_required

def api_create_user_public():

    """Create new user - PUBLIC VERSION FOR TESTING"""

    try:

        data = request.get_json()

        

        # Basic validation

        username = data.get('username', '').strip()

        email = data.get('email', '').strip()

        phone_number = data.get('phone_number', '').strip()

        password = data.get('password', '')

        role = 'user'  # Force role to 'user' for security - ignore any role from request

        

        app.logger.info(f"Creating user - Username: {username}, Email: {email}, Phone: {phone_number}, Role: '{role}', Password length: {len(password)}")

        

        if not username or len(username) < 3:

            return jsonify({'success': False, 'error': 'Username must be at least 3 characters long', 'field': 'signupUsername'}), 400

        

        # Email validation

        import re

        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'

        if email and not re.match(email_regex, email):

            return jsonify({'success': False, 'error': 'Please enter a valid email address', 'field': 'signupEmail'}), 400

        

        # Phone validation

        phone_regex = r'^[+]?[0-9]{10,15}$'

        if phone_number and not re.match(phone_regex, phone_number.replace(' ', '')):

            return jsonify({'success': False, 'error': 'Please enter a valid phone number (10-15 digits)', 'field': 'signupPhone'}), 400

        

        # Password validation with regex for complexity

        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{6,}$'

        if not password or not re.match(password_regex, password):

            return jsonify({'success': False, 'error': 'Password must contain: 6+ characters, uppercase, lowercase, number, and symbol', 'field': 'signupPassword'}), 400

        

        # Check if user exists

        app.logger.info(f"Checking if user exists: {username}")

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:

            app.logger.info(f"User already exists: {existing_user.username}")

            return jsonify({'success': False, 'error': 'Username already exists. Please choose a different username', 'field': 'signupUsername'}), 400

        else:

            app.logger.info(f"User does not exist, proceeding with creation")

        

        # Check if email already exists

        if email and User.query.filter_by(email=email).first():

            return jsonify({'success': False, 'error': 'Email address already registered. Please use a different email', 'field': 'signupEmail'}), 400

        

        # Check if phone number already exists

        if phone_number and User.query.filter_by(phone_number=phone_number).first():

            return jsonify({'success': False, 'error': 'Phone number already registered. Please use a different phone number', 'field': 'signupPhone'}), 400

        

        # Create user

        try:

            new_user = User(username=username, email=email if email else None, phone_number=phone_number if phone_number else None, role=role)

            new_user.set_password(password)

            db.session.add(new_user)

            db.session.commit()

            

            app.logger.info(f"User created successfully: {new_user.username} (ID: {new_user.id})")

            

            return jsonify({

                'success': True,

                'message': 'User created successfully',

                'user': {

                    'id': new_user.id,

                    'username': new_user.username,

                    'email': new_user.email,

                    'phone_number': new_user.phone_number,

                    'role': new_user.role,

                    'created_at': new_user.created_at.strftime('%Y-%m-%d %H:%M') if new_user.created_at else None

                }

            })

        except Exception as create_error:

            db.session.rollback()

            app.logger.error(f"Error creating user: {str(create_error)}")

            return jsonify({'success': False, 'error': f'Database error: {str(create_error)}'}), 500

        

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error creating user: {str(e)}")

        app.logger.error(f"Exception type: {type(e).__name__}")

        import traceback

        app.logger.error(f"Traceback: {traceback.format_exc()}")

        return jsonify({'success': False, 'error': f'Failed to create user: {str(e)}'}), 500



@app.route('/api/users', methods=['POST'])

@admin_required_api

@database_required

def api_create_user():

    """Create new user - NEW CLEAN VERSION"""

    try:

        data = request.get_json()

        

        # Basic validation

        username = data.get('username', '').strip()

        password = data.get('password', '')

        role = data.get('role', 'user')

        

        if not username or len(username) < 3:

            return jsonify({'success': False, 'error': 'Username must be at least 3 characters'}), 400

        

        if not password or len(password) < 6:

            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400

        

        if role not in ['admin', 'user', 'staff']:

            return jsonify({'success': False, 'error': 'Invalid role'}), 400

        

        # Check if user exists

        if User.query.filter_by(username=username).first():

            return jsonify({'success': False, 'error': 'Username already exists'}), 400

        

        # Create user

        new_user = User(username=username, role=role)

        new_user.set_password(password)

        db.session.add(new_user)

        db.session.commit()

        

        return jsonify({

            'success': True,

            'message': 'User created successfully',

            'user': {

                'id': new_user.id,

                'username': new_user.username,

                'role': new_user.role,

                'created_at': new_user.created_at.strftime('%Y-%m-%d %H:%M') if new_user.created_at else None

            }

        })

        

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error creating user: {str(e)}")

        return jsonify({'success': False, 'error': 'Failed to create user'}), 500



@app.route('/api/users/<int:user_id>', methods=['PUT'])

@admin_required_api

@database_required

def api_update_user(user_id):

    """Update user - NEW CLEAN VERSION"""

    try:

        user = User.query.get_or_404(user_id)

        

        # Protect admin user

        if user.username == 'admin':

            return jsonify({'success': False, 'error': 'Cannot modify admin user'}), 403

        

        data = request.get_json()

        username = data.get('username', '').strip()

        password = data.get('password', '')

        role = data.get('role', user.role)

        

        if not username or len(username) < 3:

            return jsonify({'success': False, 'error': 'Username must be at least 3 characters'}), 400

        

        if role not in ['admin', 'user', 'staff']:

            return jsonify({'success': False, 'error': 'Invalid role'}), 400

        

        # Check username conflict

        existing = User.query.filter(User.username == username, User.id != user_id).first()

        if existing:

            return jsonify({'success': False, 'error': 'Username already exists'}), 400

        

        # Update user

        user.username = username

        user.role = role

        if password:

            user.set_password(password)

        

        db.session.commit()

        

        return jsonify({

            'success': True,

            'message': 'User updated successfully',

            'user': {

                'id': user.id,

                'username': user.username,

                'role': user.role,

                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else None

            }

        })

        

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error updating user: {str(e)}")

        return jsonify({'success': False, 'error': 'Failed to update user'}), 500



@app.route('/api/senders', methods=['GET'])

@login_required

@database_required

def api_get_senders():

    """Get unique sender names and phone numbers for autocomplete"""

    try:

        query = request.args.get('q', '').strip()

        

        if len(query) < 1:

            return jsonify({'senders': []})

        

        # Get unique sender names that contain the query (anywhere in the name)

        senders = db.session.query(Delivery.sender_name, Delivery.sender_phone)\
            .filter(Delivery.sender_name.ilike(f'%{query}%'))\
            .distinct()\
            .order_by(Delivery.sender_name)\
            .limit(10)\
            .all()

        

        sender_list = []

        for name, phone in senders:

            sender_list.append({

                'name': name,

                'phone': phone

            })

        

        return jsonify({'senders': sender_list})

        

    except Exception as e:

        app.logger.error(f"Error getting senders: {str(e)}")

        return jsonify({'success': False, 'error': 'Failed to load senders'}), 500



@app.route('/api/users/<int:user_id>', methods=['DELETE'])

@admin_required_api

@database_required

def api_delete_user(user_id):

    """Delete user - NEW CLEAN VERSION"""

    try:

        user = User.query.get_or_404(user_id)

        

        # Protect admin user

        if user.username == 'admin':

            return jsonify({'success': False, 'error': 'Cannot delete admin user'}), 403

        

        # Soft delete

        user.is_active = False

        db.session.commit()

        

        return jsonify({'success': True, 'message': 'User deleted successfully'})

        

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error deleting user: {str(e)}")

        return jsonify({'success': False, 'error': 'Failed to delete user'}), 500



@app.route('/auto_hard_delete_user', methods=['POST'])

@admin_required

@database_required

def auto_hard_delete_user():

    """Automatic hard delete user from database"""

    try:

        data = request.get_json()

        username = data.get('username')

        

        if not username:

            return jsonify({'success': False, 'error': 'Username required'})

        

        # Find user

        user = User.query.filter_by(username=username).first()

        if not user:

            return jsonify({'success': False, 'error': 'User not found'})

        

        # Delete all deliveries created by this user

        deliveries_to_delete = Delivery.query.filter_by(created_by=user.id).all()

        delivery_count = len(deliveries_to_delete)

        

        for delivery in deliveries_to_delete:

            db.session.delete(delivery)

        

        # Delete the user

        db.session.delete(user)

        db.session.commit()

        

        app.logger.info(f"Auto hard deleted user: {username} and {delivery_count} deliveries")

        

        return jsonify({

            'success': True, 

            'message': f'User {username} and {delivery_count} deliveries hard deleted'

        })

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error in auto hard delete: {str(e)}")

        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/complete_hard_delete_user', methods=['POST'])

@admin_required

@database_required

def complete_hard_delete_user():

    """Complete hard delete user with audit log cleanup"""

    try:

        data = request.get_json()

        username = data.get('username')

        

        if not username:

            return jsonify({'success': False, 'error': 'Username required'})

        

        # Find user

        user = User.query.filter_by(username=username).first()

        if not user:

            return jsonify({'success': False, 'error': 'User not found'})

        

        user_id = user.id

        

        # Step 1: Delete audit logs for this user

        from app import AuditLog

        audit_logs_to_delete = AuditLog.query.filter_by(username=username).all()

        audit_count = len(audit_logs_to_delete)

        

        for audit_log in audit_logs_to_delete:

            db.session.delete(audit_log)

        

        # Step 2: Delete all deliveries created by this user

        from app import Delivery

        deliveries_to_delete = Delivery.query.filter_by(created_by=user_id).all()

        delivery_count = len(deliveries_to_delete)

        

        for delivery in deliveries_to_delete:

            db.session.delete(delivery)

        

        # Step 3: Delete the user

        db.session.delete(user)

        db.session.commit()

        

        app.logger.info(f"Complete hard deleted user: {username}")

        app.logger.info(f"Deleted {audit_count} audit logs and {delivery_count} deliveries")

        

        return jsonify({

            'success': True, 

            'message': f'User {username} completely deleted with {audit_count} audit logs and {delivery_count} deliveries'

        })

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error in complete hard delete: {str(e)}")

        return jsonify({'success': False, 'error': str(e)}), 500



# ==================== LEGACY USER MANAGEMENT (KEEP FOR COMPATIBILITY) ====================



@app.route('/debug/create_user_simple', methods=['POST'])

@admin_required_api

@database_required

def debug_create_user_simple():

    """Simple user creation for debugging."""

    try:

        data = request.get_json()

        app.logger.info(f"Simple debug - Raw data: {data}")

        

        username = data.get('username', '').strip()

        password = data.get('password', '')

        role = data.get('role', 'user')

        

        app.logger.info(f"Simple debug - Parsed: username='{username}', password_len={len(password)}, role='{role}'")

        

        # Check existing users

        existing_users = User.query.all()

        app.logger.info(f"Simple debug - Existing users: {[u.username for u in existing_users]}")

        

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:

            app.logger.warning(f"Simple debug - Username '{username}' already exists!")

            return jsonify({'error': f'Username "{username}" already exists', 'debug': True}), 400

        

        # Create user without validation

        new_user = User(username=username, role=role)

        new_user.set_password(password)

        db.session.add(new_user)

        db.session.commit()

        

        app.logger.info(f"Simple debug - User created successfully: {username}")

        return jsonify({'success': True, 'message': 'User created successfully', 'debug': True})

        

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Simple debug - Error: {str(e)}", exc_info=True)

        return jsonify({'error': str(e), 'debug': True}), 500



@app.route('/create_user', methods=['POST'])

@admin_required_api

@database_required

def create_user():

    """Create a new user."""

    try:

        app.logger.info(f"Create user attempt - Session: {dict(session)}")

        

        # Check if user is authenticated

        if 'user_id' not in session:

            app.logger.warning("Unauthorized access attempt to create_user")

            return jsonify({

                'error': 'Authentication required',

                'redirect': '/login'

            }), 401

        

        # Check if user is admin

        if session.get('user_role') != 'admin':

            app.logger.warning(f"Non-admin user attempted to create user. Role: {session.get('user_role')}")

            return jsonify({

                'error': 'Admin access required'

            }), 403

        

        # Get JSON data with better error handling

        try:

            data = request.get_json()

            app.logger.info(f"Raw request data: {data}")

        except Exception as json_error:

            app.logger.error(f"JSON parsing error: {str(json_error)}")

            return jsonify({'error': 'Invalid JSON data'}), 400

        

        if not data:

            app.logger.error("No JSON data received in create_user")

            return jsonify({'error': 'No data provided'}), 400

            

        username = data.get('username', '').strip()

        password = data.get('password', '')

        role = data.get('role', 'user')  # Default to 'user' if not specified

        

        app.logger.info(f"Creating user: {username}, role: {role}")

        app.logger.info(f"Received data: {dict(data)}")

        

        # Enhanced validation

        if not username:

            app.logger.error("Username is empty")

            return jsonify({'error': 'Username is required'}), 400

            

        if not password:

            app.logger.error("Password is empty")

            return jsonify({'error': 'Password is required'}), 400

            

        if len(username) < 3:

            app.logger.error(f"Username too short: {username}")

            return jsonify({'error': 'Username must be at least 3 characters long'}), 400

            

        if len(password) < 6:

            app.logger.error(f"Password too short: {len(password)} characters")

            return jsonify({'error': 'Password must be at least 6 characters long'}), 400

        

        if role not in ['admin', 'user', 'staff']:

            app.logger.error(f"Invalid role: {role}")

            return jsonify({'error': 'Role must be admin, user, or staff'}), 400

        

        # Check if user already exists

        try:

            existing_user = User.query.filter_by(username=username).first()

            if existing_user:

                app.logger.warning(f"Username already exists: {username}")

                return jsonify({'error': 'Username already exists'}), 400

        except Exception as db_error:

            app.logger.error(f"Database query error: {str(db_error)}")

            return jsonify({'error': 'Database error checking username'}), 500

        

        # Create new user with transaction handling

        try:

            new_user = User(username=username, role=role)

            new_user.set_password(password)

            db.session.add(new_user)

            db.session.commit()

            

            app.logger.info(f"User created successfully: {username} (ID: {new_user.id})")

            

            return jsonify({

                'success': True, 

                'message': 'User created successfully',

                'user': {

                    'id': new_user.id,

                    'username': new_user.username,

                    'role': new_user.role,

                    'created_at': new_user.created_at.strftime('%Y-%m-%d %H:%M') if new_user.created_at else None

                }

            })

            

        except Exception as commit_error:

            db.session.rollback()

            app.logger.error(f"Database commit error: {str(commit_error)}")

            return jsonify({'error': 'Failed to save user to database'}), 500

        

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Unexpected error creating user: {str(e)}", exc_info=True)

        return jsonify({'error': 'An unexpected error occurred while creating the user'}), 500



@app.route('/update_user/<int:user_id>', methods=['PUT'])

@admin_required_api

@database_required

def update_user(user_id):

    """Update an existing user."""

    try:

        user = User.query.get_or_404(user_id)

        

        # Prevent editing the main admin

        if user.username == 'Admin':

            return jsonify({'error': 'Cannot modify admin user'}), 403

        

        data = request.get_json()

        username = data.get('username', '').strip()

        password = data.get('password', '')

        role = data.get('role', user.role)

        

        if not username:

            return jsonify({'error': 'Username is required'}), 400

        

        if role not in ['admin', 'user', 'staff']:

            return jsonify({'error': 'Role must be admin, user, or staff'}), 400

        

        # Check if username is taken by another user

        existing_user = User.query.filter(User.username == username, User.id != user_id).first()

        if existing_user:

            return jsonify({'error': 'Username already exists'}), 400

        

        # Update user

        user.username = username

        user.role = role

        if password:  # Only update password if provided

            user.set_password(password)

        

        db.session.commit()

        

        return jsonify({

            'success': True, 

            'message': 'User updated successfully',

            'user': {

                'id': user.id,

                'username': user.username,

                'role': user.role,

                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else None

            }

        })

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error updating user: {str(e)}")

        return jsonify({'error': 'Failed to update user'}), 500



@app.route('/delete_user/<int:user_id>', methods=['DELETE'])

@admin_required_api

@database_required

def delete_user(user_id):

    """Delete a user."""

    try:

        user = User.query.get_or_404(user_id)

        

        # Prevent deleting the main admin

        if user.username == 'Admin':

            return jsonify({'error': 'Cannot delete admin user'}), 403

        

        # Soft delete by deactivating

        user.is_active = False

        db.session.commit()

        

        return jsonify({'success': True, 'message': 'User deleted successfully'})

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error deleting user: {str(e)}")

        return jsonify({'error': 'Failed to delete user'}), 500



@app.route('/get_delivery_trends')

@login_required

@database_required

def get_delivery_trends():

    """Get delivery trends data for charts."""

    try:

        # Get date range from query params (default to last 30 days)

        days = request.args.get('days', 30, type=int)

        end_date = get_current_time()

        start_date = end_date - timedelta(days=days)

        

        # Get deliveries within date range

        deliveries = Delivery.query.filter(

            Delivery.created_at >= start_date,

            Delivery.created_at <= end_date

        ).order_by(Delivery.created_at).all()

        

        # Group by date and status

        daily_data = {}

        

        for delivery in deliveries:

            date_key = delivery.created_at.strftime('%Y-%m-%d')

            

            if date_key not in daily_data:

                daily_data[date_key] = {'Pending': 0, 'In Transit': 0, 'Delivered': 0}

            

            daily_data[date_key][delivery.status] = daily_data[date_key].get(delivery.status, 0) + 1

        

        # Prepare data for Chart.js

        dates = sorted(daily_data.keys())

        pending_counts = [daily_data[date].get('Pending', 0) for date in dates]

        in_transit_counts = [daily_data[date].get('In Transit', 0) for date in dates]

        delivered_counts = [daily_data[date].get('Delivered', 0) for date in dates]

        

        return jsonify({

            'labels': [datetime.strptime(date, '%Y-%m-%d').strftime('%b %d') for date in dates],

            'datasets': [

                {

                    'label': 'Pending',

                    'data': pending_counts,

                    'borderColor': '#f59e0b',

                    'backgroundColor': 'rgba(245, 158, 11, 0.1)',

                    'tension': 0.3,

                    'borderWidth': 2,

                    'pointRadius': 3,

                    'pointHoverRadius': 5

                },

                {

                    'label': 'In Transit',

                    'data': in_transit_counts,

                    'borderColor': '#3b82f6',

                    'backgroundColor': 'rgba(59, 130, 246, 0.1)',

                    'tension': 0.3,

                    'borderWidth': 2,

                    'pointRadius': 3,

                    'pointHoverRadius': 5

                },

                {

                    'label': 'Delivered',

                    'data': delivered_counts,

                    'borderColor': '#10b981',

                    'backgroundColor': 'rgba(16, 185, 129, 0.1)',

                    'tension': 0.3,

                    'borderWidth': 2,

                    'pointRadius': 3,

                    'pointHoverRadius': 5

                }

            ]

        })

        

    except Exception as e:

        app.logger.error(f"Error getting delivery trends: {str(e)}")

        return jsonify({'error': 'Failed to load delivery trends'}), 500



@app.route('/get_revenue_charts')

@login_required

@database_required

def get_revenue_charts():

    """Get revenue data for charts."""

    try:

        # Check if user is authenticated

        if 'user_id' not in session:

            app.logger.warning("Unauthorized access attempt to get_revenue_charts")

            return jsonify({

                'line_chart': {'labels': [], 'datasets': []},

                'summary': {

                    'total_revenue': 0,

                    'total_expenses': 0,

                    'total_profit': 0,

                    'profit_margin': 0

                },

                'error': 'Authentication required'

            }), 401

        

        # Get date range from query params (default to last 30 days)

        days = request.args.get('days', 30, type=int)

        end_date = get_current_time()

        start_date = end_date - timedelta(days=days)

        

        # Get deliveries within date range

        deliveries = Delivery.query.filter(

            Delivery.created_at >= start_date,

            Delivery.created_at <= end_date

        ).order_by(Delivery.created_at).all()

        

        # Group by date

        daily_revenue = {}

        daily_expenses = {}

        

        for delivery in deliveries:

            date_key = delivery.created_at.strftime('%Y-%m-%d')

            

            amount = float(delivery.amount) if delivery.amount else 0.0

            expenses = float(delivery.expenses) if delivery.expenses else 0.0

            

            daily_revenue[date_key] = daily_revenue.get(date_key, 0) + amount

            daily_expenses[date_key] = daily_expenses.get(date_key, 0) + expenses

        

        # Prepare data for Chart.js

        dates = sorted(daily_revenue.keys())

        revenue_data = [daily_revenue[date] for date in dates]

        expenses_data = [daily_expenses[date] for date in dates]

        

        # Calculate totals

        total_revenue = sum(revenue_data)

        total_expenses = sum(expenses_data)

        

        return jsonify({

            'line_chart': {

                'labels': [datetime.strptime(date, '%Y-%m-%d').strftime('%b %d') for date in dates],

                'datasets': [

                    {

                        'label': 'Revenue',

                        'data': revenue_data,

                        'borderColor': '#10b981',

                        'backgroundColor': 'rgba(16, 185, 129, 0.1)',

                        'tension': 0.3,

                        'borderWidth': 2,

                        'pointRadius': 3,

                        'pointHoverRadius': 5

                    },

                    {

                        'label': 'Expenses',

                        'data': expenses_data,

                        'borderColor': '#ef4444',

                        'backgroundColor': 'rgba(239, 68, 68, 0.1)',

                        'tension': 0.3,

                        'borderWidth': 2,

                        'pointRadius': 3,

                        'pointHoverRadius': 5

                    }

                ]

            },

            'summary': {

                'total_revenue': round(total_revenue, 2),

                'total_expenses': round(total_expenses, 2)

            }

        })

        

    except Exception as e:

        app.logger.error(f"Error getting revenue charts: {str(e)}")

        # Return empty data structure with zeros to prevent JavaScript errors

        return jsonify({

            'line_chart': {

                'labels': [],

                'datasets': []

            },

            'summary': {

                'total_revenue': 0,

                'total_expenses': 0,

                'total_profit': 0,

                'profit_margin': 0

            },

            'error': 'Failed to load revenue charts'

        }), 500



@app.route('/get_revenue_analytics')

@login_required_api

@database_required

def get_revenue_analytics():

    """Get revenue analytics data with real-time updates."""

    try:

        # Get period from query params (daily, weekly, monthly)

        period = request.args.get('period', 'daily')

        

        # Calculate date ranges based on period

        end_date = get_current_time()

        

        if period == 'daily':

            start_date = end_date - timedelta(days=7)

            period_days = 7

        elif period == 'weekly':

            start_date = end_date - timedelta(weeks=5)

            period_days = 35

        else:  # monthly

            start_date = end_date - timedelta(days=365)

            period_days = 365

        

        # Get deliveries within date range

        deliveries = Delivery.query.filter(

            Delivery.created_at >= start_date,

            Delivery.created_at <= end_date

        ).order_by(Delivery.created_at).all()

        

        # Group by date

        daily_data = {}

        for delivery in deliveries:

            date_key = delivery.created_at.strftime('%Y-%m-%d')

            amount = float(delivery.amount) if delivery.amount else 0.0

            

            if date_key not in daily_data:

                daily_data[date_key] = {'revenue': 0.0, 'count': 0, 'costs': 0.0}

            daily_data[date_key]['revenue'] += float(amount)  # Use actual delivery amount as revenue

            daily_data[date_key]['costs'] += 0  # No operational costs by default

            daily_data[date_key]['count'] += 1

        

        # Process data based on period

        if period == 'daily':

            labels, revenue_data = process_daily_data(daily_data, period_days)

        elif period == 'weekly':

            labels, revenue_data = process_weekly_data(daily_data, period_days)

        else:  # monthly

            labels, revenue_data = process_monthly_data(daily_data, period_days)

        

        # Calculate metrics

        total_revenue = sum(revenue_data)

        avg_daily = total_revenue / len(revenue_data) if revenue_data else 0

        peak_revenue = max(revenue_data) if revenue_data else 0

        peak_index = revenue_data.index(peak_revenue) if revenue_data else 0

        peak_label = labels[peak_index] if labels else 'N/A'

        

        # Calculate growth rate

        growth_rate = calculate_growth_rate(revenue_data)

        

        # Generate target data (80% of average, minimum values)

        avg_target = max(avg_daily * 0.8, 500 if period == 'daily' else 2000 if period == 'weekly' else 6000)

        target_data = [avg_target] * len(revenue_data)

        

        return jsonify({

            'period': period,

            'date_range': {

                'start': start_date.strftime('%Y-%m-%d'),

                'end': end_date.strftime('%Y-%m-%d'),

                'description': get_period_description(period)

            },

            'labels': labels,

            'revenue': revenue_data,

            'target': target_data,

            'metrics': {

                'total_revenue': total_revenue,

                'avg_daily': avg_daily,

                'peak_revenue': peak_revenue,

                'peak_label': peak_label,

                'growth_rate': growth_rate

            }

        })

        

    except Exception as e:

        app.logger.error(f"Error getting revenue analytics: {str(e)}")

        return jsonify({'error': 'Failed to load revenue analytics'}), 500



def process_daily_data(daily_data, days):

    """Process daily data for revenue analytics."""

    labels = []

    revenue = []

    

    for i in range(days):

        date = get_current_time() - timedelta(days=days-1-i)

        date_key = date.strftime('%Y-%m-%d')

        

        # Format label as day name

        label = date.strftime('%a')

        if i == 0 or i == days - 1:

            label = date.strftime('%b %d')  # Show date for first and last

        

        labels.append(label)

        revenue.append(daily_data.get(date_key, {}).get('revenue', 0.0))

    

    return labels, revenue



def process_weekly_data(daily_data, days):

    """Process weekly data for revenue analytics."""

    labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']

    revenue = [0.0] * 5

    

    for date_key, data in daily_data.items():

        date_obj = datetime.strptime(date_key, '%Y-%m-%d')

        days_ago = (get_current_time() - date_obj).days

        

        if days_ago < 35:  # Within 5 weeks

            week_num = min(days_ago // 7, 4)

            revenue[4 - week_num] += data['revenue']  # Reverse order for chronological

    

    return labels, revenue



def process_monthly_data(daily_data, days):

    """Process monthly data for revenue analytics."""

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 

                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    labels = month_names

    revenue = [0.0] * 12

    

    for date_key, data in daily_data.items():

        date_obj = datetime.strptime(date_key, '%Y-%m-%d')

        month_num = date_obj.month - 1  # 0-indexed

        

        # Only include data from the last 12 months

        if (get_current_time() - date_obj).days < 365:

            revenue[month_num] += data['revenue']

    

    return labels, revenue



def calculate_growth_rate(revenue_data):

    """Calculate growth rate from first to last period."""

    if len(revenue_data) < 2:

        return '+0.0%'

    

    first = revenue_data[0]

    last = revenue_data[-1]

    

    if first == 0:

        return '+100.0%' if last > 0 else '+0.0%'

    

    growth = ((last - first) / first) * 100

    sign = '+' if growth >= 0 else ''

    return f'{sign}{growth:.1f}%'



def get_period_description(period):

    """Get human-readable period description."""

    descriptions = {

        'daily': 'Last 7 days',

        'weekly': 'Last 5 weeks',

        'monthly': 'Last 12 months'

    }

    return descriptions.get(period, 'Last 7 days')



@app.route('/system_health')

@admin_required

def system_health():

    """System health monitoring page (admin only)."""

    return render_template('system_health.html')

@login_required

def get_system_health():

    """Get system health and performance metrics."""

    try:

        # Try to import psutil, provide fallback if not available

        try:

            import psutil

            psutil_available = True

        except ImportError:

            psutil_available = False

            app.logger.warning("psutil not available - using fallback data")

        

        # Get system information (always available)

        system_info = {

            'platform': platform.system(),

            'platform_release': platform.release(),

            'platform_version': platform.version(),

            'architecture': platform.machine(),

            'hostname': platform.node(),

            'processor': platform.processor(),

        }

        

        if psutil_available:

            # Get real system metrics

            try:

                # Get CPU usage

                cpu_usage = psutil.cpu_percent(interval=0.1)

                cpu_count = psutil.cpu_count()

                cpu_freq = psutil.cpu_freq()

                

                # Get memory usage

                memory = psutil.virtual_memory()

                memory_usage = memory.percent

                memory_total = memory.total

                memory_available = memory.available

                memory_used = memory.used

                

                # Get disk usage

                disk = psutil.disk_usage('/')

                disk_usage = disk.percent

                disk_total = disk.total

                disk_free = disk.free

                disk_used = disk.used

                

                # Get network stats

                network = psutil.net_io_counters()

                bytes_sent = network.bytes_sent if network else 0

                bytes_recv = network.bytes_recv if network else 0

                

                # Get process information

                process_count = len(psutil.pids())

                current_process = psutil.Process()

                process_memory = current_process.memory_info()

                process_cpu = current_process.cpu_percent()

                

            except Exception as psutil_error:

                app.logger.error(f"psutil error: {str(psutil_error)}")

                # Fallback to mock data

                cpu_usage = 25

                cpu_count = 4

                cpu_freq = None

                memory_usage = 45

                memory_total = 8 * 1024**3  # 8GB

                memory_available = memory_total * 0.55

                memory_used = memory_total * 0.45

                disk_usage = 30

                disk_total = 500 * 1024**3  # 500GB

                disk_free = disk_total * 0.70

                disk_used = disk_total * 0.30

                bytes_sent = 1024 * 1024 * 100  # 100MB

                bytes_recv = 1024 * 1024 * 150  # 150MB

                process_count = 120

                process_memory = type('obj', (object,), {'rss': 1024 * 1024 * 50})()  # 50MB

                process_cpu = 5.0

        else:

            # Fallback mock data when psutil is not available

            cpu_usage = 25

            cpu_count = 4

            cpu_freq = None

            memory_usage = 45

            memory_total = 8 * 1024**3  # 8GB

            memory_available = memory_total * 0.55

            memory_used = memory_total * 0.45

            disk_usage = 30

            disk_total = 500 * 1024**3  # 500GB

            disk_free = disk_total * 0.70

            disk_used = disk_total * 0.30

            bytes_sent = 1024 * 1024 * 100  # 100MB

            bytes_recv = 1024 * 1024 * 150  # 150MB

            process_count = 120

            process_memory = type('obj', (object,), {'rss': 1024 * 1024 * 50})()  # 50MB

            process_cpu = 5.0

        

        # Calculate system uptime (simplified - using app start time)

        app_start_time = datetime.now() - timedelta(hours=24)  # Simulated 24 hours uptime

        uptime = datetime.now() - app_start_time

        uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"

        

        # Get database performance (always available)

        db_start = datetime.now()

        delivery_count = Delivery.query.count()

        db_query_time = (datetime.now() - db_start).total_seconds() * 1000

        

        return jsonify({

            'system_info': system_info,

            'performance': {

                'cpu': {

                    'usage_percent': cpu_usage,

                    'count': cpu_count,

                    'frequency': cpu_freq.current if cpu_freq else 0,

                    'status': 'healthy' if cpu_usage < 80 else 'warning' if cpu_usage < 95 else 'critical'

                },

                'memory': {

                    'usage_percent': memory_usage,

                    'total_gb': round(memory_total / (1024**3), 2),

                    'available_gb': round(memory_available / (1024**3), 2),

                    'used_gb': round(memory_used / (1024**3), 2),

                    'status': 'healthy' if memory_usage < 80 else 'warning' if memory_usage < 95 else 'critical'

                },

                'disk': {

                    'usage_percent': disk_usage,

                    'total_gb': round(disk_total / (1024**3), 2),

                    'free_gb': round(disk_free / (1024**3), 2),

                    'used_gb': round(disk_used / (1024**3), 2),

                    'status': 'healthy' if disk_usage < 80 else 'warning' if disk_usage < 95 else 'critical'

                },

                'network': {

                    'bytes_sent_mb': round(bytes_sent / (1024**2), 2),

                    'bytes_recv_mb': round(bytes_recv / (1024**2), 2),

                    'status': 'healthy'

                }

            },

            'processes': {

                'total_count': process_count,

                'current_app': {

                    'memory_mb': round(process_memory.rss / (1024**2), 2),

                    'cpu_percent': process_cpu,

                    'status': 'healthy'

                }

            },

            'database': {

                'query_time_ms': round(db_query_time, 2),

                'delivery_count': delivery_count,

                'status': 'healthy' if db_query_time < 100 else 'warning' if db_query_time < 500 else 'critical'

            },

            'uptime': {

                'formatted': uptime_str,

                'total_hours': uptime.total_seconds() / 3600,

                'status': 'healthy'

            },

            'overall_status': 'healthy' if cpu_usage < 80 and memory_usage < 80 and disk_usage < 80 and db_query_time < 100 else 'warning' if cpu_usage < 95 and memory_usage < 95 and disk_usage < 95 and db_query_time < 500 else 'critical',

            'timestamp': datetime.now().isoformat(),

            'psutil_available': psutil_available

        })

        

    except Exception as e:

        app.logger.error(f"Error getting system health: {str(e)}")

        # Return fallback data instead of error

        return jsonify({

            'error': 'System monitoring unavailable',

            'fallback_data': {

                'system_info': {

                    'platform': 'Unknown',

                    'architecture': 'Unknown',

                    'hostname': 'Unknown'

                },

                'performance': {

                    'cpu': {'usage_percent': 0, 'status': 'unknown'},

                    'memory': {'usage_percent': 0, 'status': 'unknown'},

                    'disk': {'usage_percent': 0, 'status': 'unknown'},

                    'network': {'bytes_sent_mb': 0, 'bytes_recv_mb': 0, 'status': 'unknown'}

                },

                'overall_status': 'unknown',

                'timestamp': datetime.now().isoformat()

            }

        }), 200



@app.route('/get_status_distribution')

@login_required

@database_required

def get_status_distribution():

    """Get status distribution data for pie chart."""

    try:

        # Get date range from query params (default to last 30 days)

        days = request.args.get('days', 30, type=int)

        end_date = get_current_time()

        start_date = end_date - timedelta(days=days)

        

        # Get deliveries within date range

        deliveries = Delivery.query.filter(

            Delivery.created_at >= start_date,

            Delivery.created_at <= end_date

        ).all()

        

        # Count by status

        status_counts = {'Pending': 0, 'In Transit': 0, 'Delivered': 0}

        

        for delivery in deliveries:

            if delivery.status in status_counts:

                status_counts[delivery.status] += 1

        

        return jsonify({

            'labels': list(status_counts.keys()),

            'data': list(status_counts.values()),

            'counts': status_counts

        })

        

    except Exception as e:

        app.logger.error(f"Error getting status distribution: {str(e)}")

        return jsonify({'error': 'Failed to load status distribution'}), 500



@app.route('/get_delivery_trends_line')

@login_required

@database_required

def get_delivery_trends_line():

    """Get delivery trends line chart data."""

    try:

        # Get date range from query params (default to last 30 days)

        days = request.args.get('days', 30, type=int)

        end_date = get_current_time()

        start_date = end_date - timedelta(days=days)

        

        # Get deliveries within date range

        deliveries = Delivery.query.filter(

            Delivery.created_at >= start_date,

            Delivery.created_at <= end_date

        ).order_by(Delivery.created_at).all()

        

        # Group by date and count total deliveries

        daily_counts = {}

        

        for delivery in deliveries:

            date_key = delivery.created_at.strftime('%Y-%m-%d')

            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1

        

        # Prepare data for Chart.js

        dates = sorted(daily_counts.keys())

        counts = [daily_counts[date] for date in dates]

        

        return jsonify({

            'labels': [datetime.strptime(date, '%Y-%m-%d').strftime('%b %d') for date in dates],

            'data': counts

        })

        

    except Exception as e:

        app.logger.error(f"Error getting delivery trends line: {str(e)}")

        return jsonify({'error': 'Failed to load delivery trends'}), 500



@app.route('/get_recent_deliveries')

@login_required

@database_required

def get_recent_deliveries():

    """Get recent deliveries with lazy loading support - shows all deliveries (for reports page)."""

    try:

        # Get pagination parameters

        page = request.args.get('page', 1, type=int)

        per_page = request.args.get('per_page', 20, type=int)

        offset = (page - 1) * per_page

        

        # Get filter parameters

        period = request.args.get('period', 'all')

        status = request.args.get('status', 'all')

        search = request.args.get('search', '')

        

        # Build base query

        query = Delivery.query

        

        # Apply period filter
        if period != 'all':
            now = datetime.utcnow()
            if period == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(Delivery.created_at >= start_date)
            elif period == 'week':
                start_date = now - timedelta(days=7)
                query = query.filter(Delivery.created_at >= start_date)
            elif period == 'month':
                start_date = now - timedelta(days=30)
                query = query.filter(Delivery.created_at >= start_date)
            elif period == 'year':
                start_date = now - timedelta(days=365)
                query = query.filter(Delivery.created_at >= start_date)

        

        # Apply status filter
        if status != 'all':
            query = query.filter(Delivery.status == status)

        

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Delivery.display_id.ilike(search_term),
                    Delivery.sender_name.ilike(search_term),
                    Delivery.sender_phone.ilike(search_term),
                    Delivery.recipient_name.ilike(search_term),
                    Delivery.recipient_phone.ilike(search_term),
                    Delivery.recipient_address.ilike(search_term),
                    Delivery.delivery_person.ilike(search_term),
                    Delivery.payment_by.ilike(search_term)
                )
            )

        

        # Get total count for pagination info

        total_count = query.count()

        

        # Get deliveries for current page

        recent_deliveries = query.order_by(Delivery.created_at.desc()).offset(offset).limit(per_page).all()

        

        # Convert to list of dictionaries

        deliveries_data = []

        for delivery in recent_deliveries:

            delivery_dict = {

                'id': delivery.id,

                'display_id': delivery.display_id,

                'sender_name': delivery.sender_name,

                'sender_phone': delivery.sender_phone,

                'recipient_name': delivery.recipient_name,

                'recipient_phone': delivery.recipient_phone,

                'recipient_address': delivery.recipient_address,

                'status': delivery.status,

                'amount': float(delivery.amount) if delivery.amount else 0.0,

                'expenses': float(delivery.expenses) if delivery.expenses else 0.0,

                'delivery_person': delivery.delivery_person or '',

                'goods_type': delivery.goods_type,

                'quantity': delivery.quantity,

                'payment_by': delivery.payment_by,

                'created_at': delivery.created_at.isoformat() if delivery.created_at else None,

                'time_ago': get_time_ago(delivery.created_at) if delivery.created_at else "Unknown"

            }

            deliveries_data.append(delivery_dict)

        

        # Return paginated response

        return jsonify({

            'deliveries': deliveries_data,

            'pagination': {

                'page': page,

                'per_page': per_page,

                'total': total_count,

                'pages': (total_count + per_page - 1) // per_page,

                'has_next': page * per_page < total_count,

                'has_prev': page > 1

            }

        })

        

    except Exception as e:

        app.logger.error(f"Error getting recent deliveries: {str(e)}")

        return jsonify({'error': 'Failed to load recent deliveries'}), 500



@app.route('/get_user_recent_deliveries')

@login_required

@database_required

def get_user_recent_deliveries():

    """Get recent deliveries for the current user (for add_delivery page)."""

    try:

        # Get current user ID from session

        current_user_id = session.get('user_id')

        

        # Get recent deliveries (last 10) created by the current user only

        recent_deliveries = Delivery.query.filter_by(created_by=current_user_id).order_by(Delivery.created_at.desc()).limit(10).all()

        

        # Convert to list of dictionaries

        deliveries_data = []

        for delivery in recent_deliveries:

            delivery_dict = {

                'id': delivery.id,

                'display_id': delivery.display_id,

                'sender_name': delivery.sender_name,

                'sender_phone': delivery.sender_phone,

                'recipient_name': delivery.recipient_name,

                'recipient_phone': delivery.recipient_phone,

                'recipient_address': delivery.recipient_address,

                'status': delivery.status,

                'amount': float(delivery.amount) if delivery.amount else 0.0,

                'expenses': float(delivery.expenses) if delivery.expenses else 0.0,

                'delivery_person': delivery.delivery_person or '',

                'goods_type': delivery.goods_type,

                'quantity': delivery.quantity,

                'payment_by': delivery.payment_by,

                'created_at': delivery.created_at.isoformat() if delivery.created_at else None,

                'time_ago': get_time_ago(delivery.created_at) if delivery.created_at else "Unknown"

            }

            deliveries_data.append(delivery_dict)

        

        return jsonify(deliveries_data)

        

    except Exception as e:

        return jsonify({'error': 'Failed to load recent deliveries'}), 500



@app.route('/update_delivery_expenses_and_person', methods=['POST', 'OPTIONS'])

@login_required

def update_delivery_expenses_and_person():

    """Update delivery expenses and delivery person."""

    

    # Handle preflight OPTIONS request

    if request.method == 'OPTIONS':

        response = make_response()

        response.headers.add("Access-Control-Allow-Origin", "*")

        response.headers.add('Access-Control-Allow-Headers', "*")

        response.headers.add('Access-Control-Allow-Methods', "*")

        return response

    

    try:

        data = request.get_json()

        

        if not data:

            return jsonify({'error': 'No data provided'}), 400

        

        delivery_id = data.get('delivery_id')

        expenses = data.get('expenses', 0.0)

        delivery_person = data.get('delivery_person', '')

        

        if not delivery_id:

            return jsonify({'error': 'Delivery ID is required'}), 400

        

        # Find the delivery by display_id

        delivery = Delivery.query.filter_by(display_id=delivery_id).first()

        if not delivery:

            return jsonify({'error': 'Delivery not found'}), 404

        

        # Update delivery person only (expenses are now handled via amount field in delivery details)

        delivery.delivery_person = delivery_person or ''

        

        db.session.commit()

        

        response = jsonify({

            'success': True,

            'message': 'Delivery updated successfully',

            'delivery': {

                'id': delivery.id,

                'display_id': delivery.display_id,

                'expenses': float(delivery.expenses),

                'delivery_person': delivery.delivery_person

            }

        })

        response.headers.add("Access-Control-Allow-Origin", "*")

        return response

        

    except Exception as e:

        db.session.rollback()

        app.logger.error(f"Error updating delivery: {str(e)}")

        return jsonify({'error': 'Failed to update delivery'}), 500



@app.route('/update_delivery', methods=['POST', 'OPTIONS'])

@login_required

def update_delivery():

    """Alternative simple endpoint to update delivery."""

    

    if request.method == 'OPTIONS':

        response = make_response()

        response.headers.add("Access-Control-Allow-Origin", "*")

        response.headers.add('Access-Control-Allow-Headers', "*")

        response.headers.add('Access-Control-Allow-Methods', "*")

        return response

    

    try:

        data = request.get_json()

        delivery_id = data.get('delivery_id')

        expenses = data.get('expenses')  

        delivery_person = data.get('delivery_person', '')

        amount = data.get('amount')  # New revenue parameter

        

        delivery = Delivery.query.filter_by(display_id=delivery_id).first()

        if not delivery:

            return jsonify({'error': 'Delivery not found'}), 404

        

        # Update expenses if provided

        if expenses is not None:

            delivery.expenses = float(expenses) if expenses else 0.0

        

        # Update revenue (amount) if provided

        if amount is not None:

            delivery.amount = float(amount) if amount else 0.0

        

        # Always update delivery person if provided

        if delivery_person:

            delivery.delivery_person = delivery_person

            

        db.session.commit()

        

        return jsonify({'success': True, 'message': 'Updated'})

    except Exception as e:

        db.session.rollback()

        return jsonify({'error': str(e)}), 500



@app.route('/audit_logs')

@admin_required

def audit_logs():

    """Render the audit logs page for administrators."""

    try:

        # Get query parameters for filtering

        page = request.args.get('page', 1, type=int)

        per_page = request.args.get('per_page', 50, type=int)

        action_filter = request.args.get('action', '')

        username_filter = request.args.get('username', '')

        date_from = request.args.get('date_from', '')

        date_to = request.args.get('date_to', '')

        

        # Build query

        query = AuditLog.query

        

        # Apply filters

        if action_filter:

            query = query.filter(AuditLog.action.ilike(f'%{action_filter}%'))

        if username_filter:

            query = query.filter(AuditLog.username.ilike(f'%{username_filter}%'))

        if date_from:

            try:

                date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')

                query = query.filter(AuditLog.timestamp >= date_from_dt)

            except ValueError:

                pass

        if date_to:

            try:

                date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')

                query = query.filter(AuditLog.timestamp <= date_to_dt)

            except ValueError:

                pass

        

        # Order by timestamp descending (newest first)

        query = query.order_by(AuditLog.timestamp.desc())

        

        # Paginate

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        audit_logs = pagination.items

        

        return render_template('audit_logs.html', 

                             audit_logs=audit_logs, 

                             pagination=pagination,

                             action_filter=action_filter,

                             username_filter=username_filter,

                             date_from=date_from,

                             date_to=date_to)

    except Exception as e:

        app.logger.error(f"Error loading audit logs: {str(e)}")

        flash('Error loading audit logs', 'danger')

        return render_template('audit_logs.html', audit_logs=[], pagination=None)



@app.errorhandler(404)

def not_found_error(error):

    """Handle 404 errors."""

    return render_template('404.html'), 404



@app.errorhandler(500)

def internal_error(error):

    """Handle 500 errors."""

    db.session.rollback()

    return render_template('500.html'), 500



def create_default_admin():

    """Create default admin user if it doesn't exist."""

    try:

        # Check for admin user (case-insensitive)

        admin_user = User.query.filter(User.username.ilike('admin')).first()

        if not admin_user:

            admin_user = User(username='admin', role='admin')

            admin_user.set_password('ErrantMate@24!')

            db.session.add(admin_user)

            db.session.commit()

            print("Default admin user created: admin / ErrantMate@24! (role: admin)")

        else:

            print("Admin user already exists")

    except Exception as e:

        print(f"Error creating admin user: {e}")

        db.session.rollback()



def main():

    """Main application entry point."""

    print("Starting ErrantMate Application...")

    

    with app.app_context():

        try:

            # Ensure database tables exist

            db.create_all()

            

            # Create admin user if needed

            create_default_admin()

            

            print("Application ready!")

            print("Access the app at: http://localhost:5001")

            print("Login with: admin / ErrantMate@24!")

            

        except Exception as e:

            print(f"Startup error: {e}")

            import traceback

            traceback.print_exc()

    

    try:

        app.run(debug=True, host='0.0.0.0', port=5001)

    except Exception as e:

        print(f"Failed to start server: {e}")





if __name__ == '__main__':

    main()

