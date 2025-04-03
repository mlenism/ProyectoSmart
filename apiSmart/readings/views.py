from datetime import date
from django.db.models import Count, Case, When, IntegerField
from django.http import JsonResponse
from django.utils.timezone import now
from django.views import View
from django.shortcuts import get_object_or_404
from .models import FinalHechos  # Ajusta el nombre de tu modelo si es diferente.
from ..meters.models import Meter  # Ajusta el nombre de tu modelo si es diferente.
from django.db import connection

class MeterStatusView(View):
    def get(self, request, meter_id):
        # Obtener la fecha actual

        get_object_or_404(Meter, meter_code=meter_id)  # Verifica si el medidor existe

        today = now().date()
        year, month = today.year, today.month

        # Contar los días totales en el mes actual
        #total_days_in_month = (date(year, month + 1, 1) - date(year, month, 1)).days if month < 12 else 31

        # Obtener los días únicos con lecturas para el meter_id en el mes actual
        readings = FinalHechos.objects.filter(
            meter_id=meter_id,
            recv_time_id__startswith=f"{year}{str(month).zfill(2)}"  # Filtra por año-mes en recv_time_id (YYYYMMDD)
        ).values('recv_time_id').annotate(
            walkby_count=Count(Case(When(gateway_id='WalkBy', then=1), output_field=IntegerField())),
            total_count=Count('recv_time_id')
        )

        # Contar días con al menos una lectura distinta de 'WalkBy'
        days_with_non_walkby = sum(1 for r in readings if r['walkby_count'] < r['total_count'])

        # Contar días totales con cualquier lectura
        days_with_any_reading = len(readings)
        # Determinar el estado del medidor
        if days_with_any_reading == 0:
            status = "SIN LECTURA"
        elif days_with_non_walkby == today.day:
            status = "DIARIO"
        elif days_with_non_walkby > 0:
            status = "INTERMITENTE"
        else:
            status = "WALKBY"

        return JsonResponse({"meter_id": meter_id, "status": status})

class LastReadingView(View):
    def get(self, request, meter_id):
        # Validar si el medidor existe en el modelo Meters
        get_object_or_404(Meter, meter_code=meter_id)

        query = """
        SELECT recv_time_id, real_volume 
        FROM smart_med.final_hechos
        WHERE meter_id = %s
        ORDER BY recv_time_id DESC
        LIMIT 1;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [meter_id])
            row = cursor.fetchone()

        if row:
            return JsonResponse({"meter_id": meter_id, "recv_time_id": row[0], "real_volume": row[1]})
        else:
            return JsonResponse({"error": "No readings found"}, status=404)
