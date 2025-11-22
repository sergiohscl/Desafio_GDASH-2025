from io import BytesIO
from openpyxl import Workbook


def generate_xlsx_bytes(logs_queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Weather Logs"

    headers = [
        'collected_at', 'temperature', 'humidity',
        'wind_speed', 'condition', 'rain_probability', 'source',
    ]
    ws.append(headers)

    for log in logs_queryset:
        ws.append([
            log.collected_at.isoformat(),
            log.temperature,
            log.humidity,
            log.wind_speed,
            log.condition,
            log.rain_probability,
            log.source,
        ])

    output = BytesIO()
    wb.save(output)
    return output.getvalue()
