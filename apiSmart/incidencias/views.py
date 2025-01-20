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

class IncidenciaCreateView(viewsets.ModelViewSet):
    
    queryset = Incidencia.objects.all()

    serializer_class = IncidenciaSerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['incidencia_id',
                       'meter_code'
                       'fecha_incidencia',
                       'falla'
                        ]
    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        incidencia_id = self.request.query_params.get('incidencia_id') #Habilitar filtrado por status
        fecha_incidencia = self.request.query_params.get('fecha_incidencia') #Habilitar filtrado por tapa_id
        falla = self.request.query_params.get('falla') #Habilitar filtrado por create_date
        meter_code = self.request.query_params.get('meter_code') #Habilitar filtrado por create_date

        if incidencia_id:
            # Split the creator query parameter by comma to handle multiple values
            incidencia_id_list = [c.strip() for c in incidencia_id.split(',')]
            queryset = queryset.filter(incidencia_id__in=incidencia_id_list)
        if fecha_incidencia:
            fecha_incidencia_list = [c.strip() for c in fecha_incidencia.split(',')]
            queryset = queryset.filter(fecha_incidencia__in=fecha_incidencia_list)
        if falla:
            queryset = queryset.filter(falla=falla)
        if meter_code:
            queryset = queryset.filter(meter_code=meter_code)
        return queryset
    

    def perform_create(self, serializer):
        img_base64 = self.request.data.get("img")
        
        if img_base64:
            # Decodifica la imagen de base64 a binario
            img_data = base64.b64decode(img_base64)
            serializer.save(img=img_data)
        else:
            serializer.save()

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