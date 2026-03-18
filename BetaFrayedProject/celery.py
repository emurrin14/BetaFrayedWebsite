import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BetaFrayedProject.settings')

app = Celery('BetaFrayedProject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()