import os
from celery import Celery

# Define qual arquivo de settings o celery deve usar
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amb_config.settings')

# Cria instância do celery
app = Celery('amb_config')

# Lê configurações do Django (usa namespace "CELERY_")
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover para encontrar tasks nos apps
app.autodiscover_tasks()
