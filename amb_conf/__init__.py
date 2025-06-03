from __future__ import absolute_import, unicode_literals

# Importa a instância do Celery para que ela seja executada com o Django
from .celery import app as celery_app

__all__ = ('celery_app',)
