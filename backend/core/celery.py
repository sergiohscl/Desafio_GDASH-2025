import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Nome igual ao projeto Django
app = Celery("core")

# Lê configurações que começam com CELERY_ no settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descobre automaticamente tasks.py de cada app registrado em INSTALLED_APPS
app.autodiscover_tasks()

# Agendamento do Celery Beat
app.conf.beat_schedule = {
    "fetch-weather-every-hour": {
        # Nome completo da task (módulo + função)
        "task": "apps.weather.tasks.fetch_weather_data",
        "schedule": crontab(minute=0, hour="*"),  # a cada 1h
    },
}
