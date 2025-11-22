from rest_framework import serializers
from apps.weather.models import WeatherLog


class WeatherLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherLog
        fields = [
            'id',
            'collected_at',
            'temperature',
            'humidity',
            'wind_speed',
            'condition',
            'rain_probability',
            'source',
        ]
