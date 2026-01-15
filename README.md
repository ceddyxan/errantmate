# Errantmate - Delivery Management System

A Flask-based web application for managing delivery operations with real-time tracking, reporting, and user management.

## Features

- 📦 Delivery tracking and management
- 👥 User authentication and role-based access
- 📊 Real-time dashboard with statistics
- 📈 Financial reporting and analytics
- 🌙 Dark mode support
- 📱 Mobile-responsive design
- 🔍 Audit logging for security

## Quick Start

### Local Development

1. Clone the repository
```bash
git clone <your-repo-url>
cd errantmate
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Initialize database
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

6. Run the application
```bash
python app.py
```

## Deployment

### Heroku

1. Install Heroku CLI
2. Login to Heroku: `heroku login`
3. Create app: `heroku create your-app-name`
4. Add PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev`
5. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production
```
6. Deploy:
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### PythonAnywhere

1. Create a PythonAnywhere account
2. Upload your files via Git or web interface
3. Create a new web app
4. Set the working directory to your project
5. Install requirements: `pip install -r requirements.txt`
6. Configure the WSGI file to point to `wsgi.py`
7. Set environment variables in the web tab
8. Reload the web app

### DigitalOcean App Platform

1. Create a DigitalOcean account
2. Create a new app
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set run command: `gunicorn app:app`
6. Add environment variables
7. Deploy

## Environment Variables

- `SECRET_KEY`: Flask secret key (required)
- `DATABASE_URL`: Database connection URL (optional, defaults to SQLite)
- `FLASK_ENV`: Environment (development/production)

## Database Setup

### SQLite (Development)
The app uses SQLite by default. The database file will be created at `instance/deliveries.db`.

### PostgreSQL (Production)
Set the `DATABASE_URL` environment variable:
```
postgresql://username:password@hostname:port/database_name
```

## Default Admin User

After first run, create an admin user:
1. Register a new account
2. Update the user's role to 'admin' in the database
3. Or use the Flask shell to create one:
```python
from app import User, db
admin = User(username='admin', role='admin')
admin.set_password('your-password')
db.session.add(admin)
db.session.commit()
```

## Project Structure

```
errantmate/
├── app.py              # Main Flask application
├── wsgi.py             # WSGI entry point
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── Procfile          # Heroku process configuration
├── runtime.txt       # Python version specification
├── templates/         # Jinja2 templates
│   ├── base.html     # Base template with navigation
│   ├── index.html    # Dashboard
│   ├── add_delivery.html
│   ├── login.html
│   └── reports.html
├── static/           # Static assets (CSS, JS, images)
└── instance/         # Instance-specific files (database)
```

## Security Considerations

- Change the default `SECRET_KEY` in production
- Use HTTPS in production
- Keep dependencies updated
- Regularly backup your database
- Monitor audit logs for suspicious activity

## Database Migrations

When updating to newer versions that include database schema changes, run the appropriate migration script:

### For Development (SQLite):
```bash
python add_revenue_column.py
```

### For Production (PostgreSQL):
**Option 1: Python Script**
```bash
python migrate_production_db.py
```

**Option 2: Direct SQL**
```bash
psql -d your_database_name -f add_revenue_column.sql
```

### Migration Scripts:
- `add_revenue_column.py` - For local development (SQLite)
- `migrate_production_db.py` - For production environment (PostgreSQL)
- `add_revenue_column.sql` - Direct PostgreSQL SQL script

All scripts will:
- Add new database columns automatically
- Update existing records with default values
- Support both PostgreSQL and SQLite databases
- Verify successful migration completion

## Support

For issues and questions, please create an issue in the repository.

## License

© 2025 Xandega AI Solutions. All rights reserved.
