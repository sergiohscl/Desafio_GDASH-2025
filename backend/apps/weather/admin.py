from django.contrib import admin
from .models import WeatherLog


@admin.register(WeatherLog)
class WeatherLogAdmin(admin.ModelAdmin):
    list_display = (
        "collected_at",
        "temperature",
        "humidity",
        "wind_speed",
        "rain_probability",
        "condition",
        "source",
    )
    list_filter = (
        "source",
        "condition",
        "collected_at",
    )
    search_fields = (
        "condition",
        "source",
    )
    readonly_fields = (
        "collected_at",
        "raw_payload",
    )
    date_hierarchy = "collected_at"
    ordering = ("-collected_at",)

    fieldsets = (
        (
            "Dados de clima",
            {
                "fields": (
                    "collected_at",
                    "temperature",
                    "humidity",
                    "wind_speed",
                    "rain_probability",
                    "condition",
                    "source",
                )
            },
        ),
        (
            "Payload bruto (JSON)",
            {
                "classes": ("collapse",),
                "fields": ("raw_payload",),
            },
        ),
    )
