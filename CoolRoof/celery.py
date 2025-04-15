from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from billiard import freeze_support  # Fix multiprocessing issue on Windows

# Fix for Windows multiprocessing issues
#freeze_support()

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoolRoof.settings')

app = Celery('CoolRoof')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery settings to avoid Windows multiprocessing issues
#app.conf.worker_concurrency = 2  # Reduce concurrency
#app.conf.broker_connection_retry_on_startup = True  # Ensure connection retry

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
