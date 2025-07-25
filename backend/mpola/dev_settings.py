# Development settings for Mpola Pay
# This file enables synchronous task execution without Redis

from .settings import *

# Override Celery settings for development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

print("🔧 Development mode: Tasks will execute synchronously (no Redis required)")
