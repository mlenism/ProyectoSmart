from .models import Meter
from .serializer import Meterserializer
from ..pagination import CustomPageNumberPagination
from rest_framework import viewsets
from rest_framework import viewsets
from rest_framework.views import APIView
from .serializer import Meterserializer
from datetime import datetime
from django.http import JsonResponse
from rest_framework import filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from rest_framework import status
from django.db import connection
from rest_framework.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.views import APIView

from datetime import datetime
from django.http import JsonResponse


#Vista para los datos de los medidores
class MeterViewSet(viewsets.ModelViewSet):

    queryset = Meter.objects.all()  # Define el queryset aquí

    #Serializador de los medidores
    serializer_class = Meterserializer
    pagination_class = CustomPageNumberPagination

    #Filtros del backend
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['create_time_id', 
                       'create_ts_id', 
                       'meter_code', 
                       'meter_id',
                       'meter_type',
                       'creator',
                       'longitude',
                       'latitude',
                       'status']  # Añade estos campos a los campos ordenables

    def get_queryset(self):
        queryset = super().get_queryset()
        creator = self.request.query_params.get('creator') #definir que se puede filtrar por creador
        status = self.request.query_params.get('status') #Habilitar filtrado por status
        tapa_id = self.request.query_params.get('tapa_id') #Habilitar filtrado por tapa_id
        create_date = self.request.query_params.get('create_date') #Habilitar filtrado por create_date
        meter_code = self.request.query_params.get('meter_code') #Habilitar filtrado por create_date

        if creator:
            # Split the creator query parameter by comma to handle multiple values
            creator_list = [c.strip() for c in creator.split(',')]
            queryset = queryset.filter(creator__in=creator_list)
        if status:
            status_list = [c.strip() for c in status.split(',')]
            queryset = queryset.filter(status__in=status_list)
        if tapa_id:
            queryset = queryset.filter(tapa_id=tapa_id)
        if create_date:
            queryset = queryset.filter(create_date=create_date)
        if meter_code:
            queryset = queryset.filter(meter_code=meter_code)
        # Ordenar por 'create_time_id' y 'create_ts_id'
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            if ordering == 'create_date':
                # Ordenar por create_time_id y create_ts_id en orden descendente
                queryset = queryset.order_by(
                    F('create_time_id').desc(nulls_last=True),
                    F('create_ts_id').desc(nulls_last=True)
                )
            elif ordering.startswith('-create_date'):
                # Ordenar por create_time_id y create_ts_id en orden ascendente
                queryset = queryset.order_by(
                    F('create_time_id').asc(nulls_last=True),
                    F('create_ts_id').asc(nulls_last=True)
                )

        return queryset
    

    def list(self, request, *args, **kwargs):
        # Verifica si se debe desactivar la paginación
        no_paginate = request.query_params.get('no_paginate', 'false').lower() == 'true'

        queryset = self.filter_queryset(self.get_queryset())

        if no_paginate:
            # Desactiva la paginación y devuelve todos los registros
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            # Usa la paginación definida
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
#Vista para los medidores que no tienen datos aún
class MeterEmptyViewSet(viewsets.ModelViewSet):
    queryset = Meter.objects.all()
    serializer_class = Meterserializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtra los medidores con longitude o latitude nulo
        queryset = queryset.filter(tapa_id=6,longitude__isnull=True,latitude__isnull=True)
        return queryset
    
#Vista para el autocomplete de los medidores 
class MeterAutocompleteView(APIView):

    queryset = Meter.objects.all()
    serializer_class = Meterserializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            results = Meter.objects.filter(meter_code__icontains=query)
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(results, request)
            if page is not None:
                serializer = Meterserializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = Meterserializer(results, many=True)
            return Response(serializer.data)
        return JsonResponse([], safe=False)
    
class MedidoresExclusivosPorGatewayAPIView(APIView):
    def get(self, request):
        # Obtener parámetros de consulta
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        service_centers = request.query_params.getlist('service_centers')  # Obtener lista de service_centers
        print("recibiendo los datos")
        # Validar fechas como antes
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

        # Convertir la lista de service_centers en formato para la consulta SQL
        if service_centers:
            service_center_list = ', '.join([f"'{center}'" for center in service_centers])
            service_center_clause = f"g.service_center IN ({service_center_list})"
        else:
            service_center_clause = '1=1'  # No se filtra por service_center si no se proporciona ninguno

        # Consulta SQL ajustada para incluir gateways sin medidores exclusivos
        query = f"""
            WITH medidores_por_gateway AS (
                SELECT
                    fh.gateway_id,
                    fh.meter_id,
                    COUNT(*) AS lecturas -- Conteo de lecturas por medidor
                FROM
                    final_hechos fh
                JOIN
                    final_medidores fm ON fh.meter_id = fm.meter_code -- Unir con la tabla de medidores
                WHERE
                    fh.meter_time >= {start_date} AND fh.meter_time <= {start_date}
                    AND fm.status != 'NO OPERATIVO' -- Filtrar solo medidores operativos
                GROUP BY
                    fh.gateway_id, fh.meter_id
            ),
            medidores_unicos AS (
                SELECT
                    mg.meter_id
                FROM
                    medidores_por_gateway mg
                GROUP BY
                    mg.meter_id
                HAVING
                    COUNT(DISTINCT mg.gateway_id) = 1 -- Solo medidores asociados a un solo gateway
            ),
            conteo_por_gateway AS (
                SELECT
                    g.gateway_id,
                    g.service_center,
                    COUNT(DISTINCT mg.meter_id) AS medidores_exclusivos,
                    COALESCE(SUM(mg.lecturas), 0) AS total_lecturas -- Sumar las lecturas de los medidores exclusivos
                FROM
                    stg3_gateways g
                LEFT JOIN
                    medidores_por_gateway mg ON upper(mg.gateway_id) = g.gateway_id
                JOIN
                    medidores_unicos mu ON mg.meter_id = mu.meter_id
                GROUP BY
                    g.gateway_id, g.service_center
            )
            -- Aquí añadimos los gateways sin medidores exclusivos
            SELECT
                g.gateway_id,
                g.service_center,
                COALESCE(cpg.medidores_exclusivos, 0) AS medidores_exclusivos,
                COALESCE(cpg.total_lecturas, 0) AS total_lecturas
            FROM
                stg3_gateways g
            LEFT JOIN
                conteo_por_gateway cpg ON g.gateway_id = cpg.gateway_id -- Incluye gateways sin medidores exclusivos
            WHERE
                {service_center_clause}
            ORDER BY
                medidores_exclusivos DESC;
        """
	
        with connection.cursor() as cursor:
            print("Ejecutando el cursor")
            cursor.execute(query)
            results = cursor.fetchall()
            print("cursor ejecutado")

        # Construir la respuesta
        response_data = [
            {
                'gateway_id': row[0],
                'service_center': row[1],
                'medidores_exclusivos': row[2],
                'total_lecturas': row[3],
            } for row in results
        ]

        return Response(response_data, status=status.HTTP_200_OK)

class MedidoresNoExclusivosPorGatewayAPIView(APIView):
    def get(self, request):
        # Obtener parámetros de consulta
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        service_centers = request.query_params.getlist('service_centers')  # Obtener lista de service_centers

        # Validar fechas como antes
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

        # Convertir la lista de service_centers en formato para la consulta SQL
        if service_centers:
            service_center_list = ', '.join([f"'{center}'" for center in service_centers])
            service_center_clause = f"sg.service_center IN ({service_center_list})"
        else:
            service_center_clause = '1=1'  # No se filtra por service_center si no se proporciona ninguno

        # Consulta SQL ajustada para incluir gateways sin medidores exclusivos
        query = f"""
        WITH gateways_lecturas AS (
            SELECT
                fh.gateway_id,
                COUNT(DISTINCT fh.meter_id) AS medidores_conectados, -- Conteo de medidores distintos conectados por gateway
                COUNT(*) AS lecturas_registradas -- Conteo total de lecturas por gateway
            FROM
                final_hechos fh
            JOIN
                final_medidores fm ON fh.meter_id = fm.meter_code -- Unir con la tabla de medidores
            WHERE
                fh.meter_time >= {start_date}
                AND fh.meter_time <= {end_date}
                AND fm.status != 'NO OPERATIVO' -- Filtrar solo medidores operativos
            GROUP BY
                fh.gateway_id
        )
        SELECT
            sg.gateway_id,
            sg.service_center,
            COALESCE(gl.medidores_conectados, 0) AS medidores_conectados, -- Si no hay lecturas, asignar 0
            COALESCE(gl.lecturas_registradas, 0) AS lecturas_registradas  -- Si no hay lecturas, asignar 0
        FROM
            stg3_gateways sg
        LEFT JOIN
            gateways_lecturas gl ON sg.gateway_id = gl.gateway_id
        WHERE
            {service_center_clause}
        ORDER BY
            medidores_conectados DESC;
        """

        with connection.cursor() as cursor:
            print("Entra")
            cursor.execute(query)
            print("Sale")
            results = cursor.fetchall()

        # Construir la respuesta
        response_data = [
            {
                'gateway_id': row[0],
                'service_center': row[1],
                'medidores_exclusivos': row[2],
                'total_lecturas': row[3],
            } for row in results
        ]

        return Response(response_data, status=status.HTTP_200_OK)