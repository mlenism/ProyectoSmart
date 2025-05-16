from datetime import date
from calendar import monthrange
from django.db.models import Count, Case, When, IntegerField
from django.http import JsonResponse
from django.utils.timezone import now
from django.views import View
from django.shortcuts import get_object_or_404
from .models import FinalHechos  # Ajusta el nombre de tu modelo si es diferente.
from ..meters.models import Meter  # Ajusta el nombre de tu modelo si es diferente.
from django.db import connection
from datetime import datetime
from ..pagination import CustomPageNumberPagination
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
class MeterStatusView(View):
    def get(self, request, meter_id):
        # Verifica si el medidor existe
        get_object_or_404(Meter, meter_code=meter_id)

        # Obtener fecha actual
        today = now().date()

        # Calcular mes y año anterior
        if today.month == 1:
            year, month = today.year - 1, 12
        else:
            year, month = today.year, today.month - 1

        # Obtener cantidad de días del mes anterior
        total_days_in_month = monthrange(year, month)[1]

        # Obtener lecturas del mes anterior
        readings = FinalHechos.objects.filter(
            meter_id=meter_id,
            recv_time_id__startswith=f"{year}{str(month).zfill(2)}"
        ).values('recv_time_id').annotate(
            walkby_count=Count(Case(When(gateway_id='WalkBy', then=1), output_field=IntegerField())),
            total_count=Count('recv_time_id')
        )

        days_with_non_walkby = sum(1 for r in readings if r['walkby_count'] < r['total_count'])
        days_with_any_reading = len(readings)

        # Determinar el estado del medidor
        if days_with_any_reading == 0:
            status = "SIN LECTURA"
        elif days_with_non_walkby == total_days_in_month:
            status = "DIARIO"
        elif days_with_non_walkby > 0:
            status = "INTERMITENTE"
        else:
            status = "WALKBY"

        return JsonResponse({"meter_id": meter_id, "status": status})

#@permission_classes([AllowAny]) 
class MeterReadingsByDateRangeView(APIView):
    pagination_class = CustomPageNumberPagination

    def get(self, request, meter_id):
        get_object_or_404(Meter, meter_code=meter_id)

        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if not start_date or not end_date:
            return JsonResponse({"error": "Debe proporcionar 'start_date' y 'end_date'"}, status=400)

        try:
            start_date = int(start_date)
            end_date = int(end_date)
        except ValueError:
            return JsonResponse({"error": "Las fechas deben ser numéricas (YYYYMMDD)"}, status=400)

        readings = FinalHechos.objects.filter(
            meter_id=meter_id,
            recv_time_id__gte=start_date,
            recv_time_id__lte=end_date
        ).values("recv_time_id", "recv_ts_id", "real_volume", "gateway_id").order_by("recv_time_id")

        formatted_readings = []
        for r in readings:
            try:
                date_str = str(r["recv_time_id"])
                time_str = str(r["recv_ts_id"]).zfill(6) if r["recv_ts_id"] is not None else "000000"
                combined_str = f"{date_str}{time_str}"
                timestamp = datetime.strptime(combined_str, "%Y%m%d%H%M%S")
                formatted_date = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                formatted_date = None

            formatted_readings.append({
                "meter_id": meter_id,
                "datetime": formatted_date,
                "real_volume": r["real_volume"],
                "gateway_id": r["gateway_id"],
            })

        # Aplicar paginación
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(formatted_readings, request, view=self)
        return paginator.get_paginated_response(page)

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
