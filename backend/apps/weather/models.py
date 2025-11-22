from django.db import models


class WeatherLog(models.Model):
    collected_at = models.DateTimeField(auto_now_add=True)

    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    condition = models.CharField(max_length=255, null=True, blank=True)
    rain_probability = models.FloatField(null=True, blank=True)

    source = models.CharField(max_length=100, default='open-meteo')
    raw_payload = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-collected_at']

    def __str__(self):
        return f"{self.collected_at} - {self.temperature}°C"
