import csv
from datetime import timedelta
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.weather.models import WeatherLog
from .serializers import WeatherLogSerializer
from utils.generate_insights_text import generate_insights_text
from utils.generate_xlsx_bytes import generate_xlsx_bytes
from rest_framework import status


class WeatherLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/weather/logs/           -> lista registros
    /api/weather/logs/export.csv -> exporta CSV
    /api/weather/logs/export.xlsx-> exporta XLSX
    /api/weather/logs/insights   -> gera/retorna insights de IA
    """
    queryset = WeatherLog.objects.all()
    serializer_class = WeatherLogSerializer

    @action(detail=False, methods=['get'], url_path='export.csv')
    def export_csv(self, request):
        logs = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="weather_logs.csv"' # noqa E501

        writer = csv.writer(response)
        writer.writerow([
            'collected_at', 'temperature', 'humidity',
            'wind_speed', 'condition', 'rain_probability', 'source',
        ])

        for log in logs:
            writer.writerow([
                log.collected_at.isoformat(),
                log.temperature,
                log.humidity,
                log.wind_speed,
                log.condition,
                log.rain_probability,
                log.source,
            ])

        return response

    @action(detail=False, methods=['get'], url_path='export.xlsx')
    def export_xlsx(self, request):
        logs = self.get_queryset()
        xlsx_bytes = generate_xlsx_bytes(logs)

        response = HttpResponse(
            xlsx_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' # noqa E501
        )
        response['Content-Disposition'] = 'attachment; filename="weather_logs.xlsx"' # noqa E501
        return response

    @action(detail=False, methods=['get', 'post'], url_path='insights')
    def insights(self, request):
        """
        Gera insights baseados nos dados históricos.
        - GET: usa intervalo padrão (últimos 7 dias ou ?days=3)
        - POST: permite enviar {"days": 3} no body.
        """
        # 1) Pega o valor cru de days (body ou query string)
        raw_days = None
        if request.method == 'POST':
            raw_days = request.data.get('days')
        else:  # GET
            raw_days = request.query_params.get('days')

        # 2) Define default se vier vazio
        if raw_days in (None, ''):
            days = 7
        else:
            # 3) Valida/transforma em int
            try:
                days = int(raw_days)
            except (TypeError, ValueError):
                return Response(
                    {"detail": "O parâmetro 'days' deve ser um número inteiro."}, # noqa E501
                    status=status.HTTP_400_BAD_REQUEST,
                )

        since = timezone.now() - timedelta(days=days)
        logs = WeatherLog.objects.filter(collected_at__gte=since)

        serializer = self.get_serializer(logs, many=True)
        insights_text = generate_insights_text(serializer.data)

        return Response({
            "days": days,
            "count": len(serializer.data),
            "insights": insights_text,
            "data": serializer.data,
        })
