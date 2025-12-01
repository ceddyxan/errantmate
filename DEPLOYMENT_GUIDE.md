# ErrantMate Deployment Guide

## Prerequisites
- Git repository with your code
- Render account (free tier available)
- All security improvements implemented

## Deployment Steps

### 1. Push Your Code to Git Repository
```bash
git init
git add .
git commit -m "Implement security improvements and prepare for deployment"
git branch -M main
git remote add origin <your-git-repo-url>
git push -u origin main
```

### 2. Deploy to Render

#### Option A: Via Render Dashboard (Recommended)
1. Go to [render.com](https://render.com)
2. Sign up/login to your account
3. Click "New" → "Web Service"
4. Connect your Git repository
5. Render will automatically detect your Python application
6. Configure the service:
   - **Name**: errantmate
   - **Environment**: Python 3
   - **Region**: Choose nearest to your users
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start.py`
   - **Health Check Path**: `/health`

#### Option B: Via render.yaml (Automatic)
1. Push your code with the `render.yaml` file
2. Connect your repository to Render
3. Render will automatically create services based on `render.yaml`

### 3. Environment Variables Configuration
Render will automatically set:
- `SECRET_KEY`: Auto-generated 64-character key
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: production

### 4. Database Initialization
After deployment:
1. Visit `https://your-app-url.onrender.com/force-init-db`
2. This will create all database tables and the admin user

### 5. Login Credentials
- **Username**: `admin`
- **Password**: `ErrantMate@24!`

## Security Features Enabled
✅ CSRF Protection
✅ Rate Limiting (5 login attempts per 5 minutes)
✅ Secure Secret Key
✅ Production Logging
✅ PostgreSQL Database
✅ HTTPS Encryption

## Monitoring and Logs
- Check Render Dashboard for service logs
- Application logs are stored in `/logs/errantmate.log`
- Health check available at `/health`

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
- Visit `/force-init-db` to initialize database
- Check DATABASE_URL environment variable

#### 2. Build Failures
- Verify all dependencies in `requirements.txt`
- Check Python version compatibility (3.11.9)

#### 3. Health Check Failures
- Ensure `/health` endpoint is accessible
- Check application startup logs

#### 4. Login Issues
- Use the new secure password: `ErrantMate@24!`
- Check rate limiting (wait 5 minutes if locked out)

### Useful Endpoints
- `/health` - Health check
- `/force-init-db` - Database initialization
- `/check-db` - Database status check

## Performance Optimization
- Free tier includes 750 hours/month
- PostgreSQL database has connection limits
- Consider upgrading for higher traffic

## Security Best Practices
1. Change the default admin password after first login
2. Regularly check audit logs
3. Monitor for suspicious login attempts
4. Keep dependencies updated

## Support
- Render documentation: https://render.com/docs
- Application logs in Render Dashboard
- Health monitoring at `/health` endpoint
