from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Apunta al settings de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

# (Opcional) Si quieres TZ local en vez de UTC:
app.conf.enable_utc = False
app.conf.update(timezone="America/Mexico_City")

# OJO: todo en minúsculas
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descubre tasks.py en cada app instalada de Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Demo task
@app.task(bind=True)
def debug_task(self):
    print(f"request {self.request!r}")