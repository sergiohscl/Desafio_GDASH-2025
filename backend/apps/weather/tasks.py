# apps/weather/tasks.py

import json
from pathlib import Path

import requests
from celery import shared_task
from django.conf import settings

from .models import WeatherLog

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


@shared_task
def fetch_weather_data():
    """
    Produtor: busca dados de clima (Open-Meteo) e envia o payload normalizado
    para outra task via fila (store_weather_log).
    """

    # Coordenadas de exemplo (Brasília) – ajuste para sua cidade se quiser.
    params = {
        "latitude": -15.7801,
        "longitude": -47.9292,
        "hourly": (
            "temperature_2m,"
            "relativehumidity_2m,"
            "windspeed_10m,"
            "precipitation_probability,"
            "weathercode"
        ),
        "timezone": "auto",
    }

    # Usamos a lib `requests` aqui (não urllib)
    response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    if not times:
        return  # nada pra processar

    last_index = len(times) - 1

    normalized = {
        "collected_at": times[last_index],
        "temperature": hourly.get("temperature_2m", [None])[last_index],
        "humidity": hourly.get("relativehumidity_2m", [None])[last_index],
        "wind_speed": hourly.get("windspeed_10m", [None])[last_index],
        "rain_probability": hourly.get(
            "precipitation_probability", [None]
        )[last_index],
        "condition_code": hourly.get("weathercode", [None])[last_index],
        "source": "open-meteo",
        "raw": data,
    }

    # Opcional: salva JSON em disco para debug/auditoria
    try:
        logs_dir = Path(settings.BASE_DIR) / "weather_json"
        logs_dir.mkdir(exist_ok=True)

        safe_timestamp = normalized["collected_at"].replace(":", "-")
        file_path = logs_dir / f"weather_{safe_timestamp}.json"

        file_path.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        # Não queremos que erro de log em arquivo quebre a task
        pass

    # Envia para o "worker" via Celery (Message Broker)
    store_weather_log.delay(normalized)


@shared_task
def store_weather_log(payload: dict):
    """
    Worker: consome a mensagem (JSON normalizado) e grava no banco (WeatherLog). # noqa E501
    """
    WeatherLog.objects.create(
        temperature=payload.get("temperature"),
        humidity=payload.get("humidity"),
        wind_speed=payload.get("wind_speed"),
        rain_probability=payload.get("rain_probability"),
        condition=str(payload.get("condition_code")),
        source=payload.get("source", "open-meteo"),
        raw_payload=payload.get("raw"),
    )
