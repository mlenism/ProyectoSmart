from rest_framework import viewsets
from rest_framework.views import APIView
from .serializer import IncidenciaSerializer
from .models import Incidencia
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from ..pagination import CustomPageNumberPagination
import base64
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from rest_framework.exceptions import ValidationError
from django.db.models import F
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

class IncidenciaCreateView(viewsets.ModelViewSet):
    
    queryset = Incidencia.objects.all()

    serializer_class = IncidenciaSerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['incidencia_id',
                       'meter_code',
                       'fecha_incidencia',
                       'falla'
                        ]

    def get_queryset(self):
        queryset = super().get_queryset()

        incidencia_id = self.request.query_params.get('incidencia_id')
        fecha_incidencia = self.request.query_params.get('fecha_incidencia')
        falla = self.request.query_params.get('falla')
        meter_code = self.request.query_params.get('meter_code')
        fecha_gte_str = self.request.query_params.get('fecha_gte')
        fecha_lte_str = self.request.query_params.get('fecha_lte')

        if incidencia_id:
            incidencia_id_list = [c.strip() for c in incidencia_id.split(',')]
            queryset = queryset.filter(incidencia_id__in=incidencia_id_list)

        if fecha_incidencia:
            fecha_incidencia_list = [c.strip() for c in fecha_incidencia.split(',')]
            queryset = queryset.filter(fecha_incidencia__in=fecha_incidencia_list)

        if falla:
            queryset = queryset.filter(falla=falla)

        if meter_code:
            queryset = queryset.filter(meter_code=meter_code)

        if fecha_gte_str and fecha_lte_str:
            try:
                fecha_gte = make_aware(datetime.strptime(fecha_gte_str, "%Y%m%d")) + timedelta(days=1)
                fecha_lte = make_aware(datetime.strptime(fecha_lte_str, "%Y%m%d")) + timedelta(days=1)
                queryset = queryset.filter(
                    fecha_incidencia__gte=fecha_gte,
                    fecha_incidencia__lte=fecha_lte  # NOT __lte
                )
            except ValueError:
                pass

        return queryset
    

    def perform_create(self, serializer):
        img_base64 = self.request.data.get("img")
        
        if img_base64:
            # Decodifica la imagen de base64 a binario
            img_data = base64.b64decode(img_base64)
            serializer.save(img=img_data)
        else:
            serializer.save()


class IncidenciaAutocompleteView(APIView):
    queryset = Incidencia.objects.all()
    serializer_class = IncidenciaSerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = [
        'incidencia_id',
        'meter_code',
        'fecha_incidencia',
        'falla'
    ]

    def get(self, request):
        query = request.GET.get('q', '')
        fecha_incidencia_gte = request.GET.get('fecha_incidencia_gte')
        fecha_incidencia_lte = request.GET.get('fecha_incidencia_lte')
        fecha_incidencia_exact = request.GET.get('fecha_incidencia_exact')

        results = Incidencia.objects.all()

        if query:
            results = results.filter(meter_code__icontains=query)

        # Aplicar filtros de rango y exactitud
        if fecha_incidencia_gte:
            results = results.filter(fecha_incidencia__gte=fecha_incidencia_gte)
        if fecha_incidencia_lte:
            results = results.filter(fecha_incidencia__lte=fecha_incidencia_lte)
        if fecha_incidencia_exact:
            results = results.filter(fecha_incidencia=fecha_incidencia_exact)

        # Ordenar los resultados
        results = results.order_by(
            F('fecha_incidencia').desc(nulls_last=True),
            F('incidencia_id').desc(nulls_last=True)
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(results, request)
        if page is not None:
            serializer = IncidenciaSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = IncidenciaSerializer(results, many=True)
        return Response(serializer.data)
    
class ConteoIncidenciasBase(APIView):
    def get(self, request):
        try:
            # Obtener parámetros de consulta
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            creator = request.query_params.get('creator')

            # Validar fechas
            try:
                if start_date:
                    start_date_validator = datetime.strptime(start_date, '%Y%m%d').date()
                if end_date:
                    end_date_validator = datetime.strptime(end_date, '%Y%m%d').date()

                if not start_date or not end_date:
                    raise ValidationError("Both start_date and end_date are required.")

                if start_date > end_date:
                    raise ValidationError("start_date cannot be greater than end_date.")
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYYMMDD."}, status=status.HTTP_400_BAD_REQUEST)

            # Validar creator
            if not creator:
                return Response({"error": "Creator parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Query SQL ajustada para incluir el rango de fechas y creator
            query = f"""
                WITH IncidenciasEnRango AS (
                    SELECT
                        fi.meter_code,
                        fi.falla_id,
                        fi.fecha_incidencia,
                        fm.creator,
                        ff.falla_desc,
                        ff.falla_type
                    FROM
                        final_incidencias fi
                    INNER JOIN
                        final_medidores fm ON fi.meter_code = fm.meter_code
                    INNER JOIN
                        final_fallas ff ON fi.falla_id = ff.falla_id
                    WHERE
                        fi.fecha_incidencia BETWEEN {start_date} AND {end_date} 
                        AND fm.creator = '{creator}'
                )
                SELECT
                    COUNT(*) AS total_incidencias,
                    falla_type,
                    falla_desc,
                    COUNT(falla_id) AS conteo_tipo_falla
                FROM
                    IncidenciasEnRango
                GROUP BY
                    falla_type, falla_desc
                ORDER BY
                    falla_type, falla_desc;
            """

            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

            # Construir la respuesta
            response_data = [
                {
                    'total_incidencias': row[0],
                    'falla_type': row[1],
                    'falla_desc': row[2],
                    'conteo_tipo_falla': row[3]
                } for row in results
            ]

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            # Captura errores generales y proporciona un mensaje de error
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)