import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mpola.settings')

app = Celery('mpola')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Setup Django before autodiscovering tasks
import django
django.setup()

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Explicitly import our tasks to ensure they are registered
from . import tasks

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Configure Celery for better development experience
app.conf.update(
    # Task settings
    task_always_eager=False,  # Set to True for synchronous execution during testing
    task_eager_propagates=True,
    task_ignore_result=False,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # Error handling
    task_reject_on_worker_lost=True,
    
    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)
