# Celery Setup Guide for Mpola Pay

This guide will help you set up and run Celery for handling background tasks in the Mpola Pay application.

## 🎯 Quick Start Options

### Option 1: Production Mode (with Redis)
```bash
# 1. Install and start Redis
brew install redis
brew services start redis

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run database migrations
python manage.py migrate

# 4. Start Celery services
./start_celery.sh
```

### Option 2: Development Mode (no Redis required)
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Run database migrations
python manage.py migrate

# 3. Start in development mode
./start_celery_dev.sh

# 4. In another terminal, start Django
export DJANGO_SETTINGS_MODULE=mpola.dev_settings
python manage.py runserver
```

## 📋 Detailed Setup Instructions

### Prerequisites

1. **Python 3.8+** with pip
2. **Redis** (for production mode only)
3. **Django** application properly configured

### Installing Redis

#### macOS (using Homebrew)
```bash
brew install redis
brew services start redis

# Test Redis connection
redis-cli ping
# Should return: PONG
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
```

#### Docker (any OS)
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

### Python Dependencies

Install required packages:
```bash
pip install celery redis django-celery-beat flower
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## 🚀 Running Celery

### Method 1: Using the Startup Script (Recommended)

The startup script handles everything automatically:

```bash
# Make script executable (first time only)
chmod +x start_celery.sh

# Start all Celery services
./start_celery.sh
```

This will start:
- ✅ Celery Worker (processes background tasks)
- ✅ Celery Beat (handles scheduled tasks)
- ✅ Flower Monitor (web interface at http://localhost:5555)

### Method 2: Manual Commands

If you prefer to run each service separately:

#### Terminal 1 - Celery Worker
```bash
celery -A mpola worker --loglevel=info --pool=solo
```

#### Terminal 2 - Celery Beat (for scheduled tasks)
```bash
celery -A mpola beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

#### Terminal 3 - Flower Monitor (optional)
```bash
pip install flower
celery -A mpola flower --port=5555
```

### Method 3: Development Mode (No Redis)

For development and testing without Redis:

```bash
# Use development settings
export DJANGO_SETTINGS_MODULE=mpola.dev_settings
python manage.py runserver
```

In this mode, tasks run synchronously in the same process.

## 🔧 Configuration

### Celery Settings

Key settings in `mpola/settings.py`:

```python
# Basic Celery configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'UTC'

# Task settings
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_TIME_LIMIT = 600       # 10 minutes

# Scheduled tasks
CELERY_BEAT_SCHEDULE = {
    'process-scheduled-payments': {
        'task': 'mpola.tasks.process_scheduled_payments',
        'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours
    },
}
```

### Environment Variables

Optional environment variables:

```bash
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0
export DJANGO_SETTINGS_MODULE=mpola.settings
```

## 📊 Monitoring

### Flower Web Interface

Access the Flower monitoring interface at: http://localhost:5555

Features:
- View active workers
- Monitor task execution
- Browse task history
- Real-time task statistics

### Command Line Monitoring

```bash
# Check worker status
celery -A mpola status

# Monitor tasks in real-time
celery -A mpola events

# Inspect active tasks
celery -A mpola inspect active
```

## 🧪 Testing Tasks

### Test the Scheduled Payments

You can trigger scheduled payments manually:

```bash
# Using curl
curl -X POST http://localhost:8000/trigger-scheduled-payments/ \
  -H "Content-Type: application/json"

# Check scheduled payments status
curl -X GET http://localhost:8000/scheduled-payments-status/
```

### Test Individual Tasks

```python
# In Django shell: python manage.py shell
from mpola.tasks import process_scheduled_payments

# Run task directly
result = process_scheduled_payments()
print(result)

# Or queue the task (requires Celery worker)
result = process_scheduled_payments.delay()
print(f"Task ID: {result.id}")
```

## 🛠 Troubleshooting

### Common Issues

#### Redis Connection Error
```
Error: [Errno 61] Connection refused
```
**Solution:** Make sure Redis is running:
```bash
brew services start redis
# or
redis-server
```

#### Task Not Executing
**Check:** 
1. Celery worker is running
2. Redis is accessible
3. Task is properly registered

```bash
celery -A mpola inspect registered
```

#### Permission Errors
**Solution:** Ensure proper file permissions:
```bash
chmod +x start_celery.sh
```

### Development Mode Issues

If tasks seem to hang in development mode, make sure you're using the development settings:

```bash
export DJANGO_SETTINGS_MODULE=mpola.dev_settings
```

## 📁 File Structure

```
backend/
├── celery_app.py           # Celery configuration
├── start_celery.sh         # Production startup script
├── start_celery_dev.sh     # Development startup script
├── mpola/
│   ├── settings.py         # Django settings with Celery config
│   └── tasks.py           # Task definitions
└── payments/
    └── views.py           # API endpoints that trigger tasks
```

## 🔄 Task Definitions

Main tasks defined in `mpola/tasks.py`:

- `process_scheduled_payments()` - Process all due payments
- `process_schedule_payments(schedule_id)` - Process specific schedule
- `process_receiver_payment(receiver_id)` - Process individual receiver

## 🎯 Next Steps

1. **Start Redis** (for production mode)
2. **Run the startup script**: `./start_celery.sh`
3. **Test the API endpoints** to trigger tasks
4. **Monitor with Flower** at http://localhost:5555
5. **Check logs** for any issues

## 📞 Support

If you encounter issues:

1. Check the logs in the terminal where Celery is running
2. Verify Redis is accessible: `redis-cli ping`
3. Ensure all dependencies are installed: `pip list`
4. Try development mode first: `./start_celery_dev.sh`

Happy coding! 🚀
